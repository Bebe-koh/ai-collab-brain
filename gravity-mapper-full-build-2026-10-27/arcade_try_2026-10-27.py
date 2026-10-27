"""Scratch try of arcade tricks against the mapper, 2026-10-27.
NOT live code: reads the sealed rails cache, never writes project files.
Tests (all accuracy-checked, not just timed):
 A rails scalar vs array vs linear-interp lookup grid
 B single-tracer particle accel loop vs batched accel (shared rails/indirect once)
 C live sin/cos vs lookup table (nearest + linear interp) for a phase grid
 D fresh allocation vs reused buffer in the batched accel
Timing note: the eccentric v4 re-run is running concurrently, so times are
noisy; min-of-repeats is reported and accuracy is the primary verdict.
"""
import json, time, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rails_brain import PlanetRails, PLANET_MU, MU_SUN
from particle_brain import NBodyParticle

def mintime(fn, reps=5):
    best = 1e99
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t0)
    return best

out = {}
# --- load rails from sealed cache (no rebuild) ---
cache = os.path.join(HERE, 'sealed_runs', 'planet_rails.npz')
rails = PlanetRails.build(0.0, 27.0, dt_days=0.5, cache_path=cache)
out['rails_cache'] = cache
ts = np.linspace(0.5, 26.5, 500)
# A1 scalar loop
def scalar():
    return np.stack([rails.positions(float(t)) for t in ts])
# A2 array call
def array():
    return rails.positions(ts)
ref = array()
scal = scalar()
out['A_scalar_vs_array_maxdiff_AU'] = float(np.max(np.abs(scal - ref)))
out['A_scalar_time_s'] = mintime(scalar, 3)
out['A_array_time_s'] = mintime(array, 5)
# A3 linear-interp lookup on the rails' own 0.5-day grid
grid_t = rails._grid_t; grid_pos = rails._grid_pos  # (nt,8,3)
def lookup():
    res = np.empty((len(ts), 8, 3))
    for j in range(8):
        for c in range(3):
            res[:, j, c] = np.interp(ts, grid_t, grid_pos[:, j, c])
    return res
lk = lookup()
out['A_lookup_linear_maxdiff_AU'] = float(np.max(np.abs(lk - ref)))
out['A_lookup_time_s'] = mintime(lookup, 5)
out['A_lookup_vs_floors'] = 'lookup error vs 1e-7 AU fitter floor and 7.04e-5 AU ROM floor: see maxdiff'

# B batching: single-tracer _rhs loop vs vectorized batched accel
p = NBodyParticle(rails)
t_test = 10.0
K = 20
a_vals = np.linspace(1.0, 40.0, K)
states = np.stack([np.array([a, 0.0, 0.0, 0.0, np.sqrt(MU_SUN / a), 0.0]) for a in a_vals])
def single_loop():
    return np.stack([p._rhs(t_test, s)[3:] for s in states])
def batched():
    r = states[:, :3]
    rj = rails.positions(t_test)  # (8,3) once
    rn = np.linalg.norm(r, axis=1)
    a = -MU_SUN * r / rn[:, None] ** 3
    d = rj[None, :, :] - r[:, None, :]  # (K,8,3)
    dn = np.linalg.norm(d, axis=2)
    rn_j = np.linalg.norm(rj, axis=1)
    a = a + np.sum(PLANET_MU[None, :, None] * (d / dn[:, :, None] ** 3 - rj[None, :, :] / rn_j[None, :, None] ** 3), axis=1)
    return a
s_acc = single_loop(); b_acc = batched()
out['B_single_vs_batched_maxdiff_AU_per_yr2'] = float(np.max(np.abs(s_acc - b_acc)))
out['B_single_time_s'] = mintime(single_loop, 5)
out['B_batched_time_s'] = mintime(batched, 5)

# C sin/cos lookup
n_c = np.sqrt(MU_SUN / 5.0 ** 3)
phases = np.linspace(0, 2 * np.pi, 7200, endpoint=False)
ang = n_c * t_test + phases
def live():
    return np.cos(ang), np.sin(ang)
# table: 3600 entries over 0..2pi
tab_n = 3600
tab_ang = np.linspace(0, 2 * np.pi, tab_n, endpoint=False)
tab_c, tab_s = np.cos(tab_ang), np.sin(tab_ang)
idx = np.round(ang / (2 * np.pi) * tab_n).astype(int) % tab_n
def nearest():
    return tab_c[idx], tab_s[idx]
def linear():
    x = (ang % (2 * np.pi)) / (2 * np.pi) * tab_n
    i0 = np.floor(x).astype(int) % tab_n; i1 = (i0 + 1) % tab_n; fr = x - np.floor(x)
    return tab_c[i0] * (1 - fr) + tab_c[i1] * fr, tab_s[i0] * (1 - fr) + tab_s[i1] * fr
lc, ls = live(); nc_, ns_ = nearest(); lic, lis = linear()
out['C_nearest_cos_sin_maxerr'] = float(max(np.max(np.abs(nc_ - lc)), np.max(np.abs(ns_ - ls))))
out['C_linear_cos_sin_maxerr'] = float(max(np.max(np.abs(lic - lc)), np.max(np.abs(lis - ls))))
out['C_position_err_at_5AU_nearest_AU'] = float(out['C_nearest_cos_sin_maxerr'] * 5.0)
out['C_position_err_at_5AU_linear_AU'] = float(out['C_linear_cos_sin_maxerr'] * 5.0)
out['C_live_time_s'] = mintime(live, 5)
out['C_nearest_time_s'] = mintime(nearest, 5)
out['C_linear_time_s'] = mintime(linear, 5)

# D buffer reuse in batched accel
buf_d = np.empty((K, 8, 3)); buf_dn = np.empty((K, 8))
def batched_reuse():
    r = states[:, :3]
    rj = rails.positions(t_test)
    rn = np.linalg.norm(r, axis=1)
    a = -MU_SUN * r / rn[:, None] ** 3
    np.subtract(rj[None, :, :], r[:, None, :], out=buf_d)
    np.sum(buf_d * buf_d, axis=2, out=buf_dn)
    np.sqrt(buf_dn, out=buf_dn)
    rn_j = np.linalg.norm(rj, axis=1)
    a = a + np.sum(PLANET_MU[None, :, None] * (buf_d / buf_dn[:, :, None] ** 3 - rj[None, :, :] / rn_j[None, :, None] ** 3), axis=1)
    return a
out['D_batched_reuse_maxdiff_vs_batched'] = float(np.max(np.abs(batched_reuse() - b_acc)))
out['D_batched_reuse_time_s'] = mintime(batched_reuse, 5)

with open(os.path.join(HERE, 'arcade_try_results_2026-10-27.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
