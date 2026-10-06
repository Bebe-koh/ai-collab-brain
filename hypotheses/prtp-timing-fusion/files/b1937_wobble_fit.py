"""B1937 deterministic-wobble fit (PRTP repair step 3).

Models for B1937's 167-bin series (15.5 yr):
  M0: quadratic + power-law red (chain shape, free scale) + white (free)
  M1: M0 + free sinusoid (A, P, phi free)
  M2: M0 + sinusoid with P fixed at 31 yr (Vivekanand 2020)
Quadratic is GLS-profiled at each likelihood evaluation.
Compares via dlnL and BIC. A deterministic sinusoid competing against the
stochastic power law tests whether the drift is better described as
quasi-deterministic (planet/precession per Vivekanand) than red noise.
"""
import numpy as np, json, os
from scipy.optimize import minimize

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
os.chdir(HID)
ND = "nanograv15yr/extracted/narrowband"
z = np.load("nanograv_binned.npz", allow_pickle=True)
centers = z["centers"]

b = z["binned_B1937"]
mjd = centers[b[:, 0].astype(int)]
t_yr = (mjd - mjd[0]) / 365.25
T = t_yr.max()
r = b[:, 1] * 1e3  # ns
n = len(r)

pars = [l.strip() for l in open(f"{ND}/noise/B1937+21.nb.pars.txt")]
ch = np.loadtxt(f"{ND}/noise/B1937+21.nb.chain_1.txt")
lgA = np.median(ch[:, pars.index("B1937+21_red_noise_log10_A")])
gam = np.median(ch[:, pars.index("B1937+21_red_noise_gamma")])

def red_cov(t_yr, logA, gamma, T_yr, nfreq=30):
    A = 10 ** logA
    F = []
    for k in range(1, nfreq + 1):
        f = k / T_yr
        S = A ** 2 / (12 * np.pi ** 2) * f ** (-gamma)
        phi = S / T_yr
        F.append(np.sqrt(phi) * np.sin(2 * np.pi * f * t_yr))
        F.append(np.sqrt(phi) * np.cos(2 * np.pi * f * t_yr))
    F = np.array(F).T
    return F @ F.T * (365.25 * 86400 * 1e9) ** 2

Cr = red_cov(t_yr, lgA, gam, T) + 1e-6 * np.eye(n)
X = np.vstack([np.ones(n), t_yr, t_yr ** 2]).T  # profiled timing model

