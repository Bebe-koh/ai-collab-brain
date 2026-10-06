# A blind-spot-free observable for Kerr/CS polarimetry: the calibrator-differential transient statistic
Date: 2026-10-03. Status: exploratory (pen-and-paper theory). No observational claims.
Patched 2026-10-03 with round-2 synthetic-test corrections (marked [C2];
see `blindspot_synthetic_test_note.md`).
Prereads: `closure_phase_derivation_note.md` (+2026-09-24 addendum), `eht_kerrcs_null_bound_note.md`.

## 0. Problem

The Kerr/CS program searches for a dynamical-pseudoscalar-θ slip that rotates
every cross-hand visibility,
V^RL → V^RL·e^{−2iΔχ(t)}, V^LR → V^LR·e^{+2iΔχ(t)}, with
Δχ(t) = πγ·[1+tanh((t−t0)/τ)] (k=1, Reading A verified 2026-09-24; τ=46.9 s for
Sgr A*, 18.0 h for M87*). Two structural problems were found on 2026-09-25:

- **(P1) Exact blind spot.** The closure-phase step observable measures the
  *permanent* phasor offset |1−e^{−24iπγ}| = 2|sin(12πγ)| and is exactly blind
  at γ=k/12 (k integer).
- **(P2) Exact degeneracy.** A synchronized all-station R–L gain jump
  ψ_i→ψ_i+δ produces common-mode steps (+3δ on RL, −3δ on LR) identical to a
  slip with Δχ=−δ/2. This confounder killed the EHT run (no calibrator scans
  in the public release).

This note derives one observable that resolves both. Headline result:

> **The k/12 blind spot is a property of endpoint-comparing (step-amplitude)
> statistics, not of the signal.** A transient-resolving matched filter has no
> blind spot in *detection*. The synchronized-jump degeneracy is *exactly*
> broken — provably unbreakable from target-only closure data — by a
> calibrator-differential construction.

## 1. Governing equations

Slip (verified transform, §4 of derivation note), per baseline ij:

    V^RL_ij(t) → V^RL_ij(t)·e^{−2iΔχ(t)},   V^LR_ij(t) → V^LR_ij(t)·e^{+2iΔχ(t)}   (1)
    Δχ(t) = πγ·[1+tanh((t−t0)/τ)],   Δχ_max = 2πγ  (k=1).                        (2)

Closure phases ψ^RL_ijk = arg(V^RL_ij V^RL_jk V^RL_ki) shift by −6Δχ(t) on every
triangle (global-slip morphology: same U(t) on all baselines — assumption A1);
ψ^LR_ijk shifts by +6Δχ(t).

Station cross-hand phases enter as (derivation note §5, eq. 4):
ψ^RL_ijk ⊃ +(ψ_i+ψ_j+ψ_k), ψ^LR_ijk ⊃ −(ψ_i+ψ_j+ψ_k).
A synchronized jump ψ_i→ψ_i+δ ∀i gives Δψ^RL_ijk=+3δ, Δψ^LR_ijk=−3δ, ∀ triangles.

Stacked phasors (per the EHT pipeline: inverse-variance weighted triangle
phasors after circular-mean derotation):
S^RL(t) → S^RL(t)·e^{−6iΔχ(t)} (slip) or ·e^{+3iδ(t)} (jump);
S^LR(t) → S^LR(t)·e^{+6iΔχ(t)} (slip) or ·e^{−3iδ(t)} (jump).                (3)

## 2. Why (P1) exists — and what it is really about

Define the differenced channel D(t) = S^RL(t)·conj(S^LR(t)) (EHT pipeline's
primary observable). Under the slip, D → D·e^{−12iΔχ(t)}; total excursion
−12·Δχ_max = −24πγ. The *asymptotic* (t→±∞) phasor changes by the factor
e^{−24iπγ}. Any statistic built only from the before/after states sees the
step amplitude

    A(γ) = |1 − e^{−24iπγ}| = 2|sin(12πγ)|,                                  (4)

with exact zeros at γ=k/12. At those couplings the initial and final phasors
coincide, so endpoint-comparing statistics are *exactly* blind. This is a
theorem about 2π-periodic observables, not a pipeline artifact. (Figure, left
panel.)

