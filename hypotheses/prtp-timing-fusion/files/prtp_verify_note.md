# PRTP Estimator Verification — Independent Reimplementation

**Date:** 2026-09-22
**Status:** verification-simulation, simulation-only. Independent code written
from `PRTP_verified_estimator_spec.md` only; `estimators.py`, `simulate.py`,
`xray.py` were NOT imported (only read, for the pulsar catalog coordinates).
**Implementation:** `hidden_files/prtp_verify.py` (plain numpy).
**Results:** `hidden_files/prtp_verify_results.json`. Seed 20260922 throughout.

## What was verified

### Test 1 — Hellings–Downs curve shape: REPRODUCED

Fresh implementation of mu(gamma) = 1 + 3x ln(x) − x/2, x = (1−cos gamma)/2.

| Check | Result |
|---|---|
| mu(0) = 1 (limit) | 1.0 exactly |
| Zero crossing (bisection, computed not asserted) | 49.32° |
| Spherical mean of mu | −1.5e−11 ≈ 0 (no monopole) |
| Legendre a0 (monopole) | −1.5e−11 ≈ 0 |
| Legendre a1 (dipole) | −1.5e−11 ≈ 0 |
| Legendre a2 (quadrupole) | 0.625, dominant |
| PSD over 20 random 6-pulsar direction sets | min eigenvalue 0.024 > 0 |
| Unit diagonal | max deviation 0.0 |

The quadrupolar character (no monopole, no dipole, quadrupole dominant) was
confirmed numerically via the Legendre expansion, not assumed.

### Test 2 — GLS weight optimality: REPRODUCED

60 random symmetric-positive-definite covariance matrices (N=4 and N=8,
log-uniform eigenvalue spectra spanning 5 decades):

- Weights sum to 1 to machine precision (max deviation 4.4e−16).
- GLS variance ≤ unweighted-mean variance in all 60 matrices.
- GLS variance ≤ best of 500 random simplex weight vectors in all 60 matrices.

The spec's weight formula is the variance minimizer, confirmed numerically.

### Test 3 — Headline Monte Carlo: REPRODUCED WITH QUALIFICATION

Synthetic per-epoch residuals y = m·1 + noise, noise ~ N(0, C),
C = white + dipolar ephemeris + quadrupolar GWB per the spec's component
forms. Common (monopolar) component m estimated by GLS fusion vs unweighted
mean; RMS error over trials. Genie-aided (true) covariance, matching the
report's nominal-condition setup.

Noise levels (documented choices): white sigma_w from the catalog
(120/150/250/700 ns); ephemeris 50 m / c ≈ 167 ns dipolar (from the
catalog's EPH_RMS_M); GWB per-epoch RMS parameterized directly and swept
over {50, 100, 200} ns.

| Config | RMS GLS (ns) | RMS unweighted (ns) | Ratio |
|---|---|---|---|
| 4 anchors, full C, GWB 50 ns | 129.2 | 212.5 | 1.65 |
| 4 anchors, full C, GWB 100 ns | 137.4 | 220.9 | 1.61 |
| 4 anchors, full C, GWB 200 ns | 163.4 | 245.7 | 1.50 |
| 4 anchors, white only | 86.3 | 189.3 | 2.19 |
| 4 anchors, white + ephemeris | 127.2 | 218.5 | 1.72 |
| 4 anchors, white + GWB | 101.9 | 206.0 | 2.02 |
| 10 pulsars, full C, GWB 100 ns | 98.9 | 146.0 | 1.48 |

Batch spread (30 batches × 100 trials): full-C config 1.63 ± 0.13
(range 1.32–1.87); white-only 2.24 ± 0.22 (range 1.75–2.62).

**Comparison to the report's claims:**
- Report: "GLS beat the unweighted mean ~2× in all 12 conditions."
  Independent result: GLS always wins (ratios 1.48–2.24, never below 1),
  but the full-covariance configurations sit at 1.5–1.7, not 2. The "~2×"
  headline holds in white-noise-dominated regimes (2.0–2.2) and is a fair
  rounding there, but overstates the correlated-noise regimes.
- Report's specific figures "unweighted mean 373 ns, GLS fusion 226 ns"
  (ratio 1.65) reproduce almost exactly: independent full-C 4-anchor run
  gives 1.61–1.65.

**Mechanism note:** much of the advantage is heteroscedastic white noise,
not exotic correlation structure. The GLS weights for the 4-anchor full-C
config are [0.466, 0.277, 0.231, 0.026] — B1855+09 (700 ns white noise)
is nearly excluded, while the unweighted mean gives it 25%. Inverse-variance
down-weighting of the noisiest pulsar does most of the work; the
dipolar/quadrupolar terms add robustness on top.

## Honest limits

- Synthetic data with matched conditions (genie-aided covariance, Gaussian
  noise, static per-epoch estimation). This is NOT a revalidation of all 8
  PRTP rounds — no Kalman smoother, no red-noise time series, no cadence
  effects, no estimated-covariance degradation, no X-ray measurement model.
- GWB per-epoch RMS was parameterized directly; mapping the report's
  strain amplitude (2e−15 at f=1/yr) to per-epoch RMS needs the full
  red-noise spectral treatment, so the GWB sweep is representative, not
  exact.
- Single common-mode estimation task; the report's harder results (joint
  nav-clock separation, time transfer) are untouched by this verification.
- Verdicts use "reproduced / did not reproduce" — nothing here is
  "validated" in the flight sense.

## Bottom line

The spec's mathematics checks out from an independent implementation: the
HD curve has the claimed shape and quadrupolar character, the GLS weights
are the variance minimizer, and the headline "~2× over unweighted" claim
reproduces as 1.5–2.2× depending on regime — with the report's own 1.65
figure landing exactly. The "~2×" summary is slightly generous for
correlated-noise regimes; "1.5–2× depending on noise regime" would be the
tighter claim.
