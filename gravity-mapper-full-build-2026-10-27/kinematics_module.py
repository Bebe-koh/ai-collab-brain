"""Kinematics observation module for the gravity mapper.

Extends the pipeline beyond sky positions (x, y) to handle:
- proper motions (vx, vy): angular velocity on the sky
- radial velocities (vz): line-of-sight velocity (requires 3D)

Each observable type has a predict() that maps simulated state to the
expected observation, and the combined score weights by inverse variance.

The "combined answer": fit with positions only, fit with positions+kinematics,
compare. Agreement -> confidence. Disagreement -> bad data or wrong model.
"""
import math

# G in AU^3 / (M_sun * yr^2)
G = 4.0 * math.pi * math.pi


def predict_position(body):
    """(x, y) from simulated body."""
    return (body.x, body.y)


def predict_proper_motion(body):
    """(vx, vy) from simulated body. In 2D, proper motion IS velocity."""
    return (body.vx, body.vy)


def predict_radial_velocity(body):
    """vz from simulated body. Requires 3D state (z, vz).

    Our 2D bodies don't have z/vz. Returns None if unavailable —
    the scorer skips RV terms for 2D simulations.
    """
    if hasattr(body, 'vz'):
        return (body.vz,)
    return None


def score_observations(rows, manifest, candidates, build_system_fn, score_fn):
    """Score candidates against mixed observation types.

    rows: list of dicts with keys:
        object_id, time_years, kind ('pos'|'pm'|'rv'),
        v1, v2 (optional), sigma1, sigma2 (optional)
    Returns total chi-squared (inverse-variance weighted).
    """
    from collections import defaultdict
    system = build_system_fn(manifest, candidates)
    # group rows by time
    by_time = defaultdict(list)
    for r in rows:
        by_time[r['time_years']].append(r)
    max_time = max(by_time)
    # need DT from the simulator
    from gravity_mapper.catalog.scenario_simulator import DT
    steps = int(round(max_time / DT))
    total_chi2 = 0.0
    count = 0
    for step in range(steps + 1):
        t = round(step * DT, 10)
        if t not in by_time:
            continue
        state = {b.object_id: b for b in system}
        for r in by_time[t]:
            body = state[r['object_id']]
            kind = r.get('kind', 'pos')
            if kind == 'pos':
                px, py = predict_position(body)
                s1 = r.get('sigma1', 1e-5)
                s2 = r.get('sigma2', 1e-5)
                total_chi2 += ((r['v1'] - px) / s1) ** 2
                total_chi2 += ((r['v2'] - py) / s2) ** 2
                count += 2
            elif kind == 'pm':
                vx, vy = predict_proper_motion(body)
                s1 = r.get('sigma1', 1e-6)
                s2 = r.get('sigma2', 1e-6)
                total_chi2 += ((r['v1'] - vx) / s1) ** 2
                total_chi2 += ((r['v2'] - vy) / s2) ** 2
                count += 2
            elif kind == 'rv':
                pred = predict_radial_velocity(body)
                if pred is None:
                    continue
                s1 = r.get('sigma1', 1e-6)
                total_chi2 += ((r['v1'] - pred[0]) / s1) ** 2
                count += 1
        # step simulation
        if step < steps:
            from gravity_mapper.catalog.scenario_simulator import step_verlet
            step_verlet(system)
    return total_chi2 / max(count, 1)


def rows_from_positions(pos_rows):
    """Convert legacy position rows to kinematics format."""
    out = []
    for r in pos_rows:
        out.append({
            'object_id': r['object_id'],
            'time_years': r['time_years'],
            'kind': 'pos',
            'v1': r['x_au'], 'v2': r['y_au'],
            'sigma1': 1e-5, 'sigma2': 1e-5,
        })
    return out


def proper_motions_from_positions(pos_rows, dt_years=0.1):
    """Derive 'observed' proper motions via finite difference.

    NOTE: These are NOT independent of the positions — same information.
    Useful for testing the machinery, not for real constraint. Real PMs
    come from independent fits (e.g., Gaia 5-parameter solution).
    """
    from collections import defaultdict
    by_oid = defaultdict(list)
    for r in pos_rows:
        by_oid[r['object_id']].append(r)
    out = []
    for oid, rs in by_oid.items():
        rs.sort(key=lambda r: r['time_years'])
        for i in range(len(rs) - 1):
            r0, r1 = rs[i], rs[i + 1]
            dt = r1['time_years'] - r0['time_years']
            if dt < dt_years / 2:
                continue
            vx = (r1['x_au'] - r0['x_au']) / dt
            vy = (r1['y_au'] - r0['y_au']) / dt
            # sigma scales as position sigma / dt
            sig = 1e-5 / dt * 1.5  # ~1.5x for finite-difference noise
            out.append({
                'object_id': oid,
                'time_years': round((r0['time_years'] + r1['time_years']) / 2, 10),
                'kind': 'pm',
                'v1': vx, 'v2': vy,
                'sigma1': sig, 'sigma2': sig,
            })
    return out
