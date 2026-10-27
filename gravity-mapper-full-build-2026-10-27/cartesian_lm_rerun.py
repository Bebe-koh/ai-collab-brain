#!/usr/bin/env python3
"""Ammonite blind test re-run through the promoted Cartesian+LM fitter.

Variant A — two-body truth: REBOUND ias15, Sun + massless particle, identical
setup to ammonite_blind_test_note.md section 3 (same arc, cadence, noise).

Variant B — N-body truth (the substantive new rung): Sun + 8 planets
integrated live, massless Ammonite. Planet initial states from JPL's
approximate Keplerian elements Table 1 (verified 2026-10-17 at
https://ssd.jpl.nasa.gov/planets/approx_pos.html; valid 1800-2050, covers the
2005-2026 arc). Observation times and the noise realization are IDENTICAL to
variant A, so the two variants differ ONLY by planetary perturbations.

The fitter (cartesian_lm_fitter.fit_orbit) is a pure two-body Keplerian
fitter in both variants: for variant B this is an explicit, documented model
mismatch — the rung tests whether the standard fitter still recovers the
published (osculating, epoch) elements when the truth includes planetary
perturbations (~2.3e-3 AU over the arc, ~32x the noise sigma).

Pre-registered criterion (unchanged from the note): |dq|/q < 1% AND
|da|/a < 1% on all 3 seeds per variant. Non-convergence or unphysical =
FAIL, not "needs tuning". A variant-B failure is reported honestly with the
numbers; no tuning into passing.

REBOUND guards (note section 7): sim.G = MU_SUN on every simulation;
sim.t equals the element epoch when the epoch-osculating particle is added;
variant-A truth cross-checked against analytic Keplerian propagation
(< 1e-9 AU, asserted inside ammonite_test.make_observations).
"""
import json
import math
import sys
import time

import numpy as np

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/real_data')
import ammonite_test as AT
from secular_elements import elements_to_cart, MU_SUN, TWO_PI
from cartesian_lm_fitter import fit_orbit

SEEDS = AT.SEEDS
T_EPOCH_YR = AT.T_EPOCH_YR
TRUTH = dict(a=248.0, e=0.734, q=248.0 * (1.0 - 0.734))  # adopted JPL SBDB

# ---------------------------------------------------------------- planets
# JPL approximate Keplerian elements, Table 1 (1800-2050), at J2000:
# a [AU], e, I [deg], L [deg], long.peri. [deg], long.node [deg], mass [Msun].
# Verified 2026-10-17 via browser fetch of ssd.jpl.nasa.gov/planets/approx_pos.html.
# Earth row uses the EM Bary elements and Earth+Moon mass.
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


def build_nbody_sim():
    """Sun + 8 planets from JPL Table-1 elements at J2000, integrated to the
    Ammonite element epoch; then the massless particle is added at its
    Sun-relative adopted state (r_sun + r_helio), so its Sun-relative
    osculating state equals the adopted elements exactly at sim.t."""
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
    sim.integrate(T_EPOCH_YR)
    # guard: particle state is osculating at sim.t == T_EPOCH_YR (note sec 7)
    assert abs(sim.t - T_EPOCH_YR) < 1e-12
    sun = sim.particles[0]
    r0, v0 = elements_to_cart(AT.ADOPTED, mu=MU_SUN)
    sim.add(m=0.0,
            x=sun.x + r0[0], y=sun.y + r0[1], z=sun.z + r0[2],
            vx=sun.vx + v0[0], vy=sun.vy + v0[1], vz=sun.vz + v0[2])
    return sim


