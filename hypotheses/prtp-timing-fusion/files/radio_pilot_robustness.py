"""PRTP round 3: non-oracle clock-noise re-run + data-gap robustness.

Builds on nanograv_radio_pilot.py (round 2). Two realism upgrades:

(A) ESTIMATED qf: the round-2 pilot gave the filter oracle clock-noise
    PSD (true qf). A flight system must estimate qf from the data.
    Here qf is estimated per hybrid realization by maximum (pseudo-)
    likelihood over a qf grid, using the Kalman innovation likelihood
    (standard adaptive-Kalman practice), then the filter is re-run with
    the estimated qf. The oracle-vs-estimated cost factor is measured
    directly: rms(estimated qf) / rms(oracle qf), per (M, seed).

(B) DATA GAPS: mission-realistic observing gaps — 25% and 40% of epochs
    dropped in contiguous MJD blocks (downlink blackouts / scheduling
    gaps) — re-run at M=1 and M=100 (oracle qf, to isolate the gap
    effect), plus a combined full-realism case (M=1, 25% gaps,
    estimated qf), plus the 3-yr mission window at M=1 with estimated qf.

Configuration matches the round-2 headline: PRIMARY 3-pulsar ensemble
(J1909+B1855+J0437), recalibrated white (RECAL, a data-measured noise
fix held fixed here to isolate the qf-estimation cost), GATE=25.

SIMULATION-ONLY. Hybrid = real NANOGrav 15-yr binned residuals +
synthetic RW-FM clock.
"""
import sys, json, warnings, time
warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files')
import nanograv_radio_pilot as P

HID = '/home/hatch/workspace/prtp/hidden_files'
PI = [0, 2, 3]                      # J1909, B1855, J0437 (B1937 excluded)
SEEDS = [101, 102, 103, 104, 105]
MULTS = [0, 1, 100, 1000, 3300]
GATE = 25.0


# --------------------------------------------------------------------------
# innovation pseudo-log-likelihood (mirrors kalman_red's loop, no store)
# --------------------------------------------------------------------------
def filter_loglik(t, y, mask, Rdiag, qf, qred, gate=GATE):
    """Sum of marginal Gaussian log-likelihood terms over kept obs:
    -0.5 * sum(nis + log S) with the same per-pulsar marginal gating as
    the filter. A pseudo-likelihood (ignores cross-pulsar S terms);
    standard for adaptive-Kalman qf selection."""
    n, npsr = y.shape
    d = 3 + npsr
    I = np.eye(d)

    def FQ(dtk):
        F = np.eye(d)
        F[0, 1] = dtk
        F[0, 2] = 0.5 * dtk ** 2
        F[1, 2] = dtk
        Q = np.diag([0.0, qf * dtk, P.QD * dtk]
                    + [q * dtk for q in qred])
        return F, Q

    x = np.zeros(d)
    Tspan = float(t[-1] - t[0])
    p0 = [1e-6, 1e-18, P.QD * Tspan] \
        + [float(q * Tspan / 3.0) for q in qred]
    Pm = np.diag(p0)
    ll = 0.0
    nobs = 0
    for k in range(n):
        if k > 0:
            Fk, Qk = FQ(t[k] - t[k - 1])
            x = Fk @ x
            Pm = Fk @ Pm @ Fk.T + Qk
        obs = np.where(mask[k])[0]
        keep = []
        Sdiag = {}
        nud = {}
        for i in obs:
            nu = y[k, i] - (x[0] + x[3 + i])
            S = Pm[0, 0] + Pm[3 + i, 3 + i] + 2 * Pm[0, 3 + i] \
                + Rdiag[k, i]
            if nu * nu / S <= gate:
                keep.append(i)
                Sdiag[i] = S
                nud[i] = nu
        if keep:
            for i in keep:
                ll += -0.5 * (nud[i] ** 2 / Sdiag[i]
                              + np.log(Sdiag[i]))
                nobs += 1
            nk = len(keep)
            H = np.zeros((nk, d))
            for r_, i in enumerate(keep):
                H[r_, 0] = 1.0
                H[r_, 3 + i] = 1.0
            Rk = np.diag(Rdiag[k][keep])
            nu = y[k, keep] - H @ x
            S = H @ Pm @ H.T + Rk
            K = Pm @ H.T @ np.linalg.inv(S)
            x = x + K @ nu
            IKH = I - K @ H
            Pm = IKH @ Pm @ IKH.T + K @ Rk @ K.T
    return ll, nobs


def estimate_qf_ml(t, y, mask, Rdiag, qred, qf_1x):
    """ML qf on a log grid of effective clock multipliers M_eff
    (qf = qf_1x * M_eff^2), coarse then 2 refinement passes."""
    cand = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300,
            1000, 3000, 10000]
    best_m, best_ll = None, -np.inf
    for rnd in range(3):
        for m in cand:
            ll, _ = filter_loglik(t, y, mask, Rdiag,
                                  qf_1x * m * m, qred)
            if ll > best_ll:
                best_ll, best_m = ll, m
        if rnd < 2:
            lo = max(np.log10(best_m) - 0.6, -2.0)
            hi = min(np.log10(best_m) + 0.6, 4.0)
            cand = np.logspace(lo, hi, 5).tolist()
    return qf_1x * best_m * best_m, best_m, best_ll


