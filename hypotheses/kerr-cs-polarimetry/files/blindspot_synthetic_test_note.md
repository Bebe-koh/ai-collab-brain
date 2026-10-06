# Synthetic injection-recovery test of the blind-spot-free statistic
**Date:** 2026-10-03 · **Status:** simulation-only stress test of
`blindspot_free_observable_note.md` (round 1) · No observational claims.

## 0. What was tested

Round 1 derived the calibrator-differential transient statistic
R(t) = Q_tgt/Q_cal, Q = S^RL·conj(S^LR), finite-differenced to
r(t) = R(t+Δt)·conj(R(t)) and matched-filtered against the exact nonlinear
tanh template (note Eqs. 6–10), claiming (i) no detection blind spot at
γ=k/12, (ii) exact breaking of the synchronized R–L jump degeneracy,
(iii) blind spot returning when the ramp is unresolved, (iv) a practical
mod-1/12 estimation ambiguity at low S/N. This note stress-tests each claim
with end-to-end synthetic data.

**Simulation** (`blindspot_work/synth_test.py`; results in `synth_results.json`):
stacked closure phasors for target + calibrator with

- slip: Q_tgt → Q_tgt·exp(−12iΔχ(t)), Δχ = πγ[1+tanh((t−t₀)/τ)], τ = 46.9 s;
- synchronized jump: Q → Q·exp(+6iδ(t)) on **both** sources, δ a Heaviside step;
- slow intrinsic phase drift on both sources + white complex thermal noise;
- calibrator either ideal (same cadence) or interleaved (60-s scans every
  120/300/600 s, linear complex interpolation to target times).

