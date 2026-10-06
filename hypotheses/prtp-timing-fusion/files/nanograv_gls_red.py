"""Red-noise extension for the NANOGrav real-data GLS check.

Loads binned residuals (nanograv_binned.npz), adds a red-noise-inclusive
covariance using the NANOGrav noise-chain power-law medians, and compares:
  (a) white-only GLS  (the toy's estimator, C = diag(white))
  (b) white+red GLS   (C = diag(white + red_var), red from chain A/gamma)
against the unweighted mean, with jackknife uncertainties.

Writes: nanograv_gls_results.json (merged), used by nanograv_gls_note.md
"""
import json
import os
import numpy as np
from scipy.integrate import quad

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
NOISE = os.path.expanduser(
    "~/workspace/prtp/hidden_files/nanograv15yr/extracted/narrowband/noise")

YR_S = 365.25 * 86400.0


def red_variance_us2(log10_A, gamma, T_span_yr, bin_days=30.0):
    """Red-noise variance (us^2) of bin means for power-law PSD.

    P(f) = A^2/(12 pi^2) (f/fyr)^-gamma  [yr^3], NANOGrav 15yr convention.
    Bin averaging applies a sinc^2(pi f Delta) window; mean subtraction
    removes f < ~1/T_span.
    """
    A = 10.0 ** log10_A
    fyr = 1.0
    Delta = bin_days / 365.25  # yr
    fmin = 1.0 / T_span_yr
    fmax = 20.0 / Delta
    c = A ** 2 / (12.0 * np.pi ** 2)  # yr^3 at f=fyr

    def integrand(f):
        x = np.pi * f * Delta
        w = (np.sin(x) / x) ** 2 if x > 1e-9 else 1.0
        return c * (f / fyr) ** (-gamma) * w

    val, _ = quad(integrand, fmin, fmax, limit=200)
    return val * (YR_S * 1e6) ** 2  # yr^3 -> us^2


def gls_weights(C):
    ones = np.ones(C.shape[0])
    w = np.linalg.solve(C, ones)
    return w / (ones @ w)


def variance_ratio(R, w_a, w_b):
    """var(w_a . R) / var(w_b . R); R = (n_epoch, n_psr) in us."""
    a = R @ w_a
    b = R @ w_b
    a -= a.mean(); b -= b.mean()
    return float(np.var(a) / np.var(b)), float(np.sqrt(np.var(a)) * 1e3), \
        float(np.sqrt(np.var(b)) * 1e3)


def jackknife_ratio(R, w_a, w_b):
    n = R.shape[0]
    rs = []
    for i in range(n):
        Ri = np.delete(R, i, axis=0)
        r, _, _ = variance_ratio(Ri, w_a, w_b)
        rs.append(r)
    rs = np.array(rs)
    return float(rs.mean()), float(rs.std())


