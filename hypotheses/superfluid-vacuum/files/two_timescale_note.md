# Q4: The two-timescale pinning signature — is the suppression ratio universal?

**Status:** exploratory / literature compilation + calculation. NOT a result, NOT a detection claim. Date: 2026-09-25.
**Question:** neutron-star superfluidity shows a prompt-vs-relaxed split (fast probes see near-microphysical coupling, slow probes see pinning-suppressed coupling). Define R = (slow response)/(fast response) per pinned quantum fluid. Is R universal, or system-dependent? What sets it?
**Answer in one line:** R is **not** universal — it spans ~30 orders of magnitude even within a single superconductor sample as the drive varies. What is generic is the *existence* of the two-timescale split (prompt ≈ microphysical, relaxed = suppressed); its *magnitude* is set by the pinning barrier in thermal units, the drive, and dimensionality.

---

## Plain-language summary

Every pinned quantum fluid answers a sudden push in two voices: a fast one that sees the true, microscopic friction, and a slow one that sees friction choked down by pinning. We asked whether the *ratio* of slow-to-fast is the same everywhere — a universal number that could fingerprint pinned quantum fluids across the universe. It isn't. In neutron stars the slow branch is ~10^-6–10^-3 of the fast branch; in a niobium-selenide superconductor it ranges from ~10^-2 near depinning down to ~10^-31 deep in the pinned regime, all in the same sample. The ratio is set by how tall the pinning barriers are compared to thermal jiggling, and how hard you drive — both vary wildly. But the *pattern* (two timescales, fast ≈ theory, slow << fast) shows up everywhere pinning exists, and is *absent* where pinning doesn't exist (bulk helium) — exactly as the framework predicts. For the vacuum question, this reframes existing bounds (they pin the slow branch near zero) and tells a vortex-vacuum model what shape it must have — but it produces no new prediction.

---

## 1. The definition: R per system

Uniformly: **R = (effective transport coefficient from the slow/relaxed/pinned response) / (transport coefficient from the fast/prompt/depinned response)**, both dimensionless. "Transport coefficient" means whatever coupling appears in that system's equation of motion — B for neutron stars, normalized vortex velocity v/v_c for superconductors. These are the closest comparable dimensionless forms, not identical quantities; the comparison is structural, and §7 states exactly where it strains.

The framework being tested: in a pinned quantum fluid, a *fast* probe (sudden, strong, or depinning drive) measures something near the microscopic coupling, while a *slow* probe (relaxed, subcritical drive) measures an effective coupling suppressed by pinning/creep. R << 1 with R → 1 at depinning.

---

## 2. Neutron stars (reused from Q2 — not recomputed)

- **Fast:** Vela 2016 glitch rise, τ_r ≤ 12.6 s → B ≳ 5.7×10^-6 (Ashton et al. 2019); rise-shape fits B_core ≈ 3×10^-5–10^-4 (Graber et al. 2018). Microphysical benchmark B_mf ≈ 4×10^-4 (Alpar, Langer & Sauls 1984; Andersson et al. 2006).
- **Slow:** 11 resolved glitch recoveries → B_mf = 10^-9.96–10^-7.68 (`q2_work/dong5_glitch.csv`); 105 pulsars timing-noise coupling → B_eff upper bounds 10^-9.87–10^-5.88 (`q2_work/dong105_tau.csv`).
- **R_NS = B_slow/B_fast:** computed directly from the CSVs —
  R_NS ≈ **10^-6.0–10^-3.2** (using Table A recoveries; B_fast = 3×10^-5–10^-4).
- **Caveats (carried from Q2, not softened):** the fast probe samples the core, the slow probe is crust-recovery-dominated — R_NS mixes regions, so part of the "suppression" may be region-mixing rather than pure pinning. The two-component model tension (q_heal ≪ x_s, Dong et al. §6.3) means extra reservoirs participate; the B values inherit it. No entry is a direct measurement of microphysical B.

---

## 3. Superconducting vortices — the cleanest laboratory pair

