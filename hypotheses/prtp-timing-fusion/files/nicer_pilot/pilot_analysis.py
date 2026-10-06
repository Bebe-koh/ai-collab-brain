"""PRTP NICER pilot analysis: G1 (TOA precision), N1 (duty), systematics.

Reads dwells.csv (Pass 2 output). Produces pilot_g1n1.json + figures.
Does NOT inject clock or run the filter (see pilot_filter.py).
"""
import sys, os, json, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/hatch/workspace/prtp')
sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files/nicer_pilot')
import xray
import pilot_toa as pt

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
PSRS = ['J0437-4715', 'J0030+0451', 'J0218+4232', 'B1821-24']
# sim catalog params (xray.py XRAY_PULSARS): alpha (src ct/s), beta (bg ct/s),
# duty (pulse FWHM fraction), P0 (s)
CAT = {}
for _name, _P0ms, _ra, _dec, _al, _be, _du in xray.XRAY_PULSARS:
    if _name in PSRS:
        CAT[_name] = dict(alpha=_al, beta=_be, duty=_du, P0=_P0ms * 1e-3)


def cr_pred(psr, T):
    c = CAT[psr]
    return xray.toa_precision(c['alpha'], c['beta'], c['duty'], c['P0'], T)

# quality cuts for a "valid" dwell TOA
Q = dict(min_n=50, min_exp=300.0, min_htest=20.0)


def load():
    import glob
    files = sorted(glob.glob(PILOT + '/dwells_*.csv'))
    assert files, 'no dwells_*.csv found; run pilot_pass2.py first'
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df[(df['n_phot'] >= Q['min_n']) & (df['exp_s'] >= Q['min_exp'])
            & (df['htest'] >= Q['min_htest'])
            & np.isfinite(df['dphi']) & np.isfinite(df['sigma_dphi'])].copy()
    return df


def g1_ratios(df):
    """Per-dwell measured sigma vs sim CR prediction at realized exposure."""
    out = {}
    for psr in PSRS:
        d = df[df['psr'] == psr]
        if len(d) == 0:
            out[psr] = None
            continue
        pred = np.array([cr_pred(psr, e) for e in d['exp_s'].values])
        meas = d['sigma_dphi'].values * d['P0_s'].values
        ratio = meas / pred
        out[psr] = dict(n=len(d), med_ratio=float(np.median(ratio)),
                        p10=float(np.percentile(ratio, 10)),
                        p90=float(np.percentile(ratio, 90)),
                        frac_lt2=float((ratio < 2).mean()),
                        med_sig_meas_ns=float(np.median(meas) * 1e9),
                        med_sig_pred_ns=float(np.median(pred) * 1e9))
    return out


