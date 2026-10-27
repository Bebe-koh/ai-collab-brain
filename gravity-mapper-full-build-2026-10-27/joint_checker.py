#!/usr/bin/env python3
"""Spec-driven checker entry point (D9 prototype, NEW FILE).

check_model mirrors check_fit's gates and verdict logic, but for
joint models: the TRAINING REFIT's RMS gates (never the full-data
fit's RMS), the holdout MSE ratio is computed from the joint and
null train refits on the SAME partition, and the start rule is
reported verbatim. Full-data RMS is reported for display only.
Frozen-parameter removal is prohibited by construction: the caller
must supply refits, and this module always refits.
"""
import time

import numpy as np

from joint_driver import fit_model, make_particle


def _mse_ratio(null_holdout_rms, joint_holdout_rms):
    if (np.isfinite(null_holdout_rms) and np.isfinite(joint_holdout_rms)
            and joint_holdout_rms > 0):
        r = null_holdout_rms / joint_holdout_rms
        return float(r * r)
    return float('nan')


def check_model(fit, ts, obs, spec, sigma, holdout_frac=0.30,
                seed=0, early_stop_rms=None, n_starts=3):
    """Validate a joint fit dict from fit_model. Returns a verdict
    dict with verbatim numbers (see plan). Strict starts only:
    train refits use data-driven tracer starts on TRAIN data and
    the D10 mass scan; no hint from the full-data fit is passed.
    """
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    t_ref = spec.t_ref
    reasons = []
    gates = {}
    gates['converged'] = bool(fit.get('success', False))
    if not gates['converged']:
        reasons.append('optimizer did not converge')
    a, e = fit.get('a', float('nan')), fit.get('e', float('nan'))
    masses = fit.get('masses_solar') or []
    gates['physical'] = bool(
        np.isfinite(a) and a > 0 and np.isfinite(e) and 0.0 <= e < 1.0
        and all(np.isfinite(m) and m > 0 for m in masses))
    if not gates['physical']:
        reasons.append('unphysical elements or masses')

    n = len(ts)
    n_hold = int(round(n * holdout_frac))
    train_rms = np.inf
    holdout_rms = np.inf
    null_holdout_rms = np.inf
    joint_refit_success = False
    null_refit_success = False
    joint_refit_wall = 0.0
    null_refit_wall = 0.0
    if n_hold >= 5 and gates['converged'] and gates['physical']:
        order = np.argsort(ts)
        ts_s, obs_s = ts[order], obs[order]
        ts_tr, obs_tr = ts_s[:-n_hold], obs_s[:-n_hold]
        ts_ho, obs_ho = ts_s[-n_hold:], obs_s[-n_hold:]
        # Joint train refit (strict).
        t0 = time.perf_counter()
        refit = fit_model(ts_tr, obs_tr, spec, make_particle(spec),
                          n_starts=n_starts, seed=seed,
                          early_stop_rms=early_stop_rms)
        joint_refit_wall = time.perf_counter() - t0
        train_rms = float(refit.get('rms_au', np.inf))
        joint_refit_success = bool(refit.get('success', False))
        if joint_refit_success:
            pred = make_particle(spec).predict(
                np.array(refit['theta']), ts_ho, t_ref)
            if pred is not None:
                holdout_rms = float(
                    np.sqrt(np.mean((pred - obs_ho) ** 2)))
        # Null train refit on the SAME partition (also the k=1
        # removal refit: reduced model refit, never frozen).
        null_spec = spec.without_candidates()
        t0 = time.perf_counter()
        null_refit = fit_model(ts_tr, obs_tr, null_spec,
                               make_particle(null_spec),
                               n_starts=n_starts, seed=seed,
                               early_stop_rms=early_stop_rms)
        null_refit_wall = time.perf_counter() - t0
        null_refit_success = bool(null_refit.get('success', False))
        if null_refit_success:
            pred_n = make_particle(null_spec).predict(
                np.array(null_refit['theta']), ts_ho, t_ref)
            if pred_n is not None:
                null_holdout_rms = float(
                    np.sqrt(np.mean((pred_n - obs_ho) ** 2)))
    gates['noise_consistent'] = bool(np.isfinite(train_rms)
                                     and train_rms <= 5.0 * sigma)
    if not gates['noise_consistent']:
        reasons.append(f'train-refit rms {train_rms:.2e} AU > 5x sigma '
                       f'({5.0 * sigma:.2e} AU): model biased or wrong')
    gates['holdout_ok'] = bool(np.isfinite(holdout_rms)
                               and holdout_rms <= max(5.0 * sigma,
                                                      3.0 * train_rms))
    if not gates['holdout_ok']:
        if not np.isfinite(holdout_rms):
            reasons.append('holdout prediction unavailable (abstain path)')
        else:
            reasons.append(f'holdout rms {holdout_rms:.2e} AU exceeds '
                           f'max(5x sigma, 3x train rms)')

    if not gates['converged'] or not gates['physical']:
        verdict = 'FAIL'
    elif not np.isfinite(holdout_rms):
        verdict = 'ABSTAIN'
    elif gates['holdout_ok'] and gates['noise_consistent']:
        verdict = 'PASS'
    elif gates['holdout_ok'] and not gates['noise_consistent']:
        verdict = 'ABSTAIN'
        reasons.append('holdout coherent but above noise floor: escalate')
    else:
        verdict = 'FAIL'

    return {
        'verdict': verdict, 'gates': gates,
        'train_rms_au': float(train_rms),
        'holdout_rms_au': float(holdout_rms),
        'null_holdout_rms_au': float(null_holdout_rms),
        'holdout_mse_ratio': _mse_ratio(null_holdout_rms, holdout_rms),
        'sigma_au': float(sigma),
        'full_fit_rms_au': float(fit.get('rms_au', np.inf)),
        'full_fit_rms_note': 'display only; never gates',
        'start_rule': 'strict',
        'spec_id': spec.spec_id,
        'fitted_masses_solar': list(masses),
        'fitted_mass_uncertainties': None,
        'mass_uncertainty_note': 'not available from LM driver',
        'joint_refit_success': joint_refit_success,
        'null_refit_success': null_refit_success,
        'joint_refit_wall_s': joint_refit_wall,
        'null_refit_wall_s': null_refit_wall,
        'reasons': reasons,
    }
