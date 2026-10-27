#!/usr/bin/env python3
"""Modular N-body fitter validation — variant A/B re-run via the conductor.

Gravity Mapper modular N-body fitter (2026-10-24).

Variant A — two-body truth: REBOUND ias15, Sun + massless particle,
identical setup to ammonite_blind_test_note.md section 3 (same arc,
cadence, noise). The conductor should NOT escalate (Keplerian rms ~
sigma) and the fit must still PASS: no regression allowed.

Variant B — N-body truth: Sun + 8 planets live (cartesian_lm_rerun
builder, JPL Table-1 elements). Identical times and noise realization
to variant A; the ONLY difference is planetary perturbations. The
conductor MUST escalate (Keplerian rms 41x sigma) and the N-body fit
must PASS. This is the fix's success condition.

Pre-registered criterion (unchanged): |dq|/q < 1% AND |da|/a < 1% on all
3 seeds per variant. Blind discipline: the conductor sees only (t, x, y,
z); truth is opened only for scoring after each fit. A variant-B failure
is reported honestly with numbers; no tuning into passing.

Timing per rung is recorded: the rails design should keep the N-body fit
within a small multiple of the Keplerian cost.
"""
import json
import sys
import time

import numpy as np

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/real_data')
import ammonite_test as AT
import cartesian_lm_rerun as CLR
from rails_brain import PlanetRails
from conductor_brain import run_ladder

SEEDS = AT.SEEDS
T_EPOCH_YR = AT.T_EPOCH_YR
TRUTH = dict(a=248.0, e=0.734, q=248.0 * (1.0 - 0.734))


def score(fit, variant):
    dq = abs(fit['q'] - TRUTH['q']) / TRUTH['q']
    da = abs(fit['a'] - TRUTH['a']) / TRUTH['a']
    ok = bool(fit['success'] and dq < 0.01 and da < 0.01
              and 0.0 <= fit['e'] < 1.0 and fit['a'] > 0)
    return dict(variant=variant, q_fit=fit['q'], a_fit=fit['a'],
                e_fit=fit['e'], dq_rel=dq, da_rel=da,
                converged=fit['success'], nfev=fit['nfev'],
                rms_au=fit['rms_au'], passed=ok)


def run_variant(variant, rails):
    print(f"=== Variant {variant} ===", flush=True)
    results = []
    for seed in SEEDS:
        if variant == 'A':
            ts, obs = AT.make_observations(seed)
        else:
            ts, obs, dmax = CLR.make_observations_nbody(seed)
        t0 = time.time()
        res = run_ladder(ts, obs, AT.SIGMA_AU, rails, t_ref=T_EPOCH_YR,
                         seed=seed)
        wall = time.time() - t0
        r = score(res['fit'], variant)
        r['seed'] = seed
        r['path'] = res['path']
        r['escalated'] = res['escalated']
        r['keplerian_check'] = res['keplerian_check']['verdict']
        r['keplerian_check_reasons'] = res['keplerian_check']['reasons']
        r['keplerian_time_s'] = res['keplerian_time_s']
        r['nbody_check'] = (res['nbody_check']['verdict']
                            if res['nbody_check'] else None)
        r['nbody_time_s'] = res['nbody_time_s']
        r['wall_s'] = wall
        if variant == 'B':
            r['nbody_deviation_au'] = dmax
        results.append(r)
        print(f"  seed {seed}: path={r['path']} "
              f"q={r['q_fit']:.4f} (|dq|/q={r['dq_rel']:.4%}) "
              f"a={r['a_fit']:.3f} (|da|/a={r['da_rel']:.4%}) "
              f"check={r['nbody_check'] or r['keplerian_check']} "
              f"wall={wall:.1f}s -> {'PASS' if r['passed'] else 'FAIL'}",
              flush=True)
    npass = sum(r['passed'] for r in results)
    print(f"  VARIANT {variant}: {'PASS' if npass == 3 else 'FAIL'} "
          f"({npass}/3 seeds)", flush=True)
    return results


if __name__ == '__main__':
    t0 = time.time()
    rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                              cache_path=HERE + '/sealed_runs/planet_rails.npz')
    out = {'truth': {**TRUTH, 'source': 'JPL SBDB API 2026-10-14'},
           'criterion': '|dq|/q < 1% AND |da|/a < 1% on all 3 seeds',
           'seeds': SEEDS, 'sigma_au': AT.SIGMA_AU,
           'architecture': 'five brains: rails, particle, optimizer, '
                           'checker, conductor'}
    out['variant_A_twobody'] = run_variant('A', rails)
    out['variant_B_nbody'] = run_variant('B', rails)
    json.dump(out, open(HERE + '/sealed_runs/nbody_fitter_rerun_results.json',
                        'w'), indent=1)
    a_pass = all(r['passed'] for r in out['variant_A_twobody'])
    b_pass = all(r['passed'] for r in out['variant_B_nbody'])
    print(f"\nOVERALL A (two-body truth): {'PASS' if a_pass else 'FAIL'}",
          flush=True)
    print(f"OVERALL B (N-body truth):   {'PASS' if b_pass else 'FAIL'}",
          flush=True)
    print(f"({time.time()-t0:.0f}s total)", flush=True)
