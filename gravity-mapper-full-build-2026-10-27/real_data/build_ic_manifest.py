"""Build epoch-consistent tracer ICs by fitting Keplerian elements to the
early arc of the real Horizons data (first 2 years, 30-day cadence, exact).

Why: tracer_elements.json has phases off by tens of degrees at t=0
(Earth IC 1.75 AU from data), which doomed the rediscovery test. Fitting
to a short early arc gives elements ~ the true osculating elements at
t=0, so the 15-yr residual shows Jupiter's FULL differential effect --
the signal the blind fit must find.

Steps:
1. fit_orbit (sparse_orbit_fitter) per tracer on t in [0, 2] yr
2. elements_to_manifest_item -> manifest items (drop-in for rediscovery_test)
3. drift diagnostic: Jupiter-free sim vs data over 15 yr
4. control: sim WITH Jupiter+Saturn (truth) vs data -> residual floor;
   if floor << drift, the residual IS the giant-planet signal.
"""
import sys, os, math, csv, json
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')

from gravity_mapper.catalog.scenario_simulator import keplerian_body, step_verlet, DT, Body
from sparse_orbit_fitter import fit_orbit, elements_to_manifest_item

B = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data'
IDS = ['Earth', 'Mars', 'Ceres', 'Vesta']
MASSES = {'Earth': 3.003e-6, 'Mars': 3.213e-7, 'Ceres': 4.7e-10, 'Vesta': 1.3e-10}
TRUTH = {'Jupiter': (9.55e-4, 5.20, 0.0), 'Saturn': (2.86e-4, 9.58, 0.0)}
FIT_SPAN = 2.0  # years


def load_raw():
    obs = {}
    for r in csv.DictReader(open(B + '/horizons_tracers.csv')):
        obs.setdefault(r['object_id'], []).append(
            (float(r['time_years']), float(r['x_au']), float(r['y_au'])))
    for oid in obs:
        obs[oid].sort()
    return obs


def load_dt():
    obs = {}
    for r in csv.DictReader(open(B + '/horizons_tracers_dt.csv')):
        obs.setdefault(r['object_id'], []).append(
            (float(r['time_years']), float(r['x_au']), float(r['y_au'])))
    for oid in obs:
        obs[oid].sort()
    return obs


def build_bodies(items, extra=()):
    bodies = [keplerian_body({'object_id': 'sun', 'mass_solar': 1.0,
                              'orbital_radius_au': 0.0, 'phase_rad': 0.0})]
    for it in items:
        bodies.append(keplerian_body(it))
    for name, (m, r, ph) in extra:
        bodies.append(keplerian_body({'object_id': name, 'mass_solar': m,
                                      'orbital_radius_au': r, 'phase_rad': ph}))
    return bodies


def drift_rms(items, obs, extra=()):
    bodies = build_bodies(items, extra)
    state = {b.object_id: b for b in bodies}
    times = sorted(set(t for oid in IDS for t, _, _ in obs[oid]))
    t0, tmax = min(times), max(times)
    n_steps = int(round((tmax - t0) / DT))
    wanted = set(round(t, 10) for t in times)
    by_oid_t = {(oid, round(t, 10)): (x, y) for oid in IDS for t, x, y in obs[oid]}
    acc = {oid: [0.0, 0] for oid in IDS}
    for k in range(n_steps + 1):
        t = round(t0 + k * DT, 10)
        if t in wanted:
            for oid in IDS:
                b = state[oid]
                x, y = by_oid_t[(oid, t)]
                acc[oid][0] += (b.x - x) ** 2 + (b.y - y) ** 2
                acc[oid][1] += 1
        if k < n_steps:
            step_verlet(bodies)
    return {oid: math.sqrt(acc[oid][0] / acc[oid][1]) for oid in IDS}


def main():
    raw = load_raw()
    obs = load_dt()
    items = []
    print(f"Fitting Keplerian elements to first {FIT_SPAN} yr of data:", flush=True)
    for oid in IDS:
        arc = [(t, x, y) for t, x, y in raw[oid] if t <= FIT_SPAN]
        fit = fit_orbit(arc, t0=0.0, n_starts=12)
        print(f"  {oid:6s} a={fit['a_au']:.6f} e={fit['e']:.6f} "
              f"om={math.degrees(fit['omega_rad']):8.2f} "
              f"M0={math.degrees(fit['M0_rad']):8.2f} rms={fit['rms_au']:.2e} "
              f"n={fit['n_obs']}", flush=True)
        items.append(elements_to_manifest_item(oid, MASSES[oid], fit))
    json.dump(items, open(B + '/tracer_manifest_t0.json', 'w'), indent=1)
    print("wrote tracer_manifest_t0.json", flush=True)

    print("\nDrift diagnostic (Jupiter-free sim vs data, 15 yr):", flush=True)
    d = drift_rms(items, obs)
    for oid in IDS:
        print(f"  {oid:6s} RMS drift = {d[oid]:.3e} AU", flush=True)

    print("\nControl (sim WITH Jupiter+Saturn at truth, circular) vs data:", flush=True)
    d2 = drift_rms(items, obs, extra=[('Jupiter', TRUTH['Jupiter']),
                                      ('Saturn', TRUTH['Saturn'])])
    for oid in IDS:
        print(f"  {oid:6s} RMS drift = {d2[oid]:.3e} AU", flush=True)
    print("\nIf control << drift, the residual is the giant-planet signal.", flush=True)


if __name__ == '__main__':
    main()
