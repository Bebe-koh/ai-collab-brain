"""Rank the source of the ~350 ns common monopole in NANOGrav binned residuals.

Compares four time-domain signatures on the 14-epoch GLS common-mode series
plus one spatial (dipole) test for ephemeris error on the full 56-vector:

  M0      null: common mode = formal noise only
  M_clock epoch-uncorrelated common variance (clock-jump-like), 1 param
  M_uldm  coherent common sinusoid (ULDM Earth-term-like), 3 params
  M_smooth smooth common red process, gamma=4.5 fixed, free ampl, 1 param
  E0/E1   spatial: per-epoch monopole vs monopole + annual dipole
          (ephemeris-error signature), on 14x4 residual vector

Ranking by BIC. Archival-data analysis; not a detection claim.
"""
import json
import os
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
YR_S = 365.25 * 86400.0

# ---------------------------------------------------------------- data
z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
R_us = z["R"]            # (14, 4) microseconds
V_us2 = z["V"]           # (14, 4) white variance, us^2
sig2_us2 = z["sig2"]     # (4,) red variance, us^2
mjd = z["mjd_c"]
order = [str(x) for x in z["order"]]
NS = 1e3                 # us -> ns
R = R_us * NS
V = V_us2 * NS**2
# NOTE: npz sig2 is NOT the chain-median red variance used in prior notes
# (it is far too small: 6 ns vs 301 ns for B1937). Use the published
# chain-median red variances from aldm_real_results.json instead.
_red = json.load(open(os.path.join(HID, "aldm_real_results.json")))
sig2 = (np.array(_red["red_epoch_sigma_ns"]) ** 2)
n_ep, n_psr = R.shape
t_yr = (mjd - mjd[0]) / 365.25
T_span = float(t_yr[-1] - t_yr[0])

# per-pulsar mean subtraction (same preprocessing as prior notes)
Rm = R - R.mean(axis=0, keepdims=True)
Ce = V + sig2[None, :]   # (14,4) ns^2, diagonal white+red per epoch

# GLS common-mode series per epoch
c, cvar = [], []
for e in range(n_ep):
    w = 1.0 / Ce[e]
    c.append(float(np.sum(w * Rm[e]) / np.sum(w)))
    cvar.append(float(1.0 / np.sum(w)))
# For the time-domain fits use the PUBLISHED vetted series (continuity with
# prior notes); the plain per-epoch GLS above reproduces its formal errors
# exactly and the series to <80 ns (estimator regularization differences).
_pub = _red["white_plus_red"]
y = np.array(_pub["common_mode_ns"], dtype=float)
y = y - y.mean()
sig = np.array(_pub["common_mode_std_ns"], dtype=float)
# cross-check my plain GLS recomputation against the published series
# (diagnostic only; fits below use the published vetted series)
_ref = np.array(_pub["common_mode_ns"])
_refe = np.array(_pub["common_mode_std_ns"])
_c = np.array(c); _cv = np.array(cvar)
print("series max abs dev vs published ns:",
      round(float(np.abs((_c - _c.mean()) - (_ref - _ref.mean())).max()), 2))
print("formal err max abs dev vs published ns:",
      round(float(np.abs(np.sqrt(_cv) - _refe).max()), 2))
w0 = (1.0 / (V[0] + sig2)); w0 /= w0.sum()
print("GLS weights e0:", dict(zip(order, np.round(w0, 3))))
print("common-mode ns:", np.round(y, 1))
print("formal err  ns:", np.round(sig, 1))
print("T_span yr:", round(T_span, 2))

