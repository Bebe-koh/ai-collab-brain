"""Perturber-parameter fitter on the current stack (J3 achievement port).

Ports the legacy J3 blind two-body recovery to the current build:
  - visible bodies' initial states are GIVEN (like the legacy manifest)
  - hidden perturber parameters (mass, radius, phase per body) are FITTED
    by forward-prediction MSE, with a holdout gate as final judge
  - blind protocol: the fitter takes NO truth; the harness scores after

Forward model: rebound ias15, G = MU_SUN -- the same engine the
validated planet rails are built from (particle_brain's own self-test
validates its integrator against REBOUND to < 1e-6 AU). The fitter does
NOT use PlanetRails/NBodyParticle: those hardcode 8 planets, and a
clean Saturn-plus-Mercury-only system cannot be forced through them
without fighting validated code.

v2 changes (after v1 validation 2026-10-26):
  - MULTI-TRACER fitting: v1's single tracer left a mass-radius
    degeneracy valley (fitted m*r == truth m*r to 4 digits while mass
    and radius were individually 41%/71% off). J3's data had 3 visible
    objects; multiple tracers at different radii break the degeneracy.
    All tracers ride in ONE simulation as massless test particles, so
    one forward prediction still costs one integration.
  - GATE: TWO_BODY iff holdout ratio >= 1.2 (rom_closure discipline).
    v1's any-improvement gate false-positived on noiseless null data
    (a 4e-15 phantom "improved" holdout 58-million-fold by mopping up
    NM convergence residual). The harness now also adds realistic
    noise, which makes the gate meaningful.
  - UNINFORMATIVE JOINT STARTS (J4's remedy, not ported in v1): 8
    random 6D starts alongside the grid seeds, because a heavy
    secondary distorts the one-body fit that grid seeds rely on
    (v1 heavy case: one-body Saturn off 1-2%, joint refine wandered,
    holdout rejected). First-pass refine (maxfev 200), top-2 go to
    full refinement alongside top-2 grid seeds.

v1 scope notes carried over: 3D position MSE (legacy was 2D), tracer
states FIXED at given initial states (only body parameters fitted --
this keeps each evaluation to one forward prediction, not a
tracer-state refit).

v3 changes (eccentric extras, 2026-10-27):
  - REPRESENTATION: candidates may be 4-tuples (mass, a, e, M0) with
    Keplerian eccentric states (_eccentric_state); e = 0 reduces
    EXACTLY to the circular state, so this generalizes rather than
    replacing the circular model. predict_positions dispatches per
    candidate by tuple length, so all circular callers are unchanged.
  - FITTING: fit_eccentric_secondary (circular screen + e-scan over
    top-3 cells + joint 7D refinement of Saturn + eccentric secondary)
    plus uninformative-ecc starts; refine() accepts steps/bounds/func
    overrides (circular behavior unchanged by default).
  - BOUNDS: eccentricity [0, 0.9] (Kepler solver's robust regime);
    mass/radius bounds unchanged (the null-slowness fix).

Search v2 (2026-10-27, after the 9/20 validation): ECC_RADIUS_GRID
(2.5 -> 3.0, 3.5, 4.0, 4.5 -> 5.0), e-scan over top-6 screen cells,
joint seeds 3 grid + 3 uninformative. The circular pipeline is
untouched (grid_screen defaults to RADIUS_GRID); only
fit_eccentric_secondary uses the denser grid.

Search v3 (2026-10-27, after search v2's smoke failed IDENTICALLY on
case 16): the circular screen + e-scan proposal is abandoned for the
secondary stage. A screen diagnostic showed the circular screen is
nearly flat for eccentric truths (best cells 1.5e-10 to 3.3e-10 with
wrong phases/masses), so e-scanning at wrong (m, a, phase) cannot
reach the truth basin. eccentric_screen searches (mass, radius,
phase, e) jointly; the top-3 screen seeds go to joint refinement.

Search v4 (2026-10-27, after search v3's smoke ALSO failed identically
on case 16): the 4D screen's truth neighborhood ranked 25th/34th
because the 1-dex mass grid leaves the nearest cell 3.9x off in mass,
so most of the signal stays unfitted. MASS_GRID_FINE (0.25-dex steps)
puts a cell within 1.33x of any truth mass; a fine-mass screen test
on case 16 put truth-neighborhood cells at ranks 0/1/3 (best
7.55e-11 vs old screen best 1.42e-10). Tests A/B/C established the
truth basin exists and NM converges to it from truth (train
9.79e-15 vs alias 8.40e-11), so the failure is purely proposal
resolution in mass.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize

from rails_brain import MU_SUN

TWO_PI = 2.0 * math.pi

# Grid mirrors J3's screen size: 7 masses x 8 radii x 6 phases = 336.
MASS_GRID = np.logspace(-9, -3, 7)
RADIUS_GRID = np.array([0.35, 0.5, 1.0, 1.5, 2.5, 5.0, 9.6, 20.0])
PHASE_GRID = np.array([i * TWO_PI / 6.0 for i in range(6)])

TOP_K_ONE = 3
TOP_K_JOINT_GRID = 2
TOP_K_JOINT_UNINF = 2

# Eccentric search v2 (2026-10-27 fix, after the 9/20 validation):
# denser radius grid in the 2-6 AU band (the v1 grid jumped 2.5 ->
# 5.0 AU, stranding truths at 3.0-3.9 AU at a 2.5 AU attractor), wider
# e-scan, more joint seeds. grid_screen takes radius_grid as a
# parameter so the VALIDATED circular pipeline keeps its original
# grid byte-for-byte; only the eccentric secondary fit uses
# ECC_RADIUS_GRID. The v2 circular record is unaffected.
ECC_RADIUS_GRID = np.array([0.35, 0.5, 1.0, 1.5, 2.5, 3.0, 3.5, 4.0,
                            4.5, 5.0, 9.6, 20.0])
TOP_K_ECC_SCAN = 6
TOP_K_ECC_JOINT_GRID = 3
TOP_K_ECC_JOINT_UNINF = 3
N_UNINFORMED = 8
UNINF_SEED = 12345
UNINF_MAXFEV = 200
NM_STEPS_1BODY = np.array([0.3, 0.2, 0.5])  # log10m, log10r, phase
NM_MAXFEV_1BODY = 400
NM_MAXFEV_2BODY = 800
NM_XATOL = 1e-3
NM_FATOL = 1e-18
GATE_RATIO = 1.2

# Bounds for Nelder-Mead (added 2026-10-27 after the null-slowness
# diagnosis): the designed search space, exactly. Grid masses span
# 1e-9..1e-3 and radii 0.35..20; uninformative starts span masses
# 1e-9..1e-3 and radii 0.3..25. Without bounds, NM on no-signal (null)
# data drifted a secondary to mass ~5e-13 at radius ~0.0027 AU —
# ~142,000 orbits over the 20-yr span, ~87 s per predict, ~60 hours
# for the remaining evals — while mercury/heavy converge inside the
# designed space in ~4 minutes. These bounds exclude nothing the
# fitter was designed to search; they only stop it leaving that
# space. Phase is unbounded (already modulo 2pi in _params_to_bodies).
NM_BOUNDS_1BODY = [(-9.0, -3.0),
                   (math.log10(0.3), math.log10(25.0)),
                   (None, None)]

# Eccentric joint refinement (v3, 2026-10-27): Saturn (circular 3) +
# secondary (eccentric 4). Steps per parameter and bounds per parameter,
# in joint order [logm1, loga1, phase1, logm2, loga2, e2, phase2].
# Eccentricity bound 0.9 keeps the Kepler solver in its robust regime
# and excludes near-parabolic orbits the mapper does not target.
NM_STEPS_ECC_JOINT = np.array([0.3, 0.2, 0.5, 0.3, 0.2, 0.1, 0.5])
NM_BOUNDS_ECC_JOINT = [(-9.0, -3.0),
                       (math.log10(0.3), math.log10(25.0)),
                       (None, None),
                       (-9.0, -3.0),
                       (math.log10(0.3), math.log10(25.0)),
                       (0.0, 0.9),
                       (None, None)]
NM_MAXFEV_ECC = 1200
E_SCAN = [0.0, 0.1, 0.2, 0.3, 0.4]


def _circular_state(mass, radius, phase):
    """Circular coplanar state at t_ref (heliocentric, before com shift)."""
    v = math.sqrt(MU_SUN / radius)
    return (radius * math.cos(phase), radius * math.sin(phase), 0.0,
            -v * math.sin(phase), v * math.cos(phase), 0.0)


def _kepler_E(M, e):
    """Solve Kepler's equation M = E - e*sin(E) for E (radians).

    Newton iteration from E0 = M + e*sin(M); robust for e <= 0.9
    (the fitter's eccentricity bound). Returns E mod 2pi."""
    M = M % TWO_PI
    if e < 1e-12:
        return M
    E = M + e * math.sin(M)
    for _ in range(100):
        f = E - e * math.sin(E) - M
        fp = 1.0 - e * math.cos(E)
        d = f / fp
        E -= d
        if abs(d) < 1e-13:
            break
    return E % TWO_PI


def _eccentric_state(mass, a, e, M0):
    """Eccentric coplanar state at t_ref from (a, e, mean anomaly M0).

    At e = 0 this reduces EXACTLY to _circular_state with phase = M0
    (E = M0, r = a, velocity = sqrt(mu/a)(-sin M0, cos M0)), so the
    eccentric representation is a strict generalization, not a second
    model. In-plane only (the circular fitter is coplanar throughout).
    """
    E = _kepler_E(M0, e)
    cosE, sinE = math.cos(E), math.sin(E)
    r = a * (1.0 - e * cosE)
    sq = math.sqrt(max(0.0, 1.0 - e * e))
    cos_nu = (cosE - e) / (1.0 - e * cosE)
    sin_nu = (sq * sinE) / (1.0 - e * cosE)
    x, y = r * cos_nu, r * sin_nu
    fac = math.sqrt(MU_SUN * a) / r
    vx, vy = -fac * sinE, fac * sq * cosE
    return (x, y, 0.0, vx, vy, 0.0)


def predict_positions(tracer_states, candidates, ts, mu=MU_SUN):
    """Forward-predict tracer positions at times ts (ascending, >= 0).

    tracer_states: list of (6,) Cartesian (r0, v0) at t_ref=0.
    candidates: list of (mass_solar, radius_au, phase_rad).
    Returns (n, k, 3) barycentric positions (move_to_com applied, exactly
    as in the legacy Sun-momentum adjustment), k = number of tracers.
    None on failure.
    """
    import rebound
    try:
        sim = rebound.Simulation()
        sim.add(m=1.0)
        for cand in candidates:
            if len(cand) == 4:
                mass, a, e, M0 = cand
                x, y, z, vx, vy, vz = _eccentric_state(mass, a, e, M0)
            else:
                mass, radius, phase = cand
                x, y, z, vx, vy, vz = _circular_state(mass, radius, phase)
            sim.add(m=mass, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)
        for st in tracer_states:
            sim.add(m=0.0, x=st[0], y=st[1], z=st[2],
                    vx=st[3], vy=st[4], vz=st[5])
        sim.move_to_com()
        sim.integrator = 'ias15'
        sim.G = mu
        sim.t = 0.0
        k = len(tracer_states)
        out = np.empty((len(ts), k, 3))
        for i, t in enumerate(ts):
            sim.integrate(float(t))
            for j in range(k):
                p = sim.particles[-(k - j)]
                out[i, j] = (p.x, p.y, p.z)
        if not np.all(np.isfinite(out)):
            return None
        return out
    except Exception:
        return None


def _params_to_bodies(params):
    """Flat [log10m, log10r, phase] x n -> [(mass, radius, phase)]."""
    bodies = []
    for i in range(0, len(params), 3):
        bodies.append((10.0 ** params[i], 10.0 ** params[i + 1],
                       params[i + 2] % TWO_PI))
    return bodies


def _bodies_to_params(bodies):
    params = []
    for mass, radius, phase in bodies:
        params.extend([math.log10(mass), math.log10(radius), phase])
    return np.array(params, float)


def _ecc_joint_to_bodies(params):
    """Joint 7-vector -> [Saturn (circular 3-tuple), secondary (ecc 4-tuple)].

    Layout: [logm1, loga1, phase1, logm2, loga2, e2, phase2]."""
    return [(10.0 ** params[0], 10.0 ** params[1], params[2] % TWO_PI),
            (10.0 ** params[3], 10.0 ** params[4],
             min(max(params[5], 0.0), 0.9), params[6] % TWO_PI)]


def _ecc_joint_to_params(bodies):
    sat, sec = bodies
    return np.array([math.log10(sat[0]), math.log10(sat[1]), sat[2],
                     math.log10(sec[0]), math.log10(sec[1]), sec[2],
                     sec[3]], float)


def _ecc_joint_mse(params, tracer_states, ts, obs):
    """MSE of a joint eccentric candidate (Saturn + eccentric secondary)."""
    bodies = _ecc_joint_to_bodies(params)
    pred = predict_positions(tracer_states, list(bodies), ts)
    if pred is None:
        return np.inf
    return float(np.mean((pred - obs) ** 2))


def mse_for_params(params, fixed_bodies, tracer_states, ts, obs):
    """MSE of forward prediction for fitted + fixed bodies vs obs."""
    fitted = _params_to_bodies(params)
    pred = predict_positions(tracer_states, list(fixed_bodies) + fitted, ts)
    if pred is None:
        return np.inf
    return float(np.mean((pred - obs) ** 2))


def grid_screen(tracer_states, ts, obs, fixed_bodies=(),
                radius_grid=None):
    """Score every grid cell (fitted body appended after fixed bodies).

    Returns a list of (mse, candidate) sorted by ascending MSE.
    radius_grid defaults to RADIUS_GRID (the circular pipeline's
    validated grid); the eccentric fit passes ECC_RADIUS_GRID.
    """
    radii = RADIUS_GRID if radius_grid is None else radius_grid
    results = []
    for mass in MASS_GRID:
        for radius in radii:
            for phase in PHASE_GRID:
                cand = (float(mass), float(radius), float(phase))
                pred = predict_positions(tracer_states,
                                         list(fixed_bodies) + [cand], ts)
                if pred is None:
                    continue
                mse = float(np.mean((pred - obs) ** 2))
                results.append((mse, cand))
    results.sort(key=lambda t: t[0])
    return results


def refine(params0, fixed_bodies, tracer_states, ts, obs, maxfev,
           steps=None, bounds=None, func=None):
    """Nelder-Mead refinement of body parameters (log-mass, log-radius,
    phase per body; eccentric joint vectors use steps/bounds/func).

    Returns (best_params, best_mse).

    Bounded to the designed search space (NM_BOUNDS_1BODY per body):
    without bounds NM drifts on flat/no-signal landscapes into
    micro-orbits (see null_slowness_diagnosis.md)."""
    n = len(params0)
    if steps is None:
        steps = np.tile(NM_STEPS_1BODY, n // 3)
    else:
        steps = np.asarray(steps, float)
    # .copy() is REQUIRED: np.asarray does not copy a float64 array,
    # and without it every simplex vertex aliases params0 (degenerate
    # simplex bug caught in v1 smoke testing, 2026-10-26).
    simplex = [np.asarray(params0, float).copy()]
    for i in range(n):
        point = np.asarray(params0, float).copy()
        point[i] += steps[i]
        simplex.append(point)
    # Clip the initial simplex into bounds (starts are inside by
    # construction; this is defense, not a behavior change).
    if bounds is None:
        bounds = NM_BOUNDS_1BODY * (n // 3)
    for point in simplex:
        for i, (lo, hi) in enumerate(bounds):
            if lo is not None:
                point[i] = min(max(point[i], lo), hi)
    if func is not None:
        res = minimize(
            func, np.asarray(params0, float),
            method='Nelder-Mead',
            bounds=bounds,
            options={'initial_simplex': np.array(simplex),
                     'maxfev': maxfev, 'xatol': NM_XATOL,
                     'fatol': NM_FATOL})
    else:
        res = minimize(
            mse_for_params, np.asarray(params0, float),
            args=(fixed_bodies, tracer_states, ts, obs),
            method='Nelder-Mead',
            bounds=bounds,
            options={'initial_simplex': np.array(simplex),
                     'maxfev': maxfev, 'xatol': NM_XATOL,
                     'fatol': NM_FATOL})
    return res.x, float(res.fun)


def _uninformative_starts():
    """N_UNINFORMED random joint 6D starts (seeded, reproducible)."""
    rng = np.random.default_rng(UNINF_SEED)
    starts = []
    for _ in range(N_UNINFORMED):
        bodies = []
        for _ in range(2):
            bodies.append((float(10.0 ** rng.uniform(-9, -3)),
                           float(10.0 ** rng.uniform(math.log10(0.3),
                                                    math.log10(25.0))),
                           float(rng.uniform(0, TWO_PI))))
        starts.append(_bodies_to_params(bodies))
    return starts


def fit_one_body(tracer_states, ts, obs):
    """Blind one-body fit: screen + refine top-K. Returns dict."""
    screen = grid_screen(tracer_states, ts, obs)
    refined = []
    for mse0, cand in screen[:TOP_K_ONE]:
        params, mse = refine(_bodies_to_params([cand]), (),
                             tracer_states, ts, obs, NM_MAXFEV_1BODY)
        refined.append((_params_to_bodies(params), mse))
    refined.sort(key=lambda t: t[1])
    return {'screen_best': screen[0], 'refined': refined,
            'best': refined[0]}


def fit_two_body(tracer_states, ts, obs, body1):
    """Secondary screen given body1 + joint 6D refinement.

    Seeds: top grid seeds plus top uninformative first-pass seeds.
    Returns dict with the best joint solution first.
    """
    screen = grid_screen(tracer_states, ts, obs, fixed_bodies=[body1])
    refined = []
    for mse0, cand in screen[:TOP_K_JOINT_GRID]:
        params0 = _bodies_to_params([body1, cand])
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             NM_MAXFEV_2BODY)
        refined.append((_params_to_bodies(params), mse, 'grid'))
    first_pass = []
    for params0 in _uninformative_starts():
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             UNINF_MAXFEV)
        first_pass.append((params, mse))
    first_pass.sort(key=lambda t: t[1])
    for params0, mse0 in first_pass[:TOP_K_JOINT_UNINF]:
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             NM_MAXFEV_2BODY)
        refined.append((_params_to_bodies(params), mse, 'uninformative'))
    refined.sort(key=lambda t: t[1])
    return {'screen_best': screen[0],
            'refined': [(b, m) for b, m, _ in refined],
            'refined_sources': [s for _, _, s in refined],
            'best': refined[0][:2]}


