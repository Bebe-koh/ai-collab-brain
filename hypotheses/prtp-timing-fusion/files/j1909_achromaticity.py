"""J1909 achromaticity test: is the ~8.8-yr, ~400-ns excursion the same at all
radio frequencies (intrinsic spin noise) or frequency-dependent (instrumental)?

Method: load the published NANOGrav 15-yr PINT par solution + 35k narrowband
TOAs, compute post-fit residuals WITHOUT refitting, split TOAs by frontend
flag (-f): 800 MHz (Rcvr_800) vs 1.4 GHz (Rcvr1_2) vs 3 GHz (3GHz_YUPPI),
bin each in 60-day bins, fit the 8.84-yr wave per band, compare A/phase.

Achromatic (same A, same phase) -> intrinsic. Chromatic -> instrumental.
"""
import numpy as np, json, os
from scipy.optimize import minimize

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
os.chdir(HID)

import pint.models, pint.toa
from pint.residuals import Residuals

m = pint.models.get_model("nanograv15yr/extracted/narrowband/par/J1909-3744_PINT_20220303.nb.par")
t = pint.toa.get_TOAs("nanograv15yr/extracted/narrowband/tim/J1909-3744_PINT_20220303.nb.tim", model=m)
print("TOAs:", t.ntoas, flush=True)

rs = Residuals(t, m)
tr = rs.time_resids.to("us").value * 1e3          # ns
mjd = t.get_mjds().value
print(f"residual rms: {np.nanstd(tr):.0f} ns", flush=True)

flags = t.get_flags()
fe = np.array([flags[i].get("f", "?") for i in range(t.ntoas)])
bands = {"800MHz": [f for f in set(fe) if f.startswith("Rcvr_800")],
         "1.4GHz": [f for f in set(fe) if f.startswith("Rcvr1_2")],
         "3GHz":   [f for f in set(fe) if "3GHz" in f]}
for k, v in bands.items():
    print(k, v, flush=True)

P = 8.84
out = {}
for band, flist in bands.items():
    sel = np.isin(fe, flist)
    tm, rr = mjd[sel], tr[sel]
    print(f"{band}: {sel.sum()} TOAs, MJD {tm.min():.0f}-{tm.max():.0f}", flush=True)
    edges = np.arange(tm.min(), tm.max() + 60, 60)
    bc = 0.5 * (edges[:-1] + edges[1:])
    rb, eb, tb = [], [], []
    for i in range(len(edges) - 1):
        s = (tm >= edges[i]) & (tm < edges[i + 1])
        if s.sum() >= 5:
            rb.append(np.median(rr[s])); eb.append(np.std(rr[s]) / np.sqrt(s.sum())); tb.append(bc[i])
    rb, eb, tb = map(np.array, (rb, eb, tb))
    ty = (tb - tb[0]) / 365.25
    eb = np.maximum(eb, 15.0)
    def nll(p):
        c, A, ph = p
        return 0.5 * np.sum(((rb - c - A * np.sin(2 * np.pi * ty / P + ph)) / eb) ** 2)
    r = minimize(nll, [0.0, 300.0, 1.0], method="Nelder-Mead",
                 options=dict(maxiter=20000))
    c, A, ph = r.x
    r0 = minimize(lambda p: 0.5 * np.sum(((rb - p[0]) / eb) ** 2), [0.0], method="Nelder-Mead")
    out[band] = {"n_toa": int(sel.sum()), "n_bins": len(rb),
                 "A_ns": float(A), "phi": float(ph % (2 * np.pi)),
                 "dlnL_wave": float(r0.fun - r.fun),
                 "rms_ns": float(np.std(rb))}
    print(f"  {band}: A={A:.0f} ns, phi={ph % (2*np.pi):.2f}, dlnL={r0.fun-r.fun:.0f}, bins={len(rb)}",
          flush=True)

json.dump(out, open("j1909_achromaticity.json", "w"), indent=1)
print("wrote j1909_achromaticity.json", flush=True)
