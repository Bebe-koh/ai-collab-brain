"""Diagnosis: start joint NM FROM the synthetic truth (V2-redo).

If NM stays at truth -> optimization problem (bad basins).
If NM drifts away -> model problem (circular two-body can't fit the dynamics).
Uses synthetic truth (known, not blind) — diagnosis only.
"""
import sys, os
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
from residual_statistic import load_rows
from validate_pipeline import simulate_bodies, SATURN
from j2_mercury_scale import joint_refine_ext
from gravity_mapper.catalog.catalog_two_body_recovery import Candidate, score

manifest, real_train, real_holdout = load_rows()
earth_truth = Candidate(mass_solar=3.0e-6, radius_au=2.5, phase_rad=2.0)
rows = simulate_bodies(manifest, real_train, (SATURN, earth_truth), seed=45)

# score AT truth
mse_truth = score(rows, manifest, (SATURN, earth_truth))
hmse_truth = score(real_holdout, manifest, (SATURN, earth_truth))
print(f"At truth: train={mse_truth:.3e} holdout={hmse_truth:.3e}", flush=True)

# NM from truth — does it stay?
c1, c2, fun, nit = joint_refine_ext(rows, manifest, SATURN, earth_truth,
                                   maxiter=600)
hmse = score(real_holdout, manifest, (c1, c2))
print(f"NM from truth: train={fun:.3e} holdout={hmse:.3e} nit={nit}", flush=True)
print(f"  b1: m={c1.mass_solar:.4e} r={c1.radius_au:.3f}", flush=True)
print(f"  b2: m={c2.mass_solar:.4e} r={c2.radius_au:.3f} p={c2.phase_rad:.3f}",
      flush=True)
print(f"  truth b2: m=3.0e-6 r=2.5", flush=True)
