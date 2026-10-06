"""Stage 3: long-baseline per-bin GLS monopole series M(t) + ULDM scan.

Builds M(t) over all 194 thirty-day bins (161 with >=2 pulsars, ~15.9 yr),
then:
  (a) clock-like epoch-uncorrelated common variance fit (cf. M_clock);
  (b) ULDM coherent-sinusoid grid scan, periods 60 d - 20 yr, diagonal errs;
  (c) red-marginalized sinusoid scan (null = diag + propagated per-pulsar
      red covariance, free overall red scale; alt adds sinusoid at each f).
Key question: does the 14-epoch 6.7-yr ULDM "peak" (P > span) resolve into
anything with a 15.9-yr baseline?
"""
import json
import os
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

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
    P[p] = {"idx": idx, "res": res, "wv": wv, "rv": float(rv),
            "gamma": ch["gamma"], "log10_A": ch["log10_A"], "Tspan": Tspan}

# per-bin GLS monopole (need >=2 pulsars for a "common" mode)
MB, SB, TB, WB = [], [], [], []
for bi in range(len(centers)):
    ys, vs, ws = [], [], []
    wdict = {}
    for a, p in enumerate(order):
        m = P[p]["idx"] == bi
        if m.any():
            j = int(np.nonzero(m)[0][0])
            ys.append(P[p]["res"][j])
            vs.append(P[p]["wv"][j] + P[p]["rv"])
            wdict[a] = P[p]["wv"][j] + P[p]["rv"]
    if len(ys) >= 2:
        ys = np.array(ys); vs = np.array(vs)
        w = 1.0 / vs
        MB.append(float(np.sum(w * ys) / np.sum(w)))
        SB.append(float(1.0 / np.sum(w)))
        TB.append(float(t_yr_all[bi]))
        WB.append(wdict)
MB = np.array(MB); SB = np.array(SB); TB = np.array(TB)
sig = np.sqrt(SB)
y = MB - MB.mean()
n = len(y)
print(f"monopole series: {n} bins, span {TB.max()-TB.min():.2f} yr", flush=True)
print("series rms ns:", round(float(np.sqrt((y**2).mean())), 1),
      "median formal err ns:", round(float(np.median(sig)), 1), flush=True)

res = {"n_bins": n, "span_yr": float(TB.max() - TB.min()),
       "t_yr": [float(t) for t in TB],
       "M_ns": [float(v) for v in y],
       "M_err_ns": [float(v) for v in sig]}

def lnlike_diag(yy, mu, var):
    return float(-0.5 * np.sum((yy - mu) ** 2 / var + np.log(2 * np.pi * var)))

# (a) clock-like
lnL0 = lnlike_diag(y, np.zeros_like(y), sig ** 2)
def nll_c(lg):
    return -lnlike_diag(y, np.zeros_like(y), sig ** 2 + 10 ** lg)
r = minimize_scalar(nll_c, bounds=(-2, 8), method="bounded")
lnLc = -r.fun
res["clock"] = {"sigma_c_ns": float(np.sqrt(10 ** r.x)), "lnL": lnLc,
                "dlnL_vs_null": lnLc - lnL0,
                "bic": float(np.log(n) - 2 * lnLc)}
print("clock: sigma_c=%.1f ns dlnL=%.1f" % (np.sqrt(10 ** r.x), lnLc - lnL0),
      flush=True)

# (b) ULDM grid scan, diagonal errors
periods_d = np.logspace(np.log10(60), np.log10(20 * 365.25), 120)
peaks = []
for Pd in periods_d:
    f = 1.0 / (Pd / 365.25)
    X = np.column_stack([np.sin(2 * np.pi * f * TB),
                         np.cos(2 * np.pi * f * TB)])
    W = np.diag(1.0 / sig ** 2)
    beta, *_ = np.linalg.lstsq(W @ X, W @ y, rcond=None)
    ll = lnlike_diag(y, X @ beta, sig ** 2)
    peaks.append((ll, float(Pd), float(np.hypot(beta[0], beta[1]))))
peaks.sort(key=lambda t: -t[0])
res["uldm_diag"] = {
    "best": {"period_days": peaks[0][1], "period_yr": peaks[0][1] / 365.25,
             "amplitude_ns": peaks[0][2], "lnL": peaks[0][0],
             "dlnL_vs_null": peaks[0][0] - lnL0},
    "top5": [{"period_days": p, "period_yr": p / 365.25, "lnL": ll,
              "amplitude_ns": a} for ll, p, a in peaks[:5]]}
b = res["uldm_diag"]["best"]
print("uldm diag: best P=%.0f d (%.2f yr) A=%.0f ns dlnL=%.1f"
      % (b["period_days"], b["period_yr"], b["amplitude_ns"], b["dlnL_vs_null"]),
      flush=True)

