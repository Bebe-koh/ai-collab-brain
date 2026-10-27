"""Blind two-body test v2: periodogram-seeded secondary search.

Addresses the weak-signal trapping failure of the sequential approach
(blind_two_body_test.py), where the Stage B grid+NM locked onto a spurious
35-AU low-frequency fit instead of the true inner secondary.

New idea: after fitting the dominant body, run Lomb-Scargle on the train
residuals. A real secondary imprints its (synodic) period as a coherent peak;
noise does not. Convert the peak period to a radius seed via Kepler III and
focus the Stage B grid there.

Protocol (sealed-truth):
  A.  One-body grid + NM on train -> body 1 (dominant).
  A2. Compute train residual time series (observed - body1-only model).
  A3. Lomb-Scargle periodogram over 0.1-5 yr; top peak -> radius seed.
      If no peak above the bootstrap noise floor, fall back to full grid.
  B.  Focused grid (mass x radius-seed neighborhood x phase) + NM -> body 2.
  C.  Joint 6D NM refinement.
  D.  Holdout gate (20%). E. Unseal truth for scoring.

Run from the source_upload/ directory:
  python3 /path/to/blind_two_body_v2_test.py
"""
import sys
import math
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.signal import lombscargle

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
    DT, load_json as sim_load_json, step_verlet,
)

TOP_K = 8
ONE_BODY_BOUNDS = [(-6.0, -2.7), (0.3, 35.0), (0.0, 2.0 * math.pi)]
SECONDARY_BOUNDS = [(-8.0, -2.7), (0.15, 35.0), (0.0, 2.0 * math.pi)]
# extended low-mass end for the secondary search (secondaries are smaller)
MASS_GRID_2 = (1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 5.0e-5,
               1.0e-4, 2.5e-4, 5.0e-4)


def angle_error(first: float, second: float) -> float:
    return abs((first - second + math.pi) % (2.0 * math.pi) - math.pi)


def c2x(c: Candidate):
    return np.array([math.log10(c.mass_solar), c.radius_au, c.phase_rad])


def x2c(x) -> Candidate:
    return Candidate(mass_solar=10.0 ** x[0], radius_au=float(x[1]),
                     phase_rad=float(x[2] % (2.0 * math.pi)))


def residual_series(train_rows, manifest, fixed):
    """Return (times, residuals) with residuals[t, tracer, xy] = obs - model."""
    by_time: dict[float, list[dict]] = {}
    for row in train_rows:
        by_time.setdefault(row["time_years"], []).append(row)
    system = build_system(manifest, fixed)
    max_time = max(by_time)
    steps = int(round(max_time / DT))
    times, resids = [], []
    # tracer order for consistent indexing
    tracer_ids = sorted({r["object_id"] for r in train_rows})
    for step in range(steps + 1):
        time = round(step * DT, 10)
        if time in by_time:
            state = {b.object_id: b for b in system}
            row = [0.0] * (2 * len(tracer_ids))
            bymap = {r["object_id"]: r for r in by_time[time]}
            for i, tid in enumerate(tracer_ids):
                b = state[tid]
                r = bymap[tid]
                row[2 * i] = r["x_au"] - b.x
                row[2 * i + 1] = r["y_au"] - b.y
            times.append(time)
            resids.append(row)
        if step < steps:
            step_verlet(system)
    return np.array(times), np.array(resids), tracer_ids


def periodogram_seed(times, resids):
    """Lomb-Scargle over 0.1-5 yr; return (peak_period, peak_power, snr)."""
    periods = np.linspace(0.1, 5.0, 400)
    ang = 2.0 * np.pi / periods
    # sum power over tracers and axes
    total = np.zeros_like(periods)
    n_series = resids.shape[1]
    for s in range(n_series):
        y = resids[:, s]
        y = y - y.mean()
        if np.std(y) < 1e-18:
            continue
        total += lombscargle(times, y, ang, normalize=True)
    total /= max(n_series, 1)
    k = int(np.argmax(total))
    # SNR vs median (robust noise floor estimate)
    snr = total[k] / max(np.median(total), 1e-12)
    return periods[k], total[k], snr, periods, total


