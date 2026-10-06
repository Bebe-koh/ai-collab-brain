# Tunneling rate for Kerr pseudoscalar phase slips — derived, then falsified
**Date:** 2026-10-05 · **Status:** exploratory (completed-toy). No observational claims.
Derives the 2π phase-slip tunneling rate from the field-theory action on Kerr
— the normalization the quantum-extension note (2026-10-03) flagged as "never
derived" — instead of stipulating a potential and tuning it to 230 GHz.

**Bottom line up front:** the instanton rate is derived in closed form, and it
*excludes* tunneling as the origin of the slips by 50–250 orders of magnitude.
The slips must be classical (driven). The discrete-slip phenomenology —
55.56° quantization, Poisson counting — survives as mechanism-independent.
Three structural results fall out along the way (Pontryagin charge, winding
energetics, statistics correction), plus a new consistency bound f ≪ M_pl (no practical constraint — §5 corrects an
earlier dimensional error); the θ sector is instead cornered into
~10 eV ≲ f ≲ ~10¹⁴ eV by lab bounds below and drive-torque plausibility above.

## 0. Conventions and inherited assumptions

- Kerr background fixed (no backreaction — consistency checked in §5).
- Complex scalar Φ = (f/√2)e^{iθ}; canonical φ_c = fθ (mass dimension 1).
- Minimal periodic completion of the phase dynamics:
  S = ∫d⁴x√(−g)[½(∂φ_c)² − μ⁴(1−cos(φ_c/f))].
  μ is free; f is free. (The thread's θFF̃ coupling sets the EVPA observable
  Δχ = 2πγk per 2π slip; it does not enter the rate.)
- Homogeneous mode φ_c(t) coherent over patch r ∈ [r₊+δ, r_c], r_c = 10M
  (emission-region scale). Global-slip coherence is inherited from the R(t)
  program's morphology assumption.
- Benchmark: Sgr A*, M = 4.3×10⁶M☉, a₊ = 0.9; asserted slip cadence
  τ_slip = 46.9 s (still asserted — §6).
- Natural units ħ = c = 1 throughout; M☉ = 1.12×10⁶⁶ eV.

## 1. Effective action of the homogeneous mode (derived)

For φ_c(t): S = ∫dt[½M_φφ̇_c² − V̄(φ_c)],
  M_φ = ∫√(−g)(−g^{tt})d³x,   V̄ = μ̄⁴(1−cos(φ_c/f)),   μ̄⁴ = μ⁴V_patch.

On Kerr (Boyer–Lindquist), √(−g)(−g^{tt}) = sinθ[(r²+a²)²−a²Δsin²θ]/Δ.
Numerical integration (geo_integrals.py) gives, in M = 1 units:

| a₊ | Ī ≡ M_φ/M³ (r_c=10M, δ_r=10⁻⁶) | r_c scaling |
|---|---|---|
| 0.0 | 7153 | rc5: 2356, rc20: 40490 |
| 0.5 | 7185 | — |
| 0.9 | **7452** | rc5: 2678, rc20: 40760 |
| 0.998 | 10540 | — |

Cutoff dependence: δ_r = 10⁻³ → 10⁻⁶ changes Ī by 7% (logarithmic horizon
divergence — the stretched-horizon brick-wall term); extrapolating the log to
a Planck proper-distance cutoff moves Ī by O(1), irrelevant below. IR scaling
is ∝ r_c³ as expected. **Adopted: M_φ = 7452·M³** (a₊ = 0.9, r_c = 10M).

## 2. Three structural results

### 2a. The Pontryagin charge vanishes — dCS does not drive the homogeneous mode
*R*R̃ is a pseudoscalar; Kerr is reflection-symmetric across the equator, so
*R*R̃ is odd under θ→π−θ while √(−g) is even. Hence
  Q ≡ ∫_{r>r₊} *R*R̃ √(−g)d³x = 0   exactly.
The dynamical-Chern-Simons coupling (α/4)θ*R*R̃ therefore supplies **no linear
tilt** to the homogeneous mode. (It sources dipolar θ ∝ cosθ hair instead —
irrelevant here.) If the classical slips are driven, the drive is not dCS
gravity; the live candidate is the thread's own θFF̃ coupling against the
magnetospheric E·B, or a phenomenological torque. Not derived here.

### 2b. Winding sectors are non-degenerate; the ergosphere drives winding
For θ = kφ: E_k = (f²/2)k²·2π∫√(−g)g^{φφ}d³x ≡ (f²/2)k²·κ̃M.
Split at the ergosphere (polar cap θ∈[0.05,π−0.05] excluded — the kφ ansatz
carries a vortex-core log divergence on the axis, stated):

| a₊ | κ̃_ergo | κ̃_outside |
|---|---|---|
| 0.0 | 0 | +371 |
| 0.5 | −14.7 | +370 |
| 0.9 | **−110** | +375 |

