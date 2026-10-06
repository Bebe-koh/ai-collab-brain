# Neutron-star superfluids and the superfluid-vacuum hypothesis

**Status:** exploratory study note (NOT a goal, NOT a result). Date: 2026-09-24.
**Purpose:** prior-art review for Jase's question — can numbers from neutron-star
superfluidity inform the idea that the universe's vacuum is itself a superfluid?
**Rule used throughout:** Part 1 is established physics; Part 2 is speculative
hypothesis, graded honestly; Part 3 keeps the two separated and does not oversell.

---

## Plain-language summary

Neutron stars really do contain superfluids — this is settled physics with measured
numbers. Neutrons in the crust pair up below about ten billion degrees; protons in
the core become superconducting; deeper neutrons pair in a more exotic channel at
around a billion degrees. The smoking gun is pulsar **glitches**: sudden spin-ups
that happen when a vast array of ~10^17 quantum vortices suddenly unpin and dump
angular momentum into the crust. About 670 glitches in ~200 pulsars are catalogued,
and they tell us what fraction of the star is superfluid (~a few percent of the
moment of inertia) and how strongly the superfluid drags on normal matter.

Separately, a few physicists have proposed that the **vacuum of space itself** is a
superfluid, with gravity emerging from its collective motion the way sound emerges
from air. The serious version (Volovik) is respected theoretical physics but its
strongest claim — that the vacuum *literally is* a quantum liquid — is his
interpretation, not consensus. Other versions range from peer-reviewed-but-fringe
(Zloshchastiev's logarithmic vacuum) to fringe (Winterberg's Planck aether).

The honest bridge: neutron-star numbers **cannot confirm** the vacuum hypothesis —
no vacuum model predicts anything different about neutron stars than standard
physics does. But they can do two genuine things: (1) they are the **only empirical
data on quantum vortices and quantum turbulence at extreme density**, so any vacuum
model with vortices in it must be consistent with how vortices *actually* behave;
(2) **analogue gravity is real, demonstrated physics** — flowing superfluids in the
lab genuinely generate effective curved spacetimes for sound waves, including
observed Hawking-radiation analogues — so the *mechanism* the hypothesis invokes
is not fantasy. The cheapest next step is free: download the public glitch catalog
and compare glitch avalanche statistics against laboratory quantum-turbulence data.

---

## PART 1 — Neutron-star superfluidity (established physics)

### 1.1 Where the superfluids live

A neutron star (~1.4 solar masses, radius ~12 km, central density several times
nuclear saturation density n_0 = 0.16 fm^-3) is cold by nuclear standards
(interior T ~ 10^7–10^8 K after ~10^4 yr) but its Fermi energy is enormous, so
nucleons form Cooper pairs — the same BCS mechanism as superconductors, driven by
the nuclear force instead of phonons.

| Region | Pairing channel | Gap Δ(0) | Critical temp T_c | Density range |
|---|---|---|---|---|
| Inner crust, free neutrons | ^1S_0 (singlet, s-wave) | ~1–3 MeV (max) | up to ~10^10 K (onset ~5×10^9 K at 0.15 n_0) | ~10^11–10^14 g/cm^3 |
| Outer core, protons | ^1S_0 (singlet) | ~0.5–1 MeV | ~(2–7)×10^9 K (model-dependent) | ~n_0–2 n_0 |
| Outer core, neutrons | ^3P_2 (triplet, p-wave) | ~0.1–1 MeV | ~10^8–10^9 K | ~n_0–3 n_0 |

Key relations and numbers:

- **BCS gap–T_c relation (s-wave):** k_B T_c = (e^γ/π) Δ(0) ≈ 0.567 Δ(0),
  γ ≈ 0.577 (Euler–Mascheroni). For Δ = 1 MeV → T_c ≈ 6.6×10^9 K.
  (Triplet ^3P_2 has an angle-dependent gap and a slightly different prefactor,
  but the same order of magnitude.)