def _holdout_mse(bodies, tracer_states, ts, obs):
    pred = predict_positions(tracer_states, bodies, ts)
    if pred is None:
        return np.inf
    return float(np.mean((pred - obs) ** 2))


def run_blind_fit(tracer_states, ts_train, obs_train, ts_hold, obs_hold):
    """Full blind two-body pipeline. Takes NO truth. Returns a report."""
    print('  [fit] one-body stage ...', flush=True)
    one = fit_one_body(tracer_states, ts_train, obs_train)
    one_body, one_train = one['best']
    one_hold = _holdout_mse(list(one_body), tracer_states, ts_hold, obs_hold)
    print(f'  [fit] one-body done: train={one_train:.3e} '
          f'holdout={one_hold:.3e}', flush=True)
    print('  [fit] two-body stage ...', flush=True)
    two = fit_two_body(tracer_states, ts_train, obs_train, one_body[0])
    two_bodies, two_train = two['best']
    two_hold = _holdout_mse(list(two_bodies), tracer_states,
                            ts_hold, obs_hold)
    ratio = one_hold / two_hold if two_hold > 0 else float('inf')
    verdict = 'TWO_BODY' if ratio >= GATE_RATIO else 'ONE_BODY'
    return {
        'one_body': {'bodies': [list(b) for b in one_body],
                     'train_mse': one_train, 'holdout_mse': one_hold},
        'two_body': {'bodies': [list(b) for b in two_bodies],
                     'train_mse': two_train, 'holdout_mse': two_hold,
                     'refined_seeds': [
                         {'bodies': [list(b) for b in bodies], 'mse': mse}
                         for bodies, mse in two['refined']],
                     'refined_sources': two['refined_sources']},
        'verdict': verdict,
        'holdout_ratio': ratio,
        'gate_ratio': GATE_RATIO,
        'one_body_screen_best': one['screen_best'],
        'two_body_screen_best': two['screen_best'],
    }


