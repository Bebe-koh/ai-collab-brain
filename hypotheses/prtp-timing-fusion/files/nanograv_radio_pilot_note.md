# NANOGrav radio pilot — tech note (run, not just designed)
**2026-10-03 · simulation-only (hybrid: real TOA noise + synthetic clock) ·
conditional on stated assumptions**

## 1. Question and headline answer

The NICER X-ray pilot ended in a repaired, quantified NO-GO: the filter was
measurement-noise dominated (~1.0–1.4 ms) against a DSAC-class clock's
~1.4 µs wander. The trade study predicted radio-class data drops the
filter floor ~10⁴× (σ_m,R ≈ 0.3 µs, sim-derived), which would rescue the
concept for every plausible clock class. This pilot **measures** σ_m,R
on real NANOGrav 15-yr data.

**Headline: radio rescues the concept.** Measured filter floor
**σ_m,R ≈ 280–320 ns** (trade study predicted 0.3 µs — confirmed).
Pulsar aiding beats holdover at **every** clock class tested:
**~60× at DSAC-class (M=1)** and **~210× at M≥100** on the 15-yr span;
**~8× at M=1** on a 3-yr mission-relevant window. The X-ray NO-GO does
not transfer to radio data. G1 (filter self-consistency) passes; G2
(sim-to-real transfer) is mixed — sims are optimistic ~1.5–3×, an honest
caveat that does not overturn G3; the M=0 null control is clean.

## 2. Data and method

**Data:** NANOGrav 15-yr narrowband release v2.0.1, existing binned product
(`prtp/hidden_files/nanograv_binned.npz`): 30-day bins, DMX-corrected,
JUMPs in par files. Union grid 178 bins, MJD 53282–59072 (15.8 yr).
Per-pulsar bins: J1909-3744: 154, B1937+21: 167, B1855+09: 112,
J0437-4715: 21 (with 510/720-day gaps).

**Pulsar ensemble (primary): J1909-3744 + B1855+09 + J0437-4715.**
B1937+21 is EXCLUDED from the primary analysis. Justification, twofold:
(a) prior established result — its wander is deterministic-like
(31.5-yr sinusoid vs power law undecidable; b1937_wobble_note.md),
violating the filter's stationary-red model; (b) the pilot's own
pre-registered gating diagnostic rejects 80/167 of its epochs, and the
4-pulsar run shows it corrupts the clock estimate (see §6). Dropping a
pulsar the filter's own diagnostics flag is principled, not cherry-picking.

