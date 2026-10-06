"""
Synthetic injection-recovery test of the blind-spot-free calibrator-differential
transient statistic (round 2 of the Kerr/CS polarimetry thread).  v2: fixed
significance calibration (empirical FPR thresholds), fixed jump amplitudes,
normalized statistic for estimation.

Tests the claims of blindspot_free_observable_note.md:
  C1: new statistic has no detection blind spot at gamma=k/12 (old one does)
  C2: synchronized all-station R-L jump degeneracy broken by R(t)=Q_tgt/Q_cal
  C3: blind spot returns when the ramp is unresolved (dt >> tau)
  C4: practical mod-1/12 estimation ambiguity appears at low S/N
  C5: parameter recovery accuracy (gamma, t0)
  C6: calibrator-interpolation residuals for intra-scan jumps (residual floor)

Signal model (per note Sec. 1-4):
  Q(t) = S^RL . conj(S^LR)
  slip:  Q_tgt -> Q_tgt . exp(-12 i dchi(t)), dchi = pi*gamma*[1+tanh((t-t0)/tau)]
  jump:  Q     -> Q     . exp(+6 i delta(t))   (target AND calibrator)
  R(t) = Q_tgt(t)/Q_cal(t_tilde);  r(t) = R(t+dt).conj(R(t))
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TAU = 46.9
OUT = {}

# ---------------------------------------------------------------- physics ---
def slip_factor(t, gamma, t0, tau=TAU):
    dchi = np.pi * gamma * (1.0 + np.tanh((t - t0) / tau))
    return np.exp(-12j * dchi)

def jump_factor(t, t1, delta0):
    return np.exp(6j * delta0 * (t >= t1))

def template_u(tm, dt, gamma_t, t0, tau=TAU):
    dphi = (-12.0 * np.pi * gamma_t
            * (np.tanh((tm + dt - t0) / tau) - np.tanh((tm - t0) / tau)))
    return np.exp(1j * dphi) - 1.0

# ------------------------------------------------------------- data gen -----
def gen_series(t, gamma, t0, delta0, t1, sig_t, sig_c,
               cal_mode="ideal", cal_cad=300.0, scan_len=60.0, seed=0):
    rng = np.random.default_rng(seed)
    phi_t = 0.20 * np.sin(2 * np.pi * t / 900.0)
    phi_c = 0.15 * np.sin(2 * np.pi * t / 700.0 + 1.0)
    Qt = (np.exp(1j * phi_t) * slip_factor(t, gamma, t0)
          * jump_factor(t, t1, delta0))
    Qt = Qt + (rng.normal(size=t.shape) + 1j * rng.normal(size=t.shape)) * sig_t / np.sqrt(2)
    Qc_true = 2.0 * np.exp(1j * phi_c) * jump_factor(t, t1, delta0)
    Qc_obs = (Qc_true + (rng.normal(size=t.shape) + 1j * rng.normal(size=t.shape))
              * sig_c / np.sqrt(2))
    if cal_mode == "ideal":
        Qc_t = Qc_obs
    else:
        scan = (np.mod(t, cal_cad) < scan_len)
        Qc_t = np.empty_like(Qc_obs)
        Qc_t.real = np.interp(t, t[scan], Qc_obs[scan].real)
        Qc_t.imag = np.interp(t, t[scan], Qc_obs[scan].imag)
    R = Qt / Qc_t
    r = R[1:] * np.conj(R[:-1])
    tm = 0.5 * (t[1:] + t[:-1])
    return r, tm, Qt, R

# ------------------------------------------------------------- statistics ---
def build_U(tm, dt, ggrid, t0grid, tau=TAU):
    U = np.empty((len(ggrid), len(t0grid), len(tm)), dtype=complex)
    for i, g in enumerate(ggrid):
        for j, tt in enumerate(t0grid):
            U[i, j] = template_u(tm, dt, g, tt, tau)
    return U

def zmax_new(r, U):
    """Unnormalized max-over-grid detection statistic (for detection vs null)."""
    d = r - 1.0
    Z = np.abs(np.einsum("t,ijt->ij", d, np.conj(U)))
    return Z.max(), Z

def zgrid_norm(r, U):
    """Template-energy-normalized grid (for parameter estimation)."""
    d = r - 1.0
    num = np.abs(np.einsum("t,ijt->ij", d, np.conj(U)))
    den = np.sqrt(np.einsum("ijt,ijt->ij", U, np.conj(U)))
    return num / np.maximum(den, 1e-30)

def old_oracle(Qt, t, tevent, tau=TAU, t_excl_after=np.inf):
    """Asymptotic endpoint step at the known event time, ramp excluded.

    This is the note's Eq. 4 statistic: |<Q>_post - <Q>_pre|/|<Q>_pre| with
    pre = t < tevent-3tau, post = tevent+3tau < t < t_excl_after.
    Exactly 2|sin(12 pi gamma)| for a slip (blind at k/12)."""
    pre = Qt[t < tevent - 3*tau]
    post = Qt[(t > tevent + 3*tau) & (t < t_excl_after)]
    if len(pre) < 3 or len(post) < 3:
        return 0.0
    return abs(post.mean() - pre.mean()) / abs(pre.mean())

def old_free(Qt, t, t0grid):
    """Free-t0 step search (what a naive pipeline step-search does)."""
    best = 0.0
    for tt in t0grid:
        pre = Qt[t < tt]; post = Qt[t >= tt]
        if len(pre) < 5 or len(post) < 5:
            continue
        step = abs(post.mean() - pre.mean()) / abs(pre.mean())
        best = max(best, step)
    return best

def det_stats(vals, null):
    """Detection fraction at empirical FPR 1% / 0.1%, and median margin."""
    q99 = np.quantile(null, 0.99); q999 = np.quantile(null, 0.999)
    return (float(np.mean(vals > q99)), float(np.mean(vals > q999)),
            float(np.median(vals) / q99))

# ------------------------------------------------------------- experiment A --
print("=== Exp A: detection significance vs gamma (old vs new) ===", flush=True)
dt = 10.0
t = np.arange(-600.0, 600.0 + dt, dt)
t0grid = np.arange(-200.0, 201.0, 20.0)
ggrid = np.arange(0.02, 0.42, 0.02)
gammas = [0.0, 1/48, 1/24, 1/12, 0.15, 1/6, 1/4, 1/3]
M, MNULL = 120, 3000
sig_t, sig_c = 0.05, 0.025

r0, tm0, _, _ = gen_series(t, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c, seed=7)
U0 = build_U(tm0, dt, ggrid, t0grid)
zn_null = np.empty(MNULL); zo_null = np.empty(MNULL); zof_null = np.empty(MNULL)
for k in range(MNULL):
    r, tm, Qt, _ = gen_series(t, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c, seed=1000 + k)
    zn_null[k], _ = zmax_new(r, U0)
    zo_null[k] = old_oracle(Qt, t, 0.0)
    zof_null[k] = old_free(Qt, t, t0grid)

resA = []
for g in gammas:
    zn = np.empty(M); zo = np.empty(M); zof = np.empty(M)
    for k in range(M):
        r, tm, Qt, _ = gen_series(t, g, 0.0, 0.0, 1e9, sig_t, sig_c, seed=2000 + k)
        zn[k], _ = zmax_new(r, U0)
        zo[k] = old_oracle(Qt, t, 0.0)
        zof[k] = old_free(Qt, t, t0grid)
    dn1, dn01, mn = det_stats(zn, zn_null)
    do1, do01, mo = det_stats(zo, zo_null)
    df1, _, _ = det_stats(zof, zof_null)
    resA.append(dict(gamma=g, new_det1=dn1, new_det01=dn01, new_margin=mn,
                     old_det1=do1, old_det01=do01, old_margin=mo,
                     oldfree_det1=df1))
    print(f"  gamma={g:7.4f}  new: det@1%={dn1:.2f} det@0.1%={dn01:.2f} margin={mn:5.1f}   "
          f"old(oracle): det@1%={do1:.2f} margin={mo:5.1f}   old(free-t0): det@1%={df1:.2f}",
          flush=True)
OUT["expA"] = resA

# ------------------------------------------------------------- experiment B --
print("=== Exp B: synchronized R-L jump confounder ===", flush=True)
# delta chosen so the jump makes a REAL step in Q: |e^{6id}-1| = 2|sin 3d|
deltas = [np.pi/24, np.pi/12, np.pi/6, np.pi/4]
resB = []
for d0 in deltas:
    zn = np.empty(M); zo = np.empty(M)
    for k in range(M):
        r, tm, Qt, _ = gen_series(t, 0.0, 0.0, d0, 300.0, sig_t, sig_c,
                                 seed=3000 + k)
        zn[k], _ = zmax_new(r, U0)
        zo[k] = old_oracle(Qt, t, 300.0)
    dn1, dn01, mn = det_stats(zn, zn_null)
    do1, do01, mo = det_stats(zo, zo_null)
    resB.append(dict(delta=float(d0), new_det1=dn1, new_det01=dn01,
                     old_det1=do1, old_det01=do01))
    print(f"  delta={d0:6.4f} (|step|={2*abs(np.sin(3*d0)):.2f})  new: det@1%={dn1:.2f} "
          f"old: det@1%={do1:.2f} (false alarm)", flush=True)
OUT["expB"] = resB

print("  slip(1/12)+jump(pi/6):", flush=True)
zn = np.empty(M); zo = np.empty(M); zo0 = np.empty(M)
for k in range(M):
    r, tm, Qt, _ = gen_series(t, 1/12, 0.0, np.pi/6, 300.0, sig_t, sig_c,
                             seed=4000 + k)
    zn[k], _ = zmax_new(r, U0)
    zo[k] = old_oracle(Qt, t, 0.0, t_excl_after=290.0)  # slip window only
    # matched null: same windowing, no slip, no jump
    _, _, Qt0, _ = gen_series(t, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c, seed=4100 + k)
    zo0[k] = old_oracle(Qt0, t, 0.0, t_excl_after=290.0)
dn1, dn01, mn = det_stats(zn, zn_null)
do1, do01, mo = det_stats(zo, zo0)
print(f"    new: det@1%={dn1:.2f} margin={mn:.1f}   old(slip-window): det@1%={do1:.2f} margin={mo:.1f}", flush=True)
OUT["expB_slip_plus_jump"] = dict(new_det1=dn1, new_margin=mn, old_det1=do1, old_margin=mo)

# ------------------------------------------------------------- experiment C --
print("=== Exp C: unresolved ramp (dt >> tau) ===", flush=True)
resC = []
for dti in [10.0, 20.0, 50.0, 100.0, 200.0]:
    ti = np.arange(-600.0, 600.0 + dti, dti)
    r0i, tmi0, _, _ = gen_series(ti, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c, seed=7)
    Ui = build_U(tmi0, dti, ggrid, t0grid)
    zn = np.empty(M); znn = np.empty(1000)
    for k in range(M):
        r, tmi, _, _ = gen_series(ti, 1/12, 0.0, 0.0, 1e9, sig_t, sig_c,
                                 seed=5000 + k)
        zn[k], _ = zmax_new(r, Ui)
    for k in range(1000):
        r, tmi, _, _ = gen_series(ti, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c,
                                 seed=6000 + k)
        znn[k], _ = zmax_new(r, Ui)
    dn1, dn01, mn = det_stats(zn, znn)
    resC.append(dict(dt=dti, dt_over_tau=dti/TAU, new_det1=dn1, new_det01=dn01,
                     new_margin=mn))
    print(f"  dt={dti:6.1f}s (dt/tau={dti/TAU:4.2f}): det@1%={dn1:.2f} margin={mn:5.1f}", flush=True)
OUT["expC"] = resC

# Exp C2: unresolved regime is a sample-phase lottery. dt=200 s fixed, random
# grid offsets: does the blind spot return for some phasings but not others?
print("=== Exp C2: dt=200 s, sample-phase lottery ===", flush=True)
dti = 200.0
resC2 = []
for off in [0.0, 50.0, 100.0, 150.0]:
    ti = off + np.arange(-600.0, 600.0 + dti, dti)
    r0i, tmi0, _, _ = gen_series(ti, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c, seed=7)
    Ui = build_U(tmi0, dti, ggrid, t0grid)
    zn = np.empty(60); znn = np.empty(300)
    for k in range(60):
        r, tmi, _, _ = gen_series(ti, 1/12, 0.0, 0.0, 1e9, sig_t, sig_c,
                                 seed=6500 + k)
        zn[k], _ = zmax_new(r, Ui)
    for k in range(300):
        r, tmi, _, _ = gen_series(ti, 0.0, 0.0, 0.0, 1e9, sig_t, sig_c,
                                 seed=6800 + k)
        znn[k], _ = zmax_new(r, Ui)
    dn1, _, mn = det_stats(zn, znn)
    resC2.append(dict(offset=off, new_det1=dn1, new_margin=mn))
    print(f"  offset={off:5.0f}s: det@1%={dn1:.2f} margin={mn:5.1f}", flush=True)
OUT["expC2"] = resC2

# ------------------------------------------------------------- experiment D --
print("=== Exp D: calibrator interpolation residuals ===", flush=True)
resD = []
for cad in [120.0, 300.0, 600.0]:
    for t1, tag in [(cad/2, "mid-gap"), (30.0, "in-scan")]:
        zn = np.empty(M); resid = np.empty(M)
        for k in range(M):
            r, tm, Qt, R = gen_series(t, 0.0, 0.0, np.pi/6, t1, sig_t, sig_c,
                                     cal_mode="interleaved", cal_cad=cad,
                                     seed=7000 + k)
            zn[k], _ = zmax_new(r, U0)
            # residual step in R(t) across the jump, vs full jump step
            wpre = R[(t > t1 - 120) & (t < t1 - 10)]
            wpost = R[(t > t1 + 10) & (t < t1 + 120)]
            resid[k] = abs(wpost.mean() - wpre.mean()) / abs(wpre.mean())
        dn1, dn01, _ = det_stats(zn, zn_null)
        full = 2*abs(np.sin(3*np.pi/6))
        resD.append(dict(cal_cad=cad, jump_t1=t1, tag=tag,
                         spurious_det1=float(dn1),
                         resid_step=float(np.median(resid)),
                         suppression=float(full/np.median(resid))))
        print(f"  cad={cad:5.0f}s jump {tag}: spurious det@1%={dn1:.2f}  "
              f"resid step={np.median(resid):.4f} (full={full:.2f}, "
              f"suppression x{full/np.median(resid):.0f})", flush=True)
OUT["expD"] = resD
zn = np.empty(M)
for k in range(M):
    r, tm, Qt, _ = gen_series(t, 1/12, 0.0, 0.0, 1e9, sig_t, sig_c,
                             cal_mode="interleaved", seed=8000 + k)
    zn[k], _ = zmax_new(r, U0)
dn1, dn01, mn = det_stats(zn, zn_null)
print(f"  slip 1/12, interleaved cal, no jump: det@1%={dn1:.2f} margin={mn:.1f}", flush=True)
OUT["expD_slip_interleaved"] = dict(new_det1=dn1, new_margin=mn)

# ------------------------------------------------------------- experiment E --
# Least-squares estimator: chi2(gt,t0) = sum|d - u(gt,t0)|^2  <=>  maximize
#   obj = 2*Re[sum d conj(u)] - sum|u|^2.  Unlike the normalized matched filter
# (which discards amplitude and is flat in the linear regime), this uses both
# amplitude and nonlinear shape.
print("=== Exp E: mod-1/12 estimation ambiguity vs S/N (LS estimator) ===", flush=True)
gprof = np.arange(0.01, 0.35, 0.01)
Up = build_U(tm0, dt, gprof, t0grid)
UU = np.einsum("ijt,ijt->ij", Up, np.conj(Up)).real

def ls_fit(r, Up, UU, gprof, t0grid):
    d = r - 1.0
    cross = np.einsum("t,ijt->ij", d, np.conj(Up))
    obj = 2 * cross.real - UU
    ii, jj = np.unravel_index(obj.argmax(), obj.shape)
    return gprof[ii], t0grid[jj], obj

# shape correlation between gamma and gamma+1/12 templates (note's 99.7% claim)
a = (template_u(tm0, dt, 1/12, 0.0) - 1.0)
b = (template_u(tm0, dt, 1/6, 0.0) - 1.0)
ac = a - a.mean(); bc = b - b.mean()
shape_corr = abs(np.sum(ac * np.conj(bc))) / np.sqrt(np.sum(abs(ac)**2) * np.sum(abs(bc)**2))
print(f"  mean-subtracted shape corr(s_1/12, s_1/6) = {shape_corr:.4f}", flush=True)
OUT["expE_shape_corr"] = float(shape_corr)

resE = []
for s in [0.02, 0.05, 0.1, 0.2, 0.4]:
    n_true = n_plus = n_other = 0
    for k in range(80):
        r, tm, Qt, _ = gen_series(t, 1/12, 0.0, 0.0, 1e9, s, s/2, seed=9000 + k)
        gh, th, _ = ls_fit(r, Up, UU, gprof, t0grid)
        if abs(gh - 1/12) < 0.03:
            n_true += 1
        elif abs(gh - 1/6) < 0.03:
            n_plus += 1
        else:
            n_other += 1
    resE.append(dict(sig=s, frac_true=n_true/80, frac_plus=n_plus/80,
                     frac_other=n_other/80))
    print(f"  sig={s:.2f}: LS picks 1/12: {n_true/80:.2f}, picks 1/6 (alias): {n_plus/80:.2f}, "
          f"other: {n_other/80:.2f}", flush=True)
OUT["expE"] = resE

# Exp E2: phase-unwrapping estimator (note's "lifted in principle" claim).
# Sum the per-sample phase INCREMENTS (cumsum, not last-minus-first):
# gamma = -sum(delta_Phi) / 24pi, valid while |delta_Phi| < pi per sample.
print("=== Exp E2: unwrapping (cumsum) estimator ===", flush=True)
resE2 = []
for s in [0.01, 0.05, 0.1, 0.2, 0.4]:
    gh = np.empty(80)
    for k in range(80):
        r, tm, Qt, _ = gen_series(t, 1/12, 0.0, 0.0, 1e9, s, s/2, seed=9200 + k)
        win = (tm > -3*TAU) & (tm < 3*TAU)
        total = np.sum(np.angle(r[win]))  # increments already in (-pi, pi]
        gh[k] = -total / (24 * np.pi * np.tanh(3.0))
    ok = np.mean(abs(gh - 1/12) < 0.1 * (1/12))
    resE2.append(dict(sig=s, gamma_hat_mean=float(gh.mean()),
                      gamma_hat_std=float(gh.std()), frac_ok=float(ok)))
    print(f"  sig={s:.2f}: cumsum gamma_hat={gh.mean():.4f}±{gh.std():.4f} "
          f"(true 0.0833, within-10% frac={ok:.2f})", flush=True)
OUT["expE2"] = resE2

# Exp E3: alias robustness at larger true gamma (amplitude ratio -> 1) and
# higher noise: true gamma=0.25, alias 1/3.
print("=== Exp E3: LS alias test, true gamma=0.25 ===", flush=True)
resE3 = []
for s in [0.2, 0.4, 0.8]:
    n_true = n_plus = n_other = 0
    for k in range(80):
        r, tm, Qt, _ = gen_series(t, 0.25, 0.0, 0.0, 1e9, s, s/2, seed=9300 + k)
        gh, th, _ = ls_fit(r, Up, UU, gprof, t0grid)
        if abs(gh - 0.25) < 0.03:
            n_true += 1
        elif abs(gh - 1/3) < 0.03:
            n_plus += 1
        else:
            n_other += 1
    resE3.append(dict(sig=s, frac_true=n_true/80, frac_plus=n_plus/80,
                      frac_other=n_other/80))
    print(f"  sig={s:.2f}: LS picks 0.25: {n_true/80:.2f}, picks 1/3 (alias): {n_plus/80:.2f}, "
          f"other: {n_other/80:.2f}", flush=True)
OUT["expE3"] = resE3

# ------------------------------------------------------------- experiment F --
print("=== Exp F: parameter recovery at high S/N (LS estimator) ===", flush=True)
resF = []
for gtrue in [1/12, 0.15]:
    gh = np.empty(80); th = np.empty(80)
    for k in range(80):
        r, tm, Qt, _ = gen_series(t, gtrue, 40.0, 0.0, 1e9, 0.05, 0.025,
                                 seed=9500 + k)
        gh[k], th[k], _ = ls_fit(r, Up, UU, gprof, t0grid)
    resF.append(dict(gamma_true=gtrue, gamma_hat_mean=float(gh.mean()),
                     gamma_hat_std=float(gh.std()),
                     frac_near_true=float(np.mean(abs(gh-gtrue) < 0.03)),
                     frac_near_alias=float(np.mean(abs(gh-(gtrue+1/12)) < 0.03)),
                     t0_hat_mean=float(th.mean()), t0_hat_std=float(th.std())))
    print(f"  gamma={gtrue:.4f}, t0=40: gamma_hat={gh.mean():.4f}±{gh.std():.4f} "
          f"(near-true {np.mean(abs(gh-gtrue)<0.03):.2f}, near-alias {np.mean(abs(gh-(gtrue+1/12))<0.03):.2f})  "
          f"t0_hat={th.mean():.1f}±{th.std():.1f}", flush=True)
OUT["expF"] = resF

with open("synth_results.json", "w") as f:
    json.dump(OUT, f, indent=1)
print("wrote synth_results.json", flush=True)

# ------------------------------------------------------------------ plots ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
g = [r["gamma"] for r in resA]
ax.plot(g, [r["new_det1"] for r in resA], "o-", label="new: R(t) matched filter")
ax.plot(g, [r["old_det1"] for r in resA], "s--", label="old: asymptotic step (oracle t0)")
ax.plot(g, [r["oldfree_det1"] for r in resA], "^:", label="old: free-t0 step search", alpha=0.7)
for kk in [1, 2, 3, 4]:
    ax.axvline(kk/12, color="k", ls=":", alpha=0.4)
ax.set_xlabel("injected γ"); ax.set_ylabel("detection fraction @ FPR=1%")
ax.set_title("A: detection vs γ — old blind at k/12, new is not")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
ax.plot(g, [r["new_margin"] for r in resA], "o-", label="new")
ax.plot(g, [r["old_margin"] for r in resA], "s--", label="old")
for kk in [1, 2, 3, 4]:
    ax.axvline(kk/12, color="k", ls=":", alpha=0.4)
ax.set_xlabel("injected γ"); ax.set_ylabel("median Z / null 99th pct")
ax.set_title("A: detection margin vs γ")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("synth_figA.png", dpi=110)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
dd = [r["delta"] for r in resB]
ax.plot(dd, [r["old_det1"] for r in resB], "s--", label="old (false alarm)")
ax.plot(dd, [r["new_det1"] for r in resB], "o-", label="new (silent)")
ax.set_xlabel("jump amplitude δ (rad)"); ax.set_ylabel("detection fraction @ FPR=1%")
ax.set_title("B: jump-only injection — old fires, new silent")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
dc = [r["dt_over_tau"] for r in resC]
ax.semilogx(dc, [r["new_det1"] for r in resC], "o-")
ax.axvline(1.0, color="k", ls=":", alpha=0.5, label="Δt = τ")
ax.set_xlabel("Δt/τ"); ax.set_ylabel("new-stat detection fraction @ FPR=1%, γ=1/12")
ax.set_title("C: blind spot returns when ramp unresolved")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
fig.tight_layout(); fig.savefig("synth_figBC.png", dpi=110)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
ss = [r["sig"] for r in resE]
ax.semilogx(ss, [r["frac_true"] for r in resE], "o-", label="picks γ=1/12")
ax.semilogx(ss, [r["frac_plus"] for r in resE], "s--", label="picks γ=1/6 (alias)")
ax.semilogx(ss, [r["frac_other"] for r in resE], "^-.", label="other")
ax.set_xlabel("per-sample fractional noise σ"); ax.set_ylabel("fraction of realizations")
ax.set_title("E: mod-1/12 alias takes over at low S/N")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
for s, ls in [(0.02, "-"), (0.4, "--")]:
    objs = []
    for k in range(40):
        r, tm, Qt, _ = gen_series(t, 1/12, 0.0, 0.0, 1e9, s, s/2, seed=9900 + k)
        _, _, obj = ls_fit(r, Up, UU, gprof, t0grid)
        j0 = obj.argmax(axis=1)
        objs.append(obj[np.arange(len(gprof)), j0])
    P = np.mean(objs, axis=0); P = (P - P.min()) / (P.max() - P.min())
    ax.plot(gprof, P, ls, label=f"σ={s}")
ax.axvline(1/12, color="k", ls=":", alpha=0.5); ax.axvline(1/6, color="k", ls=":", alpha=0.5)
ax.set_xlabel("template γ"); ax.set_ylabel("normalized <LS objective>")
ax.set_title("E: LS(γ) profile — twin peaks at γ, γ+1/12 at low S/N")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("synth_figE.png", dpi=110)
print("figures written", flush=True)
