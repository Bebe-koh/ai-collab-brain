"""Veto channels, undifferenced pipeline (same as search).
SUM = S^RL*S^LR (slip cancels, station R-L cancels). RR, LL (slip-invariant)."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits
from pipeline import raw_triangle_series, stack_from_raw, Bank, TAU_SLIP

DATADIR = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
FILES = {
    "2017-04-06 hi": "ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-06 lo": "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-07 hi": "ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
    "2017-04-07 lo": "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
}
for label, fn in FILES.items():
    raw = raw_triangle_series(load_uvfits(os.path.join(DATADIR, fn)))
    res = {}
    for ch in ("diff", "sum", "RR", "LL"):
        t, d = stack_from_raw(raw, t0_jd=None, combine=ch)
        ts = (t-t[0])*86400.0
        gr = np.arange(ts.min()+3*TAU_SLIP, ts.max()-3*TAU_SLIP, 20.0)
        b = Bank(ts, gr)
        z, gb = b.zgrid(d)
        res[ch] = (float(z.max()), float(gb[z.argmax()]))
    print(f"{label}: " + " | ".join(f"{ch}={v[0]:.2f}(g{ v[1]})" for ch, v in res.items()), flush=True)
