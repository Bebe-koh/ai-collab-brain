import numpy as np

tau, dt, t0 = 46.9, 10.0, 0.0
t = np.arange(-300, 300, dt)

def s_sig(t, gamma):
    dPhi = -12.0*np.pi*gamma*(np.tanh((t+dt-t0)/tau)-np.tanh((t-t0)/tau))
    return np.exp(1j*dPhi)

# (1) transient signal energy vs gamma (deviation from null s=1)
gs = np.linspace(0, 0.5, 101)
E = np.array([np.sum(np.abs(s_sig(t,g)-1.0)**2) for g in gs])
print("signal energy E(gamma)= sum|s-1|^2:")
for g in [0.0, 1/12, 0.15, 1/6, 0.25, 0.5]:
    print(f"  gamma={g:.4f}  E={np.sum(np.abs(s_sig(t,g)-1.0)**2):.3f}")
print("  E>0 for all gamma>0:", bool(np.all(E[1:]>1e-12)))

# (2) mean-subtracted template correlation: discriminability of gamma vs gamma+1/12
def mcorr(g1, g2):
    a = s_sig(t,g1)-1.0; b = s_sig(t,g2)-1.0
    return np.abs(np.sum(a*np.conj(b)))/np.sqrt(np.sum(np.abs(a)**2)*np.sum(np.abs(b)**2))
print("mean-subtracted corr(s_1/12, s_1/6) =", round(mcorr(1/12,1/6),4))
print("mean-subtracted corr(s_1/12, s_1/12) =", round(mcorr(1/12,1/12),4))
print("mean-subtracted corr(s_0.15, s_0.15+1/12) =", round(mcorr(0.15,0.15+1/12),4))

# (3) old vs new: effective detection amplitude
old = 2*np.abs(np.sin(12*np.pi*gs))
print("old amplitude at gamma=1/12:", round(2*abs(np.sin(12*np.pi/12)),6))
print("new signal energy at gamma=1/12:", round(np.sum(np.abs(s_sig(t,1/12)-1.0)**2),3))
np.savez("demo2.npz", gs=gs, E=E, old=old)