def make_observations_nbody(seed):
    """N-body truth observations. Identical times and noise realization to
    variant A; the ONLY difference is planetary perturbations in dynamics."""
    ts = AT.opposition_cadence(AT.N_OBS, AT.T_START, AT.T_END, seed)
    pos_helio = np.empty((len(ts), 3))
    # forward pass (t >= epoch) and backward pass (t < epoch), fresh sims
    for direction in ('fwd', 'bwd'):
        sim = build_nbody_sim()
        for k, t in enumerate(ts):
            if (direction == 'fwd') == (t >= T_EPOCH_YR):
                sim.integrate(t, exact_finish_time=1)
                p, s = sim.particles[9], sim.particles[0]
                pos_helio[k] = [p.x - s.x, p.y - s.y, p.z - s.z]
    # sanity: N-body vs two-body difference must be well above the noise
    # (proving the variant is non-trivial) and below a sanity cap. It is
    # dominated by short-period indirect-term oscillations (Jupiter's pull on
    # the Sun, double-integrated in the heliocentric frame), ~0.05 AU here —
    # much larger than the note section 8's 2.3e-3 AU, which compared
    # sim-frame positions and was dominated by the Sun's wobble instead.
    ana = np.array([AT.state_at(AT.ADOPTED, t)[0] for t in ts])
    dmax = float(np.max(np.abs(pos_helio - ana)))
    assert 1e-3 < dmax < 5e-1, f"unexpected N-body deviation: {dmax:.3e} AU"
    rng = np.random.default_rng(seed)  # first draws = noise, as in variant A
    obs = pos_helio + rng.normal(0.0, AT.SIGMA_AU, size=pos_helio.shape)
    with open(HERE + '/sealed_runs/ammonite_truth_nbody.json', 'w') as f:
        json.dump({"object": "2023 KQ14 (Ammonite)", "variant": "B: N-body truth",
                   "adopted_elements": "JPL SBDB 2026-10-14 (same as variant A)",
                   "epoch_jd": AT.EPOCH_JD, "q_au": TRUTH['q'],
                   "planets": "JPL approx elements Table 1 at J2000, live REBOUND",
                   "nbody_deviation_au": dmax, "seed": seed,
                   "note": "SEALED: fitter must never open this file"}, f, indent=1)
    np.savez(HERE + '/sealed_runs/ammonite_obs_nbody.npz',
             t=ts, obs=obs, sigma_au=AT.SIGMA_AU)
    return ts, obs, dmax


def score(fit, variant):
    dq = abs(fit['q'] - TRUTH['q']) / TRUTH['q']
    da = abs(fit['a'] - TRUTH['a']) / TRUTH['a']
    ok = bool(fit['success'] and dq < 0.01 and da < 0.01
              and 0.0 <= fit['e'] < 1.0 and fit['a'] > 0)
    return dict(variant=variant, q_fit=fit['q'], a_fit=fit['a'],
                e_fit=fit['e'], dq_rel=dq, da_rel=da,
                converged=fit['success'], nfev=fit['nfev'],
                rms_au=fit['rms_au'], passed=ok)


def run_variant(variant):
    print(f"=== Variant {variant} ===", flush=True)
    results = []
    for seed in SEEDS:
        if variant == 'A':
            ts, obs = AT.make_observations(seed)  # two-body truth + guard
            dmax = None
        else:
            ts, obs, dmax = make_observations_nbody(seed)
        fit = fit_orbit(ts, obs, t_ref=T_EPOCH_YR, seed=seed)  # blind
        r = score(fit, variant)
        r['seed'] = seed
        if dmax is not None:
            r['nbody_deviation_au'] = dmax
        results.append(r)
        print(f"  seed {seed}: q={r['q_fit']:.4f} (|dq|/q={r['dq_rel']:.4%}) "
              f"a={r['a_fit']:.3f} (|da|/a={r['da_rel']:.4%}) "
              f"nfev={r['nfev']} -> {'PASS' if r['passed'] else 'FAIL'}",
              flush=True)
    npass = sum(r['passed'] for r in results)
    print(f"  VARIANT {variant}: {'PASS' if npass == 3 else 'FAIL'} "
          f"({npass}/3 seeds)", flush=True)
    return results


if __name__ == '__main__':
    t0 = time.time()
    out = {'truth': {**TRUTH, 'source': 'JPL SBDB API 2026-10-14',
                             'note': '66-vs-71 AU dispute resolved for 66'},
           'criterion': '|dq|/q < 1% AND |da|/a < 1% on all 3 seeds',
           'seeds': SEEDS, 'sigma_au': AT.SIGMA_AU}
    out['variant_A_twobody'] = run_variant('A')
    out['variant_B_nbody'] = run_variant('B')
    json.dump(out, open(HERE + '/sealed_runs/cartesian_lm_rerun_results.json',
                        'w'), indent=1)
    a_pass = all(r['passed'] for r in out['variant_A_twobody'])
    b_pass = all(r['passed'] for r in out['variant_B_nbody'])
    print(f"\nOVERALL A (two-body truth): {'PASS' if a_pass else 'FAIL'}",
          flush=True)
    print(f"OVERALL B (N-body truth):   {'PASS' if b_pass else 'FAIL'}",
          flush=True)
    print(f"({time.time()-t0:.0f}s total)", flush=True)