def main() -> dict:
    inference_manifest, observation_bundle = load_solver_inputs(SCENARIO_ID)
    if observation_bundle["withheld_truth_available_to_solver"] is not False:
        raise RuntimeError("withheld truth exposed to solver")
    all_rows = flatten_rows(observation_bundle)
    train_rows, holdout_rows = split_rows(all_rows)

    def refine(train_rows, manifest, fixed, cand0, bounds, label):
        def f(x):
            return score(train_rows, manifest, fixed + (x2c(x),))
        res = minimize(f, c2x(cand0), method="Nelder-Mead", bounds=bounds,
                       options={"maxiter": 400, "xatol": 1e-5, "fatol": 1e-14})
        c = x2c(res.x)
        print(f"  {label}: {res.fun:.3e} ({res.nit} iters, ok={res.success})", flush=True)
        return c, res.fun

    # ---- Stage A: body 1 (same as before) ----
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
        cc, mm = refine(train_rows, inference_manifest, (), c, ONE_BODY_BOUNDS, f"A#{k}")
        r1.append((mm, cc))
    r1.sort(key=lambda t: t[0])
    body1, mse1 = r1[0][1], r1[0][0]
    print(f"  body1 = ({body1.mass_solar:.3e}, {body1.radius_au:.3f}, "
          f"{body1.phase_rad:.4f}) train MSE {mse1:.3e}", flush=True)

    # ---- Stage A2/A3: residual periodogram ----
    print("Stage A2: residual periodogram", flush=True)
    times, resids, tids = residual_series(train_rows, inference_manifest, (body1,))
    peak_period, peak_power, snr, periods, power = periodogram_seed(times, resids)
    print(f"  peak period {peak_period:.3f} yr, power {peak_power:.3f}, "
          f"SNR {snr:.1f} (tracers: {tids})", flush=True)
    radius_seed = peak_period ** (2.0 / 3.0)  # Kepler III, solar units
    use_seed = snr > 3.0
    print(f"  radius seed {radius_seed:.3f} AU, use_seed={use_seed}", flush=True)
    # save periodogram for the record
    np.savez(Path(__file__).resolve().parent / "periodogram.npz",
             periods=periods, power=power, times=times)

    # ---- Stage B: focused (or full) grid + NM for body 2 ----
    print("Stage B: secondary grid + refinement", flush=True)
    if use_seed:
        radii = sorted({max(radius_seed * f, 0.15) for f in (0.4, 0.6, 0.85, 1.0, 1.2, 1.6, 2.2)})
        masses = MASS_GRID_2
        print(f"  focused radii: {[f'{r:.2f}' for r in radii]}", flush=True)
    else:
        radii, masses = RADIUS_GRID, MASS_GRID
        print("  fallback: full grid (no significant peak)", flush=True)
    scored2 = []
    for mass in masses:
        for radius in radii:
            for pi in range(PHASE_STEPS):
                c = Candidate(mass_solar=mass, radius_au=radius,
                              phase_rad=2.0 * math.pi * pi / PHASE_STEPS)
                scored2.append((score(train_rows, inference_manifest, (body1, c)), c))
    scored2.sort(key=lambda t: t[0])
    print(f"  coarse best train MSE = {scored2[0][0]:.3e}", flush=True)
    r2 = []
    for k, (_, c) in enumerate(scored2[:TOP_K]):
        cc, mm = refine(train_rows, inference_manifest, (body1,), c,
                        SECONDARY_BOUNDS, f"B#{k}")
        r2.append((mm, cc))
    r2.sort(key=lambda t: t[0])
    body2, mse2 = r2[0][1], r2[0][0]
    print(f"  body2 = ({body2.mass_solar:.3e}, {body2.radius_au:.3f}, "
          f"{body2.phase_rad:.4f}) train MSE {mse2:.3e}", flush=True)

    # ---- Stage C: joint 6D refinement ----
    print("Stage C: joint 6D refinement", flush=True)
    outer, inner = (body1, body2) if body1.radius_au > body2.radius_au else (body2, body1)
    x0 = np.concatenate([c2x(outer), c2x(inner)])
    b_outer = [(-6.0, -2.7), (max(inner.radius_au * 1.5, 1.0), 40.0), (0.0, 2 * math.pi)]
    b_inner = [(-8.0, -2.7), (0.2, outer.radius_au / 1.5), (0.0, 2 * math.pi)]

    def f6(x):
        return score(train_rows, inference_manifest, (x2c(x[:3]), x2c(x[3:])))

    res = minimize(f6, x0, method="Nelder-Mead", bounds=b_outer + b_inner,
                   options={"maxiter": 800, "xatol": 1e-5, "fatol": 1e-14})
    j_outer, j_inner = x2c(res.x[:3]), x2c(res.x[3:])
    print(f"  joint train MSE = {res.fun:.3e} ({res.nit} iters, ok={res.success})", flush=True)

    # ---- Stage D: holdout gate ----
    one_holdout = score(holdout_rows, inference_manifest, (body1,))
    two_holdout = score(holdout_rows, inference_manifest, (j_outer, j_inner))
    improvement = (one_holdout - two_holdout) / max(one_holdout, 1e-30)
    accepted = (improvement >= TWO_SOURCE_HOLDOUT_IMPROVEMENT_REQUIRED
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
        re_ = abs(c.radius_au - float(t["orbital_radius_au"])) / float(t["orbital_radius_au"])
        pe = angle_error(c.phase_rad, float(t["phase_rad"]))
        errs.append((me, re_, pe, t["object_id"]))
        print(f"  {t['object_id']}: mass_err {me:.2%}, radius_err {re_:.2%}, "
              f"phase_err {pe:.4f}", flush=True)
    recovered = (accepted and len(truths) == 2 and all(
        me <= 0.75 and re_ <= 0.40 and pe <= 0.60 for me, re_, pe, _ in errs))

    result = {
        "scenario_id": SCENARIO_ID,
        "method": "periodogram_seeded_grid_nm_plus_joint_6d",
        "periodogram_peak_period_yr": peak_period,
        "periodogram_peak_snr": snr,
        "radius_seed_au": radius_seed,
        "seed_used": bool(use_seed),
        "outer": {"mass_solar": j_outer.mass_solar, "radius_au": j_outer.radius_au,
                  "phase_rad": j_outer.phase_rad},
        "inner": {"mass_solar": j_inner.mass_solar, "radius_au": j_inner.radius_au,
                  "phase_rad": j_inner.phase_rad},
        "joint_train_mse": res.fun,
        "two_source_improvement_fraction": improvement,
        "two_source_accepted": bool(accepted),
        "per_body_errors": [
            {"truth_id": tid, "mass_relative_error": me,
             "radius_relative_error": re_, "phase_absolute_error": pe}
            for me, re_, pe, tid in errs],
        "recovered": bool(recovered),
    }
    out = Path(__file__).resolve().parent / "blind_two_body_v2_result.json"
    out.write_text(json.dumps(result, indent=2))
    print(f"saved -> {out}\nRECOVERED = {recovered}")
    return result


if __name__ == "__main__":
    main()
