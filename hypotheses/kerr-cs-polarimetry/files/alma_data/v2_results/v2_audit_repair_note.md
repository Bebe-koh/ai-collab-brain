# EVPA search v2: audit repair and re-calibration (2026-10-06)

## Headline

The independent audit of the v1 search script was correct on both major
findings, and I confirmed each one myself before repairing:

1. **Unwrapping bug — CONFIRMED and FIXED.** v1 called `np.unwrap` on a
   `(time, 4)` array without `axis=0`, unwrapping across spectral windows
   instead of along time. Demonstrated: SPW values `[-89, -88, 87, 88]`
   came out `[-89, -88, -93, -92]` — two bands silently shifted by -180°,
   corrupting the band average wherever inter-band EVPA differences
   crossed the ±90° boundary. v2 unwraps along time; a synthetic +20°
   step is recovered exactly in all bands.
2. **Circular-shift null artifact — CONFIRMED and FIXED.** v1 shifted the
   raw series including its slow baseline drift, joining drift
   end-to-beginning into a discontinuity the tanh template then
   "detected". On a drift-only synthetic with no event: v1-style null
   99th percentile = **253** (pure artifact); v2 residual-shift null
   99th = **2.8**. On the real data the v1 nulls (~40-46) were likewise
   inflated; v2 campaign nulls are 20-38 depending on EB.

All three EBs were rerun end-to-end with the repaired pipeline.

## Verdict after repair

- **No detections.** Every EB's strongest candidate sits below its own
  campaign-level null 99th percentile (X4947: 25.3 < 26.6; X448f:
  16.9 < 20.2; X4227: 35.7 < 37.5).
- **55.6° slips: excluded, now with a measured number.** Focused
  injection-recovery (100 trials per EB, 55.6° tanh at τ=46.9 s injected
  into the real per-SPW series, full pipeline incl. veto): **100/100
  detected in every EB** → P(detect) ≥ 0.971 (95% lower bound), per epoch,
  for resolved tanh ramps with τ in [10,120] s inside analyzed segments.
- **General sensitivity is weaker than v1 claimed, and now honest.**
  v1 quoted "~6-8° exclusion" from predicted S/N vs an inflated null.
  Measured 90%-detection amplitudes: X4947 19-29°, X448f 6-12°, X4227
  10-12° (varies with EB noise and τ). The v1 "~6-8°" and ">>99% from
  predicted S/N" claims are superseded.

## What else changed (the audit's smaller findings)

- **Unused `sig` argument** → removed; the fit is ordinary least squares
  with amplitude uncertainty from fit residuals, now documented as such.
- **Achromaticity computed but unenforced** → replaced by a real,
  calibrated veto (below). v1's per-candidate chi2 numbers were
  diagnostics only.
- **Pooled per-segment null maxima** → per-EB campaign null: one
  surrogate per segment, max |S/N| over grid × segments, 1000 campaigns.
  This matches the detection statistic (the EB's strongest candidate).
- **Sensitivity from median σ_A at one τ** → injection-recovery curves
  P(detect) vs amplitude at τ = 10/46.9/120 s, per EB.

## The veto: three designs, one survivor

This deserves detail because the first two designs failed on the real
data in instructive ways.

**Design 1 — common-amplitude χ² (abandoned).** Fit per-SPW amplitudes,
test consistency with a common value. Failed: real data have inter-SPW
correlated systematics, so the residual-based per-SPW errors are
misspecified. True 55.6° injections scored χ²/3 up to ~50-128 while some
single-SPW jumps scored < 5. No threshold separates them.

**Design 2 — per-SPW S/N coincidence (abandoned as sole veto).**
Require ≥3/4 SPWs to agree in sign with |S/N|>3. True-accept was 1.000,
but 8-20% of detected single-SPW jumps also passed. Root cause:
selection bias — the veto is evaluated at a (t0, τ) chosen by the
detection statistic on overlapping data, which inflates the other SPWs'
apparent S/N in the signal direction.

**Design 3 — coincidence + dilution-ratio (adopted).** A single-SPW
artifact of amplitude J appears diluted ~4× in the inverse-variance band
average, so max|A_spw|/|Ā| ≈ 4 for artifacts vs ≈ 1.0-1.2 for true
signals. The ratio uses amplitudes only, making it robust to the
selection bias above. Calibrated: true 55.6° injections give 1.0-1.8
(120 trials, 0 above 1.8); single-SPW jumps give median 3.6-8.6.
Veto PASSES iff coincidence holds AND max|A_spw|/|Ā| ≤ 2.0.
End-to-end: true-accept 1.000 at 55.6°; single-SPW-jump false-pass
0.00-0.015 (X4947/X448f: 0.00 at all tested jump sizes; X4227: ≤0.08
at 20°, 0.00 at 80°).

The Faraday λ² comparison is retained as a diagnostic only: with four
SPWs spanning 213-229 GHz the λ² lever arm (16%) is too small to
distinguish Faraday rotation from an achromatic signal, and requiring
the common model to beat Faraday was rejecting true injections.

## Single-sample jump scan (unresolved τ << 4 s)

The tanh grid covers resolved ramps (τ ≥ 10 s). A separate scan flags
the largest single-sample jump per segment with per-SPW steps:
- Nothing achromatic and large. The biggest features are
  single-or-dual-SPW dominated and negative-going in the band average
  only through dilution, e.g. X4947 seg4: band-avg -8.2° from per-SPW
  steps [-3.6, -75.5, -61.5, +4.3] — instrumental, correctly rejected
  by the veto (only 2/4 SPWs agree, wrong-sign SPW3).
- No candidate resembling an unresolved achromatic step was found.

## Files

- `evpa_transient_search_v2.py` — repaired implementation (selftest
  included: `python3 evpa_transient_search_v2.py --selftest`).
- `transient_search_v2_report.md` — full per-EB numbers.
- `~/workspace/your_files/repro-packages/alma_evpa_search_v2_repro.zip`
  — v2 script + v1 script (provenance) + 3 IQUV NPZs + both reports.
- `~/workspace/your_files/alma_csv/` — the three EBs as CSV
  (`mjd,I0..U3`) + META.txt, for the independent re-check.

## What this changes downstream

- The remaining 5 EBs (reduction still running) will be searched with
  v2, not v1. Per-EB campaign nulls stay separate; exclusion statements
  will use the least-sensitive EB.
- The observing-requirements memo's sensitivity floor should be updated
  from the v1 "~6°" figure to the measured A_90 range once all 8 EBs
  are in.
- Standing lesson (added to the repair record): surrogate nulls must be
  built from residuals, never from raw drifting series; and any veto
  statistic must be calibrated end-to-end on injections into the real
  data, because analytic error bars do not survive inter-band
  correlated systematics.

## Reproducibility re-run (2026-10-06)

Grok's audit caught a real defect in the committed code: `N_CAMP=500`
and `injection_recovery(trials=25)` while this note described 1000
campaigns and 100 trials, with no run log of the original invocation.
Fix: N_CAMP 500->1000, trials 25->100, X4227 added to the default file
list (values only; script md5 `eb55f47a98d3431dd0bc9a933a7575fb`).
Full re-run on all three EBs (fixed seeds; command in
`v2_results/RUN_LOG.md`): null95/null99, observed campaign maxima, and
100/100 detection fractions at 55.6 deg / tau=46.9 s reproduce exactly;
A90/A99 moved 1-4 deg (MC noise from 25->100 trials), all inside the
published ranges. Headline claims confirmed. Comparison table and
diagnostics in `v2_results/rerun_reconciliation_2026-10-06.md`.