# --------------------------------------------------------------------------
# contiguous-block gap mask
# --------------------------------------------------------------------------
def gap_mask(mask, tb, frac, seed, nblocks=24):
    """Drop ~frac of observed entries in contiguous MJD blocks."""
    rng = np.random.default_rng(seed)
    edges = np.linspace(tb.min(), tb.max(), nblocks + 1)
    order = rng.permutation(nblocks)
    total = int(mask.sum())
    target = frac * total
    gm = mask.copy()
    removed = 0
    for b in order:
        if removed >= target:
            break
        if b == nblocks - 1:
            sel = (tb >= edges[b]) & (tb <= edges[b + 1])
        else:
            sel = (tb >= edges[b]) & (tb < edges[b + 1])
        removed += int(gm[sel].sum())
        gm[sel] = False
    return gm, removed / total


# --------------------------------------------------------------------------
def main():
    t0 = time.time()
    print('loading data...', flush=True)
    t, tb, y, mask = P.load_binned()
    model = P.noise_model(t, y, mask)
    qred = np.array([model[p]['qred'] for p in P.PSRS])
    Rdiag = np.full_like(y, np.nan)
    for i, p in enumerate(P.PSRS):
        Rdiag[mask[:, i], i] = model[p]['white_var'] * P.RECAL[p]
    # primary 3-pulsar subset
    yp, maskp, Rp = y[:, PI], mask[:, PI], Rdiag[:, PI]
    qp = qred[PI]
    qf_1x = P.qf_1x_analytic()
    ev = tb >= tb[0] + 60.0
    res = dict(seeds=SEEDS, mults=MULTS, qf_1x=float(qf_1x),
               config='primary 3-pulsar, recalibrated white, GATE=25')

    # ---- (A) estimated-qf sweep -----------------------------------------
    print('=== (A) estimated-qf sweep, full 15-yr ===', flush=True)
    rowsA = []
    for mult in MULTS:
        qf_true = qf_1x * mult ** 2
        row = dict(clock_mult=mult)
        orc, est, mhat, costs, g3o, g3e, chi2e = [], [], [], [], [], [], []
        hold = None
        for s in SEEDS:
            clk = (np.zeros_like(t) if mult == 0
                   else P.gen_clock_scaled(t, qf_true, s))
            if hold is None and mult > 0:
                hold = float(np.sqrt(np.mean(clk[ev] ** 2))) * 1e9
            yh = np.nan_to_num(yp + clk[:, None])
            ro = P.run_case(t, tb, yh, Rp, maskp, qf_true, qp, clk, ev)
            qh, mh, _ = estimate_qf_ml(t, yh, maskp, Rp, qp, qf_1x)
            re = P.run_case(t, tb, yh, Rp, maskp, qh, qp, clk, ev)
            orc.append(ro['rms_ns'])
            est.append(re['rms_ns'])
            mhat.append(mh)
            costs.append(re['rms_ns'] / ro['rms_ns'])
            chi2e.append(max(re['chi2'].values()))
            if mult > 0:
                g3o.append(hold / ro['rms_ns'])
                g3e.append(hold / re['rms_ns'])
        row['oracle_mean_ns'] = float(np.mean(orc))
        row['est_mean_ns'] = float(np.mean(est))
        row['est_all_ns'] = [float(v) for v in est]
        row['mhat_mean'] = float(np.mean(mhat))
        row['mhat_all'] = [float(v) for v in mhat]
        row['cost_mean'] = float(np.mean(costs))
        row['cost_all'] = [float(v) for v in costs]
        row['G1_chi2max_est'] = float(np.max(chi2e))
        if mult > 0:
            row['holdover_ns'] = hold
            row['G3_oracle'] = float(np.mean(g3o))
            row['G3_est'] = float(np.mean(g3e))
        print('  M=%5d: oracle %.0f ns | est %.0f ns (cost %.2fx) | '
              'Mhat~%.2g | G1chi2 %.2f | G3 %.1fx -> %.1fx'
              % (mult, row['oracle_mean_ns'], row['est_mean_ns'],
                 row['cost_mean'], row['mhat_mean'],
                 row['G1_chi2max_est'],
                 row.get('G3_oracle', 0), row.get('G3_est', 0)),
              flush=True)
        rowsA.append(row)
    res['A_estimated_qf'] = rowsA

    # ---- (B) gap runs, oracle qf (isolate gap effect) --------------------
    print('=== (B) gap runs, oracle qf ===', flush=True)
    rowsB = []
    for frac, gseed in [(0.25, 7), (0.40, 8)]:
        gmask, got = gap_mask(maskp, tb, frac, gseed)
        for mult in [1, 100]:
            qf = qf_1x * mult ** 2
            row = dict(gap_frac=frac, gap_actual=float(got),
                       clock_mult=mult, qf_mode='oracle')
            rms, g3, chi2m, rej = [], [], [], []
            hold = None
            for s in SEEDS:
                clk = P.gen_clock_scaled(t, qf, s)
                if hold is None:
                    hold = float(np.sqrt(np.mean(clk[ev] ** 2))) * 1e9
                r = P.run_case(t, tb, np.nan_to_num(yp + clk[:, None]),
                               Rp, gmask, qf, qp, clk, ev)
                rms.append(r['rms_ns'])
                g3.append(hold / r['rms_ns'])
                chi2m.append(max(r['chi2'].values()))
                rej.append(r['info']['n_rejected'])
            row['hybrid_mean_ns'] = float(np.mean(rms))
            row['hybrid_all_ns'] = [float(v) for v in rms]
            row['G3_mean'] = float(np.mean(g3))
            row['G3_all'] = [float(v) for v in g3]
            row['G1_chi2max'] = float(np.max(chi2m))
            row['n_rejected_mean'] = float(np.mean(rej))
            row['holdover_ns'] = hold
            print('  gap %.0f%% M=%4d: hybrid %.0f ns | G3 %.1fx | '
                  'G1chi2 %.2f | rej %.0f'
                  % (100 * got, mult, row['hybrid_mean_ns'],
                     row['G3_mean'], row['G1_chi2max'],
                     row['n_rejected_mean']), flush=True)
            rowsB.append(row)
    res['B_gaps_oracle'] = rowsB

    # ---- (C) combined full realism: M=1, 25% gaps, estimated qf ---------
    print('=== (C) combined: M=1, 25% gaps, estimated qf ===', flush=True)
    gmask, got = gap_mask(maskp, tb, 0.25, 7)
    qf = qf_1x * 1.0
    rms, g3, mhat, chi2m = [], [], [], []
    hold = None
    for s in SEEDS:
        clk = P.gen_clock_scaled(t, qf, s)
        if hold is None:
            hold = float(np.sqrt(np.mean(clk[ev] ** 2))) * 1e9
        yh = np.nan_to_num(yp + clk[:, None])
        qh, mh, _ = estimate_qf_ml(t, yh, gmask, Rp, qp, qf_1x)
        r = P.run_case(t, tb, yh, Rp, gmask, qh, qp, clk, ev)
        rms.append(r['rms_ns'])
        g3.append(hold / r['rms_ns'])
        mhat.append(mh)
        chi2m.append(max(r['chi2'].values()))
    res['C_combined'] = dict(gap_frac=0.25, gap_actual=float(got),
                             clock_mult=1, qf_mode='estimated',
                             hybrid_mean_ns=float(np.mean(rms)),
                             hybrid_all_ns=[float(v) for v in rms],
                             G3_mean=float(np.mean(g3)),
                             G3_all=[float(v) for v in g3],
                             mhat_all=[float(v) for v in mhat],
                             G1_chi2max=float(np.max(chi2m)),
                             holdover_ns=hold)
    print('  combined: hybrid %.0f ns | G3 %.1fx | G1chi2 %.2f'
          % (np.mean(rms), np.mean(g3), np.max(chi2m)), flush=True)

    # ---- (D) 3-yr window, M=1, estimated qf ------------------------------
    print('=== (D) 3-yr window, M=1, estimated qf ===', flush=True)
    w3 = tb >= tb.max() - 3 * 365.25
    ev3 = w3 & (tb >= tb[w3][0] + 60.0)
    tw, tbw = t[w3], tb[w3]
    rms, g3, mhat = [], [], []
    hold = None
    for s in SEEDS:
        clk = P.gen_clock_scaled(tw, qf, s)
        if hold is None:
            hold = float(np.sqrt(np.mean(clk[ev3[w3]] ** 2))) * 1e9
        yh = np.nan_to_num(yp[w3] + clk[:, None])
        qh, mh, _ = estimate_qf_ml(tw, yh, maskp[w3], Rp[w3], qp, qf_1x)
        r = P.run_case(tw, tbw, yh, Rp[w3], maskp[w3], qh, qp, clk,
                       ev3[w3])
        rms.append(r['rms_ns'])
        g3.append(hold / r['rms_ns'])
        mhat.append(mh)
    res['D_3yr_est'] = dict(clock_mult=1, qf_mode='estimated',
                            hybrid_mean_ns=float(np.mean(rms)),
                            hybrid_all_ns=[float(v) for v in rms],
                            G3_mean=float(np.mean(g3)),
                            G3_all=[float(v) for v in g3],
                            mhat_all=[float(v) for v in mhat],
                            holdover_ns=hold)
    print('  3yr M=1 est: hybrid %.0f ns | G3 %.1fx'
          % (np.mean(rms), np.mean(g3)), flush=True)

    res['elapsed_s'] = time.time() - t0
    with open(HID + '/radio_pilot_robustness.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('wrote radio_pilot_robustness.json (%.0fs)' % res['elapsed_s'],
          flush=True)
    return res


if __name__ == '__main__':
    main()
