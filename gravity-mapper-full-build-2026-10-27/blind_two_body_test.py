"""Blind two-body optimizer test for Gravity Mapper catalog recovery.

Extends the proven one-body fix (grid + Nelder-Mead) to two hidden bodies.

Protocol (sealed-truth):
  A. One-body grid + NM on train -> body 1 (dominant).
  B. With body 1 fixed, grid + NM for body 2 on train.
  C. Joint 6D Nelder-Mead refinement of (body1, body2) on train.
  D. Holdout validation: two-source must beat one-source by >=20%.
  E. ONLY THEN unseal truth; greedy match by radius; score vs
     mass<=75%, radius<=40%, phase<=0.60 rad (original tolerances).

Run from the source_upload/ directory:
  python3 /path/to/blind_two_body_test.py
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
    load_json,
)
from gravity_mapper.catalog.catalog_recovery import (
    MASS_GRID,
    RADIUS_GRID,
    load_solver_inputs,
)
from gravity_mapper.catalog.scenario_simulator import load_json as sim_load_json

TOP_K = 8
ONE_BODY_BOUNDS = [(-6.0, -2.7), (0.3, 35.0), (0.0, 2.0 * math.pi)]


def angle_error(first: float, second: float) -> float:
    return abs((first - second + math.pi) % (2.0 * math.pi) - math.pi)


def c2x(c: Candidate):
    return np.array([math.log10(c.mass_solar), c.radius_au, c.phase_rad])


def x2c(x) -> Candidate:
    return Candidate(mass_solar=10.0 ** x[0], radius_au=float(x[1]),
                     phase_rad=float(x[2] % (2.0 * math.pi)))


def main() -> dict:
    inference_manifest, observation_bundle = load_solver_inputs(SCENARIO_ID)
    if observation_bundle["withheld_truth_available_to_solver"] is not False:
        raise RuntimeError("withheld truth exposed to solver")
    all_rows = flatten_rows(observation_bundle)
    train_rows, holdout_rows = split_rows(all_rows)

    def grid_search(train_rows, manifest, fixed=()):
        """Brute-force grid; `fixed` = tuple of already-fit Candidates."""
        scored = []
        for mass in MASS_GRID:
            for radius in RADIUS_GRID:
                for pi in range(PHASE_STEPS):
                    cand = Candidate(mass_solar=mass, radius_au=radius,
                                     phase_rad=2.0 * math.pi * pi / PHASE_STEPS)
                    mse = score(train_rows, manifest, fixed + (cand,))
                    scored.append((mse, cand))
        scored.sort(key=lambda t: t[0])
        return scored

    def refine_single(train_rows, manifest, fixed, cand0, bounds, label):
        def f(x):
            return score(train_rows, manifest, fixed + (x2c(x),))
        res = minimize(f, c2x(cand0), method="Nelder-Mead", bounds=bounds,
                       options={"maxiter": 400, "xatol": 1e-5, "fatol": 1e-14})
        c = x2c(res.x)
        print(f"  {label}: {res.fun:.3e} ({res.nit} iters, ok={res.success})", flush=True)
        return c, res.fun

    # ---- Stage A: body 1 ----
    print("Stage A: one-body grid + refinement", flush=True)
    g1 = grid_search(train_rows, inference_manifest)
    print(f"  coarse best train MSE = {g1[0][0]:.3e}", flush=True)
    r1 = []
    for k, (_, c) in enumerate(g1[:TOP_K]):
        cc, mm = refine_single(train_rows, inference_manifest, (), c, ONE_BODY_BOUNDS, f"A#{k}")
        r1.append((mm, cc))
    r1.sort(key=lambda t: t[0])
    body1, mse1 = r1[0][1], r1[0][0]
    print(f"  body1 = ({body1.mass_solar:.3e}, {body1.radius_au:.3f}, "
          f"{body1.phase_rad:.4f}) train MSE {mse1:.3e}", flush=True)

    # ---- Stage B: body 2 with body 1 fixed ----
    print("Stage B: second-body grid + refinement (body1 fixed)", flush=True)
    g2 = grid_search(train_rows, inference_manifest, fixed=(body1,))
    print(f"  coarse best train MSE = {g2[0][0]:.3e}", flush=True)
    r2 = []
    for k, (_, c) in enumerate(g2[:TOP_K]):
        cc, mm = refine_single(train_rows, inference_manifest, (body1,), c,
                               ONE_BODY_BOUNDS, f"B#{k}")
        r2.append((mm, cc))
    r2.sort(key=lambda t: t[0])
    body2, mse2 = r2[0][1], r2[0][0]
    print(f"  body2 = ({body2.mass_solar:.3e}, {body2.radius_au:.3f}, "
          f"{body2.phase_rad:.4f}) train MSE {mse2:.3e}", flush=True)

    # ---- Stage C: joint 6D refinement ----
    print("Stage C: joint 6D refinement", flush=True)
    # order outer-first to avoid label switching; set radius bounds apart
    outer, inner = (body1, body2) if body1.radius_au > body2.radius_au else (body2, body1)
    x0 = np.concatenate([c2x(outer), c2x(inner)])
    b_outer = [(-6.0, -2.7), (max(inner.radius_au * 1.5, 1.0), 40.0), (0.0, 2 * math.pi)]
    b_inner = [(-8.0, -2.7), (0.2, outer.radius_au / 1.5), (0.0, 2 * math.pi)]

    def f6(x):
        co = x2c(x[:3])
        ci = x2c(x[3:])
        return score(train_rows, inference_manifest, (co, ci))

    res = minimize(f6, x0, method="Nelder-Mead", bounds=b_outer + b_inner,
                   options={"maxiter": 800, "xatol": 1e-5, "fatol": 1e-14})
    j_outer, j_inner = x2c(res.x[:3]), x2c(res.x[3:])
    print(f"  joint train MSE = {res.fun:.3e} ({res.nit} iters, ok={res.success})", flush=True)
    print(f"  outer = ({j_outer.mass_solar:.3e}, {j_outer.radius_au:.3f}, {j_outer.phase_rad:.4f})",
          flush=True)
    print(f"  inner = ({j_inner.mass_solar:.3e}, {j_inner.radius_au:.3f}, {j_inner.phase_rad:.4f})",
          flush=True)

    # ---- Stage D: holdout validation ----
    one_holdout = score(holdout_rows, inference_manifest, (body1,))
    two_holdout = score(holdout_rows, inference_manifest, (j_outer, j_inner))
    improvement = (one_holdout - two_holdout) / max(one_holdout, 1e-30)
    accepted = (improvement >= TWO_SOURCE_HOLDOUT_IMPROVEMENT_REQUIRED
                and two_holdout < one_holdout)
    print(f"  one-source holdout {one_holdout:.3e}, two-source {two_holdout:.3e}, "
          f"improvement {improvement:.2%}, accepted={accepted}", flush=True)

    # ---- Stage E: unseal truth for scoring ----
    _, truth_path, _ = scenario_paths(SCENARIO_ID)
    truth = sim_load_json(truth_path)["withheld_objects"]
    # greedy match by radius
    cands = sorted([j_outer, j_inner], key=lambda c: c.radius_au)
    truths = sorted(truth, key=lambda t: float(t["orbital_radius_au"]))
    errs = []
    for c, t in zip(cands, truths):
        me = abs(c.mass_solar - float(t["mass_solar"])) / float(t["mass_solar"])
        re_ = abs(c.radius_au - float(t["orbital_radius_au"])) / float(t["orbital_radius_au"])
        pe = angle_error(c.phase_rad, float(t["phase_rad"]))
        errs.append((me, re_, pe, t["object_id"]))
        print(f"  matched {t['object_id']}: mass_err {me:.2%}, radius_err {re_:.2%}, "
              f"phase_err {pe:.4f} rad", flush=True)
    recovered = (accepted and len(truths) == 2 and all(
        me <= 0.75 and re_ <= 0.40 and pe <= 0.60 for me, re_, pe, _ in errs))

    result = {
        "scenario_id": SCENARIO_ID,
        "method": "sequential_grid_nm_plus_joint_6d",
        "body1": {"mass_solar": body1.mass_solar, "radius_au": body1.radius_au,
                  "phase_rad": body1.phase_rad},
        "outer": {"mass_solar": j_outer.mass_solar, "radius_au": j_outer.radius_au,
                  "phase_rad": j_outer.phase_rad},
        "inner": {"mass_solar": j_inner.mass_solar, "radius_au": j_inner.radius_au,
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
    out = Path(__file__).resolve().parent / "blind_two_body_result.json"
    out.write_text(json.dumps(result, indent=2))
    print(f"saved -> {out}\nRECOVERED = {recovered}")
    return result


if __name__ == "__main__":
    main()
