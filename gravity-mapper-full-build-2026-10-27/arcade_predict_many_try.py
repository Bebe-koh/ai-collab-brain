"""Scratch: stacked multi-tracer predict vs per-tracer predict loop."""
import os, sys, time, json
import numpy as np
from scipy.integrate import solve_ivp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rails_brain import PlanetRails, PLANET_MU, MU_SUN
from particle_brain import NBodyParticle, _physical

rails = PlanetRails.build(0.0, 27.0, dt_days=0.5, cache_path=os.path.join(HERE, 'sealed_runs/planet_rails.npz'))
p = NBodyParticle(rails)
a_vals = [1.0, 5.2, 30.0]
states = np.stack([np.array([a, 0, 0, 0, np.sqrt(MU_SUN/a), 0], float) for a in a_vals])
ts = np.linspace(5.0, 10.0, 21); t_ref = 5.0

def rhs_stack(t, y):
    K = len(a_vals); r = y.reshape(K, 6)[:, :3]; v = y.reshape(K, 6)[:, 3:]
    rj = rails.positions(t)
    rn = np.linalg.norm(r, axis=1)
    acc = -MU_SUN * r / rn[:, None]**3
    d = rj[None] - r[:, None]
    dn = np.linalg.norm(d, axis=2); rn_j = np.linalg.norm(rj, axis=1)
    acc = acc + np.sum(PLANET_MU[None, :, None]*(d/dn[:, :, None]**3 - rj[None]/rn_j[None, :, None]**3), axis=1)
    out = np.empty_like(y); out.reshape(K, 6)[:, :3] = v; out.reshape(K, 6)[:, 3:] = acc
    return out

t0=time.perf_counter()
sol = solve_ivp(rhs_stack, (t_ref, ts[-1]), states.ravel(), method='DOP853', t_eval=ts, rtol=p.rtol, atol=p.atol)
t_stack = time.perf_counter()-t0
stacked = sol.y.T.reshape(len(ts), len(a_vals), 6)[:, :, :3]
t0=time.perf_counter()
singles = np.stack([p.predict(s, ts, t_ref) for s in states], axis=1)
t_single = time.perf_counter()-t0
print('success', sol.success, 'stacked_s', t_stack, 'single_loop_s', t_single)
print('maxdiff_AU', float(np.max(np.abs(stacked-singles))))
print(json.dumps({'stacked_s': t_stack, 'single_s': t_single, 'maxdiff': float(np.max(np.abs(stacked-singles)))}))