Crucially, the *path* is never trivial: during the ramp the phasor winds
continuously by −24πγ. The transient signature in the finite-differenced
series e(t)=D(t+Δt)·conj(D(t)),

    s_γ(t) = exp(i[Φ(t+Δt)−Φ(t)]),  Φ(t) = −12πγ[1+tanh((t−t0)/τ)],          (5)

satisfies s_γ(t)≠1 during the ramp for *every* γ≠0. Its signal energy
E(γ)=Σ_t|s_γ(t)−1|² is smooth and strictly positive for all γ>0 (verified
numerically; e.g. E(1/12)=2.73, E(0.15)=8.34 at 10-s sampling). **Detection via
the transient therefore has no blind spot.** (Figure, middle panel.)

Resolution condition. The transient is resolvable only if the ramp is sampled.
**[C2 — round-2 correction, 2026-10-03.]** The "blind spot returns" phrasing in
the original paragraph is refined: for Δt≫τ the blind spot does not return
deterministically. What happens is a **sample-phase lottery** — detection is
blind only when the full 2πk winding falls inside a single inter-sample
interval (then E→~0.04, as in the original demo at Δt=200 s); if a sample
lands near the ramp center, the two straddling sample pairs each see ~π of
winding (r≈−1, an O(1) transient) and detection proceeds normally (synthetic
grid at Δt/τ=4.26: 3 of 4 grid offsets detected). Heuristic: P(detect) ~ 2τ/Δt
(order-of-magnitude, from a 4-offset grid). Design rule: Δt ≲ τ guarantees
resolution; coarser sampling trades detection probability per the lottery, it
does not deterministically re-blind. For Sgr A* (τ=46.9 s, Δt=10 s) this is
moot; for M87* (τ=18 h) it holds trivially.

Estimation caveat (honest). Detection ≠ estimation. The transient *shapes* at
γ and γ+1/12 are 99.7% correlated (mean-subtracted), because the extra 2π of
winding is spread thinly across the ramp.
**[C2 — round-2 correction, 2026-10-03.]** The practical ambiguity is much
weaker than the original paragraph suggested. The alias template carries 2×
the amplitude (1.33× at γ=0.25), and amplitude is well measured — so the
correct estimator, the *amplitude-aware* least squares
χ²(γ_t,t₀)=Σ_t|r(t)−1−u(t;γ_t,t₀)|² with the template at natural amplitude
(the Eq. 10 normalization discards amplitude and is flat in the linear
regime — use the LS form in practice), picks the true γ in 100% of synthetic
realizations at per-sample σ∈{0.02,…,0.4} with zero alias picks. Confusion
appears only as scatter at very low S/N, never as alias-locking. Phase
unwrapping through the ramp remains the principled ambiguity-lifter at high
S/N (synthetic: γ̂=0.0809±0.0006 at σ=0.05, within 10% up to σ=0.2; the
per-sample |ΔΦ|<π condition holds — max 0.66 rad at γ=1/12), but it is a
refinement, not a rescue. Net, corrected: the new observable converts an
*exact* blind spot into (a) no detection gap and (b) an estimation problem
with no practical aliasing wherever detection itself is significant.
Exclusion curves have no holes.

## 3. Why (P2) cannot be fixed with target-only closure data (proof)

From (3): the slip maps (S^RL,S^LR) → (S^RL·e^{−6iΔχ(t)}, S^LR·e^{+6iΔχ(t)});
the synchronized jump maps (S^RL,S^LR) → (S^RL·e^{+3iδ(t)}, S^LR·e^{−3iδ(t)}).
With 3δ(t) ≡ −6Δχ(t) these maps are *identical* as transformations of the
observables. Hence **no function of target-only closure phasors — however
clever — can separate a synchronized jump from a slip.** The degeneracy is
mathematically exact, not a pipeline limitation. Breaking it requires either
(a) additional data (calibrators), or (b) observables outside the closure
set. This note takes route (a); §7 sketches a conditional route-(b).

