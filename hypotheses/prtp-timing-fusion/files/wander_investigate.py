"""Deep characterization of the B1937+21 x B1855+09 correlated wander.

Part A: 14-epoch common data (correlation drivers, detrending, timescale,
        chance probability via surrogates).
Part B: full-resolution binned series (167/112 bins) - wander shape.
Part C: backend/observatory dependence from par files.
"""
import json, os, re
import numpy as np

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
NS = 1e3
z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
R = z["R"] * NS
mjd = z["mjd_c"]
order = [str(x) for x in z["order"]]
Rm = R - R.mean(0)
t_yr = (mjd - mjd[0]) / 365.25
res = {"mjd_c": [float(x) for x in mjd]}

# ---------------- A1: leave-one-epoch-out correlation ----------------
i37, i55 = 2, 3
r_full = float(np.corrcoef(Rm[:, i37], Rm[:, i55])[0, 1])
loo = []
for e in range(len(mjd)):
    m = np.ones(len(mjd), bool); m[e] = False
    r = float(np.corrcoef(Rm[m, i37], Rm[m, i55])[0, 1])
    loo.append({"drop_mjd": float(mjd[e]), "r": r, "delta": r - r_full})
res["A1_r_full"] = r_full
res["A1_loo"] = loo
print("A1: r_full =", round(r_full, 4))
for l in loo:
    print("   drop %6.0f -> r=%+.3f (delta %+.3f)" % (l["drop_mjd"], l["r"], l["delta"]))

# ---------------- A2: correlation after removing common mode ----------------
_red = json.load(open(os.path.join(HID, "aldm_real_results.json")))
sig2 = np.array(_red["red_epoch_sigma_ns"]) ** 2
V = z["V"] * NS ** 2
Ce = V + sig2[None, :]
c = np.array([np.sum(Rm[e] / Ce[e]) / np.sum(1 / Ce[e]) for e in range(len(mjd))])
Rc = Rm - c[:, None]                      # subtract common mode
r_nocm = float(np.corrcoef(Rc[:, i37], Rc[:, i55])[0, 1])
res["A2_r_after_commonmode_removal"] = r_nocm
print("A2: r after common-mode removal =", round(r_nocm, 4))

# ---------------- A3: detrend (cubic) then correlate ----------------
def detrend(y, t, deg=3):
    X = np.vander(t, deg + 1)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta, beta
d37, b37 = detrend(Rm[:, i37], t_yr)
d55, b55 = detrend(Rm[:, i55], t_yr)
r_det = float(np.corrcoef(d37, d55)[0, 1])
res["A3_r_after_cubic_detrend"] = r_det
res["A3_cubic_coef_B1937_ns"] = [float(x) for x in b37]
res["A3_cubic_coef_B1855_ns"] = [float(x) for x in b55]
res["A3_resid_rms_ns"] = [float(np.std(d37)), float(np.std(d55))]
print("A3: r after cubic detrend =", round(r_det, 4),
      "| resid rms ns:", [round(float(np.std(d37)), 1), round(float(np.std(d55)), 1)])

# ---------------- A4: timescale via lag-1 autocorrelation ----------------
def lag1(y):
    return float(np.corrcoef(y[:-1], y[1:])[0, 1])
res["A4_lag1_autocorr"] = {order[i]: lag1(Rm[:, i]) for i in range(4)}
print("A4: lag-1 autocorr:", {order[i]: round(lag1(Rm[:, i]), 3) for i in range(4)})

# ---------------- A5: chance probability via phase-randomized surrogates -----
# Preserve each series' power spectrum (hence redness), destroy cross-phase.
rng = np.random.default_rng(7)
n_sim = 20000
y1, y2 = Rm[:, i37] - Rm[:, i37].mean(), Rm[:, i55] - Rm[:, i55].mean()
F1 = np.fft.rfft(y1)
cnt = 0
for _ in range(n_sim):
    ph = rng.uniform(0, 2 * np.pi, len(F1))
    ph[0] = 0
    if len(y1) % 2 == 0:
        ph[-1] = 0
    s2 = np.fft.irfft(np.abs(F1) * np.exp(1j * ph), n=len(y1))
    r = np.corrcoef(y1, s2)[0, 1]
    if abs(r) >= abs(r_full):
        cnt += 1
