"""PRTP NANOGrav radio pilot — run the design from csac_trade_study.md §6.

Real data: NANOGrav 15-yr narrowband binned residuals (30-day bins,
DMX-corrected, JUMPs in par files). Noise model follows the hard lesson:
NEVER the binned formal errors (underestimated 10-100x in amplitude).
Per-bin white from the two-component ML fit (chain_binned_step2.json);
per-pulsar red qred from white-subtracted first differences (R4 recipe,
as in the NICER repair), with B1855 from the chain structure function
(its R4 estimate is white-swamped) and J0437 at the floor (gamma~white).

Filter: causal Kalman, states [clk_ph, clk_fr, clk_dr, red_0..3],
empirical white R, per-pulsar marginal innovation gating (chi2>25),
plus RTS smoother for the model-predicted error (G1-radio).

Hybrid: synthetic RW-FM clock injected into REAL residuals at
M in {0, 1, 100, 1000, 3300} (qf = qf_1x * M^2, M=0 -> zero clock),
>=5 seeds per class. Matched sims: same grid/mask, per-pulsar red RW
at the fitted qred + white at empirical R.

Criteria (mirroring the X-ray pilot):
  G1-radio: smoother-predicted clock error vs measured hybrid RMS < 3x
  G2-radio: hybrid RMS / matched-sim RMS < 1.5
  G3-radio: hybrid RMS < holdover RMS at each M
  Null (M=0): estimated clock RMS ~ predicted level (no monopole)

SIMULATION-ONLY. Hybrid = real TOA noise + synthetic clock.
"""
import sys, os, json, warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files/nicer_pilot')
import pilot_filter as pf  # noqa: E402  (audited: gen_clock calibrator)

HID = '/home/hatch/workspace/prtp/hidden_files'
GOAL = '/home/hatch/workspace/goals/prtp-pulsar-timing-fusion-validation/hidden_files'
PSRS = ['J1909-3744', 'B1937+21', 'B1855+09', 'J0437-4715']
KEYS = ['J1909', 'B1937', 'B1855', 'J0437']
GATE = 25.0
SEEDS_HYBRID = [101, 102, 103, 104, 105]
SEEDS_SIM = list(range(9000, 9008))
MULTS = [0, 1, 100, 1000, 3300]
QD = 1e-52  # drift-state PSD, same as repair


# --------------------------------------------------------------------------
# data + noise model
# --------------------------------------------------------------------------
def load_binned():
    z = np.load(HID + '/nanograv_binned.npz', allow_pickle=True)
    centers = z['centers']
    # union grid over all pulsar bins
    idx = sorted(set(np.concatenate(
        [z['binned_' + k][:, 0].astype(int) for k in KEYS]).tolist()))
    tb = centers[np.array(idx)]
    n = len(tb)
    npsr = len(PSRS)
    y = np.full((n, npsr), np.nan)
    mask = np.zeros((n, npsr), bool)
    for i, k in enumerate(KEYS):
        b = z['binned_' + k]
        bi = b[:, 0].astype(int)
        rows = np.searchsorted(idx, bi)
        y[rows, i] = b[:, 1] * 1e-6   # us -> s
        mask[rows, i] = True
    # per-pulsar mean subtraction (same convention as the repair pipeline)
    for i in range(npsr):
        m = mask[:, i]
        y[m, i] -= np.mean(y[m, i])
    t = (tb - tb[0]) * 86400.0
    return t, tb, y, mask


def noise_model(t, y, mask):
    """white_var: two-component ML fit per 30-day bin (chain_binned_step2).
    qred: R4 recipe — white-subtracted first differences (seconds units),
    floor 1e-24. B1855: R4 is white-swamped -> chain structure-function
    value. J0437: gamma~0.52 (white-like) -> floor."""
    white_ns = {'J1909-3744': 31.0, 'B1937+21': 205.0,
                'B1855+09': 463.0, 'J0437-4715': 222.0}
    model = {}
    for i, psr in enumerate(PSRS):
        m = mask[:, i]
        r = y[m, i]
        wv = (white_ns[psr] * 1e-9) ** 2
        d = np.diff(r)
        dt = np.diff(t[m])
        qhat = (d ** 2 - 2.0 * wv) / dt
        q_emp = max(float(np.mean(qhat)), 1e-24)
        model[psr] = dict(white_var=wv, q_emp=q_emp, n=int(m.sum()))
    # overrides with documented justification
    model['B1855+09']['qred'] = 6.9e-22   # chain SF @30d (R4 white-swamped)
    model['B1855+09']['qred_src'] = 'chain_structure_function'
    model['J0437-4715']['qred'] = 1e-24   # gamma=0.52 ~ white; floor
    model['J0437-4715']['qred_src'] = 'floor_gamma_white'
    for psr in ('J1909-3744', 'B1937+21'):
        model[psr]['qred'] = model[psr]['q_emp']
        model[psr]['qred_src'] = 'R4_empirical'
    return model


