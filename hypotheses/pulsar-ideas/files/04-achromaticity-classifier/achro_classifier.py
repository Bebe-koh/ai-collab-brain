#!/usr/bin/env python3
"""
Automated achromaticity classifier for pulsar timing noise.

Fresh re-derivation (2026-10-06) of the contemporaneous-native-bin
cross-correlation method described in
~/workspace/prtp/hidden_files/b1937_wobble_note.md, extended with the
blind-spot fix documented in fresh_run_note.md:

  BLIND SPOT of correlation-only: a pure dispersion-measure (DM) signal
  produces the SAME shape in every band (it is one underlying DM(t) scaled
  by nu^-2), so the cross-band correlation is ~1 for DM noise too — as long
  as the signal clears the noise in both bands. Correlation alone cannot
  separate "achromatic" from "DM". The fix used here: measure BOTH the
  weighted correlation r (is there a common mode?) AND the common-mode
  amplitude ratio alpha = A2/A1 (what is its chromatic index?):
      achromatic : alpha ~= 1
      DM-like    : alpha ~= (nu1/nu2)^2
      scattering : alpha ~= (nu1/nu2)^4
  alpha is estimated symmetrically as sign(r)*sqrt(var2/var1) on the
  contemporaneous bins, with bootstrap uncertainties on both r and alpha.

Pipeline per pulsar:
  1. Load public NANOGrav 15-yr narrowband .par/.tim with PINT.
  2. Two configurations:
       FULL  - published par as-is (includes DMX): post-fit residuals test
               for RESIDUAL (unmodeled) chromaticity -> model-adequacy check.
       NODMX - DMX parameters removed/zeroed and refit: residuals keep the
               full chromatic content -> dominant-noise-character classifier.
  3. Split residuals by receiver band; 30-day inverse-variance-weighted bins.
  4. Keep ONLY genuinely contemporaneous native bins (identical bin centers
     present in both bands).
  5. Weighted correlation + amplitude ratio + bootstrap CIs + shuffle null.
  6. Classify per band pair; optional sliding-window ("per-epoch") mode.

Weighting choice (documented): bin weight w = 1/(s1^2 + s2^2) with
s = scaled white error, sigma^2 = (EFAC*sigma_toa)^2 + EQUAD^2, from the
fitted white-noise parameters. ECORR (intra-epoch correlated white) is not
in the weights; the bootstrap over bins still yields honest CIs for r/alpha.
An unweighted cross-check is run and reported.
"""

import numpy as np

BIN_DAYS = 30.0
N_BOOT = 2000
RNG_SEED = 20261006


# --------------------------------------------------------------------------
# Binning
# --------------------------------------------------------------------------
def weighted_bin(times_mjd, resids_us, sigmas_us, bin_days=BIN_DAYS):
    """Inverse-variance weighted mean per bin on a fixed grid.

    Returns (centers, means, errs, counts). Bins with no TOAs are dropped;
    the grid itself is fixed so that "contemporaneous" matching across bands
    is exact.
    """
    t = np.asarray(times_mjd, float)
    r = np.asarray(resids_us, float)
    s = np.asarray(sigmas_us, float)
    ok = np.isfinite(t) & np.isfinite(r) & np.isfinite(s) & (s > 0)
    t, r, s = t[ok], r[ok], s[ok]
    if len(t) == 0:
        return np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0, dtype=int)
    t0 = np.floor(t.min())
    idx = ((t - t0) / bin_days).astype(int)
    centers, means, errs, counts = [], [], [], []
    for b in np.unique(idx):
        m = idx == b
        w = 1.0 / s[m] ** 2
        wsum = w.sum()
        if wsum <= 0:
            continue
        centers.append(t0 + (b + 0.5) * bin_days)
        means.append(np.sum(w * r[m]) / wsum)
        errs.append(1.0 / np.sqrt(wsum))
        counts.append(int(m.sum()))
    return (np.array(centers), np.array(means), np.array(errs),
            np.array(counts, dtype=int))


def contemporaneous(b1, b2):
    """Match two binned series on identical bin centers.

    b1, b2 = (centers, means, errs, counts). Returns
    (x, sx, y, sy, n_overlap) or None if no overlap.
    """
    c1, m1, e1, _ = b1
    c2, m2, e2, _ = b2
    lut = {c: i for i, c in enumerate(c1)}
    pairs = [(lut[c], j) for j, c in enumerate(c2) if c in lut]
    if not pairs:
        return None
    i1 = np.array([p[0] for p in pairs])
    i2 = np.array([p[1] for p in pairs])
    return m1[i1], e1[i1], m2[i2], e2[i2], len(pairs)


