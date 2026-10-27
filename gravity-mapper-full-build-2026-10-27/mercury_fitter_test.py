"""Mercury fitter test: blind perturber-parameter recovery on the current stack.

Runs the new perturber_fitter (J3 achievement port) blind on three
synthetic cases and scores after. The fitter takes NO truth; this
harness holds truth only for post-hoc scoring.

Cases (harness truth, synthetic definitions -- NOT the sealed legacy
scenario truth, which is never opened):
  mercury: tracer Mars-like, truth Saturn (2.86e-4, 9.58, 4.75) +
           Mercury (1.66e-7, 0.39, 0.19). Values near J3's recovered
           bodies, rounded to 3 significant figures.
  heavy:   same tracer, truth Saturn + Earth (3.0e-6, 2.5, 2.0)
           (J4's truth values, published in j4_v2r_result.json).
  null:    same tracer, truth Saturn only.

Tracer: Mars-like elements a=1.524, e=0.093, i=1.85 deg,
Omega=49.6 deg, omega=286.5 deg, M=100 deg. Span 20 yr, dt 0.1 yr
(201 points), train = first 70%, holdout = last 30% (checker split).

PREDECLARED ACCEPTANCE (written before any run):
  mercury: verdict TWO_BODY, secondary mass rel err < 1%, radius
           rel err < 2%, phase abs err < 0.1 rad, holdout ratio >= 100.
           Robustness: >= 2 of 3 joint refined seeds' secondary within
           5% mass of truth.
  null:    verdict ONE_BODY.
  heavy:   NO pass/fail predeclared (open problem in both builds).
           Verdict, recovered params and ratio reported honestly.
  cross-check: rebound ias15 vs whfast (dt=0.001 yr) max position
           difference reported; consistency claimed if < 1e-5 AU or
           < 10x the fitted holdout RMS (integration error must not
           dominate the fit).

ASSUMPTIONS (recorded, not hidden):
  - Noiseless observations (J3's noise level unknown; noiseless proves
    the search capability. Noisy validation is follow-up work.)
  - Single massless tracer (its own mass effect on candidates is
    second-order; legacy visible bodies had masses, this is a v1
    simplification).
  - Circular coplanar perturbers (v1). Eccentric is stage 2.
  - 3D position MSE (legacy score was 2D; 3D is the generalization).
  - Truth and fit share the rebound ias15 forward model: this test
    validates the FITTER (blind search + identification), not the
    physics engine. Rebound ias15 is the engine the validated stack
    itself was validated against (particle_brain self-test).
  - Secondary identification in fitted output: the smaller-mass body
    (mass ordering holds in both test cases).

Run with the rebound venv python (rebound is not a system package):
  /tmp/rebound_venv/bin/python mercury_fitter_test.py
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rails_brain import MU_SUN, elements_to_cart  # noqa: E402
from perturber_fitter import (  # noqa: E402
    predict_positions, run_blind_fit)

TRACER_ELEMENTS = dict(a=1.524, e=0.093, i=math.radians(1.85),
                       Omega=math.radians(49.6),
                       omega=math.radians(286.5), M=math.radians(100.0))
SPAN_YR = 20.0
DT_YR = 0.1
TRAIN_FRAC = 0.7

CASES = {
    'mercury': [(2.86e-4, 9.58, 4.75), (1.66e-7, 0.39, 0.19)],
    'heavy': [(2.86e-4, 9.58, 4.75), (3.0e-6, 2.5, 2.0)],
    'null': [(2.86e-4, 9.58, 4.75)],
}


def tracer_state():
    r, v = elements_to_cart(TRACER_ELEMENTS, mu=MU_SUN)
    return np.concatenate([np.asarray(r, float), np.asarray(v, float)])


def phase_diff(a, b):
    return abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)


def make_case(truth_bodies):
    ts = np.arange(0.0, SPAN_YR + 1e-9, DT_YR)
    obs = predict_positions(tracer_state(), truth_bodies, ts)
    assert obs is not None, 'truth generation failed'
    n_train = int(len(ts) * TRAIN_FRAC)
    return {
        'tracer_state': tracer_state(),
        'ts_train': ts[:n_train], 'obs_train': obs[:n_train],
        'ts_hold': ts[n_train:], 'obs_hold': obs[n_train:],
    }


def score_case(name, truth_bodies, report):
    two = report['two_body']['bodies']
    secondary = min(two, key=lambda b: b[0])
    primary = max(two, key=lambda b: b[0])
    out = {'verdict': report['verdict'],
           'holdout_ratio': report['holdout_ratio'],
           'one_holdout': report['one_body']['holdout_mse'],
           'two_holdout': report['two_body']['holdout_mse'],
           'fitted_primary': primary, 'fitted_secondary': secondary}
    if len(truth_bodies) == 2:
        tm, tr, tp = sorted(truth_bodies, key=lambda b: b[0])[0]
        fm, fr, fp = secondary
        out['truth_secondary'] = [tm, tr, tp]
        out['mass_rel_err'] = abs(fm - tm) / tm
        out['radius_rel_err'] = abs(fr - tr) / tr
        out['phase_abs_err'] = phase_diff(fp, tp)
        seeds_ok = 0
        for seed in report['two_body']['refined_seeds']:
            s_sec = min(seed['bodies'], key=lambda b: b[0])
            if abs(s_sec[0] - tm) / tm < 0.05:
                seeds_ok += 1
        out['seeds_within_5pct_mass'] = seeds_ok
        out['n_seeds'] = len(report['two_body']['refined_seeds'])
    return out


def cross_check_ias15_whfast():
    """ias15 vs whfast on the Mercury system; returns max position diff."""
    import rebound
    truth = CASES['mercury']
    ts = np.arange(0.0, SPAN_YR + 1e-9, DT_YR)
    tr = tracer_state()

    def run(integrator, dt=None):
        sim = rebound.Simulation()
        sim.add(m=1.0)
        for mass, radius, phase in truth:
            v = math.sqrt(MU_SUN / radius)
            sim.add(m=mass, x=radius * math.cos(phase),
                    y=radius * math.sin(phase), z=0,
                    vx=-v * math.sin(phase), vy=v * math.cos(phase), vz=0)
        sim.add(m=0.0, x=tr[0], y=tr[1], z=tr[2],
                vx=tr[3], vy=tr[4], vz=tr[5])
        sim.move_to_com()
        sim.integrator = integrator
        if dt is not None:
            sim.dt = dt
        sim.G = MU_SUN
        sim.t = 0.0
        out = []
        for t in ts:
            sim.integrate(float(t))
            p = sim.particles[-1]
            out.append([p.x, p.y, p.z])
        return np.array(out)

    a = run('ias15')
    b = run('whfast', dt=0.001)
    return float(np.max(np.linalg.norm(a - b, axis=1)))


def main():
    t_start = time.time()
    record = {'config': {
        'tracer_elements': {k: (math.degrees(v) if k in
                                ('i', 'Omega', 'omega', 'M') else v)
                            for k, v in TRACER_ELEMENTS.items()},
        'span_yr': SPAN_YR, 'dt_yr': DT_YR, 'train_frac': TRAIN_FRAC,
        'noise': 0.0, 'tracer_mass': 0.0, 'perturbers': 'circular',
        'cases': {k: [list(b) for b in v] for k, v in CASES.items()}},
        'cases': {}}
    print('cross-check ias15 vs whfast ...', flush=True)
    cc = cross_check_ias15_whfast()
    record['cross_check_ias15_whfast_max_diff_au'] = cc
    print(f'  max diff: {cc:.3e} AU', flush=True)
    for name, truth in CASES.items():
        print(f'case {name} ...', flush=True)
        case = make_case(truth)
        t0 = time.time()
        report = run_blind_fit(case['tracer_state'], case['ts_train'],
                               case['obs_train'], case['ts_hold'],
                               case['obs_hold'])
        dt = time.time() - t0
        scored = score_case(name, truth, report)
        scored['runtime_s'] = dt
        scored['full_report'] = report
        record['cases'][name] = scored
        print(f"  verdict={scored['verdict']} "
              f"ratio={scored['holdout_ratio']:.3e} ({dt:.0f}s)", flush=True)
        if 'mass_rel_err' in scored:
            print(f"  secondary: mass_err={scored['mass_rel_err']:.2%} "
                  f"radius_err={scored['radius_rel_err']:.2%} "
                  f"phase_err={scored['phase_abs_err']:.4f} rad "
                  f"seeds {scored['seeds_within_5pct_mass']}/"
                  f"{scored['n_seeds']}", flush=True)
    record['total_runtime_s'] = time.time() - t_start
    out_path = Path(__file__).resolve().parent / 'mercury_fitter_results.json'
    out_path.write_text(json.dumps(record, indent=1))
    print(f'saved {out_path} ({record["total_runtime_s"]:.0f}s total)',
          flush=True)


if __name__ == '__main__':
    main()
