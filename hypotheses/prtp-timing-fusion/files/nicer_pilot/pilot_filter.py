"""PRTP NICER pilot: clock injection + causal filter + G2/G3 verdict.

Pipeline:
  dwells.csv -> quality cuts -> per-pulsar unwrapped residuals (s)
  -> 0.25-d bins (weighted mean, combined sigma, mask)
  -> qred per pulsar (common-mode-cleaned scalar ML + global LL scale)
  -> inject known DSAC-class clock (true qf) -> causal Kalman (tv extension
     of round5.kalman_masked: diagonal time-varying R, per-pulsar qred)
  -> G2: pilot clock RMS vs matched-sim RMS (same grid/mask/white/qred)
  -> G3: vs holdover; gap-crossing smoothness
Saves pilot_filter.json + figures.
"""
import sys, os, json, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/hatch/workspace/prtp')
from simulate import calibrate_clock_qf, DSAC_ADEV_1D

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
PSRS = ['J0437-4715', 'J0030+0451', 'J0218+4232', 'B1821-24']
BIN_D = 0.25
SPAN = (58300.0, 59030.0)
Q = dict(min_n=50, min_exp=300.0, min_htest=20.0)
SEED = 777


def kalman_masked_tv(t, y, mask, Rdiag, qf, qred, return_ll=False):
    """Minimal generalization of round5.kalman_masked for the pilot's
    irregular data: Rdiag (n, npsr) per-epoch white variance (diagonal),
    qred (npsr,) per-pulsar red PSD. State space, F, Q, H, and the
    predict/update equations are unchanged from the audited code."""
    n, npsr = y.shape
    d = 3 + npsr
    dt = float(np.median(np.diff(t)))
    F = np.eye(d)
    F[0, 1] = dt
    F[0, 2] = 0.5 * dt ** 2
    F[1, 2] = dt
    qd = 1e-52
    qred = np.atleast_1d(np.asarray(qred, dtype=float))
    Q = np.diag([0.0, qf * dt, qd * dt] + list(qred * dt))
    Hfull = np.zeros((npsr, d))
    Hfull[:, 0] = 1.0
    for i in range(npsr):
        Hfull[i, 3 + i] = 1.0
    x = np.zeros(d)
    P = np.diag([1e-6, 1e-18, 1e-30] + [1e-12] * npsr)
    I = np.eye(d)
    out = np.zeros(n)
    ll = 0.0
    for k in range(n):
        if k > 0:
            x = F @ x
            P = F @ P @ F.T + Q
        obs = np.where(mask[k])[0]
        if len(obs):
            H = Hfull[obs]
            Rk = np.diag(Rdiag[k][obs])
            nu = y[k, obs] - H @ x
            S = H @ P @ H.T + Rk
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ nu
            P = (I - K @ H) @ P
            if return_ll:
                sgn, ld = np.linalg.slogdet(S)
                ll += -0.5 * (sgn * ld + nu @ np.linalg.solve(S, nu)
                              + len(obs) * np.log(2 * np.pi))
        out[k] = x[0]
    return (out, ll) if return_ll else out


def load_residuals():
    """Per-pulsar unwrapped residual series in seconds (mean-subtracted)."""
    import glob
    files = sorted(glob.glob(PILOT + '/dwells_*.csv'))
    assert files, 'no dwells_*.csv found; run pilot_pass2.py first'
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df[(df['n_phot'] >= Q['min_n']) & (df['exp_s'] >= Q['min_exp'])
            & (df['htest'] >= Q['min_htest'])
            & np.isfinite(df['dphi']) & np.isfinite(df['sigma_dphi'])].copy()
    series = {}
    for psr in PSRS:
        d = df[df['psr'] == psr].sort_values('mjd_mid')
        if len(d) < 10:
            continue
        ph = np.unwrap(d['dphi'].values * 2 * np.pi) / (2 * np.pi)
        sig = d['sigma_dphi'].values * d['P0_s'].values
        w = 1 / sig ** 2
        r = (ph - np.average(ph, weights=w)) * d['P0_s'].values
        series[psr] = dict(mjd=d['mjd_mid'].values, r=r, sig=sig)
    return series


