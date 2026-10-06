"""Anchor-pulsar shake-out: B1937+21, B1855+09, J0437-4715.

Same diagnostic as the J1909 achromaticity test: published PINT par + TOAs,
post-fit residuals (no refit), split by frontend flag, 60-day bins per band.

Questions:
- B1937+21: is the ~15-yr, 17-us peak-to-peak wander achromatic (intrinsic
  spin noise) or chromatic (ISM/scattering)? Fit quadratic drift per band,
  cross-correlate band series.
- B1855+09: is the 2009-2011 ASP-era +/-3000 ns jump episode in all bands?
  430 MHz is very ISM-sensitive -> strong discriminant.
- J0437-4715: per-band rms / variance excess characterization (21 bins only
  in the npz; use full TOA residuals here).
"""
import numpy as np, json, os

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
os.chdir(HID)

import pint.models, pint.toa
from pint.residuals import Residuals

PULSARS = {
    "B1937+21": {
        "par": "nanograv15yr/extracted/narrowband/par/B1937+21_PINT_20220306.nb.par",
        "tim": "nanograv15yr/extracted/narrowband/tim/B1937+21_PINT_20220306.nb.tim",
        "bands": {"800MHz": ["Rcvr_800_GASP", "Rcvr_800_GUPPI"],
                  "1.4GHz": ["Rcvr1_2_GASP", "Rcvr1_2_GUPPI", "L-wide_ASP", "L-wide_PUPPI"],
                  "Sband": ["S-wide_ASP", "S-wide_PUPPI"]},
    },
    "B1855+09": {
        "par": "nanograv15yr/extracted/narrowband/par/B1855+09_PINT_20220301.nb.par",
        "tim": "nanograv15yr/extracted/narrowband/tim/B1855+09_PINT_20220301.nb.tim",
        "bands": {"430MHz": ["430_ASP", "430_PUPPI"],
                  "1.4GHz": ["L-wide_ASP", "L-wide_PUPPI"]},
    },
    "J0437-4715": {
        "par": "nanograv15yr/extracted/narrowband/par/J0437-4715_PINT_20220301.nb.par",
        "tim": "nanograv15yr/extracted/narrowband/tim/J0437-4715_PINT_20220301.nb.tim",
        "bands": {"1.5GHz": ["1.5GHz_YUPPI"], "3GHz": ["3GHz_YUPPI"]},
    },
}

out = {}
for psr, cfg in PULSARS.items():
    print(f"== {psr}", flush=True)
    m = pint.models.get_model(cfg["par"])
    t = pint.toa.get_TOAs(cfg["tim"], model=m)
    rs = Residuals(t, m)
    tr = rs.time_resids.to("us").value * 1e3  # ns
    mjd = t.get_mjds().value
    flags = t.get_flags()
    fe = np.array([flags[i].get("f", "?") for i in range(t.ntoas)])
    po = {"n_toa": t.ntoas, "bands": {}}
    series = {}
    for band, flist in cfg["bands"].items():
        sel = np.isin(fe, flist)
        tm, rr = mjd[sel], tr[sel]
        edges = np.arange(53180, 58960, 60)
        bc = 0.5 * (edges[:-1] + edges[1:])
        rb, tb = [], []
        for i in range(len(edges) - 1):
            s = (tm >= edges[i]) & (tm < edges[i + 1])
            if s.sum() >= 3:
                rb.append(np.median(rr[s])); tb.append(bc[i])
        rb, tb = np.array(rb), np.array(tb)
        series[band] = (tb, rb)
        po["bands"][band] = {"n_toa": int(sel.sum()), "n_bins": len(rb),
                             "rms_ns": float(np.std(rb)) if len(rb) else None,
                             "ptp_ns": float(np.ptp(rb)) if len(rb) else None}
        print(f"  {band}: {sel.sum()} TOAs, {len(rb)} bins, rms={np.std(rb):.0f} ns, ptp={np.ptp(rb):.0f} ns",
              flush=True)
    bands = list(series)
    if len(bands) >= 2:
        # cross-band correlation on common bins (interp to shared grid)
        grid = np.arange(53200, 58960, 60)
        cols = {}
        for b in bands:
            tb, rb = series[b]
            cols[b] = np.interp(grid, tb, rb, left=np.nan, right=np.nan)
        ok = ~np.isnan(cols[bands[0]])
        for b in bands[1:]:
            ok &= ~np.isnan(cols[b])
        corrs = {}
        for i in range(len(bands)):
            for j in range(i + 1, len(bands)):
                a, c = cols[bands[i]][ok], cols[bands[j]][ok]
                r = float(np.corrcoef(a, c)[0, 1]) if ok.sum() > 5 else None
                corrs[f"{bands[i]}x{bands[j]}"] = r
        po["cross_band_corr"] = corrs
        print(f"  cross-band corr (n={ok.sum()} common bins): {corrs}", flush=True)
    if psr == "B1937+21":
        # quadratic drift amplitude per band
        for b in bands:
            tb, rb = series[b]
            if len(rb) < 10:
                continue
            x = (tb - tb[0]) / 365.25
            p = np.polyfit(x, rb, 2)
            drift = np.polyval(p, x)
            po["bands"][b]["quad_drift_ptp_ns"] = float(np.ptp(drift))
            print(f"  {b}: quadratic drift ptp = {np.ptp(drift):.0f} ns", flush=True)
    if psr == "B1855+09":
        # ASP-era jump episode 2009-2011: MJD 54800-55600
        for b in bands:
            tb, rb = series[b]
            s = (tb >= 54800) & (tb <= 55600)
            adj = np.abs(np.diff(rb[s])) if s.sum() > 2 else [np.nan]
            po["bands"][b]["asp_episode_max_adjacent_ns"] = float(np.nanmax(adj))
            po["bands"][b]["asp_episode_ptp_ns"] = float(np.ptp(rb[s])) if s.sum() > 2 else None
            print(f"  {b}: ASP-episode ptp={np.ptp(rb[s]):.0f} ns, max adjacent swing={np.nanmax(adj):.0f} ns",
                  flush=True)
    out[psr] = po

json.dump(out, open("anchor_shakeout.json", "w"), indent=1)
print("wrote anchor_shakeout.json", flush=True)
