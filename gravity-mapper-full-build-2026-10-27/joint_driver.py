#!/usr/bin/env python3
"""Generalized joint driver (D9 prototype, NEW FILE).

Spec object + generalized driver (spec section 2.1-2.3). Adds a
JointParticle propagator and a multi-start LM driver over
theta = tracer state (6) + log10 masses (k). It does NOT modify
fit_state, NBodyParticle, or any existing brain; it mirrors
fit_state's LM discipline verbatim (method, tolerances, start
perturbations, best-cost among COMPLETED starts only, early stop
only after a successful start).

Mass convention (plan, stated before runs): mu_j =
10**(logmass_j) * MU_SUN, masses in solar masses. This follows the
spec text and differs from rom_closure.PerturbedParticle, which
passes inventor masses directly as extra_mus; reconciling the two
is a promotion-time item, not resolved here.
"""
import math
import os
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))
from secular_elements import cart_to_elements, MU_SUN
from cartesian_lm_fitter import data_driven_start
from rails_brain import PLANET_MU

_BIG = 1e6  # residual penalty for unphysical / out-of-bounds trials
MEARTH_SOLAR = 3.003e-6  # presentation only, never enters the fit
# D10 scan: inventor log-mass + these decade offsets, in order.
MASS_SCAN_OFFSETS = [0.0, -1.0, 1.0, -2.0, 2.0]


def _physical(x, mu=MU_SUN):
    el = cart_to_elements(np.asarray(x[:3], float),
                          np.asarray(x[3:], float), mu=mu)
    return (np.isfinite(el['a']) and el['a'] > 0
            and 0.0 <= el['e'] < 1.0)


class JointParticle:
    """Heliocentric ODE propagator: Sun + planet rails + trial
    perturbers. Perturber geometry is fixed (circular coplanar,
    radius/phase from the spec); ONLY masses vary, rebuilt from the
    current trial on every evaluation (spec section 2.2).
    """

    def __init__(self, rails, geometry, logmass_bounds, t_ref,
                 mu=MU_SUN, rtol=1e-9, atol=1e-11):
        self.rails = rails
        self.geometry = list(geometry)  # [(radius_au, phase_rad)]
        self.logmass_bounds = list(logmass_bounds)
        self.t_ref = float(t_ref)
        self.mu = mu
        self.rtol = rtol
        self.atol = atol
        self.planet_mu = PLANET_MU
        self.n_predict_calls = 0
        self.predict_wall_s = 0.0
        self._current_mus = np.zeros(len(self.geometry))

    def _perturber_positions(self, t):
        out = []
        for (r, p) in self.geometry:
            n = math.sqrt(MU_SUN / r ** 3)
            th = p + n * (float(t) - self.t_ref)
            out.append([r * math.cos(th), r * math.sin(th), 0.0])
        return np.array(out) if out else np.zeros((0, 3))

    def _rhs(self, t, y):
        r = y[:3]
        v = y[3:]
        rn = np.linalg.norm(r)
        a = -self.mu * r / rn ** 3
        if self.rails is not None:
            rj = self.rails.positions(t)  # (8, 3)
            d = rj - r
            dn = np.linalg.norm(d, axis=1)
            rn_j = np.linalg.norm(rj, axis=1)
            a = a + np.sum(
                self.planet_mu[:, None] * (d / dn[:, None] ** 3
                                           - rj / rn_j[:, None] ** 3),
                axis=0)
        if len(self.geometry):
            rk = self._perturber_positions(t)
            d = rk - r
            dn = np.linalg.norm(d, axis=1)
            rn_k = np.linalg.norm(rk, axis=1)
            a = a + np.sum(
                self._current_mus[:, None] * (d / dn[:, None] ** 3
                                              - rk / rn_k[:, None] ** 3),
                axis=0)
        return np.concatenate([v, a])

    def predict(self, theta, ts, t_ref):
        """theta = [state(6), log10 masses(k)] -> (n,3) or None."""
        t0 = time.perf_counter()
        try:
            theta = np.asarray(theta, float)
            k = len(self.geometry)
            if theta.shape != (6 + k,):
                return None
            if not np.all(np.isfinite(theta)):
                return None
            if not _physical(theta[:6], mu=self.mu):
                return None
            for j, lm in enumerate(theta[6:]):
                lo, hi = self.logmass_bounds[j]
                if not (lo <= lm <= hi):
                    return None
            # Per-trial rebuild: masses from THIS trial only.
            self._current_mus = (10.0 ** theta[6:]) * MU_SUN
            ts = np.asarray(ts, float)
            out = np.empty((len(ts), 3))
            for mask, direction in ((ts >= t_ref, 1), (ts < t_ref, -1)):
                if not mask.any():
                    continue
                t_seg = ts[mask]
                order = np.argsort(t_seg) if direction == 1 else \
                    np.argsort(-t_seg)
                t_ord = t_seg[order]
                sol = solve_ivp(self._rhs, (t_ref, t_ord[-1]), theta[:6],
                                method='DOP853', t_eval=t_ord,
                                rtol=self.rtol, atol=self.atol)
                if not sol.success or sol.y.shape[1] != len(t_ord):
                    return None
                inv = np.empty_like(order)
                inv[order] = np.arange(len(order))
                out[mask] = sol.y[:3].T[inv]
            if not np.all(np.isfinite(out)):
                return None
            return out
        finally:
            self.n_predict_calls += 1
            self.predict_wall_s += time.perf_counter() - t0