(Note: the *time profiles* differ — tanh vs Heaviside — so a transient
template *does* distinguish an ideal instantaneous jump from the slip. But
real instrumental jumps have unknown profiles and the EHT background is
systematics-dominated; profile shape is corroborating evidence, not a
principled degeneracy-breaker. The differential construction below is.)

## 4. Proposed observable: calibrator-differential transient statistic

Form the same differenced channel for the target and for an interleaved
calibrator: Q_tgt(t)=S^RL_tgt·conj(S^LR_tgt), Q_cal(t)=S^RL_cal·conj(S^LR_cal).
Define the differential

    R(t) = Q_tgt(t) / Q_cal(t̃(t)),                                           (6)

with t̃(t) the calibrator time interpolated to the target timestamp
(same processing — stacking, derotation — applied to both sources).

Slip (target only):  R → R·e^{−12iΔχ(t)}.            (signal preserved)      (7)
Jump (both sources): R → R·e^{+6iδ(t)}·e^{−6iδ(t̃)} ≈ R. (jump cancels)       (8)

The cancellation in (8) is exact when δ(t)=δ(t̃) — i.e. when the jump is
*sampled* by calibrator scans. **[C2 — round-2 correction, 2026-10-03.]** A
jump occurring *between* calibrator scans (mid-gap) is unobservable in the
calibrator data, and at realistic interleaved cadence the differential gives
no suppression at all (synthetic: 60-s scans every 300 s → residual step
1.97 of 2.00, ×1 suppression, spurious matched-filter detections at 100%;
every 120 s → ×7 suppression, residual 0.28, still spuriously detected).
Jumps *within* calibrator scans are suppressed ×13–17 and stay silent. So the
"residual floor" is not a floor at all for mid-gap jumps — they pass through
unsuppressed. The degeneracy-breaking is exact for *sampled* jumps; for
mid-gap jumps the defense is the veto chain (§6), which must be treated as
primary, not backup: a calibrator-only step search sees the mid-gap jump as
an inter-scan step. The calibrator's intrinsic source phase is slowly varying
and is removed by the final differencing step.

Final statistic: r(t) = R(t+Δt)·conj(R(t)), matched-filtered against the
*exact nonlinear* template

    s(t; γ_t, t0) = exp(−12iπγ_t·[tanh((t+Δt−t0)/τ) − tanh((t−t0)/τ)]),       (9)

    Z(γ_t,t0) = |Σ_t r(t)·conj(s(t;γ_t,t0))| / √(Σ_t|s|²/2).                 (10)

No small-angle linearization anywhere: at γ_t=k/12 the template winds by
exactly −2πk across the ramp and is a distinctive, non-degenerate signature.
Per §2 (as corrected [C2]), detection has no blind spot wherever the ramp is
resolved; coarser sampling gives the sample-phase lottery, not a hard blind
spot.
**[C2]** For *estimation*, use the amplitude-aware least-squares form
χ²(γ_t,t₀)=Σ_t|r(t)−1−u(t;γ_t,t₀)|² with the template at natural amplitude,
not the Eq. 10 normalization, which discards amplitude information and is
flat in the linear regime (round-2 synthetic: zero alias picks with the LS
form at per-sample σ≤0.4; see §2 estimation caveat).

Practical variant. If the calibrator is weakly polarized (noisy Q_cal), replace
division by jump-subtraction: estimate δ̂(t) from the calibrator's closure
phases (or parallel-hand data), form Q̃_tgt(t)=Q_tgt(t)·e^{−6iδ̂(t)}, then
difference and template-match. Same cancellation, better noise behavior.

## 5. Gamma dependence and zeros of the new observable

- Detection response: ∝ √E(γ), smooth, E(γ)>0 ∀γ>0. **No zeros at γ=k/12.**
  (Old: exact zeros, Eq. 4.)
- The only exact "blind" point is γ=0 (the null) — trivial.
- **[C2]** Unresolved limit Δt≫τ: *sample-phase lottery*, not a deterministic
  blind-spot return — blind only when the full 2πk winding falls in one
  inter-sample interval; heuristic P(detect) ~ 2τ/Δt.
