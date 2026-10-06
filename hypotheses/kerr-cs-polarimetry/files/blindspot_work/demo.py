import numpy as np

tau = 46.9          # s, Sgr A* slip timescale
dt = 10.0           # s, sampling
t = np.arange(-200, 200, dt)
t0 = 0.0

def Phi(t, gamma):
    """Total differenced-channel phase excursion: -12*dchi(t), dchi_max=2*pi*gamma."""
    return -12.0*np.pi*gamma*(1.0+np.tanh((t-t0)/tau))

def s_template(t, gamma_t):
    """Differenced-domain signature: exp(i[Phi(t+dt)-Phi(t)])."""
    return np.exp(1j*(Phi(t+dt, gamma_t)-Phi(t, gamma_t)))

# (a) old step-amplitude statistic vs gamma
gammas = np.linspace(0, 0.5, 1201)
old_resp = np.abs(1.0-np.exp(-24j*np.pi*gammas))  # = 2|sin(12 pi gamma)|
zeros = gammas[np.where(old_resp < 1e-9)[0]]
print("old-statistic zeros near k/12:", np.round(zeros[:6], 4))

# (b) new statistic: normalized correlation of true signal at gamma_true
#     against template bank, evaluated at gamma_true = 1/12
def corr(g_true, g_t):
    s_true = s_template(t, g_true)
    s_t = s_template(t, g_t)
    return np.abs(np.sum(s_true*np.conj(s_t))) / np.sqrt(np.sum(np.abs(s_t)**2)*np.sum(np.abs(s_true)**2))

g_true = 1.0/12.0
bank = np.linspace(0, 0.25, 501)
resp = np.array([corr(g_true, gt) for gt in bank])
print("new-statistic response at gamma_true=1/12:")
for gt in [0.0, 1/12, 1/6, 0.15, 0.25]:
    print(f"  template gamma={gt:.4f} -> corr={corr(g_true, gt):.4f}")
print("  min over bank:", resp.min().round(4), " max:", resp.max().round(4))

# (c) ambiguity: corr between s_{1/12} and s_{1/6} (one extra winding)
print("corr(s_1/12, s_1/6) =", round(corr(1/12, 1/6), 4), " (1.0 would mean exact degeneracy)")

# (d) per-sample max phase step at gamma=1/12 (unwrapping check)
dphi = np.abs(Phi(t+dt, g_true)-Phi(t, g_true))
print("max |dPhi|/sample at gamma=1/12:", round(dphi.max(), 3), "rad (< pi => unwrappable)")

# save data for plot
np.savez("demo_data.npz", gammas=gammas, old_resp=old_resp, bank=bank, resp=resp,
         t=t, s_true_r=s_template(t,g_true).real, s_true_i=s_template(t,g_true).imag)
print("saved demo_data.npz")