def make_particle(spec):
    """Build a JointParticle for a spec (fresh counters per model)."""
    return JointParticle(spec.rails, spec.geometry(),
                         spec.logmass_bounds, spec.t_ref,
                         rtol=spec.rtol, atol=spec.atol)


def fit_model(ts, obs, spec, particle, n_starts=3, seed=0,
              max_nfev=500, x0_hint_tracer=None, hint_source=None,
              early_stop_rms=None):
    """Multi-start LM fit of theta = state(6) + log10 masses(k).

    Discipline mirrored from fit_state verbatim; the only new
    dimension is the D10 mass scan (start 0 = inventor value, then
    offsets [0,-1,+1,-2,+2] decades cycling). Strict by construction:
    tracer starts are data-driven (or a training-data hint when
    hint_source says so); mass starts are the D10 scan. No full-data
    hint is ever passed by the prototype's own checker.
    """
    ts = np.asarray(ts, float)
    obs = np.asarray(obs, float)
    t_ref = spec.t_ref
    inv_log = np.array(spec.inventor_logmasses(), float)

    def predict_theta(theta):
        return particle.predict(theta, ts, t_ref)

    def residuals(theta):
        pred = predict_theta(theta)
        if pred is None:
            return np.full(obs.size, _BIG)
        return (pred - obs).ravel()

    rng = np.random.default_rng(seed)
    base_tracer = (np.asarray(x0_hint_tracer, float)
                   if x0_hint_tracer is not None
                   else data_driven_start(ts, obs, t_ref))
    starts = []
    for i in range(n_starts):
        if i == 0:
            tr = base_tracer
        else:
            rp = base_tracer[:3] * (1.0 + 0.03 * rng.standard_normal(3))
            vp = base_tracer[3:] * (1.0 + 0.10 * rng.standard_normal(3))
            tr = np.concatenate([rp, vp])
        off = MASS_SCAN_OFFSETS[i % len(MASS_SCAN_OFFSETS)]
        starts.append(np.concatenate([tr, inv_log + off]))

    best, best_cost = None, np.inf
    for si, xs in enumerate(starts):
        try:
            sol = least_squares(residuals, xs, method='lm',
                                max_nfev=max_nfev,
                                ftol=1e-15, xtol=1e-15, gtol=1e-15)
        except Exception:
            continue
        if not sol.success:
            continue
        if not np.all(np.isfinite(sol.fun)):
            continue
        if predict_theta(sol.x) is None:
            continue
        cost = float(np.sum(sol.fun ** 2))
        if cost < best_cost:
            best_cost = cost
            best = (sol, si)
        if (early_stop_rms is not None and best is not None
                and best[0].success
                and float(np.sqrt(np.mean(best[0].fun ** 2)))
                < early_stop_rms):
            break

    if best is None:
        return {'success': False, 'rms_au': np.inf, 'n_obs': len(ts),
                'n_starts': n_starts, 't_ref_yr': float(t_ref),
                'spec_id': spec.spec_id, 'k': spec.k,
                'theta': None, 'logmasses': None,
                'masses_solar': None, 'masses_earth': None,
                'start_rule': 'strict',
                'hint_source': hint_source}
    sol, si = best
    el = cart_to_elements(sol.x[:3], sol.x[3:6], mu=MU_SUN)
    rms = float(np.sqrt(np.mean(sol.fun ** 2)))
    ok = bool(sol.success and np.isfinite(el['a']) and el['a'] > 0
              and 0.0 <= el['e'] < 1.0
              and all(np.isfinite(m) and m > 0
                      for m in (10.0 ** sol.x[6:])))
    masses = [float(10.0 ** lm) for lm in sol.x[6:]]
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
        'v0_au_yr': [float(v) for v in sol.x[3:6]],
        'theta': [float(v) for v in sol.x],
        'logmasses': [float(v) for v in sol.x[6:]],
        'masses_solar': masses,
        'masses_earth': [m / MEARTH_SOLAR for m in masses],
        't_ref_yr': float(t_ref),
        'rms_au': rms, 'cost': float(sol.cost), 'nfev': int(sol.nfev),
        'n_starts': n_starts, 'best_start': int(si),
        'n_obs': len(ts), 'spec_id': spec.spec_id, 'k': spec.k,
        'start_rule': 'strict', 'hint_source': hint_source,
    }
