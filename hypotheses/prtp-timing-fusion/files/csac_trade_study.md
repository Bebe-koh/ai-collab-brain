# PRTP clock-class trade study + NANOGrav radio pilot design
**2026-10-03 · simulation-only · conditional on stated assumptions**

## 1. Question and headline answer

The repaired NICER pilot ended in a quantified NO-GO: on X-ray data the
filter is measurement-noise dominated (~1.0–1.4 ms) while a DSAC-class
clock wanders ~1.4 µs, so pulsar aiding beats holdover only for clocks
~1000× worse than DSAC. Two questions follow:

**(a) For which clock classes does aiding actually win?** Break-even is a
surface in (clock ADEV, dataset quality, span), not a single number:

- **X-ray (NICER-like) data, 2-yr span:** break-even at **M\* ≈ 850–1000**
  (ADEV(1d) ≈ 3×10⁻¹²). A CSAC (M ≈ 3,300) wins ~4×; DSAC loses by ~800×.
- **Radio (NANOGrav-like) data, 2-yr span:** break-even at **M\* ≈ 0.2**
  (planning figure, sim-derived — the radio pilot must measure it). Aiding
  wins even for clocks several times *better* than DSAC; for a CSAC it wins
  by ~10⁴×.
- **Span is leverage:** on X-ray data a CSAC needs ≳1 yr of span before
  aiding pays (at 6 months, holdover still wins).

**(b) Radio pilot:** designed below (not run). All data products already
exist in the workspace.

## 2. Measured anchors (not vibes)

| # | Quantity | Value | Source |
|---|---|---|---|
| A1 | X-ray filter floor σ_m,X | 1.04 ms (1×) → 1.38 ms (1000×), nearly flat in clock quality | repair note §3, hybrid injection, measured |
| A2 | Holdover RMS, 1× DSAC, 2-yr span | 1.4 µs; linear in M (14 µs @10×, 140 µs @100×, 1.40 ms @1000×) | repair note §3 sweep table, measured |
| A3 | Clock model | frequency random walk, qf ∝ M², calibrated to ADEV(1d)=3e-15·M | simulate.py / pilot_filter.py |
| A4 | Radio filter floor σ_m,R (planning) | ≈ 0.3 µs (range 0.1–1.0) | **sim-derived** (Round 1: Kalman 92 ns steady-state, 4 pulsars, σ_w 120–700 ns, 14 d cadence, 3 yr). TO BE MEASURED by the radio pilot |
| A5 | CSAC SA.65 | ADEV 3.0×10⁻¹⁰ @ 1 s; aging < 9×10⁻¹⁰/mo | Microchip datasheet (verified 2026-10-03) |
| A6 | CSAC SA65-LN | ADEV < 1×10⁻¹¹ @ 1 s; drift < 0.9 ppb/mo | Microchip (verified 2026-10-03) |

Effective stochastic ADEV(1d) for CSAC: white-FM extrapolation
3e-10/√86400 ≈ 1e-12, but the flicker floor (~1e-11) intervenes first.
Adopted: **σ_y(1d) ≈ 1×10⁻¹¹, range 3×10⁻¹²–3×10⁻¹¹ → M ≈ 3,300
(range 1,000–10,000)**. SA65-LN: M ≈ 1,000–3,300.

## 3. Break-even derivation

Holdover (free-running clock, RW FM) over span T, from anchor A2 and the
RW-FM T^1.5 scaling (checked numerically against the sim's own clock
generator; agreement within ~2×, see §5):

    H(M, T) = M · 1.4 µs · (T / 2 yr)^1.5                          (1)

Filter RMS is measurement-noise dominated and nearly flat in M (A1):

    σ_m(M) ≈ σ_X = 1.2 ms (X-ray) ; σ_R ≈ 0.3 µs (radio, planning)  (2)

Break-even M\*(T) = σ_m / [1.4 µs · (T/2yr)^1.5]. Improvement factor
I(M,T) = H(M,T)/σ_m (>1 ⇒ aiding wins).

### Table 1 — Break-even multiplier M\* (ADEV(1d) = M × 3e-15)

| dataset \ span | 0.5 yr | 1 yr | 2 yr | 5 yr |
|---|---|---|---|---|
| X-ray (σ_m=1.2 ms, measured) | 6,900 | 2,400 | **860** | 220 |
| Radio (σ_m=0.3 µs, sim-derived) | 1.7 | 0.6 | **0.2** | 0.05 |

