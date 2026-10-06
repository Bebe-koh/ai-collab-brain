"""PRTP NICER pilot: real-data TOA extraction pipeline.

SIMULATION-FREE measurement code (operates on real NICER event data).
For each NICER ObsID of a SEXTANT pulsar:
  1. read cleaned events (astropy), apply PI (energy) cut
  2. group photons into dwells from GTIs (merge gaps < 600 s, split > 3600 s)
  3. compute PINT pulse phases on a sparse time grid per dwell (<=64 pts),
     cubic-interpolate to all photons (phase - F0*t detrended)
  4. unbinned maximum-likelihood phase vs a frozen Fourier template
     -> per-dwell phase offset, formal sigma, log-likelihood (significance)

Two-pass workflow:
  Pass 1 (pilot_template.py): stack photons from a subset of ObsIDs per
      pulsar, choose energy band by H-test, build frozen Fourier template.
  Pass 2 (pilot_produce.py): all ObsIDs with frozen band+template
      -> dwells.csv (one row per dwell).

All exploratory / simulation-only. No flight claims.
"""
import numpy as np
from scipy.interpolate import CubicSpline

# ---------------------------------------------------------------------------
# event / GTI I/O (astropy; works on .gz directly)
# ---------------------------------------------------------------------------

def read_events(evt_path, pi_lo, pi_hi):
    """Return TIME (MET s, float64) and PI for photons in the PI band,
    plus the file's MJDREF (MJDREFI+MJDREFF) for TIME->MJD conversion."""
    from astropy.io import fits
    with fits.open(evt_path) as h:
        ev = h['EVENTS'].data
        hdr = h['EVENTS'].header
        mjdref = float(hdr.get('MJDREFI', 56658)) + \
            float(hdr.get('MJDREFF', 0.0))
        pi = ev['PI'].astype(np.float64)
        m = (pi >= pi_lo) & (pi <= pi_hi)
        t = ev['TIME'][m].astype(np.float64)
        order = np.argsort(t, kind='stable')
        return t[order], pi[m][order], mjdref


def read_gti(evt_path):
    """Return (START, STOP) arrays (MET s) of the GTI extension."""
    from astropy.io import fits
    with fits.open(evt_path) as h:
        g = h['GTI'].data
        s = g['START'].astype(np.float64)
        e = g['STOP'].astype(np.float64)
    order = np.argsort(s, kind='stable')
    return s[order], e[order]


# ---------------------------------------------------------------------------
# dwell construction from GTIs
# ---------------------------------------------------------------------------

def make_dwells(gti_start, gti_stop, gap_merge=600.0, max_len=3600.0,
                min_exp=300.0):
    """Merge GTIs separated by < gap_merge s into dwells; split dwells
    longer than max_len; drop dwells with total GTI exposure < min_exp.
    Returns list of dicts {t0, t1, exp} (MET s)."""
    dwells = []
    if len(gti_start) == 0:
        return dwells
    cs, ce = gti_start[0], gti_stop[0]
    for s, e in zip(gti_start[1:], gti_stop[1:]):
        if s - ce <= gap_merge:
            ce = max(ce, e)
        else:
            dwells.append((cs, ce))
            cs, ce = s, e
    dwells.append((cs, ce))
    out = []
    for cs, ce in dwells:
        # exposure = sum of GTI overlap, clipped per-GTI before summing
        ov = np.clip(np.minimum(gti_stop, ce) - np.maximum(gti_start, cs),
                     0.0, None)
        # split long dwells
        n = max(1, int(np.ceil((ce - cs) / max_len)))
        for k in range(n):
            a = cs + (ce - cs) * k / n
            b = cs + (ce - cs) * (k + 1) / n
            ov2 = np.clip(np.minimum(gti_stop, b) - np.maximum(gti_start, a),
                          0.0, None)
            e2 = float(ov2.sum())
            if e2 >= min_exp:
                out.append({'t0': float(a), 't1': float(b), 'exp': e2})
    return out


