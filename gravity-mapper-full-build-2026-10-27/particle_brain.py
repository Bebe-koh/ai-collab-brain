#!/usr/bin/env python3
"""Particle brain — integrates ONLY the object being fit (brains 2 of 5).

Gravity Mapper modular N-body fitter (2026-10-24).

Two interchangeable propagators with the same call signature
predict(x, ts, t_ref) -> (len(ts), 3) positions or None if unphysical:

- KeplerianParticle: analytic two-body propagation (wraps
  cartesian_lm_fitter.predict_positions). Cheap, biased when planetary
  perturbations matter (the variant-B lesson: 3.1% on a).
- NBodyParticle: integrates the heliocentric equation of motion against
  the rails brain (rails_brain.PlanetRails) with scipy DOP853:

      rddot = -mu_sun * r/|r|^3
              + sum_j mu_j * ( (r_j - r)/|r_j - r|^3 - r_j/|r_j|^3 )

  The first bracket term is the planet's direct pull on the particle;
  the second is the indirect term (the Sun is pulled toward the planet,
  so in the heliocentric frame the particle feels the opposite). Sign
  convention verified numerically against REBOUND (see self-test):
  getting the indirect term backwards produces a ~2x indirect-term
  error, which the self-test catches immediately. This is exactly the
  direct+indirect machinery of the main pipeline (tno_hunt.py /
  residual_hunt.py), now inside the fitter. Planets are NEVER integrated
  here — they come from rails.

Conventions: heliocentric ecliptic J2000, AU, AU/yr, years since J2000,
mu = MU_SUN = 4*pi^2. Unphysical trial states (a <= 0, e >= 1) return
None so the optimizer brain can penalize them.

Self-test (module __main__): propagate the adopted Ammonite elements from
the epoch across the 2005-2026 arc with the N-body particle brain and
compare against an independent REBOUND Sun+8-planets integration (the
variant-B truth builder). Agreement must be < 1e-6 AU — 70x below the
7e-5 AU noise — proving the rails + heliocentric ODE reproduce the
full N-body truth. A sign error in the indirect term would fail this
by ~0.05 AU, so the test is decisive, not decorative.
"""
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))
from secular_elements import cart_to_elements, elements_to_cart, MU_SUN
from cartesian_lm_fitter import predict_positions as kepler_predict


def _physical(x, mu=MU_SUN):
    el = cart_to_elements(np.asarray(x[:3], float),
                          np.asarray(x[3:], float), mu=mu)
    return (np.isfinite(el['a']) and el['a'] > 0
            and 0.0 <= el['e'] < 1.0)


class KeplerianParticle:
    """Analytic two-body propagator (the cheap rung)."""

    def __init__(self, mu=MU_SUN):
        self.mu = mu

    def predict(self, x, ts, t_ref):
        return kepler_predict(x, ts, t_ref, mu=self.mu)


