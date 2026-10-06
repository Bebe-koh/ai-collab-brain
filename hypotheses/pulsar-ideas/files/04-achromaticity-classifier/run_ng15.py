#!/usr/bin/env python3
"""
Driver for the fresh-run achromaticity classifier on NANOGrav 15-yr data.

Pulsars:
  J1939+2134 (B1937+21) : KNOWN achromatic wander (control, expect achromatic)
  J1713+0747            : KNOWN chromatic events, strong DM variations
                          (control, expect DM-like)
  J1600-3053            : AMBIGUOUS (DMX vs DMGP disagree in the literature)

For each pulsar, two configurations:
  FULL  - published par (with DMX): residual-chromaticity / model-adequacy check
  NODMX - DMX parameters removed, refit: dominant-noise-character classifier

For each band pair with enough contemporaneous 30-day bins:
  weighted correlation r, amplitude ratio alpha, bootstrap CIs, shuffle null,
  classification (achromatic / DM-like / scattering-like / mixed / no-common-mode).

Also: sliding-window ("per-epoch") mode on J1713+0747, and a TOA-drop
degradation test.
"""
import os, re, sys, glob, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from achro_classifier import (
    weighted_bin, contemporaneous, bootstrap_cis, shuffle_null_pvalue,
    classify_pair, BIN_DAYS)

PULSARS = {
    "J1939+2134": {"truth": "achromatic"},
    "J1713+0747": {"truth": "chromatic"},
    "J1600-3053": {"truth": "ambiguous"},
}
MIN_BINS = 8          # minimum contemporaneous bins for a band pair
BAND_SEP = 1.30       # min fractional freq separation to call two groups bands


def find_pulsar_files(datadir, psr):
    """Locate .par and .tim (narrowband) for a pulsar in the extracted tree."""
    cands = []
    for root, dirs, files in os.walk(datadir):
        for fn in files:
            if fn.endswith(".par") and psr.replace("+", "_") in fn.replace("+", "_"):
                cands.append(os.path.join(root, fn))
    # NANOGrav layout: narrowband/<psr>/<psr>.par etc. Be permissive, then filter.
    pars = [c for c in cands if "narrowband" in c]
    if not pars:
        pars = cands
    if not pars:
        return None, None
    par = sorted(pars)[0]
    base = os.path.splitext(par)[0]
    tim = base + ".tim"
    if not os.path.exists(tim):
        # try any .tim next to the par
        tims = glob.glob(os.path.join(os.path.dirname(par), "*.tim"))
        tim = tims[0] if tims else None
    return par, tim


def load_and_fit(par, tim, remove_dmx=False):
    import pint.models, pint.toa, pint.fitter
    m = pint.models.get_model(par)
    if remove_dmx:
        for p in list(m.params):
            if re.match(r"DMX_\d+$", p):
                try:
                    m.remove_param(p)
                except Exception:
                    m[p].value = 0.0
                    m[p].frozen = True
    t = pint.toa.get_TOAs(tim)
    f = pint.fitter.WLSFitter(t, m)
    f.fit_toas(maxiter=20)
    return f


def extract(f):
    """Per-TOA arrays: mjd, resid_us, sigma_us, freq_mhz, frontend flag."""
    import astropy.units as u
    r = f.resids.time_resids.to(u.us).value
    toas = f.toas
    mjd = toas.get_mjds().value
    sig = toas.get_errors().to(u.us).value
    frq = toas.get_freqs().to(u.MHz).value
    try:
        fe = np.array(toas.get_flag_value("fe")[0])
    except Exception:
        fe = np.array(["unknown"] * len(mjd))
    ok = np.isfinite(mjd) & np.isfinite(r) & np.isfinite(sig) & (sig > 0)
    return mjd[ok], r[ok], sig[ok], frq[ok], fe[ok]