def assign_dwells(times, dwells):
    """dwell index per photon (-1 if outside all dwells)."""
    idx = np.full(len(times), -1, dtype=np.int64)
    for d, w in enumerate(dwells):
        m = (times >= w['t0']) & (times <= w['t1'])
        idx[m] = d
    return idx


# ---------------------------------------------------------------------------
# PINT phase grid + cubic interpolation
# ---------------------------------------------------------------------------

def grid_indices(times, dwell_idx, per_dwell=64):
    """Evenly-spaced-in-TIME photon indices per dwell for the PINT grid.
    Guarantees time coverage of each dwell (index-spacing would starve
    short GTIs)."""
    sel = []
    for d in np.unique(dwell_idx):
        if d < 0:
            continue
        ii = np.where(dwell_idx == d)[0]
        if len(ii) < 8:
            continue
        t = times[ii]
        t0, t1 = t.min(), t.max()
        k = min(per_dwell, len(ii))
        tg = np.linspace(t0, t1, k)
        # nearest photon at or after each grid time
        pos = np.searchsorted(t, tg)
        pos = np.clip(pos, 0, len(ii) - 1)
        sel.append(ii[np.unique(pos)])
    return np.concatenate(sel) if sel else np.array([], dtype=np.int64)


def time_grid_indices(times, t0, t1, n=256):
    """Evenly-spaced-in-time photon indices over [t0, t1] (for Pass 1)."""
    tg = np.linspace(t0, t1, n)
    pos = np.searchsorted(times, tg)
    pos = np.clip(pos, 0, len(times) - 1)
    return np.unique(pos)


def write_grid_fits(src_evt, times_sel, out_path):
    """Write a minimal EVENTS FITS with the selected photons (by TIME
    matching against the source file's full PI range). Returns n written."""
    from astropy.io import fits
    with fits.open(src_evt) as h:
        ev = h['EVENTS'].data
        hdr = h['EVENTS'].header
        tall = ev['TIME'].astype(np.float64)
    # match selected times to source rows (times came from this file)
    order = np.argsort(tall, kind='stable')
    pos = np.searchsorted(tall[order], times_sel)
    pos = np.clip(pos, 0, len(order) - 1)
    rows = order[pos]
    # verify match
    if not np.allclose(tall[rows], times_sel, atol=1e-3):
        raise RuntimeError('grid TIME match failed')
    with fits.open(src_evt) as h:
        ev = h['EVENTS'].data
        hdr = h['EVENTS'].header
        sub = ev[rows]
        hdu = fits.BinTableHDU(sub, header=hdr, name='EVENTS')
        hdul = fits.HDUList([fits.PrimaryHDU(), hdu])
        hdul.writeto(out_path, overwrite=True)
    return len(rows)


_model_cache = {}


def pint_grid_phases(grid_fits, orb_path, par_path):
    """Register NICER observatory, load grid photons, return
    (times_met, phase_total) with phase_total = int+frac (float, unwrapped
    by construction since int part is monotonic). The PINT model is cached
    per par file (read-only use)."""
    from pint.event_toas import get_NICER_TOAs
    from pint.observatory.satellite_obs import get_satellite_observatory
    import pint.models as pm
    get_satellite_observatory('NICER', orb_path, overwrite=True)
    toas = get_NICER_TOAs(grid_fits, planets=True)
    if par_path not in _model_cache:
        _model_cache[par_path] = pm.get_model(par_path)
    model = _model_cache[par_path]
    ph = model.phase(toas, abs_phase=True)
    total = ph.int.value.astype(np.float64) + ph.frac.value.astype(np.float64)
    return total, model.F0.value


def interp_phases(times, grid_times, grid_phase, F0):
    """Cubic-spline interpolate total pulse phase to all photon times.
    Detrends by F0*t for numerical accuracy. Returns fractional phase."""
    y = grid_phase - F0 * grid_times
    cs = CubicSpline(grid_times, y, extrapolate=False)
    tot = F0 * times + cs(times)
    return tot % 1.0


# ---------------------------------------------------------------------------
# Fourier template + unbinned ML phase
# ---------------------------------------------------------------------------

