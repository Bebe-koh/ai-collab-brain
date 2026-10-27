#!/usr/bin/env python3
"""Bounded diagnostic: identical-state cross-evaluation (proposal 2).

Question: does the holdout-ratio discrepancy (spline 1.00370573 vs
analytic 1.00371696) come from evaluating the model, or from the
checker refits landing at slightly different states?

Method (no optimizer in the comparison itself):
  1. Re-run both fits with state capture. The checker's refit state is
     recorded by wrapping checker_brain.fit_state (behavior unchanged).
  2. Cross-evaluate: both extra models (spline, analytic) at each
     checker's final refit state; predict the held-out 30% and compare
     holdout RMS and MSE ratios. Baseline holdout is common (reused).
  3. Report refit termination proxies (nfev, cost, best_start) — the
     fitter does not record stopping reason or optimality.

No default is switched, no threshold is changed, and the original
failed comparison is not relabeled. Results are saved to JSON.
"""
import json
import math
import sys
import time

import numpy as np

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/real_data')

import checker_brain
import rom_closure
from rom_closure import (PerturbedParticle, build_synthetic_dataset,
                         fit_candidate, holdout_mse_ratio,
                         baseline_fingerprint_for)
from rails_brain import PlanetRails
from secular_elements import MU_SUN

MEARTH = 1.0 / 332946.0
BIG3 = [(1.571e-4 * MEARTH, 2.78, 0.0), (4.336e-5 * MEARTH, 2.37, 0.0),
        (3.419e-5 * MEARTH, 2.85, 0.0)]
TRACER = {'a': 40.0, 'e': 0.1, 'i': 0.087, 'Omega': 1.2, 'omega': 3.5,
          'M': 5.0}
NOVEL_TRUTH = (1e-4, 8.0, 1.0)
RAILS = HERE + '/sealed_runs/planet_rails.npz'
OUT = HERE + '/diagnostic_identical_state_2026-10-26.json'


class AnalyticExtraRails:
    """Drop-in replacement for ExtraRails: direct circular formula."""

    def __init__(self, bodies, t_ref):
        self.bodies = list(bodies)
        self.t_ref = t_ref
        self.n = len(bodies)

    @classmethod
    def from_bodies(cls, bodies, t_ref, t_min, t_max, dt_days=0.5):
        return cls(bodies, t_ref)

    def positions(self, t):
        out = []
        for (m, r, p) in self.bodies:
            n = math.sqrt(MU_SUN / r ** 3)
            th = p + n * (float(t) - self.t_ref)
            out.append([r * math.cos(th), r * math.sin(th), 0.0])
        return np.array(out)


