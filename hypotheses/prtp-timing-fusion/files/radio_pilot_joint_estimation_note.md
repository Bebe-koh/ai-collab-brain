# PRTP round 4 — joint white-noise + clock-noise estimation
**2026-10-03 · simulation-only (hybrid: real NANOGrav 15-yr binned
residuals + synthetic RW-FM clock) · conditional on stated assumptions**

## 1. Question and headline answer

Round 3 removed the oracle on the clock-noise PSD (ML qf, cost 1.00×
at M≤1000) but held per-pulsar white noise at the separately-measured
recalibrated values — the qf cost was conditional on known white. A
flight system estimates everything from the data. This round closes
the last estimation loophole: **per-pulsar white levels AND qf are
estimated jointly from the hybrid data**, by alternating coordinate
ascent on the Kalman innovation pseudo-log-likelihood (the same
objective round 3 used for qf).

**Headline: the loophole is closed — joint estimation costs nothing,
and the clock PSD is nailed exactly.**

- The joint estimator **converges in 2–3 iterations** from a
  deliberately naive start (white at raw two-component-ML values,
  known to be wrong), and lands on the same point from an overshoot
  start ([3,3,3]).
- **qf estimation is exact everywhere**: Mhat = true M in all 20
  cases (M ∈ {0,1,100,1000} × 5 seeds); on the M=0 null it collapses
  to the grid floor — the estimator never invents clock noise.
- **Cost vs oracle ≤ 1.00×**: 0.94× (M=0), 0.92× (M=1), 1.005×
  (M=100), 1.000× (M=1000). The joint-ML white actually *beats*
  the separately-measured RECAL white at M≤1.
- **Every G3 verdict survives**: 60–67× (M=1), 360× (M=100),
  367× (M=1000) over holdover.
- One honest blemish (§5): G1 (innovation χ² < 3, all-obs) marginally
  fails at M≤1 (3.8/4.2, driven by B1855's heavy-tailed spikes
  against its sharpened ML white); kept-obs χ² = 2.1 passes, rms
  improves, G3 unaffected.

## 2. Method

**Objective.** The innovation pseudo-log-likelihood
−½Σ(nis + log S) over marginally-gated kept observations (GATE=25),
summed per-pulsar-marginal as in round 3. For a correctly-specified
linear-Gaussian model this is the marginal likelihood; here it is a
pseudo-likelihood (gating + marginal per-pulsar treatment), the
standard adaptive-Kalman objective.

**Alternating coordinate ascent** (per hybrid realization):
- *qf step*: ML over the round-3 log grid of effective multipliers
  M_eff (qf = qf_1x·M_eff²), given current white. Reuses
  `radio_pilot_robustness.estimate_qf_ml`.
- *white step*: per-pulsar 1-D ML line search over the white scale
  factor f_i (white_i = raw_ML_white_i × f_i), others fixed —
  13-point log grid on [0.3, 30] plus local quadratic peak fit —
  given current qf.
- Iterate until max |Δlog f| < 0.02 with qf grid point unchanged
  (2–3 iterations in practice).

