"""Wide-array (4 pulsars x full time span) spatial variance-component analysis.

Extends the 14-common-epoch spatial work to ALL binned data:
161 bins with >=2 pulsars (vs 14 before), ~15.9 yr span (vs 4.8 yr).

Stage 1: global variance-component fit per bin:
    C_b = diag(white+red)_b + Am^2 * 11' + Ad^2 * (n n') + Ah^2 * Gamma_HD
  over (Am, Ad, Ah >= 0). Nested comparisons + jackknives.
Stage 2: time-chunked (Am, Ah) fits -> stability of HD component.
Stage 3: per-bin GLS monopole series M(t); clock-like vs ULDM-sinusoid
  scan (60 d - 20 yr) with diagonal + propagated red-noise covariance.

Conventions match the prior notes: npz V field used as white variance
(same convention as the published series; see note), red variances from
NANOGrav chain medians via red_variance_us2. Archival-data analysis;
never a detection claim.
"""
import json
import os
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize, differential_evolution

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
EXT = os.path.join(HID, "nanograv15yr", "extracted")
YR_S = 365.25 * 86400.0
NS = 1e3  # us -> ns

import sys
sys.path.insert(0, HID)
from nanograv_gls_red import red_variance_us2

# ------------------------------------------------------------ data
z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
centers = z["centers"]                      # 194 bin centers, MJD
t_yr_all = (centers - centers[0]) / 365.25
g = json.load(open(os.path.join(HID, "nanograv_gls_results.json")))
chains = g["red_noise_chains"]
order = ["J0437-4715", "J1909-3744", "B1937+21", "B1855+09"]
bkeys = ["binned_J0437", "binned_J1909", "binned_B1937", "binned_B1855"]

# pulsar unit vectors (validated vs the note's HD matrix to 0.005)
RAD = np.pi / 180.0
_coords = {
    "J0437-4715": ((4, 37, 15.885), (-47, 15, 9.11)),
    "J1909-3744": ((19, 9, 47.437), (-37, 44, 14.31)),
    "B1937+21": ((19, 39, 38.561), (21, 34, 59.33)),
    "B1855+09": ((18, 57, 36.393), (9, 43, 17.21)),
}
def _nhat(name):
    (h, m, s), (dd, am, as_) = _coords[name]
    ra = (h + m / 60 + s / 3600) * 15.0 * RAD
    sg = 1.0 if dd >= 0 else -1.0
    dec = sg * (abs(dd) + am / 60 + as_ / 3600) * RAD
    return np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra),
                     np.sin(dec)])
NHAT = np.array([_nhat(p) for p in order])
def _hd(cos_z):
    x = np.clip((1.0 - cos_z) / 2.0, 1e-12, 1.0)
    return 2.0 * (1.5 * x * np.log(x) - 0.25 * x + 0.5)  # norm: 1 at 0 lag
_G = NHAT @ NHAT.T
HD_FULL = _hd(np.clip(_G, -1, 1)); np.fill_diagonal(HD_FULL, 1.0)
DIP_FULL = _G.copy(); np.fill_diagonal(DIP_FULL, 1.0)
MON_FULL = np.ones((4, 4))

# per-pulsar binned series: (bin_idx, res_ns, whitevar_ns2), mean-subtracted
P = {}
for p, bk in zip(order, bkeys):
    b = z[bk]
    idx = b[:, 0].astype(int)
    res = b[:, 1] * NS
    wv = b[:, 2] * NS ** 2          # convention B (matches published series)
    res = res - res.mean()
    Tspan = float((centers[idx].max() - centers[idx].min()) / 365.25)
    Tspan = max(Tspan, 1.0)
    ch = chains[p]
    rv_us2 = red_variance_us2(ch["log10_A"], ch["gamma"], Tspan, 30.0)
    rv = rv_us2 * NS ** 2
    P[p] = {"idx": idx, "res": res, "wv": wv, "rv": float(rv),
            "Tspan": Tspan, "gamma": ch["gamma"], "log10_A": ch["log10_A"]}
    print(f"{p}: nbins={len(idx)} Tspan={Tspan:.2f}yr redsig={np.sqrt(rv):.1f}ns "
          f"gamma={ch['gamma']:.2f}", flush=True)