def group_bands(mjd, r, sig, frq, fe):
    """Group TOAs by frontend flag; merge groups into bands by median freq.
    Returns dict band_label -> (mjd, r, sig, frq, medfreq)."""
    groups = {}
    for g in np.unique(fe):
        m = fe == g
        groups[str(g)] = (mjd[m], r[m], sig[m], frq[m], float(np.median(frq[m])))
    # merge groups whose median freqs are within BAND_SEP factor
    items = sorted(groups.items(), key=lambda kv: kv[1][4])
    bands, cur = [], None
    for name, (tm, tr, ts, tf, mf) in items:
        if cur is None or mf / cur["med"] > BAND_SEP:
            cur = {"names": [name], "med": mf, "idx": []}
            bands.append(cur)
        else:
            cur["names"].append(name)
            cur["med"] = float(np.mean([cur["med"], mf]))
        cur["idx"].append((tm, tr, ts, tf))
    out = {}
    for b in bands:
        tm = np.concatenate([i[0] for i in b["idx"]])
        tr = np.concatenate([i[1] for i in b["idx"]])
        ts = np.concatenate([i[2] for i in b["idx"]])
        tf = np.concatenate([i[3] for i in b["idx"]])
        label = "+".join(b["names"]) + f"@{b['med']:.0f}MHz"
        out[label] = (tm, tr, ts, tf, b["med"])
    return out


def analyze_pair(b1, b2, nu1, nu2, label, weighted=True):
    """Full per-pair analysis. Returns result dict."""
    bb1 = weighted_bin(*b1[:3])
    bb2 = weighted_bin(*b2[:3])
    cc = contemporaneous(bb1, bb2)
    res = {"label": label, "nu1": nu1, "nu2": nu2, "weighted": weighted}
    if cc is None:
        res.update(n_overlap=0, status="no-overlap")
        return res
    x, sx, y, sy, n = cc
    res["n_overlap"] = int(n)
    if n < MIN_BINS:
        res.update(status=f"too-few-bins({n})")
        return res
    boot = bootstrap_cis(x, y, sx, sy, weighted=weighted)
    pval, r0 = shuffle_null_pvalue(x, y, sx, sy, weighted=weighted)
    lab, detail = classify_pair(boot, nu1, nu2)
    res.update(status="ok", classification=lab, detail=detail,
               shuffle_p=pval, r_point=r0)
    # unweighted cross-check
    boot_u = bootstrap_cis(x, y, sx, sy, weighted=False)
    lab_u, _ = classify_pair(boot_u, nu1, nu2)
    res["unweighted_classification"] = lab_u
    return res


def run_pulsar(datadir, psr, remove_dmx, out_list):
    par, tim = find_pulsar_files(datadir, psr)
    if par is None:
        out_list.append({"pulsar": psr, "config": "NODMX" if remove_dmx else "FULL",
                         "status": "files-not-found"})
        return
    cfg = "NODMX" if remove_dmx else "FULL"
    print(f"[{psr} {cfg}] par={par}", flush=True)
    f = load_and_fit(par, tim, remove_dmx=remove_dmx)
    mjd, r, sig, frq, fe = extract(f)
    bands = group_bands(mjd, r, sig, frq, fe)
    print(f"[{psr} {cfg}] {len(mjd)} TOAs, bands: " +
          ", ".join(f"{k} (n={[len(v[0]) for v in [bands[k]]][0]})" for k in bands), flush=True)
    keys = sorted(bands, key=lambda k: bands[k][4])
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k1, k2 = keys[i], keys[j]
            nu1, nu2 = bands[k1][4], bands[k2][4]
            if nu2 / nu1 < BAND_SEP:
                continue
            rr = analyze_pair(bands[k1], bands[k2], nu1, nu2,
                              f"{psr} {cfg} {k1} x {k2}")
            rr.update(pulsar=psr, config=cfg, truth=PULSARS[psr]["truth"])
            out_list.append(rr)
            d = rr.get("detail", {})
            print(f"  {k1} x {k2}: n={rr.get('n_overlap')} "
                  f"class={rr.get('classification')} "
                  f"r={d.get('r', float('nan')):.4f} [{d.get('r16', float('nan')):.3f},{d.get('r84', float('nan')):.3f}] "
                  f"alpha={d.get('alpha', float('nan')):.3f} [{d.get('a16', float('nan')):.3f},{d.get('a84', float('nan')):.3f}] "
                  f"p_shuf={rr.get('shuffle_p', float('nan')):.4f}", flush=True)


