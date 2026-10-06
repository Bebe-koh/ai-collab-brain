# Wide-array spatial separation — assessment and results

**Date:** 2026-09-24
**Status:** archival-data analysis. Not a detection of anything.
**Files:**
- `~/workspace/prtp/hidden_files/wide_array.py` — variance-component fits (Stages 1–2)
- `~/workspace/prtp/hidden_files/wide_array_stage3.py` — long-baseline monopole series + ULDM scan
- `~/workspace/prtp/hidden_files/wide_array_leakage.py` — leakage diagnostics
- `~/workspace/prtp/hidden_files/wide_array_phasetest.py` — common-phase test
- `~/workspace/prtp/hidden_files/wide_array_results.json` — Stage 1–2 numbers
- `~/workspace/prtp/hidden_files/wide_array_stage3.json` — Stage 3 numbers

## Question

All real-data results so far used 4 pulsars × 14 common 30-day epochs: a robust
±350 ns monopole (common mode, chi²=406/14), source ranked clock-like; ULDM
statistically tied but with best period (6.7 yr) exceeding the 4.8-yr span;
ephemeris disfavored; the B1937/B1855 correlated wander (r≈0.94) fooled both the
HD and dipole templates. With only 4 pulsars the spatial leverage is weak by
construction. Can we do better with what's on disk?

## 1. Inventory — what actually exists

`~/workspace/prtp/hidden_files/nanograv15yr/extracted/` contains:
- `clock/`: AO/GMT/BIPM clock-correction files (used in the clock cross-check)
- `narrowband/noise/`: chain + pars files for **4 pulsars only**
  (J0437-4715, J1909-3744, B1937+21, B1855+09)
- `narrowband/par/`: 4 PINT timing models; `narrowband/tim/`: 4 TOA files

**There is no 68-pulsar data on disk.** A genuine wide-array (68-pulsar)
monopole/dipole/quadrupole separation is **not feasible** from what's here.

What IS feasible, and was not yet exploited: the binned residuals file
`nanograv_binned.npz` holds **full-span** 30-day bins per pulsar, not just the
14 common epochs:

| pulsar | bins | span |
|---|---|---|
| J0437-4715 | 21 | 4.8 yr (common window only) |
| J1909-3744 | 154 | 15.5 yr |
| B1937+21 | 167 | 15.9 yr |
| B1855+09 | 112 | 15.5 yr |

161 of 194 thirty-day bins have ≥2 pulsars (14 with 4, 87 with 3, 60 with 2).
So: a **4-pulsar × 161-bin** analysis over **15.9 yr** — 11× more epochs and
3.3× the time baseline. That is what was run.

## 2. Method

**Stage 1 — global variance-component fit.** Per bin b (pulsars S_b):
C_b = diag(white_b) + diag(s²_a) + A_m²·11ᵀ + A_d²·(n̂n̂ᵀ) + A_h²·Γ_HD,
max-likelihood over per-pulsar excess variances s²_a (a=1..4) and spatial
amplitudes (A_m, A_d, A_h ≥ 0). Nested models (drop each component), drop-one
pulsar jackknives, and a B1937+B1855-pair drop.

**Stage 2 — time-chunked fits** (5 chunks): (A_m, A_h) per chunk → is the HD
component stable or time-localized?

**Stage 3 — long-baseline monopole series.** Per-bin GLS common mode M(t)
(161 bins, 15.8 yr), then: (a) clock-like epoch-uncorrelated variance;
(b) ULDM coherent-sinusoid grid scan, P = 60 d–20 yr, diagonal errors;
(c) red-marginalized scan (null = diag + propagated per-pulsar red covariance
with free scale; alt adds sinusoid).

**Follow-ups:** leakage diagnostics (per-pulsar 7.9-yr fits, monopole variants,
weight correlations) and a joint common-phase vs independent-phase test.

Conventions match the published series (npz V field used as white variance;
see caveats). Red chain medians from `nanograv_gls_results.json`.

## 3. Results

### 3.0 Dead end, recorded: fixed-noise variance components (v1)

