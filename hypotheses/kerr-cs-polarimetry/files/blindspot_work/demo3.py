import numpy as np

tau, t0 = 46.9, 0.0
def E_of_gamma(gamma, dt):
    t = np.arange(-300, 300, dt)
    dPhi = -12.0*np.pi*gamma*(np.tanh((t+dt-t0)/tau)-np.tanh((t-t0)/tau))
    s = np.exp(1j*dPhi)
    return np.sum(np.abs(s-1.0)**2)

print("signal energy at gamma=1/12 vs sampling:")
for dt in [1.0, 5.0, 10.0, 20.0, 50.0, 200.0]:
    print(f"  dt={dt:6.1f}s (dt/tau={dt/tau:.2f}): E={E_of_gamma(1/12, dt):.4f}")
print()
print("old step amplitude at gamma=1/12:", 2*abs(np.sin(12*np.pi/12)))
