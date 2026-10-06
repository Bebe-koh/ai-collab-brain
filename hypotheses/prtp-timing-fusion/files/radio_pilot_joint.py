"""PRTP round 4: joint white-noise + clock-noise estimation on hybrid radio data.

Round 3 removed the oracle on qf (ML estimation, cost 1.00x at M<=1000)
but held white noise at the separately-measured recalibrated values.
A flight system estimates everything from the data. This round closes
the last estimation loophole: per-pulsar white levels AND the clock
random-walk level qf are estimated jointly from the hybrid data.

Method: alternating coordinate ascent on the Kalman innovation
pseudo-log-likelihood (same objective round 3 used for qf):
  - qf step: ML over the round-3 log grid of effective multipliers,
    given current white (reuses radio_pilot_robustness.estimate_qf_ml).
  - white step: per-pulsar innovation covariance matching --
    f_i <- f_i * mean(nis_i) over kept obs (E[nis]=1 at truth), given
    current qf. Standard adaptive-Kalman practice.
Init is deliberately naive: f=[1,1,1] (raw two-component-ML white,
known to be wrong by the RECAL factors 1.05/2.42/2.20), qf by one ML
grid pass. Convergence to the known truth = the estimator works.
Red-noise PSDs (qred) remain oracle (flagged as still-oracle).

Arms: M in {0, 1, 100, 1000}, seeds 101-105, PRIMARY 3-pulsar ensemble,
GATE=25, same union grid / eval window as rounds 2-3.
Plus: init-robustness check (M=1, seed 101, f init [3,3,3]).

SIMULATION-ONLY. Hybrid = real NANOGrav 15-yr binned residuals +
synthetic RW-FM clock.
"""
import sys, json, warnings, time
warnings.filterwarnings('ignore')
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files')
import nanograv_radio_pilot as P
import radio_pilot_robustness as R3

HID = '/home/hatch/workspace/prtp/hidden_files'
PI = [0, 2, 3]                      # J1909, B1855, J0437
SEEDS = [101, 102, 103, 104, 105]
MULTS = [0, 1, 100, 1000]
GATE = 25.0
RECAL_TRUE = np.array([P.RECAL['J1909-3744'], P.RECAL['B1855+09'],
                       P.RECAL['J0437-4715']])


def joint_stats(t, y, mask, Rdiag, qf, qred, gate=GATE):
    """One filter pass. Returns (pseudo_ll, nis) with nis[i] = array of
    marginal nis over kept obs for pulsar i. Mirrors R3.filter_loglik."""
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
    nis = {i: [] for i in range(npsr)}
    for k in range(n):
        if k > 0:
            Fk, Qk = FQ(t[k] - t[k - 1])
            x = Fk @ x
            Pm = Fk @ Pm @ Fk.T + Qk
        obs = np.where(mask[k])[0]
        keep = []
        for i in obs:
            nu = y[k, i] - (x[0] + x[3 + i])
            S = Pm[0, 0] + Pm[3 + i, 3 + i] + 2 * Pm[0, 3 + i] \
                + Rdiag[k, i]
            n_ = nu * nu / S
            if n_ <= gate:
                keep.append(i)
                nis[i].append(n_)
                ll += -0.5 * (n_ + np.log(S))
        if keep:
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
    return ll, {i: np.array(v) for i, v in nis.items()}


def build_Rdiag(Rraw, mask, f):
    R = np.full_like(Rraw, np.nan)
    for i in range(R.shape[1]):
        R[mask[:, i], i] = Rraw[mask[:, i], i] * f[i]
    return R


def white_ll_line(t, y, mask, Rraw, f, qf, qp):
    """Pseudo-LL at white-factor vector f (others fixed inside f)."""
    R = build_Rdiag(Rraw, mask, f)
    ll, _ = joint_stats(t, y, mask, R, qf, qp)
    return ll


def estimate_white_ml(t, y, mask, Rraw, f, qf, qp):
    """Coordinate ascent on the joint pseudo-LL: 1-D ML line search per
    pulsar (log grid + local quadratic peak fit), others held fixed."""
    f = f.copy()
    for i in range(3):
        cand = np.logspace(np.log10(0.3), np.log10(30.0), 13)
        lls = np.array([white_ll_line(
            t, y, mask, Rraw, _set(f, i, c), qf, qp)
            for c in cand])
        b = int(np.argmax(lls))
        # local quadratic refinement around the best grid point
        if 0 < b < len(cand) - 1:
            x = np.log(cand[b - 1:b + 2])
            yy = lls[b - 1:b + 2]
            A = np.vstack([x ** 2, x, np.ones(3)]).T
            a2, a1, a0 = np.linalg.lstsq(A, yy, rcond=None)[0]
            if a2 < 0:
                xpk = -a1 / (2 * a2)
                xpk = float(np.clip(xpk, x[0], x[-1]))
                f[i] = np.exp(xpk)
            else:
                f[i] = cand[b]
        else:
            f[i] = cand[b]
    return f


