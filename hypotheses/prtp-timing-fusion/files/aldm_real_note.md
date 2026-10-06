# ALDM robust GLS on real NANOGrav residuals — run note

Date: 2026-09-22. Status: **archival-data analysis, not a detection claim.**

## What was run

The user's `compute_aldm_gls_robust` (pulsar-major flattening, relative
regularization, explicit monopole variance) applied to the real
`nanograv_binned.npz` residuals: 14 common 30-day epochs x 4 pulsars
(J0437-4715, J1909-3744, B1937+21, B1855+09), residuals in seconds.
Design matrix = per-epoch common (monopolar) mode (56x14).
Noise: per-datapoint white variances from the bins; red noise as
per-pulsar diagonal variance from the NANOGrav chain medians
(log10_A, gamma), same construction as `nanograv_gls_red.py`.
Residuals transposed to pulsar-major to match the function's convention.

## Results

1. **Reproduces both earlier findings independently.** Series-variance
   ratio (GLS common mode vs unweighted mean): white-only C = **9.8x
   worse**; white+red C = **0.035 (~28x better)**. Matches the
   8.63 / 0.037 from the independent implementation.

2. **Large common-mode signal present.** White+red per-epoch common mode
   (ns): +275, +334, +352, -138, -160, -228, -202, -97, +69, +50,
   -83, -28, -34, +40 against formal per-epoch errors of ~32-50 ns.
   Swings are 5-10 sigma per epoch.

3. **Excess common variance: chi2 = 406 on 14 dof** for the
   mean-subtracted common-mode series vs its formal GLS covariance.
   The white+red diagonal model does not explain the epoch-to-epoch
   common scatter. The jumps (+352 to -138 between adjacent epochs)
   are too sharp for smooth (gamma~4) red noise, pointing to a
   genuinely epoch-uncorrelated common component: clock, ephemeris,
   ALDM-like monopole, or unmodeled white-ish common noise.

4. **Monopole-variance grid:** raising `aldm_variance` from (10 ns)^2 to
   (1 us)^2 leaves the common-mode point estimates essentially
   unchanged (series RMS fixed at 184 ns) and only inflates the formal
   errors (35 ns -> ~1 us). The estimator cannot separate monopole
   variance from the common mode it estimates -- expected, since they
   live in the same subspace. A likelihood/evidences comparison over
   `aldm_variance` would be needed for model selection; not done here.

## Caveats (read before quoting)

- Red noise is diagonal-only: temporal red correlations between epochs
  are ignored, which inflates chi2 somewhat. The sharp epoch-to-epoch
  jumps argue most of the excess is real common variance, but the exact
  406 number is model-dependent.
- N = 14 clustered epochs (J0437-4715 span-limited, gaps to 720 days).
- No monopole/quadrupole separation: with 4 pulsars and no HD template
  fit, this cannot distinguish ALDM/clock/ephemeris (monopolar) from a
  GWB monopole projection. It is evidence of *common* variance, not of
  any specific source.
- Single-pulsar leakage (90% weight sits on J1909-3744 under white+red)
  cannot be fully excluded with diagonal red modeling.

## Files

- `aldm_real_results.json` -- common-mode series, errors, grid, chi2
- `/tmp/aldm/aldm_real_run.py` -- analysis script (scratch, not archived)
- `nanograv_binned.npz`, `nanograv_gls_red.py` -- inputs (unchanged)
