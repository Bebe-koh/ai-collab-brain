#!/usr/bin/env python3
"""Ammonite (2023 KQ14) blind-recovery test — Gravity Mapper benchmark ladder.

Rung: known-body orbit recovery. Forward-integrate Ammonite's published
(JPL SBDB) orbit, generate synthetic heliocentric observations over the real
2005-2026 arc with JPL-rms-calibrated noise, seal the truth, and fit
Keplerian elements blind with a Stage-1 grid + Nelder-Mead refiner.
Success criterion (pre-registered): |dq|/q < 1% AND |da|/a < 1%.

Element machinery: hidden_files/real_data/secular_elements.py conventions
(heliocentric ecliptic J2000, mu = 4*pi^2 AU^3/yr^2), validated 1.2e-11
round-trip in the secular prototype note.
"""
import json, math, sys, time
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data')
from secular_elements import cart_to_elements, elements_to_cart, MU_SUN, TWO_PI

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
TRUTH_PATH = HERE + '/sealed_runs/ammonite_truth.json'
OBS_PATH = HERE + '/sealed_runs/ammonite_obs.npz'

# ------------------------------------------------------------------ adopted truth
# JPL Small-Body Database API, accessed 2026-10-14
# (https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=2023%20KQ14).
# Perihelion-discrepancy flag: secondary sources disagree (66 vs 71 AU).
# JPL SBDB gives q = 65.9 +/- 0.0068 AU -> the 66 AU value wins; 71 AU is
# outdated. n_obs=102, arc 2005-04-11..2026-07-20 (7770 d), rms 0.22",
# condition code 3, solution date 2026-10-13.
EPOCH_JD = 2461200.5
T_EPOCH_YR = (EPOCH_JD - 2451545.0) / 365.25   # years since J2000
ADOPTED = dict(a=248.0, e=0.734,
               i=math.radians(11.0), Omega=math.radians(72.1),
               omega=math.radians(199.0), M=math.radians(357.0))
Q_TRUE = ADOPTED['a'] * (1.0 - ADOPTED['e'])   # 65.928
# Observation window (real arc): 2005-04-11 .. 2026-07-20, in yr since J2000
T_START = (2453465.5 - 2451545.0) / 365.25     # 2005-04-11 ~ 5.266
T_END = (2461244.5 - 2451545.0) / 365.25       # 2026-07-20 ~ 26.551
N_OBS = 102
# Noise: JPL fit rms = 0.22 arcsec. At ~66 AU, 0.22" = 66*0.22/206265 AU.
SIGMA_AU = 66.0 * 0.22 / 206265.0              # ~7.0e-5 AU per component
SEEDS = [7, 777, 20261014]


def kepler_E(M, e):
    E = M
    for _ in range(60):
        dE = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= dE
        if abs(dE) < 1e-14:
            break
    return E


def state_at(el, t, t_ref=T_EPOCH_YR):
    """Analytic Keplerian state at time t (yr) for elements at t_ref."""
    n = math.sqrt(MU_SUN / el['a'] ** 3)
    M = (el['M'] + n * (t - t_ref)) % TWO_PI
    el_t = dict(el); el_t['M'] = M
    return elements_to_cart(el_t)


def make_truth_two_body():
    """Truth trajectory: integrate adopted elements with REBOUND (Sun +
    massless particle) over the arc; verify against analytic propagation."""
    import rebound
    r0, v0 = elements_to_cart(ADOPTED)
    sim = rebound.Simulation()
    sim.add(m=1.0)
    sim.add(m=0.0, x=r0[0], y=r0[1], z=r0[2], vx=v0[0], vy=v0[1], vz=v0[2])
    sim.integrator = 'ias15'
    sim.G = MU_SUN  # AU^3/yr^2/Msun: match element conventions
    sim.t = T_EPOCH_YR
    ts = np.linspace(T_START, T_END, 400)
    traj = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        sim.integrate(t, exact_finish_time=1)
        p = sim.particles[1]
        traj[k] = [p.x, p.y, p.z]
    # verify vs analytic
    ana = np.array([state_at(ADOPTED, t)[0] for t in ts])
    maxdiff = float(np.max(np.abs(traj - ana)))
    return traj, ts, maxdiff