- **Crust ^1S_0 neutrons:** the gap peaks around Fermi momentum k_F ≈ 0.8 fm^-1
  and dies at both low density (too few neutrons) and high density (repulsive
  core kills s-wave attraction). Standard gap models used in cooling codes:
  SFB (Schwenk-Friman-Brown). Onset of crust superfluidity at T ~ 5×10^9 K is
  essentially model-independent.
- **Proton superconductivity:** almost certainly type-II (magnetic flux tubes,
  not type-I domains) at neutron-star fields; models CCDK and AO bracket
  T_c ≈ 2×10^9–7×10^9 K.
- **Core ^3P_2 neutrons:** the least certain gap — predictions span two orders
  of magnitude because the pairing interaction at 2–3 n_0 is poorly known.
  This is where observation bites hardest (see Cas A below).

Sources: cooling-model compilation (Beznogov & Yakovlev style reviews;
e.g. MDPI Universe 3, 45 (2020) tabulating SFB/T72/AO/CCDK gap models);
Chamel et al. crust superfluidity reviews (arXiv:1002.03705).

### 1.2 Rotation, vortices, and the numbers

A superfluid cannot rotate rigidly; it carries angular momentum in an array of
quantized vortices, each with circulation

κ = h / (2 m_n) ≈ 2.0×10^-7 m^2/s = 2.0×10^-3 cm^2/s   (neutron *pairs*)

(the 2m_n because the condensing object is a Cooper pair). Vortex areal density:

n_v = 2Ω / κ

For the Vela pulsar (ν = 11.2 Hz, Ω ≈ 70 rad/s):
n_v ≈ 7×10^8 m^-2 ≈ 7×10^4 cm^-2,
inter-vortex spacing d ≈ n_v^-1/2 ≈ 4×10^-3 cm,
total vortices N ≈ πR^2 n_v ≈ 2×10^17 (R = 10 km).

For comparison, rotating laboratory superfluid ^4He reaches n_v ~ 10^2–10^3 cm^-2
— the neutron star is far deeper into the many-vortex (continuum) regime, which
is exactly why the two-fluid hydrodynamic description works well.

### 1.3 Pulsar glitches — the observational smoking gun

**Mechanism (standard picture, Anderson & Itoh 1975):** vortices pin to nuclei in
the crust lattice. As the crust spins down electromagnetically, the pinned
superfluid keeps its rotation — a lag builds. When the Magnus force exceeds the
pinning force, vortices unpin in an avalanche, the superfluid dumps angular
momentum into the crust, and we see a sudden spin-up: Δν/ν > 0, rise time
unresolved (seconds or less), followed by relaxation over days–years as the
fluids recouple.

**Catalog statistics (all public):**
- ~670 glitches in 208 pulsars (Basu et al. 2022 compilation of the Jodrell Bank
  online glitch catalogue + literature). Two-thirds of glitching pulsars have
  glitched only once; ~8 pulsars contribute a third of all events.
- Fractional sizes Δν/ν: 10^-11 to 10^-5 (Espinoza et al. 2011, MNRAS 414, 1679).
  Crab: all < 2×10^-7. Vela: almost all > 10^-6 ("giant" glitches, quasiperiodic
  every ~3 yr). J0537-6910: 53 glitches in 13 yr, strongly correlated
  size–waiting-time.
- Size distribution is **bimodal**; within single pulsars, sizes are often
  power-law distributed and waiting times exponential (Poisson) — the signature
  of a self-organized-critical avalanche process (Melatos et al. 2008; Haskell &
  Melatos 2015). Two pulsars (Vela, J0537-6910) are quasiperiodic instead.
- **Glitch activity:** A_g = (1/t) Σ Δν/ν. Mean ν̇_g/|ν̇| = 0.012 ± 0.001
  (Fuentes et al., A&A 2024): glitches reverse ~1.2% of spin-down on average —
  a direct measure of the decoupled superfluid fraction.

