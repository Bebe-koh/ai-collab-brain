"""Veto channels with the differenced pipeline.
SUM = S^RL*S^LR (slip cancels, station R-L cancels): any step = systematics.
RR, LL (slip-invariant): coincident step = gain/structure glitch."""
import numpy as np, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits
from pipeline import raw_triangle_series, stack_from_raw, difference_series, DiffBank, TAU_SLIP

DATADIR = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
FILES = {
    "2017-04-06 hi": "ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-06 lo": "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-07 hi": "ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-07 lo": "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
}
for label, fn in FILES.items():
    raw = raw_triangle_series(load_uvfits(os.path.join(DATADIR, fn)))
    out = {}
    for ch in ("diff", "sum", "RR", "LL"):
        t, d = stack_from_raw(raw, t0_jd=None, combine=ch)
        te, e, keep = difference_series(t, d)
        ts = (t-t[0])*86400.0
        gr = np.arange(ts.min()+3*TAU_SLIP, ts.max()-3*TAU_SLIP, 20.0)
        b = DiffBank(ts, gr, keep)
        z, gb = b.zgrid(e)
        out[ch] = (float(z.max()), float(gr[z.argmax()]), float(gb[z.argmax()]))
    print(f"{label}: " + " | ".join(f"{ch}: maxZ={v[0]:.2f}@t0={v[1]:.0f}s(g={v[2]})" for ch, v in out.items()))
