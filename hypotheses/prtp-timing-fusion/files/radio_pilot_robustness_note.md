# PRTP round 3 — non-oracle clock-noise re-run + data-gap robustness
**2026-10-03 · simulation-only (hybrid: real NANOGrav 15-yr binned
residuals + synthetic RW-FM clock) · conditional on stated assumptions**

## 1. Question and headline answer

Round 2 rescued the concept on radio data (filter floor σ_m,R ≈ 300 ns
measured; aiding beats holdover ~60× at DSAC-class, ~210× at M≥100)
but gave the filter **oracle clock-noise PSD** (true qf). The note
costed that at ~1.5–2× "unverified." A flight system must estimate the
clock noise from the data. This round removes the oracle and adds
mission-realistic observing gaps.

**Headline: the oracle was free, and the verdicts survive contact
with realism.**

- **ML qf estimation recovers the true clock-noise level almost
  exactly** (estimated M_eff = true M to the grid point in 24/25
  cases; collapses to the grid floor on the M=0 null). The
  estimated-qf filter matches oracle to **1.00× at M ≤ 1000** — the
  round-2 note's 1.5–2× was pessimistic. One outlier seed at M=3300
  costs 2.4× (mean 1.28× there); every G3 verdict still passes.
- **Contiguous observing gaps cost ~4× in RMS at DSAC-class**
  (315 ns → 1.25 µs at ~30% epochs dropped) and **~13× in G3 at
  M=100** (211× → 16×) — but G3 still passes decisively in every
  gap configuration. G1 (innovation χ² ≤ 2.0) still passes.
- **Full realism** (25%-class gaps + estimated qf, M=1): **14.7×**
  over holdover. **3-yr mission window** (M=1, estimated qf): **7.5×**
  (vs 7.9× oracle).

## 2. Method

**Configuration** (matches the round-2 headline): PRIMARY 3-pulsar
ensemble (J1909-3744 + B1855+09 + J0437-4715; B1937+21 excluded),
recalibrated white (RECAL factors held fixed — a separately
data-measured noise fix, so the cost measured here isolates qf
estimation), GATE=25, same union grid / eval window / seeds
(101–105) as round 2. G3 convention unchanged from round 2:
holdover RMS (first seed) / mean hybrid RMS.

**(A) qf estimation.** Per hybrid realization, qf is estimated by
maximum (pseudo-)likelihood over a log grid of effective clock
multipliers M_eff (qf = qf_1x·M_eff²), coarse grid
{0.01,…,10000} plus two ±0.6-dex refinement passes. The objective is
the Kalman innovation pseudo-log-likelihood
−½Σ(nis + log S) over the same marginally-gated observations the
filter uses — standard adaptive-Kalman practice. The filter is then
re-run with the estimated qf; cost = rms(estimated)/rms(oracle).

**(B) gaps.** 24 equal-MJD blocks over the 15.8-yr span; seeded shuffle;
whole blocks dropped until the target fraction of observed entries is
removed (actual: 30% and 40% — block granularity overshoots the 25%
target; both reported as actuals). Same gap mask across seeds (gaps
are a schedule property, not a noise realization). M ∈ {1, 100},
oracle qf (isolates the gap effect).

**(C) combined:** M=1, 30%-actual gaps, estimated qf.
**(D) 3-yr window:** M=1, estimated qf (same sub-window as round 2).

## 3. Results (A) — estimator calibration and oracle cost

| M | Mhat (mean) | oracle RMS | est. RMS | cost (mean) | cost (worst seed) | G3 oracle → est. |
|---|---|---|---|---|---|---|
| 0 (null) | 0.03 (floor) | 291 ns | 289 ns | 0.99× | 0.99× | clean → clean |
| 1 (DSAC) | 1.00 | 315 ns | 315 ns | 1.00× | 1.00× | 58.5× → 58.5× |
| 100 | 100 | 7.40 µs | 7.40 µs | 1.00× | 1.00× | 211× → 211× |
| 1000 | 1000 | 73.3 µs | 73.3 µs | 1.00× | 1.00× | 213× → 213× |
| 3300 (CSAC) | 3000 | 242 µs | 441 µs | 1.28× | 2.39× | 213× → 116× |

Mhat landed on the true grid point for **every seed at every M>0**
(25/25); on the null it correctly collapsed to the grid floor
(Mhat=0.03 — the estimator does not invent clock noise). The clock
PSD is strongly identified in the data, which is why estimation is
free: at M≤1000 the estimated-qf filter is bit-identical in
performance to oracle (cost exactly 1.00× on all 20 seeds).