# ------------------------------------------------- pulsar unit vectors
# standard timing positions (arcsec-level; plenty for a dipole template)
RAD = np.pi / 180.0
coords = {  # RA hms, Dec dms
    "J0437-4715": ((4, 37, 15.885), (-47, 15, 9.11)),
    "J1909-3744": ((19, 9, 47.437), (-37, 44, 14.31)),
    "B1937+21":   ((19, 39, 38.561), (21, 34, 59.33)),
    "B1855+09":   ((18, 57, 36.393), (9, 43, 17.21)),
}
def nhat(name):
    (h, m, s), (d, am, asec) = coords[name]
    ra = (h + m / 60 + s / 3600) * 15.0 * RAD
    sg = 1.0 if d >= 0 else -1.0
    dec = sg * (abs(d) + am / 60 + asec / 3600) * RAD
    return np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra),
                     np.sin(dec)])
N = np.array([nhat(p) for p in order])   # (4,3)

# validate coordinates against the HD matrix quoted in spatial_template_note
# (their convention: Earth-term ORF normalized to 1 at zero lag, i.e. 2x ORF)
def hd_orf(cos_zeta):
    x = np.clip((1.0 - cos_zeta) / 2.0, 1e-12, 1.0)
    return 2.0 * (1.5 * x * np.log(x) - 0.25 * x + 0.5)
G = N @ N.T
HD = hd_orf(np.clip(G, -1, 1))
np.fill_diagonal(HD, 1.0)
HD_ref = np.array([[1.00, -0.30, 0.17, 0.13],
                   [-0.30, 1.00, -0.16, 0.03],
                   [0.17, -0.16, 1.00, 0.77],
                   [0.13, 0.03, 0.77, 1.00]])
print("HD matrix max abs dev vs note:", round(float(np.abs(HD - HD_ref).max()), 3))

# ------------------------------------------------- likelihood machinery
def lnlike_diag(y, mu, var):
    return float(-0.5 * np.sum((y - mu) ** 2 / var + np.log(2 * np.pi * var)))

def lnlike_full(y, mu, C):
    L = np.linalg.cholesky(C)
    d = y - mu
    a = np.linalg.solve(L, d)
    return float(-0.5 * (a @ a + 2 * np.sum(np.log(np.diag(L)))
                         + len(y) * np.log(2 * np.pi)))

def bic(lnL, k, n):
    return float(k * np.log(n) - 2 * lnL)

res = {"n_epochs": n_ep, "T_span_yr": T_span,
       "hd_validation_maxdev": float(np.abs(HD - HD_ref).max()),
       "models": {}}

# M0: null
lnL0 = lnlike_diag(y, np.zeros_like(y), sig ** 2)
res["models"]["M0_null"] = {"k": 0, "lnL": lnL0, "bic": bic(lnL0, 0, n_ep),
                            "dlnL_vs_null": 0.0}

# M_clock: epoch-uncorrelated common variance
def nll_clock(lg_s2):
    return -lnlike_diag(y, np.zeros_like(y), sig ** 2 + 10 ** lg_s2)
r = minimize_scalar(nll_clock, bounds=(-2, 8), method="bounded",
                    options={"xatol": 1e-6})
s2c = 10 ** r.x
lnLc = -r.fun
res["models"]["M_clock"] = {"k": 1, "lnL": lnLc, "bic": bic(lnLc, 1, n_ep),
                            "dlnL_vs_null": lnLc - lnL0,
                            "sigma_c_ns": float(np.sqrt(s2c))}

# M_smooth: common red process, gamma=4.5 fixed, free amplitude
Delta = 30.0 / 365.25  # bin width, yr
def red_cov(A, gamma=4.5):
    c0 = A ** 2 / (12 * np.pi ** 2)          # yr^3 at f=1/yr
    fmin, fmax = 1.0 / T_span, 20.0 / Delta
    C = np.zeros((n_ep, n_ep))
    for i in range(n_ep):
        for j in range(i, n_ep):
            tau = abs(t_yr[i] - t_yr[j])
            def ig(f):
                x = np.pi * f * Delta
                w = (np.sin(x) / x) ** 2 if x > 1e-9 else 1.0
                return c0 * f ** (-gamma) * w * np.cos(2 * np.pi * f * tau)
            v, _ = quad(ig, fmin, fmax, limit=200)
            C[i, j] = C[j, i] = v * (YR_S * 1e9) ** 2   # yr^2 -> ns^2
    return C
