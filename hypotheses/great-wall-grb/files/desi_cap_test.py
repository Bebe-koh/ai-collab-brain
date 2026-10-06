#!/usr/bin/env python3
"""DESI DR1 QSO fixed-cap overdensity test for the HCBGW candidate.

Cap: center RA=215.94 deg, Dec=+49.51 deg, radius 50 deg, 1.6 < z < 2.1.
Statistic: delta = N_cap/N_exp - 1, with N_exp from DESI DR1 LSS randoms
(mask-conditioned). Null: same statistic over control caps placed randomly
in the NGC footprint (empirical look-elsewhere + systematics control).

Products: desi_cap_result.json, control_caps.csv, plots.
"""
import json, os, sys, time
import numpy as np
from astropy.io import fits

BASE = os.path.expanduser("~/workspace/grb")
DESI = os.path.join(BASE, "desi_data")
OUT = os.path.join(BASE, "crosscheck_products")
os.makedirs(OUT, exist_ok=True)

CAP_RA, CAP_DEC, CAP_R = 215.94, 49.51, 50.0
ZLO, ZHI = 1.6, 2.1
RNG = np.random.default_rng(42)

def unit_vectors(ra_deg, dec_deg):
    ra = np.deg2rad(ra_deg); dec = np.deg2rad(dec_deg)
    return np.stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)], axis=1)

def cap_mask(ra, dec, cra, cdec, rad):
    v = unit_vectors(ra, dec)
    c = unit_vectors(np.array([cra]), np.array([cdec]))[0]
    cosang = v @ c
    return cosang >= np.cos(np.deg2rad(rad))

def load_dat(path):
    d = fits.getdata(path, 1)
    return d

def load_ran(path):
    d = fits.getdata(path, 1)
    return d

