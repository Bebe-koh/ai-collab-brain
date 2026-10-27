"""Injection-recovery mapper: draw the sensitivity map.

Systematically inject synthetic hidden bodies into data, run the pipeline
blind, and measure the recovery fraction over a (mass, semi-major axis) grid.

Output: a map showing where the pipeline CAN and CANNOT detect bodies.
This is what makes a null result meaningful: "we would have seen a
5-Earth-mass object at 500 AU, but not at 1000 AU."

Usage:
    python3 injection_recovery.py --masses 1e-7,1e-6,1e-5 --radii 5,10,20
"""
import sys, os, math, json, csv, argparse, itertools
import numpy as np

sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')


def inject_and_recover(base_manifest, base_rows, inj_mass, inj_radius,
                       inj_phase=0.0, label="inj", seed=42):
    """Inject a synthetic body, run J4 blind, check recovery.

    Returns dict with verdict, recovered params, and whether the injected
    body was found (mass within 50%, radius within 20%, or verdict correct
    for null).
    """
    from gravity_mapper.catalog.scenario_simulator import (
        build_system_from_manifest, step_verlet, DT, Body, G)
    from gravity_mapper.catalog.catalog_two_body_recovery import (
        Candidate, visible_bodies)
    # lazy import to avoid circularity
    from j4_blind_pipeline_v2 import run_pipeline_v2

    # Build the "true" system: base manifest + injected body
    # We simulate forward to generate synthetic observations
    from gravity_mapper.catalog.scenario_simulator import keplerian_body
    inj_item = {
        'object_id': 'injected',
        'mass_solar': inj_mass,
        'orbital_radius_au': inj_radius,
        'phase_rad': inj_phase,
        'eccentricity': 0.0,
    }
    # Get base bodies
    bodies = visible_bodies(base_manifest)
    inj_body = keplerian_body(inj_item)
    system = bodies + [inj_body]

    # Simulate and collect tracer positions at observation times
    obs_times = sorted(set(r['time_years'] for r in base_rows))
    max_t = max(obs_times)
    steps = int(round(max_t / DT))
    # map time -> index for tracers
    tracer_ids = [b.object_id for b in bodies if b.object_id != 'sun']
    synth_rows = []
    for step in range(steps + 1):
        t = round(step * DT, 10)
        if t in obs_times:
            state = {b.object_id: b for b in system}
            for oid in tracer_ids:
                b = state[oid]
                # add small noise (1e-5 AU ~ 1500 km)
                rng = np.random.default_rng(seed + step)
                synth_rows.append({
                    'object_id': oid,
                    'time_years': t,
                    'x_au': b.x + rng.normal(0, 1e-5),
                    'y_au': b.y + rng.normal(0, 1e-5),
                })
        if step < steps:
            step_verlet(system)

    # Split train/holdout
    times = sorted(set(r['time_years'] for r in synth_rows))
    cut = times[int(len(times) * 0.7)]
    train = [r for r in synth_rows if r['time_years'] <= cut]
    holdout = [r for r in synth_rows if r['time_years'] > cut]

    # Run blind (pipeline does NOT know about injected body)
    result = run_pipeline_v2(train, base_manifest, holdout, label)

    # Assess recovery
    recovered = False
    if inj_mass > 0 and result['verdict'] == 'TWO_BODY':
        rm, rr = result['b2'][0], result['b2'][1]
        # also check b1 (might have found it as primary)
        r1m, r1r = result['b1'][0], result['b1'][1]
        for m, r in [(rm, rr), (r1m, r1r)]:
            if abs(m - inj_mass) / inj_mass < 0.5 and abs(r - inj_radius) / inj_radius < 0.2:
                recovered = True
                break
    elif inj_mass == 0 and result['verdict'] == 'ONE_BODY':
        recovered = True  # correct null

    return {
        'inj_mass': inj_mass, 'inj_radius': inj_radius,
        'verdict': result['verdict'],
        'rec_b1': result['b1'][:2], 'rec_b2': result['b2'][:2],
        'recovered': recovered,
    }


def sensitivity_map(base_manifest, base_rows, masses, radii, out_path):
    """Run injection-recovery over grid. Save CSV + summary."""
    results = []
    total = len(masses) * len(radii)
    done = 0
    for m, r in itertools.product(masses, radii):
        done += 1
        print(f"[{done}/{total}] m={m:.1e} r={r:.1f}...", flush=True)
        try:
            res = inject_and_recover(base_manifest, base_rows, m, r,
                                     label=f"inj-{done}")
            results.append(res)
            status = "FOUND" if res['recovered'] else "missed"
            print(f"  -> {res['verdict']} {status}", flush=True)
        except Exception as e:
            print(f"  -> ERROR: {e}", flush=True)
            results.append({'inj_mass': m, 'inj_radius': r,
                            'verdict': 'ERROR', 'recovered': False})
    # Save
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['inj_mass', 'inj_radius', 'verdict',
                                          'rec_b1', 'rec_b2', 'recovered'])
        w.writeheader()
        for r in results:
            row = dict(r)
            row['rec_b1'] = str(row.get('rec_b1', ''))
            row['rec_b2'] = str(row.get('rec_b2', ''))
            w.writerow(row)
    # Summary
    n_found = sum(1 for r in results if r['recovered'])
    print(f"\nRecovered {n_found}/{len(results)}", flush=True)
    print(f"Saved to {out_path}", flush=True)
    return results


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--masses', default='1e-7,1e-6,1e-5',
                    help='comma-separated masses (M_sun)')
    ap.add_argument('--radii', default='5,10,20',
                    help='comma-separated radii (AU)')
    ap.add_argument('--out', default='sensitivity_map.csv')
    args = ap.parse_args()
    masses = [float(x) for x in args.masses.split(',')]
    radii = [float(x) for x in args.radii.split(',')]
    print("Injection-recovery mapper: needs base manifest/rows.", flush=True)
    print("Run via: python3 -c \"from injection_recovery import sensitivity_map; ...\"",
          flush=True)
