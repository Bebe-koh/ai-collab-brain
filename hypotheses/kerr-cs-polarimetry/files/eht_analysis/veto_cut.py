"""Veto-cut infrastructure: veto mask from SUM/RR/LL channels, applied to
search, null surrogates, and injections. A t0 is vetoed if the slip-free
veto Z exceeds T_VETO there (systematic contamination)."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import Bank, TAU_SLIP

T_VETO = 8.0  # veto threshold on slip-free channels

def veto_mask_from_raw(raw, combine_list=("sum", "RR", "LL"), t_veto=T_VETO):
    """Return (t_common, ts, veto_ok) where veto_ok[t] is True if t passes.
    Uses stack_from_raw per channel; grids aligned via common time base."""
    from pipeline import stack_from_raw
    chans = {}
    for ch in ("diff",) + tuple(combine_list):
        t, d = stack_from_raw(raw, t0_jd=None, combine=ch)
        chans[ch] = (t, d)
    # use diff channel time base
    t = chans["diff"][0]
    ts = (t - t[0]) * 86400.0
    gr = np.arange(ts.min() + 3*TAU_SLIP, ts.max() - 3*TAU_SLIP, 20.0)
    b = Bank(ts, gr)
    veto_z = np.zeros(len(gr))
    for ch in combine_list:
        tc, dc = chans[ch]
        tsc = (tc - tc[0]) * 86400.0
        # regrid: Bank on this channel's own grid, then map to common gr via nearest
        bc = Bank(tsc, gr)
        zc, _ = bc.zgrid(dc)
        veto_z = np.maximum(veto_z, zc)
    ok = veto_z < t_veto
    return t, ts, gr, ok, veto_z

def apply_veto_to_bank_result(z, gb, ok):
    """Restrict a (z, gb) bank result to unvetoed grid points."""
    return z[ok], gb[ok]
