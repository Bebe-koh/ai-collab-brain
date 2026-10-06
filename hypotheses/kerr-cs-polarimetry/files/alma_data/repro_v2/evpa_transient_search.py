#!/usr/bin/env python3
"""First-look EVPA transient search on ALMA Sgr A* 2017-04-07 polarimetry.

Hypothesis under test: classically driven phase slips of a pseudoscalar
field produce tanh-shaped EVPA transients of amplitude ~55.56 deg per 2*pi
slip (at gamma~0.1543), achromatic across bands, characteristic timescale
tau~46.9 s for Sgr A*.

Method per contiguous segment:
  y(t) = c0 + c1*(t-tc) + A * s((t-t0)/w) + noise,  s(x)=0.5*(1+tanh(x))
solved by linear least squares on a (t0, tau) grid; S/N = A_hat/sigma_A.
Detection on inverse-variance band-averaged EVPA; per-SPW fits test
achromaticity (genuine slip: common amplitude; Faraday: A ~ lambda^2).
Null: same max-over-grid search on circularly-shifted + time-reversed
surrogates.

Inputs (read-only): SGRA2017_X4947_IQUV.npz, SGRA2017_X448f_IQUV.npz
Outputs: transient_search_firstlook.md, PNG diagnostics, this script.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = "/home/hatch/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data/sgra_work"
FILES = ["SGRA2017_X4947_IQUV.npz", "SGRA2017_X448f_IQUV.npz"]

TAU_GRID = np.array([10., 15., 22., 32., 46.9, 68., 100., 120.])  # s
N_SURR = 200
GAP_TOL = 20.0        # s; larger gaps start a new segment
I_MASK_JY = 1.0       # mask integrations with median I below this (bad/phased-array-off)


def load_eb(path):
    d = np.load(path)
    mjd = d["mjd"]
    t = (mjd - mjd[0]) * 86400.0
    I, Q, U = d["I"], d["Q"], d["U"]
    freq = d["spw_freq_GHz"]
    lam2 = (299792.458 / (freq * 1e3)) ** 2  # m^2, for Faraday check
    good = np.median(I, axis=1) > I_MASK_JY
    evpa = 0.5 * np.degrees(np.arctan2(U, Q))  # (-90, 90] deg
    return dict(t=t, mjd=mjd, I=I, Q=Q, U=U, evpa=evpa, freq=freq,
                lam2=lam2, good=good, eb=str(d["eb"]))


def segments(t, good):
    """Contiguous good segments; returns list of index arrays."""
    dt = np.diff(t)
    brk = np.where((dt > GAP_TOL) | (~good[1:]))[0]
    edges = np.concatenate([[0], brk + 1, [len(t)]])
    segs = []
    for a, b in zip(edges[:-1], edges[1:]):
        idx = np.arange(a, b)
        idx = idx[good[idx]]
        if len(idx) >= 12:
            segs.append(idx)
    return segs


def unwrap_evpa(e):
    return np.unwrap(np.radians(e), period=np.pi) * 180.0 / np.pi


def search_segment(t, y, sig):
    """Grid search; returns dict of arrays over (tau, t0) and best candidate."""
    n = len(t)
    tc = t.mean()
    tb = t - tc
    results = []
    for tau in TAU_GRID:
        w = tau / 2.0
        # t0 must keep transition (t0 +/- 2w) inside the segment
        ok = (t >= t[0] + 2 * w) & (t <= t[-1] - 2 * w)
        t0s = t[ok]
        if len(t0s) == 0:
            continue
        # template matrix S[i,j] = s((t_i - t0_j)/w)
        X_ = (t[:, None] - t0s[None, :]) / w
        S = 0.5 * (1.0 + np.tanh(X_))
        m = len(t0s)
        XtX = np.empty((m, 3, 3))
        Xty = np.empty((m, 3))
        o = np.ones(n)
        XtX[:, 0, 0] = n
        XtX[:, 0, 1] = XtX[:, 1, 0] = tb.sum()
        XtX[:, 1, 1] = (tb ** 2).sum()
        XtX[:, 0, 2] = XtX[:, 2, 0] = S.sum(axis=0)
        XtX[:, 1, 2] = XtX[:, 2, 1] = (tb[:, None] * S).sum(axis=0)
        XtX[:, 2, 2] = (S ** 2).sum(axis=0)
        Xty[:, 0] = y.sum()
        Xty[:, 1] = (tb * y).sum()
        Xty[:, 2] = (S * y[:, None]).sum(axis=0)
        beta = np.linalg.solve(XtX, Xty)          # (m,3): c0,c1,A
        Ahat = beta[:, 2]
        resid = y[:, None] - (beta[:, 0] + beta[:, 1] * tb[:, None]
                              + beta[:, 2] * S)
        dof = max(n - 3, 1)
        s2 = (resid ** 2).sum(axis=0) / dof
        XtXinv = np.linalg.inv(XtX)
        varA = s2 * XtXinv[:, 2, 2]
        sigA = np.sqrt(np.maximum(varA, 1e-30))
        snr = Ahat / sigA
        for j in range(m):
            results.append((tau, t0s[j], Ahat[j], sigA[j], snr[j]))
    results = np.array(results,
                       dtype=[("tau", float), ("t0", float), ("A", float),
                              ("sigA", float), ("snr", float)])
    return results


def fit_at(t, y, t0, tau):
    """Single (t0, tau) LS fit of y = c0 + c1*(t-tc) + A*s((t-t0)/w)."""
    w = tau / 2.0
    tc = t.mean()
    tb = t - tc
    s = 0.5 * (1.0 + np.tanh((t - t0) / w))
    X = np.column_stack([np.ones_like(t), tb, s])
    beta, res, *_ = np.linalg.lstsq(X, y, rcond=None)
    dof = max(len(t) - 3, 1)
    s2 = (res[0] if len(res) else ((y - X @ beta) ** 2).sum()) / dof
    XtXinv = np.linalg.inv(X.T @ X)
    sigA = np.sqrt(max(s2 * XtXinv[2, 2], 1e-30))
    return beta[2], sigA, beta[2] / sigA


def run_null(t, y, seed=0):
    """Max |S/N| over grid for circularly-shifted + time-reversed surrogates."""
    rng = np.random.default_rng(seed)
    n = len(t)
    null_max = []
    # time-reversed
    r = search_segment(t, y[::-1], None)
    if len(r):
        null_max.append(np.max(np.abs(r["snr"])))
    for _ in range(N_SURR):
        k = rng.integers(1, n)
        ys = np.concatenate([y[k:], y[:k]])
        r = search_segment(t, ys, None)
        if len(r):
            null_max.append(np.max(np.abs(r["snr"])))
    return np.array(null_max)


def analyze_eb(path, out_prefix):
    eb = load_eb(path)
    t, evpa, good = eb["t"], eb["evpa"], eb["good"]
    segs = segments(t, good)
    print(f"{path.split('/')[-1]}: {len(t)} int, {good.sum()} good, "
          f"{len(segs)} segments")

    # per-SPW EVPA noise from diffs, per segment; band average (inv-var)
    seg_data = []
    for si, idx in enumerate(segs):
        ts = t[idx]
        es = unwrap_evpa(evpa[idx])          # (n,4) unwrapped deg
        d = np.diff(es, axis=0)
        sig_spw = d.std(axis=0) / np.sqrt(2)  # deg per sample
        sig_spw = np.maximum(sig_spw, 0.2)
        wgt = 1.0 / sig_spw ** 2
        ybar = (es * wgt).sum(axis=1) / wgt.sum()
        seg_data.append(dict(idx=idx, t=ts, es=es, ybar=ybar,
                             sig_spw=sig_spw))
        print(f"  seg{si}: n={len(idx)} span={(ts[-1]-ts[0]):.0f}s "
              f"EVPA-noise/spw={np.round(sig_spw,2)}")

    # --- detection search on band-averaged EVPA per segment ---
    all_cands = []
    for si, sd in enumerate(seg_data):
        r = search_segment(sd["t"], sd["ybar"], None)
        if len(r) == 0:
            continue
        order = np.argsort(-np.abs(r["snr"]))
        for k in order[:3]:
            all_cands.append((si, r["tau"][k], r["t0"][k], r["A"][k],
                              r["sigA"][k], r["snr"][k]))
    all_cands.sort(key=lambda c: -abs(c[5]))
    top = all_cands[:3]

    # --- achromaticity at top candidates: per-SPW fits ---
    achro = []
    for (si, tau, t0, A, sigA, snr) in top:
        sd = seg_data[si]
        Aspw, Sspw = [], []
        for spw in range(4):
            a, sa, _ = fit_at(sd["t"], sd["es"][:, spw], t0, tau)
            Aspw.append(a); Sspw.append(sa)
        Aspw = np.array(Aspw); Sspw = np.array(Sspw)
        w = 1 / Sspw ** 2
        Amean = (Aspw * w).sum() / w.sum()
        chi2 = (((Aspw - Amean) / Sspw) ** 2).sum()   # dof=3
        # Faraday alternative: A = k * lambda^2
        lam2 = eb["lam2"]
        Xf = np.column_stack([lam2])
        kf, *_ = np.linalg.lstsq(Xf / Sspw[:, None], Aspw / Sspw, rcond=None)
        Afar = kf[0] * lam2
        chi2_far = (((Aspw - Afar) / Sspw) ** 2).sum()  # dof=3
        achro.append(dict(Aspw=Aspw, Sspw=Sspw, Amean=Amean, chi2=chi2,
                          chi2_far=chi2_far, k_faraday=kf[0]))

    # --- null assessment on band-averaged series, per segment ---
    null_all = []
    for si, sd in enumerate(seg_data):
        nm = run_null(sd["t"], sd["ybar"], seed=1234 + si)
        null_all.append(nm)
    null_all = np.concatenate(null_all) if null_all else np.array([])

    # --- sensitivity: median sigma_A at tau=46.9 s across segments ---
    sigA_469 = []
    for sd in seg_data:
        r = search_segment(sd["t"], sd["ybar"], None)
        m = r[r["tau"] == 46.9]
        if len(m):
            sigA_469.append(np.median(m["sigA"]))
    sigA_469 = np.median(sigA_469) if sigA_469 else np.nan
    null95 = np.percentile(null_all, 95) if len(null_all) else np.nan

    return dict(eb=eb, seg_data=seg_data, top=top, achro=achro,
                null_all=null_all, sigA_469=sigA_469, null95=null95)


def plot_eb(res, out_prefix, ebname):
    eb, seg_data = res["eb"], res["seg_data"]
    t_all = eb["t"] / 60.0
    # 1) EVPA full track (band avg) + polarized flux
    fig, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for sd in seg_data:
        m = (sd["t"][0] <= eb["t"]) & (eb["t"] <= sd["t"][-1])
        ax[0].plot(sd["t"] / 60, sd["ybar"], ".", ms=2)
    for (si, tau, t0, A, sigA, snr) in res["top"]:
        ax[0].axvline(t0 / 60, color="r", ls="--", lw=1,
                      label=f"cand A={A:.0f}$^\\circ$ S/N={snr:.1f}" if si == res["top"][0][0] else "")
    ax[0].set_ylabel("EVPA band-avg (deg, unwrapped)")
    ax[0].set_title(f"{ebname}: EVPA track (4-SPWs inv-var avg)")
    ax[0].legend(fontsize=8, loc="best")
    pflux = np.sqrt(eb["Q"] ** 2 + eb["U"] ** 2)
    for s in range(4):
        ax[1].plot(t_all, pflux[:, s], ".", ms=2, label=f"{eb['freq'][s]:.1f} GHz")
    ax[1].set_ylabel("polarized flux (Jy)")
    ax[1].set_xlabel("minutes since EB start")
    ax[1].legend(fontsize=8, ncol=4)
    fig.tight_layout(); fig.savefig(f"{out_prefix}_track.png", dpi=110)
    plt.close(fig)

    # 2) waterfall of top-3 candidates: per-SPW EVPA + tanh model
    ntop = len(res["top"])
    fig, axes = plt.subplots(ntop, 1, figsize=(12, 3.2 * max(ntop, 1)),
                             sharex=False)
    if ntop == 1:
        axes = [axes]
    for k, ((si, tau, t0, A, sigA, snr), ac) in enumerate(zip(res["top"], res["achro"])):
        axi = axes[k]
        sd = seg_data[si]
        sel = (sd["t"] > t0 - 3 * tau) & (sd["t"] < t0 + 3 * tau)
        tt = sd["t"][sel] - t0
        w = tau / 2.0
        for spw in range(4):
            yy = sd["es"][sel, spw]
            yy = yy - np.median(yy) + ac["Aspw"][spw] * 0  # raw
            axi.plot(tt, yy, ".", ms=3, label=f"SPW{spw} {eb['freq'][spw]:.0f}GHz")
            tm = np.linspace(tt.min(), tt.max(), 200)
            base = np.median(yy)
            axi.plot(tm, base + ac["Aspw"][spw] * 0.5 * (1 + np.tanh(tm / w)),
                     lw=1.5)
        axi.axvline(0, color="k", ls=":")
        axi.set_title(f"cand: seg{si} t0={t0/60:.2f}min tau={tau:.0f}s "
                      f"A_bar={A:.1f}$^\\circ$ S/N={snr:.1f} "
                      f"achro $\\chi^2$={ac['chi2']:.1f}/3dof, "
                      f"Faraday $\\chi^2$={ac['chi2_far']:.1f}/3dof")
        axi.set_ylabel("EVPA (deg)")
        axi.legend(fontsize=7, ncol=4)
    axes[-1].set_xlabel("seconds from t0")
    fig.tight_layout(); fig.savefig(f"{out_prefix}_candidates.png", dpi=110)
    plt.close(fig)

    # 3) null distribution
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(res["null_all"], bins=40, histtype="step", lw=1.5,
            label=f"null (circ-shift), n={len(res['null_all'])}")
    obs = [abs(c[5]) for c in res["top"]]
    for i, o in enumerate(obs):
        ax.axvline(o, color=f"C{i}", ls="--",
                   label=f"obs cand{i+1} |S/N|={o:.1f}")
    ax.set_xlabel("max |S/N| over (t0, tau) grid")
    ax.set_ylabel("count")
    ax.legend(fontsize=8)
    ax.set_title(f"{ebname}: null assessment")
    fig.tight_layout(); fig.savefig(f"{out_prefix}_null.png", dpi=110)
    plt.close(fig)


def main(argv=None):
    import argparse, os
    ap = argparse.ArgumentParser(
        description="EVPA tanh-transient search on ALMA IQUV time series. "
                    "With no file arguments, reproduces the first look "
                    "(X4947+X448f).")
    ap.add_argument("files", nargs="*",
                    help=".npz IQUV files to analyze")
    ap.add_argument("--outdir", default=None,
                    help="output dir for plots/report (default: script dir)")
    ap.add_argument("--label", default=None,
                    help="report title label")
    ap.add_argument("--report", default=None,
                    help="report markdown filename")
    args = ap.parse_args(argv)

    if args.files:
        paths = [os.path.abspath(f) for f in args.files]
        default_run = False
    else:
        paths = [os.path.join(DATA_DIR, f) for f in FILES]
        default_run = True
    outdir = os.path.abspath(args.outdir) if args.outdir \
        else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)

    results = {}
    for path in paths:
        name = os.path.basename(path).replace("_IQUV.npz", "")
        res = analyze_eb(path, os.path.join(outdir, name))
        plot_eb(res, os.path.join(outdir, name), name)
        results[name] = res

    # ---- combined null + sensitivity ----
    null_all = np.concatenate([r["null_all"] for r in results.values()])
    sigA_469 = np.nanmedian([r["sigA_469"] for r in results.values()])
    null95 = np.percentile(null_all, 95)
    null99 = np.percentile(null_all, 99)

    usable_min = sum((sd["t"][-1] - sd["t"][0]) / 60.0
                     for r in results.values() for sd in r["seg_data"])
    n_seg = sum(len(r['seg_data']) for r in results.values())
    eb_names = ", ".join(results.keys())

    if default_run:
        title = "# EVPA transient search — first look (2 of 8 EBs, ALMA 2017-04-07)"
        report_name = "transient_search_firstlook.md"
        data_line = ("**Data:** SGRA2017_X4947_IQUV.npz (432 int, 11:08-11:55 UT) + "
                     "SGRA2017_X448f_IQUV.npz (428 int, 08:36-09:22 UT); 4.0 s cadence, "
                     "4 SPWs 213.1/215.1/227.1/229.1 GHz. Read-only inputs.")
        eb_scope = "in these two EBs if they occurred during coverage."
        caveat_eb = ("- First look: 2 of 8 execution blocks (~25% of the 2017-04-07 data); "
                     "the 2017-04-06/11 EBs and the remaining 04-07 EBs are not yet reduced.")
    else:
        title = f"# EVPA transient search — {args.label}" if args.label \
            else f"# EVPA transient search — {len(paths)} EBs ({eb_names})"
        report_name = args.report or (
            "transient_search_" + "_".join(sorted(results.keys())) + ".md")
        data_bits = []
        for name, r in results.items():
            n_int = sum(len(sd["t"]) for sd in r["seg_data"])
            data_bits.append(f"{name} ({n_int} int, {len(r['seg_data'])} segs)")
        data_line = ("**Data:** " + " + ".join(data_bits) +
                     "; 4.0 s cadence, 4 SPWs 213.1/215.1/227.1/229.1 GHz. "
                     "Read-only inputs.")
        eb_scope = "in these EBs if they occurred during coverage."
        caveat_eb = ("- Coverage: EBs analyzed here only; remaining execution blocks "
                     "and other observing dates are not included.")

    lines = []
    A = lines.append
    A(title)
    A("")
    A(data_line)
    A(f"**Usable contiguous coverage:** {usable_min:.0f} min in "
      f"{n_seg} segments "
      f"(gaps >20 s split; integrations masked with median I<1 Jy).")
    A("")
    A("**Method:** per segment, LS fit of "
      "y(t)=c0+c1*(t-tc)+A*0.5*(1+tanh((t-t0)/(tau/2))) on band-averaged "
      "(inv-var) EVPA; grid tau=[10,15,22,32,46.9,68,100,120] s, all t0 with "
      "t0+/-tau inside segment. Null: 200 circular shifts + time reversal per "
      "segment, same max-over-grid search.")
    A("")
    A("## Top candidates (detection grid)")
    A("")
    A("| EB | seg | t0 (UT) | tau (s) | A (deg) | sigma_A | S/N | sign |")
    A("|---|---|---|---|---|---|---|---|")
    for name, r in results.items():
        eb = r["eb"]
        for (si, tau, t0, amp, sigA, snr) in r["top"]:
            mjd0 = eb["mjd"][0] + t0 / 86400.0
            hh = (mjd0 % 1) * 24
            A(f"| {name[-5:]} | {si} | {hh:05.2f} | {tau:.0f} | {amp:+.1f} | "
              f"{sigA:.1f} | {snr:+.1f} | {'+' if amp > 0 else '-'} |")
    A("")
    A("## Achromaticity (per-SPW amplitude fits at candidate t0, tau)")
    A("")
    A("Genuine theta-slip: common amplitude across SPWs (chi2 ~ 3 dof). "
      "Faraday rotation: A proportional to lambda^2 (fit shown for comparison).")
    A("")
    for name, r in results.items():
        for i, ((si, tau, t0, amp, sigA, snr), ac) in enumerate(
                zip(r["top"], r["achro"])):
            A(f"- {name[-5:]} cand{i+1} (seg{si}, tau={tau:.0f}s): "
              f"A_spw=[{', '.join(f'{v:+.1f}' for v in ac['Aspw'])}] deg, "
              f"sigma_spw=[{', '.join(f'{v:.1f}' for v in ac['Sspw'])}], "
              f"common-A chi2={ac['chi2']:.1f}/3dof, "
              f"Faraday(lam^2) chi2={ac['chi2_far']:.1f}/3dof")
    A("")
    A("## Null assessment")
    A("")
    A(f"- Null max|S/N| over identical grid: 95th pct={null95:.1f}, "
      f"99th pct={null99:.1f} (n={len(null_all)} surrogates).")
    obs_max = max(abs(c[5]) for r in results.values() for c in r["top"])
    A(f"- Strongest observed candidate: |S/N|={obs_max:.1f}.")
    if obs_max > null99:
        A("- **Verdict: strongest candidate EXCEEDS the 99th percentile of the "
          "null — warrants follow-up (achromaticity + remaining EBs), "
          "not yet a detection claim.**")
    elif obs_max > null95:
        A("- Verdict: strongest candidate exceeds the 95th percentile but not "
          "the 99th — interesting, not significant; treat as no detection.")
    else:
        A("- Verdict: consistent with the null — **no detection**.")
    A("")
    A("## Sensitivity / upper bound")
    A("")
    A(f"- Median amplitude uncertainty at tau=46.9 s: sigma_A={sigA_469:.1f} deg.")
    A(f"- Approx. 95%-detection amplitude at tau=46.9 s: "
      f"A_95 ~= {null95:.1f} x {sigA_469:.1f} = {null95*sigA_469:.0f} deg.")
    A(f"- **Upper bound:** no tanh transients with |A| > "
      f"~{null95*sigA_469:.0f} deg and tau in [10,120] s detected in "
      f"{usable_min:.0f} min of usable 4-s ALMA Sgr A* polarimetry. "
      f"A 55.6-deg slip at tau~47 s would have S/N ~ {55.6/sigA_469:.0f}, "
      f"{'ABOVE' if 55.6/sigA_469 > null99 else 'below'} the 99th-percentile "
      f"null threshold — i.e. such slips are "
      f"{'EXCLUDED at >>99% per-epoch' if 55.6/sigA_469 > null99 else 'NOT excluded'} "
      f"{eb_scope}")
    A("")
    A("## Caveats")
    A("")
    A(caveat_eb)
    A("- Band-averaged detection weights SPWs by measured EVPA noise; one SPW "
      "per EB is noisier — downweighted, not removed.")
    A("- A 55.6-deg *unresolved* step (tau << 4 s) would appear as a single-sample "
      "jump, not a tanh; this search targets resolved ramps 10-120 s.")
    A("- Surrogate null assumes stationary noise within a segment; slow "
      "drifts are absorbed by the linear baseline in the fit.")
    A("")
    A("## Plots")
    A("")
    for name in results:
        A(f"- `{name}_track.png`: EVPA track + polarized flux")
        A(f"- `{name}_candidates.png`: top-3 candidate waterfalls (per-SPW data + tanh model)")
        A(f"- `{name}_null.png`: null histogram")

    with open(os.path.join(outdir, report_name), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
