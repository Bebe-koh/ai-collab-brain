"""Blind two-body test v3: alternating joint refinement.

Diagnosis from v1/v2 (sealed-truth blind tests on the same scenario):
  - v1 (sequential grid+NM): secondary trapped in a spurious 40-AU
    low-frequency valley; holdout rejected (-1307%).
  - v2 (periodogram-seeded): periodogram locked onto Mars's 1.88-yr tracer
    self-residual (tracer self-noise from Saturn's 0.07% fit error), not
    Mercury's period; holdout rejected (-2.15%).
  - Deep reason: Saturn's absolute fit error (~2e-7 Msun) exceeds Mercury's
    mass. A sequential search that fixes body1 imposes a noise floor: the
    true secondary's signal sits below the primary's residual structure.

New idea (v3): block coordinate descent / alternating joint refinement.
Instead of fixing body1, alternate NM blocks: optimize body1 given body2,
then body2 given body1, iterating until the joint train MSE converges.
As body2 absorbs part of the residual structure, body1's fit can improve,
lowering the sequential noise floor. The joint 6D step and holdout gate
are kept as the final arbiters. Periodogram seeding is dropped (proven
failure mode); the secondary gets a full grid with a low-mass extension.

Protocol (sealed-truth):
  A.  One-body grid + NM on train -> body 1 (dominant).
  B.  Full secondary grid (mass x radius x phase) + NM from top-K starts,
      given body1 -> top-3 (body1, body2) pairs.
  C.  Per pair: alternating joint refinement (NM on 3D blocks, roles kept
      separated by radius) until converged or max rounds; then one joint
      6D NM on the best pair.
  D.  Holdout gate (20%): two-source must beat one-source by >= 20%.
  E.  Unseal truth for scoring.

Run from the source_upload/ directory:
  python3 /path/to/blind_two_body_v3_test.py
"""
import sys
import math
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent / "source_upload"))

from gravity_mapper.catalog.catalog_two_body_recovery import (
    SCENARIO_ID,
    TRAIN_FRACTION,
    TWO_SOURCE_HOLDOUT_IMPROVEMENT_REQUIRED,
    PHASE_STEPS,
    Candidate,
    score,
    flatten_rows,
    split_rows,
    scenario_paths,
    build_system,
)
from gravity_mapper.catalog.catalog_recovery import (
    MASS_GRID,
    RADIUS_GRID,
    load_solver_inputs,
)
from gravity_mapper.catalog.scenario_simulator import (
    DT, load_json as sim_load_json,
)

TOP_K = 8
TOP_PAIRS = 3
ALT_ROUNDS_MAX = 12
ALT_REL_TOL = 1e-4  # stop when a full alternation round improves < this
ONE_BODY_BOUNDS = [(-6.0, -2.7), (0.3, 35.0), (0.0, 2.0 * math.pi)]
SECONDARY_BOUNDS = [(-8.0, -2.7), (0.15, 35.0), (0.0, 2.0 * math.pi)]
# low-mass extension for the secondary grid (secondaries are smaller);
# the solver does not know the true secondary mass.
MASS_GRID_2 = (5.0e-8, 1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 5.0e-5,
               1.0e-4, 2.5e-4, 5.0e-4)


def angle_error(first: float, second: float) -> float:
    return abs((first - second + math.pi) % (2.0 * math.pi) - math.pi)


def c2x(c: Candidate):
    return np.array([math.log10(c.mass_solar), c.radius_au, c.phase_rad])


def x2c(x) -> Candidate:
    return Candidate(mass_solar=10.0 ** x[0], radius_au=float(x[1]),
                     phase_rad=float(x[2] % (2.0 * math.pi)))


def sanitize(o):
    """Recursively convert numpy scalars to plain Python types for JSON."""
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return o


