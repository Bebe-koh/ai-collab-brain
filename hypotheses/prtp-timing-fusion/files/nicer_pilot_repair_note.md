# PRTP NICER pilot — repair note (2026-09-25)

Pilot verdict was **NO-GO** (G1 fail 2.5–3.8x, G2 20.4x, G3 6570x, N2 triggered).
This note records the repair attempt: what was changed, what the ablation
shows, and the honest re-evaluation of every criterion. Nothing here is
flight readiness — at best this is sim-to-real transfer on one ISS dataset.

## 1. Root-cause diagnosis (confirmed by ablation)

The pilot trusted the per-dwell **formal** phase uncertainties. They are
wrong in the same way the binned NANOGrav product's were: chi2/dof 3.0
(J0437) and 475 (J0030). For J0030 the filter's `qred` fell back to the
1e-20 floor on the sparse regridded grid, so the filter believed J0030
dwells ~475x more than it should have, and J0030's per-ObsID coherent
offsets (2246 us rms, within-ObsID lag-1 0.85) leaked straight into the
clock state -> 9.2 ms divergence.

Ablation at 1x DSAC (hybrid: seed-777 injected clock + real residuals):

| arm | change vs pilot | causal RMS |
|---|---|---|
| pilot (audited code, formal R) | — | 9.21 ms (reproduces pilot) |
| v2plain | R1: empirical white R + v2 qred only | 1.53 ms |
| v2bias | + R2: per-(pulsar,ObsID) bias states | 1.04 ms |
| v2full | + R3: innovation gating (chi2>25) | 1.04 ms, 0 rejected |

R1 (noise recalibration) is the dominant fix: 6x. R2 (bias states) gives
another 1.5x by absorbing the coherent per-ObsID systematics instead of
letting the clock state eat them. R3 fired on nothing — the recalibrated
model now explains the data, so gating is defense-in-depth, not load-bearing.
Gate sensitivity at 1x: gate 9 -> 1 rejection, 0.91 ms; gate 25/100 ->
0 rejections, 1.04 ms. Primary result uses the pre-registered gate 25 (~5σ).

## 2. Noise model v2 (empirical, dwell level)

| pulsar | dwells | white rms (within-ObsID diffs) | ObsID-offset rms | qred (de-offseted) |
|---|---|---|---|---|
| J0437-4715 | 57 (10 ObsIDs) | 241 us | 84 us | 1e-24 (floor: no red beyond white) |
| J0030+0451 | 26 (8 ObsIDs) | 850 us | 2246 us | 1e-24 (floor) |

White from within-ObsID diffs (same ObsID => same offset cancels); offsets
from per-ObsID weighted means; qred from white-subtracted first differences
on de-offseted dwell times. After de-offseting, neither pulsar shows
detectable red noise at these cadences — J0030's "redness" is block
offsets, J0437's is white.

## 3. G2 re-evaluation: PASS (1.16 < 1.5)

Matched sims use the v2 model (red RW at v2 qred + per-ObsID offsets
N(0, off_var) + white at binned empirical R), same grid/mask/bins:

| clock | hybrid v2full | sim mean ± std | G2 | holdover | G3 |
|---|---|---|---|---|---|
| 1x DSAC | 1.04 ms | 0.90 ± 0.31 ms | **1.16 PASS** | 1.4 us | fail (0.001x) |
| 10x | 1.05 ms | 0.90 ± 0.31 ms | 1.16 PASS | 14 us | fail (0.01x) |
| 100x | 1.07 ms | 0.91 ± 0.30 ms | 1.18 PASS | 140 us | fail (0.13x) |
| 300x | 1.13 ms | 0.92 ± 0.29 ms | 1.22 PASS | 420 us | fail (0.37x) |
| 600x | 1.23 ms | 0.96 ± 0.27 ms | 1.28 PASS | 840 us | fail (0.68x) |
| 1000x | 1.38 ms | 1.02 ± 0.25 ms | 1.35 PASS | 1.40 ms | **pass (1.01x)** |

G2 passes at every clock level: the repaired filter behaves on real data
as the v2 model predicts (ratio 1.16–1.35, inside the sim spread). The
original 20.4x failure is repaired.

## 4. G3 and the worth-flying boundary

G3 (beat holdover at 1x DSAC) still fails: 1.04 ms vs 1.4 us. This is now
understood structurally, not as a filter bug: the filter error is
measurement-noise dominated (~1.0–1.4 ms, nearly flat vs clock quality)
because the TOAs are 240–850 us white plus ms block offsets on a sparse
~46-bin grid, while a DSAC-class clock wanders only ~1.4 us over the span.
The worth-flying boundary is at **~950–1000x DSAC** (ADEV ~3e-12 at 1 d):
only for clocks ~3 orders of magnitude worse than DSAC does pulsar aiding
beat holdover on this dataset. For a DSAC-class or better clock, the honest
answer is: fly the clock, leave the pulsars out of the loop.

## 5. Criterion re-evaluation (honest)

- **G1: still FAIL, unchanged.** 3.82x (J0437) / 2.52x (J0030) vs the
  pre-pilot simulation's CR prediction, 2 pulsars < 3 needed. Recalibration
  does not retroactively pass G1 — that would be moving the goalposts.
  What the repair adds: the v2 model explains the data (chi2/dof ~ 1 by
  construction on the calibration, and the filter's G2 pass is the
  independent check that the model predicts real filter behavior).
