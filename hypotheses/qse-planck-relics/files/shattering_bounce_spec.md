# QSE Round 5 (spec): The shattering-bounce requirements — what the only remaining mechanism must do

**Date:** 2026-10-04
**Status:** Requirements specification. Exploratory. NOT a mechanism, NOT a claim that
one exists, NOT a detection or validation of anything. This document converts "no
known-physics solution" into a precise target.
**Parent notes:** `fork_conversion_note.md` (Round 3 — bounce killed), 
`fragmentation_vs_trapping_note.md` (Round 4 — fragmentation killed),
`nongaussian_endtoend_note.md` (Round 2 — abundance bar).

## 0. Why this document exists

Rounds 3–4 closed every classical mass-conversion path:

- **Bounce:** every published model bounces coherently → 1 remnant per progenitor,
  f ~ m_Pl/M, short by 10¹⁶–10³⁰. Structurally dead (`fork_conversion_note.md` §1).
- **Fragmentation:** triple no-go — (1) R_s(M_J) ≈ 1.1λ_J, so every gravitational
  fragment is a black hole; (2) the parent traps after only ~400× density
  amplification, letting at most ~20 sub-scales unlock; (3) trapped pieces can't
  subdivide → O(1–20) relics vs 10¹⁶–10³⁰ needed
  (`fragmentation_vs_trapping_note.md` §4).
- **Evaporation:** 1 remnant per progenitor (Round 2 arithmetic).

The only logical remainder (`fragmentation_vs_trapping_note.md` §6): a
**horizon-destroying shattering bounce** — Planck-scale physics that fragments the
progenitor into ~M/m_Pl pieces *without* permanent trapping. It exists in no
literature (Round 3 searched: LQG/Planck-star/fireworks/erebon/memory-burden —
all one-object-per-progenitor).

This spec states exactly what such a mechanism would have to do. It does not
argue one exists.

## 1. The quantitative bar (non-negotiable; from Round 2 + fork note §0)

| Progenitor M | Relics needed N = M/m_Pl | Required f_sh | β target (Round 2) |
|---|---|---|---|
| 10⁹ kg | 4.6 × 10¹⁶ | ~0.5 | 2 × 10⁻¹⁹ |
| 6 × 10²² kg | 2.8 × 10³⁰ | ~0.5 | 1.5 × 10⁻¹² |

Relic mass ~m_Pl ≈ 2.2 × 10⁻⁸ kg (κ ~ O(1); f_sh ~ O(1) is κ-independent).
Formation side (small-r curvaton, narrow peak Σ ≲ 0.1, γ_eff ≈ 0.05) is taken
as given — Rounds 1–2 stand; this spec is conversion-only.

## 2. The sharp fork: two horns, both need new physics

The parent traps at ρ_trap = 3c⁶/(32πG³M²) — which is **~10⁻³⁵ ρ_Pl at the
low-mass end and ~10⁻⁶³ ρ_Pl at the high-mass end** (verified: ratio scales as
M⁻²). Collapse-to-trapping takes ~1 Hubble time; the radius contracts only
~7.4× (density amplification ~400×, frag note §2). So:

- **Horn A — shatter pre-trapping (ρ ≪ ρ_Pl).** Then the trigger is *not* Planck
  physics, and the fragment scale is unexplained: at 10⁻³⁵ρ_Pl the Jeans mass
  is M_J(ρ) = M_J(ρ_Pl)·(ρ_Pl/ρ)^{1/2} ~ 10¹⁷ m_Pl — seventeen orders of
  magnitude above the required fragment mass. Gravity and pressure at these
  densities know nothing of the Planck scale. Horn A must name a *sub-Planckian*
  fragmentation trigger that nevertheless produces ~m_Pl pieces.
- **Horn B — shatter at ρ ~ ρ_Pl, post-trapping.** 35–63 orders of magnitude in
  density *after* the horizon forms. The shattering happens inside a horizon;
  the exterior still sees one BH of mass M. For relics to become DM the horizon
  must be **destroyed** (or the relics escape by a non-classical channel) —
  i.e. a violation of the classical area theorem, strictly stronger new physics
  than Horn A. Standard evaporation is not an escape hatch: it yields exactly
  the ruled-out 1-relic-per-progenitor picture.

There is no third horn in the classical regime — the triple no-go closed it.

