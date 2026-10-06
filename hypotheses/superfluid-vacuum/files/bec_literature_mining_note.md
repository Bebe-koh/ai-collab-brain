# BEC literature mining: does existing data already show the two-timescale split?

**Status:** exploratory / literature survey. NOT a result, NOT a detection claim. Date: 2026-10-03.
**Question (round 2):** before building the tabletop experiment specified in `glitch_rise_and_bec_note.md` Part B, check whether published ultracold-atom data *already* test the fast/slow pinning-split structure — i.e., rotation-step / lattice-depth-quench / lattice-rotation experiments with time-resolved vortex or condensate-rotation readouts.

## Headline verdict

**No.** No published experiment measures a two-timescale (fast + slow) vortex-transport response in a BEC with a pinning lattice. The Q4 "honest negative" survives a full survey. What the literature *does* contain is:

1. **A confirmed control, not a gap:** the MIT spin-down experiment (Abo-Shaeer, Raman & Ketterle 2002) shows exactly the single-exponential, strongly temperature-dependent relaxation the framework predicts *when there is no pinning lattice* — the unpinned fast leg, measured, with the rate (~1 s⁻¹) matching theory. This is the ^4He-bulk analog the proposal's V₀=0 control was modeled on, already in the literature.
2. **Static pinning only:** Tung+2006 (co-rotating lattice, triangular→square crossover) and Williams+2010 (rotating lattice, vortex number vs Ω and depth) — both equilibrium/steady-state, no time domain.
3. **Time-resolved transport without pinning:** ENS/JILA spin-up and crystallization experiments — single-timescale, hundreds of ms, temperature-insensitive formation.
4. **Fast-leg-only probes:** Tkachenko oscillations (damping consistent with mutual-friction theory), single-vortex real-time tracking — no slow arm, no lattice.

The dynamical rotating-lattice experiment the proposal needs has never been done. Williams+2010's apparatus (rotating 2D optical lattice, acousto-optic rotation) is the closest existing hardware — the proposed experiment is best framed as a *time-resolved extension of Williams*, not a from-scratch build.

---

## 1. What would count as existing data

To test the split, an experiment needs **all three**: (i) a tunable pinning lattice, (ii) a sudden drive step (rotation or depth quench — not an adiabatic ramp), (iii) a time-resolved rotation/vortex readout fit for a two-exponential decomposition. Steady-state vortex counts vs drive, static structure factors, and unpinned spin-up/down each supply at most two of the three.

## 2. Paper-by-paper table