**Source:** Buchacek et al. 2019, "Experimental test of strong pinning and creep in current–voltage characteristics of type II superconductors" (arXiv:1909.01707). I–V characteristics of 2H-NbSe2 (B = 1 T, T = 4.8–5.5 K) and a-MoGe, fitted within strong-pinning theory. This is the ideal system: **one curve contains both branches** — flux flow (fast, depinned) at high drive, thermal creep (slow, pinned) at subcritical drive.

The fitted characteristic (their Eq. 5):

    v/v_c = j/j_c − 1 + [(k_B T / U_c) ln(v_th / v)]^{2/3}

- **Fast branch:** free flux-flow velocity v_c = (5.2, 4.7, 4.5, 3.8)×10^2 cm/s at T = 4.8, 5.0, 5.2, 5.5 K; flux-flow resistivity follows the Bardeen–Stephen law ρ_ff/ρ_n ≈ B/H_c2 — i.e. the fast branch **recovers the microscopic value**, exactly like the Vela rise recovering ~10^-4.
- **Slow branch:** deep in the pinned regime this reduces to Arrhenius creep with the strong-pinning 3/2 barrier exponent: v ≈ v_th exp[−(U_c/k_B T)(1 − j/j_c)^{3/2}], with extracted barrier U_c ~ 1000 K at T ≈ 5 K → **U_c/k_B T ≈ 200**.
- **R_sc = v_creep/v_c** at matched reduced drive (v_th/v_c fitted as an O(0.1–1) parameter — the paper notes it comes out an order of magnitude above theory, subdominant to the exponential):

| j/j_c | (1−j/j_c)^{3/2} | v/v_th = exp[−200·…] | R_sc (× v_th/v_c ≲ 1) |
|---|---|---|---|
| 0.9 (near depinning) | 0.0316 | 1.8×10^-3 | ~10^-3–10^-2 |
| 0.7 | 0.164 | 5×10^-15 | ~10^-15 |
| 0.5 (deep pinned) | 0.354 | 2×10^-31 | ~10^-31 |

**Second material, same framework:** a-MoGe films give U_c ≈ 30–40 K at T ≈ 3.5 K → U_c/k_B T ≈ 10, so R_a-MoGe ≈ 10^-2–1 over the same drive range; at the lowest T, thermal creep saturates into **quantum creep** v ∝ exp(−S̃/ħ) with S̃/ħ < U_c/k_B T — the suppression stops following temperature and locks to the quantum action.

**What this establishes:** R is violently drive-dependent *within one sample* (~30 decades from j/j_c = 0.9 → 0.5) and material-dependent (2H-NbSe2 vs a-MoGe differ by ~30 decades at the same reduced drive). The controlling parameter is the barrier in thermal units, U_c/k_B T (or S̃/ħ in the quantum regime). There is no single "superconductor R."

---

## 4. Superfluid ^4He — honest partial negative (informative)

- **Fast branch exists and is textbook:** after a sudden change of rotation, the vortex array equilibrates on the mutual-friction time τ_mf ~ 1/(2ΩB) with B ≈ 1.2–1.5 (NIST, 1.3–1.6 K) → τ_fast ~ 0.1–1 s at Ω ~ 1–5 rad/s (Hall–Vinen second-sound lineage).
- **No pinned slow branch exists in bulk ^4He** — because bulk ^4He has **no pinning lattice** (Q3, E6: wall/impurity pinning only). There is nothing for vortices to pin *to* in the bulk, so the two-timescale split has no slow arm.
- Closest slow relaxations in the literature are different physics: post-spin-down vortex-tangle decay L(t) ∝ t^−3/2 (Skrbek et al., PNAS review — turbulence decay, not pinning); torsional-oscillator vortex-slip dissipation (Avenel & Varoquaux 1985 — wall/substrate pinning, no published prompt-vs-relaxed coupling pair).
- **Why this negative matters:** the framework *predicts* the absence — no pinning lattice, no slow branch. He II is the control experiment that confirms the split is a pinning phenomenon, not generic superfluidity.

---

## 5. BECs in optical lattices — honest negative (data gap specified)