def _set(f, i, c):
    g = f.copy()
    g[i] = c
    return g


def joint_estimate(t, yh, mask, Rraw, qp, qf_1x, f_init=None,
                   max_iter=6, verbose=False):
    """Joint ML by alternating coordinate ascent on the innovation
    pseudo-log-likelihood: qf step = round-3 ML grid given white;
    white step = per-pulsar 1-D ML line search given qf. Returns dict
    with trajectories, final (f, qf, Mhat), and iteration count."""
    f = np.array([1.0, 1.0, 1.0] if f_init is None else f_init,
                 dtype=float)
    # init qf by ML given naive white
    qh, mh, _ = R3.estimate_qf_ml(t, yh, mask, build_Rdiag(Rraw, mask, f),
                                  qp, qf_1x)
    R = build_Rdiag(Rraw, mask, f)
    ll, _ = joint_stats(t, yh, mask, R, qh, qp)
    traj = [dict(iter=0, f=[float(v) for v in f], Mhat=float(mh), ll=float(ll))]
    if verbose:
        print('    init: f=%s Mhat=%.3g ll=%.1f'
              % (np.round(f, 3), mh, ll), flush=True)
    for it in range(1, max_iter + 1):
        f_new = estimate_white_ml(t, yh, mask, Rraw, f, qh, qp)
        qh_new, mh_new, _ = R3.estimate_qf_ml(
            t, yh, mask, build_Rdiag(Rraw, mask, f_new), qp, qf_1x)
        R = build_Rdiag(Rraw, mask, f_new)
        ll_new, _ = joint_stats(t, yh, mask, R, qh_new, qp)
        df = float(np.max(np.abs(np.log(f_new / f))))
        traj.append(dict(iter=it, f=[float(v) for v in f_new],
                         Mhat=float(mh_new), ll=float(ll_new)))
        if verbose:
            print('    it %d: f=%s Mhat=%.3g ll=%.1f maxdlogf=%.3f'
                  % (it, np.round(f_new, 3), mh_new, ll_new, df),
                  flush=True)
        f, qh, mh = f_new, qh_new, mh_new
        if df < 0.02 and mh_new == traj[-2]['Mhat']:
            break
    return dict(f=f, qf=qh, Mhat=mh, traj=traj, n_iter=len(traj) - 1)