def main():
    ds = build_synthetic_dataset(TRACER, BIG3 + [NOVEL_TRUTH],
                                 rails_cache=RAILS)
    ds['known_inventory'] = list(BIG3)
    ts, obs = np.asarray(ds['ts'], float), np.asarray(ds['obs'], float)
    order = np.argsort(ts)
    n_hold = int(round(len(ts) * 0.30))
    ts_ho, obs_ho = ts[order][-n_hold:], obs[order][-n_hold:]
    t_ref = float(ts[0])
    print(f"holdout: {n_hold} points, t_ref={t_ref}", flush=True)

    # Record checker refits without changing behavior.
    recorded = []
    orig_fit_state = checker_brain.fit_state

    def spy_fit_state(ts_tr, obs_tr, predict_fn, **kw):
        out = orig_fit_state(ts_tr, obs_tr, predict_fn, **kw)
        part = getattr(predict_fn, '__self__', None)
        n_extra = (len(getattr(part, 'extra_mus', []))
                   if part is not None else -1)
        recorded.append({
            'n_extra': n_extra,
            'state': [float(v) for v in
                      (out['r0_au'] + out['v0_au_yr'])]
            if out.get('success') else None,
            'rms': float(out.get('rms_au', float('nan'))),
            'cost': float(out.get('cost', float('nan'))),
            'nfev': int(out.get('nfev', -1)),
            'best_start': int(out.get('best_start', -1)),
            'success': bool(out.get('success', False)),
        })
        return out

    checker_brain.fit_state = spy_fit_state
    try:
        spline = fit_candidate(ds, [NOVEL_TRUTH], seed=0)
        n_spline_refits = len(recorded)
        baseline = (spline['baseline_fit'], spline['baseline_check'])
        baseline_prov = baseline_fingerprint_for(
            ds, spline['extra_evaluator'])
        orig_rails = rom_closure.ExtraRails
        rom_closure.ExtraRails = AnalyticExtraRails
        try:
            analytic = fit_candidate(ds, [NOVEL_TRUTH], seed=0,
                                     baseline=baseline,
                                     baseline_provenance=baseline_prov)
        finally:
            rom_closure.ExtraRails = orig_rails
    finally:
        checker_brain.fit_state = orig_fit_state
    print(f"recorded refits: spline run={n_spline_refits}, "
          f"total={len(recorded)}", flush=True)

    # Candidate refits carry 4 extras (BIG3 + NOVEL); baseline carries 3.
    cand_refits = [r for r in recorded if r['n_extra'] == 4]
    print(f"candidate refits found: {len(cand_refits)}", flush=True)
    if len(cand_refits) != 2:
        print("unexpected refit count; recorded summary:", flush=True)
        for r in recorded:
            print(f"  n_extra={r['n_extra']} success={r['success']} "
                  f"rms={r['rms']:.3e} nfev={r['nfev']}", flush=True)
        with open(OUT, 'w') as f:
            json.dump({'recorded': recorded}, f, indent=2)
        return
    s_ref = cand_refits[0]
    a_ref = cand_refits[1]
    s_state = np.array(s_ref['state'])
    a_state = np.array(a_ref['state'])
    print(f"refit state max diff: "
          f"{float(np.max(np.abs(s_state - a_state))):.3e}", flush=True)
    print(f"spline refit: nfev={s_ref['nfev']} cost={s_ref['cost']:.6e} "
          f"best_start={s_ref['best_start']}", flush=True)
    print(f"analytic refit: nfev={a_ref['nfev']} cost={a_ref['cost']:.6e} "
          f"best_start={a_ref['best_start']}", flush=True)

    # Cross-evaluation at identical states, no optimizer.
    planet_rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                                     cache_path=RAILS)
    cand_bodies = list(BIG3) + [NOVEL_TRUTH]
    mus = [m for m, _, _ in cand_bodies]
    p_spline = PerturbedParticle(planet_rails, cand_bodies, mus,
                                 t_ref, 0.0, 27.0)
    p_analytic = PerturbedParticle(planet_rails, cand_bodies, mus,
                                   t_ref, 0.0, 27.0)
    p_analytic.extra_rails = AnalyticExtraRails(cand_bodies, t_ref)
    b_ho = float(spline['baseline_holdout'])
    print(f"baseline holdout (common): {b_ho:.6e} "
          f"(analytic run reports {analytic['baseline_holdout']:.6e})",
          flush=True)
    table = {}
    for sname, state in (('spline_refit_state', s_state),
                         ('analytic_refit_state', a_state)):
        for mname, part in (('spline_model', p_spline),
                            ('analytic_model', p_analytic)):
            pred = part.predict(state, ts_ho, t_ref)
            rms = float(np.sqrt(np.mean((pred - obs_ho) ** 2)))
            ratio = holdout_mse_ratio(b_ho, rms)
            table[f'{sname} x {mname}'] = {'holdout_rms': rms,
                                           'mse_ratio': ratio}
            print(f"{sname} x {mname}: holdout_rms={rms:.6e} "
                  f"mse_ratio={ratio:.8f}", flush=True)
    # Original refit-based ratios, for reference.
    table['orig_spline_ratio'] = float(spline['holdout_mse_ratio'])
    table['orig_analytic_ratio'] = float(analytic['holdout_mse_ratio'])
    print(f"orig ratios: spline={table['orig_spline_ratio']:.8f} "
          f"analytic={table['orig_analytic_ratio']:.8f}", flush=True)

    rec = {
        'baseline_holdout': b_ho,
        'spline_refit': s_ref,
        'analytic_refit': a_ref,
        'refit_state_max_diff': float(np.max(np.abs(s_state - a_state))),
        'cross_eval': table,
        'orig_spline_verdict': None,
        'note': 'No default switched; no threshold changed; original '
                'failed comparison preserved, not relabeled.',
    }
    with open(OUT, 'w') as f:
        json.dump(rec, f, indent=2)
    print(f"record saved: {OUT}", flush=True)


if __name__ == '__main__':
    main()
