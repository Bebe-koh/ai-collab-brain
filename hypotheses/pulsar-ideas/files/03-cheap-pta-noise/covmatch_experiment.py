"""
Fresh-run verification: covariance-matching noise-estimation shortcut for PTA-like data.

Claim under test (Jase, PRTP radio-pilot work, 2026-10-03):
  The textbook adaptive-KF white-noise update f <- f*mean(NIS) (Mehra-style
  innovation covariance matching) converges STABLY but to a NON-ML fixed point
  under process-model misspecification, over-whitening ~2x
  (B1855: f_hat=4.96 vs pseudo-LL max 2.42, direct scan).
Mechanism is folk knowledge (Brown & Rutan: "covering the errors in the model
with noise"); the quantified fixed-point/ML separation is the candidate novelty.

This script independently reproduces the phenomenon on SYNTHETIC data:
  truth  = white noise + power-law red noise  S(f) = A^2 (f/f_ref)^-gamma_true
  model  = 2-state random walk (i.e. red with gamma=2) + white, KF-estimated
  mismatch = gamma_true != 2  (real reds aren't random walks)
Estimators for the white-noise scale f (q fixed, identical for both):
  (a) covariance matching: iterate f <- f * mean(v^2 / S_innov) to convergence
  (b) direct 1-D likelihood scan over f (exact Gaussian PED likelihood from KF)
Then: separation f_a/f_b vs mismatch severity; wall-clock scaling; downstream
optimal-statistic detection-power comparison on a multi-pulsar common signal.

Simplifications (documented, orthogonal to the noise-estimation question):
  - regular sampling (real TOAs are irregular; DFT-based OS needs regularity)
  - post-fit residuals (timing-model marginalization not included)
  - q (process-noise PSD) truth-matched at f=3/T for both estimators;
    one sensitivity variant estimates q from data instead.
Units: residual time units are arbitrary; sigma_formal = 1.
"""
import numpy as np
import time

