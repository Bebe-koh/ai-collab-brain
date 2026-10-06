"""Bounded null/bound experiment: CS phase-slip search in EHT 2017 Sgr A* polarimetry.

Observable (derivation note Sec.5): slip imprints -6*dchi(t) on every RL closure
triangle and +6*dchi(t) on every LR triangle, with dchi(t) = 2*pi*gamma*k *
0.5*(1+tanh((t-t0)/tau)), tau=46.9 s for Sgr A* (verified code conventions).

Pipeline (complex-domain to avoid angle wrapping):
  per (triangle, channel): z(t)=exp(i*psi(t)), derotate by circular mean
  stack per channel -> S^RL(t), S^LR(t)
  differential D(t) = S^RL * conj(S^LR): slip -> phase -12*dchi(t); intrinsic
      Q,U variability cancels to first order (moves RL,LR together)
  detection stat Z(t0) = Re[ sum_t d(t)*conj(u(t;t0)) ] / sqrt(N/2),
      d(t)=D(t)/|D(t)|, u(t)=exp(-12i*(dchi(t)-mean(dchi)))
"""
import numpy as np, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits, build_closures, POLS

TAU_SLIP = 46.9  # s, Sgr A* model input
K_WIND = 1

def dchi_template(t, t0, gamma, tau=TAU_SLIP):
    return 2*np.pi*gamma*K_WIND*0.5*(1.0+np.tanh((t-t0)/tau))

def dataset_series(rec, tris):
    """Build per-dataset stacked differential phasor series.
    Returns dict with t (s, relative), d (unit phasors), per-triangle info."""
    t0 = None
    # group rows per (tri, pol)
    series = {}
    for (tri, p), rows in tris.items():
        rows = np.array(rows, dtype=object)
        tt = np.array([r[0] for r in rows], dtype=float)   # JD
        psi = np.array([r[1] for r in rows], dtype=float)
        var = np.array([r[2] for r in rows], dtype=float)
        w = 1.0/np.maximum(var, 1e-12)
        z = np.exp(1j*psi)
        m = np.sum(w*z)/np.sum(w)
        zt = z*np.conj(m)/abs(m)
        sname = tuple(sorted(tri))
        series.setdefault(sname, {})[p] = (tt, zt, w)
    # common time origin per dataset: min over all
    tall = np.concatenate([v[0] for dd in series.values() for v in dd.values()])
    tref = tall.min()
    out = {"tref": tref, "tris": {}}
    for sname, dd in series.items():
        if "RL" not in dd or "LR" not in dd: continue
        ttr, zrl, wrl = dd["RL"]; ttl, zlr, wlr = dd["LR"]
        t_s = (ttr - tref)*86400.0
        W = float(np.sum(wrl) + np.sum(wlr))
        entry = {"t": t_s, "zrl": zrl, "wrl": wrl,
                 "zlr": zlr, "wlr": wlr, "W": W}
        for p in ("RR", "LL"):
            if p in dd:
                ttp, zp, wp = dd[p]
                entry["z"+p.lower()] = zp; entry["w"+p.lower()] = wp
        out["tris"][sname] = entry
    return out

def stack_differential(ds):
    """Stacked D(t)=S^RL conj(S^LR) on union time grid; returns t, d (unit phasors)."""
    tris = ds["tris"]
    # union grid
    tall = np.concatenate([v["t"] for v in tris.values()])
    tu = np.unique(np.round(tall, 6))
    num_rl = np.zeros(len(tu), dtype=complex); den_rl = np.zeros(len(tu))
    num_lr = np.zeros(len(tu), dtype=complex); den_lr = np.zeros(len(tu))
    for v in ds["tris"].values():
        idx = np.searchsorted(tu, np.round(v["t"], 6))
        # accumulate weighted phasors
        np.add.at(num_rl, idx, v["wrl"]*v["zrl"]); np.add.at(den_rl, idx, v["wrl"])
        np.add.at(num_lr, idx, v["wlr"]*v["zlr"]); np.add.at(den_lr, idx, v["wlr"])
    Srl = num_rl/np.maximum(den_rl, 1e-30); Slr = num_lr/np.maximum(den_lr, 1e-30)
    D = Srl*np.conj(Slr)
    amp = np.abs(D)
    d = D/np.maximum(amp, 1e-30)
    good = (den_rl > 0) & (den_lr > 0) & (amp > 1e-12)
    # per-channel unit phasors on the same grid (vetoes)
    url = Srl/np.maximum(np.abs(Srl),1e-30); ulr = Slr/np.maximum(np.abs(Slr),1e-30)
    esum = (Srl*Slr); esum = esum/np.maximum(np.abs(esum),1e-30)
    aux = {"url": url[good], "ulr": ulr[good], "esum": esum[good]}
    return tu[good], d[good], aux

def zstat(t, d, t0, gamma, tau=TAU_SLIP):
    """One-sided matched-filter statistic at t0. Template demeaned in the
    complex domain (constant projected out -> immune to d(t)'s mean phase)."""
    chi = dchi_template(t, t0, gamma, tau)
    u_raw = np.exp(-12j*chi)
    u = u_raw - np.mean(u_raw)
    s = np.sum(d*np.conj(u))
    return float(np.real(s)/np.sqrt(np.sum(np.abs(u)**2)/2.0))

def search_grid(t, d, t0_grid, gamma):
    return np.array([zstat(t, d, t0, gamma) for t0 in t0_grid])

if __name__ == "__main__":
    datadir = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
    files = [
        "ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
        "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
        "ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
        "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    ]
    datasets = []
    for fn in files:
        rec = load_uvfits(os.path.join(datadir, fn))
        tris, ut = build_closures(rec)
        ds = dataset_series(rec, tris)
        t, d, aux = stack_differential(ds)
        datasets.append({"file": fn, "t": t, "d": d, "ntris": len(ds["tris"])})
        print(f"{fn}: ntri={len(ds['tris'])} npts={len(t)} span={t.max()-t.min():.0f}s "
              f"mean|d|_coherence={np.abs(np.mean(d)):.3f}")
    # null search on combined statistic: per t0 use datasets covering window
    t0_grid = np.arange(0, 25000, 20.0)  # s; refined per dataset below
    res = {}
    for ds in datasets:
        t, d = ds["t"], ds["d"]
        g = t0_grid[(t0_grid > t.min()+3*TAU_SLIP) & (t0_grid < t.max()-3*TAU_SLIP)]
        Z = search_grid(t, d, g, gamma=0.3)
        res[ds["file"]] = {"t0": g.tolist(), "Z": Z.tolist(),
                           "maxZ": float(Z.max()), "argmax": float(g[Z.argmax()])}
        print(f"{ds['file']}: maxZ={Z.max():.2f} at t0={g[Z.argmax()]:.0f}s  (n grid={len(g)})")
    json.dump(res, open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null_search.json"), "w"))