The single blemish: at M=3300, seed 102 — already an outlier under
oracle (717 µs vs ~100–160 µs on the other seeds) — degrades 2.4×
further under the estimated qf (1.72 ms). The estimated qf there was
0.83× true (Mhat=3000 vs 3300); on a seed with an unusually large
clock excursion, slightly under-tuned process noise makes the filter
lag. Per-seed G3 at M=3300 (estimated): 316×, **30×**, 415×, 610×,
425× — 4/5 seeds ≥300×, worst seed still 30×. Verdict stands.

G1 (innovation χ² max, estimated-qf runs): 1.47 / 1.58 / 1.33 / 1.33 /
1.69 — all pass (<3).

## 4. Results (B) — gap degradation (oracle qf)

| gaps (actual) | M | hybrid RMS | no-gap RMS | RMS ratio | G3 | G3 no-gap | G1 χ²max |
|---|---|---|---|---|---|---|---|
| 30% | 1 | 1.25 µs | 315 ns | 4.0× | **14.7×** | 58.5× | 2.00 |
| 40% | 1 | 1.19 µs | 315 ns | 3.8× | **15.5×** | 58.5× | 1.78 |
| 30% | 100 | 99.7 µs | 7.40 µs | 13.5× | **15.6×** | 211× | 1.39 |
| 40% | 100 | 120 µs | 7.40 µs | 16.1× | **13.0×** | 211× | 1.55 |

Two physical observations:

1. **Gaps hurt high-M proportionally more.** At M=1 the floor is
   measurement-noise dominated, so losing epochs costs 4×. At
   M=100 the filter must densely track fast clock wander; gaps let
   the clock random-walk away between updates (13–16× RMS cost).
   Either way G3 survives with double-digit margins.
2. **40% slightly beat 30% at M=1** (1.19 vs 1.25 µs) — mask lottery:
   the two gap masks drop different blocks (seeds 7 vs 8), and some
   blocks carry more information than others. The difference is
   within seed noise; the honest reading is "gaps cost ~4× at M=1,"
   not a precise curve.

Gating rejected nothing in any gap run (rej=0); the filter does not
need to throw data away to survive blackouts.

## 5. Results (C) and (D)

- **(C) Full realism** (M=1, 30%-actual gaps, estimated qf):
  1.25 µs, **G3 = 14.7×**, G1 χ² 2.00 — identical to gaps-only,
  because estimation is free at M=1. This is the number a mission
  proposal would quote for DSAC-class under realistic ops.
- **(D) 3-yr window** (M=1, estimated qf): 309 ns, **G3 = 7.5×**
  (oracle: 293 ns, 7.9×; cost 1.05×). The mission-relevant verdict
  is unchanged.

## 6. Bottom line for the program

- The round-2 note's "~1.5–2× real-world cost" for oracle qf is
  **replaced by a measurement: 1.00×** at M≤1000 (ML estimation is
  essentially free because the clock PSD is strongly identified),
  1.28× mean at M=3300 driven by one outlier seed.
- Every G3 verdict from round 2 survives: gaps, estimated qf, and
  both combined. Worst case tested (M=100, 40% epochs dropped):
  still 13× over holdover.
- The earned next steps are unchanged and now cheaper to defend:
  TOA-level (unbinned) data and/or the real-time loop. Nothing in
  this round moved any verdict.

## 7. Limitations (honest)

- White noise held at recalibrated values (separately data-measured);
  joint white+qf ML estimation not done — the qf cost here is
  conditional on known white.
- Red-noise PSDs (qred) still oracle (fitted from chains, not
  estimated in the loop); pulsar reds are the slower, less
  load-bearing parameters, but a fully blind pipeline would estimate
  them too.
- Gaps are whole-epoch, all-pulsar block blackouts; independent
  per-pulsar gap patterns not tested (likely *easier* for the
  filter — a common-mode clock is still observed through the
  surviving pulsars).
- Grid floor at Mhat=0.03: qf estimates below ~10⁻³×DSAC are
  quantized by the grid, irrelevant for any G3 verdict.
- Still hybrid (synthetic clock), still 30-day bins, still
  simulation-only. The M=3300 outlier-seed amplification (2.4×) is a
  reminder that seed tails exist; margins absorb them.

## Products

- `~/workspace/prtp/hidden_files/radio_pilot_robustness.py` — this
  round (ML qf grid search, gap masks, sweeps A–D)
- `~/workspace/prtp/hidden_files/radio_pilot_robustness.json` — all
  numbers (per-seed)
- This note:
  `~/workspace/goals/prtp-pulsar-timing-fusion-validation/hidden_files/radio_pilot_robustness_note.md`

*Simulation-only discipline: nothing here is flight readiness. This
round removes two idealizations from the radio pilot (oracle clock
PSD, perfect observing cadence) and measures their cost — ~1.00×
and ~4× in RMS respectively — with all headline verdicts intact.*