def nll_smooth(lgA):
    return -lnlike_full(y, np.zeros_like(y), np.diag(sig ** 2)
                        + red_cov(10 ** lgA))
r2 = minimize_scalar(nll_smooth, bounds=(-20, -8), method="bounded",
                     options={"xatol": 1e-4})
lnLs = -r2.fun
res["models"]["M_smooth"] = {"k": 1, "lnL": lnLs, "bic": bic(lnLs, 1, n_ep),
                             "dlnL_vs_null": lnLs - lnL0,
                             "log10_A": float(r2.x), "gamma": 4.5}

# M_uldm: coherent common sinusoid; grid over frequency
periods_d = np.logspace(np.log10(60), np.log10(20 * 365.25), 80)
peaks = []   # (lnL, period_d, amplitude_ns) for the periodogram
for P in periods_d:
    f = 1.0 / (P / 365.25)                     # yr^-1
    X = np.column_stack([np.sin(2 * np.pi * f * t_yr),
                         np.cos(2 * np.pi * f * t_yr)])
    W = np.diag(1.0 / sig ** 2)
    beta, *_ = np.linalg.lstsq(W @ X, W @ y, rcond=None)
    mu = X @ beta
    ll = lnlike_diag(y, mu, sig ** 2)
    peaks.append((ll, float(P), float(np.hypot(beta[0], beta[1]))))
peaks.sort(key=lambda t: -t[0])
lnLu, Pstar, Ast = peaks[0]
# refit phase at best period
f = 1.0 / (Pstar / 365.25)
X = np.column_stack([np.sin(2 * np.pi * f * t_yr),
                     np.cos(2 * np.pi * f * t_yr)])
W = np.diag(1.0 / sig ** 2)
beta, *_ = np.linalg.lstsq(W @ X, W @ y, rcond=None)
ph = float(np.arctan2(beta[1], beta[0]))
res["models"]["M_uldm"] = {"k": 3, "lnL": lnLu, "bic": bic(lnLu, 3, n_ep),
                           "dlnL_vs_null": lnLu - lnL0,
                           "best_period_days": float(Pstar),
                           "best_period_yr": float(Pstar / 365.25),
                           "amplitude_ns": Ast, "phase_rad": ph,
                           "top3_peaks": [{"period_days": p, "lnL": ll,
                                           "amplitude_ns": a}
                                          for ll, p, a in peaks[:3]],
                           "note": "freq selected on 80-pt grid: effective dof > 3, true BIC penalty larger; best period exceeds data span (not a periodicity detection)"}

# ------------------------------------------------- spatial ephemeris test
# E0: per-epoch monopole only. E1: + annual dipole n_a.(s sin + d cos)
Wv = 1.0 / np.sqrt(Ce)          # whitening weights (14,4)
Yw = (Rm * Wv).reshape(-1)      # 56-vector, whitened
def design(with_dipole):
    X = np.zeros((n_ep * n_psr, n_ep))          # per-epoch monopole indicator
    for e in range(n_ep):
        for a in range(n_psr):
            X[e * n_psr + a, e] = Wv[e, a]
    if with_dipole:
        ph = 2 * np.pi * t_yr                   # 1/yr
        extra = []
        for comp in range(3):
            ds = np.zeros(n_ep * n_psr); dc = np.zeros(n_ep * n_psr)
            for e in range(n_ep):
                for a in range(n_psr):
                    ds[e * n_psr + a] = Wv[e, a] * N[a, comp] * np.sin(ph[e])
                    dc[e * n_psr + a] = Wv[e, a] * N[a, comp] * np.cos(ph[e])
            extra += [ds, dc]
        X = np.column_stack([X] + extra)
    return X
