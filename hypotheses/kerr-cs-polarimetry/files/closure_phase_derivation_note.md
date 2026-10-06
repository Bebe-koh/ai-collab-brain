# Kerr/CS polarimetry: independent derivation check of the closure-phase route
Date: 2026-09-24. Status: exploratory (completed-toy). No observational claims.

This note independently re-derives, from the stated action, (i) the predicted
EVPA signature (achromaticity, magnitude, time dependence), (ii) the factor-of-2
convention issue, and (iii) whether time-domain RL/LR closure phases break the
degeneracy with instrumental cross-hand phase. The audit's claims are reproduced
only where the math confirms them; one of them does not survive.

## 1. Setup and conventions

Stated effective action (notebook dump, 2026-09-19):

    S = ∫ d⁴x √−g [ R/16πG − ¼ F_μνF^μν + ½(∇θ)² − V(θ) + (γ/2) θ F_μνF̃^μν ] + S_m

with F̃^μν = (1/2√−g) ε^μνρσ F_ρσ (ε = Levi-Civita symbol). θ is a dynamical
pseudoscalar; γ is a dimensionless coupling (θ kinetic term unnormalized, so γ
is unit-free — §8).

Metric signature (−,+,+,+). Heaviside–Lorentz-ish conventions as written; only
ratios and the factor of 2 are at issue, and those are convention-independent.

## 2. Equation of motion: the factor of 2, derived

Vary S_int = ∫ (γ/2) θ F_μνF̃^μν √−g d⁴x with respect to A_ν. Key identity:
√−g F_μνF̃^μν = ½ ε^μνρσ F_μνF_ρσ is metric-independent (√−g cancels), hence
topological — its metric variation vanishes, so the interaction contributes
exactly zero to T_μν (the "zero stress-energy" claim for the *interaction term*
is correct; the ½(∇θ)² kinetic term still gravitates — see §8).

    δ(√−g θ F·F̃) = θ · ½ ε^μνρσ (δF_μν F_ρσ + F_μν δF_ρσ)
                 = θ ε^μνρσ F_ρσ δF_μν            (dummy-index relabeling)
                 = 2θ √−g F̃^μν δF_μν.

With δF_μν = 2∂_μδA_ν (antisymmetry) and one integration by parts, using the
Bianchi identity ∂_μ(√−g F̃^μν) = 0:

    δS_int = −4(γ/2) ∫ d⁴x √−g (∂_μθ) F̃^μν δA_ν
           = −2γ ∫ d⁴x √−g (∂_μθ) F̃^μν δA_ν.

Together with δ(−¼F²) → +∂_μF^μν, the equation of motion is

    ★  ∂_μ F^μν = J^ν − 2γ (∂_μθ) F̃^μν.                                   (1)

The notebook's *written* EOM, ∇_μF^μν = J^ν − γ(∂_μθ)F̃^μν, is missing a factor
of 2 relative to its own action. The audit's flag (a) is confirmed by direct
variation: **the action implies −2γ∂θ·F̃; the notebook text writes −γ∂θ·F̃.**

## 3. EVPA rotation: achromaticity and magnitude, derived

Take θ = θ(t) (homogeneous; the ergospheric-winding generalization only changes
Δθ). Modified Ampère law from (1): ∇×B = Ė + g ȧ B, where g is the coupling in
the standard normalization L ⊃ (g/4)aFF̃, i.e. g = 2γ for our action.

Plane wave E,B ∝ e^{i(kz−ωt)}, circular basis e_± = (x̂±iŷ)/√2, ẑ×e_± = ∓i e_±.
Faraday: B = (k/ω) ẑ×E. Ampère gives

    k²E = ω²E + igȧk ẑ×E   →   ω²_± = k² ∓ g ȧ k,

so ω_± ≈ k ∓ gȧ/2. The circular modes accumulate opposite phases,
Δφ_± = ∓(g/2)∫ȧdt = ∓(g/2)Δa, and a linear polarization (their superposition)
rotates by half the differential phase:

    ★  Δχ = (g_aγ/2) Δθ,                                                  (2)

the standard axion-birefringence result (Carroll–Field–Jackiw). Properties:

- **Achromatic**: no ω appears in (2). Δχ ∝ λ^0 exactly, vs Faraday Δχ_F ∝ λ².
  This is the signature's one robust discriminator. ✓ (audit confirmed)
