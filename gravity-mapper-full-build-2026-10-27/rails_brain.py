#!/usr/bin/env python3
"""Rails brain — known bodies on real ephemerides (read-only planet source).

Gravity Mapper modular N-body fitter, brain 1 of 5 (2026-10-24).

Contract: given a time t (years since J2000), return the heliocentric
ecliptic-J2000 positions of the 8 planets. The fitter NEVER integrates the
planets inside the fit loop; it reads them off rails. That is what makes
N-body fitting affordable: one particle integrated against fixed rails,
not nine bodies re-integrated per function evaluation.

Rails construction: REBOUND ias15, Sun + 8 planets from JPL's approximate
Keplerian elements Table 1 at J2000 (same table as
cartesian_lm_rerun.PLANETS, verified 2026-10-17 at
ssd.jpl.nasa.gov/planets/approx_pos.html; valid 1800-2050, covers the
2005-2026 Ammonite arc). Earth row = EM Bary elements with Earth+Moon
mass, matching the main pipeline's system-GM convention. In the real world
these rails would be JPL Horizons ephemerides; here the Table-1
integration is the stand-in, and it is the SAME planet setup as the
variant-B truth generation — which is legitimate, not circular: planet
positions are known prior knowledge (the "everything we know" directive),
and the blind discipline concerns the fitted particle's elements only.

REBOUND guards (ammonite note section 7): sim.G = MU_SUN on every
simulation; sim.t is tracked explicitly; particle states are osculating
at their stated epoch.

Output: PlanetRails.positions(t) -> (8, 3) AU, cubic-spline interpolated.
Self-test (module __main__): spline vs direct REBOUND integration at
random times must agree to < 1e-8 AU (1000x below the 7e-5 AU noise).
"""
import math
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'real_data'))
from secular_elements import elements_to_cart, MU_SUN

# JPL approximate Keplerian elements, Table 1 (1800-2050), at J2000.
# Copied from cartesian_lm_rerun.PLANETS (verified 2026-10-17) with
# provenance, rather than imported through a fragile chain.
# Columns: name, a [AU], e, I [deg], L [deg], long.peri. [deg],
#          long.node [deg], mass [Msun].
PLANETS = [
    ("Mercury", 0.38709927, 0.20563593, 7.00497902, 252.25032350,
     77.45779628, 48.33076593, 1.660e-07),
    ("Venus", 0.72333566, 0.00677672, 3.39467605, 181.97909950,
     131.60246718, 76.67984255, 2.448e-06),
    ("Earth", 1.00000261, 0.01671123, -0.00001531, 100.46457166,
     102.93768193, 0.0, 3.040e-06),
    ("Mars", 1.52371034, 0.09339410, 1.84969142, -4.55343205,
     -23.94362959, 49.55953891, 3.213e-07),
    ("Jupiter", 5.20288700, 0.04838624, 1.30439695, 34.39644051,
     14.72847983, 100.47390909, 9.548e-04),
    ("Saturn", 9.53667594, 0.05386179, 2.48599187, 49.95424423,
     92.59887831, 113.66242448, 2.859e-04),
    ("Uranus", 19.18916464, 0.04725744, 0.77263783, 313.23810451,
     170.95427630, 74.01692503, 4.366e-05),
    ("Neptune", 30.06992276, 0.00859048, 1.77004347, -55.12002969,
     44.96476227, 131.78422574, 5.152e-05),
]
PLANET_NAMES = [p[0] for p in PLANETS]
PLANET_MASSES = np.array([p[7] for p in PLANETS])  # Msun
PLANET_MU = PLANET_MASSES * MU_SUN  # AU^3/yr^2


