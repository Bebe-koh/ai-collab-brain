"""Leakage diagnostics for the 7.9-yr monopole oscillation.

Q: is the 7.9-yr wave in M(t) a genuinely common signal, or leaked
per-pulsar red noise (B1937/B1855 wander? J1909's own red noise)?
Checks:
 1. per-pulsar sinusoid scan at 7.9 yr on each pulsar's full series
 2. monopole rebuilt without B1937/B1855 -> does the wave survive?
 3. phase/amplitude of the 7.9-yr fit per pulsar
 4. correlation of per-bin B1937+B1855 GLS weight with wave phase
"""
import json
import os
import numpy as np

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
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
    P[p] = {"t": t_yr_all[idx], "res": res,
            "var": wv + rv}

F_STAR = 1.0 / 7.905988188027475  # yr^-1, from stage 3

def fit_sin(t, y, var, f):
    X = np.column_stack([np.sin(2 * np.pi * f * t),
                         np.cos(2 * np.pi * f * t),
                         np.ones_like(t)])
    W = np.diag(1.0 / var)
    beta, resd, *_ = np.linalg.lstsq(W @ X, W @ y, rcond=None)
    mu = X @ beta
    ll = float(-0.5 * np.sum((y - mu) ** 2 / var + np.log(2 * np.pi * var)))
    ll0m = float(-0.5 * np.sum((y - y.mean()) ** 2 / var
                               + np.log(2 * np.pi * var)))
    A = float(np.hypot(beta[0], beta[1]))
    ph = float(np.arctan2(beta[1], beta[0]))  # y = A sin(2pift+ph)
    return {"A_ns": A, "phase_rad": ph, "dlnL_vs_const": ll - ll0m,
            "n": len(y)}

print("=== per-pulsar 7.9-yr sinusoid fit (diag white+red) ===", flush=True)
for p in order:
    d = P[p]
    r = fit_sin(d["t"], d["res"], d["var"], F_STAR)
    print("%-10s A=%7.1f ns  phase=%6.2f rad  dlnL=%7.1f  n=%d"
          % (p, r["A_ns"], r["phase_rad"], r["dlnL_vs_const"], r["n"]),
          flush=True)

# rebuild from P with index arrays
PN = {}
for p, bk in zip(order, bkeys):
    b = z[bk]
    PN[p] = {"idx": b[:, 0].astype(int)}

def mono(keep, min_psr=2):
    MB, SB, TB = [], [], []
    for bi in range(len(centers)):
        ys, vs = [], []
        for p in keep:
            j = np.nonzero(PN[p]["idx"] == bi)[0]
            if len(j):
                jj = j[0]
                # locate in P[p] arrays (same order as binned)
                ys.append(P[p]["res"][jj]); vs.append(P[p]["var"][jj])
        if len(ys) >= min_psr:
            ys = np.array(ys); vs = np.array(vs)
            w = 1.0 / vs
            MB.append(float(np.sum(w * ys) / np.sum(w)))
            SB.append(float(1.0 / np.sum(w))); TB.append(float(t_yr_all[bi]))
    MB = np.array(MB); SB = np.array(SB); TB = np.array(TB)
    return MB - MB.mean(), np.sqrt(SB), TB

print("=== monopole variants: 7.9-yr fit ===", flush=True)
for label, keep in [("no B1937/B1855 (J0437+J1909)",
                     ["J0437-4715", "J1909-3744"]),
                    ("J1909 only", ["J1909-3744"]),
                    ("no B1937 (J0437+J1909+B1855)",
                     ["J0437-4715", "J1909-3744", "B1855+09"]),
                    ("no B1855 (J0437+J1909+B1937)",
                     ["J0437-4715", "J1909-3744", "B1937+21"])]:
    y, sig, t = mono(keep, min_psr=1 if len(keep) == 1 else 2)
    r = fit_sin(t, y, sig ** 2, F_STAR)
    print("%-32s A=%7.1f ns dlnL=%7.1f n=%d span=%.1fyr"
          % (label, r["A_ns"], r["dlnL_vs_const"], r["n"], t.max() - t.min()),
          flush=True)

# weight-leakage check: per-bin B1937+B1855 weight vs wave phase
yM, sigM, tM = mono(order, min_psr=2)
wfrac = []
for bi, t in enumerate(tM):
    # find original bin index
    bidx = int(np.argmin(abs(t_yr_all - t)))
    tot = 0.0; bb = 0.0
    for a, p in enumerate(order):
        j = np.nonzero(PN[p]["idx"] == bidx)[0]
        if len(j):
            w = 1.0 / P[p]["var"][j[0]]
            tot += w
            if a in (2, 3):
                bb += w
    wfrac.append(bb / tot if tot else 0)
wfrac = np.array(wfrac)
wave = np.sin(2 * np.pi * F_STAR * tM)
print("corr(B1937+B1855 weight frac, 7.9yr wave) = %.3f" % np.corrcoef(wfrac, wave)[0, 1],
      flush=True)
print("corr(B1937+B1855 weight frac, |M(t)|) = %.3f" % np.corrcoef(wfrac, np.abs(yM))[0, 1],
      flush=True)
print("mean B1937+B1855 weight frac: %.2f" % wfrac.mean(), flush=True)
