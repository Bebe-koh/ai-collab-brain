"""PRTP NICER pilot REPAIR: recalibrated noise model + robust causal filter.

Repairs vs pilot_filter.py (each documented, ablated separately):
  R1. White noise from EMPIRICAL within-ObsID diffs. The pilot trusted formal
      sigmas; chi2/dof was 3.0 (J0437) and 475 (J0030). Same class of bug as
      the chain-vs-binned white-noise underestimation: never trust formal
      errors. R per pulsar = empirical white variance (weighted into bins).
  R2. Per-(pulsar, ObsID) bias states in the Kalman filter absorb the
      per-ObsID coherent offsets (J0030: 2246 us rms, within-ObsID lag1=0.85).
      The pilot's qred fell back to 1e-20 for J0030 (sparse regridding), so
      the filter trusted J0030 475x too much and its systematics leaked into
      the clock state -> 9.2 ms divergence.
  R3. Innovation gating (per-pulsar marginal chi2, causal, one parameter):
      reject an epoch's pulsar update when NIS > GATE. Bounds the influence
      of any single mis-modeled dwell. Justification over a heavy-tailed
      (Student-t) measurement model: with ~46 observed bins every datum
      matters; hard gating is auditable, keeps the Gaussian machinery
      (and its innovation-LL diagnostics) intact, and cannot silently
      downweight good data the way a misspecified t-model can.
  R4. qred re-estimated on de-offseted dwell-level series (white-subtracted
      first differences on true dwell times, not the sparse regridded grid).

Then: hybrid injection (same seed-777 DSAC clock as pilot), matched sims
with the v2 noise model, G2/G3 at 1x, and a worth-flying clock sweep
(1x/10x/100x/300x, following round5 S5 precedent) to map where aiding
beats holdover.

SIMULATION-ONLY. A repaired GO validates sim-to-real transfer on this one
ISS dataset, never flight readiness.
Saves repair_filter.json + figures.
"""
import sys, os, json, glob, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/hatch/workspace/prtp')
sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files/nicer_pilot')
from pilot_filter import gen_clock, kalman_masked_tv  # noqa: E402  (audited code reuse)

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
PSRS = ['J0437-4715', 'J0030+0451', 'J0218+4232', 'B1821-24']
BIN_D = 0.25
SPAN = (58300.0, 59030.0)
Q = dict(min_n=50, min_exp=300.0, min_htest=20.0)
SEED = 777
GATE = 25.0  # ~5 sigma marginal chi2 (1 dof)


# --------------------------------------------------------------------------
# data + empirical noise model v2
# --------------------------------------------------------------------------
def load_dwells():
    """Quality-cut dwells with per-pulsar mean-subtracted residuals (s),
    keeping obsid for the systematics model. y-construction identical to
    pilot_filter.load_residuals."""
    files = sorted(glob.glob(PILOT + '/dwells_*.csv'))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df[(df['n_phot'] >= Q['min_n']) & (df['exp_s'] >= Q['min_exp'])
            & (df['htest'] >= Q['min_htest'])
            & np.isfinite(df['dphi']) & np.isfinite(df['sigma_dphi'])].copy()
    df = df.sort_values(['psr', 'mjd_mid']).reset_index(drop=True)
    df['sig_s'] = df['sigma_dphi'] * df['P0_s']
    out = []
    for psr, g in df.groupby('psr'):
        if len(g) < 10:
            continue
        ph = np.unwrap(g['dphi'].values * 2 * np.pi) / (2 * np.pi)
        sig = g['sig_s'].values
        w = 1 / sig ** 2
        r = (ph - np.average(ph, weights=w)) * g['P0_s'].values
        gg = g.copy()
        gg['r'] = r
        gg['w'] = w
        out.append(gg)
    return pd.concat(out, ignore_index=True)


