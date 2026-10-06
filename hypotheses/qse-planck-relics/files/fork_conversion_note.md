# QSE Round 3: Bounce vs fragmentation — which fork delivers O(1) mass conversion?

**Date:** 2026-10-03
**Status:** Literature survey + heuristic scaling calculations. `completed-toy` at best;
nothing here is validated, and one fork is killed on published literature alone.
**Parent notes:** `nongaussian_formation_survey.md` (Round 1), `nongaussian_endtoend_note.md`
(Round 2). **Briefing:** `briefing_bearing_assessment.md` (fork definitions).

## 0. The question, sharpened by Round 2

Round 2's relic-abundance check showed the briefing's β targets (2×10⁻¹⁹ at
M ~ 10⁹ kg; 1.5×10⁻¹² at M ~ 6×10²² kg) are consistent **only** with
near-complete conversion of progenitor mass into Planck-mass relics. The
one-relic-per-progenitor picture underproduces DM by ~10¹⁶ (low-mass end).
The bounce-vs-fragmentation fork — parked early because both options inherit
the formation constraints, now unblocked since formation is solved (curvaton,
small-r) — must therefore be decided on a single criterion:

> **Which fork converts O(1) of the progenitor mass into Planck-mass relics?**

Quantified demand per progenitor:

| Progenitor M | Relics needed (N = M/m_Pl) | Required conversion f_sh |
|---|---|---|
| 10⁹ kg | 4.6×10¹⁶ | ~0.5 (Round 2: Ω ≈ 0.5 at f_sh = 1) |
| 6×10²² kg | 2.8×10³⁰ | ~0.5 |

Any mechanism delivering ~1 relic per progenitor fails by 16–30 orders of
magnitude. That is the bar.

## 1. Bounce fork: the literature gives one remnant per progenitor, always

**Remnant-DM literature (evaporation endpoint).** The entire Planck-relic DM
literature assumes one stable relic per evaporated BH: MacGibbon (1987);
Barrow–Copeland–Liddle; the Carr et al. review writes the DM contribution via
M_R(m_BH), the mass created *per PBH* — a single remnant mass per progenitor.
T&L's β ~ 10⁻⁵ benchmark is this picture's number. At the briefing's β
targets it underproduces by ~10¹⁶ (Round 2, §1). This is not a tunable
detail — it is the defining arithmetic of the remnant scenario.

**Planck-star / LQG bounce literature (bounce at/near formation).** Rovelli &
Vidotto (arXiv:1401.6562): quantum-gravitational pressure halts collapse at
Planck density and the star *bounces as a whole* — "analogous to the bouncing
of a ball"; the emerging object is a single re-expanding star / white hole.
Ashtekar–Olmedo–Singh: the LQG transition replaces the singularity with a
single black-to-white-hole transition. Kelly–Santacruz–Wilson-Ewing
(arXiv:2006.09325): quantum Oppenheimer–Snyder collapse → "nonsingular bounce
from the collapsing matter to an expanding white-hole shock wave" — one
expanding matter field, one horizon that disappears. Kiefer & Mohaddes:
wave-packet collapse bounces at a minimal radius and re-expands — unitarily,
coherently. Barceló et al.: bounce-induced BH→WH transition, one object.
In every model, the bounce is **coherent**: the whole collapsing distribution
reverses together. Conversion fraction into Planck-mass relics:
f ~ m_Pl/M ~ 2×10⁻¹⁷ (low-mass end) to 4×10⁻³¹ (high-mass end) — i.e.,
*exactly* the ruled-out picture, short by 16–30 orders of magnitude.

**White-hole "fireworks" (Haggard–Rovelli).** The BH tunnels to a white hole
and ejects its mass-energy — but the ejecta is ordinary radiation/particles
(the time-reverse of collapse), not a shower of Planck relics. One object in,
radiation out.

**"Erebons" (Rovelli, arXiv:1801.06830-ish; MDPI Universe 4:129):** white-hole
remnants as DM — explicitly **one remnant per progenitor**, lifetime
τ_WH ~ m_0⁴, internal volume ~ m_0⁴, remnant mass Planckian. Same arithmetic.

**Memory-burden remnants (Dvali et al.):** evaporation stalls, leaving a
long-lived remnant — still one per progenitor.