# (c) red-marginalized scan: C = diag(sig^2) + s2r * C_red_template
# per-pulsar red autocorrelation on a lag grid, propagated via GLS weights
Delta = 30.0 / 365.25
lag_grid = np.linspace(0, 16, 240)
cred = {}
for p in order:
    ch = chains[p]
    A = 10.0 ** ch["log10_A"]; gam = ch["gamma"]
    c0 = A ** 2 / (12 * np.pi ** 2)
    fmin, fmax = 1.0 / P[p]["Tspan"], 20.0 / Delta
    vals = []
    for tau in lag_grid:
        def ig(f, tau=tau):
            x = np.pi * f * Delta
            w = (np.sin(x) / x) ** 2 if x > 1e-9 else 1.0
            return c0 * f ** (-gam) * w * np.cos(2 * np.pi * f * tau)
        v, _ = quad(ig, fmin, fmax, limit=120)
        vals.append(v * (YR_S * 1e9) ** 2)
    cred[p] = np.array(vals)
    print(f"  cred {p} done", flush=True)

def Cred_M(i, j):
    # Cov(M_i, M_j) from per-pulsar red, via bin weights
    if abs(TB[i] - TB[j]) > 16:
        return 0.0
    tot = 0.0
    wi, wj = WB[i], WB[j]
    common = set(wi) & set(wj)
    for a in common:
        tau = abs(TB[i] - TB[j])
        cv = float(np.interp(tau, lag_grid, cred[order[a]]))
        # weight product normalized as in GLS: w_a/sum(w)
        si = sum(1.0 / wi[k] for k in wi); sj = sum(1.0 / wj[k] for k in wj)
        tot += (1.0 / wi[a] / si) * (1.0 / wj[a] / sj) * cv
    return tot

print("building C_red template (%d x %d)..." % (n, n), flush=True)
CR = np.zeros((n, n))
for i in range(n):
    for j in range(i, n):
        CR[i, j] = CR[j, i] = Cred_M(i, j)
    if i % 40 == 0:
        print(f"  row {i}/{n}", flush=True)
np.fill_diagonal(CR, np.maximum(np.diag(CR), 0))
# CR is PSD in theory (sampled PSD autocorr) but numerically indefinite:
# the true matrix is nearly singular (min eig ~1e-12 of max), so clip
# negative eigenvalues to a small floor -> nearest-PSD projection.
wlam, Q = np.linalg.eigh(CR)
floor = 1e-6 * wlam.max()
wlam = np.maximum(wlam, floor)
CR = (Q * wlam) @ Q.T
print("CR clipped: min eig now %.3g (was %.3g)" % (wlam.min(), 0.0), flush=True)

def lnlike_full(yy, mu, C):
    L = np.linalg.cholesky(C)
    d = yy - mu
    a = np.linalg.solve(L, d)
    return float(-0.5 * (a @ a + 2 * np.sum(np.log(np.diag(L)))
                         + len(yy) * np.log(2 * np.pi)))

D = np.diag(sig ** 2)
def nll_rednull(lgs2):
    return -lnlike_full(y, np.zeros_like(y), D + 10 ** lgs2 * CR)
rr = minimize_scalar(nll_rednull, bounds=(-4, 4), method="bounded",
                     options={"xatol": 1e-3})
s2r = 10 ** rr.x
lnLr = -rr.fun
Cnull = D + s2r * CR
res["red_null"] = {"red_scale": float(s2r), "lnL": lnLr,
                   "dlnL_vs_diag_null": lnLr - lnL0}
print("red null: scale=%.2f dlnL_vs_diag=%.1f" % (s2r, lnLr - lnL0), flush=True)

# sinusoid scan on top of red null (red scale fixed)
def scan_f(Pd, C):
    f = 1.0 / (Pd / 365.25)
    X = np.column_stack([np.sin(2 * np.pi * f * TB),
                         np.cos(2 * np.pi * f * TB)])
    L = np.linalg.cholesky(C)
    Xa = np.linalg.solve(L, X); ya = np.linalg.solve(L, y)
    beta, *_ = np.linalg.lstsq(Xa, ya, rcond=None)
    rsd = ya - Xa @ beta
    return float(-0.5 * (rsd @ rsd + 2 * np.sum(np.log(np.diag(L)))
                         + n * np.log(2 * np.pi))), beta

peaks2 = []
for Pd in periods_d:
    ll, beta = scan_f(Pd, Cnull)
    peaks2.append((ll, float(Pd), float(np.hypot(beta[0], beta[1]))))
peaks2.sort(key=lambda t: -t[0])
res["uldm_redmarg"] = {
    "best": {"period_days": peaks2[0][1], "period_yr": peaks2[0][1] / 365.25,
             "amplitude_ns": peaks2[0][2], "lnL": peaks2[0][0],
             "dlnL_vs_red_null": peaks2[0][0] - lnLr},
    "top5": [{"period_days": p, "period_yr": p / 365.25, "lnL": ll,
              "amplitude_ns": a} for ll, p, a in peaks2[:5]]}
b2 = res["uldm_redmarg"]["best"]
print("uldm redmarg: best P=%.0f d (%.2f yr) A=%.0f ns dlnL=%.1f"
      % (b2["period_days"], b2["period_yr"], b2["amplitude_ns"],
         b2["dlnL_vs_red_null"]), flush=True)

with open(os.path.join(HID, "wide_array_stage3.json"), "w") as f:
    json.dump(res, f, indent=1)
print("STAGE3 DONE", flush=True)