The ergospheric contribution is **negative** and grows with spin: azimuthal
winding is locally favored where g^{φφ} < 0 — the field-theoretic face of
the frame-dragging drive. Net κ̃ > 0, so winding costs net energy (no
instability of the global configuration), but the drive is real and local.
Consequences:
- There are **no degenerate winding vacua** (E_k ∝ k²): "tunneling between
  winding sectors" was the wrong picture. The consistent quantum process, if
  any, is homogeneous-mode instantons (§3).
- The classical driven/stick-slip picture is microscopically supported:
  the ergosphere winds the field up; relaxation = slip. This matches the
  thread's asserted τ_slip phenomenology better than the tunneling story.

### 2c. Instanton action for homogeneous 2π slips (derived)
Euclidean kink of (1/2)M_φφ'² = μ̄⁴(1−cos(φ/f)) between adjacent minima:
  ★  B = 8fμ̄²√M_φ = 8fμ²M³√[(4π/3)r_c³Ī]   (dimensionless)
  ω₀ = μ̄²/(f√M_φ)                              (small-oscillation freq)
  Γ = ω₀√(B/2π)e^{−B}                           (1-loop instanton rate)
For Sgr A*: B = 4.94×10²²²·fμ² (f, μ in eV). Note B ∝ M³.

## 3. The rate falsifies tunneling as the slip mechanism

| (f, μ) | B | Γ⁻¹ |
|---|---|---|
| (10¹⁹ eV, 10⁻¹⁰ eV) | 4.9×10²²¹ | ∞ |
| (10²¹ eV, 10⁻²⁰ eV) | 4.9×10²⁰³ | ∞ |
| (M_pl, 10⁻³³ eV) | 1.2×10¹⁸⁴ | ∞ |

Optimizing over μ at fixed f (dlnΓ/dμ² = 0 → B* = 1):
Γ_max(f) = 0.0184/(f²M_φ). At f = 10¹⁹ eV: Γ_max⁻¹ = 2.9×10²⁴⁶ s —
**239 orders of magnitude too slow**, and that is the absolute best case at
that f. Forcing Γ⁻¹ = 46.9 s requires f ∼ 4×10⁻¹⁰⁴ eV with μ*/f ∼ 6×10⁴³:
the potential scale 43 orders above the decay constant — EFT nonsense.
Enforcing μ ≤ f and optimizing over f: best case is one slip per ∼4×10⁵² yr.
A localized (LAMH-like) phase-slip channel gives B ∼ f²M² → needs
f ∼ 10⁻⁷² eV: absurd too. M87* is worse by (M_M87/M_SgrA)³ = 3.45×10⁹ in B.

**Verdict:** homogeneous-mode (and localized) quantum tunneling cannot produce
∼47 s slips — excluded by 50–250 orders of magnitude depending on channel.
The slips are classical (driven). The tunneling-rate normalization μ is not
merely "free" (old note) — it is **excluded from being observable**.

## 4. What survives: phenomenology without microphysics

The observable predictions never needed the tunneling mechanism — only
*discreteness* (each slip is 2π → Δχ₁ = 2πγ = 55.56° at benchmark γ) and
*random timing*. Those stand:

- **Quantization corollary (untouched):** each slip is 55.56° at γ ≈ 0.1543;
  transient amplitudes histogram at integer multiples of 2πγ. Still the
  sharpest quantum-extension test, now reclassified as a discreteness test.
- **Statistics correction:** the old note's symmetric-Skellam minimal model
  (rare ±1 quantum fluctuations on a classical background) double-counts and
  assumes a backward mechanism that the driven picture lacks. Consistent
  minimal model: slips are one-directional (frame-dragging drags one way),
  N ∼ Poisson(λT_epoch) per epoch, λ = 1/τ_slip. Per-epoch depth
  D = 2πγN: E[D] = 2πγλT, Var(D) = (2πγ)²λT. Kurtosis/Allan-variance formulas
  in the old note should be recomputed from Poisson, not Skellam — the
  *form* of the quantization prediction is unchanged.
- **R(t) program:** untouched (already on Reading A; classical).

## 5. Backreaction, γ normalization, and the resulting f-window