def planetary_check():
    """Max |two-body - N-body| over the arc with 8 planets (circular approx).
    Documents that a pure-Keplerian truth is adequate for a sednoid here."""
    import rebound
    GM = {'Mercury': 1.660e-7, 'Venus': 2.448e-6, 'Earth': 3.004e-6,
          'Mars': 3.213e-7, 'Jupiter': 9.548e-4, 'Saturn': 2.859e-4,
          'Uranus': 4.366e-5, 'Neptune': 5.152e-5}  # solar masses
    A = [0.387, 0.723, 1.0, 1.524, 5.203, 9.537, 19.19, 30.07]
    r0, v0 = elements_to_cart(ADOPTED)
    s1 = rebound.Simulation(); s1.add(m=1.0)
    s1.add(m=0.0, x=r0[0], y=r0[1], z=r0[2], vx=v0[0], vy=v0[1], vz=v0[2])
    s1.integrator = 'ias15'
    s1.G = MU_SUN
    s1.t = T_EPOCH_YR
    s2 = rebound.Simulation(); s2.add(m=1.0)
    for m, a in zip(GM.values(), A):
        s2.add(m=m, a=a)
    s2.add(m=0.0, x=r0[0], y=r0[1], z=r0[2], vx=v0[0], vy=v0[1], vz=v0[2])
    s2.integrator = 'ias15'
    s2.G = MU_SUN
    s2.t = T_EPOCH_YR
    ts = np.linspace(T_START, T_END, 60)
    dmax = 0.0
    for t in ts:
        s1.integrate(t, exact_finish_time=1); s2.integrate(t, exact_finish_time=1)
        p1, p2 = s1.particles[1], s2.particles[9]  # s2: 0=Sun, 1-8=planets, 9=particle
        d = math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2 + (p1.z-p2.z)**2)
        dmax = max(dmax, d)
    return dmax


def opposition_cadence(n, t_start, t_end, seed):
    """Survey-like cadence: observations only within +/-75 d of yearly
    opposition (outer object unobservable near conjunction). ~n obs total."""
    rng = np.random.default_rng(seed)
    years = np.arange(math.floor(t_start), math.ceil(t_end) + 1)
    per = max(1, int(round(n / len(years))))
    ts = []
    for y in years:
        opp = y + 0.05  # opposition ~early Jan (proxy; exact date irrelevant)
        w = rng.uniform(-75.0, 75.0, per) / 365.25
        for dt in w:
            t = opp + dt
            if t_start <= t <= t_end:
                ts.append(t)
    ts = np.array(sorted(ts))
    # trim/pad to exactly n
    if len(ts) > n:
        ts = np.sort(rng.choice(ts, n, replace=False))
    while len(ts) < n:
        ts = np.append(ts, rng.uniform(t_start, t_end, n - len(ts)))
        ts = np.unique(np.round(ts, 6))[:n]
    return np.sort(ts)