- **Magnitude**: with the notebook's quantized ergospheric winding Δθ = 2πk,

      from the ACTION (g = 2γ):  Δχ_slip = 2πγk          (Reading A)
      from the WRITTEN EOM (g = γ): Δχ_slip = πγk       (Reading B)

  At γ = 0.154, k = 1: A gives 0.9676 rad = 55.44°; B gives 27.72°.
  The 27.78° benchmark matches B (0.06° residual = rounding); the MC table
  (γ=0.05→18.00°, 0.10→36.00°, …) matches A exactly. **The notebook is
  internally inconsistent; benchmark↔EOM, MC table↔action.** k=1/2 is
  topologically dead (π-winding does not return Ψ=√ρe^{iθ} to itself), so the
  live options are A vs B — a convention/code question, not physics.
- **Time dependence**: entirely in θ(t). The notebook *asserts* (not derives)
  frame-dragging-driven 2πk winding in r+<r<re unwinding over τ_slip ≈ 46.9 s
  (Sgr A*) / 18.0 h (M87*), injected as a tanh ramp. No derivation of τ_slip
  from the θ wave equation in Kerr is on record; the ∝M scaling is consistent
  with gravitational time GM/c³ (mass ratio 1585 vs time ratio 1382) but the
  prefactor is asserted. Treat τ_slip as a model input.

## 4. Visibility transform and the RL/LR factor of 2

Under EVPA rotation χ→χ+Δχ: Q+iU → (Q+iU)e^{+2iΔχ} (sign per convention).
Cross-hand visibilities carry Q±iU, so each picks up **twice** the EVPA angle:

    V^RL → V^RL e^{−2iΔχ(t)},   V^LR → V^LR e^{+2iΔχ(t)},                (3)

RR, LL, I, V invariant (notebook's transform; signs are convention-dependent,
the factor 2 is not). In coherency-matrix form this is a congruence
V_ij → U(t)V_ijU†(t) with U = diag(e^{−iΔχ}, e^{+iΔχ}), the *same* U on every
baseline — i.e. the model assumes the slip rotates the *entire* compact
emission coherently. A spatially localized slip would give baseline-dependent
effective rotations (weighted by polarized flux per baseline); (3) is then an
upper bound and the closure-phase step below needs source modeling. (Assumption;
not flagged by the audit.)

## 5. Closure phases: the degeneracy structure, explicitly

Definitions (per the audit): ψ^RL_ijk = arg(V^RL_ij V^RL_jk V^RL_ki), and
likewise ψ^LR_ijk.

RIME for cross-hands (first order): with station gains factored as
g_R,i = |g_R,i|e^{i(φ_i+ψ_i/2)}, g_L,i = |g_L,i|e^{i(φ_i−ψ_i/2)}, where
ψ_i ≡ arg(g_R,i/g_L,i) is the station cross-hand (R–L) phase offset,

    V^RL_ij,obs = g_R,i g_L,j^* [V^RL_ij + D_R,i V^LL_ij + D_L,j^* V^RR_ij] + n.

Triple-product station-phase contribution:
arg(g_R,i g_L,j^*) + (j→k) + (k→i)
  = [arg g_R,i − arg g_L,j] + [arg g_R,j − arg g_L,k] + [arg g_R,k − arg g_L,i]
  = ψ_i + ψ_j + ψ_k.                                                     (4)

**The station cross-hand phases do NOT cancel in ψ^RL_ijk.** They enter as
+(ψ_i+ψ_j+ψ_k); in ψ^LR_ijk as −(ψ_i+ψ_j+ψ_k). The audit's claim — "station
cross-hand phases cancel exactly in polarimetric closure phases … station
phases sum to zero in the triple product" — confuses parallel-hand closure
(where (φ_i−φ_j) telescopes to zero) with cross-hand closure (where the R/L
asymmetry breaks the telescoping). **The "calibration-independent by
construction" claim is incorrect as stated.**

What the slip does: from (3), every RL triple product gains e^{−6iΔχ(t)}:

    ★  slip: Δψ^RL_ijk = −6Δχ(t),  Δψ^LR_ijk = +6Δχ(t),  ∀ triangles.     (5)