| # | Paper | What was measured | Timescales observed | Two-exponential? | Slow-τ scaling with depth/T | Relevance |
|---|---|---|---|---|---|---|
| 1 | Abo-Shaeer, Raman & Ketterle 2002, PRL 88, 070409 (arXiv:cond-mat/0108195) | **Spin-down**: stir 200 ms (~130 vortices, Na), stop drive, watch lattice decay in static trap via 10 nondestructive phase-contrast images (100 ms spacing); aspect ratio → rotation rate Ω(t) | **Single exponential**, τ ~ 0.4–2 s; rate increases dramatically with T (relaxation time ×17 shorter for +60% T); absolute rates ~1 s⁻¹, matching Fedichev/Muryshev theory | **No** — one timescale | No lattice; T-dependence is thermal-cloud friction, not pinning creep | **Confirmed control**: no pinning → no slow arm, exactly as the framework predicts. Two-step model (condensate→thermal cloud→trap anisotropy) parallels helium spin-down. Crystallization (formation) is T-independent, hundreds of ms — a *different* single timescale, not a second arm of one response. |
| 2 | Madison, Chevy, Bretin & Dalibard 2000/2001 (PRL 84, 806; PRL 86, 4443) | Stirring onset: ellipticity oscillations → collapse as vortex lattice forms (destructive TOF images) | Formation/nucleation: few × 100 ms | No | No lattice | Spin-up transient, unpinned. Single timescale. |
| 3 | Haljan, Coddington, Engels & Cornell 2001 (arXiv:cond-mat/0106362) | Spin up the *normal cloud* by evaporation; condensate nucleates vortices; threshold in cloud rotation for first vortex | Steady-state rotation up to 0.94 ω⊥; nucleation threshold | No | No lattice | Drive mechanism, not a step response. |
| 4 | Coddington, Engels, Schweikhard & Cornell 2003, PRL 91, 100402 | **Tkachenko oscillations** of the vortex lattice (elastic shear waves), frequencies measured | Mode periods ~100s ms; strong damping observed | No | No lattice | Fast-leg probe: lattice elasticity + mutual-friction damping. Theory (Matveenko 2011, arXiv:1101.0269) computes damping rates consistent with the observed strong damping. No pinning, no slow arm. |
| 5 | Tung, Schweikhard & Cornell 2006, PRL 97, 240402 (arXiv:cond-mat/0607697) | **Static** vortex pinning to co-rotating square/triangular OL: orientation locking, triangular→square structural crossover vs pinning strength U_pin/μ = 0.049–0.143 | None (equilibrium images) | N/A — no dynamics | N/A | Pinning exists and is tunable — the proposal's hardware premise. But zero time-domain data. |
| 6 | Williams, Al-Assam & Foot 2010, PRL 104, 170402 (arXiv:1001.0865) | **Rotating 2D OL** (⁸⁷Rb, lattice constant 2 μm, depth 100–4000 Hz): vortex number vs lattice rotation Ω and depth; lattice ramped from Ω=0 | Steady-state counts only | No | Depth changes the *nucleation regime* (deep lattice → linear N_v(Ω), Josephson-array physics) but no time series | **Closest existing apparatus** (rotating OL via acousto-optic deflectors) — but the measurement is N_v(Ω, V₀) at equilibrium, not a step response. The proposal = this apparatus + stroboscopic time resolution + step protocol. |
| 7 | Shin group 2015, PRA 91, 013603 (arXiv:1411.1847) | Circular *shaking* of anharmonic magnetic trap → circulating condensate relaxes into vortex lattice; temporal evolution presented; thermal-cloud role | Relaxation on ~seconds (circulation → lattice) | No (single relaxation) | No optical lattice — shaken *magnetic* trap | Time-resolved spin-up without pinning. Shaken-*optical*-lattice experiments in the literature are all Floquet band engineering (no vortices). |
| 8 | Rakonjac et al. 2015 (arXiv:1510.04897) | Formation + decay of vortex lattice in hybrid trap via automated vortex detection; order/disorder quantification | Formation and decay tracked | No two-arm structure | No pinning lattice | Methodology reference (image-analysis), not a split test. |
| 9 | Freilich et al. 2010, Science 329, 1182 | **Real-time** single-vortex-line and dipole dynamics via minimally destructive imaging | Vortex precession, dipole orbits | No | No lattice | Proves in-situ time-resolved vortex tracking is feasible — the proposal's readout, minus the lattice. |
| 10 | Shin group 2015 (arXiv:1502.03542) | Critical velocity for vortex shedding past a moving obstacle | Steady-state threshold | No | No lattice | Different phenomenon (shedding, not pinning creep). |

### Theory/simulation (not data — listed to keep the boundary clean)

| Paper | Content |
|---|---|
| Kasamatsu & Tsubota 2006 (arXiv:cond-mat/0608656) | Rotating-OL dynamical phases (pinned / partial / sliding / liquid) — **simulation only**; the proposal's phase map |
| Reijnders & Duine 2004, PRL 93, 060401 | U_pin analytic form — theory input to the proposal's barrier scaling |
| Mithun, Porsezian & Dey 2016, PRA 93, 013620 (arXiv:1601.00071) | Disorder-induced vortex-lattice melting — simulation |
| Kuiri, Mithun & Dey 2024 (arXiv:2406.00757) | Disorder pinning of binary-BEC lattices — simulation |
| Ancilotto & Reatto 2026 (arXiv:2404.13705) | OL + vortex statics/dynamics, T=0 GP theory — includes pinning *barrier* calculations for vortex motion, but no experiment |

## 3. Rotating-bucket context (non-BEC)

The classic rotating-bucket spin-down experiments are in helium, not BECs: sudden stop of a rotating container, vortex array decays via mutual friction — the direct ancestor of the Abo-Shaeer two-step model (there: container→normal fluid→vortices; here: condensate→thermal cloud→trap anisotropy). The Helsinki ³He-B group additionally measured vortex-front propagation into vortex-free flow with a laminar→turbulent→quantum-turbulent crossover in dissipation vs T. All single-effective-timescale in Ω(t); none involve a pinning lattice, so none test the split. Noted for completeness — the BEC rotating-trap experiments above are the closer analogs.