First attempt fixed per-pulsar red at chain values and fit only
(A_m, A_d, A_h). Result: A_h = 5185 ns, A_m → 0.2 ns, A_d → 0.1 ns —
the HD template soaked up everything and the monopole vanished.
**Diagnosis:** B1937's binned scatter (6093 ns empirical at full span)
exceeds its chain red prediction (633 ns) by ~10×; with red fixed, the
fit's only way to explain B1937's variance is the HD template (peak 0.77
on the B1937×B1855 pair). The monopole — a subtle ~180 ns effect — is
invisible next to the mis-modeled variance. **Lesson:** with per-pulsar noise this
mis-modeled, spatial components must earn their keep via *off-diagonal
covariance only* — hence the v2 parameterization with fitted per-pulsar
variances s²_a.

### 3.1 Global variance-component fit (v2): no spatial covariance at all

With per-pulsar excess variances fitted empirically, **every spatial
component goes to zero**:

| model | nll | dlnL vs null |
|---|---|---|
| m+d+h | 3719.8 | −0.0 |
| m+d | 3719.8 | −0.0 |
| m+h | 3719.8 | −0.0 |
| m | 3719.8 | −0.0 |
| null (per-pulsar variances only) | 3719.8 | — |

Fitted per-pulsar excess s (ns): J0437 **0.2**, J1909 **270.8**,
B1937 **6057.4**, B1855 **1120.6** — vs chain predictions 218/69/633/217 ns.
Profile-likelihood upper limits (≈1σ, dlnL<0.5): A_m < 2.2 ns,
A_d < 0.4 ns, A_h < 36 ns.

**The "monopole" is not a common signal.** It is per-pulsar excess
variance, and the common-mode estimator was seeing J1909's 271 ns through
an 89%-weight keyhole (σ_c = 269 ns ≈ 271 ns is no coincidence — and
J1909's excess ≈ its 7.9-yr wave RMS, 357/√2 = 252 ns).

Direct confirmation — pairwise residual correlations (overlapping bins,
permutation p-values):

| pair | r | N | p |
|---|---|---|---|
| J0437 × J1909 | −0.25 | 21 | 0.28 |
| J0437 × B1937 | +0.21 | 21 | 0.36 |
| J0437 × B1855 | +0.16 | 14 | 0.59 |
| J1909 × B1937 | **−0.57** | 149 | <10⁻⁴ |
| J1909 × B1855 | **−0.44** | 96 | <10⁻⁴ |
| B1937 × B1855 | −0.18 | 104 | 0.07 |

A 181-ns common jitter (the 14-epoch σ_c) predicts r(J0437,J1909) = +0.53;
observed −0.25 ± 0.22: ruled out at ~3.5σ. (A 269-ns common jitter is
impossible outright — it exceeds J0437's *total* per-bin scatter of
222 ns.) The significant *negative* J1909×B1937/B1855 correlations are the
anti-phase slow excursions (§3.4): J1909's 8-yr wave at phase 0.13 rad vs
B1937's at 3.22 rad. The B1937×B1855 full-span r = −0.18 reproduces the
wander investigation's "full 15-yr r = −0.18" exactly (the +0.94 was
window-local to 2015–2020).

Reconciliation with the published record: the original monopole evidence
(chi² = 406/14, σ_c = 181 ns) measured excess variance in a GLS
common-mode estimator that is 89% J1909 — it never tested cross-pulsar
*co-movement*. "Survived drop-one tests" is also consistent with
per-pulsar excess: dropping J1909 leaves B1937/B1855's huge excesses
(σ_c stays nonzero); dropping the others leaves J1909's. The v2 fit is
the first test that separates common covariance from per-pulsar variance,
and the answer is unambiguous: **dlnL = 0.0**.

(Drop-one-pulsar jackknives of the v2 fit give unstable, mutually
inconsistent spatial amplitudes — e.g. m = 818 ns without J1909, m = 0
with all four — as expected when fitting 7 parameters to small subsets
for components that are actually zero. The full-data dlnL = 0 is the
result that counts.)

### 3.2 Time-chunked (A_m, A_h): nothing stable

Five time chunks, (A_m, A_h) fits: h = 0/0/367/53/0 ns across chunks,
m ≈ 0 throughout. Given the global dlnL = 0, these are weakly-identified
fluctuations (33 bins each), not a signal — certainly no stable HD
component. The B1937/B1855-driven HD artifact does not survive empirical
per-pulsar variances: it was mis-modeled variance, not spatial structure.