**What glitches actually constrain:**
- **Superfluid moment of inertia:** I_s/I ≥ G ≡ A_g Ω/|Ω̇| (Link et al. 1999).
  With entrainment (Chamel; Andersson et al. 2012) the constraint tightens by
  ~4.3×: Vela needs I_s/I ≈ 6.9%, J0537-6910 ≈ 3.9% (Newton et al. 2015,
  Science Advances 1, e1500578). Whether the crust alone suffices is still
  debated — this is the live "glitch crisis" and it constrains the EOS and the
  crust thickness, i.e. it is real data, not theory.
- **Mutual friction:** post-glitch recovery fits give the dimensionless drag
  coefficients B, B' in the two-fluid equations. Theory expects:
  outer core B ≈ 10^-4 (electrons scattering off vortex cores; Alpar, Langer &
  Sauls 1984); crust B ≈ 10^-10 (phonon scattering) up to ≈ 10^-2 if Kelvin
  waves are excited on rapidly moving vortices (Jones 1990/92; Epstein & Baym
  1992). Observed recovery timescales (days for Vela's fast component, months
  for slow) pick out effective B values in this range — **the only empirical
  mutual-friction numbers at supranuclear density in existence.**
- **Vortex creep / pinning:** the inter-glitch spin-down and the size–waiting-time
  correlations constrain pinning forces per unit vortex length, ~10^15–10^16
  dyn/cm in standard models.

### 1.4 Related observables

- **Cooling curves:** superfluidity suppresses heat capacity and Urca neutrino
  emission (∝ exp(-Δ/T)) but opens the pair-breaking/formation (PBF) channel.
  **Cas A** (age ~340 yr, surface T ~ 2×10^6 K): the claimed rapid cooling
  (2000–2010 Chandra data) was interpreted as the onset of core ^3P_2 neutron
  superfluidity with T_c ≈ 0.5×10^9 K (Page et al. 2011, PRL 106, 081101;
  Shternin et al. 2011, MNRAS 412, L108) — "first direct evidence" of core
  superfluidity. Honest footnote: later analyses found slower continued cooling
  and questioned systematics; the T_c ≈ (0.5–1)×10^9 K constraint survives but
  with larger error bars. Still the only *thermal* measurement of a core gap.
- **GW170817 tidal deformability:** Λ̃ = 300^{+420}_{-230} (90% credible;
  Abbott et al. 2018, PRL 121, 161101). Combined with 2 M☉ pulsars
  (J0348+0432: 2.01±0.04 M☉; J0740+6620: 2.08±0.07 M☉) and NICER radii
  (J0030+0451: R ≈ 13.0 km; J0740+6620: R ≈ 13.7 km, both ~1.4–2.1 M☉),
  the EOS is pinned to R_1.4 ≈ 11.9 ± 1.4 km. This fixes the crust thickness
  (~1 km) and hence the maximum crustal superfluid reservoir — the quantity the
  glitch-crisis debate is about.
- **r-modes / continuous GWs:** superfluid mutual friction damps r-mode
  oscillations; LIGO upper limits on continuous waves from known pulsars
  therefore bound (weakly, so far) superfluid dissipation.

---

## PART 2 — Superfluid vacuum theory (the hypothesis)

### 2.1 The respectable ancestor: Sakharov's induced gravity (1967)

A.D. Sakharov, "Vacuum quantum fluctuations in curved space and the theory of
gravitation" (Dokl. Akad. Nauk SSSR 177, 70–71, 1967): the Einstein–Hilbert
action S = -(1/16πG)∫√-g R is not fundamental but **induced** — a one-loop
effect of quantum fields propagating on a curved background. Spacetime has a
"metrical elasticity" opposing curvature, generated by vacuum fluctuations;
G is then determined by field content and a cutoff (naturally the Planck
scale: G m_Pl^2 ~ 1). Modern perspective: Visser (2002, Mod. Phys. Lett. A 17,
977). This is mainstream-adjacent and respected; it says gravity *emerges* but
does not say the vacuum is a *superfluid* specifically.