def main():
    t0 = time.time()
    print("loading NGC data...", flush=True)
    dat = load_dat(os.path.join(DESI, "QSO_NGC_clustering.dat.fits"))
    ra, dec, z, w = dat['RA'], dat['DEC'], dat['Z'], dat['WEIGHT']
    print(f"  {len(ra)} quasars", flush=True)

    print("loading randoms...", flush=True)
    rra_list, rdec_list, rw_list = [], [], []
    i = 0
    while True:
        p = os.path.join(DESI, f"QSO_NGC_{i}_clustering.ran.fits")
        if not os.path.exists(p):
            break
        r = load_ran(p)
        print(f"  file {i}: {len(r)} rows, cols={r.columns.names[:8]}", flush=True)
        # weight column: prefer WEIGHT, fall back to ones
        rw = r['WEIGHT'] if 'WEIGHT' in r.columns.names else np.ones(len(r))
        rra_list.append(r['RA']); rdec_list.append(r['DEC']); rw_list.append(rw)
        i += 1
    rra = np.concatenate(rra_list); rdec = np.concatenate(rdec_list); rw = np.concatenate(rw_list)
    print(f"  total randoms: {len(rra)}", flush=True)
    print("  precomputing unit vectors...", flush=True)
    vr_all = unit_vectors(rra, rdec)
    del rra_list, rdec_list, rw_list

    def cap_mask_v(v, cra, cdec, rad):
        c = unit_vectors(np.array([cra]), np.array([cdec]))[0]
        return (v @ c) >= np.cos(np.deg2rad(rad))

    # --- data in slice ---
    in_slice = (z > ZLO) & (z < ZHI)
    ra_s, dec_s, w_s = ra[in_slice], dec[in_slice], w[in_slice]
    N_data_slice = w_s.sum()
    print(f"data in slice {ZLO}<z<{ZHI}: weighted N = {N_data_slice:.1f} ({in_slice.sum()} objects)", flush=True)

    # --- random angular selection function ---
    # f_cap = weighted random fraction inside cap (all z; random z shuffled from data)
    in_cap_r = cap_mask_v(vr_all, CAP_RA, CAP_DEC, CAP_R)
    f_cap = rw[in_cap_r].sum() / rw.sum()
    N_exp = f_cap * N_data_slice
    v_s = unit_vectors(ra_s, dec_s)
    in_cap_d = cap_mask_v(v_s, CAP_RA, CAP_DEC, CAP_R)
    N_cap = w_s[in_cap_d].sum()
    n_cap_raw = in_cap_d.sum()
    delta = N_cap / N_exp - 1.0
    # Poisson error from raw counts
    sig_poisson = np.sqrt(n_cap_raw) / N_exp
    print(f"HCB cap: N_cap(weighted)={N_cap:.1f} (raw {n_cap_raw}), N_exp={N_exp:.1f}, delta={delta:+.4f} +- {sig_poisson:.4f} (poisson)", flush=True)
    # footprint overlap: fraction of cap disc covered by footprint
    print(f"  cap random coverage f_cap={f_cap:.4f}", flush=True)

    # --- control caps: random centers in NGC footprint ---
    # draw centers uniform on sphere within RA/DEC box, keep those with decent coverage
    n_try, kept = 4000, 0
    ctrl = []
    # precompute unit vectors for randoms for fast coverage eval? use cap_mask directly
    min_nexp_frac = 0.2
    ras = RNG.uniform(90, 297, n_try)
    # uniform on sphere: sin(dec) uniform
    sindec = RNG.uniform(np.sin(np.deg2rad(-10)), np.sin(np.deg2rad(79)), n_try)
    decs = np.rad2deg(np.arcsin(sindec))
    print("placing control caps...", flush=True)
    for cra, cdec in zip(ras, decs):
        m = cap_mask_v(vr_all, cra, cdec, CAP_R)
        fc = rw[m].sum() / rw.sum()
        ne = fc * N_data_slice
        if ne < min_nexp_frac * N_exp:
            continue
        md = cap_mask_v(v_s, cra, cdec, CAP_R)
        nc = w_s[md].sum()
        dlt = nc / ne - 1.0
        ctrl.append((cra, cdec, nc, ne, dlt, md.sum()))
        kept += 1
        if kept >= 500:
            break
    ctrl = np.array(ctrl, dtype=[('ra', float), ('dec', float), ('ncap', float),
                                ('nexp', float), ('delta', float), ('nraw', float)])
    print(f"  kept {len(ctrl)} control caps", flush=True)
    np.savetxt(os.path.join(OUT, "control_caps.csv"), ctrl,
               delimiter=",", header="ra,dec,ncap_weighted,nexp,delta,nraw", fmt="%.4f")

    dvals = ctrl['delta']
    p_fixed = np.mean(dvals >= delta)  # look-elsewhere-corrected empirical p
    # also gaussian-ish z-score vs control distribution
    mu, sd = dvals.mean(), dvals.std(ddof=1)
    print(f"control delta: mean={mu:+.4f} sd={sd:.4f}", flush=True)
    print(f"HCB delta={delta:+.4f} -> z={(delta-mu)/sd:+.2f} sigma vs controls; empirical p(>=HCB)={p_fixed:.4f}", flush=True)

    # --- east/west half split (exploratory localization) ---
    # split by position angle around cap center: use tangent-plane x coordinate
    # east-west: project onto direction of increasing RA at center
    # e_RA = (-sin(ra0), cos(ra0), 0)
    ra0 = np.deg2rad(CAP_RA)
    e_ra = np.array([-np.sin(ra0), np.cos(ra0), 0.0])
    x = v_s @ e_ra
    xr = vr_all @ e_ra
    halves = {}
    for name, sel_d, sel_r in [("east", x > 0, xr > 0), ("west", x <= 0, xr <= 0)]:
        m = in_cap_d & sel_d
        nc = w_s[m].sum()
        mr = in_cap_r & sel_r
        fe = rw[mr].sum() / rw.sum()
        ne = fe * N_data_slice
        halves[name] = dict(ncap=nc, nexp=ne, delta=nc/ne - 1, nraw=int(m.sum()))
        print(f"  half {name}: N={nc:.1f} exp={ne:.1f} delta={nc/ne-1:+.4f}", flush=True)

    res = dict(
        cap=dict(ra=CAP_RA, dec=CAP_DEC, radius_deg=CAP_R, zlo=ZLO, zhi=ZHI),
        n_data_slice_weighted=float(N_data_slice), n_data_slice_raw=int(in_slice.sum()),
        n_cap_weighted=float(N_cap), n_cap_raw=int(n_cap_raw), n_exp=float(N_exp),
        delta=float(delta), poisson_sigma=float(sig_poisson),
        control=dict(n=len(ctrl), mean=float(mu), sd=float(sd),
                     z_vs_controls=float((delta-mu)/sd), empirical_p=float(p_fixed)),
        halves={k: {kk: float(vv) for kk, vv in v.items()} for k, v in halves.items()},
        n_random_files=i, n_randoms=int(len(rra)),
        runtime_s=round(time.time()-t0, 1),
    )
    with open(os.path.join(OUT, "desi_cap_result.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("wrote desi_cap_result.json", flush=True)

if __name__ == "__main__":
    main()