# R1-style empirical recalibration (from the pilot's own innovation chi2,
# a noise measurement independent of the clock): per-pulsar white_var
# scaled by the M<=1 innovation chi2/dof. Mirrors the NICER repair's R1.
RECAL = {'J1909-3744': 1.05, 'B1937+21': 1.0, 'B1855+09': 2.42,
         'J0437-4715': 2.20}


# --------------------------------------------------------------------------
# causal Kalman + RTS smoother (red states, no bias states, gating)
# --------------------------------------------------------------------------
def kalman_red(t, y, mask, Rdiag, qf, qred, gate=GATE, store=False):
    n, npsr = y.shape
    d = 3 + npsr
    I = np.eye(d)
    # Per-step dt (the union grid is irregular; J0437 has 720-d gaps).
    # F/Q rebuilt per step — the median-dt shortcut understates process
    # noise over long gaps and corrupts the covariance.
    def FQ(dtk):
        F = np.eye(d)
        F[0, 1] = dtk
        F[0, 2] = 0.5 * dtk ** 2
        F[1, 2] = dtk
        Q = np.diag([0.0, qf * dtk, QD * dtk] + [q * dtk for q in qred])
        return F, Q
    x = np.zeros(d)
    # Red-state prior: data are per-pulsar mean-subtracted, so the RW level
    # is pinned to ~qred*T/12; use qred*T/3 (conservative). (The old
    # series-variance prior left the clock-vs-mean-red degeneracy
    # prior-dominated and made P[0,0] ~100x over-conservative.)
    Tspan = float(t[-1] - t[0])
    # Drift-state prior: QD*Tspan (the actual drift variance over the span).
    # (1e-30 was harmless at 0.25-d cadence but its 0.5*dt^2 lever arm at
    # 30-d cadence inflated P[0,0] ~100x.)
    p0 = [1e-6, 1e-18, QD * Tspan]
    for i in range(npsr):
        p0.append(float(qred[i] * Tspan / 3.0))
    P = np.diag(p0)
    est = np.zeros(n)
    n_rej = 0
    n_upd = 0
    if store:
        xs, Ps, xp, Pp, Fs, Qs = [], [], [], [], [], []
    chi2_store = {i: [] for i in range(npsr)}
    for k in range(n):
        if k > 0:
            Fk, Qk = FQ(t[k] - t[k - 1])
            x = Fk @ x
            P = Fk @ P @ Fk.T + Qk
            if store:
                Fs.append(Fk); Qs.append(Qk)
        if store:
            xp.append(x.copy()); Pp.append(P.copy())
        obs = np.where(mask[k])[0]
        keep = []
        for i in obs:
            nu = y[k, i] - (x[0] + x[3 + i])
            S = P[0, 0] + P[3 + i, 3 + i] + 2 * P[0, 3 + i] + Rdiag[k, i]
            nis = nu * nu / S
            if store:
                chi2_store[i].append((k, nis))
            if nis <= gate:
                keep.append(i)
            else:
                n_rej += 1
        if keep:
            nk = len(keep)
            H = np.zeros((nk, d))
            for r_, i in enumerate(keep):
                H[r_, 0] = 1.0
                H[r_, 3 + i] = 1.0
            Rk = np.diag(Rdiag[k][keep])
            nu = y[k, keep] - H @ x
            S = H @ P @ H.T + Rk
            K = P @ H.T @ np.linalg.inv(S)
            x = x + K @ nu
            # Joseph form (the (I-KH)P shortcut can lose definiteness and
            # miscalibrate P when states are strongly correlated)
            IKH = I - K @ H
            P = IKH @ P @ IKH.T + K @ Rk @ K.T
            n_upd += 1
        est[k] = x[0]
        if store:
            xs.append(x.copy()); Ps.append(P.copy())
    info = dict(n_rejected=int(n_rej), n_updates=int(n_upd))
    if store:
        chi2 = {i: v for i, v in chi2_store.items()}
        return est, info, (np.array(xs), np.array(Ps), np.array(xp),
                           np.array(Pp), np.array(Fs), np.array(Qs)), chi2
    return est, info, None, None