### 3.3 Monopole series: the variance persists, and grows — but it is not common

- 161 bins, 15.77-yr span; series RMS **378 ns** (vs 184 ns in the 14-epoch window).
- Clock-like epoch-uncorrelated variance: **σ_c = 269 ns, dlnL = 522** vs null.
- See §3.1: this variance is J1909's private excess (271 ns fitted), not
  array co-movement. The estimator is ~90% J1909 by weight (93% mean
  weight in the 161-bin series); σ_c ≈ 271 ns is identity,
  not coincidence.

### 3.4 The 7.9-yr wave that wasn't

The ULDM grid scan on M(t) returned a striking peak: **P = 7.91 yr,
A = 265 ns, dlnL = 532** vs null (diagonal), top-5 all at 7.3–8.6 yr —
and **dlnL = 127 vs a free-scale red-noise null**. With 15.8 yr of data
this is two full cycles, not the sub-span hump of the 14-epoch analysis.
Taken at face value it would be a significant coherent oscillation.

It is not a common signal. Decisive tests:
- **Per-pulsar phases are inconsistent.** Joint fit at f = 1/7.906 yr⁻¹:
  independent phases beat a common phase by **dlnL = 619** (4 extra params).
  The common-phase fit assigns *all* amplitude to J1909 (339 ns) and zero
  to the other three pulsars. An Earth-term (monopole) wave must have one
  phase everywhere; J1909 sits at 0.13 rad, B1937 at 3.22 rad, B1855 at
  2.79 rad.
- **It is J1909's own excursion.** J1909 alone: A = 357 ns, dlnL = 846
  (diagonal null). With a full red-noise covariance (γ = 4.09, free scale
  settling at 1.7×10⁵ — i.e. the chain red amplitude underpredicts
  J1909's low-frequency variance by ~400× in amplitude), the 7.9-yr
  sinusoid still gives dlnL = 61: the wiggle is *sharper* than J1909's
  chain red spectrum — a genuine quasi-periodic feature of J1909's
  residuals, cause unknown (backend/jump aliasing and unmodeled
  systematics are candidates; J1909's tim backend flags exist on disk
  for a follow-up).
- B1937 (2202 ns, phase ≈ −π vs J1909) and B1855 (516 ns) have their own
  large slow drifts at unrelated phases — the known wander, not a wave.
- Weight-leakage check: corr(B1937+B1855 GLS weight fraction, wave
  phase) = 0.23 — the wave does not track the wander pair's weight.
  (corr with |M(t)| = 0.70 just reflects that bins where B1937/B1855
  dominate are noisier.)

**Retrospective:** the 14-epoch ULDM "6.7-yr peak" (P > span, dlnL 3.1
behind clock) was J1909's red-noise excursion all along — J1909 carries
~89% of the monopole weight, so its private wiggle printed straight onto
the common mode. The longer baseline didn't validate the peak; it
localized it to one pulsar and falsified the common-wave hypothesis.

### 3.5 ULDM: doubly excluded

Even setting the phase result aside, a 265-ns coherent common oscillation
at f = 4.0×10⁻⁹ Hz cannot be ultralight dark matter:
- Expected ULDM Earth-term amplitude at the local DM density
  (ρ₀ = 0.4 GeV/cm³, m ≈ 0.8×10⁻²³ eV): A = Ψ/(2πf) ≈ **35 ns**
  (Ψ = Gρ/πf² ≈ 8.8×10⁻¹⁶).
- 265 ns needs **ρ ≈ 60 × ρ₀ ≈ 23 GeV/cm³**, excluded by PPTA
  (ρ < 6 GeV/cm³ for m ≤ 10⁻²³ eV, 95%: Shannon et al. 2018, PPTA DR2)
  and by NANOGrav's own Ψ_c < 1.14×10⁻¹⁵ limit (Porayko & Postnov 2014,
  5-yr data; implied Ψ here ≈ 6.7×10⁻¹⁵).
So: not common (3.4), and not dark matter even if it were.

## 4. Interpretation