def _uninformative_ecc_starts(body1):
    """N_UNINFORMED joint 7D starts: Saturn at its one-body fit plus a
    random eccentric secondary (seeded, reproducible)."""
    rng = np.random.default_rng(UNINF_SEED)
    sat_params = _bodies_to_params([body1])
    starts = []
    for _ in range(N_UNINFORMED):
        sec = (float(10.0 ** rng.uniform(-9, -3)),
               float(10.0 ** rng.uniform(math.log10(0.3),
                                         math.log10(25.0))),
               float(rng.uniform(0, 0.9)),
               float(rng.uniform(0, TWO_PI)))
        starts.append(np.concatenate(
            [sat_params, _ecc_joint_to_params([body1, sec])[3:]]))
    return starts


E_GRID_ECC = [0.1, 0.2, 0.3, 0.4]

# Search v4 (2026-10-27): 0.25-dex mass grid for the eccentric screen.
# The 1-dex MASS_GRID was the binding constraint: with truth mass
# 3.88e-6, the nearest screen masses (1e-6, 1e-5) are 3.9x / 2.6x off,
# leaving most of the signal unfitted, so the truth neighborhood
# ranked 25th/34th in the 4D screen. At 0.25-dex steps a cell sits
# within 1.33x of any truth mass, and the truth neighborhood takes
# ranks 0/1/3 on case 16 (verified by a fine-mass screen test before
# this change). Full 1e-9..1e-3 range (25 masses); the screen cost is
# 7200 predicts (~4 min/case) -- accepted for a background run.
MASS_GRID_FINE = np.array([10.0 ** (-9.0 + 0.25 * k) for k in range(25)])


