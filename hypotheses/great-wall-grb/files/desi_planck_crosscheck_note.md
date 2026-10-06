# DESI DR1 QSO × Planck PR4 cross-check of the HCBGW candidate — tech note
Date: 2026-10-03. Author: Atlas (worker agent). Status: **analysis run on public data; verdict below.**
Reproducibility: code `~/workspace/grb/desi_cap_test.py`, `~/workspace/grb/kappa_xcheck.py`,
`~/workspace/grb/build_kappa.py`; products in `~/workspace/grb/crosscheck_products/`
(`desi_cap_result.json`, `control_caps.csv`, `kappa_xcheck_result.json`);
venv `~/workspace/grb/venv` (astropy 8.0.1, healpy 1.20.0).

## 1. Question
The GRBweb analysis (see `hcbqw_shuffle_note.md`) found 34 GRBs vs 22.6 expected
in a 50°-radius cap at (RA 215.94°, Dec +49.51°), z ∈ [1.6, 2.1] — a ~50% excess,
p = 0.0030 fixed geometry, p ≈ 0.0175 look-elsewhere corrected. GRB data alone
cannot go further. This note runs the decisive independent-tracer test:
do DESI DR1 spectroscopic quasars — 3,400× more objects in the same cap and
redshift slice — show the overdensity? A real Gpc-scale *matter* structure
must appear in quasars (bias b ≈ 2–2.5 at z ~ 2).

## 2. Data
- **DESI DR1 LSS** (public, v1.5pip iron): `QSO_NGC_clustering.dat.fits`
  (793,229 quasars, 0.8 < z < 3.5) with completeness weights `WEIGHT`;
  randoms `QSO_NGC_0_clustering.ran.fits` (11,610,722 rows, ~15× data) for the
  angular selection function. Cap center is in the NGC footprint; SGC overlap
  of the cap is negligible (cap Dec range −0.5°…+90°).
- **Redshift slice**: 1.6 < z < 2.1 exactly, matching the GRB slice.
  230,520 quasars (weighted N = 233,113) in the slice over NGC.
- **Planck PR4 κ**: `PR42018like_klm_{dat,mf}_MV.fits` from the
  carronj/planck_PR4_lensing GitHub release (see §5 for why this leg failed).

## 3. Method — fixed-cap count test with empirical (control-cap) null
- N_cap = Σ WEIGHT of slice quasars inside the 50° cap.
- N_exp = f_cap × Σ WEIGHT of all slice quasars, where f_cap = weighted
  random fraction inside the cap (mask-conditioned expectation).