res["A5_surrogate_p_ge_r"] = cnt / n_sim
res["A5_n_sim"] = n_sim
print("A5: P(|r| >= %.3f) under phase-randomized surrogates = %.4f" % (r_full, cnt / n_sim))

# also: white-noise null for reference
t = abs(r_full) * np.sqrt(12) / np.sqrt(1 - r_full ** 2)
from scipy.stats import t as tdist
res["A5_white_noise_p"] = float(2 * tdist.sf(t, 12))
print("    white-noise p (naive, wrong for red data) =", "%.2e" % res["A5_white_noise_p"])

# ---------------- B: full-resolution binned series ----------------
B = {}
for key, name in [("binned_B1937", "B1937+21"), ("binned_B1855", "B1855+09"),
                  ("binned_J1909", "J1909-3744"), ("binned_J0437", "J0437-4715")]:
    a = z[key]
    idx = a[:, 0].astype(int)
    B[name] = {"mjd": z["centers"][idx], "res_us": a[:, 1], "err_us": a[:, 2]}
    r_us = a[:, 1]
    print("B: %s nbins=%d span %.0f-%.0f rms %.3f us  max|.| %.2f us" %
          (name, len(a), z["centers"][idx].min(), z["centers"][idx].max(),
           r_us.std(), np.abs(r_us).max()))
res["B_nbins"] = {k: len(v["mjd"]) for k, v in B.items()}

# B1: cross-correlate full-res series on overlapping bins (B1937 x B1855)
m37, m55 = B["B1937+21"]["mjd"], B["B1855+09"]["mjd"]
common = np.intersect1d(np.round(m37).astype(int), np.round(m55).astype(int))
i37m = np.searchsorted(np.round(m37).astype(int), common)
i55m = np.searchsorted(np.round(m55).astype(int), common)
s37 = B["B1937+21"]["res_us"][i37m]; s55 = B["B1855+09"]["res_us"][i55m]
s37 -= s37.mean(); s55 -= s55.mean()
r_fullres = float(np.corrcoef(s37, s55)[0, 1])
res["B1_n_overlap_bins"] = len(common)
res["B1_r_fullres"] = r_fullres
print("B1: overlap bins =", len(common), " r =", round(r_fullres, 4))

# B2: jump scan - largest adjacent-bin steps in each full-res series
for name in ["B1937+21", "B1855+09"]:
    s = B[name]["res_us"] * 1000  # ns
    st = np.abs(np.diff(s))
    j = np.argsort(st)[-5:][::-1]
    res["B2_top_jumps_" + name] = [
        {"mjd": float(B[name]["mjd"][k + 1]), "step_ns": float(np.diff(s)[k])}
        for k in j]
    print("B2 %s top steps (ns):" % name,
          [(round(float(B[name]['mjd'][k + 1])), round(float(np.diff(s)[k])))
           for k in j])

# B3: describe wander shape - bin the full series into ~1-yr chunks
for name in ["B1937+21", "B1855+09"]:
    mj = B[name]["mjd"]; s = B[name]["res_us"]
    edges = np.arange(mj.min(), mj.max() + 365, 365)
    means = [float(s[(mj >= e) & (mj < e + 365)].mean()) for e in edges[:-1]]
    res["B3_yearly_means_us_" + name] = means
print("B3 yearly means B1937 (us):", [round(x, 2) for x in res["B3_yearly_means_us_B1937+21"]])
print("B3 yearly means B1855 (us):", [round(x, 2) for x in res["B3_yearly_means_us_B1855+09"]])

# ---------------- C: backend/observatory from par files ----------------
nd = os.path.join(HID, "nanograv15yr/extracted/narrowband/noise")
back = {}
for p in order:
    lines = [l.strip() for l in open(os.path.join(nd, p + ".nb.pars.txt")) if l.strip()]
    bes = sorted(set(re.sub(r"^" + re.escape(p) + r"_", "",
                            re.sub(r"_(efac|equad|ecorr|log10_ecorr|log10_equad)$", "", l))
                     for l in lines))
    back[p] = bes
res["C_backends"] = back
for p in order:
    print("C: %s backends:" % p)
    for b in back[p]:
        print("    ", b)

with open(os.path.join(HID, "wander_investigation.json"), "w") as f:
    json.dump(res, f, indent=1)
print("saved wander_investigation.json")