# ----------------------------------------------------------------------------
# 1. Synthetic data: white + power-law red noise (FFT method)
# ----------------------------------------------------------------------------
def gen_powerlaw_red(rng, N, dt, A, gamma, f_ref):
    """Residuals with one-sided PSD S(f) = A^2 (f/f_ref)^-gamma. f_ref in 1/day."""
    freqs = np.fft.rfftfreq(N, dt)
    S = np.zeros_like(freqs)
    m = freqs > 0
    S[m] = A ** 2 * (freqs[m] / f_ref) ** (-gamma)
    # E|X_k|^2 = S(f_k) * N / (2 dt) for 0<k<N/2  (numpy irfft normalization)
    X = np.zeros(N // 2 + 1, dtype=complex)
    X[m] = np.sqrt(S[m] * N / (2 * dt)) * (rng.standard_normal(m.sum()) +
                                          1j * rng.standard_normal(m.sum())) / np.sqrt(2)
    x = np.fft.irfft(X, n=N)
    return x


def gen_pulsar(rng, N, dt, A_red, gamma_true, f_ref, f_white=1.0, sig_formal=1.0,
               common=None, spike_frac=0.0, spike_var=100.0):
    """One pulsar's residuals: white (+ optional heavy-tailed spikes)
    + intrinsic red (+ optional common signal)."""
    y = gen_powerlaw_red(rng, N, dt, A_red, gamma_true, f_ref)
    w = rng.standard_normal(N) * sig_formal * np.sqrt(f_white)
    if spike_frac > 0:
        spike = rng.random(N) < spike_frac
        w[spike] = rng.standard_normal(spike.sum()) * sig_formal * np.sqrt(spike_var)
    y = y + w
    if common is not None:
        y = y + common
    return y


# ----------------------------------------------------------------------------
# 2. Kalman filter: 2-state random walk, scalar position measurements
#    x = [phase, freq]; F = [[1,dt],[0,1]]; Q = q*[[dt^3/3, dt^2/2],[dt^2/2, dt]]
# ----------------------------------------------------------------------------
def kf_innovations(y, dt, q, R):
    n = len(y)
    x = np.zeros(2)
    P = np.eye(2) * 1.0          # broad but finite init (same for both estimators)
    F = np.array([[1.0, dt], [0.0, 1.0]])
    Q = q * np.array([[dt ** 3 / 3.0, dt ** 2 / 2.0],
                      [dt ** 2 / 2.0, dt]])
    v = np.empty(n)
    S = np.empty(n)
    I2 = np.eye(2)
    for t in range(n):
        # predict
        x = F @ x
        P = F @ P @ F.T + Q
        # update (scalar)
        v[t] = y[t] - x[0]
        S[t] = P[0, 0] + R
        K = P[:, 0] / S[t]
        x = x + K * v[t]
        P = (I2 - np.outer(K, [1.0, 0.0])) @ P
    return v, S


def kf_loglike(y, dt, q, R):
    v, S = kf_innovations(y, dt, q, R)
    # skip first few samples to wash out the broad init transient
    k0 = 10
    return -0.5 * np.sum(np.log(2 * np.pi * S[k0:]) + v[k0:] ** 2 / S[k0:])


# ----------------------------------------------------------------------------
# 3. Estimators for the white-noise scale f  (R = f * sig_formal^2)
# ----------------------------------------------------------------------------
def cov_match(y, dt, q, sig2, f0=1.0, tol=1e-8, maxit=500):
    """(a) Textbook Mehra update: f <- f * mean(v^2/S). Returns f, n_iter."""
    f = f0
    for it in range(1, maxit + 1):
        v, S = kf_innovations(y, dt, q, f * sig2)
        nis = np.mean(v[10:] ** 2 / S[10:])
        f_new = f * nis
        if abs(f_new - f) <= tol * max(f, 1e-300):
            return f_new, it
        f = f_new
    return f, maxit  # did not converge within maxit


def ml_scan(y, dt, q, sig2, f_grid):
    """(b) Direct 1-D likelihood scan. Returns f_ML, max loglike."""
    lls = np.array([kf_loglike(y, dt, q, f * sig2) for f in f_grid])
    return f_grid[int(np.argmax(lls))], float(np.max(lls))


def truth_matched_q(A_red, gamma_true, f_ref, T_days, at_bin=1.0):
    """Random-walk q whose PSD matches truth at f = at_bin/T.
    RW phase PSD (one-sided): S_rw(f) = q / (2 pi f)^2."""
    f_star = at_bin / T_days
    S_star = A_red ** 2 * (f_star / f_ref) ** (-gamma_true)
    return S_star * (2 * np.pi * f_star) ** 2


# ----------------------------------------------------------------------------
# Experiment 1: fixed-point vs ML separation vs mismatch severity
# ----------------------------------------------------------------------------
def experiment_separation():
    rng = np.random.default_rng(7)
    N, T_yr = 1500, 15.0
    dt = T_yr * 365.25 / N
    T_days = T_yr * 365.25
    f_ref = 1.0 / 365.25          # 1/yr in 1/day
    sig2 = 1.0
    # red amplitude: red PSD = 60x white PSD at f = 1/T (red-dominated low end)
    S_w = 2.0 * sig2 * dt         # one-sided white PSD
    f_T = 1.0 / T_days
    A_red = np.sqrt(60.0 * S_w) * (f_T / f_ref) ** (4.0 / 2.0)  # calibrated at gamma=4
    f_grid = np.logspace(np.log10(0.3), np.log10(30.0), 61)

    print("=== Experiment 1: covariance-matching fixed point vs ML ===")
    print("N=%d, T=%.1f yr, dt=%.2f d; q truth-matched at f=1/T per gamma" % (N, T_yr, dt))
    print("mismatch scenarios: (i) correct model control, (ii) heavy-tailed",
          "white (B1855-like spikes), (iii) steep red (gamma=3.5), (iv) both")
    rows = []
    scenarios = [
        ("control: gamma=2, no spikes", 2.0, 0.0),
        ("spikes only: gamma=2", 2.0, 0.03),
        ("steep red only: gamma=3.5", 3.5, 0.0),
        ("both: gamma=3.5 + spikes", 3.5, 0.03),
        ("both: gamma=4.0 + spikes", 4.0, 0.03),
    ]
    for name, gamma_true, spike_frac in scenarios:
        y = gen_pulsar(rng, N, dt, A_red, gamma_true, f_ref,
                       spike_frac=spike_frac)
        q = truth_matched_q(A_red, gamma_true, f_ref, T_days, at_bin=1.0)
        # (a) from several inits -> stability check
        fa_list, it_list = [], []
        for f0 in [0.2, 1.0, 5.0, 20.0]:
            fa, it = cov_match(y, dt, q, sig2, f0=f0)
            fa_list.append(fa)
            it_list.append(it)
        fa = float(np.mean(fa_list))
        stable = (max(fa_list) - min(fa_list)) < 1e-6 * fa
        # (b)
        fb, llmax = ml_scan(y, dt, q, sig2, f_grid)
        rows.append((name, fa, fb, fa / fb, stable, int(np.mean(it_list))))
        print(f"{name:32s} f_match={fa:7.3f}  f_ML={fb:7.3f}  "
              f"ratio={fa/fb:5.2f}x  stable={stable}  iters~{np.mean(it_list):.0f}")
    return rows


if __name__ == "__main__":
    experiment_separation()