## 3. Requirements R1–R8

Any candidate mechanism must satisfy all eight, or say precisely which one it
revises and why:

- **R1 — Multiplicity:** deliver N ~ M/m_Pl relics per progenitor (4.6×10¹⁶ /
  2.8×10³⁰), f_sh ~ O(1), consistent with the β targets above.
- **R2 — No permanent trapping:** the end state contains no horizon of mass ~M.
  (Horn B: the horizon must be removed, not merely bypassed — anything less
  leaves the exterior mass budget in one BH.)
- **R3 — Fragment scale ~m_Pl:** pieces at κ·m_Pl, κ ~ O(1). Horn B gets one
  free hint — M_J(ρ_Pl) ≈ 0.56 m_Pl (corrected prefactor, frag note §1) — the
  natural terminal scale *at Planck density*; Horn A must explain the scale
  from sub-Planckian physics (see §2).
- **R4 — No re-coalescence:** 10¹⁶–10³⁰ Planck-mass fragments, born in causal
  contact at near-Planck density and strongly gravitating, must not re-merge.
  Needs a repulsion, rapid dispersal, or expansion fast enough to beat
  re-collapse. (Fork note §2, open problem — inherited, now quantified.)
- **R5 — Relic stability:** each fragment stable to today — the remnant-stability
  assumption (extremal/GUP/LQG area gap/memory burden), inherited and now
  multiplied by 10¹⁶–10³⁰ (fork note §2).
- **R6 — Formation untouched:** the curvaton formation story (Rounds 1–2) is
  not re-litigated; the mechanism acts at/after collapse, leaving β targets
  intact.
- **R7 — Halo structure:** the relic population must reproduce the framework's
  structural invariant I_QSE = ρ_s r_s³ ∝ M_halo — or the invariant is dropped
  with an explicit justification.
- **R8 — Species bound:** Planck-mass remnants with huge internal degeneracy
  face the Giddings pair-production constraint (flagged, fork note §2). Any
  proposal must address it, not inherit it silently.

## 4. Honest exit ramps (what would kill the spec itself)

- If horizon destruction is shown to imply low-energy causality/unitarity
  violation → Horn B dead. Only Horn A remains, needing a sub-Planckian
  fragmentation trigger — itself a tall order with no sketch on record.
- If both horns are closed → QSE has no logical remainder as a DM origin.
  The framework would be falsified *as dark matter*; the formation results
  (curvaton PBH formation, Rounds 1–2) stand as PBH physics, not as a relic
  model.

## 5. Candidate directions (labeled speculation — questions, not proposals)

- **Decohering bounce:** all published bounces are coherent. What *breaks*
  coherence at Planck density? (No literature; the question is the starting
  point, not an answer.)
- **QG phase transition with bubble nucleation:** bubbles as fragments — but
  nucleation happens inside the horizon (Horn B); the horizon-removal problem
  is not solved by fragmenting the interior.
- **Fragmented fireworks:** Haggard–Rovelli ejecta is ordinary radiation, not
  relics. Converting the ejecta into ~M/m_Pl Planck pieces changes the model
  entirely — and the tunneling rate for 10¹⁶–10³⁰ coordinated emissions is
  uncomputed.
- **Pre-trapping trigger (Horn A):** the least-explored horn. Is there any
  sub-Planckian instability in near-critical collapse that cascades to small
  scales before ρ_trap? (The frag note's race argument says acoustic
  oscillations block linear growth — the trigger would have to be nonlinear
  from the start.)

## 6. Bottom line

QSE's parked condition is now precise instead of vague: **the thread unparks
the day a mechanism satisfying R1–R8 — or a principled revision of them — is
written down with equations.** Until then, "shattering bounce" is a name for
a requirements list, not a theory. Nothing in this document weakens the
Rounds 3–4 kills or promotes the framework past its impasse.

## Assumptions (explicit)

1. Round 2 abundance arithmetic (β targets ↔ f_sh ~ 0.5) taken as given.
2. Spherical, radiation-dominated collapse; γ_eff ≈ 0.05 (frag note §2).
3. m_Pl ≈ 2.2 × 10⁻⁸ kg; N = M/m_Pl as in fork note §0.
4. No stabilization mechanism endorsed (R5 is a requirement, not a solution).
