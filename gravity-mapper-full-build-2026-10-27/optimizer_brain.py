#!/usr/bin/env python3
"""Optimizer brain — model-agnostic Levenberg-Marquardt (brains 3 of 5).

Gravity Mapper modular N-body fitter (2026-10-24).

Contract: fit_state(ts, obs, predict_fn, ...) minimizes residuals between
a propagator's predictions and observations. It knows NOTHING about
dynamics: predict_fn(x, ts, t_ref) is supplied by the particle brain
(Keplerian or N-body — the optimizer cannot tell which, and must not
care). Multi-start follows the sparse_orbit_fitter.py pattern (start 0
data-driven, the rest perturbed; best-cost selection), reusing
cartesian_lm_fitter.data_driven_start.

Blind discipline: fit_state receives ONLY observation times and
positions. No truth argument exists.

Returns the same dict shape as cartesian_lm_fitter.fit_orbit (success,
elements, rms, cost, nfev, state vector, bookkeeping) so the checker and
conductor brains work unchanged across propagators.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))
from secular_elements import cart_to_elements, MU_SUN
from cartesian_lm_fitter import data_driven_start

_BIG = 1e6  # residual penalty for unphysical trial states


def fit_state(ts, obs, predict_fn, t_ref=None, n_starts=8, seed=0,
              max_nfev=500, mu=MU_SUN, x0_hint=None, early_stop_rms=None):
    """Multi-start LM fit of Cartesian state (r0, v0) at t_ref.

    Args:
        ts, obs: observation times (yr since J2000) and (n,3) positions.
        predict_fn: particle-brain callable predict(x, ts, t_ref) -> (n,3)
            or None if the trial state is unphysical.
        t_ref: epoch of the fitted state (default: first obs time).
        x0_hint: optional starting state (e.g. the cheap rung's best fit,
            used by the conductor to warm-start the N-body fit). When
            given, start 0 is the hint and the rest perturb it.
        early_stop_rms: if given, stop trying further starts once a
            SUCCESSFUL start reaches rms < early_stop_rms. Principled: the
            noise floor is the goal, and a start already there cannot be
            meaningfully beaten (added 2026-10-24 after the first
            N-body validation run showed 8 full starts at ~2 s per
            predict taking ~20 min per seed). Best-cost selection among
            COMPLETED starts is unchanged; only unneeded starts are
            skipped. Never affects the pass/fail criterion.
            Phase 2 fix #1 (2026-10-26): only successful starts count
            toward best-cost selection, and early stopping requires the
            current best start to be successful.

    Returns dict (see module docstring). success=False if no start
    converged to a physical orbit.
    """
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    if t_ref is None:
        t_ref = float(ts[0])

    def residuals(x):
        pred = predict_fn(x, ts, t_ref)
        if pred is None:
            return np.full(obs.size, _BIG)
        return (pred - obs).ravel()

    rng = np.random.default_rng(seed)
    x_base = (np.asarray(x0_hint, float) if x0_hint is not None
              else data_driven_start(ts, obs, t_ref))
    starts = [x_base]
    for _ in range(n_starts - 1):
        rp = x_base[:3] * (1.0 + 0.03 * rng.standard_normal(3))
        vp = x_base[3:] * (1.0 + 0.10 * rng.standard_normal(3))
        starts.append(np.concatenate([rp, vp]))

    best, best_cost = None, np.inf
    for si, xs in enumerate(starts):
        try:
            sol = least_squares(residuals, xs, method='lm', max_nfev=max_nfev,
                                ftol=1e-15, xtol=1e-15, gtol=1e-15)
        except Exception:
            continue
        # Phase 2 fix #1: only successful starts count. An unconverged
        # run must never displace a converged one, however cheap it is.
        if not sol.success:
            continue
        if not np.all(np.isfinite(sol.fun)):
            continue
        if predict_fn(sol.x, ts, t_ref) is None:
            continue
        cost = float(np.sum(sol.fun ** 2))
        if cost < best_cost:
            best_cost = cost
            best = (sol, si)
        if (early_stop_rms is not None and best is not None
                and best[0].success
                and float(np.sqrt(np.mean(best[0].fun ** 2))) < early_stop_rms):
            break  # noise floor reached; further starts cannot beat it

    if best is None:
        return {'success': False, 'rms_au': np.inf, 'n_obs': len(ts),
                'n_starts': n_starts, 't_ref_yr': float(t_ref)}
    sol, si = best
    el = cart_to_elements(sol.x[:3], sol.x[3:], mu=mu)
    rms = float(np.sqrt(np.mean(sol.fun ** 2)))
    ok = bool(sol.success and np.isfinite(el['a']) and el['a'] > 0
              and 0.0 <= el['e'] < 1.0)
    return {
        'success': ok,
        'a': float(el['a']), 'e': float(el['e']),
        'q': float(el['q']), 'Q': float(el['Q']),
        'i_deg': math.degrees(el['i']),
        'Om_deg': math.degrees(el['Omega']),
        'om_deg': math.degrees(el['omega']),
        'M0_deg': math.degrees(el['M']),
        'elements': {k: float(v) for k, v in el.items()},
        'r0_au': [float(v) for v in sol.x[:3]],
        'v0_au_yr': [float(v) for v in sol.x[3:]],
        't_ref_yr': float(t_ref),
        'rms_au': rms, 'cost': float(sol.cost), 'nfev': int(sol.nfev),
        'n_starts': n_starts, 'best_start': int(si),
        'n_obs': len(ts),
    }