def eccentric_screen(tracer_states, ts, obs, fixed_bodies=()):
    """4D eccentric grid screen: (mass, radius, phase, e) cells.

    Search v3 (2026-10-27): the circular screen + e-scan proposal
    failed on case 16 even with a denser radius grid, because the
    circular screen is nearly flat for eccentric truths (best cells
    span 1.5e-10 to 3.3e-10 with wrong phases/masses) and e-scanning
    at wrong (m, a, phase) never reaches the truth basin. This screen
    searches eccentricity jointly from the start instead of hoping
    a circular cell plus an e-tweak stumbles into it. Returns a list
    of (mse, 4-tuple candidate) sorted by ascending MSE.
    """
    results = []
    for mass in MASS_GRID_FINE:
        for radius in ECC_RADIUS_GRID:
            for phase in PHASE_GRID:
                for e in E_GRID_ECC:
                    cand = (float(mass), float(radius), float(e),
                            float(phase))
                    pred = predict_positions(
                        tracer_states, list(fixed_bodies) + [cand], ts)
                    if pred is None:
                        continue
                    mse = float(np.mean((pred - obs) ** 2))
                    results.append((mse, cand))
    results.sort(key=lambda t: t[0])
    return results


def fit_eccentric_secondary(tracer_states, ts, obs, body1):
    """Eccentric secondary fit given body1 (circular Saturn).

    Strategy (search v3): 4D eccentric screen (mass, radius, phase,
    e jointly) -> joint 7D refinement (Saturn 3 + secondary 4) of the
    top-3 screen seeds, plus top-3 uninformative-ecc first-pass seeds.
    Saturn is refined jointly (its one-body fit absorbs some secondary
    signal, as the heavy case showed for the circular pipeline), not
    held fixed. Returns dict with the best joint solution first.
    """
    escored = eccentric_screen(tracer_states, ts, obs,
                               fixed_bodies=[body1])

    def obj(p):
        return _ecc_joint_mse(p, tracer_states, ts, obs)

    refined = []
    for mse0, sec in escored[:TOP_K_ECC_JOINT_GRID]:
        params0 = _ecc_joint_to_params([body1, sec])
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             NM_MAXFEV_ECC, steps=NM_STEPS_ECC_JOINT,
                             bounds=NM_BOUNDS_ECC_JOINT, func=obj)
        refined.append((_ecc_joint_to_bodies(params), mse, 'grid+escan'))
    first_pass = []
    for params0 in _uninformative_ecc_starts(body1):
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             UNINF_MAXFEV, steps=NM_STEPS_ECC_JOINT,
                             bounds=NM_BOUNDS_ECC_JOINT, func=obj)
        first_pass.append((params, mse))
    first_pass.sort(key=lambda t: t[1])
    for params0, mse0 in first_pass[:TOP_K_ECC_JOINT_UNINF]:
        params, mse = refine(params0, (), tracer_states, ts, obs,
                             NM_MAXFEV_ECC, steps=NM_STEPS_ECC_JOINT,
                             bounds=NM_BOUNDS_ECC_JOINT, func=obj)
        refined.append((_ecc_joint_to_bodies(params), mse, 'uninformative'))
    refined.sort(key=lambda t: t[1])
    return {'screen_best': escored[0],
            'ecc_screen_best': escored[0],
            'refined': [(b, m) for b, m, _ in refined],
            'refined_sources': [s for _, _, s in refined],
            'best': refined[0][:2]}