for tag, dd in (("E0_monopole", False), ("E1_monopole_annual_dipole", True)):
    X = design(dd)
    beta, *_ = np.linalg.lstsq(X, Yw, rcond=None)
    resid = Yw - X @ beta
    n56 = len(Yw)
    lnL = float(-0.5 * (resid @ resid + n56 * np.log(2 * np.pi)))
    k = X.shape[1]
    res["models"][tag] = {"k": k, "lnL": lnL, "bic": bic(lnL, k, n56)}
    if dd:
        dvec_s = beta[-6:-3]; dvec_c = beta[-3:]
        amp = float(np.hypot(np.linalg.norm(dvec_s), np.linalg.norm(dvec_c)))
        res["models"][tag]["dipole_amp_ns"] = amp
        res["models"][tag]["dipole_sin_ns"] = [float(x) for x in dvec_s]
        res["models"][tag]["dipole_cos_ns"] = [float(x) for x in dvec_c]
        # ecliptic latitude of the fitted dipole: an Earth-orbit error
        # must lie IN the ecliptic plane (lat ~ 0)
        ecl = np.array([np.cos(66.5607 * np.pi / 180) * np.cos(0.0),
                        np.cos(66.5607 * np.pi / 180) * np.sin(0.0),
                        np.sin(66.5607 * np.pi / 180)])  # J2000 ecl pole
        def elat(v):
            v = np.asarray(v, float)
            return float(90.0 - np.arccos(np.clip(v @ ecl / np.linalg.norm(v),
                                                 -1, 1)) * 180 / np.pi)
        res["models"][tag]["dipole_sin_ecllat_deg"] = elat(dvec_s)
        res["models"][tag]["dipole_cos_ecllat_deg"] = elat(dvec_c)

# drop-one-pulsar jackknife on the spatial test: does the annual-dipole
# advantage survive without each pulsar? (cf. the HD collapse without B1937)
jk = {}
for drop in range(n_psr):
    keep = [a for a in range(n_psr) if a != drop]
    idx = np.array([e * n_psr + a for e in range(n_ep) for a in keep])
    Yk = Yw[idx]
    out = {}
    for tag, dd in (("E0", False), ("E1", True)):
        X = design(dd)[idx]          # row-slice full design to kept pulsars
        beta, *_ = np.linalg.lstsq(X, Yk, rcond=None)
        rsd = Yk - X @ beta
        n56 = len(Yk)
        out[tag] = float(-0.5 * (rsd @ rsd + n56 * np.log(2 * np.pi)))
    jk[order[drop]] = {"dlnL_E1_vs_E0": out["E1"] - out["E0"],
                       "n": len(Yk)}
res["spatial_jackknife"] = jk

# ------------------------------------------------- ranking
for fam, n in ((["M0_null", "M_clock", "M_uldm", "M_smooth"], n_ep),
               (["E0_monopole", "E1_monopole_annual_dipole"], n_ep * n_psr)):
    ms = [(m, res["models"][m]["bic"]) for m in fam]
    ms.sort(key=lambda t: t[1])
    for m, b in ms:
        res["models"][m]["dBIC_vs_best_in_family"] = float(b - ms[0][1])
    res["ranking_" + ("time_domain" if n == n_ep else "spatial")] = \
        [m for m, _ in ms]

with open(os.path.join(HID, "monopole_ranking_results.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps({m: {k: round(v, 2) if isinstance(v, float) else v
                      for k, v in d.items() if k in
                      ("k", "lnL", "bic", "dlnL_vs_null",
                       "dBIC_vs_best_in_family", "sigma_c_ns",
                       "best_period_days", "amplitude_ns",
                       "dipole_amp_ns", "log10_A")}
                  for m, d in res["models"].items()}, indent=1))
print("ranking_time:", res["ranking_time_domain"])
print("ranking_spatial:", res["ranking_spatial"])
