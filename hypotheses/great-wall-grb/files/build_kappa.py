#!/usr/bin/env python3
"""Build Planck PR4 (NPIPE, PR3-like pipeline) kappa map from klm alms.
Subtracts mean field, synthesizes NSIDE=1024 map, applies analysis mask.
Saves kappa_pr4_n1024.npy + mask_n1024.npy
"""
import os, time
import numpy as np
import healpy as hp
from astropy.io import fits

BASE = os.path.expanduser("~/workspace/grb")
PV = os.path.join(BASE, "PR4_variations")
OUT = os.path.join(BASE, "crosscheck_products")
os.makedirs(OUT, exist_ok=True)
NS = 1024
LMAX = 2048

def read_alm(path):
    d = fits.getdata(path, 1)
    idx = d['index'].astype(np.int64) - 1  # 1-based Fortran: idx = l^2 + l + m + 1
    l = np.floor(np.sqrt(idx)).astype(np.int64)
    m = idx - l * l - l
    assert m.min() >= 0 and l.max() <= LMAX, (m.min(), l.max())
    alm = np.zeros(hp.Alm.getsize(LMAX), dtype=np.complex128)
    alm[hp.Alm.getidx(LMAX, l, m)] = d['real'] + 1j * d['imag']
    return alm

t0 = time.time()
print("reading alms...", flush=True)
alm_dat = read_alm(os.path.join(PV, "PR42018like_klm_dat_MV.fits"))
alm_mf = read_alm(os.path.join(PV, "PR42018like_klm_mf_MV.fits"))
alm = alm_dat - alm_mf
print(f"  alm ready in {time.time()-t0:.0f}s", flush=True)

print("synthesizing map...", flush=True)
kmap = hp.alm2map(alm, NS, lmax=LMAX, verbose=False)
print(f"  map: mean={kmap.mean():.3e} std={kmap.std():.3e}", flush=True)

print("reading mask...", flush=True)
md = fits.getdata(os.path.join(PV, "mask.fits.gz"), 1)
mask2048 = md['T'].reshape(-1).astype(np.float64)  # 12*2048^2 bool
mask = hp.ud_grade(mask2048, NS, order_in='RING', order_out='RING')
print(f"  mask sky frac: {(mask > 0.5).mean():.3f}", flush=True)

np.save(os.path.join(OUT, "kappa_pr4_n1024.npy"), kmap.astype(np.float32))
np.save(os.path.join(OUT, "mask_n1024.npy"), (mask > 0.5).astype(np.uint8))
print(f"saved. total {time.time()-t0:.0f}s", flush=True)
