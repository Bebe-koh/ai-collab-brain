# Q3: Dimensionless vortex-regime comparison — neutron stars vs. laboratory quantum fluids

**Status:** exploratory / pen-and-paper theory. NOT a result, NOT a detection claim. Date: 2026-09-25.
**Question:** in dimensionless terms, how far apart are neutron-star vortices from
laboratory quantum-fluid vortices (superfluid ^4He, atomic BECs)? Exactly which
extrapolations connect the regimes, and precisely where does each one break?
**Honesty rule for this note:** every number carries units and a source; every
extrapolation is labeled with its breaking point. The breaking points are the
deliverable.

---

## Plain-language summary

Put the three systems side by side in dimensionless form and the picture is stark:
a neutron star is **not** a scaled-up laboratory superfluid. Its vortices sit
~10^9 coherence lengths apart (lab helium: ~10^5; BECs: ~10–100), number ~10^17
(lab: 10^2–10^5), operate at 1–10% of their critical temperature (lab: 50–90%),
and feel mutual friction ~10,000× weaker than helium's. The *equations* are the
same shape (quantized circulation, two-fluid hydrodynamics), but the *regime* is
an extreme corner no laboratory reaches: ultra-dilute vortices, ultra-cold,
ultra-weak drag. That corner is exactly what makes neutron-star data valuable —
it anchors the asymptotic limit labs can't get to — and exactly what forbids
porting lab numbers (friction coefficients, turbulence statistics, pinning
strengths) directly onto the star. One quantity *does* transfer robustly: the
vortex line tension depends on the regime only through a logarithm, so it is
nearly the same everywhere.

---

## 1. Operating points (read this before the table)

Dimensionless comparisons are meaningless without stating the operating point.
Each column below is one concrete, sourced configuration — not a universal claim
about the whole system.

| Column | System and configuration | Why this point |
|---|---|---|
| **NS (Vela crust)** | Vela pulsar crust neutrons: ν = 11.19 Hz (Ω = 70.3 rad/s), R = 10 km, T ~ 10^8 K | The best-measured glitcher; crust is where pinning avalanches live |
| **He II (rotating bucket)** | Ω = 5 rad/s, R = 1 cm, T = 1.5 K | Typical rotating-^4He vortex-lattice experiment (Yarmchuk/Packard lineage) |
| **He II (counterflow turbulence)** | Heat-driven tangle, L = 2.6×10^10 m^-3, T ≈ 2.0 K | Zhang & Van Sciver 2005, Nature Phys. 1, 36 — measured line density |
| **BEC (Na, fast rotation)** | Ω ≈ 2π×70 Hz, R⊥ ≈ 15 μm, peak density ~10^14 cm^-3 | Abo-Shaeer et al. 2001, Science 292, 476 (up to ~130 vortices); fast-rotation parameters from the ENS/Paris quartic-trap work |

---

## 2. Master table

### 2a. Dimensional quantities (with units and sources)

