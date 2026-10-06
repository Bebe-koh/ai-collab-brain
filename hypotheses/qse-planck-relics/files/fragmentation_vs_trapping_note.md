# QSE Round 4: Fragmentation vs trapping — the timescale competition, worked out

**Date:** 2026-10-03
**Status:** Heuristic analytic calculation, all numbers reproduced by
`frag_check.py` (this directory).
`completed-toy` at best — nothing here is validated, and the verdict is a kill.
**Parent notes:** `fork_conversion_note.md` (Round 3; problem (1) is the target here),
`nongaussian_endtoend_note.md` (Round 2), `nongaussian_formation_survey.md` (Round 1).

## 0. The question

Round 3 killed the bounce fork as the mass-conversion mechanism (coherent bounce →
one remnant per progenitor, short by 10¹⁶–10³⁰) and left pre-trapping fragmentation
as the only surviving bet, with three open problems. Problem (1) — the most
load-bearing — is attacked here:

> **Under what conditions can a collapsing overdensity fragment before an
> apparent horizon forms?**

"Fragmentation wins" means: the collapsing progenitor of mass M produces
N ~ M/m_Pl **untrapped** Planck-mass pieces (4.6×10¹⁶ at M = 10⁹ kg;
2.8×10³⁰ at M = 6×10²² kg). Anything less fails the Round 2 abundance bar.

**Formation context (taken as given):** small-r curvaton (Round 2 survivor),
narrow peaked spectrum (Σ ≲ 0.1) at k_*, radiation domination at formation
(r_dec ~ 10⁻³ — the curvaton never dominates; see §6), collapse fraction β
targets as in Round 2. Both progenitor masses form at t_f with M/M_H ≡ γ_eff
≈ 0.05 (from the Round 2 numbers: M_H(t_f) = c³t_f/G).

## 1. The coincidence no-go: in radiation domination, the Jeans scale is trapped

This is the structural core of the result. It is exact at O(1) and
density-independent.

Jeans length λ_J = c_s√(π/(Gρ)); Jeans mass M_J = (π/6)λ_J³ρ
(mass in a sphere of diameter λ_J). Schwarzschild radius of that mass:

R_s(M_J)/λ_J = 2GM_J/(c²λ_J) = (π/3)(Gρλ_J²/c²) = (π²/3)(c_s/c)².

For radiation (c_s² = c²/3):

**R_s(M_J) = (π²/9)·λ_J ≈ 1.10·λ_J.**

A marginally Jeans-unstable cloud is *marginally trapped*. There is no
"collapses under gravity but doesn't trap" regime: the two thresholds coincide.
Consequences:

- (a) Any sub-region massive enough to overcome pressure (m > M_J(ρ)) is
      already inside its own Schwarzschild radius — gravitational
      "fragmentation" produces **black holes**, not untrapped fragments.
- (b) Any sub-region light enough to avoid trapping (m < m_trap(ρ), with
      m_trap = m_Pl√(3/32π)·√(ρ_Pl/ρ) ≈ 0.17·m_Pl√(ρ_Pl/ρ)) is below the Jeans
      mass (M_J/m_trap ≈ 3.25 at **all** densities, since both scale as
      ρ⁻¹ᐟ²) — pressure-supported, oscillating, swept into the bulk collapse.

The requirements "small enough not to trap" and "large enough to fragment"
are mutually exclusive, parametrically, at every density of the collapse.

*Correction to the fork note:* §2(a) wrote M_J = (π/6)c_s³/(G³ᐟ²ρ¹ᐟ²), dropping
the π³ᐟ² from λ_J³. The correct prefactor is π⁵ᐟ²/6 ≈ 2.92. With c_s = c this
would give M_J(ρ_Pl) ≈ 2.9 m_Pl, not 0.52 — but with the physical radiation
sound speed c_s = c/√3 it gives **M_J(ρ_Pl) ≈ 0.56 m_Pl**, essentially the
fork note's number, for the right reason. The terminal-scale coincidence
survives; §5 explains why the dynamics can never reach it.

## 2. The race: the parent traps after only ~400× density amplification

For a uniform collapsing sphere, trapping (boundary at 2GM/c²) occurs at

ρ_trap = 3c⁶/(32πG³M²).

Collapse begins at ~horizon-entry density ρ_form = 3H²/(8πG). The ratio:

ρ_trap/ρ_form = 1/γ_eff² ≈ **400**,

