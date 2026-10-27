#!/usr/bin/env python3
"""Proposal 2 comparison test: spline vs analytic circular extras.

Measurement/harness only — no mapper source is modified.
Step 1 (positions) already done in profile_extra_rails.py:
  max spline-vs-analytic diff 1.567e-08 AU.
Step 2 (this script, no rebound needed): compare the extra-body
  acceleration term computed from spline rails vs analytic rails.
Step 3 (needs rebound): fixed-state propagation comparison, spline
  extras vs analytic extras, everything else identical.
"""
import math
import sys

import numpy as np

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/real_data')

from secular_elements import MU_SUN
from rom_closure import ExtraRails

BODIES = [(3e-6, 2.5, 0.5), (1.6e-7, 0.39, 0.19),
          (1e-5, 5.2, 1.0), (5e-6, 7.6, 2.0)]
MUS = np.array([m for m, _, _ in BODIES])
T_REF, T_MIN, T_MAX = 5.0, 0.0, 27.0


class AnalyticRails:
    """Same positions() interface as ExtraRails, direct formula only."""

    def __init__(self, bodies, t_ref):
        self.bodies = list(bodies)
        self.t_ref = t_ref
        self.n = len(bodies)

    def positions(self, t):
        out = []
        for (m, r, p) in self.bodies:
            n = math.sqrt(MU_SUN / r ** 3)
            th = p + n * (float(t) - self.t_ref)
            out.append([r * math.cos(th), r * math.sin(th), 0.0])
        return np.array(out)


def extra_accel(rk, r, mus):
    """The extra-body term from PerturbedParticle._rhs (direct+indirect)."""
    d = rk - r
    dn = np.linalg.norm(d, axis=1)
    rn = np.linalg.norm(rk, axis=1)
    return np.sum(mus[:, None] * (d / dn[:, None] ** 3
                                  - rk / rn[:, None] ** 3), axis=0)


def main():
    spline = ExtraRails.from_bodies(BODIES, T_REF, T_MIN, T_MAX)
    analytic = AnalyticRails(BODIES, T_REF)

    # Step 2: acceleration comparison over times and tracer positions.
    times = np.linspace(0.5, 26.5, 27)
    phases = np.linspace(0.0, 2 * np.pi, 8, endpoint=False)
    max_diff = 0.0
    max_a = 0.0
    for t in times:
        rk_s = spline.positions(float(t))
        rk_a = analytic.positions(float(t))
        for ph in phases:
            r = np.array([math.cos(ph), math.sin(ph), 0.0])
            a_s = extra_accel(rk_s, r, MUS)
            a_a = extra_accel(rk_a, r, MUS)
            max_diff = max(max_diff, np.max(np.abs(a_s - a_a)))
            max_a = max(max_a, np.max(np.abs(a_s)))
    print(f"extra-accel max abs diff: {max_diff:.3e} AU/yr^2 "
          f"(typical |a_extra| scale: {max_a:.3e})", flush=True)
    print(f"diff relative to accel scale: {max_diff / max_a:.3e}",
          flush=True)

    # Step 3: fixed-state propagation comparison (needs rebound).
    try:
        from rails_brain import PlanetRails
        from rom_closure import PerturbedParticle
    except ImportError as e:
        print(f"propagation comparison skipped (no rebound): {e}", flush=True)
        return
    planet_rails = PlanetRails.build(0.0, 27.0, dt_days=0.5)
    p_spline = PerturbedParticle(planet_rails, BODIES, MUS,
                                 T_REF, 0.0, 27.0)
    p_analytic = PerturbedParticle(planet_rails, BODIES, MUS,
                                   T_REF, 0.0, 27.0)
    p_analytic.extra_rails = analytic
    n = math.sqrt(MU_SUN)
    x0 = np.array([1.0, 0.0, 0.0, 0.0, n, 0.0])
    ts_obs = np.linspace(5.0, 20.0, 60)
    out_s = p_spline.predict(x0, ts_obs, T_REF)
    out_a = p_analytic.predict(x0, ts_obs, T_REF)
    if out_s is None or out_a is None:
        print("propagation comparison failed: a predict returned None",
              flush=True)
        return
    traj_diff = np.max(np.abs(out_s - out_a))
    print(f"15-yr propagation max traj diff: {traj_diff:.3e} AU",
          flush=True)


if __name__ == '__main__':
    main()
