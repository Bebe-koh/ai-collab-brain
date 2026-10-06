# Quantum-extension predictions re-derived from the corrected benchmark
**Date:** 2026-10-03 · **Status:** exploratory (completed-toy). No observational claims.
Re-derives the Kerr quantum-extension predictions (hypothesis registry, Flag 2)
from the action-consistent benchmark, replacing the stale 27.78° value.

## 0. What was stale and why

The quantum-extension predictions (EVPA notch depth, control bands, shot-noise
signature) were built on the notebook's 27.78° benchmark. Per the 2026-09-24
factor-of-two addendum (closure_phase_derivation_note.md), that benchmark
follows the notebook's *written* EOM (Reading B, Δχ = πγk), which contradicts
the action. The code-verified, action-consistent value is Reading A:

    ★  Δχ_slip = 2πγk     (per 2π winding; k=1 live, k=1/2 topologically dead)

Inverting the old benchmark: 27.78° = πγk  ⇒  γ ≈ 0.15433 (k=1).
Corrected at the same coupling: Δχ = 2π(0.15433) = 0.9697 rad = **55.56°**.
(At the round γ = 0.15: 54.0°.) All γ labels below use k = 1 unless stated.

Nothing in the R(t) program changes: the blind-spot-free statistic, its
synthetic-test verdicts, and the observing-requirements memo already use
Reading A (dchi_max = 2πγk, verified against inject_phase_slip.py).

## 1. Notch depth at 230 GHz: re-derived

| quantity | old (stale) | corrected (Reading A) |
|---|---|---|
| notch depth, γ≈0.1543, k=1 | 27.78° | **55.56°** |
| notch depth, γ=0.15, k=1 | 27.0° | **54.0°** |
| scaling | Δχ = πγk (wrong half) | Δχ = 2πγk |
| per-Δn=±1 tunneling event | 27.78° | **55.56°** |

The correction is a pure factor of 2 in angle. The larger step is *easier* to
detect, not harder — the correction helps the classical signature.

## 2. Control bands (86 / 345 GHz): the old claim does not survive as written

The derivation note (§3) confirms achromaticity as the signature's one robust
property: Δχ ∝ λ⁰ exactly, vs Faraday Δχ_F ∝ λ². The old prediction —
"frequency-localized notch at 230 GHz with 0.00° deviation at 86/345 GHz" —
is **inconsistent with the derived achromaticity**. A θFF̃ slip cannot be
present at 230 GHz and absent at 86/345 GHz; no frequency-dependent coupling
is on record that would localize it.

Corrected, derivation-consistent prediction:

| band | old claim | corrected |
|---|---|---|
| 230 GHz (target) | 27.78° step | **55.56° step** |
| 86 GHz (control) | 0.00° | **55.56° step (identical — achromaticity test)** |
| 345 GHz (control) | 0.00° | **55.56° step (identical — achromaticity test)** |

The control bands are a Faraday veto, not a null expectation: a λ²-scaled
pattern across bands falsifies (Faraday, not θ); identical steps confirm the
achromatic discriminator. If "frequency-localized" was intended as a
resonant enhancement at 230 GHz, that is new physics requiring its own
derivation — it is not in the θFF̃ EOM.

## 3. Shot-noise signature: re-derived (and its limits made explicit)

Old claim: individual Δn = ±1 tunneling events superimpose a shot-noise-like
component on the classical background → excess kurtosis + Allan variance in
notch depth across epochs.

**Per-event amplitude (corrected):** each Δn = ±1 event changes the winding by
2π, giving Δχ₁ = 2πγ = **55.56°** at benchmark γ (was 27.78°).

**Minimal model** (the most the pasted hypothesis supports — no tunneling rate
was ever derived): per epoch, notch depth D = 2πγ(k + X), with
X = N⁺ − N⁻, N⁺,N⁻ ~ Poisson(μ) i.i.d. (symmetric extra ±1 fluctuations).
X is Skellam: E[X] = 0, Var(X) = 2μ, fourth cumulant κ₄ = 2μ.

| quantity | old | corrected | notes |
|---|---|---|---|
| quantum rms per epoch | 2πγ·√(2μ)/2 → 3.9° at μ=0.01 | **2πγ√(2μ) = 7.9° at μ=0.01** | ×2 in amplitude |
| quantum variance | (πγ)²·2μ | **(2πγ)²·2μ — ×4 for fixed μ** | |
| excess kurtosis of D | 1/(2μ) | **1/(2μ) — unchanged in form** | amplitude-independent |
| Allan floor (quantum) | ∝ (πγ)²μ/τ_avg | **∝ (2πγ)²μ/τ_avg — ×4** | white-floor excess over thermal |