- **[C2]** Estimation: no practical aliasing with the amplitude-aware LS
  estimator (zero alias picks at per-sample σ≤0.4); the 99.7% shape
  correlation is real but the alias template's 2× amplitude disfavors it.
  Unwrapping lifts the residual ambiguity at high S/N.
- **[C2]** Jump response: identically zero for *sampled* jumps (exact
  cancellation, Eq. 8); mid-gap jumps at realistic interleaved cadence pass
  through unsuppressed (×1 at 300-s cadence) — the veto chain is the primary
  defense there.

## 6. Null model, vetoes, falsifiability

Null model: r(t) = (target intrinsic variability + noise)/(calibrator
intrinsic + noise), no tanh transient. Surrogates via circular time-shifts of
r(t) (same as EHT pipeline), look-elsewhere corrected over (γ_t,t0).

Vetoes (a candidate must survive all). **[C2]** The first veto is the *primary*
defense against instrumental jumps (the differential cannot suppress mid-gap
jumps — §4); the rest are cross-checks:
- **Calibrator-only step search (PRIMARY jump veto).** Search Q_cal(t) alone
  for inter-scan steps. Any calibrator step flags the surrounding gap as
  contaminated and excludes it from the matched filter, regardless of what
  R(t) shows. A mid-gap jump is visible here as an inter-scan step even though
  the differential cannot correct it.
- Swapped differential (calibrator as "target"): any signal here = instrumental.
- RR/LL closures and the RL+LR sum channel (slip-invariant): steps here veto
  as gain glitches/structure (per derivation note §5).
- Multi-band achromaticity: identical −12Δχ(t) at 86/230/345 GHz. A λ²-scaling
  step is Faraday rotation, not θ — rules the model out, not just the event.
- Sign/rate consistency: the slip winding direction is fixed by the model;
  instrumental jumps are random-sign.

What would rule the model out (not just bound γ):
(i) transient detections scaling as λ² across bands; (ii) coincident
transients in the swapped differential; (iii) transients in total intensity
(RR/LL); (iv) a null at the computed transient sensitivity → excludes γ over
a *continuous* range (no k/12 holes), for the assumed global morphology.

## 7. Auxiliary discriminator (conditional): leakage-interference amplitude modulation

RIME: V^RL_ij,obs = g_R,i g_L,j^*·P_ij·[e^{−2iΔχ(t)} + ε_ij], with ε_ij the
*residual* (post-D-calibration) leakage ratio. Under the slip the bracket's
*amplitude* |e^{−2iΔχ}+ε_ij| modulates as Δχ sweeps (depth ∼2|ε_ij|); under a
pure-phase jump the amplitude is exactly unchanged (|g_R,i| invariant, and an
amplitude glitch would trip the RR/LL veto). So *cross-hand amplitude*
time series carry a slip-vs-jump signature — from target data alone. This is
strictly auxiliary: it needs significant, known residual leakage ε_ij per
baseline and is vulnerable to intrinsic source variability. Included for
completeness, not as the primary observable.

## 8. Data requirements

1. **Interleaved calibrator scans — required.** The missing piece in the public
   Sgr A* release. Calibrator should be bright and polarized (3C 279,
   J1924-2914, NRAO 530); use ≥2 calibrators for A3 consistency. **[C2]**
   Cadence: as fast as operations allow — but the honest requirement is not
   "fast enough to interpolate" (mid-gap jumps are unsuppressed at *any*
   realistic cadence: ×1 at 300-s, spurious detections even at ×7/120-s); it
   is "fast enough that the calibrator-only step search resolves jumps as
   inter-scan steps and the vetoed data fraction stays affordable". Faster
   cadence also shrinks each corrupted window. The veto chain (§6) is the
   primary jump defense; the differential handles only sampled jumps.
2. **Sampling Δt ≲ τ/5** to resolve the transient (10-s dumps suffice for
   Sgr A*'s 46.9 s; M87*'s 18 h is trivially resolved but red-noise-limited).
   **[C2]** Coarser sampling does not deterministically re-blind — it gives
   the sample-phase lottery, P(detect) ~ 2τ/Δt (heuristic); budget
   accordingly.