Two statistics compared throughout: **new** = max-over-(γ_t,t₀)-grid matched
filter of (r−1) against the exact template; **old** = asymptotic endpoint step
|⟨Q⟩_post − ⟨Q⟩_pre|/⟨Q⟩_pre at known event time with the ramp (±3τ) excluded
(the note's Eq. 4 quantity, A(γ) = 2|sin 12πγ|). Significance is empirical:
detection fractions at fixed 1% / 0.1% false-alarm rates from 3000 null
realizations with full look-elsewhere over the template grid. A third
diagnostic, the free-t₀ step search (max over split times, no ramp exclusion),
is also reported.

## 1. Exp A — detection vs γ: the blind spot is gone for the new statistic

| injected γ | new det@1% | old (oracle) det@1% | old (free-t₀) det@1% |
|---|---|---|---|
| 0 (null) | 0.01 | 0.02 | 0.01 |
| 1/48 | 0.01 | 1.00 | 1.00 |
| 1/24 | 0.05 | 1.00 | 1.00 |
| **1/12** | **0.97** | **0.02** | 1.00 |
| 0.15 | 1.00 | 1.00 | 1.00 |
| **1/6** | **1.00** | **0.02** | 1.00 |
| **1/4** | **1.00** | **0.02** | 1.00 |
| **1/3** | **1.00** | **0.03** | 1.00 |

(120 injections per γ; per-sample fractional noise 5%; Δt = 10 s; det@0.1%
tracks det@1% — e.g. 0.90 at γ=1/12 for the new stat.)

**Verdict C1: CONFIRMED.** The new statistic detects at 97–100% at every
k/12 blind spot of the old one, whose oracle asymptotic step sits at the null
level (2–3%) there, exactly as Eq. 4 predicts. Detection margin
(median Z / null 99th pct) is modest (~1.0–1.4) because the null is the
max over a 420-template grid — the detection *fraction* is the honest metric.

Nuance (worth one line in the round-1 note): the **free-t₀** step search is
*not* blind at k/12 (detects 100%) — a split placed inside the ramp sees the
partial-winding amplitude dip. But that detection carries the wrong morphology
(it is the transient leaking into a step statistic) and cannot identify the
event; the oracle comparison is the fair test of the note's P1 claim.

## 2. Exp B — the jump confounder: broken, with a big caveat (see §4)

Jump-only injections, δ ∈ {π/24, π/12, π/6, π/4} (chosen so each makes a real
step in Q, |e^{6iδ}−1| ∈ {0.77, 1.41, 2.00, 1.41}):

- new statistic: det@1% = **0.02** at all four amplitudes (null = 0.01) — silent;
- old statistic: det@1% = **1.00** at all four — false-alarms, as in the EHT run.

Slip (γ=1/12) + jump (δ=π/6, different time): new detects the slip at 0.98;
old in the slip window sits at 0.01 (blind to the slip, would attribute
everything to the jump).

**Verdict C2: CONFIRMED under ideal calibrator sampling.** The cancellation
R → R·e^{+6i(δ(t)−δ(t̃))} is exact when the jump is sampled.

## 3. Exp C — unresolved ramp: the note's claim needs refining

With Δt ∈ {10, 20, 50, 100, 200} s at fixed grid phase, detection at γ=1/12
stays ~1.00 even at Δt/τ = 4.26 — because a sample landed near the ramp
center and the two straddling pairs each saw ~π of winding (r ≈ −1, an O(1)
transient). Varying the sample-grid offset at Δt = 200 s:

| grid offset (s) | 0 | 50 | 100 | 150 |
|---|---|---|---|---|
| new det@1% | 1.00 | 0.98 | **0.00** | 1.00 |

**Verdict C3: REFINED, not simply confirmed.** The blind spot does not
deterministically "return" for Δt≫τ — detection becomes a **sample-phase
lottery**: blind only when the full 2π winding falls inside a single
inter-sample interval (offset 100 s: E→~0.04, as in the round-1 demo), detected
otherwise. Heuristic: P(detect) ~ 2τ/Δt. For Sgr A* (Δt=10 s) this is moot;
the round-1 note's §2/§5 wording ("blind spot returns in the unresolved
limit") should be softened to the lottery picture.

## 4. Exp D — calibrator interpolation: the exact cancellation is fragile

Interleaved calibrator (60-s scans), jump δ=π/6 either mid-gap or in-scan:

| cadence | jump mid-gap: spurious det@1% | residual step (full = 2.00) | suppression |
|---|---|---|---|
| 120 s | 1.00 | 0.28 | ×7 |
| 300 s | **1.00** | **1.97** | **×1** |
| 600 s | 0.86 | 1.74 | ×1 |
| cadence | jump in-scan: spurious det@1% | residual step | suppression |
| 120 s | 0.02 | 0.12 | ×17 |
| 300 s | 0.00 | 0.15 | ×14 |
| 600 s | 0.03 | 0.15 | ×13 |

**Verdict C2-practice: PARTIAL — this is the most important qualification.**
A jump *between* calibrator scans is unobservable in the calibrator data, and
at EHT-realistic minute cadence the differential construction gives
**no suppression at all** (×1) for mid-gap jumps: linear interpolation blends
pre- and post-jump calibrator phasors, and the corrupted R(t) trips the
matched filter spuriously (det@1% = 1.00 at 300-s cadence). In-scan jumps are
suppressed ×13–17 and stay silent. Slip detection with interleaved (no-jump)
calibrator degrades only slightly (det@1% 0.97 → 0.86).

Consequence: the "exact" degeneracy-breaking holds **iff the jump is sampled
by calibrator scans**. An instantaneous mid-gap jump is uncorrectable by this
construction alone — the defense then rests entirely on the vetoes (a
calibrator-only step search *does* see the mid-gap jump as an inter-scan
step, so the veto logic in note §6 stands, but it is doing the real work, not
the differential). Practical requirement this sharpens: calibrator cadence
must be fast enough that jumps are *resolved* as sampled steps, or the veto
chain must be treated as primary, not backup.

## 5. Exp E — estimation and the mod-1/12 ambiguity

Mean-subtracted template shape correlation: corr(s_{1/12}, s_{1/6}) = **0.9971**,
confirming the round-1 number. But the *amplitude-aware* least-squares
estimator χ²(γ_t,t₀) = Σ|d − u(γ_t,t₀)|² (template at natural amplitude —
the correct estimator; the note's Eq. 10 normalization discards amplitude and
is flat in the linear regime) picks the true γ=1/12 in **100%** of
realizations at per-sample noise σ ∈ {0.02, 0.05, 0.1, 0.2, 0.4}, with **zero**
alias picks. At true γ=0.25, σ=0.8 (per-sample S/N ~ 1): true 0.66, alias
(1/3) 0.01, scattered 0.33.

**Verdict C4: REFINED — the ambiguity is much weaker than round 1 suggested.**
The 99.7% shape correlation is real, but the alias template has 2× the
amplitude (1.33× at γ=0.25), and amplitude is well measured — so the alias is
strongly disfavored, not a practical confounder, at any S/N where detection
itself is significant. Confusion appears only as scatter at very low S/N,
never as alias-locking.

Phase-unwrapping (cumsum of per-sample increments, the note's proposed
ambiguity-lifter): γ̂ = −ΣΔΦ/(24π·tanh 3) recovers **0.0809 ± 0.0006** at
σ=0.05 (true 0.0833; −0.002 bias from the intrinsic drift + window
truncation), within 10% in 100% of realizations up to σ=0.2 and 82% at
σ=0.4 — **confirming** "lifted in principle by unwrapping at high S/N",
with the per-sample |ΔΦ|<π condition holding (max 0.66 rad here).

## 6. Exp F — parameter recovery at high S/N: CONFIRMED

LS estimator, σ=0.05: γ̂ = 0.080 (true 1/12) and 0.150 (true 0.15) at grid
precision, t̂₀ = 40.0 s exact (true 40 s), zero alias picks in 160
realizations.

## 7. Verdicts on round-1 claims

| claim | verdict |
|---|---|
| C1: no detection blind spot at γ=k/12 | **confirmed** (0.97–1.00 det@1% at all k/12 ≤ 1/3) |
| old stat exactly blind at k/12 | **confirmed** (oracle asymptotic step at null level) |
| C2: jump degeneracy broken by R(t) | **confirmed** (ideal cal); **partial** in practice — mid-gap jumps at minute cadence are unsuppressed (×1) and cause spurious detections; vetoes become primary |
| C3: blind spot returns when Δt≫τ | **refined** — sample-phase lottery, not deterministic; P(detect) ~ 2τ/Δt |
| C4: practical mod-1/12 ambiguity at low S/N | **refined/downgraded** — amplitude-aware LS never alias-locks in tested range; unwrapping lifts it as claimed |
| parameter recovery (γ, t₀) | **confirmed** at high S/N |

## 8. Limitations of this test (honest)

- White thermal noise only — no red noise, no systematics beyond the jump;
  real EHT data is systematics-dominated, which is strictly harder.
- Worked at the stacked-phasor level (note Eq. 3), not from station RIME
  visibilities; the jump was injected directly as the common-mode map.
- Global-slip morphology (A1), tanh profile and τ (A2) taken as given —
  inherited, not tested.
- Jump modeled as a Heaviside step; real instrumental jumps have unknown
  profiles (the note already flags this).
- Calibrator assumed bright (2× target amplitude); a weakly polarized
  calibrator needs the jump-subtraction variant (note §4), not tested here.
- Detection margins are modest because the null is max-over-grid; quoted
  numbers are detection *fractions* at fixed empirical FPR, the honest metric.

## 9. Bottom line

The round-1 construction survives its synthetic stress test with two
material corrections: **(1)** the "exact" jump cancellation is exact only for
*sampled* jumps — with realistic interleaved calibrator cadence, mid-gap
jumps pass through unsuppressed and the veto chain becomes the primary
defense, not the backup; **(2)** the unresolved-ramp and mod-1/12 caveats are
both softer than stated — a sample-phase lottery and a non-issue for the
amplitude-aware estimator, respectively. None of this reopens a detection
blind spot: at every γ=k/12 tested, the transient statistic detects at
≥97% where the endpoint statistic sits at the null level.

## Files
- `blindspot_work/synth_test.py` — full simulation (exps A–F)
- `blindspot_work/replot.py` — figure regeneration from `synth_results.json`
- `blindspot_work/synth_results.json` — all numbers
- `blindspot_work/synth_figA.png` — detection vs γ (old vs new)
- `blindspot_work/synth_figBC.png` — jump confounder + sample-phase lottery
- `blindspot_work/synth_figD.png` — calibrator-cadence residual floor
- `blindspot_work/synth_figE.png` — alias/estimation behavior
