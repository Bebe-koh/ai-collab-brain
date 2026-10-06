"""Pass 2: production per-dwell TOA extraction with frozen templates.

For every ObsID in obsids.csv (downloaded only):
  read events in the frozen PI band -> dwells from GTIs -> PINT phase grid
  -> interpolate -> per-dwell unbinned ML phase vs frozen template.
Saves dwells.csv: psr, obsid, mjd_mid, exp_s, n_phot, dphi, sigma_dphi,
gain, htest, P0_s.

Usage: python pilot_pass2.py [psr]   (default: all four)
Progress is checkpointed to dwells_partial.csv every 25 ObsIDs.
"""
import sys, os, csv, warnings
warnings.filterwarnings('ignore')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot_toa as pt

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
DATA = PILOT + '/data'
PARS = {
    'J0437-4715': '/home/hatch/workspace/prtp/hidden_files/nanograv15yr/extracted/narrowband/par/J0437-4715_PINT_20220301.nb.par',
    'J0030+0451': '/home/hatch/workspace/prtp/hidden_files/nanograv15yr/extracted/narrowband/par/J0030+0451_PINT_20220302.nb.par',
    'J0218+4232': PILOT + '/par/J0218+4232_tdb.par',
    'B1821-24': PILOT + '/par/J1824-2452A_tdb.par',
}
P0 = {}
def get_P0():
    import re
    for psr, par in PARS.items():
        with open(par) as f:
            for line in f:
                p = line.split()
                if len(p) >= 2 and p[0] == 'F0':
                    P0[psr] = 1.0 / float(p[1])
                    break
get_P0()
# MJDREF comes from each file header (read_events); no global constant.


def load_template(psr):
    z = np.load(PILOT + f'/templates/{psr}_template.npz')
    tmpl = {'a': z['a'], 'b': z['b'], 'n_harm': int(z['n_harm'])}
    band = tuple(int(x) for x in z['band'])
    return tmpl, band


def process_obsid(psr, obsid, tmpl, band):
    d = os.path.join(DATA, obsid)
    ev = os.path.join(d, f'ni{obsid}_0mpu7_cl.evt.gz')
    orb = os.path.join(d, f'ni{obsid}.orb.gz')
    if not os.path.exists(ev):
        ev = ev[:-3]
    if not os.path.exists(orb):
        orb = orb[:-3]
    if not (os.path.exists(ev) and os.path.exists(orb)):
        return []
    blo, bhi = band
    times, pi, mjdref = pt.read_events(ev, blo, bhi)
    if len(times) < 50:
        return []
    gs, ge = pt.read_gti(ev)
    dwells = pt.make_dwells(gs, ge, gap_merge=600.0, max_len=3600.0,
                            min_exp=300.0)
    if not dwells:
        return []
    didx = pt.assign_dwells(times, dwells)
    gi = pt.grid_indices(times, didx, per_dwell=16)
    if len(gi) < 8:
        return []
    grid_fits = f'/tmp/grid_{obsid}.fits'
    pt.write_grid_fits(ev, times[gi], grid_fits)
    try:
        gphase, F0 = pt.pint_grid_phases(grid_fits, orb, PARS[psr])
    finally:
        if os.path.exists(grid_fits):
            os.remove(grid_fits)
    phases = pt.interp_phases(times, times[gi], gphase, F0)
    fin = np.isfinite(phases)
    out = []
    for di, w in enumerate(dwells):
        ii = np.where((didx == di) & fin)[0]
        n = len(ii)
        mjd = mjdref + (w['t0'] + w['t1']) / 2.0 / 86400.0
        rec = {'psr': psr, 'obsid': obsid, 'mjd_mid': mjd,
               'exp_s': w['exp'], 'n_phot': n, 'dphi': np.nan,
               'sigma_dphi': np.nan, 'gain': 0.0, 'htest': 0.0,
               'P0_s': P0[psr]}
        if n >= 50:
            ph = phases[ii] % 1.0
            rec['htest'] = pt.h_test(ph)
            dphi, sig, gain, _ = pt.ml_phase(ph, tmpl)
            rec['dphi'] = dphi
            rec['sigma_dphi'] = sig
            rec['gain'] = gain
        out.append(rec)
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    tag = only if only else 'all'
    subset = os.environ.get('PILOT_SUBSET', '')
    minimal = os.environ.get('PILOT_MINIMAL', '')
    if minimal:
        csv_name = '/obsids_minimal.csv'
    elif subset:
        csv_name = '/obsids_subset.csv'
    else:
        csv_name = '/obsids.csv'
    rows = []
    with open(PILOT + csv_name) as f:
        for r in csv.DictReader(f):
            if only and r['psr'] != only:
                continue
            if os.path.isdir(os.path.join(DATA, r['obsid'])):
                rows.append(r)
    psrs = sorted(set(r['psr'] for r in rows))
    tmpls = {p: load_template(p) for p in psrs}
    print('Pass 2: %d obsids, pulsars %s' % (len(rows), psrs), flush=True)
    recs = []
    for i, r in enumerate(rows):
        try:
            recs.extend(process_obsid(r['psr'], r['obsid'], *tmpls[r['psr']]))
        except Exception as e:
            print('  ERROR %s %s: %s' % (r['psr'], r['obsid'], str(e)[:150]),
                  flush=True)
        if (i + 1) % 25 == 0:
            with open(PILOT + f'/dwells_partial_{tag}.csv', 'w') as f:
                w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
                w.writeheader()
                w.writerows(recs)
            print('  %d/%d obsids, %d dwells' % (i + 1, len(rows), len(recs)),
                  flush=True)
    with open(PILOT + f'/dwells_{tag}.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    print(f'saved dwells_{tag}.csv: {len(recs)} dwells', flush=True)


if __name__ == '__main__':
    main()
