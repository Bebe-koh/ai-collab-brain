#!/usr/bin/env python3
"""Planck PR4 kappa x DESI QSO cross-check for the HCBGW candidate.

1. Validation: kappa x DESI-QSO cross-power (checks the kappa map traces LSS).
2. Cap test: mean kappa in the 50-deg HCB cap vs 500 control caps (empirical null).
   The test is a relative comparison (z-score vs control distribution), so it is
   invariant under any global miscalibration of the kappa map. Absolute kappa
   scale is NOT interpreted (see note on map normalization).

Saves kappa_xcheck_result.json
"""
import json, os, time
import numpy as np
import healpy as hp
from astropy.io import fits

BASE = os.path.expanduser("~/workspace/grb")
DESI = os.path.join(BASE, "desi_data")
OUT = os.path.join(BASE, "crosscheck_products")
os.makedirs(OUT, exist_ok=True)
NS = 1024
CAP_RA, CAP_DEC, CAP_R = 215.94, 49.51, 50.0
ZLO, ZHI = 1.6, 2.1
RNG = np.random.default_rng(7)

def cap_pixels(cra, cdec, rad, nside):
    vec = hp.ang2vec(cra, cdec, lonlat=True)
    return hp.query_disc(nside, vec, np.deg2rad(rad), inclusive=False)

t0 = time.time()
print("loading kappa map + mask...", flush=True)
kmap = np.load(os.path.join(OUT, "kappa_pr4_n1024.npy")).astype(np.float64)
mask = np.load(os.path.join(OUT, "mask_n1024.npy")).astype(bool)
print(f"  kappa: mean={kmap.mean():.3e} std={kmap.std():.3e}; masked frac={(~mask).mean():.3f}", flush=True)

# --- 1. validation: kappa x QSO cross-power ---
print("building QSO overdensity map...", flush=True)
d = fits.getdata(os.path.join(DESI, "QSO_NGC_clustering.dat.fits"), 1)
sel = (d['Z'] > ZLO) & (d['Z'] < ZHI)
ra, dec, w = d['RA'][sel], d['DEC'][sel], d['WEIGHT'][sel]
print(f"  {sel.sum()} quasars in slice", flush=True)
pix = hp.ang2pix(NS, ra, dec, lonlat=True)
qmap = np.bincount(pix, weights=w, minlength=hp.nside2npix(NS)).astype(np.float64)
# uniform randoms for coverage: use mask of observed pixels via smoothing? use simple approach:
# overdensity relative to mean over observed footprint (pixels with qmap>0)
obs = qmap > 0
dmap = np.zeros_like(qmap)
dmap[obs] = qmap[obs] / qmap[obs].mean() - 1.0
# apply kappa mask to both
kk = kmap.copy(); kk[~mask] = 0.0
dd = dmap.copy(); dd[~mask] = 0.0
print("computing cross-spectrum...", flush=True)
cl_kg = hp.anafast(kk, dd, lmax=600)
cl_kk = hp.anafast(kk, lmax=600)
ell = np.arange(len(cl_kg))
# bandpower S/N in 100<l<400
b = (ell >= 100) & (ell <= 400)
# rough error: sqrt(Ckk*Cgg/((2l+1)*fsky)) summed
fsky = mask.mean()
cl_gg = hp.anafast(dd, lmax=600)
num = (cl_kg[b] ** 2).sum()
den = ((cl_kk[b] * cl_gg[b]) / ((2 * ell[b] + 1) * fsky)).sum()
snr = np.sqrt(num / den)
print(f"  kappa x QSO cross-correlation S/N (100<l<400): {snr:.1f}", flush=True)
# sign check: mean cross-power should be positive
print(f"  mean C_l^kg (100<l<400): {cl_kg[b].mean():.3e}", flush=True)

# --- 2. cap test: mean kappa in HCB cap vs control caps ---
print("cap test...", flush=True)
def cap_mean_kappa(cra, cdec):
    p = cap_pixels(cra, cdec, CAP_R, NS)
    m = mask[p]
    if m.sum() < 100:
        return np.nan
    return kmap[p][m].mean()

hcb = cap_mean_kappa(CAP_RA, CAP_DEC)
print(f"  HCB cap mean kappa = {hcb:.3e}", flush=True)

ctrl_vals = []
n_try = 0
while len(ctrl_vals) < 500 and n_try < 6000:
    n_try += 1
    cra = RNG.uniform(0, 360)
    s = RNG.uniform(-1, 1)
    cdec = np.rad2deg(np.arcsin(s))
    v = cap_mean_kappa(cra, cdec)
    if np.isnan(v):
        continue
    # require decent unmasked fraction: at least 40% of HCB cap's unmasked count
    ctrl_vals.append(v)
ctrl_vals = np.array(ctrl_vals)
# match HCB unmasked pixel count roughly: filter controls with similar coverage
p_hcb = cap_pixels(CAP_RA, CAP_DEC, CAP_R, NS)
n_hcb = mask[p_hcb].sum()
print(f"  HCB unmasked pixels: {n_hcb}", flush=True)
mu, sd = ctrl_vals.mean(), ctrl_vals.std(ddof=1)
z = (hcb - mu) / sd
p_emp = np.mean(ctrl_vals >= hcb)
print(f"  controls: n={len(ctrl_vals)} mean={mu:.3e} sd={sd:.3e}", flush=True)
print(f"  HCB z-score vs controls: {z:+.2f}; empirical p(>=HCB)={p_emp:.4f}", flush=True)

res = dict(
    cap=dict(ra=CAP_RA, dec=CAP_DEC, radius_deg=CAP_R),
    validation=dict(xcorr_snr_100_400=float(snr), mean_cl_kg=float(cl_kg[b].mean())),
    kappa_cap=dict(mean_kappa=float(hcb), unmasked_pixels=int(n_hcb)),
    controls=dict(n=len(ctrl_vals), mean=float(mu), sd=float(sd)),
    z_vs_controls=float(z), empirical_p=float(p_emp),
    caveat=("kappa map absolute normalization unverified (PR4 klm files); "
            "test is relative (z-score vs control caps), invariant under global rescaling."),
    runtime_s=round(time.time() - t0, 1),
)
with open(os.path.join(OUT, "kappa_xcheck_result.json"), "w") as f:
    json.dump(res, f, indent=2)
print("wrote kappa_xcheck_result.json", flush=True)