def regrid(series):
    """0.25-d bins: weighted-mean residual, combined sigma, mask."""
    t0, t1 = SPAN
    tb = t0 + (np.arange(int((t1 - t0) / BIN_D)) + 0.5) * BIN_D
    n = len(tb)
    npsr = len(PSRS)
    y = np.full((n, npsr), np.nan)
    Rdiag = np.full((n, npsr), np.nan)
    mask = np.zeros((n, npsr), bool)
    for i, psr in enumerate(PSRS):
        if psr not in series:
            continue
        s = series[psr]
        b = ((s['mjd'] - t0) / BIN_D).astype(int)
        for bb in np.unique(b[(b >= 0) & (b < n)]):
            m = b == bb
            w = 1 / s['sig'][m] ** 2
            y[bb, i] = np.sum(w * s['r'][m]) / np.sum(w)
            Rdiag[bb, i] = 1 / np.sum(w)
            mask[bb, i] = True
    t = (tb - t0) * 86400.0  # seconds
    return t, tb, y, Rdiag, mask


def estimate_qred(t, y, Rdiag, mask):
    """Per-pulsar red PSD: (1) method-of-moments on first differences
    (RW+white: Var(d_k) = q*dt_k + sig_k^2 + sig_{k-1}^2; handles irregular
    sampling), (2) global scale via full-filter innovation LL."""
    npsr = y.shape[1]
    q0 = np.zeros(npsr)
    for i in range(npsr):
        m = mask[:, i]
        kk = np.where(m)[0]
        if len(kk) < 20:
            q0[i] = 1e-20
            continue
        d = np.diff(y[kk, i])
        dt_k = np.diff(t[kk])
        s2 = Rdiag[kk, i]
        # q_hat = mean((d^2 - s_k^2 - s_{k-1}^2)/dt_k), floored at 0
        qhat = (d ** 2 - s2[1:] - s2[:-1]) / dt_k
        q0[i] = max(float(np.mean(qhat)), 1e-24)
    # (2) global scale via full-filter innovation LL
    scales = np.logspace(-1.5, 1.5, 13)
    lls = []
    dt = float(np.median(np.diff(t)))
    qf_try = calibrate_clock_qf(dt, t[-1] - t[0], DSAC_ADEV_1D, seed=SEED)
    for s in scales:
        _, ll = kalman_masked_tv(t, np.nan_to_num(y), mask, Rdiag,
                                 qf_try, q0 * s, return_ll=True)
        lls.append(ll)
    s_best = scales[int(np.argmax(lls))]
    return q0 * s_best, dict(q0=q0.tolist(), s_best=float(s_best),
                             ll_grid=list(zip(scales.tolist(), lls)))


def gen_clock(t, seed):
    """DSAC-class clock (true qf known): phase/freq/drift like simulate()."""
    dt = float(np.median(np.diff(t)))
    qf = calibrate_clock_qf(dt, t[-1] - t[0], DSAC_ADEV_1D, seed=seed)
    rng = np.random.default_rng(seed)
    n = len(t)
    fr = np.cumsum(rng.standard_normal(n) * np.sqrt(qf * dt))
    dr = np.cumsum(rng.standard_normal(n) * np.sqrt(1e-52 * dt))
    ph = np.cumsum(fr + 0.5 * dr * t) * dt
    return ph - ph[0], qf