def main():
    z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
    R, V, mjd_c = z["R"], z["V"], z["mjd_c"]
    sig2 = z["sig2"]
    order = [str(x) for x in z["order"]]
    n_epoch, n_psr = R.shape
    T_span_yr = float((mjd_c.max() - mjd_c.min()) / 365.25)
    print(f"epochs={n_epoch} pulsars={order} T_common={T_span_yr:.2f} yr",
          flush=True)

    # red noise medians from chains
    red = {}
    for psr in order:
        names = [l.strip() for l in open(f"{NOISE}/{psr}.nb.pars.txt")
                 if l.strip()]
        d = np.loadtxt(f"{NOISE}/{psr}.nb.chain_1.txt")
        med = dict(zip(names, np.median(d[:, :len(names)], axis=0)))
        red[psr] = (float(med[f"{psr}_red_noise_log10_A"]),
                    float(med[f"{psr}_red_noise_gamma"]))
    red_var = np.array([red_variance_us2(A, g, T_span_yr) for A, g in
                        [red[p] for p in order]])
    print("red sigma per epoch (ns):", np.round(np.sqrt(red_var) * 1e3, 1),
          flush=True)
    print("white sigma per epoch (ns):", np.round(np.sqrt(sig2) * 1e3, 1),
          flush=True)
    emp_var = np.var(R, axis=0)
    print("empirical bin variance RMS (ns):",
          np.round(np.sqrt(emp_var) * 1e3, 1), flush=True)

    C_white = np.diag(sig2)
    C_wr = np.diag(sig2 + red_var)
    w_white = gls_weights(C_white)
    w_wr = gls_weights(C_wr)
    w_mean = np.ones(n_psr) / n_psr

    r_white, rms_w, rms_m = variance_ratio(R, w_white, w_mean)
    r_wr, rms_wr, _ = variance_ratio(R, w_wr, w_mean)
    jk_white = jackknife_ratio(R, w_white, w_mean)
    jk_wr = jackknife_ratio(R, w_wr, w_mean)
    theo_white = float((w_white @ C_white @ w_white) /
                       (w_mean @ C_white @ w_mean))
    theo_wr = float((w_wr @ C_wr @ w_wr) / (w_mean @ C_wr @ w_mean))
    # high-pass (epoch differences): white-noise-regime probe
    dR = np.diff(R, axis=0)
    r_hp_white, _, _ = variance_ratio(dR, w_white, w_mean)
    r_hp_wr, _, _ = variance_ratio(dR, w_wr, w_mean)
    # cross-pulsar correlation of epoch residuals
    corr = np.corrcoef(R.T)

    print(f"white-only GLS weights: {np.round(w_white, 4)}", flush=True)
    print(f"white+red GLS weights:  {np.round(w_wr, 4)}", flush=True)
    print(f"ratio white-only GLS/mean: {r_white:.3f} "
          f"(jk {jk_white[0]:.3f}±{jk_white[1]:.3f}, theory {theo_white:.3f})",
          flush=True)
    print(f"ratio white+red GLS/mean:  {r_wr:.3f} "
          f"(jk {jk_wr[0]:.3f}±{jk_wr[1]:.3f}, theory {theo_wr:.3f})",
          flush=True)
    print(f"high-pass ratios: white-only {r_hp_white:.3f}, "
          f"white+red {r_hp_wr:.3f}", flush=True)
    print("cross-pulsar corr of epoch residuals:\n",
          np.round(corr, 2), flush=True)

    # merge into results JSON
    with open(os.path.join(HID, "nanograv_gls_results.json")) as f:
        res = json.load(f)
    res.update({
        "n_common_epochs": n_epoch,
        "T_common_yr": T_span_yr,
        "red_noise_chains": {p: {"log10_A": red[p][0], "gamma": red[p][1]}
                             for p in order},
        "red_epoch_sigma_ns": [float(np.sqrt(v) * 1e3) for v in red_var],
        "empirical_bin_rms_ns": [float(np.sqrt(v) * 1e3) for v in emp_var],
        "analysis_white_only": {
            "gls_weights": [float(x) for x in w_white],
            "variance_ratio_gls_over_mean": r_white,
            "jackknife_mean": jk_white[0], "jackknife_std": jk_white[1],
            "theoretical_ratio_under_C": theo_white,
            "highpass_ratio": r_hp_white,
            "est_gls_rms_ns": rms_w, "est_mean_rms_ns": rms_m,
        },
        "analysis_white_plus_red": {
            "gls_weights": [float(x) for x in w_wr],
            "variance_ratio_gls_over_mean": r_wr,
            "jackknife_mean": jk_wr[0], "jackknife_std": jk_wr[1],
            "theoretical_ratio_under_C": theo_wr,
            "highpass_ratio": r_hp_wr,
            "est_gls_rms_ns": rms_wr,
        },
        "cross_pulsar_corr": corr.tolist(),
    })
    with open(os.path.join(HID, "nanograv_gls_results.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("updated nanograv_gls_results.json", flush=True)


if __name__ == "__main__":
    main()