**Searched and absent:** no bounce model in the literature shatters the
progenitor mass into ~M/m_Pl Planck-scale pieces. A "shattering bounce" —
where the re-expanding interior fragments at Planck density — would be
entirely new physics: it appears in no LQG, Planck-star, or remnant paper
found. (The closest-flavored speculation, Nikolić's "gravitational crystal"
inside the hole, is still one object of mass M, not free relics.)

### Bounce verdict: DEAD as the mass-conversion mechanism

The bounce literature is unanimous in the wrong direction: coherent bounce,
one remnant per progenitor, f ~ m_Pl/M. It cannot deliver O(1) conversion at
any tuning — the shortfall is 16–30 orders of magnitude, structural, not
parametric. **The bounce fork's surviving role is exactly what the briefing
established: it removes evaporation constraints.** It does not and cannot
produce the relic population. Kill it as the conversion mechanism; keep the
evaporation-constraint result.

## 2. Fragmentation fork: no calculation exists, but the mass scale is right

**Literature status: empty.** The PBH-formation literature (Carr; Musco &
Miller; Harada–Yoo–Kohri; the Yoo et al. peak-theory program) treats the
collapsing overdensity as **coherent** — the Jeans criterion is used to decide
whether pressure *prevents* collapse, not as a fragmentation channel. No
paper found computes fragmentation of a primordial overdensity into many
Planck-mass pieces, pre- or post-trapping. Searches on "fragmentation" +
PBH formation return only the standard coherent-collapse literature.
(Q-ball/oscillon fragmentation literature makes macroscopic fragments that
*become* BHs — the wrong direction.)

**What can be said anyway — three heuristic scalings, all `completed-toy`:**

**(a) Terminal fragment scale.** Jeans mass M_J = (π/6) c_s³/(G^{3/2}ρ^{1/2}).
Pushed to Planck density with c_s ~ c:
M_J(ρ_Pl) = (π/6) m_Pl ≈ 0.52 m_Pl.
*If* hierarchical fragmentation proceeds to Planck density, the natural
terminal fragment scale is the Planck mass — not an input assumption but an
output of the scaling. This is the fragmentation fork's strongest point: it
is the only fork whose natural mass scale coincides with the required relic
mass.

**(b) Trapping filter.** A uniform fragment of mass m forms a trapped surface
when its radius reaches 2Gm/c², i.e. at density
ρ_trap ≈ 3c⁶/(32πG³m²) = (3/32π)(m_Pl/m)² ρ_Pl.
A 10³ m_Pl fragment traps at ~3×10⁻⁸ ρ_Pl; a 10⁶ m_Pl fragment at
~3×10⁻¹⁴ ρ_Pl. **Only ~m_Pl fragments reach Planck density untrapped.**
This cuts both ways: it structurally selects the Planck scale as the unique
fragment mass that survives to Planck density without forming a horizon —
but it also means imperfect fragmentation leaves heavy *trapped* fragments,
each of which needs its own remnant story (back to the bounce/evaporation
problem per fragment). A clean shatter must go essentially directly to
m_Pl pieces.

**(c) The race.** Fragmentation must beat coherent collapse *and* complete
before trapped surfaces form ("pre-trapping" is load-bearing, not decorative:
post-trapping fragments are inside a horizon, and the exterior still sees one
BH). In radiation domination, sub-horizon density perturbations oscillate
acoustically rather than growing — linear fragmentation does not happen; the
mechanism would have to be nonlinear, late in collapse. No timescale
calculation exists. This is the fork's biggest open dynamical question.

**Further open problems (all unquantified):**
- **Re-coalescence:** at Planck density with Planck-scale separations, m_Pl
  fragments are in causal contact and strongly gravitating; nothing in the
  heuristic prevents re-merging. No calculation.
- **Stability:** each Planck-mass fragment must survive to today — a
  Planck-mass BH evaporates in ~t_Pl without new physics. The fragmentation
  fork therefore *inherits the remnant-stability assumption* (extremal/GUP/LQG
  area gap/memory burden — the mechanisms discussed in the remnant
  literature). It does not escape that assumption; it multiplies it by
  10¹⁶–10³⁰.
