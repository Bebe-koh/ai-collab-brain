"""Veto channels + diagnostics.
Veto A (RL+LR sum, esum): slip cancels AND station R-L phases cancel -> any
    step here is systematics.
Veto B (RR, LL): slip-invariant -> coincident step = gain/structure glitch.
"""
import numpy as np, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits, build_closures
from slip_search import dataset_series, stack_differential, zstat, search_grid, TAU_SLIP

def stack_pol(ds, pol):
    tris = ds["tris"]
    tall = np.concatenate([v["t"] for v in tris.values()])
    tu = np.unique(np.round(tall, 6))
    num = np.zeros(len(tu), dtype=complex); den = np.zeros(len(tu))
    zk, wk = "z"+pol.lower(), "w"+pol.lower()
    for v in tris.values():
        if zk not in v: continue
        idx = np.searchsorted(tu, np.round(v["t"], 6))
        np.add.at(num, idx, v[wk]*v[zk]); np.add.at(den, idx, v[wk])
    S = num/np.maximum(den, 1e-30)
    d = S/np.maximum(np.abs(S), 1e-30)
    good = den > 0
    return tu[good], d[good]

if __name__ == "__main__":
    datadir = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
    files = [
        ("ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits", 18840.0),
        ("ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits", 18720.0),
        ("ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits", None),
        ("ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits", None),
    ]
    for fn, t0c in files:
        rec = load_uvfits(os.path.join(datadir, fn))
        tris, ut = build_closures(rec)
        ds = dataset_series(rec, tris)
        t, d, aux = stack_differential(ds)
        g = np.arange(t.min()+3*TAU_SLIP, t.max()-3*TAU_SLIP, 20.0)
        Z = search_grid(t, d, g, 0.3)
        print(f"== {fn[16:24]}")
        print(f"   DIFF(RL-LR): Z mean={Z.mean():+.2f} std={Z.std():.2f} max={Z.max():+.2f} min={Z.min():+.2f}")
        if t0c: print(f"   Z(t0c={t0c:.0f})={zstat(t,d,t0c,0.3):+.2f}")
        # Veto A: sum channel (slip cancels)
        Ze = search_grid(t, aux["esum"], g, 0.3)
        sA = f"max={Ze.max():+.2f}"
        if t0c: sA += f" Zsum(t0c)={zstat(t,aux['esum'],t0c,0.3):+.2f}"
        print(f"   SUM veto: {sA}")
        # Veto B: RR / LL
        for pol in ("RR", "LL"):
            tp, dp = stack_pol(ds, pol)
            gp = np.arange(tp.min()+3*TAU_SLIP, tp.max()-3*TAU_SLIP, 20.0)
            Zp = search_grid(tp, dp, gp, 0.3)
            sB = f"max={Zp.max():+.2f}"
            if t0c: sB += f" Z(t0c)={zstat(tp,dp,t0c,0.3):+.2f}"
            print(f"   {pol} veto: {sB}")
