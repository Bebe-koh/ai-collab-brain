"""Variant tests: what actually drives the (a) vs (b) separation?"""
import numpy as np
from covmatch_experiment import (gen_pulsar, gen_powerlaw_red, kf_innovations,
    kf_loglike, cov_match, ml_scan, truth_matched_q)

rng = np.random.default_rng(11)
N, T_yr = 1500, 15.0
dt = T_yr * 365.25 / N
T_days = T_yr * 365.25
f_ref = 1.0 / 365.25
sig2 = 1.0
S_w = 2.0 * sig2 * dt
f_T = 1.0 / T_days
A_red = np.sqrt(60.0 * S_w) * (f_T / f_ref) ** 2.0
f_grid = np.logspace(np.log10(0.3), np.log10(30.0), 61)

def gated_ml(y, dt, q, sig2, f_grid, gate=5.0, maxit=10):
    """Iterative gated ML: fit f on kept obs, gate |v|/sqrt(S) > gate, repeat."""
    f = 1.0
    kept = np.ones(len(y), bool)
    for _ in range(maxit):
        # scan on kept obs only
        lls = []
        for ff in f_grid:
            v, S = kf_innovations(y, dt, q, ff * sig2)
            k = kept.copy(); k[:10] = False
            lls.append(-0.5 * np.sum(np.log(2*np.pi*S[k]) + v[k]**2 / S[k]))
        f_new = f_grid[int(np.argmax(lls))]
        v, S = kf_innovations(y, dt, q, f_new * sig2)
        kept_new = (np.abs(v) / np.sqrt(S)) < gate
        kept_new[:10] = False
        if f_new == f and np.array_equal(kept_new, kept):
            break
        f, kept = f_new, kept_new
    return f

def run_case(name, y, q):
    fa, _ = cov_match(y, dt, q, sig2, f0=1.0)
    fb, _ = ml_scan(y, dt, q, sig2, f_grid)
    fb_g = gated_ml(y, dt, q, sig2, f_grid)
    print(f"{name:44s} match={fa:6.3f}  ML={fb:6.3f}  gatedML={fb_g:6.3f}  "
          f"ratio_ungated={fa/fb:4.2f}x  ratio_gated={fa/fb_g:4.2f}x")

# Case 1: spikes + steep red, q @ 1/T  (baseline "both")
y = gen_pulsar(rng, N, dt, A_red, 3.5, f_ref, spike_frac=0.03)
q = truth_matched_q(A_red, 3.5, f_ref, T_days, at_bin=1.0)
run_case("spikes+steep red, q@1/T", y, q)

# Case 2: same truth, q matched at HIGH freq (30/T) -> RW under-covers low-f red
q2 = truth_matched_q(A_red, 3.5, f_ref, T_days, at_bin=30.0)
run_case("spikes+steep red, q@30/T (under-covered)", y, q2)

# Case 3: add deterministic sinusoid (B1937-like 31-yr term scaled to 15-yr span:
# use 7-yr period) on top of PL red + spikes
t = np.arange(N) * dt
y3 = gen_pulsar(rng, N, dt, A_red, 3.5, f_ref, spike_frac=0.03)
red_rms = np.std(gen_powerlaw_red(rng, N, dt, A_red, 3.5, f_ref))
y3 = y3 + 1.5 * red_rms * np.sin(2 * np.pi * t / (7 * 365.25))
run_case("spikes+steep red+sine(7yr), q@1/T", y3, q)

# Case 4: broken power law red (steeper below 3/T) + spikes
def gen_broken(rng, N, dt, A, f_ref, f_brk, g_lo, g_hi):
    freqs = np.fft.rfftfreq(N, dt)
    S = np.zeros_like(freqs); m = freqs > 0
    S[m] = np.where(freqs[m] < f_brk,
                    A**2 * (freqs[m]/f_ref)**(-g_lo),
                    A**2 * (f_brk/f_ref)**(g_hi-g_lo) * (freqs[m]/f_ref)**(-g_hi))
    X = np.zeros(N//2+1, dtype=complex)
    X[m] = np.sqrt(S[m]*N/(2*dt)) * (rng.standard_normal(m.sum())+1j*rng.standard_normal(m.sum()))/np.sqrt(2)
    return np.fft.irfft(X, n=N)
y4 = gen_broken(rng, N, dt, A_red, f_ref, 3.0/T_days, 5.0, 2.5)
w = rng.standard_normal(N); sp = rng.random(N) < 0.03
w[sp] = rng.standard_normal(sp.sum())*10.0
y4 = y4 + w
# q matched to broken-PL at 1/T
S_star = A_red**2 * ((1.0/T_days)/f_ref)**(-5.0)
q4 = S_star * (2*np.pi/T_days)**2
run_case("broken PL red + spikes, q@1/T", y4, q4)
