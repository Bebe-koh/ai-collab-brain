"""B1937 rigorous cross-band achromaticity (PRTP repair step 3b).

Post-fit residuals (published PINT par, no refit), split by receiver band,
30-day bins per band. Correlation computed ONLY on genuinely contemporaneous
bins (both bands have native TOAs in the same bin) with inverse-variance
weighting. No interpolation across gaps.

Tests Vivekanand (2020)'s hypotheses: a Moon-sized planetary companion or
precession predicts achromatic wander; steep-DM-gradient noise predicts
chromatic wander (DM delay ~ 1/f^2).
"""
import numpy as np, json, os
import pint.models, pint.toa
from pint.residuals import Residuals

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
os.chdir(HID)

BANDS = {"800MHz": ["Rcvr_800"],
         "1.4GHz": ["Rcvr1_2", "L-wide"],
         "Sband": ["S-wide"]}

m = pint.models.get_model("nanograv15yr/extracted/narrowband/par/B1937+21_PINT_20220306.nb.par")
t = pint.toa.get_TOAs("nanograv15yr/extracted/narrowband/tim/B1937+21_PINT_20220306.nb.tim", model=m)
rs = Residuals(t, m)
tr = rs.time_resids.to("us").value * 1e3  # ns
mjd = t.get_mjds().value
flags = t.get_flags()
fe = np.array([f.get("fe", "") for f in flags])

BIN = 30.0
t0 = mjd.min()
binidx = ((mjd - t0) // BIN).astype(int)
nbins = binidx.max() + 1

def band_series(felist):
    sel = np.isin(fe, felist)
    tb, rb, eb = [], [], []
    for b in range(nbins):
        s = sel & (binidx == b)
        if s.sum() >= 3:
            # robust mean, formal error of weighted mean
            tb.append(t0 + (b + 0.5) * BIN)
            rb.append(np.median(tr[s]))
            eb.append(1.4826 * np.median(np.abs(tr[s] - np.median(tr[s])))
                      / np.sqrt(s.sum()))
    return np.array(tb), np.array(rb), np.array(eb)

series = {b: band_series(fl) for b, fl in BANDS.items()}
for b, (tb, rb, eb) in series.items():
    print(f"{b}: {len(rb)} native bins", flush=True)

def wcorr(x, y, wx, wy):
    w = 1.0 / (wx ** 2 + wy ** 2 + 1e-12)
    xm = np.sum(w * x) / w.sum(); ym = np.sum(w * y) / w.sum()
    cov = np.sum(w * (x - xm) * (y - ym)) / w.sum()
    vx = np.sum(w * (x - xm) ** 2) / w.sum(); vy = np.sum(w * (y - ym) ** 2) / w.sum()
    return cov / np.sqrt(vx * vy)

out = {"n_bins": {b: len(v[0]) for b, v in series.items()}, "pairs": {}}
bands = list(series)
for i in range(len(bands)):
    for j in range(i + 1, len(bands)):
        bi, bj = bands[i], bands[j]
        ti, ri, ei = series[bi]; tj, rj, ej = series[bj]
        # match on identical bin centers (same 30-day grid => contemporaneous)
        common, ii, jj = np.intersect1d(np.round(ti, 6), np.round(tj, 6),
                                        return_indices=True)
        r = wcorr(ri[ii], rj[jj], ei[ii], ej[jj])
        # also raw correlation of the drift (unweighted) for reference
        r_raw = float(np.corrcoef(ri[ii], rj[jj])[0, 1])
        out["pairs"][f"{bi}x{bj}"] = {"n_overlap": int(len(common)),
                                      "wcorr": float(r), "raw_corr": r_raw}
        print(f"{bi} x {bj}: n_overlap={len(common)} wcorr={r:.4f} raw={r_raw:.4f}",
              flush=True)

json.dump(out, open("b1937_achromaticity.json", "w"), indent=1)
print("wrote b1937_achromaticity.json")
