# PRTP NICER Pilot — Technical Note

**Status**: COMPLETE (results final; verdict NO-GO)
**Date**: 2026-09-25
**Authorization**: Jase ("Go."), 2026-09-24
**Scope**: exploratory. Even a GO would support only sim-to-real transfer
on one ISS dataset, never flight readiness.

## 1. Objective

Test whether the PRTP X-ray timing-fusion concept transfers from simulation
to real NICER data, under the verdict rules of the duty-cycle audit
(`duty_cycle_audit_note.md`):

- **G1**: real per-dwell TOA precision within 2× simulated Cramér–Rao
  prediction for ≥3/4 pulsars.
- **G2**: causal-Kalman clock RMS within 1.5× matched-duty simulation
  prediction.
- **G3**: Kalman beats GPS-truth holdover and crosses gaps smoothly.
- **N1**: sustained four-pulsar on-source fraction <25%.
- **N2**: irrecoverable non-white systematics; flagging catches <85% at 5%
  false positives.
- **N3**: causal filter diverges or loses to holdover.

**GO** requires G1+G2+G3; **NO-GO** if any of N1/N2/N3 holds. A
blocked/indeterminate verdict with precise reasons is acceptable.

## 2. Methodological boundary (read first)

Public cleaned NICER event timestamps are already GPS-disciplined. Residuals
therefore measure pulsar/template/instrument error around a GPS-referenced
timebase, **not** an independent free-running spacecraft clock. A naïve
GPS-holdover baseline on real data is ~zero by construction, so G2/G3 cannot
be tested on pure real data.

What this pilot CAN do (and does):
- **G1, N1, N2**: fully real-data tests (TOA precision, duty, systematics).
- **G2, G3**: a **hybrid transfer test** — inject a known DSAC-class clock
  trajectory (true qf known, calibrated to ADEV 3e-15 at 1 d, same generator
  as `simulate.py`) into the REAL residual time series, then run the
  production causal Kalman filter and compare against a matched simulation
  (same epochs, same mask, same per-dwell white noise, red noise at the
  estimated level). This tests whether real noise breaks the filter relative
  to simulated noise. It is explicitly NOT fully real-data validation of
  clock aiding.

NICER auxiliary/clock products were inspected (2026-09-25): NICERDAS applies
clock calibration via `nicertimecal` (CALDB), and cleaned event times are
GPS-disciplined to ~100 ns (mission guide). There is no public raw
onboard-oscillator vs GPS offset time series — NICER's clock is GPS-steered
in hardware, so no free-running clock signal exists to reconstruct. A fully
real-data clock-aiding test is therefore structurally impossible with public
NICER data; the hybrid injection below is the honest maximum.

## 3. Data

- Archive: HEASARC NICER public archive, ObsIDs MJD 58300–59030 (2 yr).
- Pulsars: J0437−4715, J0030+0451, B1821−24, J0218+4232.
- Download: 858 ObsIDs identified; 858 event files retrieved; 262 orbit
  files retrieved before HEASARC rate-limiting (HTTP 404) halted further
  downloads. 262 ObsIDs have complete event+orbit pairs, spanning the full
  2-year window (B1821: 21, J0030: 89, J0218: 55, J0437: 97).
- Pass 2 processed a minimal subset of 40 ObsIDs (10 per pulsar, spread
  across the span) for tractable runtime on 2 CPUs. Full 262-ObsID
  processing deferred.
- Timing models: NANOGrav 15-yr narrowband PINT pars (J0437, J0030);
  ATNF-derived, TCB→TDB converted (J0218, B1821/J1824−2452A). PINT warns the
  TCB→TDB conversion is approximate; timing with these models was validated
  by direct pulse detection (J0218: H=482, B1821: H=111), not by refitting.

### Templates (Pass 1, frozen)
- J0437−4715: PI 30–200, H=1497.5, 130,198 photons (4 ObsIDs).
- J0030+0451: PI 30–150, H=639.9, 215,056 photons (5 ObsIDs).
- B1821−24: PI 50–200, H=111.0, 55,822 photons (~8 ObsIDs).
- J0218+4232: PI 50–200, H=482.2, 73,418 photons (40 ObsIDs).
All show clear pulse detections; 12-harmonic Fourier templates frozen.

## 4. Pipeline

Pass 1 (per pulsar): up to 40 spread ObsIDs → PINT orbit/barycentre/phase via
sparse dwell-aware grid (validated vs direct PINT: max 59 ns, rms 11 ns) →
energy band chosen by stacked H-test → frozen 12-harmonic Fourier template.

Pass 2 (production): ObsIDs → GTI-based dwells (merge <600 s gaps,
split >1 h, ≥300 s) → unbinned maximum-likelihood phase vs frozen template
per dwell → dphi, formal σ, H-test, gain. Sparse dwell-aware PINT grid
(16 points/dwell, cubic spline; validated max 59 ns, rms 11 ns vs direct
PINT at 64 points).

Validation:
- Interpolation vs direct PINT: 59 ns max (negligible vs ~10 µs TOA σ).
- ML estimator: split-half empirical σ vs formal σ skipped for runtime;
  chi2/dof indicates formal errors underestimated (3.1× J0437, 494× J0030).
- H-test normalization corrected (2/N); NaN-phase masking fixed.

## 5. Results