with γ_eff = M/M_H(t_f) ≈ 0.05 from the Round 2 numbers — **independent of
progenitor mass** (verified numerically for both ends: 407.4 in each case).
Radius contracts by only ~7.4×; the whole collapse-to-trapping takes ~1 Hubble
time (t_ff at trapping ≈ 0.3 t_f). This is the standard PBH result: barely
super-threshold perturbations trap after O(1) Hubble times.

Sub-horizon modes oscillate acoustically (no linear growth — the fork note's
problem (1) premise). During collapse, a comoving mode k unlocks (becomes
super-Jeans) as λ_phys/λ_J ∝ a_patch⁻¹ᐟ² grows; unlock needs density
amplification (k/k_J,i)⁶. Demanding unlock before the parent traps:

(k/k_J,i)⁶ < ρ_trap/ρ_form ≈ 400  →  k ≲ 2.7 k_J,i.

So at most ~(2.7)³ ≈ **20** sub-volumes can even become gravitationally
unstable in time — and that needs δ₀ ~ O(1) on all of them, which the narrow
curvaton peak (Σ ≲ 0.1, power at 3k_* suppressed by ~e⁻⁶⁰) does not provide.
A mode at 2k_J,i unlocks at 64× amplification with only ~6× left to trapping
(linear growth ~1.8×), so it needs δ₀ ≳ 0.5 at horizon entry to go nonlinear
at all. Realistically: a **handful** of the largest sub-scales, each forming a
**trapped** sub-BH (by §1) of mass ~M/10–M/20.

Unlocking m_Pl-scale fragments would need density amplification
(M_J,i/m_Pl)² ~ 10³⁶–10⁶³ (verified); the parent traps at 400×. Not close.

## 3. Cascade termination: trapped pieces cannot subdivide

Every fragment that forms via §2 is trapped (§1) → it is a black hole, interior
causally disconnected → it yields ≤ O(1) relic (evaporation/bounce remnant —
the Round 3 arithmetic). The fragmentation cascade **terminates at the first
trapped generation**. There is no second act:

| Scenario | Fragments | Relics (≤1 each) | Needed | Shortfall |
|---|---|---|---|---|
| Coherent (realistic, peaked spectrum) | 1 | 1 | 4.6×10¹⁶ / 2.8×10³⁰ | 10¹⁶–10³⁰ |
| Handful of sub-BHs (optimistic) | ~5 | ~5 | same | 10¹⁵–10²⁹ |
| Absolute ceiling (unphysical δ₀~1) | ~20 | ~20 | same | 10¹⁵–10²⁹ |

Nonlinear spikes don't escape this: an untrapped nonlinear lump in radiation
domination either disperses (pressure) or collapses — and collapsing means
shrinking r at fixed m, so 2Gm/(rc²) → 1: it traps. There is no stable-fragment
fixed point without new physics (which is the remnant-stability assumption,
problem (3), not a fragmentation mechanism).

## 4. Verdict on problem (1): FRAGMENTATION LOSES — KILL

The triple no-go:

1. **Coincidence:** R_s(M_J) ≈ 1.1λ_J — gravitational instability and trapping
   are the same scale in radiation domination. Fragmentation *means* making
   black holes.
2. **Race:** the parent traps after ~400× density amplification; only
   k ≲ 2.7k_J,i sub-scales unlock in time; realistic spectra give a handful of
   pieces, all trapped.
3. **Termination:** trapped pieces can't subdivide; relic count per progenitor
   is O(1–20) vs the required 10¹⁶–10³⁰.

**The pre-trapping fragmentation fork is dead as the mass-conversion
mechanism.** Combined with Round 3's bounce kill, *no classical mechanism*
converts O(1) of the progenitor mass into Planck relics: bounce gives 1
remnant (coherent), fragmentation gives ≤20 trapped pieces (each ≤1 remnant),
evaporation gives 1 remnant (Round 2: underproduces by 10¹⁶).

## 5. What this says about the fork note's §2(a)–(b)

- (a) M_J(ρ_Pl) ~ m_Pl is real (corrected prefactor, §1) but **dynamically
      unreachable**: the cascade to reach it would have to pass through
      trapped generations. It is a stability scale of Planck-density matter,
      not a fragmentation endpoint.