**Correction (2026-10-05):** an earlier version of this section stated
f ≪ 1 eV from E_θ/M_BH. That was a dimensional error: it compared the field's
integrated energy to the BH *energy* M_BH while dropping that M_BH = M/G differs
from the geometric length M by M_pl². The correct local criterion,
8πG·T_θ ≪ 1/M² with T_θ ∼ f²k²/M², gives
  ★  f ≪ M_pl/√(4πκ̃') ∼ 10²⁵–10²⁶ eV,
i.e. no practical constraint beyond EFT consistency (f < M_pl). The "f ≪ 1 eV"
bound is withdrawn.

The θ sector *is* constrained, but from two other sides:

**(a) γ normalization (closes the thread's "unit-free γ" open item).**
The thread's action has (γ/2)θFF̃ with ½(∇θ)² unnormalized. Restoring the
normalization ½f²(∇θ)² (θ = phase, φ_c = fθ canonical), the derivation note's
§3 gives g = 2γ in L ⊃ (g/4)aFF̃ with a = φ_c, i.e.
  ★  g_aγ = 2γ/f.
A detection at benchmark γ ≈ 0.15 therefore maps to g_aγ = 0.3/f. Lab/stellar
bounds then bound f from *below* (drive_torque.py):
- CAST (m_θ ≲ 0.02 eV): g < 6.6×10⁻¹¹ GeV⁻¹ → f ≳ 4.5 eV,
- HB stars (m_θ ≲ 10 keV): g < 10⁻¹⁰ GeV⁻¹ → f ≳ 3 eV.
The heavy-θ escape (m_θ > 10 keV) requires μ ≲ f for EFT consistency, and
m_θ = μ²/f ≲ f then forces f > 10 keV anyway — the lower bound is robust:
  ★  f ≳ few eV × (γ/0.15).

**(b) Drive-torque plausibility bounds f from above.**
θ EOM: f²□θ = (γ/2)FF̃. For the homogeneous mode,
d/dt[M_θθ̇] = (γ/2)∫FF̃√(−g)d³x, M_θ = f²ĪM³, |FF̃| = 4|E·B|.
Changing θ̇ by 2π/τ_slip over τ_slip needs τ_req = M_θ·2π/τ_slip².
Magnetospheric supply: τ_av = 2γ∫|E·B|dV ∼ 2γ·(0.1B²)·η_fill·(10M)³,
with B ∼ 10–50 G (EHT polarization), E ∼ 0.1B (reconnection), η_fill ∼
10⁻³–10⁻¹ (current-sheet filling). For Sgr A*:

| B (G) | η_fill | f ≲ (eV) |
|---|---|---|
| 10 | 10⁻³ | 1.1×10¹³ |
| 30 | 10⁻² | 1.1×10¹⁴ |
| 50 | 10⁻¹ | 5.6×10¹⁴ |

Setting τ_av = τ_req gives the largest f the magnetosphere can still drive:
  ★  f ≲ 10¹³–10¹⁵ eV × √(γ/0.15)   (magnetospheric-parameter uncertainty)
i.e. the θF̃F × E·B drive is *plausible* — the torque exists at the needed
order — provided f is not trans-Planckian-adjacent. (Steady 46.9 s rolling
additionally needs damping or stick-slip/limit-cycle dynamics — still open;
the estimate establishes sufficiency of torque, not the exact cadence.)

**Derived viable window for the θ sector** (benchmark γ ≈ 0.15):
  ★  ~10 eV ≲ f ≲ ~10¹⁴ eV
Thirteen orders wide, non-trivial, and compatible with both lab bounds and
the drive hypothesis. The thread's γ is no longer unit-free: it is g_aγ·f/2
with f in this window.

## 6. Predictions and open derivations

- **M87* cross-check:** classical drive scales with dynamical time:
  τ_slip ∝ M → τ_M87 ≈ 46.9 s × (6.5×10⁹/4.3×10⁶) ≈ **19.7 h** at the same γ
  physics. Tunneling would have predicted total silence (B ∝ M³) — already
  excluded, so a ∼20 h slip cadence at M87* would independently confirm the
  classical mechanism. Concrete, falsifiable, no new parameters.
- **Still open:** (i) deriving τ_slip ≈ 46.9 s from the θ wave equation on
  Kerr (the drive's timescale — was asserted, remains asserted); (ii) the
  drive's origin — leading candidate θFF̃ × magnetospheric E·B, needs an
  order-of-magnitude torque estimate; (iii) vortex-core regularization of the
  winding profile (sets the O(1–100) in §5).

## 7. Old vs new — quantum-extension ledger

| claim (2026-10-03 note) | status now |
|---|---|
| notch 55.56° per 2π slip | survives (kinematics, mechanism-independent) |
| achromaticity discriminator | survives |
| epoch-depth quantization at 2πγ multiples | survives, reclassified as discreteness test |
| tunneling rate μ "free parameter" | **excluded from observability** (this note) |
| symmetric Skellam fluctuations | **replaced by one-directional Poisson** |
| winding→Δθ(t) mapping "asserted" | superseded: relevant process is homogeneous-mode; winding sectors non-degenerate |
| μ ≪ 1 consistency condition | moot (no tunneling); Poisson regime needs λT ≳ 1, satisfied |
| f-scale of the θ sector | **derived window ~10 eV ≲ f ≲ ~10¹⁴ eV** (lab bounds below via g_aγ = 2γ/f — this also closes the thread's "unit-free γ" open item; drive-torque plausibility above). Backreaction alone gives only f ≪ M_pl (an earlier f ≪ 1 eV claim in this note was a dimensional error, corrected in §5) |

## Scripts
- geo_integrals.py — M_φ and winding-coefficient Kerr integrals.
- rate_calibration.py — instanton rate, optimization, exclusion numbers.

## Assumptions (stated, not smuggled)
- Periodic potential μ⁴(1−cos(φ/f)) is the minimal completion; μ, f free.
- Homogeneous mode coherent over r_c = 10M patch (global-slip morphology).
- Stretched-horizon (log) and polar-cap (vortex-core) regularizations; results
  insensitive at the order-of-magnitude level except where noted.
- Fixed Kerr background; backreaction checked a posteriori (§5).
- 1-loop instanton prefactor; O(1) factors irrelevant against 50+ orders.
