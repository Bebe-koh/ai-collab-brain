#!/usr/bin/env python3
"""Conductor brain — orchestrates the ladder, declares verdicts (5 of 5).

Gravity Mapper modular N-body fitter (2026-10-24).

Contract: run_ladder(ts, obs, sigma, rails, t_ref) runs the cheap rung
first and escalates ONLY on evidence, never on truth:

1. Keplerian rung: fit with the analytic particle brain, check with the
   checker brain.
2. Escalation rule (pre-registered): if the Keplerian fit's train rms
   exceeds 5x sigma — i.e. the cheap model cannot reach the noise floor
   — the model is biased and the N-body rung is REQUIRED. (Variant A:
   Keplerian rms ~ sigma, no escalation. Variant B: Keplerian rms 41x
   sigma, escalate.) A checker FAIL on convergence/physics also
   escalates; a checker ABSTAIN escalates.
3. N-body rung: fit with the rails particle brain, warm-started from the
   Keplerian best state (warm-starting uses only observations, via the
   Keplerian fit — no truth leakage), check again.
4. Verdict: the final fit, the path taken ('keplerian' or 'nbody'), both
   checker verdicts, and per-rung timing. The conductor NEVER scores
   against truth; the harness does that after the conductor returns.

Timing is measured per rung and reported: the rails design should keep
the N-body fit within a small multiple of the Keplerian cost. If it is
10x slower, the report must say so and explain why.
"""
import time

import numpy as np

from optimizer_brain import fit_state
from checker_brain import check_fit
from particle_brain import KeplerianParticle, NBodyParticle

ESCALATION_RMS_SIGMA = 5.0  # pre-registered: cheap model biased above this


def run_ladder(ts, obs, sigma, rails, t_ref=None, seed=0):
    """Run the two-rung ladder. Returns dict with final fit, path,
    checker verdicts, and timing. Blind: sees only (ts, obs)."""
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    if t_ref is None:
        t_ref = float(ts[0])

    kep = KeplerianParticle()
    t0 = time.time()
    fit_k = fit_state(ts, obs, kep.predict, t_ref=t_ref, seed=seed)
    t_kep = time.time() - t0
    chk_k = check_fit(fit_k, ts, obs, kep.predict, sigma, t_ref=t_ref,
                      seed=seed)

    escalate = (chk_k['verdict'] in ('FAIL', 'ABSTAIN')
                or (np.isfinite(fit_k.get('rms_au', np.inf))
                    and fit_k['rms_au'] > ESCALATION_RMS_SIGMA * sigma))
    result = {'path': 'keplerian', 'fit': fit_k, 'check': chk_k,
              'keplerian_check': chk_k, 'keplerian_time_s': t_kep,
              'nbody_time_s': None, 'nbody_check': None,
              'escalated': bool(escalate)}
    if not escalate:
        return result

    nb = NBodyParticle(rails)
    x_hint = None
    if fit_k.get('success', False):
        x_hint = np.array(fit_k['r0_au'] + fit_k['v0_au_yr'])
    t0 = time.time()
    # N-body path uses fewer starts (4) + early stop at the noise floor:
    # the warm hint is start 0, and a start already at rms < 2*sigma
    # cannot be meaningfully beaten. This cut the first validation run's
    # ~20 min per variant-B seed to minutes without changing the
    # pass/fail criterion or the fitted values (LM converged = converged).
    fit_n = fit_state(ts, obs, nb.predict, t_ref=t_ref, seed=seed,
                      n_starts=4, x0_hint=x_hint,
                      early_stop_rms=2.0 * sigma)
    t_nb = time.time() - t0
    chk_n = check_fit(fit_n, ts, obs, nb.predict, sigma, t_ref=t_ref,
                      seed=seed, early_stop_rms=2.0 * sigma)
    result.update({'path': 'nbody', 'fit': fit_n, 'check': chk_n,
                   'nbody_check': chk_n, 'nbody_time_s': t_nb})
    return result
