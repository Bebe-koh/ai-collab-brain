"""J3: blind two-body pipeline. No Mercury-informed starts.

1. One-body fit via Procedure P (blind).
2. Extended sequential grid (masses 1e-9..1e-3 log, radii 0.2..40, phases 8)
   to RANK secondary seeds.
3. Joint-refine (all 6 params) the top 15 seeds.
4. Model selection by HOLDOUT: best 2-body vs 1-body.

If the best 2-body holdout beats 1-body holdout and the secondary is
Mercury-scale, the pipeline works blind.
"""
import sys, os, math, json
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
import numpy as np
from residual_statistic import load_rows, one_body_fit
from j2_mercury_scale import joint_refine_ext
from gravity_mapper.catalog.catalog_two_body_recovery import Candidate, score

# extended grid (blind: covers 6 dex in mass)
GRID_MASSES = [10.0**e for e in (-9, -8, -7, -6, -5, -4, -3)]
GRID_RADII = [0.3, 0.6, 1.0, 2.0, 5.0, 10.0, 20.0, 35.0]
N_PHASE = 6
TOP_K = 15


def main():
    manifest, train_rows, holdout_rows = load_rows()
    print("Step 1: blind one-body fit...", flush=True)
    c1, _ = one_body_fit(train_rows, manifest)
    mse1 = score(train_rows, manifest, (c1,))
    hmse1 = score(holdout_rows, manifest, (c1,))
    print(f"  primary: m={c1.mass_solar:.4e} r={c1.radius_au:.3f} "
          f"train={mse1:.3e} holdout={hmse1:.3e}", flush=True)

    print("Step 2: extended sequential grid for seeds...", flush=True)
    scored = []
    for m in GRID_MASSES:
        for r in GRID_RADII:
            for pi in range(N_PHASE):
                c2 = Candidate(m, r, 2 * math.pi * pi / N_PHASE)
                s = score(train_rows, manifest, (c1, c2))
                scored.append((s, c2))
    scored.sort(key=lambda t: t[0])
    print(f"  grid size {len(scored)}, best sequential {scored[0][0]:.3e} "
          f"(1-body {mse1:.3e})", flush=True)
    print("  top-5 seeds (mass, radius):",
          [(f"{c.mass_solar:.1e}", round(c.radius_au, 2)) for _, c in scored[:5]],
          flush=True)

    print(f"Step 3: joint-refine top {TOP_K}...", flush=True)
    results = []
    for i, (_, c2_init) in enumerate(scored[:TOP_K]):
        jc1, jc2, fun, nit = joint_refine_ext(train_rows, manifest, c1, c2_init)
        hmse = score(holdout_rows, manifest, (jc1, jc2))
        results.append((fun, hmse, jc1, jc2))
        print(f"  [{i}] train={fun:.3e} holdout={hmse:.3e} "
              f"b2: m={jc2.mass_solar:.3e} r={jc2.radius_au:.3f}", flush=True)

    print("Step 4: holdout model selection...", flush=True)
    results.sort(key=lambda t: t[1])  # by holdout
    best = results[0]
    print(f"  1-body holdout: {hmse1:.3e}", flush=True)
    print(f"  best 2-body holdout: {best[1]:.3e} "
          f"(train {best[0]:.3e})", flush=True)
    print(f"  b1: m={best[2].mass_solar:.6e} r={best[2].radius_au:.4f} "
          f"p={best[2].phase_rad:.4f}", flush=True)
    print(f"  b2: m={best[3].mass_solar:.6e} r={best[3].radius_au:.4f} "
          f"p={best[3].phase_rad:.4f}", flush=True)
    verdict = "TWO_BODY" if best[1] < hmse1 else "ONE_BODY"
    print(f"  VERDICT: {verdict}", flush=True)
    json.dump({"one_body": {"train": mse1, "holdout": hmse1,
                           "c": [c1.mass_solar, c1.radius_au, c1.phase_rad]},
               "verdict": verdict,
               "best_two": {"train": best[0], "holdout": best[1],
                            "b1": [best[2].mass_solar, best[2].radius_au, best[2].phase_rad],
                            "b2": [best[3].mass_solar, best[3].radius_au, best[3].phase_rad]}},
              open("j3_results.json", "w"), indent=1)
    print("saved j3_results.json", flush=True)


if __name__ == "__main__":
    main()