def noise_model_v2(df):
    """Empirical per-pulsar noise decomposition (dwell level, seconds).

    white_var: from within-ObsID diffs (same ObsID => same offset cancels).
    off_var:   variance of per-ObsID weighted means (coherent systematics).
    qred:      RW PSD from de-offseted first differences, white-subtracted.
    """
    model = {}
    for psr, g in df.groupby('psr'):
        g = g.sort_values('mjd_mid').reset_index(drop=True)
        r = g['r'].values
        d2w = []
        for _, gg in g.groupby('obsid'):
            rr = r[gg.index.values]
            if len(rr) >= 2:
                d2w.extend(np.diff(rr) ** 2 / 2.0)
        white_var = float(np.mean(d2w)) if d2w else float(np.var(r))
        off = g.groupby('obsid').apply(
            lambda gg: np.average(r[gg.index.values], weights=g['w'].values[gg.index.values]))
        off_var = float(np.var(off.values))
        r_de = r - g['obsid'].map(off).values
        t = g['mjd_mid'].values * 86400.0
        d = np.diff(r_de)
        dt = np.diff(t)
        qhat = (d ** 2 - 2.0 * white_var) / dt
        qred = max(float(np.mean(qhat)), 1e-24)
        model[psr] = dict(white_var=white_var, off_var=off_var, qred=qred,
                          n=int(len(g)), n_obsids=int(g['obsid'].nunique()),
                          white_rms_us=np.sqrt(white_var) * 1e6,
                          off_rms_us=np.sqrt(off_var) * 1e6)
    return model


def regrid_v2(df, model):
    """0.25-d bins. y identical to pilot (formal-weighted mean); R from the
    empirical white model: Var = white_var * sum(w^2)/(sum w)^2.
    Also returns obmap (bin -> obsid index per pulsar) and per-bin R."""
    t0, t1 = SPAN
    tb = t0 + (np.arange(int((t1 - t0) / BIN_D)) + 0.5) * BIN_D
    n = len(tb)
    npsr = len(PSRS)
    y = np.full((n, npsr), np.nan)
    Rdiag = np.full((n, npsr), np.nan)
    mask = np.zeros((n, npsr), bool)
    obmap = np.full((n, npsr), -1, dtype=int)
    ob_lists = {}  # psr -> list of obsids (stable order)
    for i, psr in enumerate(PSRS):
        if psr not in model:
            continue
        s = df[df['psr'] == psr].sort_values('mjd_mid')
        ob_lists[psr] = sorted(s['obsid'].unique())
        ob_index = {ob: j for j, ob in enumerate(ob_lists[psr])}
        wv = model[psr]['white_var']
        b = ((s['mjd_mid'].values - t0) / BIN_D).astype(int)
        sv = s['r'].values
        wv_arr = s['w'].values
        ob_arr = s['obsid'].values
        for bb in np.unique(b[(b >= 0) & (b < n)]):
            m = b == bb
            w = wv_arr[m]
            y[bb, i] = np.sum(w * sv[m]) / np.sum(w)
            Rdiag[bb, i] = wv * np.sum(w ** 2) / np.sum(w) ** 2
            mask[bb, i] = True
            # weight-dominant obsid for the bias state
            best, bw = None, -1.0
            for ob in np.unique(ob_arr[m]):
                wb = w[ob_arr[m] == ob].sum()
                if wb > bw:
                    bw, best = wb, ob
            obmap[bb, i] = ob_index[best]
    t = (tb - t0) * 86400.0
    return t, tb, y, Rdiag, mask, obmap, ob_lists