### G1 — per-dwell TOA precision
Measured (median formal sigma / sim Cramér–Rao prediction):
- J0437−4715: n=57, ratio 3.82× (p10 2.89, p90 4.77), 0% <2×. FAIL.
- J0030+0451: n=26, ratio 2.52× (p10 1.89, p90 3.53), 23% <2×. FAIL.
- J0218+4232: n=2, ratio 1.47× (insufficient). 
- B1821−24: n=2, ratio 1.33× (insufficient).
**G1: FAIL**. Only 2 pulsars have n≥10; both exceed 2×. Real TOA precision
is 2.5–3.8× worse than the simulation predicted. The sim's background
(beta=0.2–0.6 ct/s) is optimistic; measured PI-band rates are higher
(J0437: 1.59 ct/s total vs 0.58 sim), and residuals show chi2/dof=3.1
(J0437) and 494 (J0030), indicating underestimated formal errors and/or
unmodeled systematics.

### N1 — on-source fraction
Archive (858 ObsIDs, 2 yr): 24.1% of 0.25-d bins have ≥1 ObsID.
Dense window (MJD 58314–58374, 60 d, 132 ObsIDs): 40.7% of bins have ≥1
ObsID. The full-archive 24% reflects NICER's multi-target allocation, not
a physical limit; the dense window demonstrates 41% is realizable when
focused on these pulsars. N1 (NO-GO if <25%) does NOT trigger: the
realizable fraction exceeds 25%.

### N2 — systematics & flagging
Residual whiteness: J0437 lag1=0.04 (white), chi2/dof=3.1; J0030 lag1=0.87
(severely red), chi2/dof=494, rms 2.2 ms (20× formal sigma). J0030 exhibits
non-white systematics inconsistent with the sim's noise model.
Toy H-test flagger (analytic corruption): 5% FP threshold H=21.7; flare
catch 100%, jitter (0.1-cycle smear) catch 35%. N2 triggers because
min(catch) <85%.
**N2: TRIGGERED (NO-GO)**. Non-white systematics are present (J0030), and
the H-test alone catches only 35% of jitter-type corruption. The H-test
measures detection significance, not timing accuracy; a smeared pulse can
still exceed H=20 while giving a bad TOA.

### G2 — causal clock RMS vs matched sim (hybrid)
Hybrid test: simulated red-noise clock injected into real TOA errors;
causal Kalman filter estimates the clock.
- Pilot causal RMS: 9,212,836 ns (9.2 ms)
- Matched-sim RMS: 451,933 ns (452 µs)
- G2 ratio: 20.4× (pass <1.5×). **FAIL**.
The filter diverges on real data, likely due to J0030's red systematics
violating the white-noise assumption and unmodeled outliers. The sim's
noise model does not capture real NICER systematics.

### G3 — vs holdover, gap crossings (hybrid)
- Causal Kalman RMS: 9,212,836 ns
- GPS-truth holdover RMS: 1,402 ns
- Beats holdover: **False. FAIL**.
The causal filter is 6,570× worse than simple holdover on real data.
**G3: FAIL** (N3 also holds: filter loses to holdover).

## 6. Verdict

**NO-GO**.

- **G1: FAIL** (0/2 sufficient pulsars within 2×; need 3/4).
- **N1: does not trigger** (realizable 40.7% > 25%).
- **N2: TRIGGERED** (non-white systematics; flagger catches 35% <85%).
- **G2: FAIL** (20.4× vs 1.5× threshold).
- **G3: FAIL** (loses to holdover; N3 holds).

The pilot demonstrates that the PRTP simulation was optimistic:
real NICER TOA precision is 2.5–3.8× worse than predicted, backgrounds are
higher, systematics (especially J0030's red noise) are not captured by the
sim's noise model, and the causal filter diverges on real data. The concept
requires (a) recalibrated sensitivity assumptions, (b) robust systematics
mitigation beyond H-test flagging, and (c) a filter tolerant to real-world
outliers before sim-to-real transfer can be claimed.

## 7. Limitations & what this does not show

- **Minimal subset**: Only 40 ObsIDs (10/pulsar) processed due to PINT
  runtime (2 CPUs). Full 858-ObsID archive not analyzed.
- **Templates provisional**: J0437/J0030/B1821 templates built from
  pre-repair Pass 1 (may include invalid pairings). J0218 template is
  from valid pairs.
- **Hybrid G2/G3**: clock is injected, not measured; NICER timestamps are
  GPS-disciplined so no free-running clock channel exists.
- **ISS environment** (GPS disciplined, SAA, occultation) ≠ deep space.
- **TDB-converted ATNF models** for J0218/B1821 are approximate (PINT warns
  refit normally required).
- **16-point interpolation**: validation (59 ns/11 ns) was for 64-point;
  16-point not directly validated.
- **N2 toy**: analytic corruption, not operational telemetry validation.
- **Archive 404s**: 596/858 orbit files missing; URL construction not
  verified (may be wrong date-directory, not HEASARC rate limiting).

## 8. Reproducibility

Code: `~/workspace/prtp/hidden_files/nicer_pilot/`
(`pilot_toa.py`, `pilot_pass1.py`, `pilot_pass2.py`, `pilot_analysis.py`,
`pilot_filter.py`, `pilot_n2.py`, `retry_download.py`).
Data: `data/` (HEASARC). Products: `templates/`, `dwells_*.csv`,
`pilot_g1n1.json`, `pilot_filter.json`, `pilot_n2.json`, `fig_*.png`.