def rts_smoother(xs, Ps, xp, Pp, Fs, Qs):
    n, d = xs.shape
    xs_s = xs.copy()
    Ps_s = Ps.copy()
    for k in range(n - 2, -1, -1):
        # Fs[k] is the transition from k -> k+1 (stored at step k+1)
        Fk = Fs[k]
        G = Ps[k] @ Fk.T @ np.linalg.inv(Pp[k + 1])
        xs_s[k] = xs[k] + G @ (xs_s[k + 1] - xp[k + 1])
        Ps_s[k] = Ps[k] + G @ (Ps_s[k + 1] - Pp[k + 1]) @ G.T
    return xs_s, Ps_s


# --------------------------------------------------------------------------
# matched sims
# --------------------------------------------------------------------------
def sim_radio(t, mask, Rdiag, qred, seed):
    rng = np.random.default_rng(seed)
    n, npsr = mask.shape
    dt = np.diff(t, prepend=t[0])
    y = np.full((n, npsr), np.nan)
    for i in range(npsr):
        m = mask[:, i]
        # RW on the true (irregular) time grid, matching the filter's model
        rw = np.cumsum(rng.standard_normal(n) * np.sqrt(qred[i] * dt))
        y[m, i] = (rw[m] + rng.standard_normal(m.sum())
                   * np.sqrt(Rdiag[m, i]))
        y[m, i] -= np.mean(y[m, i])
    return y


def qf_1x_analytic():
    """DSAC-class qf, analytic: for RW FM, ADEV^2(tau) = qf*tau/6
    (S_y = qf/(4 pi^2 f^2), ADEV^2 = (2pi^2/3) h_-2 tau).
    Verified numerically: ADEV(1d) = 3.7e-15 at qf = 6.25e-34.
    (The sim's bisect calibrator silently returns the bracket top when the
    sampling dt exceeds tau, because adev_phase yields NaN — do NOT use it
    at 30-day cadence.)"""
    return 6.0 * (3.0e-15) ** 2 / 86400.0


def gen_clock_scaled(t, qf, seed):
    rng = np.random.default_rng(seed)
    n = len(t)
    dt = np.diff(t, prepend=t[0])
    fr = np.cumsum(rng.standard_normal(n) * np.sqrt(qf * dt))
    dr = np.cumsum(rng.standard_normal(n) * np.sqrt(QD * dt))
    ph = np.cumsum((fr + 0.5 * dr * t) * dt)
    return ph - ph[0]


# --------------------------------------------------------------------------
# one case
# --------------------------------------------------------------------------
def run_case(t, tb, y, Rdiag, mask, qf, qred, clock_true, ev):
    """Returns rms_ns, pred_ns (smoother, diagnostic), innovation chi2/dof
    per pulsar (G1-radio: filter self-consistency), and gating info."""
    est, info, tr, chi2_raw = kalman_red(t, np.nan_to_num(y), mask, Rdiag,
                                         qf, qred, store=True)
    xs, Ps, xp, Pp, Fs, Qs = tr
    xs_s, Ps_s = rts_smoother(xs, Ps, xp, Pp, Fs, Qs)
    err = est[ev] - clock_true[ev]
    rms = float(np.sqrt(np.mean(err ** 2)))
    pred = float(np.mean(np.sqrt(np.maximum(Ps_s[ev, 0, 0], 0.0))))
    # G1-radio: innovation chi2/dof per pulsar over the eval window
    # (predicted measurement variance vs actual).
    chi2m = {}
    for i, v in chi2_raw.items():
        vv = [nis for (k, nis) in v if ev[k]]
        if vv:
            chi2m[i] = float(np.mean(vv))
    return dict(rms_ns=rms * 1e9, pred_ns=pred * 1e9, chi2=chi2m, info=info)