def sliding_window(datadir, psr, window_yr=2.0, step_yr=0.5):
    """Per-epoch mode: classify in sliding windows (NODMX config)."""
    from achro_classifier import weighted_bin as wb
    par, tim = find_pulsar_files(datadir, psr)
    f = load_and_fit(par, tim, remove_dmx=True)
    mjd, r, sig, frq, fe = extract(f)
    bands = group_bands(mjd, r, sig, frq, fe)
    keys = sorted(bands, key=lambda k: bands[k][4])
    if len(keys) < 2:
        return []
    # use the two most separated bands
    k1, k2 = keys[0], keys[-1]
    nu1, nu2 = bands[k1][4], bands[k2][4]
    out = []
    t0, t1 = mjd.min(), mjd.max()
    wdays, sdays = window_yr * 365.25, step_yr * 365.25
    tc = t0 + wdays / 2
    while tc + wdays / 2 <= t1:
        sel1 = (bands[k1][0] >= tc - wdays / 2) & (bands[k1][0] < tc + wdays / 2)
        sel2 = (bands[k2][0] >= tc - wdays / 2) & (bands[k2][0] < tc + wdays / 2)
        b1 = tuple(a[sel1] for a in bands[k1][:4])
        b2 = tuple(a[sel2] for a in bands[k2][:4])
        rr = analyze_pair(b1, b2, nu1, nu2, f"{psr} window@{tc:.0f}")
        rr["tcenter"] = float(tc)
        out.append(rr)
        tc += sdays
    return out


def degradation(datadir, psr, fractions=(0.0, 0.25, 0.5, 0.75), seed=7):
    """Drop random TOA fractions, rerun NODMX classification on the widest pair."""
    rng = np.random.default_rng(seed)
    par, tim = find_pulsar_files(datadir, psr)
    f = load_and_fit(par, tim, remove_dmx=True)
    mjd, r, sig, frq, fe = extract(f)
    out = []
    for frac in fractions:
        keep = rng.random(len(mjd)) >= frac
        bands = group_bands(mjd[keep], r[keep], sig[keep], frq[keep], fe[keep])
        keys = sorted(bands, key=lambda k: bands[k][4])
        if len(keys) < 2:
            out.append({"frac_dropped": frac, "status": "no-bands"})
            continue
        k1, k2 = keys[0], keys[-1]
        rr = analyze_pair(bands[k1], bands[k2], bands[k1][4], bands[k2][4],
                          f"{psr} drop{frac}")
        rr["frac_dropped"] = frac
        rr["n_toa"] = int(keep.sum())
        out.append(rr)
    return out


def main():
    datadir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data")
    results = []
    for psr in PULSARS:
        for remove_dmx in (False, True):
            try:
                run_pulsar(datadir, psr, remove_dmx, results)
            except Exception as e:
                import traceback; traceback.print_exc()
                results.append({"pulsar": psr,
                                "config": "NODMX" if remove_dmx else "FULL",
                                "status": f"error: {type(e).__name__}: {e}"})
    print("\n=== sliding window: J1713+0747 (NODMX) ===", flush=True)
    try:
        sw = sliding_window(datadir, "J1713+0747")
        for rr in sw:
            d = rr.get("detail", {})
            print(f"  t={rr['tcenter']:.0f} n={rr.get('n_overlap')} "
                  f"class={rr.get('classification')} r={d.get('r', float('nan')):.3f} "
                  f"alpha={d.get('alpha', float('nan')):.3f}", flush=True)
    except Exception:
        import traceback; traceback.print_exc()
        sw = []
    print("\n=== degradation: J1713+0747 (NODMX) ===", flush=True)
    try:
        dg = degradation(datadir, "J1713+0747")
        for rr in dg:
            d = rr.get("detail", {})
            print(f"  dropped={rr.get('frac_dropped')} n_toa={rr.get('n_toa')} "
                  f"class={rr.get('classification')} r={d.get('r', float('nan')):.3f} "
                  f"alpha={d.get('alpha', float('nan')):.3f}", flush=True)
    except Exception:
        import traceback; traceback.print_exc()
        dg = []
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump({"pairs": results, "sliding": sw, "degradation": dg},
                  fh, indent=1, default=str)
    print("\nwrote results.json", flush=True)


if __name__ == "__main__":
    main()