def main():
    t0 = time.time()
    print('loading data...', flush=True)
    t, tb, y, mask = P.load_binned()
    model = P.noise_model(t, y, mask)
    qred = np.array([model[p]['qred'] for p in P.PSRS])
    Rraw = np.full_like(y, np.nan)
    for i, p in enumerate(P.PSRS):
        Rraw[mask[:, i], i] = model[p]['white_var']
    yp, maskp, Rrawp = y[:, PI], mask[:, PI], Rraw[:, PI]
    qp = qred[PI]
    # oracle white: raw * RECAL (the known truth for hybrid data)
    Roracle = build_Rdiag(Rrawp, maskp, RECAL_TRUE)
    qf_1x = P.qf_1x_analytic()
    ev = tb >= tb[0] + 60.0

    res = dict(seeds=SEEDS, mults=MULTS, qf_1x=float(qf_1x),
               config='primary 3-pulsar, JOINT white+qf estimation, '
                      'GATE=25, qred still oracle',
               recal_true=[float(v) for v in RECAL_TRUE])

    rows = []
    for mult in MULTS:
        qf_true = qf_1x * mult ** 2
        row = dict(clock_mult=mult)
        orc, jnt, fhat, mhat, costs, g3o, g3j, chi2j, nits = \
            [], [], [], [], [], [], [], [], []
        hold = None
        for s in SEEDS:
            clk = (np.zeros_like(t) if mult == 0
                   else P.gen_clock_scaled(t, qf_true, s))
            if hold is None and mult > 0:
                hold = float(np.sqrt(np.mean(clk[ev] ** 2))) * 1e9
            yh = yp + clk[:, None]  # NaN preserved outside mask
            je = joint_estimate(t, yh, maskp, Rrawp, qp, qf_1x)
            Rj = build_Rdiag(Rrawp, maskp, je['f'])
            rj = P.run_case(t, tb, yh, Rj, maskp, je['qf'], qp, clk, ev)
            ro = P.run_case(t, tb, yh, Roracle, maskp, qf_true, qp,
                            clk, ev)
            orc.append(ro['rms_ns'])
            jnt.append(rj['rms_ns'])
            fhat.append([float(v) for v in je['f']])
            mhat.append(float(je['Mhat']))
            costs.append(rj['rms_ns'] / ro['rms_ns'])
            chi2j.append(max(rj['chi2'].values()))
            nits.append(je['n_iter'])
            if mult > 0:
                g3o.append(hold / ro['rms_ns'])
                g3j.append(hold / rj['rms_ns'])
        row['oracle_mean_ns'] = float(np.mean(orc))
        row['joint_mean_ns'] = float(np.mean(jnt))
        row['joint_all_ns'] = [float(v) for v in jnt]
        row['fhat_mean'] = [float(v) for v in np.mean(fhat, axis=0)]
        row['fhat_all'] = fhat
        row['fhat_std'] = [float(v) for v in np.std(fhat, axis=0)]
        row['mhat_mean'] = float(np.mean(mhat))
        row['mhat_all'] = [float(v) for v in mhat]
        row['cost_mean'] = float(np.mean(costs))
        row['cost_all'] = [float(v) for v in costs]
        row['n_iter_mean'] = float(np.mean(nits))
        row['G1_chi2max_joint'] = float(np.max(chi2j))
        if mult > 0:
            row['holdover_ns'] = hold
            row['G3_oracle'] = float(np.mean(g3o))
            row['G3_joint'] = float(np.mean(g3j))
            row['G3_joint_all'] = [float(v) for v in g3j]
        print('  M=%5d: oracle %.0f ns | joint %.0f ns (cost %.3fx) | '
              'fhat=%s (truth %s) | Mhat~%.3g | G1chi2 %.2f | '
              'G3 %.1fx -> %.1fx | iters %.1f'
              % (mult, row['oracle_mean_ns'], row['joint_mean_ns'],
                 row['cost_mean'], np.round(row['fhat_mean'], 3),
                 np.round(RECAL_TRUE, 3), row['mhat_mean'],
                 row['G1_chi2max_joint'],
                 row.get('G3_oracle', 0), row.get('G3_joint', 0),
                 row['n_iter_mean']), flush=True)
        rows.append(row)
    res['joint_sweep'] = rows

    # ---- pseudo-LL diagnostic: is (fhat,qhat) the joint maximum? -------
    print('=== pseudo-LL diagnostic (M=1, seed 101) ===', flush=True)
    mult = 1
    qf_true = qf_1x * mult ** 2
    s = SEEDS[0]
    clk = P.gen_clock_scaled(t, qf_true, s)
    yh = yp + clk[:, None]
    je = joint_estimate(t, yh, maskp, Rrawp, qp, qf_1x, verbose=True)
    fh, qh = je['f'], je['qf']
    pts = {
        'fhat_qhat': (fh, qh),
        'truth_truth': (RECAL_TRUE, qf_true),
        '2fhat_qhat': (2 * fh, qh),
        'fhat/2_qhat': (fh / 2, qh),
        'fhat_4qhat': (fh, 4 * qh),
        'fhat_qhat/4': (fh, qh / 4),
    }
    diag = {}
    for name, (ff, qq) in pts.items():
        ll, _ = joint_stats(t, yh, maskp, build_Rdiag(Rrawp, maskp, ff),
                            qq, qp)
        diag[name] = float(ll)
        print('    %-12s ll=%.1f' % (name, ll), flush=True)
    res['ll_diagnostic'] = diag
    res['ll_traj_M1_s101'] = je['traj']

    # ---- init robustness: overshoot start -------------------------------
    print('=== init robustness (M=1, seed 101, f init [3,3,3]) ===',
          flush=True)
    je2 = joint_estimate(t, yh, maskp, Rrawp, qp, qf_1x,
                         f_init=[3.0, 3.0, 3.0], verbose=True)
    res['init_robustness'] = dict(f_init=[3, 3, 3],
                                  f_final=[float(v) for v in je2['f']],
                                  Mhat_final=float(je2['Mhat']),
                                  n_iter=je2['n_iter'])

    res['elapsed_s'] = time.time() - t0
    with open(HID + '/radio_pilot_joint.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('wrote radio_pilot_joint.json (%.0fs)' % res['elapsed_s'],
          flush=True)
    return res


if __name__ == '__main__':
    main()