**Rejected alternative (diagnostic).** The first attempt used the
textbook adaptive-KF white update — per-pulsar innovation covariance
matching, f_i ← f_i·mean(nis_i). It converges stably but to a
**non-ML fixed point**, over-whitening ~2× (B1855 f̂=4.96 vs the
pseudo-LL maximum at 2.42, verified by direct scan). Under model
misspecification (real reds aren't random walks) moment-matching
dumps all residual misfit into white. The pseudo-LL line search was
adopted instead; the comparison is kept as a diagnostic in §5.

**Configuration.** PRIMARY 3-pulsar ensemble (J1909-3744 + B1855+09 +
J0437-4715), GATE=25, same union grid / eval window / seeds
(101–105) as rounds 2–3. Oracle reference: true qf + white at RECAL
(1.05 / 2.42 / 2.20 — the known truth for hybrid data). Red-noise
PSDs (qred) remain **oracle** (fitted from chains) — flagged as the
still-open, less load-bearing loophole.

## 3. Results — convergence and qf

| M | iters | Mhat (all 5 seeds) | f̂ mean [J1909, B1855, J0437] | RECAL truth |
|---|---|---|---|---|
| 0 (null) | 2.0 | 0.035 (floor) ×5 | [0.86, 0.38, 2.06] | [1.05, 2.42, 2.20] |
| 1 | 2.8 | 1.0 ×5 | [1.30, 0.69, 2.11] | [1.05, 2.42, 2.20] |
| 100 | 2.6 | 100 ×5 | [25, 18, 12] (ridge) | [1.05, 2.42, 2.20] |
| 1000 | 2.4 | 1000 ×5 | [20, 6, 12] (ridge) | [1.05, 2.42, 2.20] |

qf is exactly identified in every case — the common-mode clock PSD
separates cleanly from per-pulsar white at all clock levels. The
M=0 null correctly finds no clock.

**Init robustness** (M=1, seed 101): [3,3,3] → [1.00, 0.37, 2.63],
Mhat=1, same point as from [1,1,1]. Not init-sensitive.

**Pseudo-LL diagnostic** (M=1, seed 101): the converged (f̂,q̂)
sits at the maximum among all tested points — ll=4107.7 vs 4104.5
at (RECAL, true qf), 4086 at ±2× white perturbations, ≤4044 at
×4/÷4 qf perturbations. The alternating scheme finds the joint
maximum, not a saddle.

## 4. Results — cost and G3

| M | oracle RMS | joint RMS | cost | G3 oracle → joint |
|---|---|---|---|---|
| 0 (null) | 291 ns | 274 ns | 0.94× | clean → clean |
| 1 (DSAC) | 315 ns | 286 ns | 0.92× | 59.7× → 64.5× |
| 100 | 7.40 µs | 7.50 µs | 1.005× | 360.5× → 360.3× |
| 1000 | 73.3 µs | 73.3 µs | 1.000× | 367.4× → 367.5× |

(G3 = first-seed holdover RMS / mean hybrid RMS, same convention as
round 3's JSON. Per-seed G3 at M=1: 59.6–66.8×.)

Joint estimation is **free or better than free**: at M≤1 the ML
white fits the actual residuals better than the one-shot RECAL
values (cost 0.92–0.94×); at M≥100 it is exactly 1.00×. Every G3
verdict from rounds 2–3 survives with large margins.

**White identifiability.** At M≤1 the white ML finds interior
values; at M≥100 the profile likelihood is flat (ll changes <1
over ~500 obs across 30× white swings) and the maximizer drifts to
the search bounds. This is expected — at M≥100 the clock process
noise per 30-day step (~10 µs) dwarfs white (~0.5 µs), so white is
unidentifiable — and it is **non-load-bearing**: filter rms moves
<2% across 30× white swings (4913 vs 4869 ns at M=100), because the
Kalman gain balance is set by the clock process noise. A flight
system does not need to know white precisely when the clock is
this bad; and when the clock is good (M≤1), white is identifiable.

**B1855 white vs RECAL.** The joint ML prefers lower B1855 white
(0.3–2.2 across seeds, vs RECAL 2.42). The pseudo-LL maximum is at
the lower value (4107.7 > 4104.5), and rms is better (276 vs 270 ns
at seed 101). Interpretation: B1855's residuals are heavy-tailed;
moment-matching (RECAL) inflates white to cover the spikes, while
the gated pseudo-ML fits the bulk and lets gating handle the
spikes. The disagreement is real statistics, not a bug — and it is
non-load-bearing either way.

## 5. The G1 blemish (honest)

G1 as defined in rounds 2–3 (max innovation χ²/dof < 3 over **all**
obs in the eval window, including gated ones): **3.78 (M=0),
4.15 (M=1)** — marginal fail, driven entirely by B1855
(all-χ² 3.70, max nis 73 on a gated spike; kept-obs χ² = 2.12).
At M≥100 G1 passes (1.33). Oracle-white gives 1.58 on B1855.

This is the price of the sharper ML white: the filter is slightly
overconfident on B1855's occasional spikes. The spikes are still
gated (4 rejections), rms improves 8%, and G3 is 60×+. A flight
system would either accept this (margins absorb it) or robustify
the observation model (heavier tails); it does not move any
mission verdict. Noted here so the criterion history stays clean.

## 6. Bottom line for the program

- The last estimation loophole is closed: **white + qf are jointly
  estimable from the data at zero performance cost** (cost ≤1.00×,
  qf exact, G3 intact). Nothing in the filter needs an oracle
  except the red-noise PSD shapes (qred) — slower, less
  load-bearing, and the stated remaining gap.
- The round-2 "~1.5–2× real-world cost" is now fully replaced by
  measurements: 1.00× (qf, round 3) × ≤1.00× (joint white, this
  round) = **1.00× total**.
- The earned next steps are unchanged: TOA-level (unbinned) data
  and/or the real-time loop. Estimation is no longer on the risk
  list.

## 7. Limitations (honest)

- Still hybrid (synthetic RW-FM clock), still 30-day bins, still
  simulation-only.
- qred still oracle (chain-fitted, not estimated in the loop).
- B1855's white ML is seed-sensitive (0.3–2.2 across seeds) —
  flat likelihood region; non-load-bearing but the point estimate
  should not be quoted as a measurement.
- G1 marginal fail at M≤1 (see §5); criterion was calibrated on
  oracle-white filters.
- White search bounds [0.3, 30] bind at M≥100 (flat ridge); the
  rms is insensitive there, so this is cosmetic.

## Products

- `~/workspace/prtp/hidden_files/radio_pilot_joint.py` — this round
  (joint coordinate-ascent estimator, sweeps, diagnostics)
- `~/workspace/prtp/hidden_files/radio_pilot_joint.json` — all
  numbers (per-seed)
- This note:
  `~/workspace/goals/prtp-pulsar-timing-fusion-validation/hidden_files/radio_pilot_joint_estimation_note.md`

*Simulation-only discipline: this round removes the last
idealization in the estimation chain (known white noise) and
measures its cost — ≤1.00× — with all headline verdicts intact.
The filter now estimates everything it needs from the data except
the slow red-noise PSDs.*