| Quantity | NS (Vela crust) | He II (bucket) | He II (turbulence) | BEC (Na) |
|---|---|---|---|---|
| Circulation quantum κ [m^2/s] | 1.98×10^-7 = h/2m_n (neutron *pairs*) | 9.98×10^-8 = h/m_4 [arXiv:2510.27440] | same | 1.73×10^-8 = h/m_Na |
| Rotation rate Ω [rad/s] | 70.3 | 5 | n/a (driven tangle) | ~440 |
| Vortex areal density n_v = 2Ω/κ [m^-2] | 7.1×10^8 | 1.0×10^8 | n/a (use L below) | 5.1×10^10 |
| Intervortex spacing d = n_v^-1/2 [m] | 3.8×10^-5 | 1.0×10^-4 | 6.2×10^-6 (l = L^-1/2) [Zhang] | 4.4×10^-6 |
| Coherence/healing length ξ [m] | ~1×10^-14 (pairing, ~10 fm) [study note §1.1] | 1.5×10^-10 (core diameter ~0.15 nm) [arXiv:2510.27440] | same | ~2×10^-7 (0.2 μm at 4×10^14 cm^-3) [arXiv:cond-mat/0106235] |
| System size R [m] | 1.0×10^4 | 1.0×10^-2 | ~10^-2 (channel) | 1.5×10^-5 |
| Total vortices N | ~2.2×10^17 | ~3.1×10^4 | n/a (tangle) | ~10^2 |
| Temperature T [K] | ~10^8 | 1.5 | ~2.0 | ~10^-7 |
| Critical temperature T_c [K] | ~10^9–10^10 | 2.17 (T_λ) | 2.17 | ~10^-6 |
| Mutual friction B [dim'less] | ~10^-4 (core theory); 10^-10–10^-2 (crust) [study note §1.3] | ~1.2–1.5 (NIST, 1.3–1.6 K) [srd.nist.gov] | ~1 (same T range) | → 0 (normal fraction negligible) |

### 2b. Dimensionless regime numbers (the actual comparison)

| Dimensionless number | NS | He II (bucket) | He II (turb.) | BEC | Meaning |
|---|---|---|---|---|---|
| **d/ξ** (spacing / coherence length) | **~4×10^9** | ~7×10^5 | ~4×10^4 | **~20** | Diluteness of the vortex array |
| **n_v ξ^2** = (d/ξ)^-2 | 7×10^-20 | 2×10^-12 | 6×10^-10 | 2×10^-3 | Vortex density in core units |
| **d/R** (continuum quality) | 4×10^-9 | 1×10^-2 | ~10^-3 | ~0.3 | How good the coarse-grained two-fluid description is |
| **T/T_c** | 0.01–0.1 | 0.69 | 0.92 | 0.1–0.9 | Normal-fluid fraction regime |
| **Re_s = ΩR^2/κ** (superfluid Reynolds no.) | **~4×10^16** | ~5×10^3 | n/a | ~6 | Inertial vs. quantum scale separation |
| **ln(d/ξ)** (line-tension log) | ~22 | ~13.5 | ~10.6 | ~3 | Only log-sensitivity in vortex energetics |
| **B** (mutual-friction strength) | 10^-10–10^-2 | ~1 | ~1 | ~0 | Weak-drag vs. strong-drag regime |

Reading the table: the neutron star is ~10^4× more dilute in vortices than
rotating helium and ~10^8× more dilute than a BEC (d/ξ); its total vortex count
exceeds the lab by 12–15 orders of magnitude; it lives at 1–10% of T_c while
labs live at 50–90%; and its mutual friction is up to 10 orders of magnitude
weaker than helium's. **These are different corners of parameter space, not
different sizes of the same experiment.**

---

## 3. Extrapolations and exactly where each breaks (main deliverable)

### E1. Feynman's rule, n_v = 2Ω/κ — TRANSFERS (with one caveat)
The rule is verified by direct vortex counting in rotating He II (Yarmchuk,
Gordon & Packard 1979, PRL 43, 214) and in BECs (Abo-Shaeer et al. 2001).
**Break point:** in a neutron star it is *assumed*, never observed — no
telescope resolves 10^-5 m vortex spacing on a 10 km star 300 pc away. It
enters glitch models as an axiom. The quantization itself is topological and
scale-free, so this is the safest extrapolation of the set — but it remains
an untested assumption at nuclear density, not a measurement.

### E2. Two-fluid (HVBK) hydrodynamics — TRANSFERS, and is *best* justified in the NS
Coarse-graining requires d ≪ R. The table gives d/R = 4×10^-9 (NS) vs 10^-2
(He bucket) vs 0.3 (BEC). The continuum description is *most* valid in the
neutron star and *least* in the BEC — the reverse of naive intuition, and the
reverse of where the experiments are easiest. **Break point:** none in the NS
(the inequality is satisfied by 9 orders of margin); the extrapolation that
fails is lab→lab, i.e. applying coarse-grained models to few-vortex BECs.

### E3. Vortex line tension — TRANSFERS (logarithmically)
Line energy per unit length ∝ (ρ_s κ^2/4π)·ln(d/ξ). The regime enters only in
the logarithm: 22 (NS) vs 13.5 (He) vs 3 (BEC). A factor ~10^9 in d/ξ becomes
a factor ~7 in the energy. **This is the most robust quantitative bridge in
the note** — and also the least useful, since it is the quantity least
sensitive to the physics we care about. Break point: none, but don't mistake
robustness for informativeness.

### E4. Mutual-friction coefficients B, B' — DOES NOT TRANSFER
He II: B ~ O(1) at laboratory temperatures (NIST recommended values:
B = 1.53 at 1.30 K → 1.19 at 1.60 K; B' = 0.03–0.10). NS core theory:
B ~ 10^-4 (Alpar, Langer & Sauls 1984); crust: 10^-10–10^-2. The
microphysics is unrelated: roton/phonon scattering off vortex cores in He II
vs. electron scattering (core) or phonon/Kelvin-wave emission (crust) in the
star. **Break point:** four orders of magnitude in the coefficient *and* a
different scattering mechanism. Worse, the *regime* differs: He II at lab T
is the strong-drag limit; the NS core is the weak-drag limit that He II only
approaches as T → 0. **The legitimate direction is NS → lab** (the star
anchors the T→0, weak-drag asymptote), never lab → NS. Any vacuum model that
needs a dissipative coefficient must take the NS number, not helium's.

### E5. Quantum-turbulence statistics (Kolmogorov −5/3, etc.) — DOES NOT TRANSFER to glitches
Lab quantum-turbulence work reports energy spectra (Kolmogorov −5/3 in the
quasi-classical regime; Vinen/ultraquantum spectra in the random-tangle
regime). Pulsar glitches are a **slow-drive, pinned-vortex avalanche**
regime — the drive (electromagnetic spin-down) is ~10^10× slower than any lab
drive relative to the dynamical time, and vortices sit pinned for years
between events. **Break point:** different dynamical regime (steady tangle vs.
stick-slip avalanches). Q1's exponent match (α ≈ 1.2–2.0) is about the
*avalanche statistics*, which are drive-agnostic in SOC — it does not imply
the vortex *dynamics* match. Do not cite Kolmogorov spectra as evidence about
glitches.

### E6. Pinning microphysics — DOES NOT TRANSFER
NS crust: nuclear lattice, spacing a ~ 30 fm; pinning sites per intervortex
cell (d/a)^2 ~ 10^18; pinning force per unit length ~10^12–10^13 N/m
(10^15–10^16 dyn/cm, standard models). Lab analogues: He II has no bulk
lattice (wall/impurity pinning only); BECs in optical lattices have
a ~ 0.5 μm and (d/a)^2 ~ 10–100 sites per cell. **Break point:** eighteen
orders of magnitude in site density per cell; the collective-pinning theories
used for NS crust (many weak pins per vortex) operate in a regime no lab
system reproduces. The BEC optical-lattice setup is the *closest* dimensionless
analogue and is still 16 orders off in site density. Avalanche *statistics*
(Q1) are the empirical bridge; pinning *mechanisms* are not portable.

### E7. Finite-temperature damping — DOES NOT TRANSFER
T/T_c ~ 0.01–0.1 (NS) vs 0.5–0.95 (lab He/BEC). In the star the thermal
normal-fluid fraction is negligible (though electrons and superconducting
protons still couple to vortices); in the lab the normal fluid is a
substantial, viscous component that dominates dissipation. **Break point:**
any lab measurement of temperature-dependent dissipation (e.g. the B(T)
tables from NIST) cannot be extrapolated to NS conditions — the functional
form changes, not just the parameter value. The NS lives in the T→0
asymptote; lab data constrains the opposite end.

### E8. Compressibility / the acoustic-metric (analogue-gravity) mapping — TRANSFERS via BEC/He, NOT via NS
The analogue-gravity mechanism (Unruh 1981; Steinhauer 2016, 2019) needs a
compressible superfluid with a well-defined sound speed — realized in BECs
(highly compressible dilute gas) and He II (weakly compressible). A neutron
star is a relativistic, self-gravitating object; its "phonons" are not the
carriers of an analogue metric in any experimentally meaningful sense.
**Break point:** the NS does not participate in the analogue-gravity
correspondence. For the superfluid-vacuum question this means: the *mechanism*
(emergent metrics from superfluid flow) is proven by BEC/He experiments; the
NS contributes *vortex statistics and friction coefficients*, not spacetime
analogy. Keep the two channels separate.

### E9. Fermionic vs. bosonic condensates — MICROPHYSICS DOES NOT TRANSFER; TOPOLOGY DOES
NS superfluids are fermionic Cooper pairs (^1S_0, ^3P_2) with core-bound
Caroli–de Gennes–Matricon states; He II and BECs are bosonic. Vortex-core
spectroscopy, mutual-friction scattering calculations, and gap physics are
entirely different. **What survives:** circulation quantization, the Feynman
rule, reconnection topology, and the HVBK equation *form* — the topological
and hydrodynamic skeleton, not the flesh. Break point: any argument that
depends on what the vortex core is made of.

---

## 4. Bottom line for the superfluid-vacuum question

1. **The honest direction of inference is NS → lab, not lab → NS.** The star
   occupies the T→0, d/ξ→∞, B→0 asymptotic corner of the same HVBK physics.
   Its numbers anchor the extreme regime laboratories cannot reach — they do
   not borrow credibility from laboratory agreement.
2. **Three numbers genuinely constrain a vortex-invoking vacuum model:**
   the avalanche exponent band α ≈ 1.2–2.0 (Q1), the mutual-friction range
   B ≈ 10^-10–10^-2 (Q2's target), and the Feynman-rule vortex density
   n_v = 2Ω/κ at d/ξ ~ 10^9–10^10. A vacuum model whose vortices violate any
   of these is in tension with the only extreme-regime data in existence.
3. **Everything else is analogy.** Gaps, T_c, pinning forces, turbulence
   spectra, and the acoustic-metric mapping either don't transfer (E4–E9) or
   transfer only logarithmically (E3).
4. **The single most load-bearing untested assumption** in the whole bridge:
   Feynman's rule at nuclear density (E1) — assumed by every glitch model,
   observed nowhere near those conditions. If a future observable ever tested
   it and it failed, the NS vortex census (including the ~10^17 figure) would
   need revision. Nothing currently suggests failure; it is flagged because
   the entire quantitative bridge stands on it.

---

## References (sources for numbers in §2)

- Circulation quanta: κ = h/2m_n (NS pairs); κ = h/m_4 = 9.98×10^-8 m^2/s,
  ξ ≈ 0.15 nm (He II) — arXiv:2510.27440 (temporal decay of vortex line
  density in rotating thermal counterflow)
- He II mutual friction B, B' vs T (NIST recommended values) —
  https://srd.nist.gov/jpcrdreprint/1.556028.pdf
- Counterflow line density L ≈ 2.6×10^10 m^-3, spacing ≈ 6.2 μm —
  Zhang & Van Sciver, Nature Phys. 1, 36 (2005)
- BEC vortex lattices, up to ~130 vortices; ξ ≈ 0.2 μm at 4×10^14 cm^-3 —
  Abo-Shaeer et al., Science 292, 476 (2001); arXiv:cond-mat/0106235
- Fast-rotating BEC parameters (Nv = 37–126, R⊥ = 10–19 μm, rv/ξ ≈ 1.4–2.2) —
  numerical/experimental comparison, arXiv:0709.1042
- Rotating He II vortex lattices — Yarmchuk, Gordon & Packard, PRL 43, 214 (1979)
- Mutual friction review (HVBK form, B/B' phenomenology) —
  J. Low Temp. Phys. review, https://link.springer.com/10.1007/s10909-023-02972-4
- NS numbers (κ, n_v, d, N, gaps, T_c, B ranges, pinning) — study_note.md §1,
  this workspace (sources cited therein)
- Glitch avalanche exponents — glitch_universality_note.md (Q1), this workspace
