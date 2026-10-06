# NANOGrav 15-yr real-data GLS check

**Date:** 2026-09-22
**Status:** analysis of public archival data (NANOGrav 15-yr release v2.0.1,
Zenodo DOI 10.5281/zenodo.1477389). Simulation-only context; no flight/hardware
relevance. Nothing here is labeled validated or detected.

## Question

PRTP's surviving quantitative claim: the GLS common-mode estimator
`w = inv(C)@1 / (1.T@inv(C)@1)` (verified spec:
`~/workspace/prtp/PRTP_verified_estimator_spec.md`) beats the unweighted mean
by ~1.5-2x where white noise dominates. That was shown on synthetic data with
known covariance. Does it survive on real timing residuals with
data-estimated covariance?

## Data and files used

NANOGrav 15-yr narrowband `.par` (timing solution) + `.tim` (TOAs), the
collaboration's final versions (PINT-labeled, 2022-03):

| pulsar | par | tim | TOAs kept |
|---|---|---|---|
| J0437-4715 | `narrowband/par/J0437-4715_PINT_20220301.nb.par` | `narrowband/tim/J0437-4715_PINT_20220301.nb.tim` | 5,537 |
| J1909-3744 | `narrowband/par/J1909-3744_PINT_20220303.nb.par` | `narrowband/tim/J1909-3744_PINT_20220303.nb.tim` | 34,829 |
| B1937+21 | `narrowband/par/B1937+21_PINT_20220306.nb.par` | `narrowband/tim/B1937+21_PINT_20220306.nb.tim` | 23,023 |
| B1855+09 | `narrowband/par/B1855+09_PINT_20220301.nb.par` | `narrowband/tim/B1855+09_PINT_20220301.nb.tim` | 7,666 |

Noise chains (the collaboration's own MCMC noise fits to this data):
`narrowband/noise/{J0437-4715,J1909-3744,B1937+21,B1855+09}.nb.chain_1.txt`
with parameter names from the matching `.nb.pars.txt`.

## Method

1. **Residuals:** PINT 1.1.7, post-fit residuals from the published timing
   solution as-is (no refit). DE440 ephemeris; clock files from the
   IPTA pulsar-clock-corrections repo (cached locally; the sandbox blocks
   PINT's own downloader). DM already corrected via the DMX model in the
   `.par` files.
2. **Outlier cut:** MAD-based cut on raw residuals (|r - median| > 8 x 1.4826
   x MAD), 0-5% of TOAs per pulsar. A white-noise-standardized clip was
   tried first and wrongly deleted B1937+21's real red noise; the MAD cut
   is red-noise-safe. One cut applied before both estimators (no bias).
3. **Noise from the data:** per-TOA variance = (EFAC x sigma_TOA)^2 + EQUAD^2
   with posterior-median EFAC/EQUAD/ECORR per backend from the chains.
   Median EFAC: J0437 3.39, J1909 1.01, B1937+21 1.43, B1855+09 1.08.
   Weighted residual RMS: 513 / 356 / 6363 / 1036 ns — B1937+21 is
   red-noise-dominated, the rest are in a sane range for narrowband data.
4. **Common epochs:** 30-day bins; weighted bin means with corrected TOA
   variances. Only **14 common epochs** (all four pulsars observed), because
   J0437-4715 (southern pulsar, VLA campaigns) spans only MJD 57212-58952
   and its epochs are clustered with 510- and 720-day gaps.
5. **Estimators:** per-epoch static GLS (the toy's estimator) vs unweighted
   mean on the 14-epoch residual matrix. Metric: sample variance ratio
   var(GLS estimate)/var(mean estimate), with leave-one-epoch-out jackknife.

## Noise characterization (from the data)

Per-pulsar per-epoch white sigma (median formal bin uncertainty):
J0437 91.3, J1909 13.8, B1937+21 6.0, B1855+09 72.5 ns.

Red-noise chain medians (log10_A, gamma):
J0437 (-13.41, 0.52 — no significant red noise), J1909 (-14.54, 4.09),
B1937+21 (-13.57, 4.03), B1855+09 (-13.99, 3.88).
Red-noise sigma at 30-day bin scale (power-law integral): 218 / 33 / 301 /
107 ns.

Empirical bin scatter: 238 / 272 / 3502 / 609 ns. J0437 matches white+red
almost exactly; the other three exceed it several-fold, and epoch residuals
show strong cross-pulsar correlations (B1937+21 x B1855+09: **0.92**;
J1909 x B1937+21: -0.83) — evidence of common red signals and/or unmodeled
noise at N=14 (interpret cautiously).

## Results

| C used in GLS | weights (J0437, J1909, B1937+21, B1855+09) | var(GLS)/var(mean) | jackknife |
|---|---|---|---|
| white-only (the toy's C) | 0.004, 0.159, **0.832**, 0.006 | **8.63** | 8.63 +/- 0.14 |
| white + red (diagonal, chains) | 0.021, **0.898**, 0.013, 0.069 | **0.037** | 0.038 +/- 0.003 |
| empirical full C (in-sample) | 0.255, 0.751, 0.054, **-0.060** | **0.015** | 0.015 +/- 0.002 |

High-pass (epoch-difference) ratios: white-only 7.57, white+red 0.13.
Unweighted-mean common-mode RMS: ~980 ns; white+red GLS: ~190 ns;
empirical GLS: ~121 ns.

## Interpretation

1. **The toy's white-noise GLS fails on real data: 8.6x worse than the plain
   mean.** Mechanism: B1937+21's formal white floor is 6 ns (23k TOAs), so
   white-only GLS puts 83% weight on it — but its actual epoch scatter is
   3.5 us of red noise. Theory-under-C predicted a 0.035 ratio; measuring
   8.63 proves from the data alone that the white-only C is catastrophically
   misspecified. The toy's "where white noise dominates" qualifier does not
   hold at 30-day epoch scales in real PTA data.
2. **With red noise in the data-estimated C, GLS wins big (0.037, ~27x).**
   But the mechanism differs from the toy: it is almost entirely
   downweighting red-noise-loud pulsars (90% weight on the quiet J1909-3744),
   not exploiting white-noise heterogeneity.
3. **Empirical full C (0.015)** additionally exploits cross-pulsar
   correlations — note the negative weight on B1855+09 canceling its 0.92
   correlation with B1937+21. Interesting, but in-sample at N=14 with
   clustered epochs: treat as suggestive, not measured.
4. This does not falsify the toy's verified math; it bounds its regime. The
   real-data lesson: **covariance must be estimated from the data including
   red noise** — with that, GLS beats the mean decisively, just for a
   different reason than the synthetic study.

## Caveats

- Only 14 common epochs, clustered in campaigns (gaps up to 720 days);
  variance ratios are sample-dependent. Jackknife errors are tight but do
  not capture epoch-clustering dependence.
- Cross-pulsar correlations at N=14 are noisy; the 0.92 could be partly
  chance (though ~3 sigma). Do not claim a common-signal detection.
- Red-noise power-law integral assumes the chain-median power law extends
  across the band; J0437's gamma=0.52 means its "red" term is really
  unconstrained white-ish noise.
- ECORR handled approximately (median added per bin). GWB/ephemeris terms
  from the verified spec were not separately fitted here.
- Scripts: `~/workspace/prtp/hidden_files/nanograv_gls.py` (PINT loading +
  binning), `~/workspace/prtp/hidden_files/nanograv_gls_red.py`
  (red-noise + ratio analysis). Results:
  `~/workspace/prtp/hidden_files/nanograv_gls_results.json`.
  Binned residuals: `~/workspace/prtp/hidden_files/nanograv_binned.npz`.