# --------------------------------------------------------------------------
# main sweep
# --------------------------------------------------------------------------
def sweep(t, tb, y, mask, Rdiag, qred, mults, seeds_h, seeds_s, ev,
          label='full', psr_idx=None):
    """psr_idx: pulsar subset (None = all). Primary radio analysis uses
    [0, 2, 3] (J1909, B1855, J0437); B1937 is excluded because its
    deterministic-like drift violates the stationary-red model
    (b1937_wobble_note) and the pilot's own gating flags 80/167 of its
    epochs. The 4-pulsar run is kept as a failure-mode diagnostic."""
    if psr_idx is not None:
        y, mask, Rdiag = y[:, psr_idx], mask[:, psr_idx], Rdiag[:, psr_idx]
        qred = qred[psr_idx]
    qf_1x = qf_1x_analytic()
    rows = []
    for mult in mults:
        qf = qf_1x * mult ** 2
        row = dict(span=label, clock_mult=mult, qf=float(qf))
        hyb = []
        for s in seeds_h:
            clock_true = (np.zeros_like(t) if mult == 0
                          else gen_clock_scaled(t, qf, s))
            hold = float(np.sqrt(np.mean(clock_true[ev] ** 2)))
            r = run_case(t, tb, y + clock_true[:, None], Rdiag, mask,
                         qf, qred, clock_true, ev)
            hyb.append(r)
            if s == seeds_h[0]:
                row['holdover_ns'] = hold * 1e9
        hr = np.array([h['rms_ns'] for h in hyb])
        hp = np.array([h['pred_ns'] for h in hyb])
        row['hybrid_mean_ns'] = float(hr.mean())
        row['hybrid_std_ns'] = float(hr.std())
        row['hybrid_all_ns'] = hr.tolist()
        row['pred_mean_ns'] = float(hp.mean())
        # G1-radio: innovation chi2/dof within 3x of unity for every pulsar
        # (filter's predicted measurement variance vs actual).
        chi2_all = np.array([v for h in hyb for v in h['chi2'].values()])
        row['G1_chi2_max'] = float(chi2_all.max())
        row['G1_chi2_mean'] = float(chi2_all.mean())
        row['G1_chi2_by_pulsar'] = {
            str(k): float(np.mean([h['chi2'][k] for h in hyb]))
            for k in hyb[0]['chi2']}
        row['g1_ratio'] = float(hr.mean() / hp.mean())  # diagnostic only
        row['g1_pass'] = bool(chi2_all.max() < 3.0
                              and chi2_all.min() > 1.0 / 3.0)
        row['n_rejected'] = int(np.mean([h['info']['n_rejected']
                                         for h in hyb]))
        sims = []
        for s in seeds_s:
            ys = sim_radio(t, mask, Rdiag, qred, s)
            cs = (np.zeros_like(t) if mult == 0
                  else gen_clock_scaled(t, qf, 5000 + s))
            r = run_case(t, tb, ys + cs[:, None], Rdiag, mask,
                         qf, qred, cs, ev)
            sims.append(r['rms_ns'])
        sims = np.array(sims)
        row['sim_mean_ns'] = float(sims.mean())
        row['sim_std_ns'] = float(sims.std())
        row['sim_all_ns'] = sims.tolist()
        g2 = hr.mean() / sims.mean()
        row['G2_ratio'] = float(g2)
        row['G2_pass'] = bool(g2 < 1.5)
        row['G3_beats_holdover'] = bool(hr.mean() < row['holdover_ns']) \
            if mult > 0 else None
        row['improvement'] = (float(row['holdover_ns'] / hr.mean())
                              if mult > 0 else None)
        print('  [%s] M=%5d: hybrid %.0f ns | '
              'G1 chi2 max %.2f %s | '
              'sim %.0f+-%.0f ns (G2 %.2f %s) | holdover %.0f ns | '
              'G3 %s (%.1fx) | rej %d'
              % (label, mult, hr.mean(),
                 row['G1_chi2_max'],
                 'PASS' if row['g1_pass'] else 'FAIL',
                 sims.mean(), sims.std(), g2,
                 'PASS' if row['G2_pass'] else 'FAIL',
                 row['holdover_ns'], row['G3_beats_holdover'],
                 row['improvement'] if row['improvement'] else 0,
                 row['n_rejected']), flush=True)
        rows.append(row)
    return rows, qf_1x