### 2.2 Volovik — the serious version

Grigory Volovik (Landau Institute / Aalto), *The Universe in a Helium Droplet*
(Oxford Univ. Press, 2003), plus ~200 papers:
- **Claim:** the quantum vacuum is a quantum liquid; its *fermionic
  quasiparticles* (near Fermi points — topological defects in momentum space)
  are the Standard Model fermions; *collective modes* are gauge fields and
  gravity ("gravity is the elasticity of the quantum vacuum"). Superfluid
  ^3He-A is the closest laboratory analogue: its quasiparticles mimic chiral
  fermions, its order-parameter textures mimic gauge/gravity fields.
- **Key mechanism:** Lorentz invariance and gauge invariance are *emergent*,
  low-energy symmetries — exact only as T, E → 0 relative to the microscopic
  (Planck) scale. Topology (momentum-space invariants) protects the masslessness
  of fermions and gauge bosons.
- **Free parameters:** essentially the microscopic "trans-Planckian" physics,
  deliberately left unspecified — the theory's strength (universality) is also
  why it makes few hard predictions.
- **Standing:** Volovik is a respected condensed-matter physicist; the
  *analogy program* is legitimate, well-cited theoretical physics and the
  foundation of much of analogue gravity. The strong ontological claim — the
  vacuum *is* a superfluid, not merely *like* one — is his interpretation, not
  consensus. It has not produced a distinctive, confirmed prediction that
  separates it from effective field theory + GR.
- **Where it meets observation:** any emergent-Lorentz-invariance scheme must
  survive the Fermi-LAT GRB bounds (see §2.5). Volovik's answer: violations
  appear only at E ~ E_Pl, consistent with current limits.

### 2.3 Zloshchastiev — logarithmic superfluid vacuum theory

Konstantin Zloshchastiev (Durban Univ. of Technology), series from ~2010:
- **Claim:** the physical vacuum is a quantum Bose liquid obeying a
  *logarithmic* nonlinear Schrödinger equation; gravity is induced by the
  vacuum wavefunction. Derives a multi-scale gravitational potential —
  sub-Newtonian, Newtonian, galactic (logarithmic term → flat rotation curves),
  extragalactic (linear), cosmological (quadratic/de Sitter → acceleration).
  Later papers derive the emergent 4D metric and c itself from ℏ plus superfluid
  parameters (Universe 9, 234, 2023).
- **Predictions:** rotation curves cross Keplerian → flat → *non-flat* at
  galaxy outskirts (claimed seen in data; arXiv:2201.04135); Hubble-tension
  mechanisms; replaces dark matter *and* dark energy.
- **Free parameters:** the logarithmic nonlinearity coupling b (sets all the
  crossover scales), vacuum density/temperature parameters.
- **Standing:** peer-reviewed (MDPI *Universe*; 2020 paper ~22 citations),
  makes testable claims — but far outside mainstream cosmology, no independent
  replication of the rotation-curve fits, and the "predictions" are largely
  post-hoc accommodations. **Fringe-adjacent: serious mathematics, unproven
  physics.** Treat as an untested model, not a result.

### 2.4 Winterberg — Planck aether (fringe)

Friedwardt Winterberg (Univ. of Nevada, Reno), 1990s–2000s (Z. Naturforsch.
47a, 1217, 1992; book *The Planck Aether Hypothesis*):
- **Claim:** vacuum = dense, exactly nonrelativistic two-component superfluid
  of positive- and negative-mass Planck particles ("planckions",
  m_Pl ≈ 2.2×10^-8 kg each, equal numbers → zero net energy/cosmological
  constant). Lorentz invariance is a low-energy approximation; vortices and
  lattice defects are elementary particles; rotons (high-momentum,
  low-velocity excitations near the Planck cutoff) are dark matter
  (n_r ~ 10^? cm^-3 estimates in the papers).