The X-ray 2-yr entry (860) reproduces the pilot's measured ~950–1000
boundary within the expected slop (the measured value is slightly higher
because σ_m rises 1.04→1.38 ms with M; the table holds σ_m fixed).

### Table 2 — Improvement factor I = holdover / filter (X-ray data)

| clock \ span | 0.5 yr | 1 yr | 2 yr | 5 yr |
|---|---|---|---|---|
| DSAC (M=1) | 0.0001 | 0.0004 | 0.001 | 0.005 |
| 100× DSAC (M=100) | 0.015 | 0.04 | 0.12 | 0.46 |
| 1000× DSAC (M=1000) | 0.15 | 0.41 | 1.2 | 4.6 |
| **CSAC SA.65 (M≈3300)** | **0.48** | **1.4** | **3.9** | **15** |
| CSAC pessimistic (M=10000) | 1.5 | 4.1 | 12 | 46 |

### Table 3 — Improvement factor I (radio data, σ_m=0.3 µs planning)

| clock \ span | 0.5 yr | 1 yr | 2 yr | 5 yr |
|---|---|---|---|---|
| DSAC (M=1) | 0.6 | 1.7 | **4.7** | 18 |
| 10× DSAC (M=10) | 5.8 | 17 | 47 | 184 |
| **CSAC SA.65 (M≈3300)** | **1900** | **5600** | **15400** | **61000** |

Reading: on X-ray data a CSAC needs ≳1 yr span for aiding to pay, and
wins ~4× at 2 yr. On radio data the filter is ~10⁴× below the X-ray
floor, so aiding wins for every plausible clock at ≳1 yr spans — the
radio pilot's job is to confirm σ_m,R is really ~0.3 µs on real data.

## 4. CSAC verdict, with the aging-drift caveat

Stochastic part: CSAC (M≈3,300) sits **above** the X-ray break-even
(M\*≈860 at 2 yr) → aiding wins ~4× on NICER-class data, ~10⁴× on
radio-class data. The concept's natural home is exactly this clock
class: cheap, low-SWaP, too unstable to hold over.

Deterministic aging (<9×10⁻¹⁰/mo = 3.5×10⁻¹⁶/s) is a separate, larger
term: uncorrected, ½·D·T² ≈ 0.7 s over 2 yr — three orders of magnitude
above the stochastic holdover. Two notes:
- The Kalman filter carries a drift state, so it **absorbs** deterministic
  aging; the comparison above (stochastic-only holdover) is therefore
  conservative *for* aiding. A real holdover baseline would pre-calibrate
  drift, leaving residual drift uncertainty — bracketed between the two.
- SA65-LN (better short-τ, same aging) does not change this picture;
  aging, not ADEV(1 s), is the long-span driver.

Caveat that cuts the other way: the pilot's filter was handed oracle qf.
A real CSAC loop must estimate qf (and drift) from the data; Round 2's
noise-estimation work suggests a factor ~1.5–2 cost, which does not move
any verdict above (margins are 4×–10⁴×).

## 5. Assumptions, limits, and what would change the answer

1. **RW-FM clock model.** All M-scaling and the T^1.5 span law assume the
   project's calibrated random-walk-frequency clock. Real CSACs have
   white-FM at short τ and deterministic aging (treated in §4); the
   stochastic break-even is robust to this, the exact M\* less so (±3×).
2. **σ_m,X is for 2 pulsars / ~46 bins.** More pulsars or denser cadence
   lower it ~1/√N; the X-ray boundary would move down proportionally.
   The scaling is weak (square root) — it does not rescue DSAC.
3. **σ_m,R = 0.3 µs is sim-derived.** Real NANOGrav data has red noise
   (B1937 weighted RMS 6363 ns), backend jumps, and ECORR. If the measured
   σ_m,R comes out 3× worse, Table 3's factors drop 3× — verdicts unchanged
   (margins are huge). If it comes out 30× worse (9 µs), the DSAC 2-yr
   cell flips to holdover-wins; the CSAC cells still win by ~500×.
4. **Oracle qf** (see §4). Real noise-estimation cost ~1.5–2× on σ_m.
5. **The T^1.5 check** reproduced the scaling shape but ran ~1.8× above
   the pilot's measured 2-yr anchor (grid/measure details); tables use the
   pilot's measured anchor, so this only affects the span-extrapolated
   columns, flagged ±2×.