**Detectability condition** (quantum rms ≥ per-epoch thermal σ_th):

    μ ≳ σ_th² / [2(2πγ)²]

At benchmark γ: μ ≳ 0.0002 (σ_th = 1°), 0.0015 (σ_th = 3°), 0.004 (σ_th = 5°).
The threshold is low — *if* the fluctuation picture holds at any appreciable
rate, the scatter is easily detectable. But μ was never derived; it is a free
parameter, so this is a conditional prediction, not an absolute one.

**Consistency condition (new — the old picture did not state it):** the
per-event step (55.56°) equals the full classical slip (k=1). The
"small shot noise on a classical background" framing is only self-consistent
for **μ ≪ 1**: rare ±55.56° outliers on a stable 55.56° notch. For μ ~ 1 the
quantum rms (79°) swamps the classical signal and the "notch" is ill-defined.
So the corrected picture sharpens the signature: **notch depths across epochs
are quantized in units of 2πγ** (…, 0°, 55.56°, 111.1°, …) — integer-spaced
depths, with the spacing itself measuring γ. That discreteness is a stronger,
cleaner test than kurtosis alone, and it falls directly out of the Δn = ±1
structure.

**What was never established (before or after correction):** the tunneling
rate μ, the mapping from spatial winding-number fluctuations to the temporal
Δθ(t) that sources EVPA rotation (the derivation note's Δθ is a temporal
change; the quantum extension quantizes a spatial winding — the link is
asserted, not derived), and the event-counting model. The signature's *form*
survives; its *normalization* remains free.

## 4. Old vs corrected predictions — summary table

| prediction | old (stale benchmark) | corrected | status |
|---|---|---|---|
| notch depth @ 230 GHz | 27.78° | **55.56°** (γ≈0.1543, k=1) | scales ×2 |
| 86 / 345 GHz control bands | 0.00° (localized notch) | **55.56°, identical (achromaticity test)** | old claim broken — inconsistent with derived λ⁰ |
| per-tunneling-event step | 27.78° | **55.56°** | scales ×2 |
| shot-noise variance | (πγ)²·2μ | **(2πγ)²·2μ (×4)** | scales ×4 |
| excess kurtosis | 1/(2μ) | **1/(2μ)** | survives unchanged |
| Allan-variance quantum floor | ∝ (πγ)² | **∝ (2πγ)² (×4)** | scales ×4 |
| epoch-depth quantization | not stated | **depths at integer multiples of 2πγ** | new corollary of the correction |
| tunneling rate μ | free | **free (unchanged)** | still the missing normalization |
| winding→Δθ(t) mapping | asserted | **asserted (unchanged)** | still the missing link |

## 5. Verdict

- **Survive unchanged:** achromaticity (the robust discriminator); excess-kurtosis
  *form* 1/(2μ); the R(t) program and all its verdicts (already on Reading A).
- **Scale:** every angle ×2, every variance ×4. The correction helps
  detectability throughout.
- **Break:** the literal "0.00° at control bands" reading — replaced by the
  achromaticity test (identical steps at all bands; λ² pattern = Faraday veto).
- **Do not rescue:** the tunneling rate μ and the spatial-winding→temporal-Δθ
  mapping were never derived and remain free. The shot-noise signature is a
  well-formed *conditional* prediction (if μ, then this scatter with this
  quantization), not a quantitative forecast. Do not quote a predicted
  kurtosis value without stating the assumed μ.
- **New from this re-derivation:** the epoch-depth quantization corollary
  (integer multiples of 2πγ) and the μ ≪ 1 consistency condition — both are
  sharper than the original kurtosis/Allan-variance framing and should replace
  it as the stated quantum test.

**Bottom line:** the quantum-extension picture survives the factor-of-two
correction structurally and gets *stronger* observationally (bigger steps,
×4 variances, a quantization prediction). What it does not gain is the
normalization it never had: μ and the winding→rotation mapping remain open
derivations. Label: completed-toy. Nothing here is a detection claim.

## Assumptions (inherited, not re-derived)
- θ = phase of a single-valued complex field; ergospheric 2πk winding driven
  by frame-dragging; τ_slip ≈ 46.9 s (Sgr A*) asserted, not derived from the
  θ wave equation in Kerr.
- Global-slip morphology (coherent U(t) on all baselines); k = 1 benchmark
  coupling γ ≈ 0.1543 carried over from the old benchmark's implied value.
- Δn = ±1 tunneling events Poisson-distributed and symmetric per epoch
  (minimal model for the shot-noise claim).
- ½(∇θ)² backreaction neglected (small-gradient assumption).