- **Standing:** **fringe.** Published in real (if minor) journals, but as even
  sympathetic summaries note, "the theory never gained significant traction,
  as specific predictions were scarce, and some details were sketchy."
  Negative-mass constituents and exact nonrelativistic microphysics put it in
  direct tension with the Lorentz bounds below. Of historical/sociological
  interest only.

### 2.5 Cousins worth knowing (live research, adjacent)

- **Analogue gravity** (Unruh 1981; Barceló–Liberati–Visser, Living Rev.
  Relativity 2011): perturbations of a flowing superfluid obey
  □_g φ = 0 with an *acoustic metric* g_μν built from the background flow —
  a genuine emergent curved spacetime for phonons. **Experimentally
  demonstrated:** Steinhauer (Nature Phys. 2016; Nature 2019) observed
  Hawking-radiation correlations from an acoustic horizon in a BEC
  (4,600 repetitions; thermal spectrum confirmed 2019). This is the
  *proven* core of every superfluid-vacuum idea: effective metrics from
  superfluid flow are real physics.
- **BEC spacetime condensate** (B.L. Hu and collaborators): spacetime as a
  condensate, geometrogenesis — theoretical, no distinctive predictions yet.
- **Superfluid dark matter** (Berezhiani & Khoury, PRL 2015): DM forms a
  superfluid in galaxies; its phonons mediate a MOND-like force. Live,
  debated, testable program — but it is about *dark matter*, not the vacuum.

### 2.6 Where the hypothesis stands against observation

