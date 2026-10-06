# BEC optical-lattice tabletop glitch experiment — feasibility numbers

**Status:** exploratory / feasibility calculation. NOT a result, NOT a detection claim. Date: 2026-10-03.
**Question (round 3):** the proposal (`glitch_rise_and_bec_note.md` Part B) is specified; the literature mining (`bec_literature_mining_note.md`) confirmed no existing data and framed it as a time-resolved extension of Williams+2010. What it lacked was numbers an experimentalist could evaluate. This note computes them.

**Bottom line up front:** the experiment is **feasible, but the proposal's parameter ranges need correction in three places** — the lattice depth must come down ~50× (h×10 kHz → h×(50–250) Hz), the rotation steps down ~10× (±0.15ω⊥ → ±(0.005–0.05)ω⊥), and the vortex number at Ω=0.8ω⊥ is ~125, not 20–30. With corrected parameters there is a real operating window: τ_fast ~ 0.2–0.5 s, τ_slow ~ 3–15 s, separable at ≳10×, detectable in the Monte Carlo below. Per-subsystem verdicts in §11.

Reproducible script: `hidden_files/feasibility_calc.py` (BEC scales, barriers, crossovers). Two-exponential Monte Carlo results tabulated in §8.

---

## 1. Five corrections to the proposal's design parameters

| # | Proposal said | Corrected | Why |
|---|---|---|---|
| 1 | V₀ = 0 → h×10 kHz | **V₀ ∈ {0, 50, 100, 200, (400)} Hz** | Thermal creep needs ΔE_hop/k_BT ~ 5–12; at h×10 kHz the barrier is ΔE/k_BT ~ 5000 — vortices never hop (§4). h×10 kHz is also past the Mott crossover (no phase coherence). |
| 2 | δω ∈ ±0.15 ω⊥ | **δω ∈ ±(0.005–0.05) ω⊥** | Depinning crossover δω_c(V₀) = 0.007–0.03 ω⊥ across the useful V₀ range (§5); the old scan is almost entirely in the depinned/sliding regime at creep-relevant depths. |
| 3 | N_v ≈ 20–30 at Ω = 0.8ω⊥ | **N_v ≈ 125** (a_v ≈ 5.1 μm) | Feynman rule with centrifugal TF correction (§2). More vortices = better readout statistics; the 20–30 number belongs to Ω ≈ 0.3ω⊥. Kept Ω = 0.8ω⊥. |
| 4 | d_OL = 2–5 μm, free choice | **Recommend d_OL = 2.5 μm** | At d = 5 μm the useful V₀ ≈ 200 Hz is ~9 E_r (deep, coherence risk); at 2.5 μm it is ~2 E_r (safe). Incommensurate with a_v = 5.1 μm — acceptable (Kasamatsu simulated incommensurate cases; barrier computed for it). |
| 5 | δω > 0 and < 0 symmetric | **δω < 0 (spin-down) is the primary measurement** | Spin-up needs vortex *nucleation* at the edge (extra barrier, conflates creep with nucleation); spin-down only needs vortices to exit. Use δω > 0 for the asymmetry test, δω < 0 for the clean two-exponential. |

---

## 2. BEC scales (⁸⁷Rb, N = 2×10⁵, ω⊥ = 2π×20 Hz, ω_z = 2π×200 Hz)

| Quantity | Value |
|---|---|
| μ/h | 847 Hz (μ/k_B = 40.6 nK) |
| R⊥(Ω=0) / R_z | 22.2 μm / 2.22 μm |
| Peak density n₀ | 1.09×10²⁰ m⁻³ |
| Healing length ξ | 262 nm |
| T_c | 114 nK (operating T = 55–90 nK → T/T_c = 0.48–0.79) |
| E_r/h at d = 2.5 μm | 92 Hz (ξ/d = 0.105 — Reijnders–Duine regime) |
| Circulation quantum κ = h/m | 4.60×10⁻⁹ m²/s |

Vortex number (Feynman n_v = 2Ω/κ, centrifugal-corrected TF radii):