## 6. NANOGrav radio pilot — design (not run)

**Goal:** the original PRTP concept (radio pulsar timing fusion for clock
estimation) tested on real data — the test the X-ray recast failed to be.

**Data (all already in workspace):**
- NANOGrav 15-yr narrowband release v2.0.1
  (`prtp/hidden_files/nanograv15yr/`): TOAs + par files for J0437-4715,
  J1909-3744, B1937+21, B1855+09 (5,537 / 34,829 / 23,023 / 7,666 TOAs),
  plus the collaboration's noise chains
  (`narrowband/noise/*.nb.chain_1.txt`, EFAC/EQUAD/ECORR per backend).
- Existing binned product (`prtp/hidden_files/nanograv_binned.npz`):
  30-day bins — 154 (J1909), 167 (B1937), 112 (B1855), 21 (J0437);
  only 14 epochs common to all four.
- Tooling: `venv_pint` (PINT 1.1.7); established recipes in
  `nanograv_gls_note.md` (MAD outlier cut, DMX-corrected residuals) and
  `chain_binned_note.md` (two-component white fit).

**Pulsars/epochs:** primary three J1909-3744 + B1937+21 + B1855+09 (longest
binned series, chains available); J0437-4715 as fourth where it overlaps.
Use the full per-pulsar binned series (masked Kalman handles
asynchronous data — do NOT restrict to the 14 common epochs). Full 15-yr
span for the σ_m,R measurement; a 3-yr sub-window for the
mission-relevant break-even check.

**Noise model (the hard lesson, applied):** never trust binned formal
errors (chain_binned_note: underestimated 10–100×). Per-bin white from
the chains: σ² = (EFAC·σ_TOA)² + EQUAD² with posterior-median
EFAC/EQUAD/ECORR per backend (J0437 3.39 / J1909 1.01 / B1937 1.43 /
B1855 1.08); red states per pulsar with qred from the chains (B1937 is
red-dominated — the filter must absorb it, and the achromaticity result
in b1937_wobble_note.md justifies single-band use). No NICER-style
ObsID bias states (radio has no block offsets); verify JUMPs are applied
from the par files. Innovation gating χ²>25 as defense-in-depth.

**Clock injection (hybrid, as in the NICER repair):** synthetic RW-FM
clock at M ∈ {0 (null), 1, 100, 1000, 3300}, ≥5 seeds per class,
calibrated to ADEV(1d) = 3e-15·M via the existing calibrator. Real
residuals + injected clock; filter is given oracle qf (same as pilot;
note the §4 caveat).

**Estimator:** repaired Kalman v2 (empirical white R, per-pulsar red
states, causal filter + RTS smoother), adapted per above. Static GLS as
the robust fallback (per Round 1: no transient, never diverges).

**Success/failure criteria (mirroring the X-ray pilot):**
- **G1-radio:** filter's predicted error (CR bound from the fitted model)
  vs measured hybrid RMS within 3×, on ≥3 of 4 pulsars' worth of data.
- **G2-radio:** hybrid RMS / matched-sim RMS < 1.5 (sim-to-real transfer).
- **G3-radio:** hybrid RMS < holdover RMS at each M; expect PASS at all
  M ≥ 1 (Table 3), with the measured margin recorded.
- **Null control (the ±350 ns lesson):** M=0 injection → estimated clock
  consistent with zero within σ_m; any significant monopole is a
  systematic, not a detection.

**Deliverables:** pilot note with the three criteria verdicts, the
**measured σ_m,R** (the single number Table 1–3 need), hybrid-vs-sim
plots, and the null-control result. Estimated compute: binned Kalman on
~450 bins × 4 pulsars × 5 clock classes × 5 seeds — minutes on 2 CPUs.

## 7. Bottom line for the program

- The NO-GO stands for DSAC-class clocks on X-ray data. It was never
  about CSACs.
- **CSAC + pulsar aiding is a go on paper:** ~4× win on X-ray-class data
  at 2-yr spans, ~10⁴× on radio-class data, with the deterministic aging
  term making the case stronger, not weaker.
- The radio pilot is fully specified and all inputs exist; its measured
  σ_m,R is the one number that firms up (or revises) Table 3.