# --------------------------------------------------------------------------
# repaired causal filter: bias states + innovation gating
# --------------------------------------------------------------------------
def kalman_masked_tv_bias(t, y, mask, Rdiag, qf, qred, obmap, ob_lists,
                          model, gate=GATE, return_info=False):
    """Delta vs pilot_filter.kalman_masked_tv (audited):
    + per-(pulsar,ObsID) bias states (F=1, Q=0, prior var = off_var)
      absorbing coherent per-ObsID systematics;
    + per-pulsar marginal innovation gating (NIS > gate -> drop that
      pulsar's update at that epoch, causal: uses only the prior).
    State: [clk_ph, clk_fr, clk_dr, red_0..3, bias_0..B-1]."""
    n, npsr = y.shape
    bstart, nb = {}, 0
    for i, psr in enumerate(PSRS):
        bstart[i] = nb
        nb += len(ob_lists.get(psr, []))
    d = 3 + npsr + nb
    dt = float(np.median(np.diff(t)))
    F = np.eye(d)
    F[0, 1] = dt
    F[0, 2] = 0.5 * dt ** 2
    F[1, 2] = dt
    qd = 1e-52
    qred = np.atleast_1d(np.asarray(qred, dtype=float))
    Q = np.diag([0.0, qf * dt, qd * dt] + list(qred * dt) + [0.0] * nb)
    # measurement rows per pulsar: clock + own red + own obsid bias
    Hrows = {}
    for i, psr in enumerate(PSRS):
        h = np.zeros(d)
        h[0] = 1.0
        h[3 + i] = 1.0
        Hrows[i] = h
    x = np.zeros(d)
    p0 = [1e-6, 1e-18, 1e-30] + [1e-12] * npsr
    for i, psr in enumerate(PSRS):
        ov = model.get(psr, {}).get('off_var', 1e-12)
        p0 += [ov] * len(ob_lists.get(psr, []))
    P = np.diag(p0)
    I = np.eye(d)
    out = np.zeros(n)
    n_rej = 0
    n_upd = 0
    for k in range(n):
        if k > 0:
            x = F @ x
            P = F @ P @ F.T + Q
        obs = [i for i in np.where(mask[k])[0]
               if obmap[k, i] >= 0]
        keep = []
        for i in obs:
            h = Hrows[i].copy()
            h[3 + npsr + bstart[i] + obmap[k, i]] = 1.0
            nu = y[k, i] - h @ x
            S = h @ P @ h + Rdiag[k, i]
            if nu * nu / S <= gate:
                keep.append(i)
            else:
                n_rej += 1
        if keep:
            H = np.zeros((len(keep), d))
            for r_, i in enumerate(keep):
                H[r_, 0] = 1.0
                H[r_, 3 + i] = 1.0
                H[r_, 3 + npsr + bstart[i] + obmap[k, i]] = 1.0
            Rk = np.diag(Rdiag[k][keep])
            nu = y[k, keep] - H @ x
            S = H @ P @ H.T + Rk
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ nu
            P = (I - K @ H) @ P
            n_upd += 1
        out[k] = x[0]
    info = dict(n_rejected=int(n_rej), n_updates=int(n_upd))
    return (out, info) if return_info else out


# --------------------------------------------------------------------------
# matched sims with the v2 noise model
# --------------------------------------------------------------------------
def sim_v2(t, mask, Rdiag, obmap, ob_lists, model, qred, seed):
    """Same grid/mask/bins as the real data; per-pulsar red RW (v2 qred) +
    per-ObsID offsets N(0, off_var) + white at the binned empirical R."""
    rng = np.random.default_rng(seed)
    n, npsr = mask.shape
    dt = float(np.median(np.diff(t)))
    y = np.full((n, npsr), np.nan)
    for i, psr in enumerate(PSRS):
        if psr not in model:
            continue
        m = mask[:, i]
        rw = np.cumsum(rng.standard_normal(n) * np.sqrt(qred[i] * dt))
        offs = rng.standard_normal(len(ob_lists[psr])) \
            * np.sqrt(model[psr]['off_var'])
        y[m, i] = (rw[m] + offs[obmap[m, i]]
                   + rng.standard_normal(m.sum()) * np.sqrt(Rdiag[m, i]))
    return y


