#!/usr/bin/env python3
"""Bounded development-only acceptance test: spline vs analytic extras.

Implements the approved rule in acceptance_rule_proposal_2026-10-26.md.
Sequence: pre-flight -> same-path control (spline twice) -> if the
control passes, the variant comparison (spline vs analytic) on the
fresh belt case -> Q1 fixed-state cross-evaluation.

Hard guards: no final-partition use, no threshold change, no default
switch, no relabeling of the original failed comparison. No source
file is modified; the analytic variant is an in-memory monkeypatch.
"""
import json
import math
import os
import platform
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
                         verdict_for_candidate_detailed,
                         baseline_fingerprint_for)
from rails_brain import PlanetRails
from secular_elements import MU_SUN
import rebound

MEARTH = 1.0 / 332946.0
BIG3 = [(1.571e-4 * MEARTH, 2.78, 0.0), (4.336e-5 * MEARTH, 2.37, 0.0),
        (3.419e-5 * MEARTH, 2.85, 0.0)]
TRACER = {'a': 40.0, 'e': 0.1, 'i': 0.087, 'Omega': 1.2, 'omega': 3.5,
          'M': 5.0}
RAILS = HERE + '/sealed_runs/planet_rails.npz'
OUT = HERE + '/acceptance_test_belt_2026-10-26.json'


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


def rel_diff(a, b_ref):
    """|a - b| / |spline reference|; absolute diff on zero reference."""
    if b_ref == 0:
        return abs(a - b_ref)
    return abs(a - b_ref) / abs(b_ref)


def fit_summary(res):
    cf = res['candidate_fit']
    chk = res['candidate_check']
    outcome, ratio, reason = verdict_for_candidate_detailed(res)
    return {
        'candidate_rms': float(cf.get('rms_au', float('nan'))),
        'candidate_cost': float(cf.get('cost', float('nan'))),
        'candidate_nfev': int(cf.get('nfev', -1)),
        'candidate_best_start': int(cf.get('best_start', -1)),
        'candidate_success': bool(cf.get('success', False)),
        'candidate_state': [float(v) for v in
                            (cf['r0_au'] + cf['v0_au_yr'])],
        'checker_verdict': chk['verdict'],
        'checker_gates': dict(chk['gates']),
        'baseline_holdout': float(res['baseline_holdout']),
        'candidate_holdout': float(res['candidate_holdout']),
        'mse_ratio': float(res['holdout_mse_ratio']),
        'decision': outcome,
        'decision_reason': reason,
        't_baseline_s': float(res['t_baseline_s']),
        't_candidate_s': float(res['t_candidate_s']),
    }


