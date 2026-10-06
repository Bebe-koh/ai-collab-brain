"""Chain-vs-binned reconciliation, step 1: quantify and decompose.

For each anchor pulsar:
  1. Build chain-predicted covariance of the 30-day binned series from the
     enterprise red-noise posterior (median log10_A, gamma; Fourier design
     matrix, 30 freqs over the data span) + measured bin errors.
  2. chi2/n of the observed binned series under that covariance.
  3. Subtract best-fit quadratic (timing-model directions F0/F1) via GLS and
     recompute chi2/dof.

If (3) -> ~1, the "excess" lived in timing-model directions: the fixed-par
binning kept low-order power that enterprise attributed to the timing model
(the G-matrix marginalization). Fix = project out timing model when binning.
If (3) still >> 1, the chains genuinely miss low-frequency structure
(e.g. J1909's 8.8-yr wobble) and need explicit extra components.
"""
import numpy as np, json, os

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
os.chdir(HID)
ND = os.path.join(HID, "nanograv15yr/extracted/narrowband")
z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
centers = z["centers"]

def red_cov(t_yr, logA, gamma, T_yr, nfreq=30):
    # Fourier-basis red covariance, enterprise convention
    A = 10 ** logA
    F = []
    for k in range(1, nfreq + 1):
        f = k / T_yr
        S = A ** 2 / (12 * np.pi ** 2) * (f) ** (-gamma)  # f_yr = 1/yr; yr^3
        phi = S / T_yr  # * df, df = 1/T
        F.append(np.sqrt(phi) * np.sin(2 * np.pi * f * t_yr))
        F.append(np.sqrt(phi) * np.cos(2 * np.pi * f * t_yr))
    F = np.array(F).T
    C = F @ F.T * (365.25 * 86400 * 1e9) ** 2  # yr^2 -> ns^2
    return C

out = {}
for psr, key in [("J1909-3744", "binned_J1909"), ("B1937+21", "binned_B1937"),
                 ("B1855+09", "binned_B1855"), ("J0437-4715", "binned_J0437")]:
    b = z[key]
    mjd = centers[b[:, 0].astype(int)]
    t_yr = (mjd - mjd[0]) / 365.25
    T_yr = t_yr.max()
    r = b[:, 1] * 1e3   # ns
    e = np.maximum(b[:, 2] * 1e3, 20.0)
    n = len(r)

    pars = [l.strip() for l in open(os.path.join(ND, f"noise/{psr}.nb.pars.txt"))]
    ch = np.loadtxt(os.path.join(ND, f"noise/{psr}.nb.chain_1.txt"))
    lgA = np.median(ch[:, pars.index(f"{psr}_red_noise_log10_A")])
    gam = np.median(ch[:, pars.index(f"{psr}_red_noise_gamma")])

    C = red_cov(t_yr, lgA, gam, T_yr) + np.diag(e ** 2)
    Ci = np.linalg.inv(C)
    chi2 = float(r @ Ci @ r)

    # GLS quadratic subtraction (timing-model directions)
    X = np.vstack([np.ones(n), t_yr, t_yr ** 2]).T
    XtCi = X.T @ Ci
    beta = np.linalg.solve(XtCi @ X, XtCi @ r)
    rr = r - X @ beta
    chi2_q = float(rr @ Ci @ rr)

    # chain-predicted binned rms vs observed
    pred_rms = float(np.sqrt(np.mean(np.diag(C))))
    obs_rms = float(np.std(r))
    out[psr] = {"n": n, "log10A": float(lgA), "gamma": float(gam),
                "chi2_over_n": chi2 / n,
                "chi2_over_dof_after_quad": chi2_q / (n - 3),
                "pred_rms_ns": pred_rms, "obs_rms_ns": obs_rms}
    print(f"{psr}: n={n} logA={lgA:.2f} gam={gam:.2f} "
          f"chi2/n={chi2/n:.1f} -> after quad {chi2_q/(n-3):.1f} | "
          f"rms pred={pred_rms:.0f} obs={obs_rms:.0f} ns")

json.dump(out, open("chain_binned_step1.json", "w"), indent=1)
print("wrote chain_binned_step1.json")