def build_template(phases, n_bins=128, n_harm=12, min_harm=1):
    """Stack phases -> Fourier-smoothed template normalized to mean 1.
    Returns dict with cos/sin coefficients (k=1..n_harm) and diagnostics."""
    hist, _ = np.histogram(phases, bins=n_bins, range=(0, 1))
    n = len(phases)
    # FFT of the histogram (mean-subtracted)
    F = np.fft.rfft(hist - hist.mean())
    a = np.zeros(n_harm + 1)
    b = np.zeros(n_harm + 1)
    for k in range(min_harm, min(n_harm, len(F) - 1) + 1):
        # hist = mean*(1 + sum ...) ; convert FFT bins to Fourier coeffs
        # rfft[k] = sum_j h_j exp(-2 pi i k j / n_bins)
        # h_j/mean - 1 = sum_k 2|F_k|/(n_bins*mean) cos(2 pi k j/n - arg)
        c = F[k] / (n_bins * hist.mean()) * 2.0
        a[k] = c.real
        b[k] = c.imag
    return {'a': a, 'b': b, 'n_harm': n_harm, 'n_phot': n,
            'n_bins': n_bins}


def template_eval(phi, tmpl):
    """Evaluate normalized template at phases phi (array, [0,1))."""
    a, b = tmpl['a'], tmpl['b']
    out = np.ones_like(phi)
    for k in range(1, tmpl['n_harm'] + 1):
        if a[k] == 0 and b[k] == 0:
            continue
        ang = 2.0 * np.pi * k * phi
        out = out + a[k] * np.cos(ang) + b[k] * np.sin(ang)
    return np.clip(out, 1e-6, None)


def ml_phase(phases, tmpl, n_grid=720):
    """Unbinned ML phase shift of photons vs template.
    Returns (dphi, sigma_dphi, loglike_gain, n). dphi in [0,1)."""
    n = len(phases)
    if n < 10:
        return np.nan, np.nan, 0.0, n
    deltas = np.arange(n_grid) / n_grid
    # L(delta) = sum log T((phi - delta) % 1); vectorize over grid
    # memory: n_grid x n -- chunk if large
    best = -np.inf
    L = np.empty(n_grid)
    chunk = 72
    for c0 in range(0, n_grid, chunk):
        c1 = min(n_grid, c0 + chunk)
        dd = deltas[c0:c1]
        arg = (phases[None, :] - dd[:, None]) % 1.0
        L[c0:c1] = np.log(template_eval(arg, tmpl)).sum(axis=1)
    k = int(np.argmax(L))
    # parabolic refinement on the grid
    y0, y1, y2 = L[k - 1], L[k], L[(k + 1) % n_grid]
    den = (y0 - 2 * y1 + y2)
    dk = 0.5 * (y0 - y2) / den if den < 0 else 0.0
    dk = float(np.clip(dk, -1.0, 1.0))
    dphi = ((k + dk) / n_grid) % 1.0
    # curvature at max from the parabola (in units of 1/cycle^2)
    curv = -den * n_grid * n_grid  # d^2 L / d delta^2 (delta in cycles)
    sigma = 1.0 / np.sqrt(curv) if curv > 0 else np.nan
    gain = float(y1 - 0.0)  # vs uniform template (log T = 0)
    return dphi, sigma, gain, n


def h_test(phases, m_max=20):
    """H-test statistic for pulsation significance (de Jager et al. 1989).
    Z^2_m = (2/N) sum_k |sum_j exp(2 pi i k phi_j)|^2 ; H = max_m(Z^2_m-4m+4).
    Returns 0 under no pulsation; H~25+ is a solid detection."""
    ph = np.asarray(phases)
    ph = ph[np.isfinite(ph)] % 1.0
    n = len(ph)
    if n < 10:
        return 0.0
    Z2 = 0.0
    H = 0.0
    for m in range(1, m_max + 1):
        ang = 2.0 * np.pi * m * ph
        Z2 += (2.0 / n) * (np.cos(ang).sum() ** 2 + np.sin(ang).sum() ** 2)
        H = max(H, Z2 - 4 * m + 4)
    return H