# per-bin assembly: bins with >=2 pulsars
BINS = []
for bi in range(len(centers)):
    ps, ys, vs = [], [], []
    for a, p in enumerate(order):
        m = P[p]["idx"] == bi
        if m.any():
            j = int(np.nonzero(m)[0][0])
            ps.append(a); ys.append(P[p]["res"][j])
            vs.append(P[p]["wv"][j] + P[p]["rv"])
    if len(ps) >= 2:
        BINS.append({"bi": bi, "t": float(t_yr_all[bi]),
                     "ps": np.array(ps), "y": np.array(ys),
                     "wv": np.array(vs)})   # white only; s2 fitted per pulsar
print(f"bins>=2: {len(BINS)}", flush=True)
NSET = {2: 0, 3: 0, 4: 0}
for b in BINS:
    NSET[len(b["ps"])] += 1
print("per-bin pulsar-count histogram:", NSET, flush=True)

# ------------------------------------------------------------ Stage 1
# REVISED parameterization (v2): per-pulsar excess variances are FIT
# (the chain red amplitudes underpredict B1937/B1855 by ~6-12x; fixing
# them lets the mis-modeled variance masquerade as spatial signal).
#   C_b = diag(white_b) + diag(s2_a) + Am^2*11' + Ad^2*(n n') + Ah^2*Gamma
# Spatial components must earn their keep via OFF-DIAGONAL covariance.
def nll_var(theta, bins, comps=("m", "d", "h")):
    """theta = [log10(s2_a) x4, log10(A2_k) for k in comps]."""
    s2 = 10.0 ** np.asarray(theta[:4])
    A2 = {}
    for t, c in zip(theta[4:], comps):
        A2[c] = 10.0 ** t
    ll = 0.0
    for b in bins:
        ps = b["ps"]; n = len(ps)
        C = np.diag(b["wv"] + s2[ps])
        if "m" in A2:
            C = C + A2["m"] * MON_FULL[np.ix_(ps, ps)]
        if "d" in A2:
            C = C + A2["d"] * DIP_FULL[np.ix_(ps, ps)]
        if "h" in A2:
            C = C + A2["h"] * HD_FULL[np.ix_(ps, ps)]
        try:
            L = np.linalg.cholesky(C)
        except np.linalg.LinAlgError:
            return 1e12
        a = np.linalg.solve(L, b["y"])
        ll += float(a @ a + 2 * np.sum(np.log(np.diag(L)))
                    + n * np.log(2 * np.pi))
    return 0.5 * ll

def fit_var(bins, comps, nrestart=3):
    nb = [(-2, 10)] * 4 + [(-4, 10)] * len(comps)
    best = (1e300, None)
    for si in range(nrestart):
        r = differential_evolution(
            nll_var, bounds=nb, args=(bins, comps), seed=7 + si,
            maxiter=80, tol=1e-7, polish=True, workers=1)
        if r.fun < best[0]:
            best = (r.fun, r.x)
    nll, x = best
    S = {p: float(np.sqrt(10 ** x[a])) for a, p in enumerate(order)}
    A = {c: float(np.sqrt(10 ** xi)) for c, xi in zip(comps, x[4:])}
    return {"nll": float(nll), "S_ns": S, "A_ns": A,
            "x": [float(v) for v in x]}

results = {}
for comps in [("m", "d", "h"), ("m", "d"), ("m", "h"), ("m",), ()]:
    tag = "var_" + ("+".join(comps) if comps else "null")
    results[tag] = fit_var(BINS, comps)
    print(tag, "S:", {k: round(v, 1) for k, v in results[tag]["S_ns"].items()},
          "A:", {k: round(v, 1) for k, v in results[tag]["A_ns"].items()},
          "nll=%.1f" % results[tag]["nll"], flush=True)