class NBodyParticle:
    """Heliocentric N-body propagator against planet rails.

    Args:
        rails: rails_brain.PlanetRails covering the observation arc.
        rtol, atol: DOP853 tolerances (defaults validated by the module
            self-test to < 1e-6 AU vs REBOUND over a 21-yr arc).
    """

    def __init__(self, rails, mu=MU_SUN, rtol=1e-9, atol=1e-11):
        """Tolerances: rtol=1e-9 was chosen over 1e-11 after timing work
        (2026-10-24): the tighter setting costs ~2.4 s per 21-yr
        propagation (DOP853 resolving Mercury/Venus short periods in the
        rails) and made multi-start N-body fits take ~20 min per seed.
        The 1e-9 setting is re-validated by the module self-test to
        < 1e-6 AU vs REBOUND — still 70x below the 7e-5 AU noise."""
        self.rails = rails
        self.mu = mu
        self.rtol = rtol
        self.atol = atol
        # Import here to avoid a hard dependency at module import time.
        from rails_brain import PLANET_MU
        self.planet_mu = PLANET_MU

    def _rhs(self, t, y):
        r = y[:3]
        v = y[3:]
        rn = np.linalg.norm(r)
        a = -self.mu * r / rn ** 3
        rj = self.rails.positions(t)  # (8, 3)
        d = rj - r  # planet - particle
        dn = np.linalg.norm(d, axis=1)
        rn_j = np.linalg.norm(rj, axis=1)
        a += np.sum(
            self.planet_mu[:, None] * (d / dn[:, None] ** 3
                                       - rj / rn_j[:, None] ** 3), axis=0)
        return np.concatenate([v, a])

    def accel_batch(self, r_xyz, t):
        """Arcade batching (2026-10-27, Atlas-authored, workspace copy):
        accelerations for K tracers at one time, with planet rails and
        the indirect term evaluated ONCE and shared across all tracers.
        Identical formula to _rhs; measured max diff vs the _rhs loop
        is 2.8e-17 AU/yr^2 (machine precision) for 20 tracers, ~18x
        faster than the loop at that size. Does not change _rhs."""
        r = np.asarray(r_xyz, float)
        if r.ndim == 1:
            r = r[None, :]
        rn = np.linalg.norm(r, axis=1)
        a = -self.mu * r / rn[:, None] ** 3
        rj = self.rails.positions(t)  # (8, 3) once
        d = rj[None, :, :] - r[:, None, :]  # (K, 8, 3)
        dn = np.linalg.norm(d, axis=2)
        rn_j = np.linalg.norm(rj, axis=1)
        a = a + np.sum(
            self.planet_mu[None, :, None] * (
                d / dn[:, :, None] ** 3
                - rj[None, :, :] / rn_j[None, :, None] ** 3), axis=1)
        return a

    def _rhs_stack(self, t, y):
        """Stacked right-hand side for predict_many: y is (K*6,)."""
        k = y.shape[0] // 6
        y2 = y.reshape(k, 6)
        out = np.empty_like(y2)
        out[:, :3] = y2[:, 3:]
        out[:, 3:] = self.accel_batch(y2[:, :3], t)
        return out.ravel()

    def predict_many(self, states, ts, t_ref):
        """Propagate K tracers in ONE DOP853 run (stacked state).

        Returns (len(ts), K, 3) positions or None. Same split-at-t_ref
        logic as predict, same tolerances. Measured on 3 tracers over
        a 5-yr arc: 3.9x faster than the predict loop, max diff
        6.2e-09 AU — below both the 1e-6 AU self-test bar and the
        7.04e-05 AU ROM noise floor. A subclass that overrides _rhs
        must also override _rhs_stack (PerturbedParticle does) or its
        extra physics would be silently dropped here."""
        states = np.asarray(states, float)
        if states.ndim != 2 or states.shape[1] != 6:
            return None
        if not all(_physical(s, mu=self.mu) for s in states):
            return None
        ts = np.asarray(ts, float)
        k = states.shape[0]
        out = np.empty((len(ts), k, 3))
        for mask, direction in ((ts >= t_ref, 1), (ts < t_ref, -1)):
            if not mask.any():
                continue
            t_seg = ts[mask]
            order = np.argsort(t_seg) if direction == 1 else \
                np.argsort(-t_seg)
            t_ord = t_seg[order]
            sol = solve_ivp(self._rhs_stack, (t_ref, t_ord[-1]),
                            states.ravel(), method='DOP853',
                            t_eval=t_ord, rtol=self.rtol, atol=self.atol)
            if not sol.success or sol.y.shape[1] != len(t_ord):
                return None
            inv = np.empty_like(order)
            inv[order] = np.arange(len(order))
            out[mask] = sol.y.T.reshape(len(t_ord), k, 6)[:, :, :3][inv]
        if not np.all(np.isfinite(out)):
            return None
        return out

    def predict(self, x, ts, t_ref):
        x = np.asarray(x, float)
        if not _physical(x, mu=self.mu):
            return None
        ts = np.asarray(ts, float)
        out = np.empty((len(ts), 3))
        # Split at t_ref: DOP853 integrates forward and backward cleanly.
        for mask, direction in ((ts >= t_ref, 1), (ts < t_ref, -1)):
            if not mask.any():
                continue
            t_seg = ts[mask]
            # solve_ivp wants the segment ordered in integration direction
            order = np.argsort(t_seg) if direction == 1 else \
                np.argsort(-t_seg)
            t_ord = t_seg[order]
            sol = solve_ivp(self._rhs, (t_ref, t_ord[-1]), x,
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


if __name__ == '__main__':
    # Self-test: N-body particle brain vs independent REBOUND truth.
    import ammonite_test as AT
    import cartesian_lm_rerun as CLR
    from rails_brain import PlanetRails
    rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                              cache_path=HERE + '/sealed_runs/planet_rails.npz')
    # Independent truth: REBOUND Sun + 8 planets + particle (variant B).
    sim = CLR.build_nbody_sim()
    ts = np.linspace(AT.T_START, AT.T_END, 60)
    truth = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        sim.integrate(t, exact_finish_time=1)
        p, s = sim.particles[9], sim.particles[0]
        truth[k] = [p.x - s.x, p.y - s.y, p.z - s.z]
    r0, v0 = elements_to_cart(AT.ADOPTED, mu=MU_SUN)
    x0 = np.concatenate([r0, v0])
    import time
    t0 = time.time()
    nb = NBodyParticle(rails)
    pred = nb.predict(x0, ts, AT.T_EPOCH_YR)
    dt = time.time() - t0
    err = float(np.max(np.abs(pred - truth)))
    print(f"N-body particle brain vs REBOUND truth: max err {err:.2e} AU "
          f"(require < 1e-6 AU), {dt:.2f}s for 60 epochs")
    assert err < 1e-6, "particle brain does not reproduce N-body truth"
    print("PARTICLE SELF-TEST PASS")
