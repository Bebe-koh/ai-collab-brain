#!/usr/bin/env python3
"""Fresh-run: systematic precursor search before Crab pulsar glitches.

Data: Jodrell Bank Crab monthly ephemeris (crab2.txt, MJD 47296-61245, 482
monthly nu points) + JB glitch catalogue epochs (B0531+21, 32 glitches).

Design (independent rebuild; statistical philosophy mirrors the Kerr transient
pipeline but adapted to red, irregularly-sampled monthly timing data):
  For each glitch with a clean pre-window:
    - reference trend: inverse-variance linear fit on [-360,-60] d
    - probe residuals on [-60,+30] d
  Test A: stacked weighted-mean residual in [-60,0] d (precursor slow-down dip)
  Test B: max positive step (forerunner microglitch) in [-210,-30] d
  Test C: paired pre/post RMS of detrended residuals (IAR claim replication)
  Null: identical procedure at random glitch-free epochs drawn from each
        glitch's own clean inter-glitch stretch (matched noise environment)
  Positive control: the pipeline must recover the catalogued glitches themselves
  Injection-recovery: phase-randomized surrogates + injected exponential dips
        -> sensitivity floor (detection efficiency vs amplitude)

Outputs: precursor_search.py (this), precursor_search_note.md, PNGs.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = np.load("crab_monthly.npz")
MJD, NU, SNU = D["mjd"], D["nu"], D["s_nu"]  # s_nu in Hz
NUDOT = D["nudot"]

# Crab glitch epochs (MJD) from JB glitch catalogue gTable.html, B0531+21
GLITCHES = np.array([
    40491.80, 41161.98, 41250.32, 42447.26, 46663.69, 47767.50, 48945.60,
    50020.04, 50260.03, 50458.94, 50489.70, 50812.59, 51452.02, 51740.66,
    51804.75, 52084.07, 52146.76, 52498.26, 52587.20, 53067.08, 53254.11,
    53331.17, 53970.19, 54580.38, 55875.49, 57839.80, 58064.56, 58237.36,
    58470.70, 58687.57, 60872.90, 60893.90])
DF = np.array([7.2, 1.9, 2.1, 35.7, 6, 81.0, 4.2, 2.1, 31.9, 6.1, 0.8, 6.2,
               6.8, 25.1, 3.5, 22.6, 8.9, 3.4, 1.7, 214, 4.9, 2.8, 21.8, 4.7,
               39, 2.2, 516.37, 4.08, 2.3, 31.7, 2.33, 4.53]) * 1e-9  # dF/F

T0, T1 = MJD[0], MJD[-1]
G = GLITCHES[(GLITCHES > T0 + 30) & (GLITCHES < T1 - 60)]
print(f"glitches in ephemeris span: {len(G)}")

REF = (-360.0, -60.0)     # reference fit window (days rel glitch)
PROBE = (-60.0, 30.0)     # probe window
STEPWIN = (-210.0, -30.0)  # forerunner search window
MINPTS = 8
SIGNU_MAX = 30e-9          # downweight noisier points


def wlinfit(t, y, w):
    """Inverse-variance linear fit; returns (a, b, cov)."""
    W = np.diag(w)
    X = np.column_stack([np.ones_like(t), t])
    XtWX = X.T @ W @ X
    try:
        cov = np.linalg.inv(XtWX)
    except np.linalg.LinAlgError:
        return None
    beta = cov @ X.T @ W @ y
    return beta[0], beta[1], cov


def detrend(tg):
    """Fit reference trend before epoch tg; return residual interpolator data.

    Returns dict with probe times/residuals/weights, or None if insufficient data.
    """
    m = (MJD >= tg + REF[0]) & (MJD <= tg + REF[1]) & (SNU < SIGNU_MAX)
    t, y, w = MJD[m] - tg, NU[m], 1.0 / SNU[m] ** 2
    if len(t) < MINPTS:
        return None
    fit = wlinfit(t, y, w)
    if fit is None:
        return None
    a, b, cov = fit
    mp = (MJD >= tg + PROBE[0]) & (MJD <= tg + PROBE[1]) & (SNU < SIGNU_MAX)
    tp, yp, wp = MJD[mp] - tg, NU[mp], 1.0 / SNU[mp] ** 2
    if len(tp) < 3:
        return None
    r = yp - (a + b * tp)
    # residual variance incl. trend uncertainty
    Xp = np.column_stack([np.ones_like(tp), tp])
    var = 1.0 / wp + np.einsum("ij,jk,ik->i", Xp, cov, Xp)
    return dict(t=tp, r=r, var=var, w=1.0 / var, a=a, b=b)


def clean_stretch(tg):
    """Largest [lo,hi] with [t-360, t+60] glitch-free for t in it (null epochs)."""
    prev = GLITCHES[GLITCHES < tg - 1]
    nxt = GLITCHES[GLITCHES > tg + 1]
    lo = (prev[-1] + 420) if len(prev) else T0 + 400
    hi = (nxt[0] - 420) if len(nxt) else T1 - 100
    lo = max(lo, T0 + 400)
    hi = min(hi, T1 - 100)
    return (lo, hi) if hi > lo else None


def stat_A(dd):
    """Stacked weighted-mean residual in [-60,0] d. dd: list of detrend dicts."""
    ds, vs = [], []
    for d in dd:
        m = (d["t"] >= -60) & (d["t"] < 0)
        if m.sum() == 0:
            return None
        w = d["w"][m]
        ds.append(np.sum(w * d["r"][m]) / np.sum(w))
        vs.append(1.0 / np.sum(w))
    ds, vs = np.array(ds), np.array(vs)
    W = 1.0 / vs
    Dstack = np.sum(W * ds) / np.sum(W)
    return Dstack, ds, np.sqrt(vs)


def step_stat(tg):
    """Max positive-step z-score in STEPWIN before tg."""
    m = (MJD >= tg + STEPWIN[0] - 120) & (MJD <= tg + STEPWIN[1] + 120) & (SNU < SIGNU_MAX)
    t, y, w = MJD[m] - tg, NU[m], 1.0 / SNU[m] ** 2
    if len(t) < 8:
        return np.nan, np.nan
    best, best_t = -np.inf, np.nan
    cands = t[(t >= STEPWIN[0]) & (t <= STEPWIN[1])]
    for tc in cands:
        mb = (t >= tc - 110) & (t < tc - 20)
        ma = (t > tc + 20) & (t <= tc + 110)
        if mb.sum() < 2 or ma.sum() < 2:
            continue
        mu_b = np.sum(w[mb] * y[mb]) / np.sum(w[mb])
        mu_a = np.sum(w[ma] * y[ma]) / np.sum(w[ma])
        se = np.sqrt(1 / np.sum(w[mb]) + 1 / np.sum(w[ma]))
        z = (mu_a - mu_b) / se
        if z > best:
            best, best_t = z, tc
    return best, best_t


def rms_pre_post(tg):
    """RMS of detrended residuals pre [-400,-30] vs post [+30,+400] d."""
    d = detrend(tg)
    if d is None:
        return None
    # extend probe for RMS: recompute residuals on wider window
    m = (MJD >= tg - 400) & (MJD <= tg + 400) & (SNU < SIGNU_MAX)
    t, y, w = MJD[m] - tg, NU[m], 1.0 / SNU[m] ** 2
    r = y - (d["a"] + d["b"] * t)
    pre = r[(t >= -400) & (t < -30)]
    post = r[(t > 30) & (t <= 400)]
    if len(pre) < 5 or len(post) < 5:
        return None
    return np.std(pre), np.std(post)


# ---- select glitches usable for the stacked search ----
usable = []
for tg in G:
    dd = detrend(tg)
    cs = clean_stretch(tg)
    if dd is not None and cs is not None:
        usable.append(tg)
usable = np.array(usable)
print(f"usable glitches (clean ref + null stretch): {len(usable)}")
print("MJDs:", np.round(usable, 1))

rng = np.random.default_rng(0)
N_SURR = 2000

# ---- Test A ----
dd_real = [detrend(tg) for tg in usable]
A_real, A_di, A_si = stat_A(dd_real)
print(f"\nTest A: stacked pre-glitch [-60,0]d residual = {A_real*1e9:.2f} nHz")
print("per-glitch d_i (nHz):", np.round(A_di * 1e9, 1))

A_null = []
for _ in range(N_SURR):
    dd_s = []
    for tg in usable:
        lo, hi = clean_stretch(tg)
        tprime = rng.uniform(lo, hi)
        dd_s.append(detrend(tprime))
    s, _, _ = stat_A(dd_s)
    A_null.append(s)
A_null = np.array(A_null)
p_A = (np.sum(A_null <= A_real) + 1) / (N_SURR + 1)  # one-sided: dip = negative
print(f"Test A: null median={np.median(A_null)*1e9:.2f} nHz, "
      f"null 0.5%={np.percentile(A_null,0.5)*1e9:.2f} nHz, p(one-sided dip)={p_A:.4f}")

# ---- Test B ----
B_real_z, B_real_t = np.array([step_stat(tg) for tg in usable]).T
B_real = np.nanmean(B_real_z)
print(f"\nTest B: mean max forerunner-step z = {B_real:.2f}")
print("per-glitch (z, t_rel_d):", [(round(z,1), round(t,0)) for z, t in zip(B_real_z, B_real_t)])
B_null = []
for _ in range(N_SURR):
    zs = []
    for tg in usable:
        lo, hi = clean_stretch(tg)
        tprime = rng.uniform(lo, hi)
        z, _ = step_stat(tprime)
        zs.append(z)
    B_null.append(np.nanmean(zs))
B_null = np.array(B_null)
p_B = (np.sum(B_null >= B_real) + 1) / (N_SURR + 1)
print(f"Test B: null 99.5%={np.percentile(B_null,99.5):.2f}, p={p_B:.4f}")

# ---- Test C: pre vs post RMS ----
pairs = []
for tg in usable:
    rp = rms_pre_post(tg)
    if rp is not None:
        pairs.append(rp)
pairs = np.array(pairs)
pre, post = pairs[:, 0], pairs[:, 1]
n_pos = np.sum(pre > post)
from math import comb
p_C = sum(comb(len(pairs), k) for k in range(n_pos, len(pairs)+1)) / 2**len(pairs)
print(f"\nTest C: {n_pos}/{len(pairs)} glitches have pre-RMS > post-RMS; "
      f"median pre={np.median(pre)*1e9:.1f} nHz post={np.median(post)*1e9:.1f} nHz; "
      f"sign-test p={p_C:.4f}")

# ---- Positive control: recover the glitches themselves ----
print("\nPositive control: step z at catalogued glitch epochs (should be huge for big ones)")
for tg, df in zip(GLITCHES, DF):
    if tg < T0 or tg > T1:
        continue
    z, _ = step_stat(tg + 105)  # search window [-105,+75]d rel glitch
    print(f"  MJD {tg:.0f} dF/F={df*1e9:.1f}e-9 -> max step z in [-105,+75]d = {z:.1f}")
