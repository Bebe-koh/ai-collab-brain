#!/usr/bin/env python3
"""EVPA tanh-transient search v2 (repaired implementation).

Hypothesis under test: classically driven phase slips of a pseudoscalar
field produce tanh-shaped EVPA transients of amplitude ~55.56 deg per 2*pi
slip, achromatic across bands, characteristic timescale tau~46.9 s.

REPAIRS vs v1 (audit 2026-10-06):
  R1. Temporal unwrapping. v1 called np.unwrap on a (time, 4-SPWs) array
      without an axis, unwrapping across spectral windows instead of time.
      v2 unwraps along time (axis=0). Verified on synthetic +20-deg step.
  R2. Residual-based null. v1 circular-shifted the RAW series including its
      slow baseline drift; joining drift end-to-beginning manufactures a
      discontinuity the template then "detects", inflating null thresholds.
      v2 fits a linear baseline per segment, shifts only the residuals, and
      adds the fitted baseline back. Validated on drift-only synthetics.
  R3. Campaign-level false alarm. v1 pooled per-segment surrogate maxima;
      that is not the distribution of the maximum over the campaign. v2
      builds the null from per-EB campaign maxima (one surrogate per
      segment, max over segments), matching the detection statistic.
  R4. Injection-recovery calibration. v1 quoted ">>99% exclusion" from
      predicted S/N vs a null percentile. v2 injects achromatic tanh events
      into the real per-SPW series, runs the full pipeline (detection +
      achromaticity veto), and reports measured detection probability vs
      amplitude at each tau. Exclusion bounds come from A_90(tau).
  R5. Achromaticity veto with enforced threshold. v1 computed chi2 but
      enforced nothing. v2 requires a per-SPW S/N coincidence (>=3 of 4
      SPWs agree in sign with |S/N|>3) plus a dilution-ratio test
      (max|A_spw|/|A_bar| <= 2.0). An amplitude-chi2 version was tried and
      abandoned: per-SPW amplitude errors are misspecified in real data
      (true 55.6-deg injections reached chi2/3 ~ 50-128 while some
      single-SPW jumps scored < 5); a pure coincidence rule admitted
      selection bias. The dilution ratio is robust to that bias.
  R6. Honest fitting statement. v1's search_segment accepted a `sig`
      argument it never used (ordinary least squares; amplitude uncertainty
      from fit residuals). v2 drops the dead argument and documents OLS.

PARAMETER CORRECTION (2026-10-06): the committed source briefly carried
N_CAMP=500 and injection_recovery(trials=25) while the published
methodology claimed 1000 campaigns and 100 trials, and the default file
list omitted X4227. All three are corrected above (N_CAMP=1000,
trials=100, X4227 included) so the code as committed now generates the
published numbers. A later audit pass caught single_spw_jump_fpr still at
trials=25; corrected to 100 the same day and the control re-run
(false-pass 0.00-0.06, see repair note). See v2_results/RUN_LOG.md for
the exact invocation and v2_results/rerun_reconciliation_2026-10-06.md
for the verification.

Method per contiguous segment:
  y(t) = c0 + c1*(t-tc) + A * s((t-t0)/w) + noise,  s(x)=0.5*(1+tanh(x))
solved by ordinary least squares on a (t0, tau) grid; S/N = A_hat/sigma_A
with sigma_A from fit residuals. Detection on inverse-variance
band-averaged EVPA; per-SPW fits test achromaticity.

Inputs (read-only): SGRA2017_*_IQUV.npz
Outputs: report .md, PNG diagnostics, this script.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = "/home/hatch/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data/sgra_work"

TAU_GRID = np.array([10., 15., 22., 32., 46.9, 68., 100., 120.])  # s
N_CAMP = 1000         # surrogate campaigns for the per-EB null
                      # (2026-10-06 correction: was 500 in the committed source while the
                      #  published methodology claimed 1000; corrected to match.)
GAP_TOL = 20.0        # s; larger gaps start a new segment
I_MASK_JY = 1.0       # mask integrations with median I below this


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
    """R1: unwrap along TIME (axis 0), not across spectral windows."""
    return np.degrees(np.unwrap(np.radians(e), period=np.pi, axis=0))


def search_segment(t, y):
    """Grid search; returns structured array over (tau, t0); OLS, sigma_A
    from fit residuals."""
    n = len(t)
    tc = t.mean()
    tb = t - tc
    results = []
    for tau in TAU_GRID:
        w = tau / 2.0
        ok = (t >= t[0] + 2 * w) & (t <= t[-1] - 2 * w)
        t0s = t[ok]
        if len(t0s) == 0:
            continue
        X_ = (t[:, None] - t0s[None, :]) / w
        S = 0.5 * (1.0 + np.tanh(X_))
        m = len(t0s)
        XtX = np.empty((m, 3, 3))
        Xty = np.empty((m, 3))
        XtX[:, 0, 0] = n
        XtX[:, 0, 1] = XtX[:, 1, 0] = tb.sum()
        XtX[:, 1, 1] = (tb ** 2).sum()
        XtX[:, 0, 2] = XtX[:, 2, 0] = S.sum(axis=0)
        XtX[:, 1, 2] = XtX[:, 2, 1] = (tb[:, None] * S).sum(axis=0)
        XtX[:, 2, 2] = (S ** 2).sum(axis=0)
        Xty[:, 0] = y.sum()
        Xty[:, 1] = (tb * y).sum()
        Xty[:, 2] = (S * y[:, None]).sum(axis=0)
        beta = np.linalg.solve(XtX, Xty[:, :, None])[..., 0]  # (m,3): c0,c1,A
        # (explicit (m,3,1) RHS: np.linalg.solve with a stacked (m,3) RHS
        # raises under numpy>=2; the [:,:,None] form works on 1.x and 2.x)
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
    return np.array(results,
                    dtype=[("tau", float), ("t0", float), ("A", float),
                           ("sigA", float), ("snr", float)])


def fit_at(t, y, t0, tau):
    """Single (t0, tau) OLS fit; returns (A, sigA, snr)."""
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


def baseline_fit(t, y):
    """OLS linear baseline; returns (fitted baseline, residuals)."""
    tb = t - t.mean()
    X = np.column_stack([np.ones_like(t), tb])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    base = X @ beta
    return base, y - base


def surrogate_series(t, y, rng):
    """R2: residual-based surrogate. Fits the linear baseline, applies a
    random transformation (circular shift / time reversal / sign-flipped
    shift) to the RESIDUALS only, and adds the fitted baseline back.
    Preserves slow drift and correlated noise; destroys coherent tanh
    transitions. Avoids the v1 artifact where shifting the raw series
    joined drift end-to-beginning into a template-matching discontinuity."""
    base, r = baseline_fit(t, y)
    n = len(t)
    mode = rng.integers(3)
    if mode == 0:
        k = rng.integers(1, n)
        rs = np.concatenate([r[k:], r[:k]])
    elif mode == 1:
        rs = r[::-1]
    else:
        k = rng.integers(1, n)
        rs = -np.concatenate([r[k:], r[:k]])
    return base + rs


def campaign_null(seg_data, n_camp=N_CAMP, seed=0):
    """R3: per-EB null = distribution of the campaign maximum: one
    surrogate per segment, max |S/N| over grid AND segments, repeated
    n_camp times. This matches the detection statistic."""
    rng = np.random.default_rng(seed)
    maxima = np.empty(n_camp)
    for c in range(n_camp):
        best = 0.0
        for sd in seg_data:
            ys = surrogate_series(sd["t"], sd["ybar"], rng)
            r = search_segment(sd["t"], ys)
            if len(r):
                m = np.max(np.abs(r["snr"]))
                if m > best:
                    best = m
        maxima[c] = best
    return maxima


def achromaticity(t, es, sig_spw, t0, tau, lam2):
    """Per-SPW amplitude fits at (t0, tau); returns diagnostics dict."""
    Aspw, Sspw = [], []
    for spw in range(es.shape[1]):
        a, sa, _ = fit_at(t, es[:, spw], t0, tau)
        Aspw.append(a); Sspw.append(sa)
    Aspw = np.array(Aspw); Sspw = np.array(Sspw)
    w = 1 / np.maximum(Sspw, 1e-30) ** 2
    Amean = (Aspw * w).sum() / w.sum()
    chi2 = (((Aspw - Amean) / np.maximum(Sspw, 1e-30)) ** 2).sum()  # 3 dof
    # Faraday alternative: A = k * lambda^2 (no intercept)
    Xs = lam2 / np.maximum(Sspw, 1e-30)
    ys = Aspw / np.maximum(Sspw, 1e-30)
    kf = (Xs @ ys) / (Xs @ Xs)
    chi2_far = (((Aspw - kf * lam2) / np.maximum(Sspw, 1e-30)) ** 2).sum()
    return dict(Aspw=Aspw, Sspw=Sspw, Amean=Amean, chi2=chi2,
                chi2_far=chi2_far, k_faraday=kf)


def veto(ac):
    """R5: enforced achromaticity veto — per-SPW S/N coincidence plus a
    dilution-ratio test.

    A genuine sky signal (achromatic or Faraday-like) appears in multiple
    bands: (a) >=3 of 4 SPWs agree in sign with the band-averaged amplitude
    with |S/N|>3, and (b) the largest single-SPW amplitude is not much
    larger than the band-averaged amplitude. A single-SPW instrumental
    artifact appears diluted by ~4x in the inverse-variance average, so
    max|A_spw|/|A_bar| ~ 4 (equal weights); true signals give ~1.0-1.2.

    (An amplitude-chi2 version was abandoned first: per-SPW amplitude
    errors are misspecified in real data with inter-SPW correlated
    systematics — true 55.6-deg injections reached chi2/3 ~ 50-128 while
    some single-SPW jumps scored < 5. A pure coincidence rule was tried
    second but admits selection bias: the veto is evaluated at a location
    chosen by the detection statistic on overlapping data, inflating the
    other SPWs' apparent S/N. The dilution ratio is robust to that bias.)
    """
    Aspw = np.asarray(ac["Aspw"]); Sspw = np.asarray(ac["Sspw"])
    Abar = ac["Amean"]
    if abs(Abar) < 1e-12:
        return False
    snr_spw = Aspw / np.maximum(Sspw, 1e-30)
    agree = (np.sign(snr_spw) == np.sign(Abar)) & (np.abs(snr_spw) > 3)
    coincidence = int(agree.sum()) >= 3
    dilution = np.max(np.abs(Aspw)) / abs(Abar)
    return bool(coincidence and dilution <= 2.0)


def build_segments(eb):
    t, evpa, good = eb["t"], eb["evpa"], eb["good"]
    segs = segments(t, good)
    seg_data = []
    for idx in segs:
        ts = t[idx]
        es = unwrap_evpa(evpa[idx])          # (n,4), R1 temporal unwrap
        d = np.diff(es, axis=0)
        sig_spw = np.maximum(d.std(axis=0) / np.sqrt(2), 0.2)
        wgt = 1.0 / sig_spw ** 2
        ybar = (es * wgt).sum(axis=1) / wgt.sum()
        seg_data.append(dict(t=ts, es=es, ybar=ybar, sig_spw=sig_spw,
                             wgt=wgt))
    return seg_data


def analyze_eb(path, n_camp=N_CAMP, seed=1234):
    eb = load_eb(path)
    seg_data = build_segments(eb)
    print(f"{path.split('/')[-1]}: {len(eb['t'])} int, {eb['good'].sum()} good, "
          f"{len(seg_data)} segments")

    # --- detection: best per-segment candidate, then campaign max ---
    seg_best = []
    for si, sd in enumerate(seg_data):
        r = search_segment(sd["t"], sd["ybar"])
        if len(r) == 0:
            continue
        j = np.argmax(np.abs(r["snr"]))
        seg_best.append((si, r["tau"][j], r["t0"][j], r["A"][j],
                         r["sigA"][j], r["snr"][j]))
    seg_best.sort(key=lambda c: -abs(c[5]))
    camp_max = abs(seg_best[0][5]) if seg_best else 0.0

    # --- campaign null ---
    null = campaign_null(seg_data, n_camp=n_camp, seed=seed)
    null95, null99 = np.percentile(null, [95, 99])

    # --- achromaticity + veto on top candidates ---
    cands = []
    for (si, tau, t0, A, sigA, snr) in seg_best[:5]:
        sd = seg_data[si]
        ac = achromaticity(sd["t"], sd["es"], sd["sig_spw"], t0, tau,
                           eb["lam2"])
        cands.append(dict(si=si, tau=tau, t0=t0, A=A, sigA=sigA, snr=snr,
                          ac=ac, veto_pass=veto(ac)))

    return dict(eb=eb, seg_data=seg_data, seg_best=seg_best,
                camp_max=camp_max, null=null, null95=null95, null99=null99,
                cands=cands)


def injection_recovery(seg_data, lam2, thr, amps, taus, trials=100, seed=7):
    """R4: inject achromatic tanh(A, t0, tau) into real per-SPW series,
    run full pipeline (detection + veto); returns P(detect) per (tau, A).
    Detection requires: segment best |S/N| >= thr, veto passes at that
    candidate, and recovered t0 within +/-tau of the injected t0.
    (2026-10-06 correction: default trials was 25 while published
    methodology claimed 100; corrected to match.)"""
    rng = np.random.default_rng(seed)
    P = np.zeros((len(taus), len(amps)))
    chi2_true = []   # chi2/3 of detected true injections (diagnostic)
    dil_true = []    # dilution ratio max|A_spw|/|A_bar| (veto diagnostic)
    for ti, tau in enumerate(taus):
        w = tau / 2.0
        # only segments long enough to host the transition (t0 +/- 2w)
        elig = [i for i, sd in enumerate(seg_data)
                if sd["t"][-1] - sd["t"][0] >= 4 * w]
        if not elig:
            continue
        weights = np.array([len(seg_data[i]["t"]) for i in elig], dtype=float)
        weights /= weights.sum()
        for ai, A in enumerate(amps):
            hits = 0
            for _ in range(trials):
                si = elig[rng.choice(len(elig), p=weights)]
                sd = seg_data[si]
                t = sd["t"]
                t0 = rng.uniform(t[0] + 2 * w, t[-1] - 2 * w)
                s = 0.5 * (1.0 + np.tanh((t - t0) / w))
                es_inj = sd["es"] + A * s[:, None]      # achromatic
                ybar = (es_inj * sd["wgt"]).sum(axis=1) / sd["wgt"].sum()
                r = search_segment(t, ybar)
                if len(r) == 0:
                    continue
                j = np.argmax(np.abs(r["snr"]))
                if abs(r["snr"][j]) < thr:
                    continue
                if abs(r["t0"][j] - t0) > tau:
                    continue
                ac = achromaticity(t, es_inj, sd["sig_spw"],
                                   r["t0"][j], r["tau"][j], lam2)
                if not veto(ac):
                    continue
                hits += 1
                chi2_true.append(ac["chi2"] / 3.0)
                dil_true.append(np.max(np.abs(ac["Aspw"]))
                                / max(abs(ac["Amean"]), 1e-12))
            P[ti, ai] = hits / trials
    return P, np.array(chi2_true), np.array(dil_true)


def single_spw_jump_fpr(seg_data, lam2, thr, jumps=(20., 40., 80.),
                        trials=100, seed=21):
    """Inject a jump into ONE SPW only; measure how often it passes the
    full pipeline incl. veto (should be ~0 for a good veto)."""
    rng = np.random.default_rng(seed)
    out = {}
    weights = np.array([len(sd["t"]) for sd in seg_data], dtype=float)
    weights /= weights.sum()
    for J in jumps:
        chi2s, passed, det = [], 0, 0
        for _ in range(trials):
            si = rng.choice(len(seg_data), p=weights)
            sd = seg_data[si]
            t = sd["t"]
            spw = rng.integers(4)
            i0 = rng.integers(2, len(t) - 2)
            es_inj = sd["es"].copy()
            es_inj[i0:, spw] += J          # single-sample step, one SPW
            ybar = (es_inj * sd["wgt"]).sum(axis=1) / sd["wgt"].sum()
            r = search_segment(t, ybar)
            if len(r) == 0:
                continue
            j = np.argmax(np.abs(r["snr"]))
            if abs(r["snr"][j]) < thr:
                continue
            det += 1
            ac = achromaticity(t, es_inj, sd["sig_spw"],
                               r["t0"][j], r["tau"][j], lam2)
            chi2s.append(ac["chi2"] / 3.0)
            if veto(ac):
                passed += 1
        out[J] = dict(detected=det / trials, false_pass=passed / trials,
                      chi2=np.array(chi2s))
    return out


def scan_single_sample_jumps(sd):
    """Light single-sample jump scan on band-averaged EVPA (unresolved
    tau << 4 s steps are outside the tanh grid). Returns top jumps with
    per-SPW consistency info."""
    y = sd["ybar"]
    d = np.diff(y)
    sig = np.median(np.abs(d)) / 0.6745  # robust per-sample noise
    sig = max(sig, 1e-6)
    z = np.abs(d) / sig
    order = np.argsort(-z)[:5]
    jumps = []
    for k in order:
        per_spw = np.diff(sd["es"], axis=0)[k, :]
        jumps.append(dict(i=int(k), dy=float(d[k]), z=float(z[k]),
                          per_spw=per_spw))
    return jumps, sig


# ---------------------------------------------------------------- selftest
def selftest():
    """Validate the repairs on synthetics. Raises on failure."""
    rng = np.random.default_rng(0)
    # T1: temporal unwrapping of a +20-deg step near the angle boundary.
    # Flat base so the step is measured cleanly; the base sits near -80 deg
    # so the +20-deg step exercises the +/-90-deg wrap.
    n = 200
    base = np.full((n, 4), -80.0)
    step = np.zeros((n, 4)); step[100:, :] = 20.0
    e = (base + step + 89.9) % 180 - 89.9   # wrap into (-90, 90]
    u = unwrap_evpa(e)
    dA = u[101:120, :].mean(axis=0) - u[80:99, :].mean(axis=0)
    assert np.all(np.abs(dA - 20.0) < 2.0), f"T1 unwrap failed: {dA}"
    print(f"T1 unwrap OK: recovered step per SPW = {np.round(dA,2)}")
    # T1b: the v1 bug, for the record — unwrap across SPWs (axis=-1) cannot
    # repair a step that crosses the +/-90-deg wrap cut, so the measured
    # step comes back off by exactly 180 deg in every band. (Claude audit
    # 2026-10-06: a +20-deg step read as -160 deg.)
    e2 = np.full((n, 4), 80.0)
    e2[100:, :] += 20.0
    e2 = e2 + rng.normal(0, 1.0, e2.shape)
    e2 = (e2 + 89.9) % 180 - 89.9
    u_bug = np.degrees(np.unwrap(np.radians(e2), period=np.pi))  # axis=-1
    dA_bug = u_bug[101:120, :].mean(axis=0) - u_bug[80:99, :].mean(axis=0)
    u_fix2 = unwrap_evpa(e2)
    dA_fix2 = u_fix2[101:120, :].mean(axis=0) - u_fix2[80:99, :].mean(axis=0)
    print(f"T1b v1-style (axis=-1) gives: {np.round(dA_bug,2)} "
          f"vs fixed: {np.round(dA_fix2,2)} (true step +20 deg)")
    assert np.all(np.abs(dA_bug + 160.0) < 5.0), \
        f"T1b: bug not demonstrated (buggy={np.round(dA_bug,2)})"
    assert np.all(np.abs(dA_fix2 - 20.0) < 3.0), \
        f"T1b: fixed unwrap failed on boundary-crossing step: {dA_fix2}"
    print("T1b OK: bug demonstrated (-160 deg) and fixed (+20 deg)")

    # T2: drift-only series, no event.
    #   (a) v1-style raw circular shift should inflate the null (the artifact)
    #   (b) v2 residual shift should not.
    t = np.arange(600) * 4.0
    drift = 30.0 * (t - t.mean()) / (t.max() - t.min())
    y = drift + rng.normal(0, 0.5, len(t))
    sd = dict(t=t, ybar=y)
    # raw-shift null (v1 style)
    raw_max = []
    for _ in range(60):
        k = rng.integers(1, len(t))
        r = search_segment(t, np.concatenate([y[k:], y[:k]]))
        raw_max.append(np.max(np.abs(r["snr"])) if len(r) else 0)
    raw99 = np.percentile(raw_max, 99)
    # residual-shift null (v2)
    v2null = campaign_null([sd], n_camp=60, seed=1)
    v299 = np.percentile(v2null, 99)
    print(f"T2 drift-only: raw-shift null 99th={raw99:.1f} (artifact), "
          f"residual-shift null 99th={v299:.1f}")
    assert raw99 > 20, "T2: raw-shift artifact did not reproduce"
    assert v299 < 12, f"T2: residual null still inflated: {v299}"
    print("T2 OK: residual null immune to the drift-shift artifact")

    # T3: inject 55.6-deg tanh at 46.9 s into white noise -> loud detection
    y3 = rng.normal(0, 0.5, len(t))
    w = 46.9 / 2
    y3 += 55.6 * 0.5 * (1 + np.tanh((t - 1200.0) / w))
    r = search_segment(t, y3)
    j = np.argmax(np.abs(r["snr"]))
    print(f"T3 injection: recovered A={r['A'][j]:.1f} tau={r['tau'][j]:.0f} "
          f"S/N={r['snr'][j]:.0f}")
    assert abs(r["A"][j] - 55.6) < 5 and r["snr"][j] > 50
    print("T3 OK")
    print("SELFTEST PASSED")


# ---------------------------------------------------------------- plotting
def plot_eb(res, out_prefix, ebname):
    eb, seg_data = res["eb"], res["seg_data"]
    t_all = eb["t"] / 60.0
    fig, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for sd in seg_data:
        ax[0].plot(sd["t"] / 60, sd["ybar"], ".", ms=2)
    for c in res["cands"][:3]:
        ax[0].axvline(c["t0"] / 60, color="r", ls="--", lw=1)
    ax[0].set_ylabel("EVPA band-avg (deg, unwrapped)")
    ax[0].set_title(f"{ebname}: EVPA track (4-SPWs inv-var avg) [v2]")
    pflux = np.sqrt(eb["Q"] ** 2 + eb["U"] ** 2)
    for s in range(4):
        ax[1].plot(t_all, pflux[:, s], ".", ms=2,
                   label=f"{eb['freq'][s]:.1f} GHz")
    ax[1].set_ylabel("polarized flux (Jy)")
    ax[1].set_xlabel("minutes since EB start")
    ax[1].legend(fontsize=8, ncol=4)
    fig.tight_layout(); fig.savefig(f"{out_prefix}_track.png", dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(res["null"], bins=40, histtype="step", lw=1.5,
            label=f"campaign null (resid-shift), n={len(res['null'])}")
    ax.axvline(res["camp_max"], color="C1", ls="--",
               label=f"observed campaign max |S/N|={res['camp_max']:.1f}")
    ax.axvline(res["null99"], color="k", ls=":",
               label=f"null 99th={res['null99']:.1f}")
    ax.set_xlabel("campaign max |S/N| over grid x segments")
    ax.set_ylabel("count")
    ax.legend(fontsize=8)
    ax.set_title(f"{ebname}: campaign null [v2]")
    fig.tight_layout(); fig.savefig(f"{out_prefix}_null.png", dpi=110)
    plt.close(fig)


def a_quantile(amps, p, q):
    """Amplitude at which detection probability reaches q (interp)."""
    if np.all(p < q):
        return np.inf
    i = np.argmax(p >= q)
    if i == 0:
        return amps[0]
    a0, a1 = amps[i - 1], amps[i]
    p0, p1 = p[i - 1], p[i]
    return a0 + (q - p0) / max(p1 - p0, 1e-12) * (a1 - a0)


def main(argv=None):
    import argparse, os, time
    ap = argparse.ArgumentParser(description="EVPA tanh-transient search v2")
    ap.add_argument("files", nargs="*", help=".npz IQUV files to analyze")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--ncamp", type=int, default=N_CAMP)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-inject", action="store_true",
                    help="skip injection-recovery calibration")
    args = ap.parse_args(argv)

    if args.selftest:
        selftest()
        return

    if args.files:
        paths = [os.path.abspath(f) for f in args.files]
    else:
        paths = [os.path.join(DATA_DIR, f) for f in
                 ["SGRA2017_X4947_IQUV.npz", "SGRA2017_X448f_IQUV.npz",
                  "SGRA2017_X4227_IQUV.npz"]]  # 2026-10-06: X4227 was omitted from the default list; added
    outdir = os.path.abspath(args.outdir) if args.outdir \
        else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)

    t_start = time.time()
    results = {}
    for path in paths:
        name = os.path.basename(path).replace("_IQUV.npz", "")
        res = analyze_eb(path, n_camp=args.ncamp)
        plot_eb(res, os.path.join(outdir, name + "_v2"), name)
        results[name] = res

    # ---- injection-recovery per EB (threshold = its own campaign null99) --
    amps = np.array([0.5, 1., 2., 3., 4., 6., 8., 12., 20., 30., 55.6])
    taus_ir = np.array([10., 46.9, 120.])
    ir = {}
    if not args.skip_inject:
        for name, r in results.items():
            P, chi2t, dilt = injection_recovery(r["seg_data"], r["eb"]["lam2"],
                                                r["null99"], amps, taus_ir)
            js = single_spw_jump_fpr(r["seg_data"], r["eb"]["lam2"],
                                     r["null99"])
            ir[name] = dict(P=P, chi2_true=chi2t, jumps=js,
                            med_dil=np.median(dilt) if len(dilt) else np.nan,
                            max_dil=np.max(dilt) if len(dilt) else np.nan)
            print(f"{name}: injection P(detect) done in "
                  f"{time.time()-t_start:.0f}s; true-signal dilution ratio: "
                  f"median={ir[name]['med_dil']:.2f}, max={ir[name]['max_dil']:.2f} "
                  f"(veto allows <= 2.0)")

    # ---- report ----
    lines = []
    A = lines.append
    eb_names = ", ".join(results.keys())
    A(f"# EVPA transient search v2 — {args.label or eb_names} "
      f"({len(paths)} EBs)")
    A("")
    A("**Implementation:** `evpa_transient_search_v2.py`. Repairs vs v1: "
      "temporal unwrapping (axis=0); residual-based surrogates (baseline fit "
      "+ shifted residuals); campaign-level null (max over grid x segments "
      f"per EB, n={args.ncamp} campaigns); injection-recovery calibration; "
      "enforced achromaticity veto (per-SPW S/N coincidence + "
      "dilution-ratio test).")
    A("")
    for name, r in results.items():
        eb = r["eb"]
        n_int = sum(len(sd["t"]) for sd in r["seg_data"])
        A(f"## {name}")
        A(f"- Integrations: {n_int} in {len(r['seg_data'])} segments; "
          f"4-s cadence; SPWs {', '.join(f'{f:.1f}' for f in eb['freq'])} GHz.")
        A(f"- Campaign null (residual-shift): 95th={r['null95']:.1f}, "
          f"99th={r['null99']:.1f}.")
        A(f"- Observed campaign max |S/N|={r['camp_max']:.1f} "
          f"({'ABOVE' if r['camp_max'] > r['null99'] else 'below'} null 99th).")
        A("- Top candidates (veto applied):")
        for c in r["cands"][:3]:
            ac = c["ac"]
            A(f"  - seg{c['si']} t0+{c['t0']/60:.1f}min tau={c['tau']:.0f}s "
              f"A={c['A']:+.1f} S/N={c['snr']:+.1f} "
              f"veto={'PASS' if c['veto_pass'] else 'FAIL'} "
              f"(chi2/3={ac['chi2']/3:.1f}, Faraday chi2/3={ac['chi2_far']/3:.1f})")
        if name in ir:
            P = ir[name]["P"]
            A("- Injection-recovery P(detect) vs amplitude (full pipeline):")
            for ti, tau in enumerate(taus_ir):
                a90 = a_quantile(amps, P[ti], 0.90)
                a99 = a_quantile(amps, P[ti], 0.99)
                p556 = np.interp(55.6, amps, P[ti])
                A(f"  - tau={tau:.0f}s: A_90={a90:.1f} deg, A_99={a99:.1f} deg, "
                  f"P(detect 55.6 deg)={p556:.3f}")
            j = ir[name]["jumps"]
            jl = ", ".join(f"{J:.0f}deg: det={v['detected']:.2f}, "
                            f"veto-pass={v['false_pass']:.2f}"
                            for J, v in j.items())
            A(f"- Single-SPW-jump control: {jl}")
            A(f"- True-signal dilution ratio max|A_spw|/|A_bar|: median "
              f"{ir[name]['med_dil']:.2f}, max {ir[name]['max_dil']:.2f} "
              f"(veto passes <= 2.0; single-SPW artifacts score ~4)")
        A("")
    # single-sample jump scan summary
    A("## Single-sample jump scan (unresolved tau << 4 s)")
    for name, r in results.items():
        A(f"- {name}:")
        for sd in r["seg_data"]:
            jumps, sig = scan_single_sample_jumps(sd)
            top = jumps[0]
            spw_s = ", ".join(f"{v:+.1f}" for v in top["per_spw"])
            A(f"  - seg span {(sd['t'][-1]-sd['t'][0]):.0f}s: strongest jump "
              f"dy={top['dy']:+.1f} deg (z={top['z']:.1f}, robust sig={sig:.2f}); "
              f"per-SPW steps=[{spw_s}]")
    A("")
    A("## Caveats")
    A("- Surrogate null is conservative: any real coherent transient in the "
      "data also enters the residuals and inflates the null.")
    A("- Temporal unwrapping assumes no true >90-deg jump within one 4-s "
      "sample; unresolved steps are covered only by the jump scan above.")
    A("- Exclusion applies to resolved tanh ramps with tau in [10,120] s "
      "occurring inside analyzed segments.")
    A("- v1 claims (null percentiles ~40-46, 'excluded at >>99%' from "
      "predicted S/N) are SUPERSEDED by this v2 calibration.")
    report_name = args.report or (
        "transient_search_v2_" + "_".join(sorted(results.keys())) + ".md")
    with open(os.path.join(outdir, report_name), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[done in {time.time()-t_start:.0f}s -> {report_name}]")


if __name__ == "__main__":
    main()