3. **Multi-band (86/230/345 GHz)** for the achromaticity/Faraday discriminator
   — needed for *identification*, not for the blind-spot or degeneracy fixes.
4. **ngEHT**: helps (more stations, faster cadence, longer tracks, better S/N)
   but is not required by the construction.
5. **[C2] Analysis: estimate with the amplitude-aware least squares**
   χ²(γ_t,t₀)=Σ_t|r(t)−1−u(t;γ_t,t₀)|² (template at natural amplitude), not
   the Eq. 10 amplitude-normalized matched filter, which discards amplitude
   and is flat in the linear regime. Detect with the max-over-grid matched
   filter and empirical FPR from circular-shift null surrogates
   (look-elsewhere corrected), as in the EHT pipeline.

## 9. Assumptions and limits (not derived here)

- (A1) Global-slip morphology: same Δχ(t) on all baselines (inherited from the
  derivation note; a localized slip needs source modeling).
- (A2) tanh profile and τ (46.9 s / 18.0 h) are model inputs, asserted not
  derived — same caveat as the derivation note §8.
- (A3) Calibrator has no intrinsic slip-like transient on the τ timescale
  (mitigated: use ≥2 calibrators, require consistency; AGN variability is
  broadband, not a 46.9-s tanh).
- (A4) Instrumental jumps are station-based, hence common to target and
  calibrator (true by construction of the RIME).
- (A5) γ remains unit-free (θ kinetic term unnormalized); a detection still
  cannot be mapped to lab g_aγ bounds until the normalization is fixed.
- (A6) Quantitative sensitivity needs real closure-phase noise propagation
  (same open item as derivation note §7.5); the E(γ) curves here are noiseless
  signal energies, not detection thresholds.

## 10. Bottom line

Two exact results and one practical construction:

1. **Blind spot demoted.** |sin(12πγ)| blindness at γ=k/12 is a property of
   endpoint-comparing statistics. The transient signature s_γ(t) (Eq. 5) is
   nontrivial for every γ≠0; a matched filter with the exact nonlinear
   template has no detection blind spot wherever the ramp is temporally
   resolved (Δt≲τ; verified numerically and synthetically, 97–100% detection
   at every k/12). **[C2]** Coarser sampling gives a sample-phase lottery
   (P(detect) ~ 2τ/Δt), not a deterministic blind-spot return.
2. **Degeneracy broken — provably unbreakable without new data.** No
   target-only closure observable can separate a synchronized R–L jump from a
   slip (identical maps, §3). The calibrator-differential R(t) (Eq. 6) cancels
   the jump exactly (Eq. 8) while preserving the slip (Eq. 7) — **[C2]** for
   *sampled* jumps. Mid-gap jumps at realistic interleaved cadence pass
   through unsuppressed; there the veto chain (§6) is the primary defense.
3. **Honest residuals.** **[C2]** Estimation has no practical aliasing with
   the amplitude-aware LS estimator (use it, not the Eq. 10 normalization);
   the tanh/τ inputs remain asserted; exclusion curves from a null have no
   k/12 holes.

Predictions (units): R(t) dimensionless; template phase −12πγ[1+tanh((t−t0)/τ)]
in radians, τ in seconds; γ dimensionless. A slip at coupling γ produces a
transient in arg(r(t)) of total winding −24πγ radians over ∼2τ, present in the
target differential and absent in the swapped differential, identical across
bands (achromatic) as opposed to λ² (Faraday).

## Files
- `blindspot_work/demo.py`, `demo2.py`, `demo3.py` (numerical checks)
- `blindspot_work/blindspot_fig.png` (figure: old zeros vs new signal energy vs resolution condition)
- Data files: `demo_data.npz`, `demo2.npz`
- Round-2 synthetic stress test: `blindspot_synthetic_test_note.md`;
  `blindspot_work/synth_test.py`, `blindspot_work/replot.py`,
  `blindspot_work/synth_results.json`, figures `synth_figA/B/C/D/E.png`
- Observing-requirements memo: `observing_requirements_memo.md`
