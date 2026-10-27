"""Mercury fitter test v2: blind perturber-parameter recovery, multi-tracer.

Runs the v2 perturber_fitter blind on three synthetic cases and scores
after. The fitter takes NO truth; this harness holds truth only for
post-hoc scoring. v1 record: mercury_fitter_results.json.

v2 changes (from v1 diagnosis, 2026-10-26):
  - MULTI-TRACER data (Venus-, Earth-, Mars-like): v1's single tracer
    left a mass-radius degeneracy valley (fitted m*r == truth m*r while
    mass/radius were 41%/71% off). J3's data had 3 visible objects.
  - REALISTIC NOISE sigma=1e-7 AU (seeded per case): v1's noiseless
    data broke the ratio gate on the null case (a 4e-15 phantom
    "improved" holdout 58-million-fold by mopping up NM residual).
  - GATE ratio >= 1.2 (rom_closure discipline) instead of any
    improvement.
  - UNINFORMATIVE JOINT STARTS (J4's remedy): v1's heavy case failed
    because the one-body fit is distorted by a heavy secondary, so
    grid seeds from it go bad.

Cases (harness truth, synthetic definitions -- NOT the sealed legacy
scenario truth, which is never opened):
  mercury: truth Saturn (2.86e-4, 9.58, 4.75) +
           Mercury (1.66e-7, 0.39, 0.19).
  heavy:   truth Saturn + Earth (3.0e-6, 2.5, 2.0).
  null:    truth Saturn only.

Tracers: Venus-like a=0.723 e=0.007 i=3.39 Omega=76.7 omega=131.6
M=50; Earth-like a=1.0 e=0.017 i=0.01 Omega=0 omega=102.9 M=200;
Mars-like a=1.524 e=0.093 i=1.85 Omega=49.6 omega=286.5 M=100 (deg).
Span 20 yr, dt 0.1 yr (201 points), train = first 70%, holdout =
last 30% (checker split).

PREDECLARED ACCEPTANCE (written before any v2 run):
  mercury: verdict TWO_BODY, secondary mass rel err < 1%, radius
           rel err < 2%, phase abs err < 0.1 rad, holdout ratio >= 100.
           Robustness: >= 2 of 4 joint refined seeds' secondary within
           5% mass of truth.
  null:    verdict ONE_BODY.
  heavy:   NO pass/fail predeclared (open problem in both builds).
           Verdict, recovered params and ratio reported honestly.
           If uninformative starts close it, the blind spot is closed.
  cross-check: rebound ias15 vs whfast (dt=0.001 yr) max position
           difference over all tracers < 1e-5 AU.

ASSUMPTIONS (recorded, not hidden):
  - Circular coplanar perturbers (v1 scope; eccentric is stage 2).
  - Tracers massless (own mass effect second-order).
  - 3D position MSE (legacy was 2D).
  - Truth and fit share the rebound ias15 forward model: this test
    validates the FITTER (blind search + identification), not the
    physics engine (rebound is the engine the validated stack itself
    was validated against).

Run with the rebound venv python:
  /tmp/rebound_venv/bin/python mercury_fitter_test_v2.py
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

TRACER_ELEMENTS = [
    dict(a=0.723, e=0.007, i=math.radians(3.39),
         Omega=math.radians(76.7), omega=math.radians(131.6),
         M=math.radians(50.0)),
    dict(a=1.0, e=0.017, i=math.radians(0.01),
         Omega=math.radians(0.0), omega=math.radians(102.9),
         M=math.radians(200.0)),
    dict(a=1.524, e=0.093, i=math.radians(1.85),
         Omega=math.radians(49.6), omega=math.radians(286.5),
         M=math.radians(100.0)),
]
SPAN_YR = 20.0
DT_YR = 0.1
TRAIN_FRAC = 0.7
NOISE_SIGMA_AU = 1e-7

CASES = {
    'mercury': ([(2.86e-4, 9.58, 4.75), (1.66e-7, 0.39, 0.19)], 0),
    'heavy': ([(2.86e-4, 9.58, 4.75), (3.0e-6, 2.5, 2.0)], 1),
    'null': ([(2.86e-4, 9.58, 4.75)], 2),
}


def tracer_states():
    out = []
    for el in TRACER_ELEMENTS:
        r, v = elements_to_cart(el, mu=MU_SUN)
        out.append(np.concatenate([np.asarray(r, float),
                                   np.asarray(v, float)]))
    return out


def phase_diff(a, b):
    return abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)


def make_case(truth_bodies, noise_seed):
    ts = np.arange(0.0, SPAN_YR + 1e-9, DT_YR)
    states = tracer_states()
    clean = predict_positions(states, truth_bodies, ts)
    assert clean is not None, 'truth generation failed'
    rng = np.random.default_rng(noise_seed)
    obs = clean + rng.normal(0.0, NOISE_SIGMA_AU, clean.shape)
    n_train = int(len(ts) * TRAIN_FRAC)
    return {
        'tracer_states': states,
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
        out['seed_sources'] = report['two_body']['refined_sources']
    return out


def cross_check_ias15_whfast():
    """ias15 vs whfast on the multi-tracer Mercury system."""
    import rebound
    truth = CASES['mercury'][0]
    ts = np.arange(0.0, SPAN_YR + 1e-9, DT_YR)
    states = tracer_states()

    def run(integrator, dt=None):
        sim = rebound.Simulation()
        sim.add(m=1.0)
        for mass, radius, phase in truth:
            v = math.sqrt(MU_SUN / radius)
            sim.add(m=mass, x=radius * math.cos(phase),
                    y=radius * math.sin(phase), z=0,
                    vx=-v * math.sin(phase), vy=v * math.cos(phase), vz=0)
        for st in states:
            sim.add(m=0.0, x=st[0], y=st[1], z=st[2],
                    vx=st[3], vy=st[4], vz=st[5])
        sim.move_to_com()
        sim.integrator = integrator
        if dt is not None:
            sim.dt = dt
        sim.G = MU_SUN
        sim.t = 0.0
        out = []
        for t in ts:
            sim.integrate(float(t))
            row = []
            for j in range(len(states)):
                p = sim.particles[-(len(states) - j)]
                row.append([p.x, p.y, p.z])
            out.append(row)
        return np.array(out)

    a = run('ias15')
    b = run('whfast', dt=0.001)
    return float(np.max(np.linalg.norm(a - b, axis=2)))


def main():
    t_start = time.time()
    record = {'config': {
        'tracers': [{k: (math.degrees(v) if k in
                         ('i', 'Omega', 'omega', 'M') else v)
                     for k, v in el.items()} for el in TRACER_ELEMENTS],
        'span_yr': SPAN_YR, 'dt_yr': DT_YR, 'train_frac': TRAIN_FRAC,
        'noise_sigma_au': NOISE_SIGMA_AU,
        'noise_seeds': {k: s for k, (_, s) in CASES.items()},
        'tracer_mass': 0.0, 'perturbers': 'circular',
        'cases': {k: [list(b) for b in v] for k, (v, _) in CASES.items()}},
        'cases': {}}
    print('cross-check ias15 vs whfast ...', flush=True)
    cc = cross_check_ias15_whfast()
    record['cross_check_ias15_whfast_max_diff_au'] = cc
    print(f'  max diff: {cc:.3e} AU', flush=True)
    for name, (truth, noise_seed) in CASES.items():
        print(f'case {name} ...', flush=True)
        case = make_case(truth, noise_seed)
        t0 = time.time()
        report = run_blind_fit(case['tracer_states'], case['ts_train'],
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
    out_path = Path(__file__).resolve().parent / 'mercury_fitter_results_v2.json'
    out_path.write_text(json.dumps(record, indent=1))
    print(f'saved {out_path} ({record["total_runtime_s"]:.0f}s total)',
          flush=True)


if __name__ == '__main__':
    main()
