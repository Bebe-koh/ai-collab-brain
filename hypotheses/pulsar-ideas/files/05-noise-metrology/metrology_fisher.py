"""
Pulsar noise-metrology fresh run: does a better clock let you measure
intrinsic pulsar red noise below current published floors?

Method: Fisher information for the red-noise amplitude in a simulated
MSP timing campaign, as a function of clock grade. White noise is FITTED
freely (per the chain_binned repair lesson -- never trust formal errors).
Timing model (quadratic + annual terms) exactly marginalized via null-space
projection. Red-noise PSD uses the enterprise convention:
    S(f) = A^2/(12 pi^2) * (f/f_yr)^-gamma * yr^3   [one-sided, s^2/Hz]

Clock grades (Allan deviation sigma_y(tau), tau in seconds):
  perfect : no clock noise
  maser   : sqrt((1e-13)^2/tau + (1e-15)^2)          [ground H-maser]
  maser_s : maser + timescale steering cutoff below f=1/(100 d)
            (observatories steer to UTC; raw flicker does not extend to 1/yr)
  dsac    : sqrt((8e-13)^2/tau + (4e-15)^2)          [DSAC in-space numbers]
  csac    : (3e-10)/sqrt(tau)                        [chip-scale, white FM]

Clock PSD: S_y(f) = h0 + h_-1/f ; S_x(f) = S_y(f)/(2 pi f)^2.
  white FM: h0 = 2*tau0*sigma_y(tau0)^2 ; flicker FM: h_-1 = floor^2/(2 ln2).
"""
import numpy as np

YR = 365.25 * 86400.0
F_YR = 1.0 / YR
LN2 = np.log(2.0)

# ----------------------------------------------------------------------------
# PSD models
# ----------------------------------------------------------------------------
def S_red(f, A, gamma):
    f = np.maximum(f, 1e-30)
    return A**2 / (12 * np.pi**2) * (f / F_YR) ** (-gamma) * YR**3

def clock_Sx(f, h0, h_m1, f_steer=None):
    f = np.maximum(f, 1e-30)
    Sy = h0 + h_m1 / f
    if f_steer is not None:
        Sy = Sy / (1.0 + (f_steer / f) ** 4)   # steering kills low-f wander
    return Sy / (2 * np.pi * f) ** 2

CLOCKS = {
    "perfect": dict(h0=0.0, h_m1=0.0, f_steer=None, label="perfect clock"),
    "maser":   dict(h0=2*(1e-13)**2, h_m1=(1e-15)**2/(2*LN2), f_steer=None,
                    label="H-maser, raw flicker to 1/yr (pessimistic)"),
    "maser_s": dict(h0=2*(1e-13)**2, h_m1=(1e-15)**2/(2*LN2),
                    f_steer=1/(100*86400.0), label="H-maser + UTC steering"),
    "dsac":    dict(h0=2*(8e-13)**2, h_m1=(4e-15)**2/(2*LN2), f_steer=None,
                    label="DSAC (in-space demonstrated)"),
    "csac":    dict(h0=2*(3e-10)**2, h_m1=0.0, f_steer=None,
                    label="chip-scale atomic clock"),
}

# ----------------------------------------------------------------------------
# Campaign simulator: covariance construction
# ----------------------------------------------------------------------------
def build_campaign(pulsar, seed=0):
    rng = np.random.default_rng(seed)
    T = pulsar["T_yr"] * YR
    N = pulsar["N"]
    # ~monthly cadence with jittered spacing and a couple of gaps
    t = np.sort(rng.uniform(0, T, N))
    t = t - t.mean()
    return t

def cov_from_psd(t, S_of_f, df_factor=20, fmax=None):
    """C[i,j] = sum_k S(f_k) df cos(2 pi f_k (t_i - t_j)), one-sided PSD."""
    T = t.max() - t.min()
    df = 1.0 / (df_factor * T)
    if fmax is None:
        fmax = 0.5 / np.min(np.diff(np.sort(t)))
    K = int(fmax / df)
    f = (np.arange(K) + 1) * df
    w = S_of_f(f) * df
    F = np.exp(2j * np.pi * np.outer(t, f))          # N x K
    C = np.real((F * w) @ F.conj().T)
    return C