1. **The monopole-as-common-signal is falsified.** The ±350 ns / σ_c ≈
   269 ns "common mode" persists as *variance* but has no cross-pulsar
   covariance (A_m < 2 ns; J0437×J1909 correlation −0.25 vs +0.53
   predicted). It is J1909's private 271-ns excess — largely its
   quasi-periodic 8-yr excursion — amplified by 89% GLS weight, plus
   B1937/B1855's own large excesses. The clock-like *variance* signature
   (epoch-uncorrelated) is real; attributing it to an array-common process
   (clock, ephemeris, ULDM, systematics) was premature. The three-way
   ranking's "clock-like wins" result stands as a description of the
   *variance structure* (abrupt, epoch-uncorrelated) but the "common"
   part does not survive.
2. **The 7.9-yr wave is dead as a common signal** — it is J1909's private
   quasi-periodic excursion plus unrelated B1937/B1855 drifts. This closes
   the ULDM thread opened by the 14-epoch analysis: the "statistical tie"
   was J1909's red noise wearing a monopole costume. Doubly excluded
   (not common; 265 ns would need ~60× local DM density, ruled out by
   PPTA/NANOGrav bounds).
3. **The B1937/B1855 wander keeps its record** as the thing that fooled
   the HD template (14-epoch), the dipole template (annual), and the v1
   fit here (5185-ns HD runaway). With empirical per-pulsar variances it
   contributes no spatial component (global dlnL = 0). Its full-span
   correlation is −0.18, matching the wander investigation; the +0.94
   was window-local. Nothing here reopens it.
4. **Noise-model lesson (the big one):** chain red amplitudes underpredict
   binned low-frequency variance by large factors (B1937 ~10×, B1855 ~5×,
   J1909's red wants ×1.7×10⁵ in variance ≈ ×400 in amplitude). Any
   spatial fit that fixes per-pulsar noise at chain values *will*
   hallucinate spatial signals from mis-modeled variance — that is
   exactly what the v1 HD runaway (5185 ns) and the 14-epoch HD "detection"
   were. This sharpens the project's open question: why binned residuals
   carry ~10× the red variance the TOA chains predict. Until that is
   understood, no 4-pulsar (or 68-pulsar) spatial claim is trustworthy
   without empirical per-pulsar variances.

## 5. Caveats

- **White-noise convention**: the npz V field is used as white *variance*
  (convention B, matching all published notes in this project), though the
  binned err column it equals is plausibly a *sigma*. Red noise dominates
  the GLS weights either way (J1909 weight 88–89% under both conventions),
  so results are insensitive — but the absolute white scale is ambiguous
  in the data product. Flagged, not resolved.
- **Diagonal per-bin likelihood** ignores inter-bin red correlations in
  Stages 1–2; Stage 3(c) models them for the monopole series.
- **4 pulsars only**: 6 baselines. Monopole/dipole/HD separation is still
  fundamentally weakly constrained on subsets (see the unstable
  jackknives in §3.1); the full-data dlnL = 0 is the robust statement.
- **No 68-pulsar data on disk.** Getting it means downloading the NANOGrav
  15-yr release (public, Zenodo) *plus* per-pulsar noise models for the
  other 64 pulsars (chains not on disk) — a substantial project, not a
  download.
- J1909's 8-yr quasi-periodicity is unmodeled: if it is a systematic
  (e.g. backend-jump aliasing), it contaminates any J1909-dominated common
  mode at the ~100-ns level. Backend flags exist in the tim files for a
  targeted follow-up.
- As ever: archival-data analysis, no detection claims.

## 6. Open threads

- J1909's 8-yr quasi-periodicity: backend-flag vs wave-turning-point check
  (tim files on disk). If systematic, it contaminates any J1909-dominated
  common mode at the ~100-ns level.
- The 68-pulsar upgrade (needs data + 64 noise models) — but note the
  lesson of §4.4: without resolving the red-variance underprediction,
  more pulsars just means more mis-modeled variance to hallucinate with.
- The standing red-variance underprediction question — now the single
  biggest blocker in this whole real-data program.
- Re-analysis of the 14-epoch monopole ranking in light of §3.1: the
  "clock-like wins" result describes J1909-dominated variance structure,
  not an array-common process.