- (b) The "trapping filter" argument is subsumed by §1: it is not that
      imperfect fragmentation leaves heavy trapped fragments as a secondary
      nuisance — it is that *every* gravitational fragment is trapped, so
      there are no untrapped fragments at any scale, ever, in the classical
      regime.

## 6. Loopholes examined and closed

- **Early matter domination** (c_s → 0, fragmentation to small scales):
      closed for the Round 2 survivor — r_dec ~ 10⁻³ means the curvaton never
      dominates; both formation epochs are radiation-dominated. (Even in
      matter domination, spherical dust collapse yields one BH per patch;
      10¹⁶ lumps would need small-scale power the peaked spectrum lacks.)
- **QCD phase-transition softening** (c_s dip → easier fragmentation):
      wrong epoch — formation at T ~ 10⁹ GeV and ~10² GeV, far above
      T_QCD ~ 0.15 GeV; c_s² = 1/3 firmly.
- **Rotation / non-sphericity:** primordial collapse is near-spherical
      (tidal torques parametrically small); disk-fragmentation channels are
      unquantified and a priori negligible. Flagged, not a rescue.
- **Non-Gaussian small-scale power** (f_NL = 750 modulating sub-horizon
      modes): sub-Jeans lumps still can't collapse — they oscillate until
      unlock, and the parent still traps first (§2). NG changes the PDF tail,
      not the race. (Silk damping erases small-scale acoustic power anyway —
      this only strengthens the no-go.)
- **Quantum-gravity shattering at ρ ~ ρ_Pl:** the parent traps at
      ~10⁻³⁵ρ_Pl (low-mass end) — *thirty-five orders of magnitude* below the
      Planck density. Any Planck-scale shattering happens **inside** a
      horizon; the exterior still sees one BH of mass M. For relics to become
      DM they must escape or the horizon must be destroyed — i.e. this is not
      "pre-trapping fragmentation" but a **horizon-destroying shattering
      bounce**: new physics appearing in no literature (Round 3 searched).
      It is the only logical remainder, and it is not a known mechanism.

## 7. Bottom line for the framework

Both classical forks are now dead as conversion mechanisms. The QSE
framework's mass-conversion problem has **no known-physics solution**: what is
needed is Planck-scale physics that (i) fragments ~10⁹–10²² kg of collapsing
matter into ~10¹⁶–10³⁰ pieces, (ii) at or below the Planck mass each,
(iii) without permanent trapping, (iv) with each piece stable to today
(problem (3), inherited ×10¹⁶–10³⁰). That is a precise specification of the
new physics required — it is not a small gap. Honest status: the formation
problem (Rounds 1–2) is solved contingent on the curvaton; the conversion
problem is now the load-bearing wall, and it stands on no published
foundation.

## Assumptions (explicit)

1. Spherical collapse; near-spherical initial conditions (standard for
   inflationary peaks).
2. Radiation domination at formation (justified by r_dec ~ 10⁻³, §6).
3. Newtonian Jeans analysis for the instability criterion — O(1)
   prefactor uncertainty acknowledged, but the R_s(M_J)/λ_J = π²/9
   coincidence is prefactor-exact given the standard definitions, and the
   race argument needs only order-of-magnitude.
4. Collapse factor 1/γ_eff² uses γ_eff = 0.05 from Round 2's (t_f, M) pairs;
   O(few) profile-dependence does not affect the verdict.
5. ≤1 relic per trapped piece (standard remnant/bounce arithmetic, Round 3).

## References

- Round 3: `fork_conversion_note.md` (bounce kill; problems (1)–(3)).
- Round 2: `nongaussian_endtoend_note.md` (β targets, curvaton params,
  γ_eff from (t_f, M) pairs, r_dec ~ 10⁻³).
- Carr & Hawking (1974); Carr (1975) — PBH formation threshold, coherent
  collapse (no fragmentation channel).
- Musco & Miller; Harada–Yoo–Kohri; Yoo et al. — relativistic collapse,
  threshold δ_c (via fork note).
- de Jong, Aurrekoetxea & Lim, arXiv:2109.04896 — NR simulations: formation
  in ~1 Hubble time, coherent (matter-domination study; timescale point).
- astro-ph/0407560 — radiation-era PBH formation: collapse possible only
  briefly after horizon crossing (pressure wins thereafter on sub-horizon
  scales) — independent corroboration of the §2 race logic.
- Pi & Sasaki, arXiv:2112.12680 — curvaton formation context (Round 1/2).