def main():
    print('loading binned NANOGrav data...', flush=True)
    t, tb, y, mask = load_binned()
    print('  grid: %d bins, MJD %.0f-%.0f, obs/bin %s'
          % (len(t), tb.min(), tb.max(), mask.sum(0).tolist()), flush=True)
    model = noise_model(t, y, mask)
    qred = np.array([model[p]['qred'] for p in PSRS])
    Rdiag = np.full_like(y, np.nan)
    Rdiag_recal = np.full_like(y, np.nan)
    for i, p in enumerate(PSRS):
        Rdiag[mask[:, i], i] = model[p]['white_var']
        Rdiag_recal[mask[:, i], i] = model[p]['white_var'] * RECAL[p]
    print('noise model:', flush=True)
    for p in PSRS:
        m = model[p]
        print('  %s: white %.0f ns, qred %.2e (%s, emp %.2e), n=%d'
              % (p, np.sqrt(m['white_var']) * 1e9, m['qred'],
                 m['qred_src'], m['q_emp'], m['n']), flush=True)

    results = dict(mults=MULTS, gate=GATE, qf_note='analytic 6*ADEV^2/tau (sim bisect calibrator NaNs at 30-d cadence)',
                   noise_model={p: {k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
                                    for k, v in m.items()} for p, m in model.items()})

    # full 15-yr span: PRIMARY 3-pulsar (no B1937) + 4-pulsar diagnostic
    ev = tb >= tb[0] + 60.0
    print('=== full span sweep, PRIMARY (J1909+B1855+J0437) ===', flush=True)
    rows_full, qf_1x = sweep(t, tb, y, mask, Rdiag, qred, MULTS,
                             SEEDS_HYBRID, SEEDS_SIM, ev, label='full15yr',
                             psr_idx=[0, 2, 3])
    results['qf_1x'] = float(qf_1x)
    results['full15yr_primary'] = rows_full
    print('=== full span sweep, DIAGNOSTIC (all four, B1937 failure mode) ===',
          flush=True)
    rows_diag, _ = sweep(t, tb, y, mask, Rdiag, qred, MULTS,
                         SEEDS_HYBRID, SEEDS_SIM, ev,
                         label='full15yr_4psr')
    results['full15yr_4psr_diagnostic'] = rows_diag

    print('=== full span sweep, PRIMARY recalibrated-white ===', flush=True)
    rows_recal, _ = sweep(t, tb, y, mask, Rdiag_recal, qred, MULTS,
                          SEEDS_HYBRID, SEEDS_SIM, ev,
                          label='full15yr_recal', psr_idx=[0, 2, 3])
    results['full15yr_primary_recal'] = rows_recal

    # 3-yr sub-window (mission-relevant break-even check), primary set
    w3 = tb >= tb.max() - 3 * 365.25
    ev3 = w3 & (tb >= tb[w3][0] + 60.0)
    print('=== 3-yr window sweep, PRIMARY ===', flush=True)
    rows_3yr, _ = sweep(t[w3], tb[w3], y[w3], mask[w3], Rdiag[w3], qred,
                        [0, 1, 100, 3300], SEEDS_HYBRID, SEEDS_SIM,
                        ev3[w3], label='last3yr',
                        psr_idx=[0, 2, 3])
    results['last3yr_primary'] = rows_3yr

    with open(HID + '/nanograv_radio_pilot.json', 'w') as f:
        json.dump(results, f, indent=1)

    # figures: clock truth vs estimate + error at M=1 and M=3300 (full span,
    # PRIMARY 3-pulsar ensemble)
    pi = [0, 2, 3]
    yp, maskp, Rp = y[:, pi], mask[:, pi], Rdiag[:, pi]
    qp = qred[pi]
    for mult in (1, 3300):
        qf = qf_1x * mult ** 2
        clock_true = gen_clock_scaled(t, qf, SEEDS_HYBRID[0])
        est, info, _, _ = kalman_red(t, np.nan_to_num(yp + clock_true[:, None]),
                               maskp, Rp, qf, qp)
        fig, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot(tb, clock_true * 1e6, lw=1, label='injected clock truth')
        ax.plot(tb, est * 1e6, lw=1, alpha=0.8, label='causal estimate')
        ax.set_xlabel('MJD'); ax.set_ylabel('clock phase (us)')
        ax.set_title('NANOGrav radio pilot (J1909+B1855+J0437): M=%d hybrid' % mult)
        ax.legend(fontsize=8); fig.tight_layout()
        fig.savefig(HID + '/fig_radio_M%d_clock.png' % mult, dpi=90)
        fig, ax = plt.subplots(figsize=(9, 3.0))
        ax.plot(tb[ev], (est[ev] - clock_true[ev]) * 1e9, lw=0.8)
        ax.set_xlabel('MJD'); ax.set_ylabel('clock error (ns)')
        ax.set_title('Radio pilot clock error, M=%d (post-transient)' % mult)
        fig.tight_layout()
        fig.savefig(HID + '/fig_radio_M%d_clockerr.png' % mult, dpi=90)
    print('wrote nanograv_radio_pilot.json + figures', flush=True)
    return results


if __name__ == '__main__':
    main()
