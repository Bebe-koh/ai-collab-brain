"""NANOGrav 15yr real-data GLS check.

Loads narrowband .par/.tim for the 4 PRTP pulsars, computes post-fit
residuals with PINT (published timing solution, no refit), bins to common
30-day epochs, estimates per-pulsar white noise from the data (TOA
uncertainties scaled by chain-median EFAC/EQUAD/ECORR from the NANOGrav
noise chains), then compares the verified GLS common-mode estimator
w = inv(C)@1/(1.T@inv(C)@1) against the unweighted mean.

Outputs: nanograv_gls_results.json
"""
import json
import os
import numpy as np

BASE = os.path.expanduser("~/workspace/prtp/hidden_files/nanograv15yr/extracted")
NOISE = os.path.join(BASE, "narrowband/noise")

PULSARS = {
    "J0437-4715": ("narrowband/par/J0437-4715_PINT_20220301.nb.par",
                   "narrowband/tim/J0437-4715_PINT_20220301.nb.tim"),
    "J1909-3744": ("narrowband/par/J1909-3744_PINT_20220303.nb.par",
                   "narrowband/tim/J1909-3744_PINT_20220303.nb.tim"),
    "B1937+21":   ("narrowband/par/B1937+21_PINT_20220306.nb.par",
                   "narrowband/tim/B1937+21_PINT_20220306.nb.tim"),
    "B1855+09":   ("narrowband/par/B1855+09_PINT_20220301.nb.par",
                   "narrowband/tim/B1855+09_PINT_20220301.nb.tim"),
}

# ---------------------------------------------------------------- noise chains
def chain_medians(psr):
    """Posterior medians of the NANOGrav noise-chain parameters for psr.

    Returns dicts keyed by backend: efac, log10_equad, log10_ecorr medians,
    plus red-noise (log10_A, gamma) medians.
    """
    names_path = os.path.join(NOISE, f"{psr}.nb.pars.txt")
    with open(names_path) as f:
        names = [ln.strip() for ln in f if ln.strip()]
    # chain files may be split by observatory (e.g. B1937+21ao); use main one
    chain_path = os.path.join(NOISE, f"{psr}.nb.chain_1.txt")
    if not os.path.exists(chain_path):
        raise FileNotFoundError(f"no main chain for {psr}")
    data = np.loadtxt(chain_path)  # 19900 x (npar + 4)
    npar = len(names)
    med = np.median(data[:, :npar], axis=0)
    out = {"efac": {}, "log10_equad": {}, "log10_ecorr": {},
           "red_log10_A": None, "red_gamma": None}
    for name, m in zip(names, med):
        if name.endswith("_efac"):
            be = name[len(psr) + 1:-len("_efac")]
            out["efac"][be] = float(m)
        elif name.endswith("_log10_equad"):
            be = name[len(psr) + 1:-len("_log10_equad")]
            out["log10_equad"][be] = float(m)
        elif name.endswith("_log10_ecorr"):
            be = name[len(psr) + 1:-len("_log10_ecorr")]
            out["log10_ecorr"][be] = float(m)
        elif name.endswith("_red_noise_log10_A"):
            out["red_log10_A"] = float(m)
        elif name.endswith("_red_noise_gamma"):
            out["red_gamma"] = float(m)
    return out


def backend_key(fe, be):
    return f"{fe}_{be}"


# ---------------------------------------------------------------- residuals
def load_residuals(psr, par_rel, tim_rel):
    import pint.models
    import pint.residuals
    import pint.toa
    par = os.path.join(BASE, par_rel)
    tim = os.path.join(BASE, tim_rel)
    m, t = pint.models.get_model_and_toas(par, tim)
    r = pint.residuals.Residuals(t, m)
    res_us = r.time_resids.to_value("us")          # post-fit, published solution
    mjds = t.get_mjds().value
    sig_us = t.get_errors().to_value("us")         # raw TOA uncertainties
    # backend flags for EFAC/EQUAD lookup
    fe = np.array([str(x.get("fe", [""])[0]) if "fe" in x else "" for x in t.get_flags()])
    be = np.array([str(x.get("be", [""])[0]) if "be" in x else "" for x in t.get_flags()])
    return mjds, res_us, sig_us, fe, be


