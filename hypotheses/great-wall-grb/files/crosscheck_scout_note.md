# Cross-check scout: independent tracers for the HCBGW candidate
Date: 2026-09-25. Author: Atlas (scout agent). Status: **literature + data-availability scout only — no new data analysis was run.**

## Where the GRB-only evidence stands
From `~/workspace/grb/hcbqw_shuffle_note.md` (2026-09-24): GRBweb snapshot 9,187 rows, 734 with measured redshift. Candidate: 50° spherical cap centered RA 215.94°, Dec +49.51°, z = 1.6–2.1, containing 34 GRBs. Fixed-cap shuffle p = 0.0030; coarse look-elsewhere correction p ≈ 0.0175; well-localized subset p ≈ 0.0050; analytic exposure-stratified shuffle p ≈ 0.0088. Exposure correction was an analytic ecliptic-latitude proxy, not a measured BAT map. Verdict stands: **suggestive candidate, not a detection.** GRB-only evidence is fully squeezed — the next informative step is independent tracers (galaxies/quasars/lensing), not more GRB reshuffling.

## Prior art — read before doing anything new
1. **Fujii (2022), "Large-scale homogeneity in the distribution of quasars in the Hercules-Corona Borealis Great Wall region," Serbian Astronomical Journal 204.** Direct quasar cross-check of the HCBGW region: volume-limited SDSS DR7 quasars, 1.6 < z ≤ 2.1 (the same slice), covering ~half the suspected HCBGW region. Fractal analysis: homogeneity scale r_h = 136 ± 38 h⁻¹ Mpc; friends-of-friends: richness/size frequencies of large (>~150 h⁻¹ Mpc) quasar groups consistent with a homogeneous distribution. Conclusion: constrains the spatial extent of the HCBGW but does not contradict it (half coverage). **Do not repeat a DR7 quasar test — it has been done.** The new test must use a larger/different sample and cover the rest of the region. (https://www.osti.gov/pages/biblio/1983072; earlier related method paper arXiv:1306.1700)
2. **Horváth et al. (2020), MNRAS 498:** GRB-only clustering re-test of the HCBGW claim.
3. **Horváth et al. (2025):** new statistical method on 542 spectroscopic-redshift GRBs; reported a larger northern grouping while noting possible remaining observational biases. GRB-only.
4. **Horváth et al. (2026), Universe 12, 264:** spheroidal-resampling analysis; the northern GRB overdensity remains the strongest feature under varying shape. GRB-only — re-tests the same tracer, not independent confirmation.
5. **Christian (2020), MNRAS 495, staa1448:** critical re-examination of the HCBGW evidence — re-read before citing; its exact conclusion was not re-verified in this scout.

Net: nobody has yet published a full-region, exact-redshift, independent-tracer (DR16/DESI quasar or lensing) confirmation or refutation. That gap is real.

## Candidate independent datasets, ranked by feasibility

### Rank 1 — DESI DR1 spectroscopic quasars × Planck PR4 CMB lensing
- **What:** DESI DR1 public since 2025-03-19: 1,223,391 spectroscopic quasars, 0.8 ≤ z ≤ 3.5; the standard clustering bin g1 (0.8 ≤ z < 2.1) holds 856,831 quasars. Sub-select 1.6 < z < 2.1 to match the GRB slice exactly. Cap center (RA 216°, Dec +49.5°) lies well inside the DR1 NGC footprint.
- **Statistic:** (a) fixed-cap weighted quasar count overdensity δ_q = (N − N̄)/N̄ in the 50° cap and 1.6<z<2.1, conditioned on the DR1 mask via the public randoms, compared against matched control caps; (b) quasar × Planck PR4 κ cross-correlation C_ℓ^{κg} (or w(θ)) in the slice, then compare the inferred matter δ with the GRB-inferred signal. (c) optional: 3D count-in-cell / GRB–quasar cross-correlation.
- **Template exists:** a published DESI DR1 QSO × Planck PR4 analysis (f_NL paper, arXiv:2512.17865v2) demonstrates the exact catalog + lensing-map pipeline on public data.
- **Access/volume/compute:** public DR1 release; QSO redshift catalog a few GB; Planck PR4 κ maps a few ×100 MB. Laptop-scale with healpy/NaMaster: hours, not days.
- **Caveats:** must use the DR1 LSS/random products (not raw spectra) to handle the selection function; quasar bias b~2–3 at z~2 means δ_q = b·δ_m — a null in quasars does not rule out a low-bias structure, and vice versa.

### Rank 2 — eBOSS DR16 quasars (ready-made LSS catalogs)
- **What:** 343,708 quasars, 0.8 < z < 2.2, over 4,808 deg² (NGC), with corrected LSS catalogs including random catalogs and systematic weights, public via the SDSS-IV archive. Exact redshift overlap with the GRB slice. Most of the NGC footprint falls inside the 50° cap (overlap of order 3,500–4,800 deg² — exact number needs the LSS mask, not a box approximation).
- **Statistic:** same fixed-cap count-overdensity test as Rank 1, conditioned on the eBOSS footprint via supplied randoms. Rough in-slice density ~27 deg⁻² → of order 10⁵ quasars in the overlap: plenty of statistical power for a cap-scale test.
- **Access/volume/compute:** hundreds of MB; trivial laptop compute (minutes for the count test).
- **Why Rank 2 not 1:** smaller and shallower than DESI DR1, but the LSS products are the most turnkey. If DESI DR1 randoms turn out to be awkward, run this first.

### Rank 3 — Quaia (Gaia–unWISE) all-sky quasars × Planck PR4 / ACT DR6 κ
- **What:** 1,295,502 quasars, G < 20.5, all-sky, with k-nearest-neighbor redshifts trained on SDSS (6% catastrophic errors |Δz|/(1+z) > 0.2 for G < 20.0) and published selection-function models. Public on Zenodo (10.5281/zenodo.10403370). arXiv:2306.17749.
- **Statistic:** fixed-cap overdensity in a photo-z-selected 1.6–2.1 slice (selection-function-weighted), plus κ cross-correlation following the published ACT DR6 × Quaia high-z 2×2pt template.
- **Access/volume/compute:** ~1–2 GB download; laptop-scale.
- **Why Rank 3:** all-sky = 100% cap coverage with no footprint bookkeeping, but photo-z scatter dilutes the slice and 6% catastrophic errors leak foreground/background. Supporting evidence, not the primary confirmation.

### Rank 4 — Planck PR4 κ stack at the 34 z-slice GRB positions
- **What:** Planck PR4 NPIPE lensing convergence maps are public (nearly all-sky, ~20% higher S/N than PR3; ℓ = 100–2048). Stack mean κ within a few degrees of each of the 34 cap/slice GRBs vs. control stacks (random positions, redshift-matched GRBs outside the cap).
- **Statistic:** Δκ = ⟨κ⟩_GRB − ⟨κ⟩_control; a real Gpc-scale overdensity should sit on a positive projected-mass fluctuation.
- **Access/volume/compute:** cheapest option — one κ map (~100s of MB), minutes of compute.
- **Why Rank 4:** the positions are the same GRBs, so this is not an independent tracer — it asks "is there mass where the GRBs are" rather than "do independent objects cluster there." Also the broad lensing kernel cannot isolate z = 1.6–2.1. Useful sanity check, weak on its own.

### Rank 5 — HSC-SSP PDR3 (HECTOMAP field)
- **What:** Deep photo-z galaxy sample to z ~ 2, but the only public field plausibly inside the cap (HECTOMAP) is ~55 deg² — a pencil beam against a 7,368 deg² cap.
- **Use:** spot-check the radial (redshift) profile through one line of sight, not a test of the 50° structure. Low priority for this question.

### Rank 6 — future: Euclid DR1, DESI DR2
- **Euclid:** DR1 scheduled late 2026 (Oct/Nov) — not public as of 2026-09-25. Q1 covers only 63 deg² (EDF-N, 20 deg², is inside the cap but tiny). Revisit after DR1: deep photo-z + shear over a large area is the strongest future route.
- **DESI DR2:** cosmology results public, but the DR2 spectra/redshifts are not yet released. Revisit when the catalog drops.

## Numbers used above (scout-grade, recompute from masks before any real test)
- Cap area (50° radius): 7,368 deg².
- eBOSS DR16 QSO: 343,708 / 4,808 deg² = 71.5 deg⁻²; ~38% in 1.6<z<2.1 → ~27 deg⁻² → order 10⁵ quasars in the cap overlap.
- DESI DR1 g1: 856,831 / ~9,700 deg² ≈ 88 deg⁻²; ~35% in 1.6–2.1 → ~31 deg⁻² → ~2.3×10⁵ quasars across the cap (fuller coverage than eBOSS).
- Quaia: 1.3M all-sky; photo-z scatter means the effective in-slice number needs the published selection function.

## Recommended first actual run
**DESI DR1 QSO fixed-cap count test + Planck PR4 κ cross-correlation** (Rank 1): executable now, exact redshift reach, all-sky lensing, published template pipeline, laptop-scale compute. Fall back to **eBOSS DR16** (Rank 2) if DR1 LSS products are harder to wrangle — its randoms/weights are the most turnkey. Either way, the test must cover the half of the region Fujii (2022) did not, and must condition on the real survey mask via randoms (the GRB analysis never had a measured exposure map; the quasar catalogs do).

## Open questions for the real run
1. Exact cap∩footprint overlap from the DR1/eBOSS LSS masks (not the box estimate above).
2. Whether the DR1 quasar LSS/random products cleanly support a 1.6<z<2.1 sub-selection.
3. Quasar bias at z~2 for converting any δ_q limit into a matter-density statement.
4. Re-read Christian (2020) for the strongest published skeptical counter-arguments before writing up.