def gen_clock_scaled(t, qf, seed):
    """Same generator as pilot_filter.gen_clock, with explicit qf (for the
    clock-quality sweep; qf scales as mult^2 since ADEV ~ sqrt(qf))."""
    rng = np.random.default_rng(seed)
    n = len(t)
    dt = float(np.median(np.diff(t)))
    fr = np.cumsum(rng.standard_normal(n) * np.sqrt(qf * dt))
    dr = np.cumsum(rng.standard_normal(n) * np.sqrt(1e-52 * dt))
    ph = np.cumsum(fr + 0.5 * dr * t) * dt
    return ph - ph[0]


def run_case(t, tb, y, Rdiag, mask, qf, qred, clock_true, variant,
             obmap=None, ob_lists=None, model=None, gate=GATE):
    """One filter run.
    variant 'pilot':   audited kalman_masked_tv, formal R, pilot qred
                       (reproduces the pilot's 9.2 ms).
    variant 'v2plain': audited kalman_masked_tv, v2 R/qred (isolates the
                       noise-model recalibration).
    variant 'v2bias':  + per-ObsID bias states, no gating (isolates R2).
    variant 'v2full':  + bias states + innovation gating (full repair)."""
    ev = tb >= SPAN[0] + 60.0
    info = {}
    if variant in ('pilot', 'v2plain'):
        est = kalman_masked_tv(t, np.nan_to_num(y), mask, Rdiag, qf, qred)
    else:
        est, info = kalman_masked_tv_bias(
            t, np.nan_to_num(y), mask, Rdiag, qf, qred, obmap, ob_lists,
            model, gate=gate if variant == 'v2full' else np.inf,
            return_info=True)
    err = est[ev] - clock_true[ev]
    return dict(rms_ns=float(np.sqrt(np.mean(err ** 2)) * 1e9), info=info)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    import pilot_filter as pf
    print('loading dwells...', flush=True)
    df = load_dwells()
    model = noise_model_v2(df)
    print('noise model v2:', flush=True)
    for psr, m in model.items():
        print('  %s: white %.0f us, obsid-offset %.0f us, qred %.2e (n=%d, nobs=%d)'
              % (psr, m['white_rms_us'], m['off_rms_us'], m['qred'],
                 m['n'], m['n_obsids']), flush=True)

    # pilot products (for the 'pilot' ablation arm): formal R, pilot qred
    t, tb, y, Rdiag, mask, obmap, ob_lists = regrid_v2(df, model)
    tp, tbp, yp, Rp, maskp = pf.regrid(pf.load_residuals())
    qred_pilot, _ = pf.estimate_qred(tp, yp, Rp, maskp)
    qred_v2 = np.array([model.get(p, {}).get('qred', 1e-20) for p in PSRS])

    # DSAC-class clock, same seed as pilot; qf_1x from the same calibrator
    clock_1x, qf_1x = pf.gen_clock(t, SEED)
    print('qf_1x = %.3e' % qf_1x, flush=True)

    ev = tb >= SPAN[0] + 60.0
    n_sim = 8
    results = dict(variants=['pilot', 'v2plain', 'v2bias', 'v2full'],
                   clock_mults=[1.0, 10.0, 100.0, 300.0], n_sim=n_sim,
                   noise_model_v2={p: {k: float(v) for k, v in m.items()
                                       if k != 'n' and k != 'n_obsids'}
                                   for p, m in model.items()},
                   qf_1x=float(qf_1x), gate=GATE)
    sweep = []
    for mult in results['clock_mults']:
        qf = qf_1x * mult ** 2
        clock_true = gen_clock_scaled(t, qf, SEED) if mult != 1.0 else clock_1x
        rms_hold = float(np.sqrt(np.mean(clock_true[ev] ** 2)) * 1e9)
        row = dict(clock_mult=mult, qf=qf, rms_holdover_ns=rms_hold)
        print('=== clock %gx (qf=%.2e), holdover %.0f ns ==='
              % (mult, qf, rms_hold), flush=True)
        # hybrid: injected clock + REAL residuals
        y_inj = y + clock_true[:, None]
        for var in results['variants']:
            if var == 'pilot':
                r = run_case(tp, tbp, yp + clock_true[:, None], Rp, maskp,
                             qf, qred_pilot, clock_true, 'pilot')
            else:
                Rr, qr = (Rdiag, qred_v2)
                r = run_case(t, tb, y_inj, Rr, mask, qf, qr, clock_true, var,
                             obmap, ob_lists, model)
            row['hybrid_' + var + '_ns'] = r['rms_ns']
            row['hybrid_' + var + '_info'] = r['info']
            print('  hybrid %-8s: %.0f ns %s'
                  % (var, r['rms_ns'], r['info']), flush=True)
        # matched sims with the v2 noise model
        for var in ('v2plain', 'v2bias', 'v2full'):
            sims = []
            for s in range(n_sim):
                ys = sim_v2(t, mask, Rdiag, obmap, ob_lists, model,
                            qred_v2, 9000 + s)
                # mean-subtract per pulsar like the real pipeline
                for i in range(len(PSRS)):
                    m = mask[:, i]
                    if m.sum():
                        ys[m, i] -= np.mean(ys[m, i])
                cs = gen_clock_scaled(t, qf, 5000 + s)
                r = run_case(t, tb, ys + cs[:, None], Rdiag, mask, qf,
                             qred_v2, cs, var, obmap, ob_lists, model)
                sims.append(r['rms_ns'])
            sims = np.array(sims)
            row['sim_' + var + '_mean_ns'] = float(sims.mean())
            row['sim_' + var + '_std_ns'] = float(sims.std())
            row['sim_' + var + '_all_ns'] = sims.tolist()
            print('  sim    %-8s: mean %.0f ns (std %.0f)'
                  % (var, sims.mean(), sims.std()), flush=True)
        # G2/G3 on the full-repair arm
        g2 = row['hybrid_v2full_ns'] / row['sim_v2full_mean_ns']
        row['G2_ratio'] = float(g2)
        row['G2_pass'] = bool(g2 < 1.5)
        row['G3_beats_holdover'] = bool(row['hybrid_v2full_ns'] < rms_hold)
        row['improvement_vs_holdover'] = float(rms_hold / row['hybrid_v2full_ns'])
        print('  G2 ratio %.2f (pass<1.5: %s)  G3 beats holdover: %s (%.2fx)'
              % (g2, row['G2_pass'], row['G3_beats_holdover'],
                 row['improvement_vs_holdover']), flush=True)
        sweep.append(row)
    results['sweep'] = sweep

    with open(PILOT + '/repair_filter.json', 'w') as f:
        json.dump(results, f, indent=1)

    # figures: repaired clock + error at 1x
    mult1 = sweep[0]
    qf = qf_1x
    clock_true = clock_1x
    y_inj = y + clock_true[:, None]
    est, info = kalman_masked_tv_bias(t, np.nan_to_num(y_inj), mask, Rdiag,
                                      qf, qred_v2, obmap, ob_lists, model,
                                      gate=GATE, return_info=True)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(tb, clock_true * 1e6, lw=1, label='injected clock truth')
    ax.plot(tb, est * 1e6, lw=1, alpha=0.8, label='repaired causal estimate')
    ax.set_xlabel('MJD')
    ax.set_ylabel('clock phase (us)')
    ax.set_title('Repair: injected DSAC-class clock vs robust causal estimate')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PILOT + '/fig_repair_clock.png', dpi=90)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(tb[ev], (est[ev] - clock_true[ev]) * 1e9, lw=0.8)
    ax.set_xlabel('MJD')
    ax.set_ylabel('clock error (ns)')
    ax.set_title('Repaired causal clock error (post-transient)')
    fig.tight_layout()
    fig.savefig(PILOT + '/fig_repair_clockerr.png', dpi=90)
    print('saved repair_filter.json + figures; gating info:', info, flush=True)
    return results


if __name__ == '__main__':
    main()