def main():
    results = {"pulsars": {}, "files_used": {}}
    series = {}

    for psr, (par_rel, tim_rel) in PULSARS.items():
        results["files_used"][psr] = {"par": par_rel, "tim": tim_rel}
        print(f"--- {psr}: loading", flush=True)
        mjds, res_us, sig_us, fe, be = load_residuals(psr, par_rel, tim_rel)
        print(f"    {len(mjds)} TOAs, MJD {mjds.min():.1f}..{mjds.max():.1f}, "
              f"raw resid RMS {np.std(res_us) * 1e3:.1f} ns", flush=True)

        nz = chain_medians(psr)
        # per-TOA corrected variance: (EFAC*sigma)^2 + EQUAD^2 ; ECORR added at bin level
        efac_arr = np.ones_like(sig_us)
        equad2 = np.zeros_like(sig_us)
        for i in range(len(sig_us)):
            key = backend_key(fe[i], be[i])
            ef = nz["efac"].get(key)
            if ef is None:
                # fall back: match any backend containing be flag
                cands = [v for k, v in nz["efac"].items() if be[i] in k]
                ef = cands[0] if cands else 1.0
            efac_arr[i] = ef
            qk = nz["log10_equad"].get(key)
            if qk is None:
                qc = [v for k, v in nz["log10_equad"].items() if be[i] in k]
                qk = qc[0] if qc else -9.0
            equad2[i] = (10.0 ** qk) ** 2
        var_toa = (efac_arr * sig_us) ** 2 + equad2          # us^2
        ecorr_med = (np.median([10.0 ** v for v in nz["log10_ecorr"].values()])
                     if nz["log10_ecorr"] else 0.0)

        # ---- outlier rejection: MAD-based cut on raw residuals.
        # ---- (White-noise-standardized clipping would mistake B1937+21's
        # ---- real red noise for outliers.) Same cut before both estimators.
        keep = np.ones(len(mjds), dtype=bool)
        med = np.median(res_us)
        mad = np.median(np.abs(res_us - med))
        thresh = 8.0 * 1.4826 * mad
        keep = np.abs(res_us - med) <= thresh
        ncut = int(len(mjds) - keep.sum())
        mjds, res_us, sig_us = mjds[keep], res_us[keep], sig_us[keep]
        var_toa = var_toa[keep]
        # weighted RMS sanity check (weights = 1/var_corrected)
        w = 1.0 / var_toa
        wrms_ns = float(np.sqrt(np.sum(w * res_us ** 2) / np.sum(w)) * 1e3)
        print(f"    cut {ncut} outlier TOAs ({ncut/len(keep)*100:.2f}% of kept), "
              f"weighted resid RMS {wrms_ns:.1f} ns", flush=True)

        series[psr] = (mjds, res_us, var_toa, ecorr_med)
        results["pulsars"][psr] = {
            "n_toa": int(len(mjds)),
            "n_toa_cut": ncut,
            "mjd_min": float(mjds.min()), "mjd_max": float(mjds.max()),
            "resid_rms_ns": float(np.std(res_us) * 1e3),
            "weighted_resid_rms_ns": wrms_ns,
            "red_noise": {"log10_A": nz["red_log10_A"], "gamma": nz["red_gamma"]},
            "n_efac_backends": len(nz["efac"]),
            "median_efac": float(np.median(list(nz["efac"].values()))),
            "median_equad_ns": float(np.median([10.0**v for v in nz["log10_equad"].values()]) * 1e3),
            "median_ecorr_ns": float(ecorr_med * 1e3),
        }

    # ------------------------------------------------------- common-epoch grid
    BIN = 30.0  # days
    all_mjd = np.concatenate([s[0] for s in series.values()])
    edges = np.arange(np.floor(all_mjd.min()), np.ceil(all_mjd.max()) + BIN, BIN)
    centers = 0.5 * (edges[:-1] + edges[1:])

    binned = {}   # psr -> (bin_index, weighted mean resid us, formal bin var us^2)
    for psr, (mjds, res_us, var_toa, ecorr_med) in series.items():
        bi = np.digitize(mjds, edges) - 1
        bm, bv = [], []
        for b in range(len(centers)):
            sel = bi == b
            if not np.any(sel):
                continue
            w = 1.0 / var_toa[sel]
            bm.append((b, np.sum(w * res_us[sel]) / np.sum(w),
                       1.0 / np.sum(w) + ecorr_med ** 2))
        binned[psr] = np.array(bm)

    # common epochs: bins present for ALL four pulsars
    common = set.intersection(*[set(b[:, 0].astype(int)) for b in binned.values()])
    common = sorted(common)
    print(f"common 30-day epochs: {len(common)}", flush=True)
    order = list(PULSARS.keys())
    R = np.array([[binned[p][binned[p][:, 0].astype(int) == c][0][1]
                   for p in order] for c in common])          # us
    V = np.array([[binned[p][binned[p][:, 0].astype(int) == c][0][2]
                   for p in order] for c in common])          # us^2 formal
    mjd_c = centers[np.array(common)]

    # per-pulsar white variance: median formal bin variance (data-estimated)
    sig2 = np.array([float(np.median(V[:, j])) for j in range(4)])
    print("per-pulsar per-epoch white sigma (ns):",
          np.round(np.sqrt(sig2) * 1e3, 1), flush=True)

    # save intermediates for downstream analysis (avoids reloading PINT)
    np.savez(os.path.expanduser("~/workspace/prtp/hidden_files/nanograv_binned.npz"),
             R=R, V=V, mjd_c=mjd_c, sig2=sig2,
             order=np.array(order), centers=centers,
             binned_J0437=binned["J0437-4715"], binned_J1909=binned["J1909-3744"],
             binned_B1937=binned["B1937+21"], binned_B1855=binned["B1855+09"])

    # ------------------------------------------------------------- GLS test
    C = np.diag(sig2)
    ones = np.ones(4)
    w_gls = np.linalg.solve(C, ones)
    w_gls = w_gls / (ones @ w_gls)
    w_mean = ones / 4.0

    est_gls = R @ w_gls
    est_mean = R @ w_mean
    # remove overall means (common-mode estimators are zero-mean by construction)
    est_gls -= est_gls.mean(); est_mean -= est_mean.mean()

    var_gls, var_mean = float(np.var(est_gls)), float(np.var(est_mean))
    ratio = var_gls / var_mean
    # theoretical ratio under the assumed C
    theo = float((w_gls @ C @ w_gls) / (w_mean @ C @ w_mean))
    # high-pass check: variance of epoch-to-epoch differences (white-dominated)
    d_gls = np.diff(est_gls); d_mean = np.diff(est_mean)
    ratio_hp = float(np.var(d_gls) / np.var(d_mean))
    # split-half stability
    h = len(common) // 2
    r1 = float(np.var(est_gls[:h]) / np.var(est_mean[:h]))
    r2 = float(np.var(est_gls[h:]) / np.var(est_mean[h:]))

    print(f"GLS weights: {np.round(w_gls, 4)}", flush=True)
    print(f"var ratio GLS/mean: {ratio:.3f} (theory under C: {theo:.3f})", flush=True)
    print(f"high-pass ratio: {ratio_hp:.3f}; split halves: {r1:.3f}, {r2:.3f}", flush=True)

    results.update({
        "bin_days": BIN,
        "n_common_epochs": len(common),
        "mjd_common_min": float(mjd_c.min()), "mjd_common_max": float(mjd_c.max()),
        "pulsar_order": order,
        "per_pulsar_epoch_sigma_ns": [float(np.sqrt(s) * 1e3) for s in sig2],
        "gls_weights": [float(x) for x in w_gls],
        "est_gls_rms_ns": float(np.sqrt(var_gls) * 1e3),
        "est_mean_rms_ns": float(np.sqrt(var_mean) * 1e3),
        "variance_ratio_gls_over_mean": ratio,
        "theoretical_ratio_under_C": theo,
        "highpass_variance_ratio": ratio_hp,
        "split_half_ratios": [r1, r2],
        "notes": ("Variances are sample variances of the common-mode estimate "
                  "series on real residuals; no truth signal injected. C is "
                  "diagonal white noise estimated from the data (TOA errors "
                  "scaled by chain-median EFAC/EQUAD, median ECORR added per "
                  "bin). Red noise characterized from chain medians but not "
                  "included in the per-epoch C."),
    })
    out = os.path.expanduser(
        "~/workspace/prtp/hidden_files/nanograv_gls_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