def make_observations(seed):
    """Generate noisy synthetic observations. Writes sealed truth + obs."""
    import rebound
    rng = np.random.default_rng(seed)
    r0, v0 = elements_to_cart(ADOPTED)
    sim = rebound.Simulation()
    sim.add(m=1.0)
    sim.add(m=0.0, x=r0[0], y=r0[1], z=r0[2], vx=v0[0], vy=v0[1], vz=v0[2])
    sim.integrator = 'ias15'
    sim.G = MU_SUN  # AU^3/yr^2/Msun: match element conventions
    sim.t = T_EPOCH_YR  # state vector is osculating at T_EPOCH_YR, not t=0
    ts = opposition_cadence(N_OBS, T_START, T_END, seed)
    pos = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        sim.integrate(t, exact_finish_time=1)
        p = sim.particles[1]
        pos[k] = [p.x, p.y, p.z]
    noise = rng.normal(0.0, SIGMA_AU, size=pos.shape)
    obs = pos + noise
    with open(TRUTH_PATH, 'w') as f:
        json.dump({"object": "2023 KQ14 (Ammonite)", "source": "JPL SBDB API 2026-10-14",
                   "epoch_jd": EPOCH_JD, "elements": {k: (float(v) if k == 'a' else float(v)) for k, v in ADOPTED.items()},
                   "elements_deg": {"i": 11.0, "Omega": 72.1, "omega": 199.0, "M": 357.0},
                   "q_au": Q_TRUE, "seed": seed,
                   "note": "SEALED: fitter must never open this file"}, f, indent=1)
    np.savez(OBS_PATH, t=ts, obs=obs, sigma_au=SIGMA_AU)
    # self-consistency guard: REBOUND truth must match analytic Keplerian
    # propagation (catches G/units/epoch bugs like the 2026-10-14 G=1 incident)
    ana = np.array([state_at(ADOPTED, t)[0] for t in ts])
    maxdev = float(np.max(np.abs(pos - ana)))
    assert maxdev < 1e-9, f"truth/propagation mismatch: {maxdev:.3e} AU"
    return ts, obs


# ------------------------------------------------------------------ blind fit
def predict_batch(x, ts, t_ref=T_EPOCH_YR):
    """Positions at ts for parameter vector
    x = [log10(a), logit(e), i, Omega, omega, M0]."""
    loga, ue, i, Om, om, M0 = x
    a = 10.0 ** loga
    e = 1.0 / (1.0 + math.exp(-ue))
    el = dict(a=a, e=e, i=i, Omega=Om % TWO_PI, omega=om % TWO_PI, M=M0 % TWO_PI)
    n = math.sqrt(MU_SUN / a ** 3)
    out = np.empty((len(ts), 3))
    for k, t in enumerate(ts):
        el['M'] = (M0 + n * (t - t_ref)) % TWO_PI
        out[k] = elements_to_cart(el)[0]
    return out


def data_driven_start(ts, obs):
    """Seed angles from first-epoch position + finite-difference velocity."""
    r0 = obs[0]
    # velocity from linear fit over first ~1.5 yr of data
    m = ts < ts[0] + 1.5
    A = np.vstack([ts[m], np.ones(m.sum())]).T
    v = np.array([np.linalg.lstsq(A, obs[m, j], rcond=None)[0][0] for j in range(3)])
    el = cart_to_elements(r0, v)
    ue = math.log(el['e'] / max(1e-9, 1.0 - el['e']))
    return np.array([math.log10(max(el['a'], 1.0)), ue, el['i'], el['Omega'], el['omega'], el['M']])


def fit_blind(ts, obs):
    """Stage-1 coarse grid over (log10 a, e) + Nelder-Mead refine of top 5.

    The fitter sees ONLY (ts, obs). No truth leakage: angles for the grid
    scan come from the data-driven start above.
    """
    n = len(ts)
    cut = int(0.7 * n)
    t_tr, o_tr, t_ho, o_ho = ts[:cut], obs[:cut], ts[cut:], obs[cut:]
    x0 = data_driven_start(t_tr, o_tr)

    def tmse_full(x):
        pred = predict_batch(x, t_tr)
        return float(np.mean((o_tr - pred) ** 2))

    # Stage 1: grid over (log10 a, e); angles fixed from data-driven start
    loga_grid = np.linspace(math.log10(30.0), math.log10(1000.0), 8)
    e_grid = np.linspace(0.05, 0.95, 8)
    ue_grid = np.log(e_grid / (1.0 - e_grid))
    scored = []
    for la in loga_grid:
        for ue in ue_grid:
            x = x0.copy(); x[0] = la; x[1] = ue
            scored.append((tmse_full(x), x.copy()))
    scored.sort(key=lambda t: t[0])

    # Stage 2: Nelder-Mead refine top 5 on all 6 params
    refined = []
    for s, xg in scored[:5]:
        res = minimize(tmse_full, xg, method='Nelder-Mead',
                       options={'maxiter': 600, 'xatol': 1e-10, 'fatol': 1e-16})
        pred_ho = predict_batch(res.x, t_ho)
        hmse = float(np.mean((o_ho - pred_ho) ** 2))
        la, ue = res.x[0], res.x[1]
        a = 10.0 ** la; e = 1.0 / (1.0 + math.exp(-ue))
        refined.append(dict(success=bool(res.success), train_mse=float(res.fun),
                            holdout_mse=hmse, nit=int(res.nit),
                            a=a, e=e, i=float(res.x[2] % TWO_PI),
                            Omega=float(res.x[3] % TWO_PI),
                            omega=float(res.x[4] % TWO_PI),
                            M0=float(res.x[5] % TWO_PI),
                            q=a * (1.0 - e)))
    refined.sort(key=lambda r: r['holdout_mse'])
    return refined[0], dict(n_grid=len(scored), grid_best_train=scored[0][0],
                            train_n=cut, holdout_n=n - cut)


