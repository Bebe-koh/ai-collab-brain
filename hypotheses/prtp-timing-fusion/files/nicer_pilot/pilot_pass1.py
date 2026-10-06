"""Pass 1: per-pulsar energy-band selection + frozen Fourier template.

For a given pulsar: take up to N ObsIDs spread across the pilot span
(already-downloaded only), compute PINT phases for PI 20-300 photons via
the sparse-grid + cubic interpolation in pilot_toa, stack phases in
candidate bands, H-test each band, keep the best band, build and save the
Fourier template (n_harm=12).

Usage: python pilot_pass1.py J0437-4715
Saves: templates/<psr>_template.npz  (a, b, n_harm, band, htests, n_phot)
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
BANDS = [(30, 100), (30, 150), (30, 200), (50, 200)]  # PI: 10 eV units
N_OBS = 40


def obsids_for(psr, n=N_OBS):
    rows = []
    with open(PILOT + '/obsids.csv') as f:
        for r in csv.DictReader(f):
            if r['psr'] == psr:
                d = os.path.join(DATA, r['obsid'])
                if os.path.isdir(d):
                    rows.append(r)
    rows.sort(key=lambda r: float(r['mjd']))
    if len(rows) <= n:
        return rows
    idx = np.linspace(0, len(rows) - 1, n).astype(int)
    return [rows[i] for i in idx]


def process_one(psr, obsid):
    d = os.path.join(DATA, obsid)
    ev = os.path.join(d, f'ni{obsid}_0mpu7_cl.evt.gz')
    orb = os.path.join(d, f'ni{obsid}.orb.gz')
    if not (os.path.exists(ev) and os.path.exists(orb)):
        # try uncompressed variants
        ev2 = ev[:-3]
        orb2 = orb[:-3]
        if os.path.exists(ev2):
            ev = ev2
        if os.path.exists(orb2):
            orb = orb2
    if not (os.path.exists(ev) and os.path.exists(orb)):
        return None
    times, pi, _mjdref = pt.read_events(ev, 20, 300)
    if len(times) < 200:
        return None
    gs, ge = pt.read_gti(ev)
    dwells = pt.make_dwells(gs, ge, gap_merge=600.0, max_len=1e9,
                            min_exp=50.0)
    if not dwells:
        return None
    didx = pt.assign_dwells(times, dwells)
    gi = pt.grid_indices(times, didx, per_dwell=64)
    if len(gi) < 8:
        return None
    grid_fits = f'/tmp/grid_{obsid}.fits'
    pt.write_grid_fits(ev, times[gi], grid_fits)
    gphase, F0 = pt.pint_grid_phases(grid_fits, orb, PARS[psr])
    phases = pt.interp_phases(times, times[gi], gphase, F0)
    # sanity: interpolation reproduces grid phases
    chk = pt.interp_phases(times[gi], times[gi], gphase, F0)
    err = np.abs(((chk - gphase) % 1.0 + 0.5) % 1.0 - 0.5).max()
    if err > 1e-3:  # float64 round-trip of ~1e10-cycle phases; not physics
        raise RuntimeError(f'interp self-check failed: {err}')
    os.remove(grid_fits)
    fin = np.isfinite(phases)
    return phases[fin] % 1.0, pi[fin]


def main():
    psr = sys.argv[1]
    rows = obsids_for(psr)
    print(f'{psr}: {len(rows)} obsids for template', flush=True)
    all_ph, all_pi = [], []
    for r in rows:
        try:
            out = process_one(psr, r['obsid'])
        except Exception as e:
            print('  skip', r['obsid'], str(e)[:120], flush=True)
            continue
        if out is None:
            continue
        ph, pi = out
        all_ph.append(ph)
        all_pi.append(pi)
        print('  %s n=%d' % (r['obsid'], len(ph)), flush=True)
    phases = np.concatenate(all_ph)
    pis = np.concatenate(all_pi)
    print('total photons:', len(phases), flush=True)
    htests = []
    for blo, bhi in BANDS:
        m = (pis >= blo) & (pis <= bhi)
        H = pt.h_test(phases[m] % 1.0) if m.sum() > 100 else 0.0
        htests.append(H)
        print('  band PI %d-%d: n=%d H=%.1f' % (blo, bhi, m.sum(), H),
              flush=True)
    bi = int(np.argmax(htests))
    blo, bhi = BANDS[bi]
    m = (pis >= blo) & (pis <= bhi)
    tmpl = pt.build_template((phases[m] % 1.0), n_harm=12)
    tmpl['band'] = np.array([blo, bhi])
    tmpl['htests'] = np.array(htests)
    tmpl['bands'] = np.array(BANDS)
    os.makedirs(PILOT + '/templates', exist_ok=True)
    np.savez(PILOT + f'/templates/{psr}_template.npz', **tmpl)
    print('saved template, best band PI %d-%d H=%.1f' % (blo, bhi,
          htests[bi]), flush=True)


if __name__ == '__main__':
    main()
