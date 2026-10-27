# Planet Nine gamma verdict: 5-Earth-mass black hole at ~500 AU

Date: 2026-10-11. Reproducible calculation:
`compute_gamma_flux.py` (private execution scratch, activation 2454c9b7).

## Test case

| Quantity | Value |
|---|---|
| Black-hole mass | 5 M⊕ (2.99×10²⁵ kg) |
| Distance from Earth | ~500 AU |
| DM model | Freeze-in, ⟨σv⟩ = 1.3×10⁻⁵⁶ cm³/s, m_χ = 100 GeV |
| Spike model | Scholtz & Unwin 2019, arXiv:1909.11090; profile ρ(r) = (ρ_eq/2)(r_eq/r)^{9/4} from Eroshenko, arXiv:1607.00612. Normalization reused verbatim from `files/stage2_gamma_halo_calibration_note.md` — not re-derived here. |
| Equality radius | r_eq = 220 AU at 5 M⊕ |
| Solar tidal truncation | r_t,⊙ ≈ 10 AU at 500 AU; halo mass ≈ 1.0 M⊕ (~21% of M_BH, consistent with the calibration note's O(15–20%)) |
| Annihilation plateau | None: ceiling ⟨σv⟩ < 1.4×10⁻⁵⁴ cm³/s is ~108× above the freeze-in value, so the 9/4 profile holds to the horizon |

## Predicted gamma flux at Earth (freeze-in)

- Annihilation rate: Γ = 1.0×10²⁰ s⁻¹ (mass-independent per the calibrated treatment)
- Photon flux: **Φ_γ = 1.42×10⁻¹² photons/cm²/s** (κ₁ = 10)
- Energy flux: **Φ_E = 2.28×10⁻¹⁷ W/m²** = 2.28×10⁻¹⁴ erg/cm²/s (κ₂ = 1)

## Fermi-LAT point-source sensitivity used

1. **8-yr catalog faintest sources** (100 MeV–100 GeV), as cited in the calibration note: 8.8×10⁻¹² photons/cm²/s and 5.96×10⁻¹³ erg/cm²/s (= 5.96×10⁻¹⁶ W/m²).
2. **4FGL-DR4** (Ballet et al. 2023, arXiv:2307.12546; 14-yr catalog), verified at activation: detection threshold outside the Galactic plane "remains a little above 1×10⁻¹² erg/cm²/s" in the 100 MeV–100 GeV band (= 1×10⁻¹⁵ W/m²).

## Sky-region assumption

No sky coordinates are assumed or invented. The comparison uses the off-plane / high-latitude sensitivity, consistent with a Planet Nine search field (a ~500 AU body on an inclined orbit spends most of its time well off the Galactic plane). Sensitivity degrades toward the plane where diffuse background is brighter; the quoted thresholds are therefore the applicable optimistic reference, and the conclusion below holds a fortiori in-plane.

## Comparison (margin)

| Sensitivity reference | Sensitivity | Predicted Φ_E | Margin |
|---|---|---|---|
| 8-yr faintest photon flux | 8.8×10⁻¹² ph/cm²/s | 1.42×10⁻¹² ph/cm²/s | prediction **6.2× below** |
| 8-yr faintest energy flux | 5.96×10⁻¹⁶ W/m² | 2.28×10⁻¹⁷ W/m² | prediction **26× below** |
| 4FGL-DR4 off-plane threshold | ~1×10⁻¹⁵ W/m² | 2.28×10⁻¹⁷ W/m² | prediction **44× below** |

For reference, the thermal-WIMP variant (⟨σv⟩ = 3×10⁻²⁶ cm³/s) predicts Φ_E ≈ 5×10¹³ W/m² — ~29 orders of magnitude over the 8-yr limit, independently excluded by diffuse gamma-ray emission (Boucenna et al. 2017; Adamek et al. 2019). That kills the thermal-WIMP PBH variant outright; it says nothing about the freeze-in variant, whose prediction sits below reach.

Caveat (from the calibration note): no dedicated *moving*-source Fermi search exists — the object drifts several degrees over 8 yr, defeating catalog matching. Catalog thresholds are therefore conservative for a moving PBH; they are not silently tightened here.

## Verdict

**Gamma non-discriminating for this case.**

The freeze-in 5 M⊕ PBH at 500 AU is a factor of ~6–44 below Fermi-LAT point-source reach, depending on the reference. A Fermi non-detection is fully expected under this hypothesis and constrains ⟨σv⟩ only; it does not touch the PBH+freeze-in model. The gamma channel therefore carries no discriminating power for this case.

**Classifier consequence: the gamma channel weight goes to zero for the 5 M⊕ / 500 AU freeze-in case.** Gamma remains a veto channel only against the thermal-WIMP PBH variant, which is already excluded by diffuse emission. A bare PBH with no annihilating halo is invisible to every channel — the classifier must be allowed to report exactly that.

## What this does and does not say

- Says: under the stated spike normalization and freeze-in DM assumptions, Fermi-LAT cannot see this object; gamma cannot discriminate it from a planet or from nothing.
- Does not say: that the object exists, that it is ruled out, or that any other DM model is favored. The verdict is bounded to the flux-vs-sensitivity comparison above.
- Out of scope: Stage 1 two-body refinement, real-data target hunting, and any claim of detection or validation.
