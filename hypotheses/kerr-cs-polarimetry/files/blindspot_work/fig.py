import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

tau, t0 = 46.9, 0.0
gs = np.linspace(0, 0.5, 1001)
old = 2*np.abs(np.sin(12*np.pi*gs))

def E_of_gamma(gamma, dt):
    t = np.arange(-300, 300, dt)
    dPhi = -12.0*np.pi*gamma*(np.tanh((t+dt-t0)/tau)-np.tanh((t-t0)/tau))
    return np.sum(np.abs(np.exp(1j*dPhi)-1.0)**2)
Enew = np.array([E_of_gamma(g, 10.0) for g in gs])

dt_grid = np.array([1,2,5,10,20,30,50,80,120,200.0])
E_dt = np.array([E_of_gamma(1/12, d) for d in dt_grid])

t = np.arange(-150, 150, 10.0)
dPhi = -12.0*np.pi*(1/12)*(np.tanh((t+10-t0)/tau)-np.tanh((t-t0)/tau))
s = np.exp(1j*dPhi)

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
ax[0].plot(gs, old, lw=2)
for k in range(0, 7):
    ax[0].axvline(k/12, color="r", ls="--", alpha=0.5, lw=1)
ax[0].set_xlabel(r"$\gamma$"); ax[0].set_ylabel(r"$2|\sin(12\pi\gamma)|$")
ax[0].set_title("Old: step amplitude (exact zeros at k/12)")
ax[0].set_ylim(-0.05, 2.15)

ax[1].plot(gs, Enew, lw=2, color="g")
for k in range(0, 7):
    ax[1].axvline(k/12, color="r", ls="--", alpha=0.5, lw=1)
ax[1].set_xlabel(r"$\gamma$"); ax[1].set_ylabel(r"$E=\sum|s-1|^2$")
ax[1].set_title("New: transient signal energy (no zeros)")

ax[2].plot(dt_grid, E_dt, "o-", lw=2, color="purple")
ax[2].axvline(tau, color="k", ls=":", label=r"$\tau=46.9\,$s")
ax[2].set_xscale("log"); ax[2].set_xlabel("sampling dt (s)")
ax[2].set_ylabel(r"$E$ at $\gamma=1/12$")
ax[2].set_title("Blind spot returns when ramp unresolved")
ax[2].legend(fontsize=9)
fig.suptitle("Kerr/CS: curing the k/12 blind spot (Sgr A*, tau=46.9 s, differenced channel)")
fig.tight_layout()
fig.savefig("blindspot_fig.png", dpi=110)
print("wrote blindspot_fig.png")
