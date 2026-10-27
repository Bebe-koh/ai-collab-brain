#!/usr/bin/env python3
"""Checker brain — independent validation, never trusts the fitter (4 of 5).

Gravity Mapper modular N-body fitter (2026-10-24).

Contract: check_fit(fit, ts, obs, predict_fn, sigma) re-validates a
fit WITHOUT any knowledge of the truth. It returns PASS / FAIL / ABSTAIN
plus the numbers behind the verdict. The conductor acts on the verdict;
the rung's scored criterion (|dq|/q, |da|/a vs sealed truth) is a
separate step done by the harness AFTER fitting — the checker must never
see truth, or the whole "nobody grades their own homework" design
collapses.

Gates (all pre-registered):
1. Convergence: the optimizer must report success.
2. Physical: 0 <= e < 1, a > 0, all finite.
3. Holdout prediction: refit on the first 70% of observations by time,
   predict the held-out 30%, and require holdout_rms <= max(5*sigma,
   3*train_rms). A model that fits train but cannot predict holdout is
   overfit or biased — this is the gate that catches the variant-B
   Keplerian failure internally (its train rms is already 41x sigma, so
   it fails gate 3's sigma leg outright).
4. Noise consistency: train_rms <= 5*sigma. A correct model reaches the
   noise floor; a biased model plateaus far above it. This is the
   conductor's escalation signal, reported here as a gate, not a verdict
   override: a fit can be internally consistent yet still wrong, which
   is why the rung ALSO scores against sealed truth.

DEFINITION (Phase 2 fix #1, 2026-10-26): train_rms is the TRAINING-SPLIT
REFIT's RMS, never the full-data fit's RMS. The refit uses cold /
data-driven starts only — the full-data fit state is NEVER passed as a
hint, because warm-starting a holdout validation is not validation.
When no refit is attempted (too few held-out points, or the fit failed
the convergence/physical gates), train_rms is inf (undefined) and the
verdict follows the holdout-unavailable ABSTAIN path.

ABSTAIN is for the ambiguous middle: converged and physical, but the
holdout check is inconclusive (e.g. too few held-out points). The
conductor treats ABSTAIN as "do not promote without escalation".
"""
import numpy as np

from optimizer_brain import fit_state


def check_fit(fit, ts, obs, predict_fn, sigma, t_ref=None,
              holdout_frac=0.30, seed=0, early_stop_rms=None):
    """Validate a fit dict from optimizer_brain.fit_state.

    Returns dict with verdict ('PASS'/'FAIL'/'ABSTAIN'), gate results,
    train/holdout rms, and reasons. Deterministic given seed.
    """
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    if t_ref is None:
        t_ref = float(ts[0])
    reasons = []
    gates = {}

    # Gate 1: convergence.
    gates['converged'] = bool(fit.get('success', False))
    if not gates['converged']:
        reasons.append('optimizer did not converge')

    # Gate 2: physical.
    a, e = fit.get('a', float('nan')), fit.get('e', float('nan'))
    gates['physical'] = bool(np.isfinite(a) and a > 0
                             and np.isfinite(e) and 0.0 <= e < 1.0)
    if not gates['physical']:
        reasons.append('unphysical elements')

    # Gate 3 + 4: holdout prediction and noise consistency.
    # Phase 2 fix #1: the training refit uses cold/data-driven starts
    # ONLY (no x0_hint from the full-data fit), and train_rms is the
    # refit's RMS, never the full-data fit's RMS.
    n = len(ts)
    n_hold = int(round(n * holdout_frac))
    train_rms = np.inf
    holdout_rms = np.inf
    if n_hold >= 5 and gates['converged'] and gates['physical']:
        order = np.argsort(ts)
        ts_s, obs_s = ts[order], obs[order]
        ts_tr, obs_tr = ts_s[:-n_hold], obs_s[:-n_hold]
        ts_ho, obs_ho = ts_s[-n_hold:], obs_s[-n_hold:]
        refit = fit_state(ts_tr, obs_tr, predict_fn, t_ref=t_ref,
                          n_starts=3, seed=seed,
                          early_stop_rms=early_stop_rms)
        train_rms = float(refit.get('rms_au', np.inf))
        if refit.get('success', False):
            pred = predict_fn(np.array(refit['r0_au'] + refit['v0_au_yr']),
                              ts_ho, t_ref)
            if pred is not None:
                holdout_rms = float(np.sqrt(np.mean((pred - obs_ho) ** 2)))
    gates['noise_consistent'] = bool(np.isfinite(train_rms)
                                     and train_rms <= 5.0 * sigma)
    if not gates['noise_consistent']:
        reasons.append(f'train rms {train_rms:.2e} AU > 5x sigma '
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
        # Predicts holdout but above the noise floor: internally coherent
        # yet the model is missing something. Escalate, don't promote.
        verdict = 'ABSTAIN'
        reasons.append('holdout coherent but above noise floor: escalate')
    else:
        verdict = 'FAIL'

    return {'verdict': verdict, 'gates': gates, 'train_rms_au': train_rms,
            'holdout_rms_au': holdout_rms, 'sigma_au': float(sigma),
            'reasons': reasons}