Numerics: Reading A (Δχ=55.44°): −332.6° ≡ +27.4° (mod 360°). Reading B
(Δχ=27.72°): −166.3°. The two readings are observationally distinguishable
(audit's +27.4° vs −166.7° confirmed up to rounding).

Degeneracy table (per-triangle closure-phase steps):

| corruption                              | Δψ^RL_ijk        | Δψ^LR_ijk        | degenerate w/ slip? |
|-----------------------------------------|------------------|------------------|---------------------|
| constant ψ_i                            | const offset     | const offset     | no (no step)        |
| synchronized jump ψ_i→ψ_i+δ, ∀i at once | +3δ, all tris    | −3δ, all tris    | **YES, exact**: ≡ slip Δχ=−δ/2 |
| per-station ψ jump (one/few stations)   | triangle-depend. | triangle-depend. | no (≥4 stations resolve per-station vs common-mode) |
| gain amplitude/phase glitch             | 0 (telescopes)   | 0                | no                  |
| D-term drift                            | baseline-depend. | baseline-depend. | partially (needs modeling) |
| true global slip                        | −6Δχ(t), all tris| +6Δχ(t), all tris| —                   |
| intrinsic Q,U variability (no I change) | triangle-depend. | triangle-depend. | partially (see §7)  |

The honest version of the audit's claim (b): closure phases remove the need for
an *absolute* EVPA zero-point (constant ψ_i cannot mimic a step) and are immune
to gain phases, but they are **not** immune to *time-variable* station
cross-hand phases. The residual exact degeneracy is narrow but real: a
synchronized jump of all stations' R–L offsets. Physically contrived
(independent LOs per station; no common R/L reference in VLBI), but
"contrived" is not "excluded" — it must be bounded by controls, not assumed away.

### Closure traces (audit's "wrong tool" point — confirmed)
T_ijkl = ½Tr(V_ij V_kj^{−1} V_kl V_il^{−1}). Under the slip,
V→UVU† on every baseline: T → ½Tr(UMU†) = T by trace cyclicity. **Closure
traces are exactly blind to the as-written global slip**, while remaining the
right tool for station-Jones-immune polarimetry in general. Use closure
*phases* for this model, not traces. ✓ (audit confirmed)

### Veto / control channels
- **RR/LL closures**: immune to all station phases (telescoping) and invariant
  under the slip → coincident step here vetoes the candidate as a gain glitch
  or total-intensity structural event. They do **not** veto cross-hand phase
  jumps (which leave RR/LL untouched). The audit's null channel is half-right:
  it separates polarization events from gain glitches, not instrumental from
  astrophysical polarization steps.
- **RL+LR closure sum**: ψ^RL_ijk+ψ^LR_ijk cancels both ψ_i terms *and* the slip
  (±6Δχ cancel) → a pure systematics/source-structure monitor; a step here
  means "something else entirely" (D-term jump, structural change) and vetoes.
- **Calibrator scans** (3C 279, J1924-2914, NRAO 530): the actual control for
  the synchronized-jump degeneracy — an instrumental jump would plausibly
  appear in adjacent calibrator scans; a true slip would not. (Interleaving
  gaps set the timescale floor: jumps between target and calibrator scans are
  the residual hole.)
- **Multi-band achromaticity** (86/230/345 GHz identical steps): the Faraday
  discriminator. Not executable on current public releases (227/229 GHz only).

## 6. Verdict on the audit's two flags

(a) **Factor of 2 — confirmed real, and it is an internal inconsistency, not a
convention choice.** Direct variation of the notebook's own action gives EOM
coefficient −2γ∂θ·F̃; the notebook's written EOM has −γ∂θ·F̃. Benchmark
(27.78°) follows the written EOM; the MC table follows the action. If Reading B
is what was injected, every γ label in the sensitivity table is 2× optimistic
(sensitivity floor moves γ=0.15→0.30). Settling it is a code grep of
`inject_phase_slip.py` (was the injected visibility phase 2πγk or πγk?) —
still needs Jase's upload. The readings are observationally distinguishable
(+27.4° vs −166.3° in RL closure phase).

(b) **Closure-phase route — directionally correct, overstated, with one
material error.** What survives: time-domain RL/LR closure phases are the
right observable (traces are blind); the step needs no absolute EVPA reference;
the slip imprints a common-mode ±6Δχ(t) step on all triangles; per-station
cross-hand phases are separable from a common mode with ≥4 stations. What does
not survive: station cross-hand phases do *not* "cancel exactly" — they enter
as ±(ψ_i+ψ_j+ψ_k) — so the search is not "calibration-independent by
construction"; time-variable station terms remain a confounder class, with the
synchronized all-station jump exactly degenerate with the slip. The RR/LL null
channel vetoes gain glitches, not cross-hand jumps.

## 7. Falsifiable verdict: identifiability conditions and rule-out criteria

The signature is identifiable (as distinct from a bound) only if ALL hold:

1. **Theory**: factor-of-2 settled (code grep); γ given a normalization so a
   detection maps to a physical coupling (currently unit-free — a detection
   could not be compared to lab g_aγ bounds).
2. **Signal**: coincident steps in RL (−6Δχ) *and* LR (+6Δχ) closure phases,
   common-mode across all triangles after solving per-station ψ_i(t), with the
   tanh-ramp shape at the predicted τ_slip.
3. **Vetoes**: no coincident step in RR/LL closures (gain/structure veto), no
   step in the RL+LR sum (systematics veto), no coincident step in interleaved
   calibrator scans (instrumental-jump veto).
4. **Discriminator**: identical step angle at ≥2 widely separated bands
   (Faraday exclusion). Unavailable in current public data — any single-band
   candidate is *unidentified*, not identified.
5. **Noise**: sensitivity computed from real closure-phase triple-product noise
   propagation, not the 3° visibility-domain MC (the MC numbers do not
   transfer; Sgr A* is weakly polarized and RL closure SNR is the true floor).

**Quantitative rule-out**: a 3σ matched-filter search on Sgr A* 2024-D02-01
(10 s integrations, 35 RL + 35 LR triangles, proper noise propagation) with no
steps at the ±6Δχ level for the τ_slip≈46.9 s template excludes γ above the
resulting floor (for the assumed global-slip morphology). A null with stated
sensitivity is a bound, not a burial of the coupling.

**What would rule the model out** (not just bound γ): steps that scale as λ²
(Faraday, not θ); steps present in calibrators with the target (instrumental);
or steps in the RL+LR sum channel (non-slip systematics).

## 8. Assumptions and open items (not derived here)

- θ dynamics: ergospheric 2πk winding, its driving by frame-dragging, and
  τ_slip ≈ 46.9 s / 18.0 h are asserted model inputs, not derived from the θ
  wave equation in Kerr. The "quantized winding" needs θ to be the phase of a
  single-valued complex field — asserted.
- "Kerr background unmodified": true for the *interaction* (topological,
  §2), but the ½(∇θ)² kinetic term gravitates normally; neglecting backreaction
  requires small θ gradients — an assumption, not a theorem. Walker–Penrose
  "preservation" is then trivial, not a result.
- Global-slip morphology (same U(t) all baselines): assumes the whole compact
  emission rotates coherently; a localized slip needs source modeling and
  weakens (5).
- Time-variable D-terms and intrinsic Q,U variability (Sgr A* is variable)
  leaking through constant D-terms are confounder classes the audit underplays;
  they produce triangle-dependent steps, separable in principle via the
  common-mode requirement but not by fiat.
- Open: `inject_phase_slip.py` upload (settles the 2×); γ normalization;
  real closure-phase noise propagation; multi-band data.

## Bottom line

The physics core (achromatic EVPA rotation from θFF̃, magnitude 2πγk *from the
action as written*, topological non-gravitation of the interaction) derives
cleanly. The notebook contradicts its own action by 2× in the written EOM, and
the benchmark follows the wrong one — this is real and must be settled before
any sensitivity number is quoted. The closure-phase strategy is the correct
observable choice, but the audit's "cross-hand phases cancel exactly /
calibration-independent" claim is wrong: they enter as ±(ψ_i+ψ_j+ψ_k), leaving
a narrow exact degeneracy (synchronized all-station R–L jump ≡ slip) that only
calibrator controls and the veto channels can bound. The search is executable
on public EHT data as a *bounded* null/bound experiment, not an identification,
until multi-band achromaticity is available.

## Addendum (2026-09-24): factor-of-two CLOSED via verbatim `inject_phase_slip.py`

Jase supplied verbatim snippets from the script (via the Studio panel). Line-by-line verification against this note's independent derivation:

1. `visibility_transform`: `RL_new = RL * np.exp(-2j*dchi_rad)`, `LR_new = LR * np.exp(2j*dchi_rad)` — VERIFIED. Matches §5 exactly (−6Δχ on every RL closure triangle, +6Δχ on every LR triangle). Sign convention now explicit and locked; RR/LL untouched as claimed.
2. `dchi_max = 2.0*np.pi*gamma*k_winding` (k=1) — VERIFIED as Reading A (action-consistent). At γ=0.15: 0.3π rad = 54.0°, not 27°. The notebook's 27.78° benchmark came from the written EOM (Reading B, half the action's value).
3. `injected_step`: `0.5*dchi_max*(1+tanh((t−t0)/tau_slip))` — VERIFIED as implemented: smooth 0→dchi_max step centered at t0. Profile shape remains a modeling choice (asserted, not derived), now documented as such.

Resolution: the CODE was internally consistent (action → injection at 2πγk); the inconsistency was between the notebook's written EOM/benchmark and the code. The ROC simulations injected 2× the rotation the benchmark formula implies. **Consequence: every published γ sensitivity label from those runs is 2× optimistic — floor γ≈0.15 → γ≈0.30.** Future work: correct the written EOM to ∂F = −2γ(∂θ)F̃ and relabel, or equivalently keep the code and halve the claimed sensitivity. The "Open: inject_phase_slip.py upload" item is now closed.