def split_half_check(df):
    """Empirical per-dwell sigma: split each dwell's photons in two halves,
    ML phase each half, compare half-difference scatter to formal sigma.
    Returns per-pulsar median(empirical/formal)."""
    # needs photon phases per dwell -> recompute for a subsample of dwells
    # (expensive); do up to 10 dwells per pulsar.
    import ast
    res = {}
    for psr in PSRS:
        d = df[df['psr'] == psr].sort_values('n_phot', ascending=False).head(10)
        if len(d) < 8:
            res[psr] = None
            continue
        z = np.load(PILOT + f'/templates/{psr}_template.npz')
        tmpl = {'a': z['a'], 'b': z['b'], 'n_harm': int(z['n_harm'])}
        band = tuple(int(x) for x in z['band'])
        er = []
        for _, r in d.iterrows():
            try:
                ph = dwell_phases(psr, r['obsid'], band, r['mjd_mid'],
                                  r['exp_s'])
            except Exception:
                continue
            if ph is None or len(ph) < 100:
                continue
            rng = np.random.default_rng(7)
            idx = rng.permutation(len(ph))
            h1, h2 = ph[idx[:len(idx)//2]], ph[idx[len(idx)//2:]]
            p1, s1, _, _ = pt.ml_phase(h1, tmpl)
            p2, s2, _, _ = pt.ml_phase(h2, tmpl)
            dd = (p1 - p2 + 0.5) % 1.0 - 0.5
            emp = abs(dd) / np.sqrt(2)  # per-half sigma -> full-dwell equiv
            form = r['sigma_dphi']
            er.append(emp / form)
        res[psr] = dict(n=len(er),
                        med=float(np.median(er)) if er else np.nan)
    return res


def dwell_phases(psr, obsid, band, mjd_mid, exp_s):
    """Recompute photon phases for one dwell (for split-half check)."""
    from pint.observatory.satellite_obs import get_satellite_observatory
    d = os.path.join(PILOT, 'data', obsid)
    ev = os.path.join(d, f'ni{obsid}_0mpu7_cl.evt.gz')
    orb = os.path.join(d, f'ni{obsid}.orb.gz')
    if not os.path.exists(ev):
        ev = ev[:-3]
    if not os.path.exists(orb):
        orb = orb[:-3]
    blo, bhi = band
    times, pi, mjdref = pt.read_events(ev, blo, bhi)
    gs, ge = pt.read_gti(ev)
    dwells = pt.make_dwells(gs, ge, gap_merge=600.0, max_len=3600.0,
                            min_exp=300.0)
    # find the dwell matching mjd_mid
    best, bd = None, 1e9
    for w in dwells:
        m = mjdref + (w['t0'] + w['t1']) / 2 / 86400.0
        if abs(m - mjd_mid) < bd:
            bd, best = abs(m - mjd_mid), w
    if best is None or bd > 0.01:
        return None
    didx = pt.assign_dwells(times, dwells)
    di = dwells.index(best)
    ii = np.where(didx == di)[0]
    if len(ii) < 100:
        return None
    gi = pt.grid_indices(times, didx, per_dwell=64)
    gi_d = gi[np.isin(gi, ii)]
    if len(gi_d) < 8:
        return None
    pars = {'J0437-4715': '/home/hatch/workspace/prtp/hidden_files/nanograv15yr/extracted/narrowband/par/J0437-4715_PINT_20220301.nb.par',
            'J0030+0451': '/home/hatch/workspace/prtp/hidden_files/nanograv15yr/extracted/narrowband/par/J0030+0451_PINT_20220302.nb.par',
            'J0218+4232': PILOT + '/par/J0218+4232_tdb.par',
            'B1821-24': PILOT + '/par/J1824-2452A_tdb.par'}
    grid_fits = f'/tmp/sh_{obsid}.fits'
    pt.write_grid_fits(ev, times[gi_d], grid_fits)
    try:
        get_satellite_observatory('NICER', orb, overwrite=True)
        gphase, F0 = pt.pint_grid_phases(grid_fits, orb, pars[psr])
    finally:
        if os.path.exists(grid_fits):
            os.remove(grid_fits)
    ph = pt.interp_phases(times[ii], times[gi_d], gphase, F0)
    ph = ph[np.isfinite(ph)] % 1.0
    return ph if len(ph) >= 100 else None


def n1_duty(df, bin_d=0.25, span=(58300.0, 59030.0)):
    """On-source fraction: bins with >=1 valid dwell, and exposure/span."""
    t0, t1 = span
    nb = int((t1 - t0) / bin_d)
    occ_any = np.zeros(nb, bool)
    occ = {p: np.zeros(nb, bool) for p in PSRS}
    exp_tot = 0.0
    per_psr_exp = {p: 0.0 for p in PSRS}
    for _, r in df.iterrows():
        b = int((r['mjd_mid'] - t0) / bin_d)
        if 0 <= b < nb:
            occ_any[b] = True
            occ[r['psr']][b] = True
        exp_tot += r['exp_s']
        per_psr_exp[r['psr']] += r['exp_s']
    span_s = (t1 - t0) * 86400.0
    return dict(bin_d=bin_d,
                frac_bins_any=float(occ_any.mean()),
                frac_bins={p: float(occ[p].mean()) for p in PSRS},
                frac_exp=float(exp_tot / span_s),
                frac_exp_psr={p: float(per_psr_exp[p] / span_s)
                              for p in PSRS},
                n_dwells=len(df))


def whiteness(df):
    """Per-pulsar residual whiteness: lag-1 autocorr and chi2/dof of the
    residual series around its weighted mean (red noise expected, so this
    is descriptive, not a pass/fail). Also cross-pulsar bin correlation."""
    out = {}
    for psr in PSRS:
        d = df[df['psr'] == psr].sort_values('mjd_mid')
        if len(d) < 10:
            out[psr] = None
            continue
        # unwrap phase in time order, remove weighted mean, convert to seconds
        ph = np.unwrap(d['dphi'].values * 2 * np.pi) / (2 * np.pi)
        sig = d['sigma_dphi'].values * d['P0_s'].values
        w = 1 / sig ** 2
        r = (ph - np.average(ph, weights=w)) * d['P0_s'].values
        rc = r - np.average(r, weights=w)
        lag1 = float(np.corrcoef(rc[:-1], rc[1:])[0, 1]) if len(rc) > 2 else np.nan
        chi2dof = float(np.sum(w * rc ** 2) / (len(rc) - 1))
        out[psr] = dict(n=len(d), lag1=lag1, chi2_dof=chi2dof,
                        rms_ns=float(np.sqrt(np.mean(rc**2)) * 1e9),
                        med_sig_ns=float(np.median(
                            d['sigma_dphi'].values *
                            d['P0_s'].values) * 1e9))
    return out


def main():
    df = load()
    print('valid dwells:', len(df), df['psr'].value_counts().to_dict())
    g1 = g1_ratios(df)
    print('\nG1 (measured/predicted sigma):')
    for p in PSRS:
        print(' ', p, g1[p])
    n1 = n1_duty(df)
    print('\nN1:', json.dumps(n1, indent=1)[:600])
    wh = whiteness(df)
    print('\nwhiteness:')
    for p in PSRS:
        print(' ', p, wh[p])
    print('\nsplit-half empirical/formal sigma (subsample)...')
    import os as _os
    if _os.environ.get('SKIP_SPLITHALF'):
        sh = {p: None for p in PSRS}
        print('  skipped (SKIP_SPLITHALF)')
    else:
        sh = split_half_check(df)
        for p in PSRS:
            print(' ', p, sh[p])
    with open(PILOT + '/pilot_g1n1.json', 'w') as f:
        json.dump(dict(g1=g1, n1=n1, whiteness=wh, split_half=sh,
                       quality_cuts=Q), f, indent=1)
    print('\nsaved pilot_g1n1.json')
    # G1 figure
    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs, labels = [], []
    for p in PSRS:
        d = df[df['psr'] == p]
        if len(d) == 0:
            continue
        pred = np.array([cr_pred(p, e) for e in d['exp_s'].values])
        meas = d['sigma_dphi'].values * d['P0_s'].values
        xs.append(meas / pred)
        labels.append(f'{p} (n={len(d)})')
    ax.boxplot(xs, labels=labels, showfliers=False)
    ax.axhline(1.0, color='k', ls='--', lw=1)
    ax.axhline(2.0, color='r', ls='--', lw=1, label='G1 2x bound')
    ax.set_ylabel('measured sigma / sim CR prediction')
    ax.set_title('G1: per-dwell TOA precision vs simulation')
    ax.legend()
    fig.tight_layout()
    fig.savefig(PILOT + '/fig_g1.png', dpi=90)
    print('saved fig_g1.png')


if __name__ == '__main__':
    main()
