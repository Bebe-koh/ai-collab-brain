"""Is the 7.9-yr wave a COMMON signal? Two decisive tests.

Test 1: joint fit, common phase vs per-pulsar phases, at f=1/7.906 yr.
  A common (Earth-term) wave MUST have one phase for all pulsars.
Test 2: J1909 alone with full red-noise covariance (chain spectrum):
  does the sinusoid survive once red temporal correlations are modeled?
"""
import json
import os
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
YR_S = 365.25 * 86400.0
NS = 1e3
import sys
sys.path.insert(0, HID)
from nanograv_gls_red import red_variance_us2

z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
centers = z["centers"]
t_yr_all = (centers - centers[0]) / 365.25
g = json.load(open(os.path.join(HID, "nanograv_gls_results.json")))
chains = g["red_noise_chains"]
order = ["J0437-4715", "J1909-3744", "B1937+21", "B1855+09"]
bkeys = ["binned_J0437", "binned_J1909", "binned_B1937", "binned_B1855"]
F = 1.0 / 7.905988188027475

P = {}
for p, bk in zip(order, bkeys):
    b = z[bk]
    idx = b[:, 0].astype(int)
    res = b[:, 1] * NS
    wv = b[:, 2] * NS ** 2
    res = res - res.mean()
    Tspan = max(float((centers[idx].max() - centers[idx].min()) / 365.25), 1.0)
    ch = chains[p]
    rv = red_variance_us2(ch["log10_A"], ch["gamma"], Tspan, 30.0) * NS ** 2
    P[p] = {"t": t_yr_all[idx], "y": res, "v": wv + rv,
            "gamma": ch["gamma"], "log10_A": ch["log10_A"], "Tspan": Tspan}

def design(t, f, phase):
    return np.column_stack([np.sin(2 * np.pi * f * t + phase),
                            np.cos(2 * np.pi * f * t + phase)])

def fit_common_phase():
    # params: [A_a >=0 x4 (log), phi]; y_a = A_a * sin(2pift+phi)
    def nll(th):
        A = np.exp(th[:4]); phi = th[4]
        ll = 0.0
        for a, p in enumerate(order):
            d = P[p]
            mu = A[a] * np.sin(2 * np.pi * F * d["t"] + phi)
            ll += float(-0.5 * np.sum((d["y"] - mu) ** 2 / d["v"]
                                      + np.log(2 * np.pi * d["v"])))
        return -ll
    best = (1e300, None)
    for phi0 in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        r = minimize(nll, [5, 5, 5, 5, phi0], method="Nelder-Mead",
                     options={"maxiter": 2000, "xatol": 1e-4, "fatol": 1e-4})
        if r.fun < best[0]:
            best = (r.fun, r.x)
    return best

def fit_indep_phase():
    # params: per pulsar [logA_a, phi_a]
    def nll(th):
        ll = 0.0
        for a, p in enumerate(order):
            A = np.exp(th[2 * a]); phi = th[2 * a + 1]
            d = P[p]
            mu = A * np.sin(2 * np.pi * F * d["t"] + phi)
            ll += float(-0.5 * np.sum((d["y"] - mu) ** 2 / d["v"]
                                      + np.log(2 * np.pi * d["v"])))
        return -ll
    best = (1e300, None)
    for _ in range(4):
        x0 = list(np.random.RandomState(_).uniform(-2, 8, 8))
        r = minimize(nll, x0, method="Nelder-Mead",
                     options={"maxiter": 3000, "xatol": 1e-4, "fatol": 1e-4})
        if r.fun < best[0]:
            best = (r.fun, r.x)
    return best

def fit_null():
    ll = 0.0
    for p in order:
        d = P[p]
        ll += float(-0.5 * np.sum(d["y"] ** 2 / d["v"]
                                  + np.log(2 * np.pi * d["v"])))
    return -ll

nll_c, thc = fit_common_phase()
nll_i, thi = fit_indep_phase()
nll_0 = fit_null()
Ac = np.exp(thc[:4]); phic = thc[4] % (2 * np.pi)
Ai = np.exp(thi[0::2]); phii = thi[1::2] % (2 * np.pi)
print("common-phase: A=%s phi=%.2f nll=%.1f" % (np.round(Ac, 1), phic, nll_c),
      flush=True)
print("indep-phase : A=%s phi=%s nll=%.1f"
      % (np.round(Ai, 1), np.round(phii, 2), nll_i), flush=True)
print("dlnL(indep vs common) = %.1f  [4 extra params]" % (nll_c - nll_i),
      flush=True)
print("dlnL(common vs null)  = %.1f" % (nll_0 - nll_c), flush=True)

# Test 2: J1909 with red covariance. C = diag(white) + s2r*C_red(gamma=4.09)
d = P["J1909-3744"]
t = d["t"]; y = d["y"]
wv_only = None
# white-only diagonal from bins: reconstruct (v includes red diag; use wv)
b = z["binned_J1909"]
wv_j = b[:, 2] * NS ** 2
D = np.diag(wv_j)
Delta = 30.0 / 365.25
ch = chains["J1909-3744"]
A0 = 10.0 ** ch["log10_A"]; gam = ch["gamma"]
c0 = A0 ** 2 / (12 * np.pi ** 2)
fmin, fmax = 1.0 / d["Tspan"], 20.0 / Delta
lags = np.abs(t[:, None] - t[None, :])
# vectorized via interpolation on precomputed autocorr
lg = np.linspace(0, 16, 300)
vals = []
for tau in lg:
    def ig(f, tau=tau):
        x = np.pi * f * Delta
        w = (np.sin(x) / x) ** 2 if x > 1e-9 else 1.0
        return c0 * f ** (-gam) * w * np.cos(2 * np.pi * f * tau)
    v, _ = quad(ig, fmin, fmax, limit=120)
    vals.append(v * (YR_S * 1e9) ** 2)
CR = np.interp(lags, lg, np.array(vals))
wlam, Q = np.linalg.eigh(CR)
CR = (Q * np.maximum(wlam, 1e-6 * wlam.max())) @ Q.T

def lnlike_full(mu, C):
    L = np.linalg.cholesky(C)
    dd = y - mu
    a = np.linalg.solve(L, dd)
    n = len(y)
    return float(-0.5 * (a @ a + 2 * np.sum(np.log(np.diag(L)))
                         + n * np.log(2 * np.pi)))

# null: red with free scale
def nll_rn(lgs2):
    return -lnlike_full(np.zeros_like(y), D + 10 ** lgs2 * CR)
from scipy.optimize import minimize_scalar
rr = minimize_scalar(nll_rn, bounds=(-3, 5), method="bounded")
s2r = 10 ** rr.x
ll_rn = -rr.fun
# alt: red (fixed scale) + sinusoid at F
X = np.column_stack([np.sin(2 * np.pi * F * t), np.cos(2 * np.pi * F * t),
                     np.ones_like(t)])
C = D + s2r * CR
L = np.linalg.cholesky(C)
Xa = np.linalg.solve(L, X); ya = np.linalg.solve(L, y)
beta, *_ = np.linalg.lstsq(Xa, ya, rcond=None)
ll_rs = lnlike_full(X @ beta, C)
print("J1909 red-null: scale=%.1f nll=%.1f" % (s2r, -ll_rn), flush=True)
print("J1909 red+7.9yr sinusoid: A=%.1f ns dlnL_vs_rednull=%.1f"
      % (np.hypot(beta[0], beta[1]), ll_rs - ll_rn), flush=True)
print("DONE", flush=True)
