# Hypothesis salvage memo v3 — closed-hypothesis ledger
**Date:** 2026-10-06 · **Supersedes:** `hypothesis-salvage-memo-2026-10-06-v2.md`
**Companion to:** `hypothesis-registry-2026-10-03.md`

v3 adds evidence-type and evidence-maturity columns to the registry, splits the
QSE margins by mechanism, tightens the Hercules/ALMA/F3 language, adds a
"Closed only for" boundary line to every card, and records external source
identifiers where they exist. The v1→v2 weakenings are preserved below; v2→v3
changes are listed at the end. The honest asymmetry is kept: two entries
remain "thinnest salvage."

A dead hypothesis is not a wasted one if the kill came with numbers. What each
closed thread left behind: a numerical boundary, a reusable method, or an
explicitly documented dead end.

---

## Executive registry

| Thread | Status | Evidence type | Evidence maturity | Decisive result | Salvaged asset | Next action |
|---|---|---|---|---|---|---|
| Hercules–Corona Borealis Great Wall | Killed | New analysis | High | No matter overdensity in DESI DR1 quasars: δ=+1.6%, p=0.22; δ_m<0.018 (95%, conditional on b_q=2.4); reconciling GRB excess needs b_GRB>27 | Control-cap empirical-null methodology | Archive |
| Refractive-index gravity | Excluded | Analytic closure | High | ~14-decade shortfall, ρc-independent, under stated assumptions A1–A4 | Structural exclusion argument (inverted density hierarchy) | Do not pursue this form |
| QSE dark matter | Parked (impasse) | New analysis (end-to-end numerical) + analytic closure | Medium | Formation end-to-end 2026-10-06: curvaton 182–1317× (threshold caveat at 1.5×10⁻¹² for Δ_cr≳0.44), USR 18–48× nominal (15–108× across ζ_c); β~10⁻⁵ open but fragile — curvaton 3.5× below yet flips at +17% Δ_cr, USR 2.3×/1.7× at ζ_c=1/1.3. Conversion: all classical paths dead; parked status unchanged | Triple no-go (fragmentation) + R1–R8 shattering-bounce spec | Seek mechanism satisfying R1–R8, or falsify as DM |
| GW condensate | Closed (survey) | Literature closure | Medium | Natural GW-propagation deviations closed (speed 10⁻¹⁵, graviton mass, polarization); only silent/GR-like versions survive. NOTE: scalar-polarization bound is open-data, not peer-reviewed; two torsion bounds are preprints | 11-entry constraint table | Do not open thread; live directions have other homes |
| Superradiance trio | Anticipated | Literature closure | Medium | All three substantially covered by 2021–2025 literature (completeness per web-search arXiv IDs; systematic ADS/inSPIRE review not done) | Paper-by-paper map (22 papers) + open-corners list | Adopt bhsr / extend to GWTC-4 if appetite exists |
| 8848 THz | Quarantined | New analysis | Low | Cross-run variant wandering (8845.185/8848.13/8848.85); digitological anchor fenced as internal diagnostic, not evidence | Regression-artifact diagnostic (non-convergence across runs) | Do not cite as discovery |
| Neptune/Uranus β | Fit artifact | Analytic closure | High | Universal β predicts the WRONG SIGN of the asymmetry (0.75 predicted vs 5–10 observed); per-planet fits have no predictive content | Non-universality check | Closed |
| F3 compact objects | Three logically distinct failure modes | Literature closure | Medium | Budget (10³–10⁴ short), microlensing at own masses (≤1%), false undetectability premise | Asteroid-mass PBH window as surviving sliver (not F3's) | Restrict future scans to sliver |
| Kerr/CS tunneling | Mechanism dead | Analytic closure | High | B~10¹⁸⁴–10²²¹; tunneling excluded by 50–250 orders of magnitude per channel | Classical driven program: R(t) statistic, veto chain, ALMA search | Continue real-data program |
| Kerr/CS first real-data bound | Null (first look) | Null search | High | No qualifying 55.6° tanh transient in ~104 min; within tested morphology (tanh) and τ=10–120 s, amplitudes above ~6–8° excluded for the analyzed coverage (3 EBs) — per-epoch, NOT a global rate limit | Transient-search pipeline + surrogate-null machinery | Extend to remaining 6 EBs + 2 more days |
| Pulsar–white-hole | Dead (relabeling) | Analytic closure | Medium | 10²–10⁵ short energetically (lifetime-integrated Galactic budget); no differing observable; WHs classically unstable | Triage template (energetics + distinguishability) | Closed unless a differing prediction is named |
| Dipole repeller / void flow | No residual / constrained | Literature closure | Medium | Repeller = linear-theory void; extra coherent flow ≲ tens of km/s (order-of-magnitude synthesis, not a formal bound) | Bound on extra coherent velocity component | Closed; bulk-flow debate is systematics work |

*Evidence maturity is a rating of evidence quality and reproducibility — not a
subjective score of how likely the conclusion is.*

---

## Evidence cards

### 1. Hercules–Corona Borealis Great Wall

- **Claim:** The ~50% GRB excess in a 50°-radius cap at (RA 215.94°, Dec +49.51°),
  z∈[1.6,2.1] (34 vs 22.6 expected, p≈0.0175 look-elsewhere corrected) is a
  Gpc-scale matter overdensity.
- **Data:** DESI DR1 LSS `QSO_NGC_clustering.dat.fits` (793,229 quasars,
  0.8<z<3.5, v1.5pip iron) with completeness weights; redshift slice exactly
  1.6<z<2.1 (230,520 raw / 233,113 weighted quasars); randoms
  `QSO_NGC_0_clustering.ran.fits` (11.6M rows) for the angular selection
  function. HCB cap: 116,025 weighted (113,633 raw) quasars; expected 114,162.
- **Statistic:** δ = N_cap/N_exp − 1 against an empirical null of 500 control
  caps (50° radius, random centers, N_exp ≥ 20% of HCB cap's); p = fraction of
  control caps with δ ≥ δ_HCB.
- **Threshold:** No pre-registered exclusion threshold in the note — assessed
  post-hoc against the empirical null. **No preregistration of the quasar test
  itself.** (The original GRB p-value was look-elsewhere corrected in the prior
  analysis.)
- **Assumptions:** Quasar bias b_q≈2.4 at z~2 (DESI DR1 QSO clustering);
  GRB slice/geometry as published; DESI NGC footprint overlap conditioned via
  randoms (f_cap=0.49). **Predefinition check:** the cap geometry came from the
  GRB-clustering claim, fixed before the quasar test — not selected from
  quasar data. The control caps handle the *spatial* look-elsewhere for the
  quasar test, but not upstream choices inherited from the GRB claim: cap
  radius (50°), redshift interval (1.6–2.1), and the original GRB selection.
- **Result:** δ_HCB = +0.0163±0.0030 (Poisson); controls +0.0052±0.0170;
  z = +0.65σ; **p = 0.218**. 95% one-sided: δ_q<0.044. Conversion
  **δ_m ≈ δ_q/b_q**: 0.044/2.4 → **δ_m<0.018**, **conditional on b_q=2.4**
  (the note adopts this value; a much lower effective bias would weaken the
  limit, but no plausible bias model does so — b_q uncertainty itself is not
  propagated). Reconciling the GRB excess needs **b_GRB>27** (95% lower
  limit; literature b_GRB~2–5). Control sd (1.7%) is 5.7× the Poisson error —
  a naive Poisson test would have falsely claimed 5.4σ. Robust under
  unweighted counts and narrower slice.
- **Reproduction:** `~/workspace/grb/desi_cap_test.py`, `kappa_xcheck.py`,
  `build_kappa.py`; products in `~/workspace/grb/crosscheck_products/`
  (`desi_cap_result.json`, `control_caps.csv`); venv `~/workspace/grb/venv`.
  External: DESI DR1 public LSS data release (files named above; no paper DOI
  recorded in the note). No git VCS, no checksums, no rerun log recorded.
- **Residual:** The GRB-count excess stands as an unexplained ~2% fluctuation,
  not evidence of mass structure. The Planck κ leg was attempted but is
  uninterpretable (map validation failed: κ×QSO cross-power S/N=0.9).
- **Closed only for:** a Gpc-scale matter overdensity in the HCB cap (50°
  radius, RA 215.94° Dec +49.51°, z∈[1.6,2.1]) as traced by DESI DR1 quasars
  with b_q≈2.4.

### 2. Refractive-index gravity ansatz

- **Claim:** n(r,ρ) = 1 + 2GM/(rc²) + α(ρ/ρc)² produces dark-matter-like
  dynamics (extra light bending / effective potential).
- **Data:** Solar-system test precisions — light deflection fractional
  ε≈10⁻⁴ (VLBI γ), Shapiro delay ε≈2×10⁻⁵ (Cassini); densities: IPM
  ~10⁻²⁰ kg/m³ (1 AU), galactic ~1.7×10⁻²¹ kg/m³.
- **Statistic:** Analytic: deflection bound α(ρ₁/ρc)² ≤ 8.4×10⁻²⁰ vs galactic
  requirement δn_gal = α(ρ_gal/ρc)² ~ v_c²/c² ≈ 5×10⁻⁷.
- **Threshold:** Exclusion when the required coupling exceeds the bound at
  *every* ρc (both scale as ρc², so the gap is ρc-independent).
- **Assumptions:** (A1) ρ = local ambient baryonic density; (A2) ansatz
  governs light propagation; (A3) solar-wind profile ρ∝r⁻² (conservative —
  underestimates coronal densities); (A4) stated test precisions.
- **Result:** Max achievable δn_gal = 3.3×10⁻²¹ vs needed 5×10⁻⁷ —
  shortfall factor **1.5×10¹⁴ (~14 decades), ρc-independent**. Structural
  reason: the density hierarchy is inverted (solar system denser than
  galaxies, but better tested). Sign tension: α>0 needed for enhancement
  contradicts the registry's Slippery Saturation module (wants α<0-like
  behavior). Also: the ansatz as written cannot move stars (light only),
  so flat rotation curves were never reachable without a new matter coupling.
- **Reproduction:** `~/workspace/rhm/bound_calc.py`; plot
  `~/workspace/rhm/refractive_index_exclusion.png`. External: VLBI γ and
  Cassini Shapiro precisions are published solar-system results (no DOIs
  recorded in the note). No git VCS, no checksums recorded.
- **Residual:** None for this functional form. Escape hatches (vacuum field,
  screening, step feature) are new theories requiring their own derivations.
- **Closed only for:** the stated n(r,ρ) functional form under assumptions
  A1–A4.

### 3. QSE / Planck-remnant dark matter

- **Claim:** Planck-mass relics from PBH formation constitute all dark matter
  (β targets: 2×10⁻¹⁹ at M~10⁹ kg; 1.5×10⁻¹² at M~6×10²² kg).
- **Data:** Literature — Trivedi & Loeb arXiv:2509.20533 (Gaussian ruled out
  by LIGO); Pi & Sasaki arXiv:2112.12680 (curvaton GW floor); Abe et al.
  arXiv:2209.13891 (USR tail + induced GWs); bounce/remnant literature survey
  (Rovelli–Vidotto, Ashtekar–Olmedo–Singh, Haggard–Rovelli, erebons,
  memory burden); analytic collapse calculations (this work).
- **Statistic:** (Formation) induced-GW floor vs LIGO bound at fixed β.
  (Conversion) abundance bar: N=M/m_Pl relics per progenitor (f_sh~0.5).
- **Threshold:** LIGO/Virgo/KAGRA O3 stochastic bound Ω_GW ≲ 5×10⁻⁹;
  conversion needs f_sh~O(1), i.e. 4.6×10¹⁶ / 2.8×10³⁰ relics per progenitor.
- **Assumptions:** Narrow peaked spectrum (Σ≲0.1); curvaton r_dec≲0.1 /
  USR inflection-point tuning; radiation domination at formation
  (r_dec~10⁻³); near-spherical collapse; ≤1 relic per trapped piece; stable
  relics (no mechanism endorsed).
- **Result:** *Formation viable (contingent), by mechanism:* **curvaton**
  (small decay fraction): induced-GW floor below the O3 bound by
  **182–1317× (end-to-end 2026-10-06)** at the briefing β targets (182× at
  1.5×10⁻¹² with threshold caveat for Δ_cr≳0.44; 1317× at 2×10⁻¹⁹, robust);
  **USR** exponential tail: below by **18–48× nominal, 15–108× across
  ζ_c∈[0.5,1.3] (end-to-end)** (17.9× at 1.5×10⁻¹², formal — no in-band
  bound, the operative BBN integral bound is 6787× below; 48× at 2×10⁻¹⁹).
  At T&L's illustrative β~10⁻⁵
  the [EST] "marginal within ~3×" was recomputed end-to-end (2026-10-06):
  **curvaton** floor Ω_GW,0=1.64×10⁻⁹, nominally 3.5× below O3 — but
  **threshold-fragile**: floor ∝ Δ_cr⁸, so a ~17% upward threshold shift
  flips it to excluded (literature Δ_cr range 0.2–0.6 spans 11× safe to
  600× excluded); **USR** 2.56×10⁻⁹ at ζ_c=1 (2.3× below), 1.7× below at
  ζ_c=1.3 — nominally survives, approximation-sensitive. Verdict: the
  β~10⁻⁵ sub-case **remains open, with "marginal" as the result rather
  than a stepping stone** — the conclusion is controlled by modeling
  choices whose uncertainty exceeds the nominal margin. Briefing-target
  margins are now **end-to-end** (`formation_endtoend_note.md`,
  2026-10-06); [EST] flags retired for formation. Parked status unchanged
  (conversion impasse stands);
  fine-tuning relocates to tail shape.
  *Conversion dead classically:* bounce — every published model bounces
  coherently → 1 remnant/progenitor (f~m_Pl/M), short by 10¹⁶–10³⁰,
  structurally. Fragmentation — triple no-go: (1) R_s(M_J)≈1.1λ_J, so every
  gravitational fragment is a black hole (coincidence exact at O(1),
  density-independent); (2) the parent traps after only ~400× density
  amplification, letting at most ~20 sub-scales unlock (realistic spectra:
  a handful, all trapped); (3) trapped pieces can't subdivide → O(1–20)
  relics vs 10¹⁶–10³⁰ needed.
- **Reproduction:** Fragmentation numbers in
  `~/workspace/goals/qse-remnant-dark-matter-exploration/hidden_files/frag_check.py`;
  bounce = literature survey (no code). Formation: `marginal_beta_case_note.md`
  + `marginal_beta_calc.py` (β~10⁻⁵ end-to-end redo, 2026-10-06; also fixed a
  ~10× USR GW-reduction bug in `endtoend_calc.py`, upgrading briefing-target
  USR verdicts to 48×/18× below — algebraic fix only, model uncertainty
  remains); full formation script for all briefing targets running.
  External: arXiv:2509.20533,
  arXiv:2112.12680, arXiv:2209.13891. **Remaining gap:** the dedicated
  peak-theory + critical-collapse calculation at the relevant k_* — the
  corrected USR margins should not be treated as secure until it exists.
  No git VCS, no checksums recorded.
- **Residual:** The shattering-bounce requirements spec (R1–R8:
  multiplicity, no permanent trapping, ~m_Pl fragments, no re-coalescence,
  stability, formation untouched, halo structure, species bound) precisely
  defines the new physics needed; the mechanism exists in no literature.
  Formation results stand as PBH physics even if the DM framework fails.
- **Closed only for:** classical conversion paths (evaporation, coherent
  bounce, fragmentation) under near-spherical collapse in radiation
  domination. Formation margins are [EST] mappings, not exclusions.

### 4. GW condensate

- **Claim:** A zero-temperature BEC-like vacuum (Gross–Pitaevskii dynamics +
  Isaacson GW stress-energy + Einstein–Cartan torsion) tested against
  GWTC-4/O4a phenomenology.
- **Data:** Literature bounds compilation (11 entries): GW170817 speed
  |c_g²/c²−1|<10⁻¹⁵; graviton mass <1.2×10⁻²² eV/c² (O1–O3), <2×10⁻²³ (O4-era);
  scalar breathing polarization h_br/h_+<5.6×10⁻⁴ (95% CL, 180 events);
  PN phases GR-consistent; no ringdown echoes; modified GW friction
  constrained at O(1) (loosest); dynamical torsion |α_torsion|<1.2×10⁻⁷ (95%).
- **Statistic:** Literature survey — constraint vs natural-expectation per
  deviation channel. No new calculations.
- **Threshold:** "Natural condensate-scale" expectations vs bounds
  (qualitative closure, not a single statistical test).
- **Assumptions:** Bounds quoted as reported. Provenance caveats from the
  note: C3 (Barodkin) is open-data, not peer-reviewed; C7–C8 are recent
  preprints — trace to primary publications before quoting as established.
- **Result:** Every natural deviation channel closed: speed needs 10⁻¹⁵
  tuning; dispersion needs a cosmological healing length; scalar mode needs
  decoupling below 5.6×10⁻⁴; dynamical torsion squeezed to 10⁻⁷. Survivors:
  (i) reproduce GR in the IR and accept untestability (Volovik posture),
  (ii) BK superfluid DM (doesn't touch GW propagation), (iii) algebraic
  (non-propagating) EC torsion — silent. As stated, "GP+Isaacson+EC" is a
  parts list, not a model: no Lagrangian, no computed GW observables.
- **Reproduction:** None — literature survey only. Bounds live in the cited
  papers (references in the survey note; includes arXiv:1710.05893,
  arXiv:2509.08848, arXiv:2608.19392 among others). No git VCS.
- **Residual:** Modified GW friction (Ξ₀, O(1)) is the loosest bound;
  parity-violating birefringence stays live (adjacent to the Kerr/CS
  thread); kHz+ dispersion untestable until kHz-band detectors exist.
- **Closed only for:** natural-scale GW-propagation deviations
  (speed, dispersion, scalar polarization, dynamical torsion) as compiled;
  silent/GR-like versions survive.

### 5. Superradiance trio

- **Claim:** (a) Fast-growth-locus evolution toward extremal Kerr + emulator;
  (b) Bayesian population-level boson inference engine; (c) λφ⁴/4!
  self-interaction modification of spin-gap exclusions.
- **Data:** Literature 2021–2025, 22 papers mapped paper-by-paper.
- **Statistic:** Literature overlap assessment per hypothesis.
- **Threshold:** "Substantially anticipated" = the core construction exists
  in print.
- **Assumptions:** arXiv IDs from web search; **a systematic ADS/inSPIRE
  review would strengthen completeness claims** (completeness judged on
  web-search results only).
- **Result:** (a) Γ(a_*,Mμ) surface numerically mapped (Dolan: max
  Mω_I≈1.7×10⁻⁷ at a_*≈0.99, Mμ≈0.42); near-extremal non-smoothness known
  (level-crossing exceptional point at (Mμ)_c≈0.3705, (a/M)_c≈0.99947;
  zero-damping modes spectrally fragile) — but astrophysically marginal
  (Thorne limit 0.998; no BH observed there). (b) The engine exists: Ng et
  al. hierarchical Bayesian inference on BBH spins (2019/2021); Hoof et al.
  bhsr framework (2024) explicitly built for hierarchical population
  modeling, demo on M33 X-7 and IRAS 09149-6206, self-interactions included.
  (c) Baryakhtar et al. (2021) definitive: quartic interactions → level
  mixing, emission to infinity, quasi-equilibrium saturation; bosenova does
  NOT occur in most astrophysical parameter space; Hoof+2024 excludes it
  for |α|≲0.2.
- **Reproduction:** None — literature survey. Key arXiv IDs in the survey
  note (22 papers). No git VCS.
- **Residual:** (a) Public uncertainty-quantified Γ emulator (infrastructure,
  not discovery). (b) Run on GWTC-3/4; joint GW+XRB with honest systematics
  (execution, collaboration-scale; spin systematics dominate). (c) |α|≳0.2
  strong-coupling corner; λ-dependent critical cloud-mass curve.
- **Closed only for:** the three stated constructions as covered by the
  2021–2025 literature mapped; open corners listed above.

### 6. 8848 THz "vacuum resonance"

- **Claim:** 8848.85 THz is a physical "Vacuum Mass Resonance" anchor.
- **Data:** TuringBot symbolic-regression outputs across runs (Jase's paste):
  **8845.185, 8848.13, 8848.85 THz**; unit conversions (36.60 eV, 33.88 nm).
- **Statistic:** Cross-run convergence test (a real feature converges to one
  value; three values = three local optima) + known-physics lookup at the
  converted scale.
- **Threshold:** Convergence across independent fits — failed.
- **Assumptions:** Arithmetic only; EUV atomic data as known.
- **Result:** 36.6 eV sits in a featureless EUV continuum for abundant
  elements (between He I 24.58 eV and He II 54.42 eV edges) — no resonance,
  edge, or fundamental scale.
  [Internal diagnostic against numerology — not scientific evidence:]
  the number's only "structure" is digitological: it embeds "848", and
  matches Mount Everest's 8848.86 m height to 4 significant figures (~10⁻⁴
  coincidence or borrowed digits — either way, no mechanism connects a
  mountain's height to a vacuum frequency). 8848.85/848≈10.435 is
  meaningless. [End of fenced diagnostic.]
  The notebooks' "20-order mismatch" excision claim for the 848 sequence
  **cannot be audited from reachable files** (no derivation found
  workspace-wide); the scale ladder is consistent with excision (23–27
  orders to GUT/Planck) but the exact "20" is unverifiable.
- **Reproduction:** Arithmetic in the note; no script. The TuringBot runs
  themselves are not in the workspace. No external identifiers exist.
  No git VCS.
- **Residual:** None as an anchor. Revival needs a derivation that *produces*
  the number from stated assumptions.
- **Closed only for:** the 8848.85 THz value as a physical anchor; the
  quarantine diagnostic (cross-run non-convergence) stands.

### 7. Neptune/Uranus superfluid-drag β

- **Claim:** β=(Q_out−Q_in)/(mv²) is a universal vacuum-drag rate explaining
  the Neptune/Uranus internal-heat asymmetry.
- **Data:** Published values — masses; orbital/equatorial velocities;
  emitted/absorbed ratios (Uranus 1.06±0.08 PC91 → 1.15±0.06 2025 revision;
  Neptune 2.61±0.28 PC91); internal powers (Uranus 0.34±0.38×10¹⁵ W PC91 →
  0.63×10¹⁵ W 2025; Neptune 3.30±0.35×10¹⁵ W); Jupiter as check (Li+2018).
- **Statistic:** β_N/β_U ratio; universal-β prediction
  (Q_exc,N/Q_exc,U)=(m_N v_N²)/(m_U v_U²)=**0.75** vs observed **9.7**
  (PC91) / **5.2** (2025 revision).
- **Threshold:** Universality (planet-independent β) as the explanation
  criterion.
- **Assumptions:** Two natural readings of v (orbital, equatorial) — verdict
  identical under both; Q_exc from published E/A ratios.
- **Result:** **Decisive: universal β predicts the wrong SIGN of the
  asymmetry** — with a universal β, Neptune should radiate *less* excess
  heat than Uranus (predicted ratio 0.75), while the observed ratio is
  5–10 in Neptune's favor — off by 7–13× and in the wrong direction.
  β_N/β_U≈13 (PC91) or ≈7 (2025 revision): per-planet β values are fits by
  construction with no predictive content — not a viable model. Ephemeris:
  implied drag ~10⁻¹⁵–10⁻¹⁴ m/s², 10⁴–10⁵× below the INPOP08 bound — the
  test is passed **vacuously** (effect far below detectability), not
  confirmatorily. Physical objections independent of numbers: category error
  (orbital drag vs deep-interior heat), no mechanism for β's variation,
  v undefined.
- **Reproduction:** No script file named; "recomputed in-session from cited
  inputs" (Pearl & Conrath 1991; Li+2018; 2025 revision — published values,
  no DOIs recorded in the note). The entire result follows from one redoable
  inequality: (m_N v_N²)/(m_U v_U²)=0.75<1 while Q_exc,N/Q_exc,U>5.
  No git VCS.
- **Residual:** None. The 2025 Uranus revision softens the asymmetry but the
  direction stays wrong.
- **Closed only for:** a universal (planet-independent) vacuum-drag β
  explaining the ice-giant heat asymmetry.

### 8. F3 compact objects

- **Claim:** Galactic rotation anomalies come from neutron stars and micro
  black holes (no accretion disks/backlights, hence "undetectable").
- **Data:** Microlensing surveys — OGLE 20-yr LMC (78.7M stars;
  f≤0.01 at 1.8×10⁻⁴–6.3 M☉, 2024 Nature), EROS-2+MACHO, Subaru HSC
  (M31; 10⁻¹¹–10⁻⁶ M☉ ≤2×10⁻³), Kepler, FRB lensing; NS population ≈10⁸
  (birth-rate estimate); MW halo ≈10¹² M☉.
- **Statistic:** Halo fraction f_CO limits per mass bin (95% CL); mass-budget
  arithmetic.
- **Threshold:** f_CO=1 required for all-DM; per-survey 95% CL exclusions.
- **Assumptions:** Roughly monochromatic mass functions (extended
  distributions shift but don't remove bounds); textbook NS population
  estimate.
- **Result:** Three **logically distinct** failure modes (not statistically
  independent exclusions): (a) **budget** — NSs give 1.4×10⁸ M☉ vs 10¹²
  needed (10⁴ short), wrong spatial distribution (disk-tracing, not r⁻²
  halo); stellar BHs 10³–10⁴ short; (b) **lensing at its own masses** —
  1.4 M☉ NSs limited to ≤1% by OGLE 2024, ~10 M☉ BHs to ≤1.2%; (c)
  **premise** — "dark" objects are detectable via microlensing (the lens
  needs no light of its own); the surveys *are* the detection channel.
  Surviving f=1 window: **3.5×10⁻¹⁷–4×10⁻¹² M☉** (asteroid-mass PBHs;
  Carr+2021, Smyth+ arXiv:1906.05950) — but that is primordial-BH cosmology,
  not F3, requiring 10²⁶ objects from a tuned primordial spike (the same
  fine-tuning wall as QSE).
- **Reproduction:** Literature compilation + arithmetic in the note; no
  script. Survey references in the note (incl. arXiv:1906.05950,
  arXiv:2207.08668, arXiv:2403.02386/02398/19015, arXiv:2501.18239,
  arXiv:2602.05840, arXiv:2605.19653). No git VCS.
- **Residual:** The asteroid-mass sliver belongs to PBH cosmology and is
  being squeezed from both ends (HSC 2026 candidates; Rubin LSST ahead).
- **Closed only for:** galactic rotation from stellar-remnant compact objects
  (NSs/micro-BHs) as all-DM; the asteroid-mass PBH sliver is a different
  (primordial) hypothesis.

### 9. Kerr/CS quantum tunneling mechanism

- **Claim:** 2π phase slips of the Kerr pseudoscalar arise from quantum
  tunneling of the homogeneous mode (instanton between winding vacua).
- **Data:** Analytic derivation from S=∫d⁴x√(−g)[½(∂φ_c)²−μ⁴(1−cos(φ_c/f))];
  Kerr volume integrals numerically (M_φ=∫√(−g)(−g^tt)d³x);
  Sgr A* M=4.3×10⁶ M☉, a_*=0.9, coherence patch r∈[r₊,10M].
- **Statistic:** Instanton action B=8fμ̄²√M_φ; rate Γ=ω₀√(B/2π)e^(−B);
  compared against the asserted 46.9 s slip cadence.
- **Threshold:** Tunneling viable only if Γ⁻¹~46.9 s achievable within the
  EFT (μ≲f, f≪M_Pl).
- **Assumptions:** Kerr background fixed (backreaction checked — gives only
  f≪M_Pl, no useful bound; an earlier sub-eV claim from a dimensional error
  was withdrawn); homogeneous mode coherent over the patch (inherited from
  the R(t) program's morphology); minimal cosine potential.
- **Result:** M_φ=7452 M³; B=4.94×10²²²·fμ² (f,μ in eV). Best EFT case
  (M_Pl,10⁻³³ eV): B=1.2×10¹⁸⁴. Optimized over μ at fixed f: best
  Γ_max⁻¹=2.9×10²⁴⁶ s at f=10¹⁹ eV — **239 orders of magnitude too slow**;
  enforcing μ≤f: best ~1 slip per 4×10⁵² yr. Forcing 46.9 s needs
  μ/f~6×10⁴³ — EFT nonsense. Localized (LAMH-like) channel needs
  f~10⁻⁷² eV. **Excluded by 50–250 orders of magnitude depending on
  channel.** Structural byproducts: the Kerr Pontryagin charge vanishes for
  the homogeneous mode (dCS gravity does not drive it); winding sectors are
  non-degenerate (E_k∝k² — "tunneling between winding vacua" was the wrong
  picture); ergospheric winding locally favored (κ̃_ergo=−110 at a_*=0.9),
  supporting the classical stick-slip picture.
- **Reproduction:** `~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/tunneling/geo_integrals.py`,
  `rate_calibration.py`, `drive_torque.py`; full derivation in
  `tunneling_rate_derivation_note.md`. No external dataset. No git VCS,
  no checksums recorded.
- **Residual:** Mechanism dead. The phenomenology survives
  mechanism-independent: 55.56° quantization (at γ≈0.1543), achromaticity,
  integer-spaced amplitudes, one-directional Poisson counting. Slips must be
  classical/driven — toy-level magnetospheric E·B torque window
  ~10 eV≲f≲10¹⁴ eV (lab bounds below, drive plausibility above).
- **Closed only for:** homogeneous-mode (and LAMH-like localized) quantum
  tunneling within the stated EFT (μ≲f, f≪M_Pl) on a fixed Kerr background.

### 10. Kerr/CS first real-data bound (ALMA)

- **Claim tested:** 55.56° tanh EVPA transients with τ∈[10,120] s occur in
  Sgr A* 230 GHz polarimetry.
- **Data:** ALMA project 2016.1.01404.V, 2017-04-07, 2 of 8 execution blocks
  (X4947 11:08–11:55 UT, X448f 08:36–09:22 UT); 4.0 s Stokes IQUV; 4 SPWs
  213.1/215.1/227.1/229.1 GHz; 64 min usable contiguous coverage in 9
  segments (public since 2018).
- **Statistic:** Per-segment least-squares tanh-template fit over a
  (τ,t₀) grid on inverse-variance band-averaged EVPA; null = identical
  max-over-grid search on 200 circular shifts + time reversal per segment
  (n=1809 surrogates); achromaticity veto via common-amplitude χ² across
  SPWs (a λ²-scaling step = Faraday, not a θ slip).
- **Threshold:** Detection = above the surrogate null (95th/99th
  percentiles at |S/N|=40.7/43.1). Null-calibrated rather than
  pre-registered — stated as such.
- **Assumptions:** tanh morphology; surrogate null captures slow drifts
  (linear baseline in the fit); stationary noise within segments.
- **Result:** Strongest candidate |S/N|=25.3 (~3° amplitude, at the τ=120 s
  grid edge) — **consistent with the null, no detection**. Top candidates fail
  achromaticity badly (common-A χ²=74/3 dof). Sensitivity σ_A≈0.1–0.15° at
  τ=46.9 s; a 55.6° slip would appear at S/N~380. **No qualifying 55.6° tanh
  transient detected in 64 min; within the tested morphology (tanh) and
  τ=10–120 s, amplitudes above ~6° are excluded for the analyzed coverage.
  This is NOT a global rate limit for Sgr A*** — that would require folding
  the observation duration with an explicit event-process model. Two large
  single-sample jumps (75.5°, 47.3°) individually vetted and vetoed
  (single-SPW, noise-dominated / edge artifact).
  **Update 2026-10-06 (X4227):** third EB searched with the identical
  pipeline (07:09–08:20 UT, 39.5 min usable, 5 segments): strongest
  candidate |S/N|=35.7 (~4.1°, τ=120 s) — below its own null 95th
  percentile (42.3); a 55.6° slip would appear at S/N~293. One 39.6°
  single-sample jump vetoed (SPW2-only, non-achromatic). **Combined 3 EBs,
  ~104 min: still null; |A|≳6–8° excluded within the tested morphology/τ
  range; 55.6° tanh slips excluded at >>99% per-epoch in all three EBs.**
- **Reproduction:** `~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data/evpa_transient_search.py`;
  inputs `SGRA2017_X4947_IQUV.npz`, `SGRA2017_X448f_IQUV.npz`;
  `transient_search_firstlook.md` + PNGs alongside. External: ALMA Science
  Archive project 2016.1.01404.V (public since 2018). No git VCS,
  no checksums recorded.
- **Residual:** Per-epoch only (3 of 8 EBs, one day); τ outside [10,120] s and
  rarer/different-cadence slips not addressed; 5 more EBs + 2017-04-06/11
  pending. "First" scoped: no published tanh-transient search in
  high-cadence ALMA Sgr A* polarimetry was found in the venues searched for
  the R(t) prior-art review (`rt_prior_art_note.md`, whose novelty verdict
  carries diligence-search caveats — absence of evidence, not proof).
- **Closed only for:** tanh EVPA events with τ=10–120 s in the analyzed ALMA
  coverage (3 EBs, ~104 min, 2017-04-07; first look was 2 EBs / 64 min).

### 11. Pulsar–white-hole (thinnest salvage)

- **Claim:** Pulsars are white holes emitting matter/information/gravity that
  seeds cosmic structure, via quantized bi-directional intake/exhaust links.
- **Data:** ATNF psrcat v2.8.1 (4,393 pulsars; 2,040 with measured F0, F1);
  spin-down luminosity Ė=4π²Iν|ν̇| with I=10⁴⁵ g cm².
- **Statistic:** Population energy budget vs structure-formation benchmarks;
  distinguishability checklist (L≤Ė compliance, RVM beaming sweeps, P–Ṗ
  tracks, glitch models).
- **Threshold:** Needs (a) a spare energy budget plus a defined coupling
  mechanism, and (b) at least one observable differing from the
  rotation-powered neutron-star model.
- **Assumptions:** I=10⁴⁵ g cm²; benchmarks: galaxy binding 10⁵⁸–10⁵⁹ erg,
  supernova feedback ~10⁵⁹ erg per galaxy over cosmic time. Budget is
  **lifetime-integrated over the Galactic population** (~10⁵⁴–10⁵⁶ erg,
  birth-rate dependent); catalog completeness is a minor factor (top 10
  pulsars = 86%, top 100 = 98.5% of the budget).
- **Result:** Galactic total Ė=8.4×10³⁸ erg/s; lifetime-integrated
  ~10⁵⁴–10⁵⁶ erg — **10²–10⁵ short of seeding even one galaxy**, and the
  entire budget is already observationally accounted for (PWN, radio/X-ray/
  gamma all ≤Ė, consistent with rotation power) — no spare reservoir, and no
  coupling mechanism is defined. No differing observable: L≤Ė holds
  universally, RVM sweeps, P–Ṗ tracks, and glitch models all favor the
  standard picture with no residual anomaly. White holes are classically
  unstable (Eardley 1974); no viable theory supports stable stellar-mass
  steady emitters.
- **Reproduction:** No script path recorded in the note; recomputation
  described from ATNF psrcat v2.8.1 (public catalog) with the stated formula.
  No git VCS.
- **Residual:** None as stated. Revival needs a specific differing
  prediction (start with L>Ė or non-RVM beaming) plus a stability
  mechanism — neither exists.
- **Closed only for:** the stated white-hole pulsar hypothesis as a distinct
  mechanism from rotation-powered neutron stars.

### 12. Dipole repeller / persistent void flow (thinnest salvage)

- **Claim:** (a) The Dipole Repeller preserves an ancient-impulse signature
  (compact-object transition / long-lived vacuum-flow impulse); (b) a
  persistent extra (non-gravitational) velocity component exists in
  void/repeller basins.
- **Data:** Literature — CF2/CF3/CF4 peculiar-velocity reconstructions
  (Hoffman+2017, Courtois+2017, Dupuy & Courtois 2023); bulk-flow estimator
  debate (Watkins+2023: <0.03% ΛCDM probability at 150 h⁻¹Mpc;
  Whitford+2023: uncertainties underestimated; Tully+2023/CF4 team: no
  compelling tension without 6dFGS); void RSD (Lavaux 2016: no GR deviation;
  Nadathur+2019); velocity–velocity comparisons (~10% agreement).
- **Statistic:** Literature synthesis; order-of-magnitude bound on extra
  coherent flow from velocity–density agreement precision.
- **Threshold:** "Explained by standard" = no residual anomaly for the
  proposed mechanism to attach to.
- **Assumptions:** As reported in cited papers; the bulk-flow tension is
  estimator- and subsample-dependent (6dFGS, cosmic variance ~180 km/s).
- **Result:** (a) The Repeller is a linear-theory void, stable across
  CF2→CF3→CF4; an ancient impulse predicts the wrong morphology
  (expanding shell, not a stationary basin) — **no open residual**.
  (b) Any extra coherent velocity component on 50–200 h⁻¹Mpc scales is
  capped at **≲ tens of km/s** — an **order-of-magnitude synthesis** (per the
  source note: ~10% of the measured ~300–400 km/s flows, the precision of
  velocity–density agreement), **not a formal bound**. Too small to do the
  work the hypothesis wants, and the wrong shape for the bulk-flow debate
  (which, if real, points to more gravitational growth, not a
  non-gravitational flow).
- **Reproduction:** None — literature review, no new calculations. Key
  references: arXiv:1702.02483, arXiv:2305.02339, arXiv:2306.11269,
  arXiv:2109.14808. No git VCS.
- **Residual:** The honest open items are conventional: CF4 bulk-flow
  estimator systematics and the watershed-basin-size comparison — standard
  cosmology questions requiring no new physics.
- **Closed only for:** (a) ancient-impulse signatures in the Dipole Repeller;
  (b) extra coherent non-gravitational flow ≳ tens of km/s on 50–200
  h⁻¹Mpc scales.

---

## The meta-result (unchanged from v1)

This board has an unusually high *kill quality*: every death came with
numbers, a named mechanism, and stated assumptions. Three separate outsiders'
numbers were caught understating real noise the same way (NANOGrav's binned
formal errors, NICER's per-dwell uncertainties, the split-half statistic's
miscalibrated errors) — and each catch produced a repair rule now in active
use (never trust binned formal errors; fit the white level or propagate from
chains). A registry of clean kills, kept honestly, is itself a piece of
work: it tells the next person exactly where not to dig, and exactly where
the shovel broke.

---

## v1 → v2: phrasings weakened and why

1. **Great Wall "first quantitative test of its kind"** → dropped. Fujii
   (2022) already tested ~half the region with SDSS DR7 quasars; this test
   is the first over the *full* cap at 3× the quasar density. "Ruled out"
   is now scoped to tracer, geometry, and redshift range in every use.
2. **Refractive index "publishable constraint"** → "model-conditional bound
   closing this ansatz under stated assumptions A1–A4." The note supports
   closure of the ansatz, not a model-independent publication claim.
3. **QSE "viable with margin vs LIGO"** → the bound is now named
   (LIGO/Virgo/KAGRA O3 stochastic, Ω_GW≲5×10⁻⁹), margins stated per target,
   and every margin flagged **[EST]** (back-of-envelope mappings, not
   published numbers); marginal at β~10⁻⁵. "Triple no-go" now carries its
   domain: classical GR, radiation-dominated, near-spherical collapse.
4. **GW condensate** → provenance caveats added: the scalar-polarization
   bound is open-data (not peer-reviewed); two torsion bounds are recent
   preprints to be traced before quoting as established.
5. **8848 "20-order mismatch" excision** → flagged unauditable: no
   derivation exists in reachable files. The scale ladder is consistent
   with excision but the exact "20" is unverifiable.
6. **Kerr ALMA "first-of-its-kind bound"** → scoped to the exact observable
   (tanh, |A|>~6°, τ∈[10,120] s, 64 min, 2 EBs), per-epoch only, with the
   prior-art search's diligence caveats stated.
7. **Neptune/Uranus ephemeris** → made explicit that the test is passed
   *vacuously* (effect 10⁴–10⁵× below detectability), not confirmatorily.
8. **Missing reproduction paths** (no code or script to point at): GW
   condensate, superradiance, dipole repeller (literature surveys — nothing
   to reproduce); pulsar–white-hole, Neptune/Uranus β, 8848 (arithmetic
   described in-note, no script file); F3 (arithmetic in-note);
   QSE formation [EST] margins (no end-to-end script — the key gap);
   QSE bounce (literature survey). Stated as such in each card rather
   than inventing paths.

---

## v2 → v3: changes and why

1. **Registry: two new columns.** "Evidence type" (New analysis / Analytic
   closure / Literature closure / Exploratory estimate / Null search) and
   "Evidence maturity" (High/Medium/Low, defined as evidence quality and
   reproducibility — not a likelihood score). Entries with different
   evidentiary status no longer sit in one undifferentiated column.
2. **QSE margins split by mechanism** in registry and card: curvaton
   ≈160–1000× [EST], USR ≈5–100× [EST] at briefing targets; β~10⁻⁵
   marginal within ~3× for both. Verified verbatim against
   `nongaussian_formation_survey.md` (no discrepancy found).
3. **Hercules card:** conversion δ_m ≈ δ_q/b_q now explicit (0.044/2.4);
   δ_m<0.018 labeled conditional on b_q=2.4 (note adopts the value; b_q
   uncertainty not propagated). "Look-elsewhere handled by construction"
   replaced: control caps handle the spatial comparison only; cap radius,
   z-interval, and GRB selection are inherited upstream choices, and the
   no-preregistration limitation is now prominent.
4. **ALMA card + registry:** exclusion language replaced with the
   statistically cleaner form — no qualifying 55.6° tanh transient in
   64 min; |A|>~6° excluded within tested morphology/τ range for the
   analyzed coverage. Explicit: NOT a global rate limit for Sgr A*.
5. **F3:** "three independent deaths" / "Dead ×3" → "three logically
   distinct failure modes" (budget; lensing at own masses; false
   undetectability premise) in registry and card.
6. **Closure boundary:** every card now ends with a "Closed only for:"
   line scoping the exact model, data range, and assumptions.
7. **Source identifiers:** arXiv IDs added to Reproduction fields where the
   notes record them (QSE, GW condensate, superradiance, F3, repeller);
   dataset releases named (DESI DR1, ALMA 2016.1.01404.V, ATNF psrcat
   v2.8.1). Where nothing exists (no git VCS anywhere, no checksums, no
   rerun logs), stated plainly — nothing invented.
8. **Technical flags applied:** GW condensate non-peer-reviewed constraints
   now visible in the registry row; superradiance ADS/inSPIRE caveat in the
   registry row; 8848 digitology fenced as an internal anti-numerology
   diagnostic; Neptune/Uranus reordered to lead with the wrong-sign verdict;
   pulsar–white-hole integration interval (lifetime-integrated, birth-rate
   dependent) and completeness (top-100 = 98.5%) stated; repeller ≲ tens of
   km/s labeled order-of-magnitude synthesis, not a formal bound.
9. **QSE end-to-end formation calculation:** not attempted (separate
   research); [EST] flags and the key-gap note retained.

## Post-v3 updates (2026-10-06)

- **ALMA:** X4227 searched with the identical pipeline — null. Combined
  3 of 8 EBs, ~104 min usable: no qualifying tanh transient (|A|≳6–8°,
  τ=10–120 s); 55.6° slips excluded at >>99% per-epoch in all three.
  Registry row and card updated; per-EB nulls kept separate.
- **QSE formation:** full end-to-end script completed
  (`goals/qse-remnant-dark-matter-exploration/hidden_files/formation_endtoend_note.md`).
  Nothing failed under nominal assumptions: curvaton 182× (threshold caveat
  Δ_cr≳0.44) / 1317× (robust); USR 18×/48× nominal (15–108× across ζ_c).
  Notable: the 1.5×10⁻¹² target's GW peak sits at ~7 μHz with no direct
  bound — BBN integral bound (6787× below) is the operative constraint, so
  it is the safest target, not the riskiest. [EST] flags retired for
  formation; evidence type now "New analysis (end-to-end numerical) +
  analytic closure". Parked status unchanged (conversion impasse stands).