# profile-likelihood intervals for the spatial amplitudes (re-opt s2 + others)
def profile_err(bins, comps, best_x, ci=0.5):
    out = {}
    base = nll_var(best_x, bins, comps)
    nsp = len(comps)
    for i, c in enumerate(comps):
        gi = 4 + i  # position in theta
        lo, hi = best_x[gi] - 3, best_x[gi] + 3
        xs = np.linspace(lo, hi, 41)
        prof = []
        for xv in xs:
            def f(rest):
                xx = list(best_x); xx[gi] = xv
                k = 0
                for j in range(4 + nsp):
                    if j != gi:
                        xx[j] = rest[k]; k += 1
                return nll_var(xx, bins, comps)
            x0 = [best_x[j] for j in range(4 + nsp) if j != gi]
            r = minimize(f, x0, method="Nelder-Mead",
                         options={"xatol": 1e-3, "fatol": 1e-3,
                                  "maxiter": 300})
            prof.append(r.fun)
        prof = np.array(prof)
        inside = xs[prof - base < ci]
        out[c] = {"A_best_ns": float(np.sqrt(10 ** best_x[gi])),
                  "A_lo_ns": float(np.sqrt(10 ** inside.min())) if len(inside) else 0.0,
                  "A_hi_ns": float(np.sqrt(10 ** inside.max())) if len(inside) else 0.0,
                  "at_lower_bound": bool(best_x[gi] < -3.99)}
    return out

full = results["var_m+d+h"]
results["profile_mdh"] = profile_err(BINS, ("m", "d", "h"), full["x"])
print("profile:", json.dumps(results["profile_mdh"], indent=1), flush=True)

# ------------------------------------------------------------ jackknives
# (global pulsar indexing is kept; just filter bins)
results["jackknife"] = {}
for drop in range(4):
    keep = [a for a in range(4) if a != drop]
    b2 = [b for b in BINS if all(p in keep for p in b["ps"])]
    r = fit_var(b2, ("m", "d", "h"))
    results["jackknife"]["drop_" + order[drop]] = {
        "nbins": len(b2),
        "S_ns": {k: round(v, 1) for k, v in r["S_ns"].items()},
        "A_ns": {k: round(v, 1) for k, v in r["A_ns"].items()},
        "nll": round(r["nll"], 1)}
    print("jk drop", order[drop], "S:", results["jackknife"]["drop_" + order[drop]]["S_ns"],
          "A:", results["jackknife"]["drop_" + order[drop]]["A_ns"], flush=True)
# drop B1937+B1855 pair
keep = [0, 1]
b2 = [b for b in BINS if all(p in keep for p in b["ps"])]
r = fit_var(b2, ("m", "d", "h"))
results["jackknife"]["drop_B1937+B1855"] = {
    "nbins": len(b2),
    "S_ns": {k: round(v, 1) for k, v in r["S_ns"].items()},
    "A_ns": {k: round(v, 1) for k, v in r["A_ns"].items()},
    "nll": round(r["nll"], 1)}
print("jk drop pair S:", results["jackknife"]["drop_B1937+B1855"]["S_ns"],
      "A:", results["jackknife"]["drop_B1937+B1855"]["A_ns"], flush=True)

# ------------------------------------------------------------ Stage 2: time chunks
t_all = np.array([b["t"] for b in BINS])
edges = np.quantile(t_all, [0, .2, .4, .6, .8, 1.0])
results["chunks"] = []
for ci in range(5):
    cb = [b for b in BINS if edges[ci] <= b["t"] <= edges[ci + 1]]
    r = fit_var(cb, ("m", "h"))
    results["chunks"].append({
        "t_range_yr": [round(float(edges[ci]), 2), round(float(edges[ci + 1]), 2)],
        "nbins": len(cb),
        "S_ns": {k: round(v, 1) for k, v in r["S_ns"].items()},
        "A_ns": {k: round(v, 1) for k, v in r["A_ns"].items()},
        "nll": round(r["nll"], 1)})
    print("chunk", ci, results["chunks"][-1], flush=True)

with open(os.path.join(HID, "wide_array_results.json"), "w") as f:
    json.dump(results, f, indent=1)
print("STAGE1-2 DONE", flush=True)
