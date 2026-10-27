"""Experiment J2: joint fit with secondary mass extended DOWN to Mercury scale.

J1 found: joint NM pushes secondary mass to the lower grid bound (1e-5 Msun)
and stops; train MSE worsens, holdout collapses. The data rejects a second
body at >=1e-5 Msun. But Mercury (1.66e-7 Msun) is 60x below the grid floor.

This extends the secondary mass range to [1e-9, 1e-3] (log) and starts NM
from Mercury-like secondaries. Decisive question: does NM converge TO a
Mercury-like solution, or push mass -> 0 (no second body at any scale)?
"""
import sys, os, math, json
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
import numpy as np
from scipy.optimize import minimize
from residual_statistic import load_rows
from j1_joint_refine import PRIMARY_0, j2x, x2j
from gravity_mapper.catalog.catalog_two_body_recovery import Candidate, score

# extended bounds: mass log10 in [-9, -3], radius [0.2, 40], phase [0, 2pi]
LO_M, HI_M = -9.0, -3.0
LO_R, HI_R = 0.2, 40.0


def e2x(c):
    return np.array([(math.log10(c.mass_solar) - LO_M) / (HI_M - LO_M),
                     (c.radius_au - LO_R) / (HI_R - LO_R),
                     c.phase_rad / (2 * math.pi)])


def x2e(x):
    return Candidate(10 ** (LO_M + x[0] * (HI_M - LO_M)),
                     LO_R + x[1] * (HI_R - LO_R),
                     x[2] * 2 * math.pi % (2 * math.pi))


def joint_refine_ext(train_rows, manifest, c1_init, c2_init, maxiter=600):
    # body1: RAW units with ONE_BOUNDS (c2x is not normalized!);
    # body2: normalized extended transform with [(0,1)]^3
    from residual_statistic import c2x, x2c, ONE_BOUNDS
    x0 = np.concatenate([c2x(c1_init), e2x(c2_init)])
    bnd = list(ONE_BOUNDS) + [(0, 1)] * 3

    def f(x):
        c1 = x2c(x[:3])
        c2 = x2e(x[3:])
        return score(train_rows, manifest, (c1, c2))

    res = minimize(f, x0, method='Nelder-Mead', bounds=bnd,
                   options={'maxiter': maxiter, 'xatol': 1e-5, 'fatol': 1e-14})
    c1 = x2c(res.x[:3])
    c2 = x2e(res.x[3:])
    return c1, c2, res.fun, res.nit


def main():
    manifest, train_rows, holdout_rows = load_rows()
    mse1 = score(train_rows, manifest, (PRIMARY_0,))
    hmse1 = score(holdout_rows, manifest, (PRIMARY_0,))
    print(f"one-body: train {mse1:.3e} holdout {hmse1:.3e}", flush=True)

    # starts: Mercury-like + brackets
    starts = [
        Candidate(1.6e-7, 0.39, 1.0),    # Mercury-like
        Candidate(1.6e-7, 0.39, 4.0),    # Mercury-like, other phase
        Candidate(1e-6, 1.0, 2.0),
        Candidate(1e-7, 5.0, 0.5),
        Candidate(1e-8, 0.5, 3.0),
        Candidate(3e-7, 2.0, 5.0),
    ]
    results = []
    for i, c2_init in enumerate(starts):
        c1, c2, fun, nit = joint_refine_ext(train_rows, manifest,
                                            PRIMARY_0, c2_init)
        hmse = score(holdout_rows, manifest, (c1, c2))
        results.append((fun, hmse, c1, c2))
        print(f"[{i}] init m={c2_init.mass_solar:.1e} r={c2_init.radius_au} -> "
              f"mse={fun:.3e} (vs 1-body {mse1:.3e}) holdout={hmse:.3e}\n"
              f"    b1: m={c1.mass_solar:.4e} r={c1.radius_au:.3f}\n"
              f"    b2: m={c2.mass_solar:.4e} r={c2.radius_au:.3f} p={c2.phase_rad:.3f}",
              flush=True)
    results.sort(key=lambda t: t[0])
    json.dump({"one_body_train": mse1, "one_body_holdout": hmse1,
               "results": [{"mse": f, "holdout": h,
                            "b1": [c1.mass_solar, c1.radius_au, c1.phase_rad],
                            "b2": [c2.mass_solar, c2.radius_au, c2.phase_rad]}
                           for f, h, c1, c2 in results]},
              open("j2_results.json", "w"), indent=1)
    print("saved j2_results.json", flush=True)


if __name__ == "__main__":
    main()