| Ω/ω⊥ | μ′/h (Hz) | R′ (μm) | N_v | a_v (μm) |
|---|---|---|---|---|
| 0.3 | 815 | 22.8 | 27 | 8.4 |
| 0.5 | 755 | 24.2 | 50 | 6.5 |
| **0.8** | **563** | **30.1** | **~125** | **5.1** |

Trap period 2π/ω⊥ = 50 ms sets the fast clock; the <1 ms step is safely sudden against it (§9).

---

## 3. τ_fast — the microscopic leg

Anchored to the Abo-Shaeer spin-down measurement (no lattice: single exponential, τ ~ 0.4–2 s, rate ×17 shorter for +60% T) and the mutual-friction form τ_fast ~ 1/(2Ωα) with α ~ 0.01–0.1:

| T (nK) | T/T_c | τ_fast (adopted) |
|---|---|---|
| 60 | 0.53 | ~1.0 s |
| 70 | 0.61 | ~0.55 s |
| 90 | 0.79 | ~0.20 s |
| 100 | 0.88 | ~0.13 s |

Scaling ~ (T/T_c)⁻⁴ (ZNG-like); systematic ±2×. **Crucially the experiment does not rely on this number:** the V₀ = 0 control run measures τ_fast in situ (single exponential — the Abo-Shaeer result reproduced). Falsifier #2 (§13) is exactly the statement that τ_fast(V₀ > 0) must equal this control value.

---

## 4. τ_slow — the pinning-creep leg (the central calculation)

**Barrier derivation (stated assumptions).** Square lattice V(x) = V₀[sin²(πx/d)+sin²(πy/d)] modulates the TF density by ~V(x)/μ. Vortex core energy per unit length ≈ (πξ²)(μn₀/2); hopping one site crosses a saddle of height ΔV ≈ V₀/2, so the pinning energy per unit length is

u_p ≈ (πξ²n₀/2)·V₀,

and for the short pancake line (L_z = 2R_z = 4.4 μm ≈ 17ξ) whole-line hopping gives ΔE_hop = u_p·L_z. Attempt rate from the pinning-well curvature: ω_pin = √[u_p(2π/d)²/m_l], m_l = πρξ²ln(R⊥/ξ) the line mass per unit length, τ₀ = 1/ω_pin. Then τ_slow = τ₀·exp(ΔE_hop/k_BT).

| V₀ (Hz) | ΔE_hop/k_B (nK) | τ₀ (ms) |
|---|---|---|
| 50 | 126 | 2.5 |
| 100 | 251 | 1.8 |
| 150 | 377 | 1.4 |
| 200 | 502 | 1.2 |
| 400 | 1004 | 0.9 |
| 1000 | 2510 | 0.6 |

**τ_slow = τ₀·exp(ΔE_hop/k_BT), in seconds:**

| V₀ (Hz) | T=60 nK | T=70 nK | T=90 nK | T=100 nK |
|---|---|---|---|---|
| 50 | 0.020 | 0.015 | 0.010 | 0.009 |
| 100 | 0.11 | 0.063 | 0.028 | 0.022 |
| 150 | 0.76 | 0.31 | 0.094 | 0.062 |
| 200 | 5.3 | 1.6 | 0.33 | 0.19 |
| 400 | 1.6×10⁴ | 1.5×10³ | 61 | 20 |
| 1000 | 8×10¹⁴ | 2×10¹² | 7×10⁸ | 4×10⁷ |

**The key finding:** the proposal's "U_p/k_BT ~ 10 → τ_slow ~ seconds" was computed with the per-unit-length barrier, omitting ×L_z. The real barrier is ~40× larger in thermal units. The observable creep window (τ_slow ~ 0.3–15 s) is **V₀ ≈ h×(100–250) Hz at T ≈ 55–70 nK** — not h×10 kHz. At h×1 kHz the vortices are frozen on any laboratory timescale (τ_slow ~ 10⁸ s); that point is at most a "perfectly pinned" limiting case, and at h×10 kHz the system is past the Mott crossover anyway (no phase coherence — the point is dropped, not just frozen).