def fit_blind_cartesian(ts, obs):
    """Diagnostic/alternative fitter: Levenberg-Marquardt in Cartesian
    state-vector space (r0, v0 at t_ref). This is the standard orbit-
    determination parameterization (cf. sparse_orbit_fitter.py's
    multi-start least_squares); the cost landscape is near-quadratic,
    unlike the narrow (a,e) valley in Keplerian elements."""
    from scipy.optimize import least_squares
    n = len(ts)
    cut = int(0.7 * n)
    t_tr, o_tr, t_ho, o_ho = ts[:cut], obs[:cut], ts[cut:], obs[cut:]

    def predict(x, tarr, t_ref=T_EPOCH_YR):
        el0 = cart_to_elements(x[:3], x[3:])
        if not (el0['a'] > 0 and 0.0 <= el0['e'] < 1.0):
            return np.full((len(tarr), 3), 1e6)
        nn = math.sqrt(MU_SUN / el0['a'] ** 3)
        out = np.empty((len(tarr), 3))
        for k, t in enumerate(tarr):
            el = dict(el0)
            el['M'] = (el0['M'] + nn * (t - t_ref)) % TWO_PI
            out[k] = elements_to_cart(el)[0]
        return out

    A = np.vstack([t_tr, np.ones(len(t_tr))]).T
    coef = np.array([np.linalg.lstsq(A, o_tr[:, j], rcond=None)[0]
                     for j in range(3)])
    x0 = np.concatenate([coef[:, 0] * T_EPOCH_YR + coef[:, 1], coef[:, 0]])
    sol = least_squares(lambda x: (predict(x, t_tr) - o_tr).ravel(), x0,
                        method='lm', max_nfev=300,
                        ftol=1e-15, xtol=1e-15, gtol=1e-15)
    el = cart_to_elements(sol.x[:3], sol.x[3:])
    hmse = float(np.mean((o_ho - predict(sol.x, t_ho)) ** 2))
    return dict(success=bool(sol.success), nfev=int(sol.nfev),
                train_cost=float(sol.cost), holdout_mse=hmse,
                a=float(el['a']), e=float(el['e']), q=float(el['q']),
                i_deg=math.degrees(el['i']),
                Om_deg=math.degrees(el['Omega']),
                om_deg=math.degrees(el['omega']))


def ang_err(a, b):
    return abs((a - b + math.pi) % TWO_PI - math.pi)