## 4. Searched and empty (honest negatives)

- **Lattice-depth quench with vortices:** no published experiment. Quench literature in OLs is about Mott physics / Floquet bands, not vortex transport.
- **Time-resolved rotating-lattice transport:** none. Williams+2010 is the only rotating-OL vortex experiment and it is steady-state.
- **Shaken-lattice vortex transport:** the "shaken lattice" literature is Floquet engineering (band inversion, roton-maxon spectra — e.g. the 2023 molecular-BEC work); the one shaken-*trap* vortex experiment (Shin 2015) has no lattice.
- **Vortex creep / depinning in BEC:** all theory/simulation (see table above). No experimental depinning-threshold or creep-rate measurement with an OL.
- **CHIME/UTMOST-style "catch it live" equivalent:** n/a — this is the pulsar side, covered in the Q5a note.

## 5. Verdict: what exists, what's missing

**What exists:**
- The fast leg is measured and understood: unpinned spin-down (Abo-Shaeer: single exponential, τ ~ 1 s, strong T-dependence, theory-matched), Tkachenko damping, single-vortex tracking.
- The no-pinning control prediction is *confirmed*, not just asserted: Abo-Shaeer's single-exponential decay is exactly what the framework expects without a lattice — and the proposal's V₀=0 control run would reproduce this paper.
- Static pinning is established (Tung+2006) and rotating-lattice hardware exists (Williams+2010).
- Time-resolved vortex imaging is demonstrated (Freilich+2010; Abo-Shaeer's 10-shot phase-contrast sequences).

**What's missing — only a new experiment can get it:**
1. Any dynamical (step/quench) response of a vortex array *in the presence* of a pinning lattice.
2. The two-exponential decomposition: τ_fast (V₀-independent) vs τ_slow (exp(U_p/k_BT)).
3. The depinning crossover in step size δω_c(V₀) and the δω sign asymmetry.
4. An experimental R_BEC (slow/fast coupling ratio) in *any* system with tunable pinning.

**Refinement to the proposal from this survey:** the Abo-Shaeer protocol (stop the drive, watch Ω(t) decay via aspect-ratio/distortion imaging) is a proven, published readout for the *unpinned* leg — the proposal's V₀=0 control can cite it as a calibration rather than a prediction. And the cheapest path to the full experiment is a time-resolved upgrade of the Williams+2010 rotating-lattice apparatus, which already solves the hard problem (rotating a 2D OL about the condensate axis with acousto-optic control).

**Bottom line:** the literature confirms every *component* the proposal assumes (fast leg, control behavior, static pinning, readout techniques) and contains *none* of the two-timescale data the proposal is designed to produce. The experiment remains the only route — and it just got cheaper to justify, because half of it already exists in the literature.

## References

- Abo-Shaeer, Raman & Ketterle, PRL 88, 070409 (2002); arXiv:cond-mat/0108195
- Madison et al., PRL 84, 806 (2000); PRL 86, 4443 (2001)
- Haljan, Coddington, Engels & Cornell, arXiv:cond-mat/0106362 (2001)
- Coddington, Engels, Schweikhard & Cornell, PRL 91, 100402 (2003)
- Tung, Schweikhard & Cornell, PRL 97, 240402 (2006); arXiv:cond-mat/0607697
- Williams, Al-Assam & Foot, PRL 104, 170402 (2010); arXiv:1001.0865
- Kasamatsu & Tsubota, PRL 97, 240404 (2006); arXiv:cond-mat/0608656
- Freilich et al., Science 329, 1182 (2010)
- Shin group: arXiv:1411.1847 (PRA 91, 013603 (2015)); arXiv:1502.03542
- Rakonjac et al., arXiv:1510.04897 (2015)
- Matveenko, PRA 83, 033604 (2011); arXiv:1101.0269 (Tkachenko damping theory)
- Reijnders & Duine, PRL 93, 060401 (2004)
- Mithun, Porsezian & Dey, PRA 93, 013620 (2016); arXiv:1601.00071
- Kuiri, Mithun & Dey, arXiv:2406.00757 (2024)
- Ancilotto & Reatto, arXiv:2404.13705 (2026)
