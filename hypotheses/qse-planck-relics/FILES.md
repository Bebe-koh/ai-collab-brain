# qse-planck-relics — files index

**Question:** can quasi-stable-excess (QSE) Planck-mass relics be the dark
matter — i.e. does formation clear observational bounds, and is there a
conversion mechanism that turns progenitors into relics at the required
multiplicity?
**Status (2026-10-06):** formation SOLVED under stated assumptions;
conversion at a fundamental impasse. Thread PARKED unless new physics.

## Layout

- `files/formation_endtoend_calc.py` — **the end-to-end formation script**
  (all briefing targets × curvaton/USR channels).
- `files/formation_endtoend_note.md` — full technical note.
- `files/formation_endtoend_results.json` — key numbers, converted from the
  original `.npz` (identical values).
- `files/endtoend_calc.py` — earlier end-to-end pass (kept for provenance).
- `files/marginal_beta_calc.py` + `files/marginal_beta_case_note.md` —
  the β≈10⁻⁵ knife-edge case redo.
- `files/nongaussian_formation_survey.md` + `files/nongaussian_endtoend_note.md`
  — the non-Gaussian survey that selected curvaton/USR.
- `files/fork_conversion_note.md` — bounce killed as conversion mechanism
  (1 remnant/progenitor, f∼10⁻¹⁷–10⁻³¹).
- `files/fragmentation_vs_trapping_note.md` — fragmentation killed
  (triple no-go; O(1–20) relics vs required 10¹⁶–10³⁰).
- `files/shattering_bounce_spec.md` — the only surviving (literature-free)
  remainder: a horizon-destroying shattering bounce.
- `files/frag_check.py`, `files/briefing_bearing_assessment.md` — supporting.

## Headline results

- Curvaton: 182× headroom at 1.5×10⁻¹² (threshold caveat — fails for
  Δ_cr≳0.44) / 1317× at 2×10⁻¹⁹ (robust).
- USR: 18×/48× nominal after fixing a ~10× rms-vs-variance bug in the GW
  reduction (vs Abe et al. 2209.13891).
- The 1.5×10⁻¹² target peaks near 7 μHz (PTA/LISA gap); BBN/CMB integral
  bound gives 6,787–69,019× headroom — safest target, not riskiest.
- β≈10⁻⁵ marginal case: curvaton floor Ω_GW,0=1.64×10⁻⁹ but
  threshold-fragile (floor ∝ T⁸); USR 2.56×10⁻⁹ at ζ_c=1, ζ_c-sensitive.
  O4-era bound ~2.0×10⁻⁹ is within striking distance of the nominal USR
  point — data may decide it.

## Deliberately excluded

- Original `formation_endtoend_results.npz`: converted to JSON above.
- Nothing else of substance; the tree is complete and small.
