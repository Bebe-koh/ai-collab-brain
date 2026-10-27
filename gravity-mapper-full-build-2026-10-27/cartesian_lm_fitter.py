#!/usr/bin/env python3
"""Cartesian + Levenberg-Marquardt orbit fitter — Gravity Mapper ladder standard.

Promoted 2026-10-17 from diagnostic (ammonite_test.fit_blind_cartesian) to the
ladder's standard orbit-recovery implementation, after the Stage-1 grid +
Nelder-Mead in Keplerian elements FAILED the Ammonite rung (0/3 seeds;
|da|/a 1.1-7.6% vs the 1% criterion; NM never converged on the narrow (a,e)
valley). See hidden_files/ammonite_blind_test_note.md sections 5, 6, 10.

Why this parameterization: the least-squares cost landscape in Cartesian
state-vector space (r0, v0 at epoch) is near-quadratic, so Levenberg-Marquardt
converges in ~10 evaluations; the Keplerian-element landscape has a narrow
curved (a,e) valley that defeats Nelder-Mead. This is standard
orbit-determination practice. Multi-start follows the pattern of
sparse_orbit_fitter.py (multi-start least_squares, best-cost selection).

Conventions: heliocentric ecliptic J2000 Cartesian positions (AU) and
velocities (AU/yr), times in years since J2000, mu = MU_SUN = 4*pi^2
AU^3/yr^2 (matches real_data/secular_elements.py; validated 1.2e-11
round-trip in the secular prototype).

Blind discipline: fit_orbit(ts, obs, ...) receives ONLY observation times
and positions. No truth leakage by construction — there is no truth argument.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'real_data'))
from secular_elements import cart_to_elements, elements_to_cart, MU_SUN, TWO_PI

_BIG = 1e6  # residual penalty for unphysical trial states (flat, LM moves on)


def predict_positions(x, ts, t_ref, mu=MU_SUN):
    """Keplerian positions at times ts for state vector x = [r0, v0] at t_ref.

    x: 6-array, r0 in AU, v0 in AU/yr, heliocentric ecliptic J2000.
    Returns (len(ts), 3) array, or None if the trial state is unphysical
    (a <= 0, e >= 1, or non-finite).
    """
    el = cart_to_elements(np.asarray(x[:3], float),
                          np.asarray(x[3:], float), mu=mu)
    if not (np.isfinite(el['a']) and el['a'] > 0
            and 0.0 <= el['e'] < 1.0):
        return None
    n = math.sqrt(mu / el['a'] ** 3)
    out = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        ek = dict(el)
        ek['M'] = (el['M'] + n * (t - t_ref)) % TWO_PI
        out[k] = elements_to_cart(ek, mu=mu)[0]
    return out


def data_driven_start(ts, obs, t_ref):
    """Initial (r0, v0) at t_ref from a linear fit over the first ~1.5 yr."""
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    m = ts < ts[0] + 1.5
    if m.sum() < 2:
        m = np.ones(len(ts), bool)
    A = np.vstack([ts[m], np.ones(m.sum())]).T
    coef = np.array([np.linalg.lstsq(A, obs[m, j], rcond=None)[0]
                     for j in range(3)])
    v0 = coef[:, 0]
    r0 = v0 * t_ref + coef[:, 1]
    return np.concatenate([r0, v0])


def fit_orbit(ts, obs, t_ref=None, n_starts=8, seed=0, max_nfev=500,
              mu=MU_SUN):
    """Fit Cartesian state (r0, v0) at t_ref to observations by multi-start LM.

    Args:
        ts: (n,) observation times, years since J2000.
        obs: (n,3) heliocentric Cartesian positions, AU.
        t_ref: epoch of the fitted state vector (default: first obs time).
        n_starts: number of LM starts; start 0 is data-driven, the rest are
            relative perturbations of it (3% position, 10% velocity).
        seed: rng seed for the perturbed starts (deterministic).
        max_nfev: per-start function-evaluation cap.
        mu: gravitational parameter (default MU_SUN).

    Returns dict with success flag, elements (a, e, q, Q, angles in deg),
    rms residual, cost, nfev, fitted state vector, and bookkeeping. The best
    start is selected by least-squares cost. success=False if no start
    converged to a physical orbit.
    """
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    if t_ref is None:
        t_ref = float(ts[0])

    def residuals(x):
        pred = predict_positions(x, ts, t_ref, mu=mu)
        if pred is None:
            return np.full(obs.size, _BIG)
        return (pred - obs).ravel()

    rng = np.random.default_rng(seed)
    x0 = data_driven_start(ts, obs, t_ref)
    starts = [x0]
    for _ in range(n_starts - 1):
        rp = x0[:3] * (1.0 + 0.03 * rng.standard_normal(3))
        vp = x0[3:] * (1.0 + 0.10 * rng.standard_normal(3))
        starts.append(np.concatenate([rp, vp]))

    best, best_cost = None, np.inf
    for si, xs in enumerate(starts):
        try:
            sol = least_squares(residuals, xs, method='lm', max_nfev=max_nfev,
                                ftol=1e-15, xtol=1e-15, gtol=1e-15)
        except Exception:
            continue
        if not np.all(np.isfinite(sol.fun)):
            continue
        if predict_positions(sol.x, ts, t_ref, mu=mu) is None:
            continue
        cost = float(np.sum(sol.fun ** 2))
        if cost < best_cost:
            best_cost = cost
            best = (sol, si)

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


if __name__ == '__main__':
    # Self-test: recover a known eccentric orbit from noisy samples.
    rng = np.random.default_rng(0)
    el_true = dict(a=248.0, e=0.734, i=math.radians(11.0),
                   Omega=math.radians(72.1), omega=math.radians(199.0),
                   M=math.radians(357.0))
    r0, v0 = elements_to_cart(el_true)
    t_ref = 26.435
    ts = np.sort(rng.uniform(5.3, 26.5, 60))
    n = math.sqrt(MU_SUN / el_true['a'] ** 3)
    true_pos = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        ek = dict(el_true)
        ek['M'] = (el_true['M'] + n * (t - t_ref)) % TWO_PI
        true_pos[k] = elements_to_cart(ek)[0]
    obs = true_pos + rng.normal(0.0, 7.0e-5, size=true_pos.shape)
    fit = fit_orbit(ts, obs, t_ref=t_ref, seed=1)
    print(f"true: a={el_true['a']} e={el_true['e']} "
          f"q={el_true['a']*(1-el_true['e']):.4f}")
    print(f"fit:  a={fit['a']:.4f} e={fit['e']:.6f} q={fit['q']:.4f} "
          f"nfev={fit['nfev']} rms={fit['rms_au']:.2e} "
          f"success={fit['success']}")
    print(f"|dq|/q={abs(fit['q']-el_true['a']*(1-el_true['e']))/(el_true['a']*(1-el_true['e'])):.2e} "
          f"|da|/a={abs(fit['a']-el_true['a'])/el_true['a']:.2e}")