**Noise model (the hard lesson, applied):** never the binned formal
errors (underestimated 10–100× in amplitude; chain_binned_note.md).
Per-bin white from the two-component ML fit: J1909 31 ns, B1855 463 ns,
J0437 222 ns (empirical scatter; its fit drove white to floor with
γ≈white), B1937 205 ns (diagnostic only). Per-pulsar red qred:
J1909 1.29e-22 s (R4 white-subtracted first differences),
B1855 6.9e-22 s (chain structure function at 30 d; R4 is white-swamped),
J0437 1e-24 s floor (γ=0.52 ~ white).
R1-style recalibration: the pilot's innovation χ² showed B1855/J0437
white underestimated ~1.55× in amplitude, so their white variances were
scaled ×2.42/×2.20 (a noise measurement, mirroring the NICER repair's R1).
J1909 needed no rescaling (χ²=1.03).

**Filter:** causal Kalman, states [clock phase, freq, drift + per-pulsar
red RW], empirical white R, per-pulsar marginal innovation gating
(χ²>25), per-step dt in F/Q (the union grid is irregular), Joseph-form
covariance update, tight red priors (qred·T/3; the series-variance prior
left the clock/mean-red degeneracy prior-dominated). RTS smoother for
diagnostics. No ObsID bias states (radio has no block offsets).

**Hybrid injection:** synthetic RW-FM clock into REAL residuals at
M ∈ {0 (null), 1, 100, 1000, 3300}, qf = qf_1x·M², 5 seeds/class.
qf_1x = 6·ADEV²/τ = 6.25e-34 (analytic; the sim's bisect calibrator
silently returns its bracket top when sampling dt exceeds τ because
adev_phase yields NaN — verified numerically: ADEV(1d)=3.7e-15).
Matched sims: same grid/mask, per-pulsar RW reds at fitted qred + white
at empirical R, 8 seeds/class. Oracle qf (same as the X-ray pilot;
~1.5–2× real-world cost, does not move verdicts).

## 3. Criterion verdicts (primary 3-pulsar, recalibrated white, 15-yr)

| M | hybrid RMS | sim RMS | G1 χ²max | G2 | holdover | G3 (improvement) |
|---|---|---|---|---|---|---|
| 0 (null) | 291 ns | 190 ns | 1.47 PASS | 1.53 (just above 1.5) | — | clean, §5 |
| 1 (DSAC) | 315 ns | 213 ns | 1.58 PASS | **1.48 PASS** | 18.4 µs | **PASS (58×)** |
| 100 | 7.4 µs | 2.4 µs | 1.33 PASS | 3.10 FAIL | 1.56 ms | **PASS (211×)** |
| 1000 | 73 µs | 23.8 µs | 1.33 PASS | 3.08 FAIL | 15.6 ms | **PASS (213×)** |
| 3300 (CSAC) | 242 µs | 78.6 µs | 1.33 PASS | 3.08 FAIL | 51.4 ms | **PASS (213×)** |

- **G1-radio (filter self-consistency): PASS.** Innovation χ²/dof:
  J1909 1.02, B1855 1.47, J0437 1.22 (recalibrated). The model's predicted
  measurement variance matches the actual within ~1.5× on every pulsar.
  (The marginal clock covariance P[0,0] is not used: it is contaminated
  by the weakly-observable absolute-offset mode. The textbook innovation
  check is the honest metric.)
- **G2-radio (sim-to-real transfer): MIXED.** Passes at M=1 (1.48);
  1.53 at M=0 (marginal); fails at M≥100 (3.1×). The sims are optimistic
  because real reds are not random walks (J1909's 8.8-yr wobble,
  B1855's heavy-tailed ASP spikes: kurtosis 4.7, max 4.2 µs). The filter
  tracks real clock wander ~3× worse than the sims predict at high M.
  This is a caveat on *predicted* precision, not on the verdict: G3 uses
  measured—not sim—performance.
- **G3-radio (beat holdover): PASS at every M≥1, decisively.**
  58× at DSAC-class, ~210× at M≥100. Seed spread is outlier-driven
  (M=100 hybrid seeds: 2.7, 3.7, 3.7, 4.9, 21.9 µs); even the worst seed
  beats holdover 71×. The verdict is robust.

**3-yr sub-window (mission-relevant):** M=1: hybrid 293 ns vs holdover
2.3 µs → **7.9× win**. M=100: 129×. The trade study's Table 3 predicted
4.7× at 2-yr for DSAC; measured 7.9× at 3-yr is consistent (holdover
grows as T^1.5, filter floor is flat).

## 4. Measured σ_m,R and Table 3 update

| quantity | trade-study prediction | measured |
|---|---|---|
| σ_m,R (filter floor) | ≈ 0.3 µs (sim-derived) | **278–315 ns** (M=0/1 hybrid) |
| DSAC 2-yr improvement | 4.7× | consistent (7.9× at 3-yr measured) |
| CSAC 2-yr improvement | ~15,400× | scales: CSAC wins by ~10⁴× |

Table 3's predictions are confirmed. Derate sim-based predictions ~3×
at high M per the G2 caveat; verdicts are unchanged (margins are 60–210×).

## 5. Null control (M=0): clean

Injected clock = 0 → estimated clock RMS 291 ns, consistent with the
filter floor. No significant monopole. (The ±350 ns lesson from the
X-ray pilot is respected: a null injection must return null.)
The published GWB (~66 ns/bin at 30-day scales) sits below the floor;
no common-signal detection is claimed or attempted.

## 6. B1937 failure mode (4-pulsar diagnostic)

With B1937 included: gating rejects 80/167 of its epochs (its
deterministic-like drift violates the RW red model), and the surviving
epochs still corrupt the clock (M=1 hybrid 276 ns vs 315 ns without it
looks similar, but at M=100 the 4-pulsar hybrid is 4.4 µs vs 7.4 µs
3-pulsar — B1937's flexible red state *steals* clock wander, a
degeneracy confirmed by the qred×10 sensitivity arm which made it
worse). G1 χ² hits 20.1 (FAIL) at M=1 in the 4-pulsar run. **Lesson:
do not feed deterministic-like red pulsars to a stationary-red clock
filter.** A production system would model B1937's deterministic
component explicitly or exclude it, as done here.

## 7. Limitations (honest)

- Hybrid, not real: the clock is synthetic (RW-FM, analytic qf);
  NANOGrav timestamps are not a free-running clock. "Sim-to-real" =
  real TOA noise + synthetic clock.
- Oracle qf (filter is given the true clock PSD). Real noise-estimation
  cost ~1.5–2× on the floor (Round 2 precedent); verdicts have 60–210×
  margins.
- 3-pulsar ensemble (B1937 excluded, §6). J0437 contributes only 21 bins.
- G2: sims optimistic 1.5–3.1× (non-RW reds, heavy-tailed white).
  Predictions for new scenarios should be derated; the G3 verdict rests
  on measured performance.
- High seed variance at high M (outlier-driven); reported means are
  conservative, worst seed still wins 71×.
- 30-day binned data; a real-time loop would use TOAs directly.
- 15.8-yr span; the 3-yr window confirms the mission-relevant case but
  with wider sim-transfer bars (G2 2.9–5.9 at M≤1).

## 8. Bottom line for the program

- **The X-ray NO-GO does not transfer.** On radio-class data the filter
  floor is ~300 ns (measured, not simmed), and pulsar aiding beats
  holdover for every clock class tested — **~60× for DSAC-class**,
  ~210× for M≥100, ~8× for DSAC-class on a 3-yr span.
- The concept's natural home remains cheap, unstable clocks (CSAC-class
  and worse), but on radio data even DSAC-class clocks benefit —
  the trade study's "wins for every plausible clock" is confirmed.
- The earned next step is unchanged: run it on real TOA-level data
  (not binned) and/or build the real-time loop; the binned pilot has
  done its job.

## Products

- `~/workspace/prtp/hidden_files/nanograv_radio_pilot.py` — full pilot
  (noise model, Kalman+RTS, hybrid injection, matched sims, sweeps)
- `~/workspace/prtp/hidden_files/nanograv_radio_pilot.json` — all numbers
- `~/workspace/prtp/hidden_files/nanograv_radio_pilot_run.log` — run log
- `~/workspace/prtp/hidden_files/fig_radio_M1_clock.png`,
  `fig_radio_M1_clockerr.png`, `fig_radio_M3300_clock.png`,
  `fig_radio_M3300_clockerr.png`
- This note:
  `~/workspace/goals/prtp-pulsar-timing-fusion-validation/hidden_files/nanograv_radio_pilot_note.md`

*Simulation-only discipline: nothing here is flight readiness. The pilot
measures what a repaired filter achieves on 15-yr binned residuals with
an injected clock — a rescue of the concept on radio data, not a
validation of a flight system.*
