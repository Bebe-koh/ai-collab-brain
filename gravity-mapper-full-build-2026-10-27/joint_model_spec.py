#!/usr/bin/env python3
"""Joint model specification object (D9 prototype, NEW FILE).

A joint model is plain data, not code behavior: every brain consumes
the same spec, so no brain can close over values the others cannot
see. Stage B frees MASSES ONLY; radii and phases are fixed inventor
context, never parameters.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))

from secular_elements import MU_SUN  # noqa: E402  (path set above)


class JointSpec:
    """Spec for one joint model.

    candidates: list of (radius_au, phase_rad, inventor_mass_solar).
    rails: PlanetRails (or None only for unit-style use without
        planets; the prototype always supplies rails).
    t_ref: epoch of the tracer state (years since J2000).
    rtol/atol: DOP853 tolerances (NBodyParticle defaults).
    holdout_frac: fraction held out by time (default 0.30).
    """

    def __init__(self, candidates, rails, t_ref, rtol=1e-9, atol=1e-11,
                 holdout_frac=0.30):
        self.candidates = []
        for (r, p, m) in candidates:
            r, p, m = float(r), float(p), float(m)
            if not (math.isfinite(r) and r > 0):
                raise ValueError("candidate radius must be finite and > 0")
            if not math.isfinite(p):
                raise ValueError("candidate phase must be finite")
            if not (math.isfinite(m) and m > 0):
                raise ValueError("inventor mass must be finite and > 0")
            self.candidates.append((r, p, m))
        self.rails = rails
        self.t_ref = float(t_ref)
        self.rtol = float(rtol)
        self.atol = float(atol)
        self.holdout_frac = float(holdout_frac)
        self.k = len(self.candidates)
        # D10 bounds: inventor log-mass +/- 3 decades, per candidate.
        self.logmass_bounds = [
            (math.log10(m) - 3.0, math.log10(m) + 3.0)
            for (_, _, m) in self.candidates
        ]
        self.spec_id = self._make_id()

    def _make_id(self):
        parts = [f"k={self.k}", f"t_ref={self.t_ref!r}",
                 f"rtol={self.rtol:g}", f"atol={self.atol:g}"]
        for j, (r, p, m) in enumerate(self.candidates):
            parts.append(f"c{j}:r={r!r},phase={p!r},inv_mass={m!r}")
        return "joint:" + ";".join(parts)

    def inventor_logmasses(self):
        return [math.log10(m) for (_, _, m) in self.candidates]

    def geometry(self):
        """Fixed geometry: list of (radius_au, phase_rad)."""
        return [(r, p) for (r, p, _) in self.candidates]

    def without_candidates(self):
        """The null spec on the same rails/t_ref/tolerances."""
        return JointSpec([], self.rails, self.t_ref,
                         rtol=self.rtol, atol=self.atol,
                         holdout_frac=self.holdout_frac)