- δ = N_cap / N_exp − 1.
- **Null**: 500 control caps (50° radius, random centers, required
  N_exp ≥ 20% of the HCB cap's N_exp so coverage is comparable). The control
  δ distribution empirically captures Poisson noise, cosmic variance, AND
  residual imaging systematics — no analytic error model is trusted.
  Reported p = fraction of control caps with δ ≥ δ_HCB (look-elsewhere
  corrected by construction).
- Secondary: east/west half-cap split (exploratory localization only).

## 4. Results — quasar counts
| quantity | value |
|---|---|
| Slice quasars (NGC, weighted) | 233,113 (230,520 raw) |
| HCB cap N (weighted) | 116,025 (113,633 raw) |
| HCB cap N_exp (randoms) | 114,162 |
| δ_HCB | **+0.0163** ± 0.0030 (Poisson only) |
| Control caps (n=500): mean ± sd | +0.0052 ± **0.0170** |
| HCB z-score vs controls | **+0.65σ** |
| Empirical p (δ ≥ δ_HCB) | **0.218** |
| East half δ / West half δ | +0.0088 / +0.0293 (exploratory) |

Robustness: unweighted counts give δ = −0.025 (4% swing from WEIGHT_SYS —
significant imaging systematics in this region, which is exactly why the
control-cap null, not Poisson, is the error bar); narrower slice 1.7 < z < 2.0
gives δ = +0.015. Conclusion unchanged under all variants.

**The independent tracer shows no significant overdensity.** The +1.6% excess
is 0.65σ against the empirical control distribution (p = 0.22). Note the
control sd (1.7%) is 5.7× the Poisson error (0.3%) — a naive Poisson test
would have falsely claimed 5.4σ. The control caps are doing essential work.

## 5. Planck PR4 κ leg — attempted, INCONCLUSIVE (map calibration blocked)
Built a κ map from the PR4 `klm_dat_MV` − `klm_mf_MV` alms (NSIDE 1024, analysis
mask applied). Validation FAILED:
- κ × DESI-QSO cross-power S/N (100 < ℓ < 400) = **0.9** — a real κ map must
  correlate positively with z ~ 2 quasars at high significance.
- Map power D_ℓ ~ 3×10⁻² at ℓ = 400, ~10⁴–10⁵× the expected κ power;
  cross-checks (no mean-field subtraction, TT vs MV) all show no LSS correlation.
- The GitHub release provides no documented normalization for the klm files;
  the absolute κ scale could not be recovered from public documentation.

The cap-mean κ test was run anyway (HCB mean κ vs 500 control caps: z = +0.90,
p = 0.18) but is **uninterpretable** given the failed validation — reported
here only for completeness, not as evidence either way. A future run with a
calibrated κ map (PR3 from PLA, or ACT DR6) could add an independent mass
probe, but it is not needed for the verdict below.

## 6. Verdict: candidate WEAKENED — ruled out as a Gpc-scale matter overdensity
The GRB excess (50% ± ~25%, 34 vs 22.6) cannot be a matter-density fluctuation:
- Quasar 1σ measurement: δ_q = +0.016 ± 0.017 → 95% one-sided upper limit
  δ_q < 0.044. With quasar bias b_q ≈ 2.4 at z ~ 2: **δ_m < 0.018** (95%).
- The GRB excess requires b_GRB × δ_m = 0.50. At δ_m < 0.018 this demands
  **b_GRB > 27** (95% lower limit) — an implausible GRB bias
  on Gpc scales (literature estimates: b_GRB ~ 2–5).
- 116k quasars vs 34 GRBs: the independent, 3,400× larger sample is a typical
  patch of sky (p = 0.22).

What remains: the GRB angular overdensity is real as a *GRB-count* statement
(p ≈ 0.018 look-elsewhere corrected), but it does not correspond to excess
*mass*. Remaining explanations: a statistical fluke (~2% of random skies show
such a fluctuation), or a GRB-specific selection effect not yet identified
(Swift-exposure and redshift-follow-up stratification were tested and rejected
in `hcbqw_shuffle_note.md`, but the GRB position selection function was never
directly measured). This is consistent with Fujii (2022), who found SDSS DR7
quasars consistent with homogeneity over ~half the region — now confirmed over
the FULL cap with 3× the quasar density.

**Bottom line: the Hercules–Corona Borealis "Great Wall" is not a giant matter
structure. The GRB clustering that motivated it has no counterpart in 116,000
independent quasars covering the same sky and redshift. The candidate as a
physical overdensity is dead; only the unexplained GRB-count fluctuation
remains, and it is not evidence of a structure.**

## 7. Caveats
- Quasar bias b_q ≈ 2.4 adopted from DESI DR1 QSO clustering; a much lower
  effective bias would weaken the δ_m limit, but no plausible bias model
  bridges the factor-28 gap.
- The κ leg is inconclusive (see §5); a calibrated lensing map would be a
  useful second independent probe but cannot resurrect the matter-structure
  hypothesis given the quasar null.
- GRB redshifts used as published (no spec-z/photo-z separation), same as the
  original analysis; does not affect the quasar result.
- DESI DR1 NGC footprint covers the cap at f_cap = 0.49 of randoms; the
  northernmost cap edge (Dec > 79°) lies outside DESI — the test is conditioned
  on the actual overlap via randoms, which is the correct procedure.