def fit_model(P_fixed=None):
    """Returns (lnLmax, params). params: [log_s_red, log_s_w, A, phi(, P)]."""
    def nll(p):
        ls_red, ls_w = p[0], p[1]
        A = p[2]; phi = p[3]
        P = P_fixed if P_fixed is not None else p[4]
        if P <= 4 or P > 60:
            return 1e12, None
        s_red, s_w = np.exp(np.clip([ls_red, ls_w], -7, 12))
        C = s_red * Cr + s_w * np.eye(n)
        try:
            Ci = np.linalg.inv(C)
        except np.linalg.LinAlgError:
            return 1e12, None
        Xs = np.column_stack([X, np.sin(2 * np.pi * t_yr / P + phi),
                              np.cos(2 * np.pi * t_yr / P + phi)])
        # linear params: quad coefs + sin/cos amplitudes (A folded in)
        XtCi = Xs.T @ Ci
        beta = np.linalg.solve(XtCi @ Xs, XtCi @ r)
        rr = r - Xs @ beta
        sign, logdet = np.linalg.slogdet(C)
        return 0.5 * (rr @ Ci @ rr + logdet)
    # note: A,phi redundant with sin/cos linear amps; keep (A,phi,P) for
    # interpretability but the linear solve absorbs them; fix A=1,phi=0 and
    # let linear amps carry it. Simpler: optimize only scales + P.
    def nll2(p):
        ls_red, ls_w = p[0], p[1]
        P = P_fixed if P_fixed is not None else p[2]
        if P <= 4 or P > 60:
            return 1e12, None
        s_red, s_w = np.exp(np.clip([ls_red, ls_w], -7, 12))
        C = s_red * Cr + s_w * np.eye(n)
        try:
            Ci = np.linalg.inv(C)
        except np.linalg.LinAlgError:
            return 1e12, None
        Xs = np.column_stack([X, np.sin(2 * np.pi * t_yr / P),
                              np.cos(2 * np.pi * t_yr / P)])
        XtCi = Xs.T @ Ci
        beta = np.linalg.solve(XtCi @ Xs, XtCi @ r)
        rr = r - Xs @ beta
        sign, logdet = np.linalg.slogdet(C)
        return 0.5 * (rr @ Ci @ rr + logdet), beta
    if P_fixed is not None:
        res = minimize(lambda p: nll2(p)[0], [0.0, 11.0], method="Nelder-Mead",
                       options=dict(maxiter=8000))
        nllv, beta = nll2(res.x)
        A = float(np.sqrt(beta[3] ** 2 + beta[4] ** 2))
        phi = float(np.arctan2(beta[4], beta[3]))
        return -nllv, {"s_red": float(np.exp(res.x[0])),
                       "white_ns": float(np.sqrt(np.exp(res.x[1]))),
                       "A_ns": A, "phi": phi, "P_yr": P_fixed}
    # free P: grid then refine
    best = (1e18, None)
    for P0 in [8, 12, 16, 20, 25, 31, 40, 50]:
        res = minimize(lambda p: nll2(p)[0], [0.0, 11.0, P0],
                       method="Nelder-Mead", options=dict(maxiter=8000))
        if res.fun < best[0]:
            best = (res.fun, res.x)
    nllv, beta = nll2(best[1])
    A = float(np.sqrt(beta[3] ** 2 + beta[4] ** 2))
    phi = float(np.arctan2(beta[4], beta[3]))
    return -nllv, {"s_red": float(np.exp(best[1][0])),
                   "white_ns": float(np.sqrt(np.exp(best[1][1]))),
                   "A_ns": A, "phi": phi, "P_yr": float(best[1][2])}

def fit_M0():
    def nll(p):
        s_red, s_w = np.exp(np.clip(p, -7, 12))
        C = s_red * Cr + s_w * np.eye(n)
        Ci = np.linalg.inv(C)
        XtCi = X.T @ Ci
        beta = np.linalg.solve(XtCi @ X, XtCi @ r)
        rr = r - X @ beta
        sign, logdet = np.linalg.slogdet(C)
        return 0.5 * (rr @ Ci @ rr + logdet)
    res = minimize(nll, [0.0, 11.0], method="Nelder-Mead",
                   options=dict(maxiter=8000))
    return -res.fun, {"s_red": float(np.exp(res.x[0])),
                       "white_ns": float(np.sqrt(np.exp(res.x[1])))}

lnL0, p0 = fit_M0()
lnL1, p1 = fit_model(P_fixed=None)
lnL2, p2 = fit_model(P_fixed=31.47)

# BIC: k params (M0: 2 scales; M1: 2 scales + P,A,phi = 5; M2: 2 scales + A,phi = 4)
def bic(lnL, k):
    return k * np.log(n) - 2 * lnL

out = {"M0_red_only": {"lnL": lnL0, "BIC": bic(lnL0, 2), "params": p0},
       "M1_free_sinusoid": {"lnL": lnL1, "BIC": bic(lnL1, 5),
                            "dlnL_vs_M0": lnL1 - lnL0, "params": p1},
       "M2_P31p5yr": {"lnL": lnL2, "BIC": bic(lnL2, 4),
                    "dlnL_vs_M0": lnL2 - lnL0, "params": p2}}
json.dump(out, open("b1937_wobble_fit.json", "w"), indent=1)
for k, v in out.items():
    print(k, {kk: round(vv, 2) if isinstance(vv, float) else vv
              for kk, vv in v.items() if kk != "params"})
    print("   params:", {kk: round(vv, 2) if isinstance(vv, float) else vv
                         for kk, vv in v["params"].items()})