def run_eccentric_fit(tracer_states, ts_train, obs_train, ts_hold, obs_hold):
    """Full eccentric pipeline: circular one-body (Saturn) + eccentric
    secondary. Takes NO truth. Returns a report mirroring run_blind_fit
    (the harness scores parameter recovery; the holdout ratio is
    diagnostic, not the pass criterion)."""
    print('  [fit] one-body stage ...', flush=True)
    one = fit_one_body(tracer_states, ts_train, obs_train)
    one_body, one_train = one['best']
    one_hold = _holdout_mse(list(one_body), tracer_states, ts_hold, obs_hold)
    print(f'  [fit] one-body done: train={one_train:.3e} '
          f'holdout={one_hold:.3e}', flush=True)
    print('  [fit] eccentric-secondary stage ...', flush=True)
    two = fit_eccentric_secondary(tracer_states, ts_train, obs_train,
                                  one_body[0])
    two_bodies, two_train = two['best']
    two_hold = _holdout_mse(list(two_bodies), tracer_states,
                            ts_hold, obs_hold)
    ratio = one_hold / two_hold if two_hold > 0 else float('inf')
    return {
        'one_body': {'bodies': [list(b) for b in one_body],
                     'train_mse': one_train, 'holdout_mse': one_hold},
        'two_body': {'bodies': [list(b) for b in two_bodies],
                     'train_mse': two_train, 'holdout_mse': two_hold,
                     'refined_seeds': [
                         {'bodies': [list(b) for b in bodies], 'mse': mse}
                         for bodies, mse in two['refined']],
                     'refined_sources': two['refined_sources']},
        'holdout_ratio': ratio,
        'one_body_screen_best': one['screen_best'],
        'two_body_screen_best': two['screen_best'],
        'ecc_screen_best': two['ecc_screen_best'],
    }
