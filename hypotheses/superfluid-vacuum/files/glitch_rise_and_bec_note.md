# Follow-ups: the glitch-rise hunt (Q5a) + a BEC optical-lattice transport experiment (Q5b)

**Status:** exploratory / literature compilation + one new literature catch + experiment design. NOT a result, NOT a detection claim. Date: 2026-10-03.
**Questions.** (a) Does "fast ≈ theory" (Q2's prompt-coupling result) generalize beyond Vela, or is it a one-pulsar story? (b) Can a BEC in a tunable optical lattice measure the fast/slow pinning-split structure directly — the data gap specified in Q4 §5?

**Answers in one line.** (a) Still a one-pulsar story — but the hunt turned up a *second* Vela glitch with a fast probe (2000 January, rise ≤ 40 s plus a 1.2±0.2 min fast relaxation), and its fast B lands on the same ~10⁻⁴ as the 2016 glitch: within-pulsar reproducibility, n = 2 glitches, 1 pulsar. The Crab's resolved "rises" are the *opposite* phenomenon (slow, days) and belong in the slow column. (b) Yes — specified below as a concrete step-response experiment: sudden rotation-step of the lattice, stroboscopic vortex imaging, two-exponential readout, with quantitative falsification criteria.

---

## Plain-language summary

We went looking for more glitches caught in the act of spinning up, to see whether the fast friction Vela showed in 2016 is a Vela quirk or a general rule. We found one more: Vela's January 2000 glitch, caught by a Tasmanian telescope, spun up in under 40 seconds and then relaxed on a 1.2±0.2-minute timescale — giving the same friction number as 2016 to within the errors. So it's consistent *within* Vela (two glitches, same answer), but no other pulsar has ever been caught fast enough to check. The Crab pulsar, the only other star with a "resolved rise," actually shows the opposite: a slow, days-long extra spin-up — a different process, not the fast one.

Separately, we designed the lab experiment that could test the two-speed behavior directly: a Bose-Einstein condensate (an ultracold atomic cloud that is itself a superfluid) with its vortices pinned to a rotating laser grid. Jerk the grid's rotation suddenly — a tabletop glitch — and watch with a microscope: the cloud should answer in two voices, a fast one set by the true microscopic friction and a slow creep set by the pinning barriers. Turn the laser grid deeper and the slow voice should get exponentially slower while the fast one stays put. If it doesn't, the analogy fails, and we say exactly what "fails" looks like.

---

## PART A — the glitch-rise hunt

### A1. What counts as a "fast probe"

Q2's claim is specific: a *resolved prompt rise* (seconds) probes the unpinned mutual friction B near its microphysical value (~4×10⁻⁴), while day-to-year recoveries probe pinning-suppressed B (10⁻¹⁰–10⁻⁷.⁷). The hunt criterion is therefore strict: a measurement that *resolves the spin-up itself* on timescales ≲ minutes, or a fast (≲ minutes) post-rise relaxation component distinct from the day-scale recoveries. Upper limits from "first observation N hours after" count as weak bounds, not detections.

### A2. Resolved fast rises — the complete census

| # | Pulsar | Glitch | Rise / fast component | Inferred fast B | Data quality |
|---|---|---|---|---|---|
| 1 | Vela (J0835−4510) | 2000 Jan 16 (MJD 51559) | rise **≤ 40 s** (3σ detection limit); fast decay term **τ = 1.2±0.2 min** ("not previously observed"; 25% amplitude / 17% timescale errors) | naive B_eff ≈ 2.0×10⁻⁴ (72 s); rise bound alone → B ≳ 3.6×10⁻⁴ (naive) | **High.** Hobart 14-m single-pulse system, 10-s folds, 3 frequencies (635/990/1390 MHz). Dodson, McCulloch & Lewis 2002, ApJL 564, L85 (arXiv:astro-ph/0111404). Independently verified verbatim 2026-10-03 (see vela2000_verification.md). |
| 2 | Vela (J0835−4510) | 2016 Dec 12 (MJD 57734) | rise **≤ 12.6 s** (90%); overshoot decay **τ_d ≈ 54 s** | B ≳ 5.7×10⁻⁶ (Ashton+2019 2-fluid); naive B_eff ≈ 2.6×10⁻⁴ (54 s); rise-shape fits B_core ≈ 3×10⁻⁵–10⁻⁴ (Graber+2018) | **High.** Mt Pleasant 26-m single-pulse, Palfreyman+2018; Ashton+2019, Nat. Astron. 3, 1143. Already in Q2. |
| 3 | Vela (J0835−4510) | 2021 Jul 22 (MJD 59417.6) | rise **≲ 1 hr** (first IAR/PuMA observation 1 hr post-glitch) | naive B_eff ≳ 4×10⁻⁶ | **Weak — upper limit only.** Sosa-Fiscella+2021; HawkRAO ATel #14808 confirms Δν/ν ≈ 1.25×10⁻⁶. Not a resolved rise. |

**The new-to-our-census catch is #1.** (The paper itself announced the fast term in 2002; it was new to our fast-probe sample, not to the literature.) The Q2 note cited Dodson+2002 only in passing; the 2000 glitch's fast numbers were never folded into the fast-probe sample. Details from the paper: the glitch (Δν/ν = 3.1×10⁻⁶, then the largest recorded for Vela) was auto-detected at Hobart; modeling showed a 40 s spin-up timescale would have produced a 3σ signal, so τ_rise ≤ 40 s. Four relaxation timescales were fitted: 1.2±0.2 min (fast, "not previously observed"), 0.56 d, 3.33 d, 19.1 d. (The abstract rounds the fast term to "about 60 seconds"; Table 1 gives the fitted 1.2±0.2 min — same paper, no version discrepancy. An earlier draft of this note misread this as an ASP-vs-ApJL difference; corrected 2026-10-03.)

**The point that matters:** two independent Vela glitches, 16 years apart, caught by different backends, both show a ~1-minute fast relaxation giving the *same* naive fast B: **2.0×10⁻⁴ (2000, 72 s) vs 2.6×10⁻⁴ (2016)** — both within a factor of ~2 of the microphysical 4×10⁻⁴ (Alpar, Langer & Sauls 1984; Andersson+2006), and mutually consistent within the 2000 term's 17% timescale error. And the 2000 rise bound alone (≤ 40 s) converts naively to B ≳ 3.6×10⁻⁴, i.e. the rise is *consistent with being as fast as theory allows*. Caveat, carried honestly: the naive conversion B_eff = 1/(2πντ) is single-fluid; Ashton's two-fluid treatment of the 2016 rise gives the weaker formal bound B ≳ 5.7×10⁻⁶ because only part of the moment of inertia participates on the rise timescale. Both conversions are reported; the agreement of the two *relaxation* numbers is the model-independent part.

### A3. The Crab — resolved rises that probe the SLOW branch (do not conflate)

The Crab pulsar is the only other pulsar with time-resolved rise structure, and it is the *opposite* phenomenon: a **delayed spin-up** — an extra slow spin-up component lasting hours to days, on top of the (unresolved) prompt jump:

- 1989: ~0.8 d extended spin-up (Lyne, Pritchard & Smith 1993; Lyne+1992, Nature 359, 706)
- 1996: ~0.5 d (Wong, Backer & Lyne 2001, ApJ 548, 447)
- 2004: τ₁ = 1.7±0.8 d; 2011: τ₁ = 1.6±0.4 d (Ge+2020, ApJ 896, 55)
- 2017 Nov: best-resolved gradual rise; prompt rise < 0.48 hr (Ge+2020)
- 2019 Jul: delayed spin-up τ ≈ 18 hr (Shaw+2021, MNRAS 505, L6)

Shaw+2021: this was "the sixth Crab pulsar glitch for which part of the initial rise was resolved in time and **this phenomenon has not been observed in any other glitching pulsars**." The standard reading (Lyne+1992; Alpar+1994; Shaw+2021) is a *second, slower coupling process* — e.g. crustal-plate motion or a distinct superfluid reservoir — not the prompt mutual-friction rise. Dodson+2002 explicitly contrasted their <40 s Vela limit with the Crab's ~0.5 d. **For the fast/slow framework these belong in the slow column** (τ ~ 0.5–2 d → naive B_eff ~ 10⁻⁷–10⁻⁶, squarely in the pinning-suppressed band), and the Crab's *prompt* rise remains unresolved (≤ hours, set by JBO cadence).

### A4. Searched and empty (honest negatives)

- **J0537−6910, NICER era** (Ho+2020b; Abbott+2021a; Ho+2022; new 7-yr timing paper arXiv:2512.19800): 23 glitches measured with NICER, but glitch-epoch uncertainties are ±11–48 d. No rise information at all — cadence-limited, not physics-limited.
- **Vela 2019** (MJD 58515.59): Fermi-LAT epoch MJD 58515.5929(5) (ATel #12481); IAR/PuMA had observations 3 d before/after (Lopez Armengol+2019). Not caught live.
- **Vela 2024** (MJD 60429.87): epoch pinned to ±3.3 s by Mt Pleasant (ATel #16615), Δν/ν = 2.4×10⁻⁶, recoveries 17.3 d + 2.78 d — but Zubieta+2025 (arXiv:2502.06704) states catching a glitch "live" remains a *future goal*. Not caught live.
- **CHIME / UTMOST / MeerKAT / MeerTRAP:** no published resolved glitch rise found (searched 2026-10-03).
- **Dodson, Lewis & McCulloch 2007** (Ap&SS 308, 585, "Two decades of pulsar timing of Vela"): a review of the Mt Pleasant program — Ashton+2019 cites it alongside Dodson+2002 as the prior high-time-resolution work, but it contains no new rise measurement beyond the 2000 glitch.

### A5. Verdict on (a)

**Still a one-pulsar story — but a stronger one-pulsar story.** The fast-probe sample is now n = 2 glitches in 1 pulsar (Vela 2000, Vela 2016), both giving fast B ≈ (2–4)×10⁻⁴, i.e. within a factor of ~2 of the microphysical estimate, and both showing a distinct ~1-minute fast relaxation cleanly separated from the day-scale recoveries. Within-pulsar reproducibility is established; cross-pulsar generalization is not — no other pulsar has any fast-rise constraint, and the only other pulsar with *any* resolved rise (Crab) shows the slow-branch phenomenon. The next Vela glitch caught live (IAR/PuMA is explicitly hunting for it with 3.66-hr daily coverage) would make n = 3; a first fast rise in any *other* pulsar is what would actually generalize the claim.

---

## PART B — BEC + optical lattice: a tabletop glitch experiment

### B1. Why this system, and what it maps to

Q4 §5 specified the gap: static vortex pinning to a co-rotating optical lattice is established (Tung, Schweikhard & Cornell 2006, PRL 97, 240402), dynamical phases exist only in simulation (Kasamatsu & Tsubota 2006, cond-mat/0608656), and no prompt-vs-relaxed transport measurement exists. The proposal below turns the simulation protocol into a measurement.

**Mapping to the neutron star:**

| Neutron star | BEC analog |
|---|---|
| Crust + nuclear lattice (pinning sites) | Optical lattice (engineered pinning sites, tunable depth V₀) |
| Neutron superfluid + vortex array | BEC + quantized vortex array |
| Glitch: sudden crust spin-up, superfluid lags | **Step δω in lattice rotation rate; condensate/vortex array lags** |
| Prompt mutual-friction coupling (fast B ~ 10⁻⁴) | Prompt vortex–thermal-cloud/lattice damping (fast τ, V₀-independent) |
| Pinning-suppressed creep (slow B ~ 10⁻¹⁰–10⁻⁷) | Thermally activated vortex hopping between lattice sites (slow τ ∝ exp(U_p/k_BT)) |
| Pinning barrier vs Magnus drive | Lattice depth V₀ vs step size δω (cf. Kasamatsu force balance F = F_d + F_p + F_vv) |

The Kasamatsu–Tsubota simulations already predict the equilibrium phase structure in (δω, V₀): fully-pinned lattice (⟨S(k_SQ)⟩ > 0.7), inner-pinned/outer-depinned, pre-melting, vortex liquid (δω > 0, incommensurate nucleation), and sliding (⟨S⟩ < 0.25) — with the depinning boundary given analytically by k²V₀Q(kξ) = rδω/[2U(1−δω−Ω)] (their Eq. 4, matching the numerics). What has never been measured is the **time domain**: after a *sudden* step (not their adiabatic ramp), does the angular-momentum transfer split into a fast microscopic response and a slow pinning-creep response?

### B2. Apparatus (design parameters — labeled as choices, not quotes)

- **Atoms:** ⁸⁷Rb BEC, N ≈ 2×10⁵, in a pancake trap: ω⊥ = 2π×20 Hz radial, ω_z = 2π×200 Hz axial. Trap period 2π/ω⊥ = 50 ms sets the fast clock.
- **Rotation:** spin up to Ω = 0.80 ω⊥ by stirring; equilibrate ~2 s → vortex array of ~20–30 vortices, spacing a_v ≈ 5 μm.
- **Optical lattice:** square lattice from two orthogonal 1064-nm standing-wave pairs at small crossing angle → period d_OL ≈ 2–5 μm (commensurate with a_v); depth V₀ tunable 0 → h×10 kHz (≈ 0–50 E_r at this period); rotated by electro-optic beam steering (the rotating-mask method of Tung+2006 is the demonstrated alternative). Columnar sites along z (pancake geometry) mimic the NS crust's columnar pinning.
- **Imaging:** in-situ absorption imaging along z, ~1 μm resolution; **destructive**, so the time series is stroboscopic: prepare → step at t = 0 → hold t → image; ~10–20 runs per time point, t spanning 10 ms → 30 s. (Quantum-gas-microscope single-site readout is the upgrade path; not required.)
- **Thermometry/control:** final evaporation depth sets T/T_c ≈ 0.5–0.9 (tunes thermal activation independently of V₀).

### B3. Protocol

1. **Prepare:** equilibrate BEC at Ω with co-rotating OL (δω = 0) at chosen V₀ — the pinned square lattice of Tung+2006 / Kasamatsu initial state.
2. **Step:** at t = 0, jump the lattice rotation rate Ω → Ω + δω in < 1 ms (≪ trap period) — the tabletop glitch. Scan δω ∈ [−0.15, +0.15] ω⊥ (both signs; the simulations show strong asymmetry) and V₀ ∈ {0, shallow, intermediate, deep}.
3. **Control runs:** identical protocol at V₀ = 0 (no pinning — the ^4He-bulk analog: predicts a *single* fast timescale, no slow arm) and with δω ramped adiabatically (reproduces the Kasamatsu quasi-stationary phases).
4. **Readout per run:** vortex positions {r_j(t)} → structure factor S(k_SQ,t) = (1/N_c)|Σ_j e^{ik·r_j}| (same order parameter as the simulations); condensate rotation Ω_c(t) from the vortex-lattice rotation rate; angular momentum per atom ⟨l_z⟩(t) from vortex count × ⟨r²⟩.

### B4. What gets measured (the two-timescale readout)

Fit the rotation response to two exponentials:

Ω_c(t) = Ω_∞ − A_fast e^{−t/τ_fast} − A_slow e^{−t/τ_slow}

and extract **{τ_fast, τ_slow, A_fast, A_slow}** as functions of **(V₀, δω, T)**. Define the lab ratio **R_BEC ≡ (A_slow/τ_slow⁻¹)/(A_fast/τ_fast⁻¹)** — the slow-branch effective coupling over the fast-branch coupling, the direct analog of Q4's R.

### B5. Predicted signatures

1. **Two timescales, cleanly separated, only when pinning is on.** τ_fast ~ 1/(γω⊥) ~ 0.1–0.3 s (tens of ms with γ ~ 0.03–0.1 from vortex–thermal-cloud damping), set by the *microscopic* dissipation — **independent of V₀**. τ_slow ~ τ₀ exp(U_p/k_BT), U_p ∝ V₀ (Reijnders–Duine pinning potential used by Kasamatsu): at V₀ = h×10 kHz, T = 50 nK, U_p/k_BT ~ 10 → suppression ~5×10⁻⁵ → τ_slow ~ seconds. **R_BEC should fall exponentially as V₀ deepens at fixed T** — the lab version of Q4's barrier-in-thermal-units control parameter.
2. **Depinning crossover in the step size.** Below a critical δω_c(V₀) (Kasamatsu Eq. 4 gives the scale), the step is absorbed by creep — slow branch dominates. Above it, prompt depinning/sliding — fast branch dominates, ⟨S(k_SQ)⟩ collapses below 0.25 on the fast timescale. The crossover maps the simulation's phase boundary in the time domain.
3. **Sign asymmetry (sharp test of the simulation).** δω > 0 (lattice spun *up*): interstitial vortex nucleation → pre-melting/liquid signatures — broadened S(k), excess ⟨l_z⟩ growth beyond rigid-body, matching Kasamatsu's incommensurate phase. δω < 0 (lattice spun *down*): clean drag of the pinned lattice → textbook two-exponential response, condensate spins down. Observing the asymmetry confirms the drive-vs-pinning force balance rather than generic relaxation.
4. **V₀ = 0 control:** single exponential at τ_fast — the ^4He-bulk prediction (no pinning lattice → no slow arm), tested in the same apparatus.

### B6. What would falsify the analogy (stated in advance)

1. **No timescale separation:** if the response is always single-exponential regardless of V₀, T, δω — the slow arm doesn't exist here, and the two-timescale structure is not generic to pinned BEC vortices.
2. **τ_fast depends on V₀:** if the "prompt" response is itself pinning-suppressed (deep lattice slows even the initial response), the fast≈microscopic leg fails — there is no clean fast probe in this system.
3. **τ_slow doesn't scale with the barrier:** if the slow timescale is insensitive to V₀ and T (no exp(U_p/k_BT) dependence), the slow arm isn't pinning creep — it's something else, and the mapping to NS recoveries breaks.
4. **Prompt response ≠ independent microscopic damping:** measure the microscopic damping independently (V₀ = 0 step response, or vortex-lattice equilibration rate without lattice). If the V₀ > 0 prompt response differs from it, "prompt coupling sees friction" is false here.

Any one of these turns the experiment from a confirmation into a constraint: it would show the fast/slow split is *not* an automatic consequence of pinning, which weakens the Q4 claim that the split's *existence* is the generic fingerprint.

### B7. Honest caveats (do not overclaim)

- **Regime distance:** BEC is weakly interacting, 2D/pancake, T/T_c ~ 0.5–0.9; the NS core is strongly interacting, 3D, T/T_c ~ 0.01. Thermal creep here vs. possibly quantum creep there (cf. a-MoGe in Q4 §3). The comparison is structural — two timescales, barrier-controlled ratio — not a numerical calibration of B.
- **Destructive imaging:** the time series is reconstructed stroboscopically; run-to-run vortex-number fluctuations are the dominant noise. Requires τ_slow/τ_fast ≳ 10 for a credible two-exponential fit — the V₀/T scan is designed to guarantee this lever arm.
- **Phenomenological damping:** the γ in Kasamatsu's GP equation is put in by hand; the experiment must *measure* the microscopic damping (control B4) rather than assume the simulation's value.
- **What it can't do:** it cannot tell us the vacuum's pinning sites (Q4 §8's open problem) — it can only show that *if* a quantum fluid has tunable pinning, the fast/slow split appears with a barrier-controlled ratio, and absent pinning it doesn't.

### B8. Bottom line for the thread

If built and the signatures (B5) appear, the BEC becomes the **first system where both branches of R are measured in one tunable apparatus** — succeeding where ^4He (no pinning lattice) and the 2006 static experiment (no dynamics) could not. That would promote the two-timescale split from "seen in two very different systems" (NS + superconducting I–V) to "reproducible under controlled pinning" — the closest thing to a laboratory verification the Q4 fingerprint can get. If the falsifiers (B6) trigger instead, the honest conclusion is that pinning alone doesn't guarantee the split, and the NS/SC similarity needs another explanation. Either outcome is informative; the experiment is designed so both are publishable.

---

## Files and sources

- This note: `~/workspace/superfluid-vacuum/glitch_rise_and_bec_note.md`
- Prior notes: `mutual_friction_note.md` (Q2), `two_timescale_note.md` (Q4)
- **(a):** Dodson, McCulloch & Lewis 2002, ApJL 564, L85 (arXiv:astro-ph/0111404) — Vela 2000 rise ≤ 40 s, fast decay 1.2±0.2 min (independently verified verbatim 2026-10-03); Palfreyman+2018, Nature 556, 219 — Vela 2016 single-pulse; Ashton+2019, Nat. Astron. 3, 1143 (arXiv:1907.01124) — 2016 rise ≤ 12.6 s, τ_d ≈ 54 s; Graber, Cumming & Andersson 2018, ApJ 865, 23 — rise-shape B fits; Sosa-Fiscella+2021 (ATel #14806), Olney ATel #14808 — Vela 2021 ≲1 hr; Zubieta+2025, arXiv:2502.06704 — Vela 2024, live catch still a goal; Ge+2020, ApJ 896, 55 — Crab 2004/2011/2017 delayed spin-ups; Shaw+2021, MNRAS 505, L6 (arXiv:2103.13180) — Crab 2019 τ≈18 hr; Lyne, Pritchard & Smith 1993 — Crab 1989; Wong, Backer & Lyne 2001, ApJ 548, 447 — Crab 1996; Ho+2020b / Abbott+2021a / Ho+2022 / arXiv:2512.19800 — J0537 NICER (no rise data); Lopez Armengol+2019 — Vela 2019; ATel #12481 (Fermi-LAT), ATel #16615 (Mt Pleasant) — Vela 2019/2024 epochs
- **(b):** Tung, Schweikhard & Cornell 2006, PRL 97, 240402 (arXiv:cond-mat/0607697) — static pinning baseline; Kasamatsu & Tsubota 2006 (arXiv:cond-mat/0608656) — dynamical phases, force balance, Eq. 4 depinning boundary; Reijnders & Duine 2004, PRL 93, 060401 — U_pin analytic form used in the proposal's barrier scaling