def build_planet_sim():
    """Sun + 8 planets at J2000 from Table 1, REBOUND ias15, G = MU_SUN."""
    import rebound
    sim = rebound.Simulation()
    sim.add(m=1.0)
    for name, a, e, inc, L, lp, node, m in PLANETS:
        el = dict(a=a, e=e, i=math.radians(inc),
                  Omega=math.radians(node % 360.0),
                  omega=math.radians((lp - node) % 360.0),
                  M=math.radians((L - lp) % 360.0))
        r, v = elements_to_cart(el, mu=MU_SUN)
        sim.add(m=m, x=r[0], y=r[1], z=r[2], vx=v[0], vy=v[1], vz=v[2])
    sim.integrator = 'ias15'
    sim.G = MU_SUN  # guard: REBOUND defaults to G=1 (note section 7)
    sim.t = 0.0
    return sim


class PlanetRails:
    """Cubic-spline planet rails over [t_min, t_max] (years since J2000)."""

    def __init__(self, t_grid, pos_grid):
        """t_grid: (nt,) years; pos_grid: (nt, 8, 3) heliocentric AU."""
        self._grid_t = np.asarray(t_grid, float)
        self._grid_pos = np.asarray(pos_grid, float)
        self.t_min = float(t_grid[0])
        self.t_max = float(t_grid[-1])
        self.splines = [CubicSpline(self._grid_t, self._grid_pos[:, j, c])
                        for j in range(8) for c in range(3)]

    def positions(self, t):
        """Heliocentric planet positions at time t (scalar or array).

        Scalar t -> (8, 3). Array t (nt,) -> (nt, 8, 3). Raises if t is
        outside the rails range (no extrapolation, ever).
        """
        t = np.asarray(t, float)
        if t.min() < self.t_min or t.max() > self.t_max:
            raise ValueError(
                f"time {t.min()}..{t.max()} outside rails "
                f"{self.t_min}..{self.t_max}")
        if t.ndim == 0:
            return np.array([[self.splines[j * 3 + c](float(t))
                              for c in range(3)] for j in range(8)])
        out = np.empty((len(t), 8, 3))
        for j in range(8):
            for c in range(3):
                out[:, j, c] = self.splines[j * 3 + c](t)
        return out

    def save(self, path):
        np.savez(path, grid_t=self._grid_t, grid_pos=self._grid_pos)

    @classmethod
    def build(cls, t_min, t_max, dt_days=0.5, cache_path=None):
        """Integrate planets once, sample heliocentric positions, spline."""
        if cache_path and os.path.exists(cache_path):
            d = np.load(cache_path)
            return cls(d['grid_t'], d['grid_pos'])
        sim = build_planet_sim()
        dt_yr = dt_days / 365.25
        t_grid = np.arange(t_min, t_max + 0.5 * dt_yr, dt_yr)
        pos_grid = np.empty((len(t_grid), 8, 3))
        for k, t in enumerate(t_grid):
            sim.integrate(t, exact_finish_time=1)
            s = sim.particles[0]
            for j in range(8):
                p = sim.particles[j + 1]
                pos_grid[k, j] = [p.x - s.x, p.y - s.y, p.z - s.z]
        obj = cls(t_grid, pos_grid)
        if cache_path:
            obj.save(cache_path)
        return obj


if __name__ == '__main__':
    # Self-test: spline vs direct REBOUND at random times.
    rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                              cache_path=HERE + '/sealed_runs/planet_rails.npz')
    sim = build_planet_sim()
    rng = np.random.default_rng(0)
    worst = 0.0
    for t in rng.uniform(5.0, 26.5, 20):
        sim.integrate(t, exact_finish_time=1)
        s = sim.particles[0]
        direct = np.array([[sim.particles[j + 1].x - s.x,
                            sim.particles[j + 1].y - s.y,
                            sim.particles[j + 1].z - s.z]
                           for j in range(8)])
        err = float(np.max(np.abs(rails.positions(t) - direct)))
        worst = max(worst, err)
    print(f"rails spline vs direct REBOUND: max err {worst:.2e} AU "
          f"(require < 1e-8 AU)")
    assert worst < 1e-8, "rails interpolation too coarse"
    print("RAILS SELF-TEST PASS")
