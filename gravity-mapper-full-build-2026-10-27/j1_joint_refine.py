"""Experiment J1: joint 6-parameter refinement for two-body recovery.

v3 tried SEQUENTIAL (fit primary, then secondary on residuals) and ALTERNATING
(fit body1 | body2, then body2 | body1, repeat). Both failed: the primary
absorbs the secondary, and alternation converged in 1 round.

This tests JOINT optimization: all 6 parameters (2 x mass, radius, phase)
refined simultaneously by Nelder-Mead, starting from one-body fit + grid
secondary. If joint beats sequential, the wall is optimization, not physics.
"""
import sys, os, math, json
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
import numpy as np
from scipy.optimize import minimize
from residual_statistic import (load_rows, c2x, x2c, ONE_BOUNDS,
                                SEC_MASSES, SEC_RADII, SEC_PHASES)
from gravity_mapper.catalog.catalog_two_body_recovery import Candidate, score

# one-body fit from Procedure P (matches v3 stage_a)
PRIMARY_0 = Candidate(mass_solar=2.85998385203324e-4,
                      radius_au=9.582954521237722,
                      phase_rad=4.750737668790862)


def j2x(c1, c2):
    return np.concatenate([c2x(c1), c2x(c2)])


def x2j(x):
    return x2c(x[:3]), x2c(x[3:])


def joint_refine(train_rows, manifest, c1_init, c2_init, maxiter=500):
    bounds = ONE_BOUNDS + ONE_BOUNDS

    def f(x):
        c1, c2 = x2j(x)
        return score(train_rows, manifest, (c1, c2))

    res = minimize(f, j2x(c1_init, c2_init), method='Nelder-Mead',
                   bounds=bounds,
                   options={'maxiter': maxiter, 'xatol': 1e-5, 'fatol': 1e-14})
    c1, c2 = x2j(res.x)
    return c1, c2, res.fun, res.nit


def main():
    manifest, train_rows, holdout_rows = load_rows()
    mse1 = score(train_rows, manifest, (PRIMARY_0,))
    print(f"one-body train MSE: {mse1:.3e}", flush=True)

    # Step 1: fast sequential grid to find promising secondaries
    print("Step 1: sequential secondary grid...", flush=True)
    scored = []
    for m in SEC_MASSES:
        for r in SEC_RADII:
            for pi in range(SEC_PHASES):
                c2 = Candidate(m, r, 2 * math.pi * pi / SEC_PHASES)
                s = score(train_rows, manifest, (PRIMARY_0, c2))
                scored.append((s, c2))
    scored.sort(key=lambda t: t[0])
    top = [c2 for _, c2 in scored[:12]]
    print(f"  best sequential: {scored[0][0]:.3e}", flush=True)

    # Step 2: joint-refine all 6 params from each top candidate
    print("Step 2: joint 6-param refinement...", flush=True)
    results = []
    for i, c2_init in enumerate(top):
        c1, c2, fun, nit = joint_refine(train_rows, manifest,
                                        PRIMARY_0, c2_init, maxiter=400)
        hmse = score(holdout_rows, manifest, (c1, c2))
        results.append((fun, hmse, c1, c2, nit))
        print(f"  [{i}] mse={fun:.3e} holdout={hmse:.3e} "
              f"c1=({c1.mass_solar:.3e},{c1.radius_au:.2f}) "
              f"c2=({c2.mass_solar:.3e},{c2.radius_au:.2f}) nit={nit}",
              flush=True)
    results.sort(key=lambda t: t[0])
    hmse1 = score(holdout_rows, manifest, (PRIMARY_0,))
    print(f"\n=== best joint vs one-body (holdout {hmse1:.3e}) ===")
    for fun, hmse, c1, c2, nit in results[:5]:
        print(f"mse={fun:.3e} holdout={hmse:.3e} "
              f"improvement={(mse1-fun)/mse1:.3f}")
        print(f"  body1: m={c1.mass_solar:.6e} r={c1.radius_au:.4f} p={c1.phase_rad:.4f}")
        print(f"  body2: m={c2.mass_solar:.6e} r={c2.radius_au:.4f} p={c2.phase_rad:.4f}")
    out = [{"mse": f, "holdout": h,
            "b1": [c1.mass_solar, c1.radius_au, c1.phase_rad],
            "b2": [c2.mass_solar, c2.radius_au, c2.phase_rad]}
           for f, h, c1, c2, _ in results[:5]]
    json.dump({"one_body_mse": mse1, "one_body_holdout": hmse1,
               "joint_top5": out},
              open("j1_results.json", "w"), indent=1)
    print("\nsaved j1_results.json", flush=True)


if __name__ == "__main__":
    main()