- **N1: still does not trigger** (40.7% dense-window occupancy > 25%).
- **N2: still TRIGGERS, but narrower.** The descriptive half stands (J0030
  lag-1 0.87, chi2/dof 494 in raw dwells). The flagging half improved:
  photon-level jitter catch 35% -> 73% (see §6), but 73% < 85%, so the
  clause as written still triggers. Separately, the "irrecoverable"
  premise is undermined for the filter path: the systematics are now
  modeled (bias states) with G2 passing — recovered-through, not fatal.
  But the criterion is the criterion: N2 triggers.
- **G2: PASS** (1.16 < 1.5 at 1x; 1.16–1.35 across the sweep).
- **G3: FAIL at 1x DSAC** (0.001x); passes only at ~1000x DSAC.

**Overall: still NO-GO as a flight concept** (G1 failed, G3 failed at any
plausible clock, N2 still triggers on the 85% flagging-catch clause).
But the NO-GO is now a *sensitivity* NO-GO with a mapped boundary, not a
*filter-divergence* NO-GO. The repair converted an uncontrolled failure
into a quantified one: we know exactly where pulsar aiding helps (clocks
worse than ~1e-12 @ 1d on this cadence) and that the filter transfers
sim-to-real at 1.16x on this dataset.

## 6. Flagging v2 (beyond the H-test)

Two additions, because the H-test measures detection significance, not
timing accuracy, and sees nothing coherent across dwells:

- **F1 (per-dwell accuracy features, photon-level):** split-half phase
  disagreement (even/odd photons, ML phase each vs frozen template),
  template gain, formal sigma, plus H. Validated by corrupting REAL
  J0437 photon phases (15 dwells, PINT re-extraction): flare = +30%
  uniform-phase photons; jitter = 0.10-cycle Gaussian smear (same
  magnitude as the pilot's toy); all features recomputed through the
  same pipeline. Thresholds calibrated on the photon-level clean sample
  (each marginal at its most extreme clean value -> empirical FP 0/15,
  95% CI [0, 0.20]).
- **F2 (per-ObsID offset flag):** |ObsID weighted mean| / se under the v2
  white model, threshold 4σ.

Results (Wilson 95% CIs, n=15):

| corruption | H-only | gain-only | split-half-only | combined |
|---|---|---|---|---|
| flare (+30% uniform) | 0.47 | 0.40 | 0.07 | **0.60** [0.36, 0.80] |
| jitter (0.10 cyc; pilot magnitude) | 0.73 | 0.53 | 0.00 | **0.73** [0.48, 0.89] |

Pilot baseline (analytic toy, H-only): 35% jitter catch at 5% FP.
Flagger v2 roughly doubles it on the matched-magnitude jitter test
(35% -> 73%), with the gain feature contributing on flares. Neither
reaches the 85% N2 bar at n=15 resolution. (Note: the pilot's flare
test used +100% uniform photons, a stronger corruption than our +30%.)

Three diagnostic findings along the way:
1. The split-half statistic is miscalibrated on clean data (median 1.75
   vs 0.67 expected for |N(0,1)|): per-dwell formal errors are ~2.6x
   underestimated even at the split-half level — the same
   formal-error-distrust theme as the white-noise bug. Because of this,
   the split-half threshold had to be set very high and the feature
   contributes little at these corruption magnitudes; H and gain do the
   work. The accuracy-feature idea is sound, but it needs recalibrated
   per-dwell errors to bite.
2. The formal-sigma-inflation feature adds nothing (0.00 catch): the ML
   formal sigma does not inflate under these corruptions.
3. F2 on real J0030: 7/8 ObsIDs, 23/26 dwells (88%) exceed 4σ under the
   white model — the block offsets are not a few bad dwells, they are
   the dominant structure. Dropping them would delete the pulsar; the
   repaired filter models them instead (bias states, §1).

## 7. Limitations (carried over / remaining)

- Hybrid, not real: the clock is injected (DSAC-class, seed 777); NICER
  timestamps are GPS-disciplined, so no free-running-clock truth exists.
  "Sim-to-real" here = real TOA noise + synthetic clock, never fully
  real clock data.
- Filter is given the true clock qf (oracle, same as pilot).
- Per-ObsID offsets modeled Gaussian; 8–10 ObsIDs cannot test that shape.
- qred hit the 1e-24 floor for both pulsars: no detectable red beyond
  white/offsets at this cadence — the red states are nearly inert.
- Only 2 pulsars with adequate data; J0218/B1821 contribute nothing.
- Sim spread is large (std ~0.3 ms on 0.9 ms mean): G2's pass has
  wide error bars, honestly reported.

## 8. Products

- `repair_filter.py` — v2 noise model, bias-state+gating Kalman, ablation,
  hybrid injection, matched sims, clock sweep (audited reuse of
  `pilot_filter.gen_clock` / `kalman_masked_tv`).
- `repair_filter.json` — all numbers above.
- `fig_repair_clock.png`, `fig_repair_clockerr.png`.
- `repair_flagging.py`, `repair_flagging.json` (first-pass thresholds),
  `repair_flagging_v2.json` (recalibrated thresholds — the reported
  numbers), `recalibrate_flagging.py` — flagger v2 + photon-level
  corruption validation (PINT venv).
- Gate sensitivity: 9/25/100 at 1x (0.91/1.04/1.04 ms).
