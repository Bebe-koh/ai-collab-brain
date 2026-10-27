#!/usr/bin/env python3
"""Eccentric-secondary validation harness (v3 fitter).

PREDECLARED ACCEPTANCE (written before any validation run):
  20/20 cases recovered, where recovered means ALL of:
    mass relative error   <= 10%   (legacy tolerance)
    semi-major axis rel err <= 5%  (legacy 'radius' tolerance)
    eccentricity abs error <= 0.05 (legacy tolerance)
  Means are reported alongside the count. Any failure is diagnosed
  per case in the summary, not hidden. If fewer than 20/20 recover,
  the verdict is 'legacy tolerances not met on real dynamics' --
  NOT 'legacy was wrong': the legacy test fitted an analytic harmonic
  signal, not N-body orbits (see note below), so this test is strictly
  harder and subsumes the legacy claim only if it passes.

LEGACY-BAR CORRECTION (read the legacy code, 2026-10-27):
  legacy eccentric_body_recovery.py fits a 1D analytic signal
  amplitude*(sin(theta) + e*0.5*sin(2*theta)) by brute-force grid
  search -- its 'eccentricity' is a second-harmonic coefficient, not
  a Keplerian orbital eccentricity, and no dynamics are integrated.
  This harness therefore does NOT replicate that test: it fits REAL
  eccentric Keplerian orbits through rebound N-body integration, with
  the legacy TOLERANCES and trial count (20) carried over.

CASE DESIGN (deviations from legacy, each with a reason):
  - mass: uniform 1.5e-6..4.5e-6 Msun (legacy exact).
  - a: uniform 3.0..5.0 AU (ADAPTED from legacy 0.75..1.25: a real
    secondary at 0.75..1.25 AU would cross the Venus/Earth/Mars
    tracer orbits, making N-body recovery ill-posed via close
    encounters. At a >= 3.0 and e <= 0.40, perihelion >= 1.8 AU,
    outside Mars aphelion (1.666 AU) -- no tracer crossings.)
  - e: uniform 0..0.40 (legacy exact).
  - phase (M0): uniform 0..2pi (legacy exact).
  - known body: Saturn (2.86e-4, 9.58, 4.75) circular (v2 convention).
  - tracers: v2's Venus/Earth/Mars-like states (same harness import).
  - span 20 yr, dt 0.1 (201 pts); train first 70%, holdout last 30%
    (v2 convention). Fitting uses TRAIN only (pipeline-consistent);
    parameters are scored, holdout ratio is diagnostic.
  - noise: sigma 1e-7 AU (v2 convention; legacy's 2e-8 was on a scalar
    signal in different units and is not transferable).
  - config rng: default_rng(3000 + i) (legacy pattern); noise rng:
    default_rng(i) (v2 per-case pattern).

CHECKPOINTING (restart lesson from v2): each case writes its own
eccentric_case_{i:02d}.json IMMEDIATELY on completion, and the
summary is rewritten after each case. The driver skips cases with an
existing result file, so a restart loses at most the in-flight case.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mercury_fitter_test_v2 import tracer_states  # noqa: E402
from perturber_fitter import predict_positions, run_eccentric_fit  # noqa: E402

SATURN = (2.86e-4, 9.58, 4.75)
SIGMA = 1e-7
N_CASES = 20
HERE = Path(__file__).resolve().parent


def make_ecc_case(i):
    """Build case i: truth system + noisy train/holdout observations."""
    rng = np.random.default_rng(3000 + i)
    mass = float(rng.uniform(1.5e-6, 4.5e-6))
    a = float(rng.uniform(3.0, 5.0))
    e = float(rng.uniform(0.0, 0.40))
    phase = float(rng.uniform(0.0, 2.0 * np.pi))
    truth = [SATURN, (mass, a, e, phase)]
    ts = np.arange(0.0, 20.0 + 1e-9, 0.1)
    states = tracer_states()
    clean = predict_positions(states, truth, ts)
    assert clean is not None and np.all(np.isfinite(clean))
    noise = np.random.default_rng(i).normal(0.0, SIGMA, clean.shape)
    obs = clean + noise
    cut = int(0.7 * len(ts))
    return {'truth': truth, 'tracer_states': states,
            'ts_train': ts[:cut], 'obs_train': obs[:cut],
            'ts_hold': ts[cut:], 'obs_hold': obs[cut:]}


def score_ecc_case(i, truth, report):
    """Score fitted secondary (bodies[1]; also the smaller mass)."""
    sat_fit, sec_fit = report['two_body']['bodies']
    assert sec_fit[0] < sat_fit[0], 'secondary is not the smaller body'
    m_t, a_t, e_t, _ = truth[1]
    m_f, a_f, e_f, _ = sec_fit
    mass_err = abs(m_f - m_t) / m_t
    a_err = abs(a_f - a_t) / a_t
    e_err = abs(e_f - e_t)
    recovered = mass_err <= 0.10 and a_err <= 0.05 and e_err <= 0.05
    return {'case': i, 'truth': [list(b) for b in truth],
            'fitted_secondary': list(sec_fit),
            'fitted_primary': list(sat_fit),
            'mass_rel_err': mass_err, 'a_rel_err': a_err,
            'e_abs_err': e_err, 'recovered': bool(recovered),
            'holdout_ratio': report['holdout_ratio'],
            'one_body_holdout': report['one_body']['holdout_mse'],
            'two_body_holdout': report['two_body']['holdout_mse']}


def case_path(i):
    return HERE / f'eccentric_case_{i:02d}.json'


def write_summary(results):
    rec = sum(1 for r in results if r['recovered'])
    summary = {
        'n_cases': len(results),
        'recovered': rec,
        'mean_mass_rel_err': float(np.mean([r['mass_rel_err']
                                            for r in results])) if results else None,
        'mean_a_rel_err': float(np.mean([r['a_rel_err']
                                         for r in results])) if results else None,
        'mean_e_abs_err': float(np.mean([r['e_abs_err']
                                         for r in results])) if results else None,
        'cases': results,
    }
    (HERE / 'eccentric_fitter_results.json').write_text(
        json.dumps(summary, indent=1))
    return summary


def main():
    results = []
    for i in range(N_CASES):
        if case_path(i).exists():
            r = json.loads(case_path(i).read_text())
            results.append(r)
            print(f'case {i:02d}: SKIPPED (result exists) '
                  f"recovered={r['recovered']}", flush=True)
            continue
        print(f'case {i:02d} ...', flush=True)
        case = make_ecc_case(i)
        t0 = time.time()
        report = run_eccentric_fit(case['tracer_states'],
                                   case['ts_train'], case['obs_train'],
                                   case['ts_hold'], case['obs_hold'])
        dt = time.time() - t0
        scored = score_ecc_case(i, case['truth'], report)
        scored['runtime_s'] = dt
        case_path(i).write_text(json.dumps(scored, indent=1))
        results.append(scored)
        write_summary(results)
        print(f"case {i:02d}: recovered={scored['recovered']} "
              f"mass={scored['mass_rel_err']:.2%} "
              f"a={scored['a_rel_err']:.2%} "
              f"e={scored['e_abs_err']:.4f} ({dt:.0f}s)", flush=True)
    summary = write_summary(results)
    print(f"TOTAL: {summary['recovered']}/{summary['n_cases']} recovered; "
          f"mean mass={summary['mean_mass_rel_err']:.2%} "
          f"a={summary['mean_a_rel_err']:.2%} "
          f"e={summary['mean_e_abs_err']:.4f}", flush=True)


if __name__ == '__main__':
    main()