def null_projector(t):
    yr = 365.25 * 86400.0
    M = np.column_stack([np.ones_like(t), t, t**2,
                         np.cos(2*np.pi*t/yr), np.sin(2*np.pi*t/yr)])
    U, s, _ = np.linalg.svd(M, full_matrices=True)
    rank = np.sum(s > 1e-10 * s[0])
    return U[:, rank:]                               # N x (N-rank)

def projected_fisher(t, A_fid, gamma, sigma_w, clock):
    """Fisher matrix for theta=(ln A_red, ln sigma_w) in projected space."""
    Q = null_projector(t)
    C_red = cov_from_psd(t, lambda f: S_red(f, A_fid, gamma))
    C_clk = cov_from_psd(t, lambda f: clock_Sx(f, **{k: clock[k]
                                for k in ("h0", "h_m1", "f_steer")}))
    C = C_red + sigma_w**2 * np.eye(len(t)) + C_clk
    Cp = Q.T @ C @ Q
    dA = Q.T @ (2 * C_red) @ Q
    dW = Q.T @ (2 * sigma_w**2 * np.eye(len(t))) @ Q
    Ci = np.linalg.inv(Cp)
    F = np.empty((2, 2))
    F[0, 0] = 0.5 * np.trace(Ci @ dA @ Ci @ dA)
    F[1, 1] = 0.5 * np.trace(Ci @ dW @ Ci @ dW)
    F[0, 1] = F[1, 0] = 0.5 * np.trace(Ci @ dA @ Ci @ dW)
    return F, C_red, C_clk

def sigma_lnA(t, A_fid, gamma, sigma_w, clock):
    F, _, _ = projected_fisher(t, A_fid, gamma, sigma_w, clock)
    cov = np.linalg.inv(F)
    if cov[0, 0] <= 0 or not np.isfinite(cov[0, 0]):
        return np.inf
    return np.sqrt(cov[0, 0])

def upper_limit(t, gamma, sigma_w, clock, target_snr=2.0):
    """Solve A/sigma_A(A) = target_snr by bisection on log10 A."""
    def snr_of_logA(la):
        A = 10.0**la
        s = sigma_lnA(t, A, gamma, sigma_w, clock)
        return np.inf if not np.isfinite(s) or s == 0 else 1.0 / s
    lo, hi = -18.0, -11.0
    # ensure bracket
    assert snr_of_logA(lo) < target_snr < snr_of_logA(hi), "bracket failed"
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if snr_of_logA(mid) < target_snr:
            lo = mid
        else:
            hi = mid
    return 10.0**mid

# ----------------------------------------------------------------------------
# Pulsar campaign definitions (published-anchored)
# ----------------------------------------------------------------------------
PULSARS = {
    # name: white ns/epoch, T yr, N epochs, published (log10A, gamma or None)
    "J1909-3744": dict(sigma_w_ns=50.0, T_yr=15.0, N=180,
                       pub_logA=-14.5, pub_gamma=4.1, note="jitter~10ns/hr"),
    "J1713+0747": dict(sigma_w_ns=70.0, T_yr=15.0, N=180,
                       pub_logA=-14.1, pub_gamma=2.6, note="jitter~51ns/20min"),
    "J0437-4715": dict(sigma_w_ns=50.0, T_yr=15.0, N=180,
                       pub_logA=-13.4, pub_gamma=0.5, note="jitter~30ns/hr"),
}

def detection_snr(t, A_true, gamma, sigma_w, clock):
    s = sigma_lnA(t, A_true, gamma, sigma_w, clock)
    return 1.0 / s

if __name__ == "__main__":
    print(f"{'pulsar':12s} {'clock':10s} {'UL log10A':>10s} | "
          f"published det. SNR (maser_s)")
    print("-" * 70)
    for pname, p in PULSARS.items():
        t = build_campaign(p, seed=1)
        sw = p["sigma_w_ns"] * 1e-9
        row = []
        for cname in ["perfect", "maser", "maser_s", "dsac", "csac"]:
            ul = upper_limit(t, 4.0, sw, CLOCKS[cname])
            row.append(f"{cname:10s} {np.log10(ul):10.2f}")
        for r in row:
            print(f"{pname:12s} {r}")
        # detection SNR of the published amplitude under realistic clock
        A_pub = 10.0**p["pub_logA"]
        snr = detection_snr(t, A_pub, p["pub_gamma"], sw, CLOCKS["maser_s"])
        print(f"{'':12s} {'published A SNR':>22s} {snr:10.1f}")
        print()