**Sweet-spot operating point:** V₀ = h×200 Hz, T ≈ 55–65 nK, d = 2.5 μm → τ_slow ≈ 5–15 s, τ_fast ≈ 0.5–1.0 s, separation ~5–13× (marginal-to-good; see §8). Colder (T/T_c ≲ 0.5) improves separation exponentially until quantum tunneling takes over — which would itself be a result (quantum creep floor), flagged as a caveat in §10.

---

## 5. Depinning crossover δω_c(V₀)

Force balance per unit length: Magnus drive f_M = ρκr·δω against max pinning force f_p = 2πu_p/d. With u_p from §4 and ρκ = nh, the density cancels:

δω_c = π²ξ²V₀/(dhr).

(r = 15 μm, mid-cloud; δω_c ∝ 1/r so the edge depins first — the crossover is a front, not a sharp global value.)

| V₀ (Hz) | δω_c (d=2.5 μm) | δω_c (d=5 μm) |
|---|---|---|
| 50 | 0.0072 ω⊥ (0.90 rad/s) | 0.0036 ω⊥ |
| 100 | 0.014 ω⊥ (1.8 rad/s) | 0.0072 ω⊥ |
| 150 | 0.022 ω⊥ (2.7 rad/s) | 0.011 ω⊥ |
| 200 | 0.029 ω⊥ (3.6 rad/s) | 0.014 ω⊥ |
| 400 | 0.058 ω⊥ (7.2 rad/s) | 0.029 ω⊥ |