def main() -> dict:
    inference_manifest, observation_bundle = load_solver_inputs(SCENARIO_ID)
    if observation_bundle["withheld_truth_available_to_solver"] is not False:
        raise RuntimeError("withheld truth exposed to solver")
    all_rows = flatten_rows(observation_bundle)
    train_rows, holdout_rows = split_rows(all_rows)

    def refine(train_rows, manifest, fixed, cand0, bounds, label,
               maxiter=400):
        def f(x):
            return score(train_rows, manifest, fixed + (x2c(x),))
        res = minimize(f, c2x(cand0), method="Nelder-Mead", bounds=bounds,
                       options={"maxiter": maxiter, "xatol": 1e-5,
                                "fatol": 1e-14})
        c = x2c(res.x)
        print(f"  {label}: {res.fun:.3e} ({res.nit} iters, ok={res.success})",
              flush=True)
        return c, res.fun

    # ---- Stage A: body 1 (identical to v2) ----
    print("Stage A: one-body grid + refinement", flush=True)
    scored = []
    for mass in MASS_GRID:
        for radius in RADIUS_GRID:
            for pi in range(PHASE_STEPS):
                c = Candidate(mass_solar=mass, radius_au=radius,
                              phase_rad=2.0 * math.pi * pi / PHASE_STEPS)
                scored.append((score(train_rows, inference_manifest, (c,)), c))
    scored.sort(key=lambda t: t[0])
    r1 = []
    for k, (_, c) in enumerate(scored[:TOP_K]):
        cc, mm = refine(train_rows, inference_manifest, (), c,
                        ONE_BODY_BOUNDS, f"A#{k}")
        r1.append((mm, cc))
    r1.sort(key=lambda t: t[0])
    body1, mse1 = r1[0][1], r1[0][0]
    print(f"  body1 = ({body1.mass_solar:.3e}, {body1.radius_au:.3f}, "
          f"{body1.phase_rad:.4f}) train MSE {mse1:.3e}", flush=True)

    # ---- Stage B: full secondary grid + NM, keep top pairs ----
    print("Stage B: secondary full grid + refinement", flush=True)
    scored2 = []
    for mass in MASS_GRID_2:
        for radius in RADIUS_GRID:
            for pi in range(PHASE_STEPS):
                c = Candidate(mass_solar=mass, radius_au=radius,
                              phase_rad=2.0 * math.pi * pi / PHASE_STEPS)
                scored2.append(
                    (score(train_rows, inference_manifest, (body1, c)), c))
    scored2.sort(key=lambda t: t[0])
    print(f"  coarse best train MSE = {scored2[0][0]:.3e}", flush=True)
    r2 = []
    for k, (_, c) in enumerate(scored2[:TOP_K]):
        cc, mm = refine(train_rows, inference_manifest, (body1,), c,
                        SECONDARY_BOUNDS, f"B#{k}")
        r2.append((mm, cc))
    r2.sort(key=lambda t: t[0])
    for k, (mm, cc) in enumerate(r2[:TOP_PAIRS]):
        print(f"  pair#{k}: body2=({cc.mass_solar:.3e}, {cc.radius_au:.3f}, "
              f"{cc.phase_rad:.4f}) train MSE {mm:.3e}", flush=True)

    # ---- Stage C: alternating joint refinement per pair ----
    print("Stage C: alternating joint refinement", flush=True)

    def ordered(c1, c2):
        return (c1, c2) if c1.radius_au > c2.radius_au else (c2, c1)

    def bounds_for(outer, inner):
        b_out = [(-6.0, -2.7),
                 (max(inner.radius_au * 1.5, 1.0), 40.0),
                 (0.0, 2.0 * math.pi)]
        b_in = [(-8.0, -2.7), (0.2, outer.radius_au / 1.5),
                (0.0, 2.0 * math.pi)]
        return b_out, b_in

    def alternating(outer0, inner0, label, maxiter_block=300):
        outer, inner = outer0, inner0
        mse_prev = score(train_rows, inference_manifest, (outer, inner))
        rounds = 0
        for rounds in range(1, ALT_ROUNDS_MAX + 1):
            b_out, b_in = bounds_for(outer, inner)
            # block 1: optimize outer given inner
            def f_out(x):
                return score(train_rows, inference_manifest,
                             (x2c(x), inner))
            res = minimize(f_out, c2x(outer), method="Nelder-Mead",
                           bounds=b_out,
                           options={"maxiter": maxiter_block, "xatol": 1e-5,
                                    "fatol": 1e-14})
            outer = x2c(res.x)
            # block 2: optimize inner given outer
            def f_in(x):
                return score(train_rows, inference_manifest,
                             (outer, x2c(x)))
            res = minimize(f_in, c2x(inner), method="Nelder-Mead",
                           bounds=b_in,
                           options={"maxiter": maxiter_block, "xatol": 1e-5,
                                    "fatol": 1e-14})
            inner = x2c(res.x)
            outer, inner = ordered(outer, inner)
            mse = score(train_rows, inference_manifest, (outer, inner))
            rel = (mse_prev - mse) / max(mse_prev, 1e-30)
            print(f"  {label} round {rounds}: train MSE {mse:.3e} "
                  f"(rel improve {rel:.2e})", flush=True)
            if rel < ALT_REL_TOL:
                break
            mse_prev = mse
        return outer, inner, mse, rounds

    alt_results = []
    for k, (mm, cc) in enumerate(r2[:TOP_PAIRS]):
        o0, i0 = ordered(body1, cc)
        outer, inner, mse, rounds = alternating(o0, i0, f"alt#{k}")
        alt_results.append((mse, outer, inner, rounds))
    alt_results.sort(key=lambda t: t[0])
    best_mse, best_outer, best_inner, best_rounds = alt_results[0]
    print(f"  best after alternation: train MSE {best_mse:.3e} "
          f"({best_rounds} rounds)", flush=True)
    print(f"    outer=({best_outer.mass_solar:.3e}, {best_outer.radius_au:.3f}, "
          f"{best_outer.phase_rad:.4f})", flush=True)
    print(f"    inner=({best_inner.mass_solar:.3e}, {best_inner.radius_au:.3f}, "
          f"{best_inner.phase_rad:.4f})", flush=True)

    # joint 6D polish on the best pair
    print("Stage C2: joint 6D refinement", flush=True)
    x0 = np.concatenate([c2x(best_outer), c2x(best_inner)])
    b_outer, b_inner = bounds_for(best_outer, best_inner)

    def f6(x):
        return score(train_rows, inference_manifest, (x2c(x[:3]), x2c(x[3:])))

    res = minimize(f6, x0, method="Nelder-Mead", bounds=b_outer + b_inner,
                   options={"maxiter": 800, "xatol": 1e-5, "fatol": 1e-14})
    j_outer, j_inner = x2c(res.x[:3]), x2c(res.x[3:])
    print(f"  joint train MSE = {res.fun:.3e} ({res.nit} iters, "
          f"ok={res.success})", flush=True)

    # ---- Stage D: holdout gate ----
    one_holdout = score(holdout_rows, inference_manifest, (body1,))
    two_holdout = score(holdout_rows, inference_manifest, (j_outer, j_inner))
    improvement = (one_holdout - two_holdout) / max(one_holdout, 1e-30)
    accepted = bool(improvement >= TWO_SOURCE_HOLDOUT_IMPROVEMENT_REQUIRED
                    and two_holdout < one_holdout)
    print(f"  holdout: one {one_holdout:.3e} vs two {two_holdout:.3e} "
          f"({improvement:.2%}), accepted={accepted}", flush=True)

    # ---- Stage E: unseal truth ----
    _, truth_path, _ = scenario_paths(SCENARIO_ID)
    truth = sim_load_json(truth_path)["withheld_objects"]
    cands = sorted([j_outer, j_inner], key=lambda c: c.radius_au)
    truths = sorted(truth, key=lambda t: float(t["orbital_radius_au"]))
    errs = []
    for c, t in zip(cands, truths):
        me = abs(c.mass_solar - float(t["mass_solar"])) / float(t["mass_solar"])
        re_ = (abs(c.radius_au - float(t["orbital_radius_au"]))
               / float(t["orbital_radius_au"]))
        pe = angle_error(c.phase_rad, float(t["phase_rad"]))
        errs.append((me, re_, pe, t["object_id"]))
        print(f"  {t['object_id']}: mass_err {me:.2%}, radius_err {re_:.2%}, "
              f"phase_err {pe:.4f}", flush=True)
    recovered = bool(accepted and len(truths) == 2 and all(
        me <= 0.75 and re_ <= 0.40 and pe <= 0.60 for me, re_, pe, _ in errs))

    result = {
        "scenario_id": SCENARIO_ID,
        "method": "alternating_joint_refinement",
        "stage_a": {"mass_solar": body1.mass_solar,
                    "radius_au": body1.radius_au,
                    "phase_rad": body1.phase_rad, "train_mse": mse1},
        "alternation_rounds": best_rounds,
        "alt_train_mse": best_mse,
        "outer": {"mass_solar": j_outer.mass_solar,
                  "radius_au": j_outer.radius_au,
                  "phase_rad": j_outer.phase_rad},
        "inner": {"mass_solar": j_inner.mass_solar,
                  "radius_au": j_inner.radius_au,
                  "phase_rad": j_inner.phase_rad},
        "joint_train_mse": res.fun,
        "one_source_holdout_mse": one_holdout,
        "two_source_holdout_mse": two_holdout,
        "two_source_improvement_fraction": improvement,
        "two_source_accepted": accepted,
        "per_body_errors": [
            {"truth_id": tid, "mass_relative_error": me,
             "radius_relative_error": re_, "phase_absolute_error": pe}
            for me, re_, pe, tid in errs],
        "recovered": recovered,
    }
    out = Path(__file__).resolve().parent / "blind_two_body_v3_result.json"
    out.write_text(json.dumps(sanitize(result), indent=2))
    print(f"saved -> {out}\nRECOVERED = {recovered}")
    return result


if __name__ == "__main__":
    main()