def main():
    # ---- Pre-flight: stop and report on any failure. ----
    preflight = {
        'rom_closure_lean_present': os.path.isfile(HERE + '/rom_closure_lean.py'),
        'rails_cache_present': os.path.isfile(RAILS),
        'rebound_version': rebound.__version__,
        'save_route_writable': os.access(HERE, os.W_OK),
    }
    env = {
        'python': sys.version.split()[0],
        'numpy': np.__version__,
        'scipy': __import__('scipy').__version__,
        'rebound': rebound.__version__,
        'platform': platform.platform(),
    }
    print(f"preflight: {preflight}", flush=True)
    print(f"environment: {env}", flush=True)
    if not all([preflight['rom_closure_lean_present'],
                preflight['rails_cache_present'],
                preflight['save_route_writable']]):
        print("PRE-FLIGHT FAILED: refusing to generate new work.", flush=True)
        with open(OUT, 'w') as f:
            json.dump({'preflight': preflight, 'environment': env,
                       'status': 'preflight_failed'}, f, indent=2)
        sys.exit(2)

    # ---- Fresh case: belt development data, partial inventory. ----
    ds = build_synthetic_dataset(TRACER, BIG3, rails_cache=RAILS)
    ds['known_inventory'] = list(BIG3[:2])
    cand = [BIG3[2]]
    ts, obs = np.asarray(ds['ts'], float), np.asarray(ds['obs'], float)
    order = np.argsort(ts)
    n_hold = int(round(len(ts) * 0.30))
    ts_ho, obs_ho = ts[order][-n_hold:], obs[order][-n_hold:]
    t_ref = float(ts[0])
    print(f"belt case: known=BIG3[:2], candidate=BIG3[2], "
          f"holdout={n_hold} points, t_ref={t_ref}", flush=True)

    # ---- Record checker refits (behavior unchanged). ----
    recorded = []
    run_tag = ['?']
    orig_fit_state = checker_brain.fit_state

    def spy_fit_state(ts_tr, obs_tr, predict_fn, **kw):
        out = orig_fit_state(ts_tr, obs_tr, predict_fn, **kw)
        part = getattr(predict_fn, '__self__', None)
        n_extra = (len(getattr(part, 'extra_mus', []))
                   if part is not None else -1)
        recorded.append({
            'run': run_tag[0], 'n_extra': n_extra,
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
        t0 = time.time()
        run_tag[0] = 'spline_a'
        spline_a = fit_candidate(ds, cand, seed=0)
        t_spline_a = time.time() - t0
        t0 = time.time()
        run_tag[0] = 'spline_b'
        spline_b = fit_candidate(ds, cand, seed=0)
        t_spline_b = time.time() - t0
    finally:
        checker_brain.fit_state = orig_fit_state
    sa, sb = fit_summary(spline_a), fit_summary(spline_b)

    # ---- Control: spline twice must reproduce within Q1/Q2 bounds. ----
    control = {
        'verdicts_match': sa['checker_verdict'] == sb['checker_verdict'],
        'gates_match': sa['checker_gates'] == sb['checker_gates'],
        'decisions_match': (sa['decision'] == sb['decision']
                            and sa['decision_reason'] == sb['decision_reason']),
        'ratio_rel_diff': rel_diff(sb['mse_ratio'], sa['mse_ratio']),
        'candidate_rms_rel_diff': rel_diff(sb['candidate_rms'],
                                           sa['candidate_rms']),
        'wall_s': {'spline_a': t_spline_a, 'spline_b': t_spline_b},
    }
    control['pass'] = bool(control['verdicts_match']
                           and control['gates_match']
                           and control['decisions_match']
                           and control['ratio_rel_diff'] < 1e-9
                           and control['candidate_rms_rel_diff'] < 1e-6)
    print(f"control: pass={control['pass']} "
          f"ratio_rel_diff={control['ratio_rel_diff']:.3e} "
          f"rms_rel_diff={control['candidate_rms_rel_diff']:.3e} "
          f"verdicts={sa['checker_verdict']}/{sb['checker_verdict']} "
          f"decisions={sa['decision']}/{sb['decision']}", flush=True)
    if not control['pass']:
        print("CONTROL FAILED: halting before any variant comparison.",
              flush=True)
        with open(OUT, 'w') as f:
            json.dump({'preflight': preflight, 'environment': env,
                       'spline_a': sa, 'spline_b': sb,
                       'control': control, 'status': 'control_failed'},
                      f, indent=2)
        sys.exit(2)

    # ---- Variant comparison (spline_a vs analytic, baseline reused). ----
    baseline = (spline_a['baseline_fit'], spline_a['baseline_check'])
    baseline_prov = baseline_fingerprint_for(ds,
                                             spline_a['extra_evaluator'])
    orig_rails = rom_closure.ExtraRails
    rom_closure.ExtraRails = AnalyticExtraRails
    try:
        t0 = time.time()
        run_tag[0] = 'analytic'
        checker_brain.fit_state = spy_fit_state
        try:
            analytic = fit_candidate(ds, cand, seed=0, baseline=baseline,
                                     baseline_provenance=baseline_prov)
        finally:
            checker_brain.fit_state = orig_fit_state
        t_analytic = time.time() - t0
    finally:
        rom_closure.ExtraRails = orig_rails
    an = fit_summary(analytic)

    r_s = sa['mse_ratio']
    r_a = an['mse_ratio']
    d = min(abs(r_s - 1.0), abs(r_s - 1.2))
    bound = 0.1 * d
    crossing_10 = (r_s < 1.0) != (r_a < 1.0)
    crossing_12 = (r_s < 1.2) != (r_a < 1.2)
    q2 = {
        'spline_ratio': r_s, 'analytic_ratio': r_a,
        'threshold_distance_d': d, 'score_bound_0.1d': bound,
        'ratio_abs_diff': abs(r_a - r_s),
        'ratio_pass': bool(abs(r_a - r_s) <= bound),
        'candidate_rms_rel_diff': rel_diff(an['candidate_rms'],
                                           sa['candidate_rms']),
        'rms_pass': bool(rel_diff(an['candidate_rms'],
                                  sa['candidate_rms']) <= 1e-6),
        'verdicts_match': sa['checker_verdict'] == an['checker_verdict'],
        'gates_match': sa['checker_gates'] == an['checker_gates'],
        'decisions_match': (sa['decision'] == an['decision']
                            and sa['decision_reason'] == an['decision_reason']),
        'crossing_1.0': bool(crossing_10),
        'crossing_1.2': bool(crossing_12),
        'spline_on_threshold': bool(r_s == 1.0 or r_s == 1.2),
        'wall_s': {'spline_a': t_spline_a, 'analytic': t_analytic},
    }
    q2['boundary_fail'] = bool(crossing_10 or crossing_12
                               or not q2['verdicts_match']
                               or not q2['gates_match']
                               or not q2['decisions_match'])
    q2['pass'] = bool(q2['ratio_pass'] and q2['rms_pass']
                      and not q2['boundary_fail'])
    print(f"Q2: spline_ratio={r_s:.8f} analytic_ratio={r_a:.8f} "
          f"d={d:.6f} bound={bound:.3e} abs_diff={abs(r_a - r_s):.3e} "
          f"pass={q2['pass']} boundary_fail={q2['boundary_fail']}",
          flush=True)

    # ---- Q1: identical-state cross-evaluation (no optimizer). ----
    planet_rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                                     cache_path=RAILS)
    cand_bodies = list(BIG3[:2]) + cand
    mus = [m for m, _, _ in cand_bodies]
    p_spline = PerturbedParticle(planet_rails, cand_bodies, mus,
                                 t_ref, 0.0, 27.0)
    p_analytic = PerturbedParticle(planet_rails, cand_bodies, mus,
                                   t_ref, 0.0, 27.0)
    p_analytic.extra_rails = AnalyticExtraRails(cand_bodies, t_ref)
    b_ho = sa['baseline_holdout']
    cand_refits = [r for r in recorded
                   if r['n_extra'] == 3 and r['state'] is not None]
    refit_by_run = {}
    for r in cand_refits:
        refit_by_run.setdefault(r['run'], r)
    states = {}
    missing_refits = []
    for run, sname in (('spline_a', 'spline_refit_state'),
                       ('analytic', 'analytic_refit_state')):
        if run in refit_by_run:
            states[sname] = np.array(refit_by_run[run]['state'])
        else:
            missing_refits.append(sname)
    states['spline_candfit_state'] = np.array(sa['candidate_state'])
    states['analytic_candfit_state'] = np.array(an['candidate_state'])
    q1 = {'states': {}, 'missing_refit_states': missing_refits,
          'pass': True}
    for sname, state in states.items():
        row = {}
        for mname, part in (('spline_model', p_spline),
                            ('analytic_model', p_analytic)):
            pred = part.predict(state, ts_ho, t_ref)
            rms = float(np.sqrt(np.mean((pred - obs_ho) ** 2)))
            row[mname] = {'holdout_rms': rms,
                          'mse_ratio': float(holdout_mse_ratio(b_ho, rms)),
                          'pred': pred}
        res_diff = float(np.max(np.abs(row['spline_model']['pred']
                                        - row['analytic_model']['pred'])))
        ratio_rd = rel_diff(row['analytic_model']['mse_ratio'],
                            row['spline_model']['mse_ratio'])
        row['residual_max_diff'] = res_diff
        row['ratio_rel_diff'] = ratio_rd
        row['pass'] = bool(res_diff < 1e-7 and ratio_rd < 1e-9)
        q1['states'][sname] = {
            'spline_model': {k: v for k, v in
                             row['spline_model'].items() if k != 'pred'},
            'analytic_model': {k: v for k, v in
                               row['analytic_model'].items() if k != 'pred'},
            'residual_max_diff': res_diff,
            'ratio_rel_diff': ratio_rd,
            'pass': row['pass']}
        # Prediction vectors are recomputable from the stored states +
        # models, so only their comparison summaries are saved.
        q1['pass'] = q1['pass'] and row['pass']
        print(f"Q1 {sname}: residual_max_diff={res_diff:.3e} "
              f"ratio_rel_diff={ratio_rd:.3e} pass={row['pass']}",
              flush=True)

    overall = bool(control['pass'] and q1['pass'] and q2['pass'])
    rec = {
        'proposal': 'acceptance_rule_proposal_2026-10-26.md (approved)',
        'environment': env, 'preflight': preflight,
        'case': {'dataset': 'belt (TRACER + BIG3)',
                 'known_inventory': 'BIG3[:2]',
                 'candidate': 'BIG3[2]', 'seed': 0},
        'spline_a': sa, 'spline_b': sb, 'analytic': an,
        'control': control, 'q1': q1, 'q2': q2,
        'checker_refits': cand_refits,
        'overall_pass': overall,
        'notes': 'Termination status/message unavailable from fit_state '
                 '(LM sol.status/message dropped); counts, cost, runtime, '
                 'and environment recorded instead. No threshold, default, '
                 'or production state changed. Original failed comparison '
                 'not relabeled. Final untouched partition not used.',
    }
    with open(OUT, 'w') as f:
        json.dump(rec, f, indent=2)
    print(f"OVERALL: {'PASS' if overall else 'FAIL'}; record saved: {OUT}",
          flush=True)


if __name__ == '__main__':
    main()
