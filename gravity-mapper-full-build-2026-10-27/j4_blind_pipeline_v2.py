"""J4: blind pipeline v2 — adds uninformative joint starts.

Fix for the V2-redo blind spot (Earth-mass at 2.5 AU missed): when the
secondary is heavy enough to break the one-body fit, seeding joint refinement
from that broken fit fails. This version ALWAYS adds N_UNINFORMED joint
refinements from uninformative (log-uniform/random) starts across the full
6D space, alongside the seeded ones. Holdout picks the winner — no threshold
to tune, no special cases.

The seeded path still handles small secondaries (Mercury case); the
uninformative path handles heavy secondaries that wreck the one-body fit.
"""
import sys, os, math, json
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
import numpy as np
from residual_statistic import load_rows, one_body_fit
from j2_mercury_scale import joint_refine_ext
from j3_blind_pipeline import GRID_MASSES, GRID_RADII, N_PHASE, TOP_K
from gravity_mapper.catalog.catalog_two_body_recovery import Candidate, score
from input_validation import validate_rows
from tracer_attribution import attribution_report

N_UNINFORMED = 12  # uninformative joint starts (fixed seed => reproducible)


def uninformative_starts(n, seed=12345):
    """Log-uniform masses, uniform radii/phases. Body1 biased heavy."""
    rng = np.random.default_rng(seed)
    starts = []
    for _ in range(n):
        m1 = 10 ** rng.uniform(-5, -2.7)     # within ONE_BOUNDS mass range
        r1 = rng.uniform(3.0, 35.0)
        p1 = rng.uniform(0, 2 * math.pi)
        m2 = 10 ** rng.uniform(-9, -3)      # 1e-9 .. 1e-3
        r2 = rng.uniform(0.2, 40.0)
        p2 = rng.uniform(0, 2 * math.pi)
        starts.append((Candidate(m1, r1, p1), Candidate(m2, r2, p2)))
    return starts


def run_pipeline_v2(train_rows, manifest, holdout_rows, label):
    print(f"[{label}] Step 0: input validation...", flush=True)
    train_rows, _ = validate_rows(train_rows, label=label + "-train")
    holdout_rows, _ = validate_rows(holdout_rows, label=label + "-holdout")

    print(f"[{label}] Step 1: one-body fit...", flush=True)
    c1, _ = one_body_fit(train_rows, manifest)
    mse1 = score(train_rows, manifest, (c1,))
    hmse1 = score(holdout_rows, manifest, (c1,))
    print(f"[{label}]   1-body: train={mse1:.3e} holdout={hmse1:.3e}", flush=True)

    print(f"[{label}] Step 2: seed grid...", flush=True)
    scored = []
    for m in GRID_MASSES:
        for r in GRID_RADII:
            for pi in range(N_PHASE):
                c2 = Candidate(m, r, 2 * math.pi * pi / N_PHASE)
                s = score(train_rows, manifest, (c1, c2))
                scored.append((s, c2))
    scored.sort(key=lambda t: t[0])

    results = []
    print(f"[{label}] Step 3a: joint-refine top {TOP_K} seeded...", flush=True)
    for _, c2_init in scored[:TOP_K]:
        jc1, jc2, fun, _ = joint_refine_ext(train_rows, manifest, c1, c2_init)
        hmse = score(holdout_rows, manifest, (jc1, jc2))
        results.append((fun, hmse, jc1, jc2))

    print(f"[{label}] Step 3b: {N_UNINFORMED} uninformative joint starts...",
          flush=True)
    for i, (u1, u2) in enumerate(uninformative_starts(N_UNINFORMED)):
        jc1, jc2, fun, _ = joint_refine_ext(train_rows, manifest, u1, u2)
        hmse = score(holdout_rows, manifest, (jc1, jc2))
        results.append((fun, hmse, jc1, jc2))
        # order bodies by mass so b1 is the heavier (canonical labeling)
        if jc2.mass_solar > jc1.mass_solar:
            jc1, jc2 = jc2, jc1
        print(f"[{label}]   u[{i}] train={fun:.3e} holdout={hmse:.3e} "
              f"b1=({jc1.mass_solar:.2e},{jc1.radius_au:.2f}) "
              f"b2=({jc2.mass_solar:.2e},{jc2.radius_au:.2f})", flush=True)

    print(f"[{label}] Step 4: holdout model selection...", flush=True)
    # canonicalize: heavier body first
    canon = []
    for fun, hmse, a, b in results:
        if b.mass_solar > a.mass_solar:
            a, b = b, a
        canon.append((fun, hmse, a, b))
    canon.sort(key=lambda t: t[1])
    fun, hmse, jc1, jc2 = canon[0]
    verdict = "TWO_BODY" if hmse < hmse1 else "ONE_BODY"
    print(f"[{label}] VERDICT: {verdict} "
          f"(1-body {hmse1:.3e}, best 2-body {hmse:.3e})", flush=True)
    print(f"[{label}]   b1: m={jc1.mass_solar:.4e} r={jc1.radius_au:.3f}\n"
          f"[{label}]   b2: m={jc2.mass_solar:.4e} r={jc2.radius_au:.3f}",
          flush=True)
    print(f"[{label}] Step 5: tracer attribution...", flush=True)
    best_bodies = (jc1, jc2) if verdict == "TWO_BODY" else (c1,)
    flags = attribution_report(train_rows, manifest, best_bodies,
                               label=label)
    return {"verdict": verdict, "one_holdout": hmse1, "two_holdout": hmse,
            "b1": [jc1.mass_solar, jc1.radius_au, jc1.phase_rad],
            "b2": [jc2.mass_solar, jc2.radius_au, jc2.phase_rad],
            "outlier_tracers": [oid for oid, f in flags.items() if f]}


def main():
    manifest, train_rows, holdout_rows = load_rows()
    result = run_pipeline_v2(train_rows, manifest, holdout_rows, "J4-real")
    json.dump(result, open("j4_results.json", "w"), indent=1, default=str)
    print("saved j4_results.json", flush=True)


if __name__ == "__main__":
    main()