# --------------------------------------------------------------------------
# Statistics on contemporaneous bins
# --------------------------------------------------------------------------
def _wstats(x, y, sx, sy, weighted=True):
    """Weighted means/variances/covariance. Returns dict."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    sx = np.asarray(sx, float); sy = np.asarray(sy, float)
    if weighted:
        w = 1.0 / (sx ** 2 + sy ** 2)
    else:
        w = np.ones_like(x)
    wsum = w.sum()
    xm = np.sum(w * x) / wsum
    ym = np.sum(w * y) / wsum
    dx, dy = x - xm, y - ym
    vx = np.sum(w * dx * dx) / wsum
    vy = np.sum(w * dy * dy) / wsum
    cv = np.sum(w * dx * dy) / wsum
    return dict(w=w, xm=xm, ym=ym, vx=vx, vy=vy, cv=cv)


def wcorr(x, y, sx, sy, weighted=True):
    """Weighted Pearson correlation of contemporaneous bins."""
    st = _wstats(x, y, sx, sy, weighted)
    den = np.sqrt(st["vx"] * st["vy"])
    if den <= 0:
        return np.nan
    return st["cv"] / den


def amplitude_ratio(x, y, sx, sy, weighted=True, debiased=True):
    """Symmetric common-mode amplitude ratio A_y / A_x.

    alpha = sign(r) * sqrt(var_y / var_x) on the contemporaneous bins.
    For a common mode s(t) with band scalings k1, k2 this estimates k2/k1.

    debiased=True (default): subtract the mean measurement-error variance
    from each band's variance first. The raw ratio is biased toward 1 by the
    noise floor: sqrt((k2^2 V + s2^2)/(k1^2 V + s1^2)) != k2/k1. Debiasing
    restores an unbiased estimate when the bin errors are honest.
    """
    st = _wstats(x, y, sx, sy, weighted)
    r = st["cv"] / np.sqrt(st["vx"] * st["vy"]) if st["vx"] > 0 and st["vy"] > 0 else np.nan
    if not np.isfinite(r) or st["vx"] <= 0:
        return np.nan
    vx, vy = st["vx"], st["vy"]
    if debiased:
        ex2 = np.mean(np.asarray(sx, float) ** 2)
        ey2 = np.mean(np.asarray(sy, float) ** 2)
        vx = max(vx - ex2, 1e-30)
        vy = max(vy - ey2, 0.0)
    if vx <= 0:
        return np.nan
    return np.sign(r) * np.sqrt(vy / vx)


def bootstrap_cis(x, y, sx, sy, n_boot=N_BOOT, seed=RNG_SEED, weighted=True):
    """Bootstrap (resample bins) CIs for (r, alpha, alpha_deb). Returns dict
    with 16/50/84 percentiles and the point estimates."""
    rng = np.random.default_rng(seed)
    n = len(x)
    r0 = wcorr(x, y, sx, sy, weighted)
    a0 = amplitude_ratio(x, y, sx, sy, weighted, debiased=False)
    ad0 = amplitude_ratio(x, y, sx, sy, weighted, debiased=True)
    rb, ab, adb = [], [], []
    for _ in range(n_boot):
        ii = rng.integers(0, n, n)
        rb.append(wcorr(x[ii], y[ii], sx[ii], sy[ii], weighted))
        ab.append(amplitude_ratio(x[ii], y[ii], sx[ii], sy[ii], weighted, debiased=False))
        adb.append(amplitude_ratio(x[ii], y[ii], sx[ii], sy[ii], weighted, debiased=True))
    def pct(v):
        v = np.asarray(v, float)
        v = v[np.isfinite(v)]
        if len(v) == 0:
            return (np.nan, np.nan, np.nan)
        return tuple(np.percentile(v, [16, 50, 84]))
    return dict(r=r0, r_ci=pct(rb), n=n,
               alpha=a0, alpha_ci=pct(ab),
               alpha_deb=ad0, alpha_deb_ci=pct(adb))


def shuffle_null_pvalue(x, y, sx, sy, n_shuf=2000, seed=RNG_SEED + 1, weighted=True):
    """One-sided p-value for r under the null of no cross-band relation
    (shuffle y bins)."""
    rng = np.random.default_rng(seed)
    r0 = wcorr(x, y, sx, sy, weighted)
    cnt = 0
    for _ in range(n_shuf):
        rs = wcorr(x, rng.permutation(y), sx, sy, weighted)
        if np.isfinite(rs) and rs >= r0:
            cnt += 1
    return (cnt + 1) / (n_shuf + 1), r0


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------
def classify_pair(res, nu1_mhz, nu2_mhz, r_sig_thresh=0.5):
    """Classify one band pair (two-tier).

    res: dict from bootstrap_cis. nu1 < nu2 expected (band1 = lower freq).
    Tier 1: is there a detectable common mode? (bootstrap r CI above thresh)
    Tier 2: what is its chromatic index? compare debiased alpha CI to
            1.0 (achromatic), (nu1/nu2)^2 (DM), (nu1/nu2)^4 (scattering).
    Returns (label, detail dict). Labels:
      no-common-mode | achromatic | chromatic:DM-like |
      chromatic:scattering-like | chromatic:unclassified
    """
    r, (r16, _, r84) = res["r"], res["r_ci"]
    # classification uses the DEBIASED amplitude ratio (see module docstring)
    a, (a16, _, a84) = res["alpha_deb"], res["alpha_deb_ci"]
    detail = dict(r=r, r16=r16, r84=r84, alpha=a, a16=a16, a84=a84, n=res["n"],
                  alpha_raw=res["alpha"], alpha_raw_ci=res["alpha_ci"])
    if not np.isfinite(r) or r16 < r_sig_thresh:
        return "no-common-mode", detail
    targets = {
        "DM-like": (nu1_mhz / nu2_mhz) ** 2,
        "scattering-like": (nu1_mhz / nu2_mhz) ** 4,
    }
    detail["targets"] = dict(targets, achromatic=1.0)
    if a16 <= 1.0 <= a84:
        # CI consistent with achromatic; check it is not ALSO consistent
        # with a chromatic target (then it is genuinely ambiguous)
        also = [k for k, v in targets.items() if a16 <= v <= a84]
        if also:
            return "ambiguous:achromatic+" + "+".join(also), detail
        return "achromatic", detail
    # chromatic: alpha CI excludes 1.0
    hits = [k for k, v in targets.items() if a16 <= v <= a84]
    if len(hits) == 1:
        return "chromatic:" + hits[0], detail
    if len(hits) > 1:
        return "chromatic:ambiguous-" + "+".join(hits), detail
    return "chromatic:unclassified", detail