- **Static pinning is established:** Tung, Schweikhard & Cornell 2006 (PRL 97, 240402; arXiv:cond-mat/0607697) — vortices pin to a co-rotating optical lattice; orientation locking (triangular) and structural crossover to a pinned square lattice at sufficient depth. This is the closest laboratory realization of the NS crust geometry (engineered pinning sites).
- **No two-timescale transport data exists:** the experiment images static configurations, not prompt-vs-relaxed response. No published R_BEC.
- **Theory expects the same structure:** dynamical simulations of a BEC driven by a rotating lattice (arXiv:cond-mat/0608656) show three dynamical phases vs drive mismatch δω — fully-pinned, partially-pinned, and sliding — i.e. the fast/slow split as a function of drive, mirroring §3. Simulation only, clearly labeled.
- **Specified experiment:** sudden rotation-step of the lattice with time-resolved vortex imaging (now feasible with quantum-gas microscopes): measure the prompt lattice response vs the slow creep toward the pinned configuration.

---

## 6. Charge-density waves — partial (threshold structure, R ill-defined)

- CDWs are the classical prototype of depinning: below threshold field E_T the CDW is pinned (NMR shows only ~2° phase displacement at 0.75 E_T in NbSe3; no steady transport — the "slow" branch is polarization, not creep); above E_T it slides with j_CDW ∝ ((V−V_T)/V_T)^ζ, ζ = 1.23±0.07 (Bhattacharya et al.).
- Because the sub-threshold dc transport is zero (not merely suppressed), a transport ratio R is ill-defined — the CDW exhibits the *threshold* that separates fast from slow, but not a measurable slow transport branch. Not forced into the table.

---

## 7. Master table and verdict

| System | Fast branch (prompt) | Slow branch (relaxed) | R = slow/fast | What sets R |
|---|---|---|---|---|
| Neutron star | glitch rise B ~ 3×10^-5–10^-4 (Vela 2016) | recoveries / timing noise B ~ 10^-10–10^-7.7 | **10^-6–10^-3** | pinning barrier vs Magnus drive; region-mixing caveat (§2) |
| 2H-NbSe2 (SC) | flux flow v_c ~ 4–5×10^2 cm/s, Bardeen–Stephen | thermal creep, U_c/k_BT ≈ 200 | **10^-31–10^-2** (drive-dependent) | U_c/k_BT, reduced drive j/j_c |
| a-MoGe (SC) | flux flow (Bardeen–Stephen) | creep, U_c/k_BT ≈ 10 → quantum creep at low T | **10^-2–1** | smaller barriers; S̃/ħ floor |
| ^4He bulk | τ_mf ~ 0.1–1 s, B ~ 1 | *absent* (no bulk pinning) | N/A | framework predicts the absence |
| BEC + lattice | — | — | **no data** | static pinning seen; dynamics sim-only |
| CDW | sliding j ∝ ((V−V_T)/V_T)^1.23 | pinned (no dc transport) | ill-defined | threshold, not a ratio |

**Verdict on universality: R is not universal.** It spans from ~1 (a-MoGe near depinning) to ~10^-31 (2H-NbSe2 deep pinned), varying by ~30 decades *within one sample* as drive changes, and by ~30 decades *between materials* at fixed reduced drive. The magnitude of R is set by:
1. **Pinning barrier in thermal units** U_c/k_B T (or quantum action S̃/ħ where thermal creep freezes out) — the dominant control;
2. **Reduced drive** (j/j_c; Magnus lag vs pinning force in NS) — R → 1 at depinning by construction;
3. **Pinning regime and dimensionality** (strong single-pin vs weak collective; 3D vs 2D crossover noted in a-MoGe at low fields);
4. **T/T_c**, which sets both the barrier scale and the thermal activation.

**What IS generic:** the two-timescale *structure* — prompt response near the microscopic coupling, relaxed response suppressed by pinning — appears in every pinned quantum fluid with usable data, is absent where pinning is absent (^4He bulk), and the fast branch recovers the microphysical value in both systems where it can be checked (NS: Vela rise vs 4×10^-4; SC: ρ_ff vs Bardeen–Stephen). The *existence and direction* of the split is the fingerprint; the *ratio* is not.

---

## 8. Vacuum framing (interpretive — not a prediction)

*Everything in this section is labeled interpretation. It does not transfer evidential weight.*

If the vacuum were a pinned quantum fluid, the two-timescale structure maps as follows:

- **"Fast probe"** = trans-Planckian vortex dynamics (nucleation, depinning, fast-branch dissipation at E ~ E_Pl). Unobservable by construction — every current bound sits far below it.
- **"Slow probe"** = every low-energy test we have: Lorentz invariance (Fermi-LAT GRBs: E_QG,1 > 7.6 E_Pl ≈ 9.3×10^19 GeV, Vasileiou et al. 2013), GW speed (|c_GW − c|/c ≲ 10^-15, GW170817/GRB 170817A), PPN (γ−1 ≲ 10^-5, Cassini), equivalence principle. All read ~zero deviation.
- **Reframing of existing bounds:** they constrain the *slow branch* near zero — exactly what a pinned vacuum predicts (the pinned branch is dissipationless to within 10^-15–10^-5). This is consistent with Volovik-type emergence (violations only at E ~ E_Pl) but it is *also* consistent with "no vacuum superfluid at all." The bounds do not discriminate; they set the allowed shape.
- **The shape a vortex-invoking vacuum model must have:** pinned, with the fast (dissipative) branch above ~10^19 GeV and the slow branch at zero to current precision. Any model predicting low-energy vacuum friction is already ruled out — this is a real constraint, and it is *stronger* than the avalanche-exponent band (Q1), because it is about dynamics rather than statistics.
- **The open problem this exposes:** a pinned fluid needs pinning *sites*. Neutron stars have the nuclear lattice; superconductors have defects; the vacuum has — what? No vacuum model in the reviewed set (Volovik, Zloshchastiev, Winterberg) specifies a pinning lattice. Until one does, the two-timescale framing is a consistency condition, not a theory.
- **No new prediction is generated.** The observable it suggests — energy-dependent Lorentz violation growing toward the Planck scale — is already the existing LIV search program. Q4 sharpens *why* that program is the right one (it probes the fast branch leaking into the slow regime) but does not add a target.

**Bottom line for the vacuum question:** Q4 upgrades the honest bridge from Q1–Q3. The avalanche exponent (Q1) was generic; the friction range (Q2) was a calibration set; the regime comparison (Q3) set the extrapolation limits. The two-timescale structure is the first *dynamical* fingerprint — specific to pinned quantum fluids, absent without pinning, with the fast branch recovering microphysics in both checkable cases. It does not make the vacuum hypothesis testable by itself, but it tells any future vortex-vacuum model exactly what shape it must take (pinned, fast branch above ~10^19 GeV, slow branch at zero) and what it must supply (pinning sites). That is a specification, not evidence.

---

## Files and sources

- This note: `~/workspace/superfluid-vacuum/two_timescale_note.md`
- R_NS computed from `~/workspace/superfluid-vacuum/q2_work/dong5_glitch.csv` (Table A) and `dong105_tau.csv` (Table B) — see §2
- Buchacek et al. 2019, arXiv:1909.01707 (2H-NbSe2 / a-MoGe I–V, strong pinning + creep): v_c = (5.2, 4.7, 4.5, 3.8)×10^2 cm/s at T = 4.8–5.5 K, B = 1 T; U_c ~ 1000 K; barrier exponent 3/2; a-MoGe U_c ≈ 30–40 K, quantum creep v ∝ exp(−S̃/ħ)
- Avenel & Varoquaux 1985, PRL 55, 2704 (TO vortex-slip dissipation — cited for the He wall-pinning literature, no R extracted)
- Skrbek et al., PNAS review (quantum-turbulence decay L ∝ t^−3/2 — cited as different physics, not used for R)
- Tung, Schweikhard & Cornell 2006, PRL 97, 240402 (BEC vortex pinning, static)
- arXiv:cond-mat/0608656 (BEC dynamical vortex phases, simulation — labeled as such)
- Bhattacharya et al. (CDW depinning exponent ζ = 1.23±0.07, via review arXiv:cond-mat/9907106)
- Vasileiou et al. 2013, PRD 87, 122001 (Fermi-LAT LIV bounds — from study_note.md)
- Prior notes: `study_note.md`, `glitch_universality_note.md` (Q1), `mutual_friction_note.md` (Q2), `vortex_regime_note.md` (Q3)