def run(seed):
    print(f"=== Ammonite blind test, noise seed {seed} ===", flush=True)
    t0 = time.time()
    ts, obs = make_observations(seed)   # writes sealed truth (fitter won't open)
    best, info = fit_blind(ts, obs)     # blind: only (ts, obs)
    cart = fit_blind_cartesian(ts, obs)  # diagnostic: standard LM fitter
    # scoring opens the sealed truth AFTER fitting
    truth = json.load(open(TRUTH_PATH))
    el_t = truth['elements']
    q_t = truth['q_au']; a_t = el_t['a']
    dq = abs(best['q'] - q_t) / q_t
    da = abs(best['a'] - a_t) / a_t
    de = abs(best['e'] - el_t['e'])
    di = math.degrees(ang_err(best['i'], el_t['i']))
    dOm = math.degrees(ang_err(best['Omega'], el_t['Omega']))
    dom = math.degrees(ang_err(best['omega'], el_t['omega']))
    passed = bool(best['success'] and dq < 0.01 and da < 0.01
                  and 0.0 <= best['e'] < 1.0 and best['a'] > 0)
    print(f"  truth: q={q_t:.4f} a={a_t:.3f} e={el_t['e']:.4f}", flush=True)
    print(f"  fit:   q={best['q']:.4f} a={best['a']:.3f} e={best['e']:.4f} "
          f"(nit={best['nit']}, success={best['success']})", flush=True)
    print(f"  |dq|/q={dq:.4%}  |da|/a={da:.4%}  de={de:.5f} "
          f"di={di:.3f}deg dOm={dOm:.3f}deg dom={dom:.3f}deg", flush=True)
    print(f"  holdout_mse={best['holdout_mse']:.3e} AU^2 "
          f"({math.sqrt(best['holdout_mse'])*206265/66:.2f} arcsec @66AU)", flush=True)
    passed = bool(best['success'] and dq < 0.01 and da < 0.01
                  and 0.0 <= best['e'] < 1.0 and best['a'] > 0)
    cdq = abs(cart['q'] - q_t) / q_t
    cda = abs(cart['a'] - a_t) / a_t
    cart_passed = bool(cart['success'] and cdq < 0.01 and cda < 0.01)
    print(f"  cartesian+LM (diagnostic): q={cart['q']:.4f} (|dq|/q={cdq:.4%}) "
          f"a={cart['a']:.3f} (|da|/a={cda:.4%}) e={cart['e']:.5f} "
          f"nfev={cart['nfev']} -> {'PASS' if cart_passed else 'FAIL'}", flush=True)
    print(f"  VERDICT (grid+Nelder-Mead): {'PASS' if passed else 'FAIL'} "
          f"({time.time()-t0:.0f}s)", flush=True)
    return dict(seed=seed, q_true=q_t, a_true=a_t, e_true=el_t['e'],
                q_fit=best['q'], a_fit=best['a'], e_fit=best['e'],
                i_fit_deg=math.degrees(best['i']), Om_fit_deg=math.degrees(best['Omega']),
                om_fit_deg=math.degrees(best['omega']),
                dq_rel=dq, da_rel=da, de_abs=de, di_deg=di, dOm_deg=dOm, dom_deg=dom,
                converged=best['success'], nit=best['nit'],
                holdout_mse=best['holdout_mse'], passed=passed, info=info,
                cart=dict(q=cart['q'], a=cart['a'], e=cart['e'],
                          dq_rel=cdq, da_rel=cda, converged=cart['success'],
                          nfev=cart['nfev'], holdout_mse=cart['holdout_mse'],
                          passed=cart_passed))


if __name__ == '__main__':
    print("planetary-perturbation check (two-body vs Sun+8 planets)...", flush=True)
    dmax = planetary_check()
    print(f"  max |pos_2body - pos_Nbody| over arc = {dmax:.3e} AU "
          f"(noise sigma = {SIGMA_AU:.3e} AU)", flush=True)
    print(f"  -> {'two-body truth adequate' if dmax < 0.01*SIGMA_AU else 'WARNING: use N-body truth'}",
          flush=True)
    results = [run(s) for s in SEEDS]
    allpass = all(r['passed'] for r in results)
    allcart = all(r['cart']['passed'] for r in results)
    print(f"\nOVERALL grid+Nelder-Mead: {'PASS' if allpass else 'FAIL'} "
          f"({sum(r['passed'] for r in results)}/{len(results)} seeds)", flush=True)
    print(f"OVERALL cartesian+LM (diagnostic): {'PASS' if allcart else 'FAIL'} "
          f"({sum(r['cart']['passed'] for r in results)}/{len(results)} seeds)", flush=True)
    json.dump(results, open(HERE + '/sealed_runs/ammonite_results.json', 'w'), indent=1)