def run_transfer(seed_inj=SEED, n_sim=8):
    t, tb, y, Rdiag, mask = regrid(load_residuals())
    dt = float(np.median(np.diff(t)))
    qred, qinfo = estimate_qred(t, y, Rdiag, mask)
    print('qred:', dict(zip(PSRS, ['%.2e' % q for q in qred])), flush=True)
    print('qred scale:', qinfo['s_best'], flush=True)

    clock_true, qf = gen_clock(t, seed_inj)
    y_inj = y + clock_true[:, None]
    est = kalman_masked_tv(t, np.nan_to_num(y_inj), mask, Rdiag, qf, qred)
    # evaluation window: drop first 60 d transient
    ev = tb >= SPAN[0] + 60.0
    err = est[ev] - clock_true[ev]
    rms_pilot = float(np.sqrt(np.mean(err ** 2)))
    rms_hold = float(np.sqrt(np.mean(clock_true[ev] ** 2)))
    print('pilot causal RMS %.0f ns, holdover RMS %.0f ns'
          % (rms_pilot * 1e9, rms_hold * 1e9), flush=True)

    # matched sims: same grid/mask/white, red RW at estimated qred
    rms_sims = []
    for s in range(n_sim):
        rng = np.random.default_rng(9000 + s)
        ys = np.full_like(y, np.nan)
        for i in range(len(PSRS)):
            m = mask[:, i]
            rw = np.cumsum(rng.standard_normal(m.sum())
                           * np.sqrt(qred[i] * dt))
            w = rng.standard_normal(m.sum()) * np.sqrt(Rdiag[m, i])
            ys[m, i] = rw + w
        cs, _ = gen_clock(t, 5000 + s)
        ys_inj = ys + cs[:, None]
        es = kalman_masked_tv(t, np.nan_to_num(ys_inj), mask, Rdiag, qf,
                              qred)
        er = es[ev] - cs[ev]
        rms_sims.append(float(np.sqrt(np.mean(er ** 2))))
    rms_sims = np.array(rms_sims)
    print('matched sim RMS: mean %.0f ns, std %.0f ns'
          % (rms_sims.mean() * 1e9, rms_sims.std() * 1e9), flush=True)

    # G3: gap crossing smoothness
    anyobs = mask.any(axis=1)
    # gaps = runs of >=3 d with no observations
    gaps = []
    k = 0
    while k < len(t):
        if not anyobs[k]:
            k2 = k
            while k2 < len(t) and not anyobs[k2]:
                k2 += 1
            if (tb[min(k2, len(t)-1)] - tb[k]) >= 3.0:
                gaps.append((float(tb[k]), float(tb[min(k2, len(t)-1)])))
            k = k2
        else:
            k += 1
    gaps.sort(key=lambda g: g[1] - g[0], reverse=True)
    err_all = est - clock_true
    gap_err, nongap_err = [], []
    for k in range(len(t)):
        if not ev[k]:
            continue
        (gap_err if not anyobs[k] else nongap_err).append(err_all[k])
    gap_rms = float(np.sqrt(np.mean(np.array(gap_err) ** 2))) \
        if gap_err else np.nan
    nongap_rms = float(np.sqrt(np.mean(np.array(nongap_err) ** 2)))
    # max jump of estimate across the 5 largest gaps
    jumps = []
    for g0, g1 in gaps[:5]:
        m = (tb >= g0 - 1.0) & (tb <= g1 + 1.0) & ev
        if m.sum() > 4:
            jumps.append(float(np.abs(np.diff(est[m])).max()))

    G2 = rms_pilot / rms_sims.mean()
    G3_beats = bool(rms_pilot < rms_hold)
    out = dict(
        bin_d=BIN_D, seed_inj=seed_inj, n_sim=n_sim,
        qred=dict(zip(PSRS, [float(q) for q in qred])),
        qf=float(qf), qinfo_s_best=qinfo['s_best'],
        rms_pilot_ns=rms_pilot * 1e9, rms_holdover_ns=rms_hold * 1e9,
        rms_sim_mean_ns=float(rms_sims.mean() * 1e9),
        rms_sim_std_ns=float(rms_sims.std() * 1e9),
        rms_sims_ns=(rms_sims * 1e9).tolist(),
        G2_ratio=float(G2), G2_pass=bool(G2 < 1.5),
        G3_beats_holdover=G3_beats,
        n_gaps_3d=len(gaps),
        largest_gaps_d=[round(g[1] - g[0], 1) for g in gaps[:5]],
        gap_rms_ns=gap_rms * 1e9 if np.isfinite(gap_rms) else None,
        nongap_rms_ns=nongap_rms * 1e9,
        max_jump_ns=[j * 1e9 for j in jumps],
        n_bins_obs=int(mask.any(axis=1).sum()),
        n_bins=int(len(t)),
    )
    with open(PILOT + '/pilot_filter.json', 'w') as f:
        json.dump(out, f, indent=1)
    print('G2 ratio %.2f (pass<1.5: %s), G3 beats holdover: %s'
          % (G2, out['G2_pass'], G3_beats), flush=True)

    # figures
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(tb, clock_true * 1e6, lw=1, label='injected clock truth')
    ax.plot(tb, est * 1e6, lw=1, alpha=0.8, label='causal Kalman estimate')
    ax.set_xlabel('MJD')
    ax.set_ylabel('clock phase (us)')
    ax.set_title('Pilot clock transfer: injected DSAC-class clock vs causal estimate')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PILOT + '/fig_clock.png', dpi=90)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(tb[ev], err_all[ev] * 1e9, lw=0.8)
    ax.set_xlabel('MJD')
    ax.set_ylabel('clock error (ns)')
    ax.set_title('Causal clock error (pilot, post-transient)')
    fig.tight_layout()
    fig.savefig(PILOT + '/fig_clockerr.png', dpi=90)
    print('saved pilot_filter.json + figures', flush=True)
    return out


if __name__ == '__main__':
    run_transfer()