**Design rule:** creep steps must satisfy δω ≲ δω_c(V₀). Recommended step set: δω ∈ {0.005, 0.01, 0.02}ω⊥ for the creep measurement; {0.05, 0.1}ω⊥ to map the depinning/sliding crossover (Kasamatsu's dynamical phases in the time domain — a result in its own right). The crossover *sweeps through the scan* as V₀ varies, which is the ideal experimental handle: at fixed δω = 0.01ω⊥, V₀ = 50 Hz is depinned while V₀ = 200 Hz is pinned.

---

## 6. Signal size per step

For δω = 0.01ω⊥ = 1.26 rad/s: the vortex-pattern rotation rate changes by ΔΩ_c ~ 1.26 rad/s (full transfer). Vortex-number change (spin-up) ΔN_v = (2A/κ)·δω ≈ 1.5 — too small to count reliably, **but the observable is Ω_c(t), not N_v**: the pattern angle accumulates, sweeping ~3.8 rad in 3 s, ~19 rad over a 15 s creep. The per-image angular resolution needed is ~1° — trivially met with ~125 resolved vortices (centroid-limited orientation noise ~0.2°, see §7).

---

## 7. Readout: stroboscopic in-situ imaging

Destructive absorption imaging along z, ~1 μm resolution (demonstrated: Abo-Shaeer counted ~130 vortices; Freilich tracked single vortices in real time). Time series rebuilt stroboscopically: prepare → step (t=0) → hold t → image; t log-spaced 20 ms → 30 s (25 points); ~15 runs/point.

Noise budget per point: single-run Ω_c noise ~0.05–0.2 rad/s (centroid-limited, depending on point spacing) → ~0.05 rad/s after 15-run averaging. Dominant *systematic*: run-to-run vortex-number/equilibrium fluctuations — mitigated by the V₀=0 control and by randomizing run order. Per-point SNR for the δω = 0.01ω⊥ step: ~25.

---

## 8. Two-exponential detectability (Monte Carlo)

Model Ω_c(t) = S[1 − a_f e^{−t/τf} − a_s e^{−t/τs}], S = 1.26 rad/s, 25 log-spaced points (20 ms–30 s), σ = 0.05 rad/s/point, 200 trials per case; detection = F-test of 2-exp vs 1-exp at 3σ.

- **Nominal (τf=0.2 s, τs=3.0 s, a_s=0.8):** slow arm detected in 98% of trials; τ_s recovered as 3.03 ± 0.39 s; a_s to ±0.05.
- **Minimum slow amplitude:** a_s ≳ 0.2–0.3 for reliable detection (82% at 0.2, ~100% at ≥0.3).
- **Minimum separation:** τ_s/τ_f ≳ 10 for reliable detection (84% at 10×, 24% at 5×, ~0% at 3×).

**Design requirement: τ_slow/τ_fast ≳ 10 and slow fraction ≳ 0.3.** The sweet spot (§4) gives 5–13× — achievable but it demands the cold end (T/T_c ≲ 0.55) and V₀ ≈ h×200 Hz. The amplitude split is the largest model uncertainty: the elastic estimate gives A_fast/A_total ~ x_el/d ~ few %, but the two-fluid picture (normal fraction ~20–30% at T/T_c ~ 0.6 responding promptly via mutual friction) suggests A_fast ~ 0.2–0.5. **The experiment measures this** — and the pinned fraction vs V₀ is itself a result (the lab analog of the NS crustal superfluid participation fraction). The V₀=0 control (A_fast = 1 by construction) anchors the fit.

---

## 9. Heating and the step

- **Spontaneous emission** (1064 nm, detuning huge): < 1 nK/s at these depths — negligible over 30 s holds.
- **The step itself** is a phase/frequency jump of the lattice beams (<1 ms), no intensity change → no direct heating.
- **Band excitation:** δω ~ 1–3 rad/s ≪ band gap (~2π×92 Hz ≈ 580 rad/s at d=2.5 μm) → no interband transitions. (The 1 ms step *time* is sudden only against vortex/trap dynamics at 50 ms, which is the intent.)
- **Non-adiabatic vortex excitation:** the sudden step rings Tkachenko/phonon modes at ~10–100 ms — inside the fast leg, not a background; it is part of the prompt response being measured.
- **Verdict: heating is not a constraint.** Three-body loss at peak density sets a ~15–40 s condensate lifetime — a watch item for the longest holds (t > 10 s points), mitigated by lifetime characterization, not a showstopper.

---

## 10. Run-time budget

Per (V₀, δω, T) curve: 25 time points × 15 runs = 375 runs; at ~30 s BEC cycle ≈ 3.1 h. Priority scan — V₀ ∈ {0, 100, 200} Hz × δω ∈ {−0.01, +0.01}ω⊥ × T ∈ {65, 90} nK = 12 curves ≈ **37 h ≈ one week of beam time**. Full scan (5 V₀ × 5 δω × 2 T) ≈ 3× that. Feasible as a dedicated campaign; the priority scan alone tests all four falsifiers.

---

## 11. Error budget (ranked)

1. **Barrier prefactor (dominant):** ΔE_hop enters exponentially; the u_p estimate is O(1)-uncertain (geometry, density profile, kink vs whole-line hopping) → τ_slow uncertain by ~10²–10³× at fixed (V₀,T). **Mitigation: the experiment scans (V₀,T), it does not target a point** — the *scaling* τ_slow ∝ exp(const·V₀/T) is the robust prediction, and its slope measures the true barrier.
2. **τ_fast T-scaling:** ±2× systematic on the adopted (T/T_c)⁻⁴; irrelevant to the verdict because the V₀=0 control measures τ_fast in situ.
3. **Amplitude split A_fast/A_slow:** order-of-magnitude model uncertainty (§8); measured, not assumed. MC says a_s ≳ 0.3 needed — if the true slow fraction is smaller, the depinning scan (larger δω) raises it.
4. **V₀ calibration:** ~5–10% via Kapitza–Dirac diffraction — subdominant against (1).
5. **T calibration:** ~10% via condensate fraction — folds into (1)'s scan.
6. **Three-body lifetime:** watch item for t > 10 s points (§9).
7. **Quantum-tunneling floor:** if τ_slow saturates T-independent at the cold end, the thermal-scaling test is cut off — but that *is* quantum creep, a publishable result in its own right.

---

## 12. Per-subsystem go / no-go

| Subsystem | Verdict |
|---|---|
| BEC production + spin-up to Ω=0.8ω⊥ | **GO** — routine (JILA/MIT heritage) |
| Rotating square OL, d=2.5 μm, V₀ ≤ 400 Hz | **GO** — Williams+2010 demonstrated rotating-OL hardware; EOM/AOM rotation is standard |
| <1 ms rotation-rate step | **GO** — RF phase/frequency switching, no intensity transient |
| Stroboscopic in-situ readout, 25 pts × 15 runs | **GO** — demonstrated techniques; ~37 h for the priority scan |
| τ_fast measurement (0.1–1 s) | **GO** — well resolved; V₀=0 control anchors it |
| τ_slow in the 0.3–15 s window | **GO with corrected parameters** — requires V₀ ≈ h×(100–250) Hz and T/T_c ≲ 0.7; the proposal's h×10 kHz is ~50× too deep (frozen + Mott) |
| Two-exponential separation (≳10×) | **MARGINAL → GO at the cold end** — needs T/T_c ≲ 0.55, V₀ ≈ h×200 Hz; MC confirms detectability there |
| Depinning crossover δω_c(V₀) | **GO** — predicted in-scan (0.007–0.06 ω⊥); maps Kasamatsu's phases into the time domain |
| Heating / lifetime | **GO** — heating negligible; three-body lifetime a watch item for the longest holds |
| V₀=0 control (single exponential) | **GO** — reproduces Abo-Shaeer 2002 |

**Overall: GO with the corrected parameter set in §1.** The experiment is a time-resolved extension of demonstrated apparatus, needs ~1 week of beam time for the priority scan, and every subsystem is either demonstrated or a bounded extrapolation.

---

## 13. The four falsifiers, mapped to measurements

1. **No timescale separation** → the 2-exp vs 1-exp F-test (§8) at every (V₀,T): if 1-exp always wins, the slow arm doesn't exist here.
2. **τ_fast depends on V₀** → compare τ_fast(V₀>0) against the V₀=0 control value: any V₀-trend at fixed T kills the "prompt = microscopic" leg.
3. **τ_slow doesn't scale with the barrier** → the (V₀,T) scan must show log τ_slow linear in V₀/T with the barrier slope; flat = not pinning creep.
4. **Prompt ≠ independent microscopic damping** → V₀=0 step response and vortex-lattice equilibration rate give the independent τ_fast; disagreement with the V₀>0 prompt leg falsifies "prompt coupling sees friction" here.

---

## 14. Assumptions (stated)

TF regime; whole-line hopping (L_z ≈ 17ξ justifies rigid-line approx; kink corrections are O(1)); u_p = (πξ²n₀/2)V₀ with geometric O(1) = 1; τ₀ = 1/ω_pin from well curvature; τ_fast T⁻⁴ scaling ±2×; per-point σ = 0.05 rad/s after 15-run averaging; 30 s BEC cycle; three-body K₃ = 6×10⁻⁴² m⁶/s; no quantum-tunneling contribution above T/T_c ≈ 0.45. Research label: **completed-toy** (reproducible calculation from published formalisms + standard BEC theory) — not validated against data.

---

## 15. Bottom line for the thread

The proposal survives contact with the numbers, but only after three corrections that change what gets built: the lattice runs **~50× shallower** than proposed (hundreds of Hz, not 10 kHz), the steps **~10× smaller** (±0.01ω⊥, not ±0.15ω⊥), and the cloud holds **~125 vortices**, not 20–30. The operating window is real but not generous — it lives at the cold end (T/T_c ≲ 0.55) and demands the (V₀,T) scan be adaptive, because the barrier prefactor uncertainty (§11.1) means the first cool-down finds the window empirically rather than hitting it first try. If built to this spec and the §13 signatures appear, it becomes the first system with both branches of R measured in one tunable apparatus. If the falsifiers trigger, pinning alone doesn't guarantee the split — also publishable, and also an answer.