- **Lorentz invariance:** Fermi-LAT GRBs (Vasileiou et al. 2013, PRD 87,
  122001): no vacuum dispersion; E_QG,1 > 7.6 E_Pl ≈ 9.3×10^19 GeV (linear),
  E_QG,2 > 1.3×10^11 GeV (quadratic), 95% CL. Any superfluid-vacuum model must
  hide Lorentz violation above ~10^19 GeV (linear) — allowed for Volovik-style
  emergence, fatal for models (like Winterberg's) with low-scale preferred
  frames or superluminal vacuum modes.
- **Gravitational waves:** GW170817/GRB 170817A: |c_GW − c|/c < ~10^-15 —
  kills models where gravity and light see different effective metrics at
  low energy. (Zloshchastiev's later work claims c_GW = c; check, don't assume.)
- **Equivalence principle / PPN:** solar-system tests constrain PPN γ − 1 to
  ~10^-5 (Cassini); any vacuum-superfluid correction to the metric must be
  invisible there.
- **Bottom line:** the hypothesis survives only in the "emergence at the
  Planck scale, exact GR below it" form — which is also the form that makes
  almost no distinctive predictions. That is the central tension of the field.

---

## PART 3 — The bridge (honest assessment)

### 3.1 What genuinely transfers vs. what is analogy only

| # | Possible connection | Verdict | Why |
|---|---|---|---|
| 1 | Vortex quantization & turbulence statistics | **Genuine — best bet** | Glitch avalanches are the only data on quantized-vortex avalanches outside the lab. If a vacuum model invokes vortices (all of them do), its statistical predictions must be consistent with glitch size/waiting-time distributions. This is a real constraint channel. |
| 2 | Mutual friction coefficients B, B' | **Genuine — unique data** | The only empirical mutual-friction numbers at supranuclear density. Any two-fluid effective theory of a superfluid vacuum needs dissipative coefficients; NS values are the sole calibration point nature provides. |
| 3 | Analogue-gravity mechanism | **Genuine — proven** | Acoustic metrics from superfluid flow are demonstrated physics (Steinhauer). Volovik-type emergence is not fantasy *as a mechanism*. |
| 4 | Pairing gaps / T_c as vacuum parameters | **Analogy only** | NS superfluidity is fermionic Cooper pairing via the nuclear force at 10^9 K. A vacuum superfluid would be bosonic/Planckian. No number transfers; the microphysics is unrelated. |
| 5 | "NS proves vacuum is superfluid" | **No — logical error** | Nothing about neutron stars distinguishes vacuum models from standard physics. NS data can *constrain shared ingredients* (vortex dynamics, Lorentz invariance) but can never *confirm* the vacuum hypothesis. |
| 6 | Cooling curves / EOS / glitch crisis | **Irrelevant to vacuum** | These constrain nuclear physics, not vacuum structure. Useful only insofar as they fix the NS "laboratory" (reservoir sizes) for items 1–2. |

The sharp line: neutron stars are a **calibration laboratory for the universal
parts** of superfluid physics (quantized circulation, two-fluid hydrodynamics,
vortex avalanches) — the parts any superfluid vacuum would share by virtue of
being a superfluid. They say nothing about the vacuum's microscopic identity.

### 3.2 Three concrete quantitative questions worth pursuing

**Q1. Do glitch avalanches share statistics with laboratory quantum turbulence?**
Fit the size distribution exponent(s) and waiting-time distribution from the
public Jodrell Bank glitch catalogue (~670 events), split by pulsar class
(Crab-like vs. Vela-like), and compare quantitatively against (a) vortex-
avalanche exponents from superfluid-^4He counterflow/grid-turbulence
experiments and BEC turbulence simulations, and (b) self-organized-criticality
predictions. A match would establish universality of quantized-vortex
avalanche statistics all the way from laboratory cryostats to a 10-km star
holding ~10^17 vortices. A mismatch localizes
*where* universality breaks. Either way it is a publishable, honest result,
and it is the single number a vacuum-vortex model would most need.
*Cost: free (public catalogs) + analysis time.*

**Q2. Build the empirical mutual-friction dataset.**
Extract effective B (and B' where possible) from post-glitch recoveries for the
~31 pulsars with ≥5 glitches, using two-fluid fits (Andersson/Haskell
formalism). Publish it as a table: the first empirical mutual-friction
compilation at nuclear density. Then ask: do the values cluster at the
theoretical core value (B ~ 10^-4) or scatter across the crust range
(10^-10–10^-2)? The answer calibrates the dissipative sector of *any*
two-fluid superfluid model — including analogue ones aimed at emergent
spacetime.
*Cost: public timing data + TEMPO2/PINT analysis; weeks of work, no new
observations.*

**Q3. Dimensionless vortex-regime comparison.**
Compute for pulsars vs. laboratory superfluids the dimensionless numbers that
control vortex dynamics: vortex density in units of coherence length
(n_v ξ^2), inter-vortex spacing vs. system size, and the ratio of rotation
rate to critical values. NS crust: ξ ~ 10 fm (pairing coherence length),
d ~ 4×10^-3 cm → d/ξ ~ 10^10 — absurdly dilute vortices, far beyond any lab
regime. Documenting *how far* outside the lab regime NS vortices sit tells you
exactly which extrapolations a vacuum-superfluid model is making when it
borrows NS numbers — and which it cannot make.
*Cost: pen, paper, and the numbers in §1.2.*

### 3.3 Numbers worth getting — ranked by cost

1. **Jodrell Bank glitch catalogue** (http://www.jb.man.ac.uk/pulsar/glitches.html)
   — ~670 glitches, sizes, epochs, recoveries. **Free, public.** The single
   highest-value dataset for Q1.
2. **ATNF pulsar catalogue** (public) — ν, ν̇ for every pulsar: needed for the
   activity parameter A_g and reservoir fractions. **Free.**
3. **Derived quantities** (spreadsheet-level): A_g per pulsar, I_s/I bounds,
   vortex densities n_v = 2Ω/κ. **Free.**
4. **NICER mass–radius posteriors** (Riley/Miller et al. 2021, public) —
   fixes crust thickness → caps the crustal reservoir in the glitch-crisis
   debate. **Free.**
5. **Cas A + other cooling data** (Chandra archive, public) — thermal
   constraint on the ^3P_2 gap, T_c ≈ (0.5–1)×10^9 K. **Free; moderate
   analysis.**
6. **LIGO continuous-wave upper limits** (public) — weak bounds on r-mode/
   superfluid dissipation. **Free.**
7. **Lab quantum-turbulence literature** (spectra, avalanche exponents from
   ^4He and BEC experiments) — the comparison arm of Q1. **Free (reading).**
8. **New analysis: glitch-recovery fits for B** (Q2) — the only item costing
   real work (weeks, TEMPO2/PINT). Everything above is download-and-analyze.

### Bottom line for Jase

The universe-as-superfluid is a legitimate question with one respected
formulation (Volovik), one speculative-but-testable formulation
(Zloshchastiev), and a fringe tail (Winterberg) — plus the proven reality
that superfluids really do make effective spacetimes (analogue gravity).
Neutron stars give you the only hard numbers on quantum vortices outside a
laboratory: ~10^17 of them, avalanche statistics for ~670 events, and the
only measured mutual-friction coefficients at nuclear density. Those numbers
can't prove the vacuum is a superfluid, but they are the anvil any vortex-
based vacuum theory has to survive being struck against. Start with Q1 — it
costs nothing and ends with a real number.

---

## References (key sources consulted)

- Page, Prakash, Lattimer & Steiner 2011, PRL 106, 081101 (Cas A cooling,
  T_c ≈ 0.5×10^9 K) — https://arxiv.org/abs/1011.6142
- Shternin et al. 2011, MNRAS 412, L108 (Cas A, independent analysis)
- Espinoza et al. 2011, MNRAS 414, 1679 (315 glitches, sizes 10^-11–10^-5)
- Basu et al. 2022 compilation (670 glitches / 208 pulsars)
- Fuentes et al. 2024, A&A (glitch activity ν̇_g/|ν̇| = 0.012±0.001) —
  http://arxiv.org/pdf/1710.00952v1
- Newton, Hooker & Strohmayer 2015, Sci. Adv. 1, e1500578 (entrainment,
  Vela needs 6.9% MoI) — https://www.science.org/doi/10.1126/sciadv.1500578
- Chamel 2013 / Andersson et al. 2012 (entrainment corrections)
- Alpar, Langer & Sauls 1984 (core mutual friction B ~ 10^-4)
- Haskell & Melatos 2015, PASA (vortex-avalanche hydrodynamics, B ranges) —
  https://arxiv.org/pdf/1603.04304v1
- Abbott et al. 2018, PRL 121, 161101 (GW170817, Λ̃ = 300^+420_-230) —
  https://arxiv.org/abs/1804.08583
- Riley et al. / Miller et al. 2021 (NICER J0030, J0740 radii)
- Volovik 2003, *The Universe in a Helium Droplet* (Oxford Univ. Press)
- Zloshchastiev 2020, Universe 6, 180 (logarithmic SVT) —
  https://arxiv.org/abs/2011.12565v1
- Zloshchastiev 2023, Universe 9, 234 (emergent metric, c derived)
- Winterberg 1992, Z. Naturforsch. 47a, 1217 (Planck aether)
- Sakharov 1967, Dokl. Akad. Nauk SSSR 177, 70 (induced gravity);
  Visser 2002, Mod. Phys. Lett. A 17, 977 (modern perspective)
- Vasileiou et al. 2013, PRD 87, 122001 (Fermi-LAT LIV bounds:
  E_QG,1 > 7.6 E_Pl) — http://arxiv.org/abs/1305.3463
- Unruh 1981, PRL 46, 1351 (acoustic metric); Barceló–Liberati–Visser 2011,
  Living Rev. Relativity (analogue gravity review)
- Steinhauer 2016, Nature Phys. 12, 959; 2019 follow-up (BEC Hawking radiation)
- Berezhiani & Khoury 2015, PRL (superfluid dark matter)