- **Giddings species problem** applies to the relic population generally
  (both forks): Planck-mass remnants with huge internal degeneracy face
  pair-production constraints. Flagged, not resolved.

### Fragmentation verdict: STRAINED, not dead — the fork to bet on

No end-to-end calculation exists and the dynamical obstacles are serious
(race against trapping, acoustic oscillations, re-coalescence, stability
assumption). But unlike the bounce fork — where the literature actively
contradicts the requirement — nothing in the literature *rules out*
fragmentation, and the terminal-scale scalings (a) and (b) point at exactly
the right mass. **If the QSE framework is to survive, it survives on the
fragmentation fork**, with the following as the explicit work program:
(1) a nonlinear fragmentation calculation in a collapsing primordial
overdensity showing fragmentation beating trapping; (2) a stabilization
mechanism for Planck-mass fragments; (3) the re-coalescence analysis.

## 3. Verdicts

| Fork | Delivers O(1) conversion? | Literature bearing | Verdict |
|---|---|---|---|
| **Bounce** (coherent quantum bounce → remnant) | No: f ~ m_Pl/M, short by 10¹⁶–10³⁰, structurally | Unanimous the wrong way — every bounce model gives O(1) remnant per progenitor | **DEAD as conversion mechanism.** Surviving role: evaporation-constraint removal only (already established). |
| **Pre-trapping fragmentation** | Not demonstrated — but mass scale comes out right (M_J(ρ_Pl) ~ m_Pl; trapping filter selects m_Pl) | Empty: no calculation for or against | **STRAINED, not dead.** The only fork that can work; needs (1)–(3) above. |

**What would change these verdicts:**
- Bounce: a published "shattering bounce" mechanism converting O(1) of mass
  into many Planck relics. None exists; this would be new physics, not a
  literature retrieval.
- Fragmentation → dead: a no-go theorem showing fragmentation cannot beat
  trapping in radiation-domination collapse, or that Planck-density fragments
  necessarily re-coalesce.
- Fragmentation → viable: the nonlinear calculation (1) above.

## 4. Assumptions (explicit)

1. Relic mass ~ m_Pl per fragment (κ ~ O(1)); κ ≫ 1 would ease N but the
   required f_sh ~ O(1) is κ-independent to order of magnitude.
2. The Round 2 abundance arithmetic (β targets ↔ f_sh ~ 0.5) is taken as
   given; if β targets are revised, §0's bar moves with them.
3. Fragmentation scalings (a)–(b) are Newtonian/GR heuristics pushed to
   ρ_Pl; quantum-gravity corrections are O(1) at best in this estimate and
   could change prefactors, not the parametric conclusion.
4. Both forks assume stable Planck-mass relics; no stabilization mechanism
   is endorsed here.

## References

- Round 1: `nongaussian_formation_survey.md`; Round 2: `nongaussian_endtoend_note.md`
  (this directory).
- Rovelli & Vidotto, "Planck stars," arXiv:1401.6562 (2014) — coherent bounce,
  one object per progenitor.
- Ashtekar, Olmedo, Singh — LQG black-to-white-hole transition (via
  https://physics.aps.org/articles/v11/127).
- Kelly, Santacruz, Wilson-Ewing, "Black hole collapse and bounce in effective
  loop quantum gravity," arXiv:2006.09325 — single expanding matter field.
- Haggard & Rovelli — black-hole fireworks (BH→WH tunneling; ejecta =
  radiation, not relics).
- Rovelli, "Pre-Big-Bang Black-Hole Remnants and Past Low Entropy,"
  Universe 4:129 (erebons — one remnant per progenitor, τ_WH ~ m_0⁴).
- MacGibbon (1987); Barrow–Copeland–Liddle (1992) — one relic per evaporated BH.
- Carr et al., PBH review (arXiv:2006.02838; arXiv:2601.06024) — remnant-DM
  formalism with M_R per PBH; coherent-collapse formation.
- Domènech et al., "Unveiling Primordial Black Hole Relics Through Induced
  Gravitational Waves," arXiv:2512.22450 — relic-abundance formalism,
  m_relic = r M_Pl per PBH.
- Giddings — remnant pair-production / species problem (constraint on any
  Planck-relic population).
- Dvali et al. — memory-burden stalled evaporation (still one remnant per
  progenitor).
