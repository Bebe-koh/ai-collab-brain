# HCBGW redshift-shuffle null — tech note (2026-09-24)

Status: **catalog re-identified (GRBweb Summary snapshot 2026-09-24); shuffle
null RUN on 734 redshift rows.** Everything below is exploratory/suggestive.
Nothing here is a detection.

## 1. Objective
Re-identify Jase's 9,180-row GRB catalog (82 GRBs at z=1.6–2.1 in a 50° cap
near RA 215.94°, Dec +49.51°; recorded permutation p≈0.0125), then run a
position-fixed redshift-shuffle null: keep sky positions fixed, permute
redshifts among entries, and measure how often ≥82 GRBs land in z∈[1.6,2.1]
inside the fixed cap.

## 2. Catalog re-identification — FAILED to match
Rebuilt from Jochen Greiner's public compilation
(https://www.mpe.mpg.de/~jcg/grbgen.html, downloaded 2026-09-24;
parser `~/workspace/grb/parse_greiner.py` → `~/workspace/grb/grb_catalog_greiner.csv`):

- 2,965 rows (vs 9,180 recorded) — Greiner's table only lists bursts localized
  to <1°, so it cannot be the source.
- 768 rows with a redshift entry; 99 with z∈[1.6,2.1] (vs 82 recorded;
  count includes qualified entries such as photo-z and limits — see `z_flag`).
- Parse spot-checked against known bursts (090423 z=8.26, 080319B z=0.937,
  221009A z=0.151).

Other candidates checked: Swift GRB table (~1,700 rows), Fermi GBM (~3,500),
BATSE (2,704) — none reaches 9,180. A web search for a 9,180-row GRB sample
found nothing. The most plausible source is the IceCube **GRBweb** aggregate
database, but its advertised bulk SQLite/txt download could not be retrieved
(links not exposed; summary-table page failed to load on 2026-09-24).

**Per the no-fabrication rule, the shuffle null was NOT run on the
non-matching catalog** — a p-value from different data would answer a
different question and could be mistaken for validation of the original
p≈0.0125. Exactly what's missing is documented in
`~/workspace/grb/PROVENANCE.md`.

## 2b. Catalog re-identification — RESOLVED via GRBweb (2026-09-24, ~16:10 PDT)
A live browser session retrieved the IceCube **GRBweb** bulk download:
- SQLite: https://user-web.icecube.wisc.edu/~grbweb_public/GRBweb2.sqlite
- Summary table (txt): https://user-web.icecube.wisc.edu/~grbweb_public/Summary_table.txt
(downloaded to `~/workspace/grb/Summary_table.txt`, 2.5 MB; site updates daily,
last update 2026-09-24 08:31 UTC).

Parsed counts (missing values coded −999; script `redshift_shuffle_test.py`):

| metric | recorded original | GRBweb snapshot 2026-09-24 |
|---|---|---|
| total rows | 9,180 | **9,187** |
| rows with measured z | — | 734 |
| z in [1.6, 2.1] | 82 | **84** |
| z-rows in 50° cap (RA 215.94°, Dec +49.51°) | — | 198 |
| z-rows in cap AND z∈[1.6,2.1] | (82 per §3 design) | **34** |

The 9,187 vs 9,180 row match (7 daily-update additions) and 84 vs 82 z-slice
match identify GRBweb's Summary table as the source catalog of the original
analysis, at an earlier snapshot. Redshift column: spectroscopic where
available (GRBweb aggregates published values; no photo-z/limit flags were
separated in this run — a refinement for later). Schema correction (from a
row-level check of GRB220810A against the pasted field inventory, 2026-09-24):
column 11 is **peak flux** (erg/cm²/s), not fluence_error — 3.0e-08 as a
fluence error would imply 0.0004% precision, implausible; as peak flux it is
sensible. All other pasted values (RA 309.35, Dec 2.66, T90 8.96, fluence
6.7868e-06, MJD 59801.9692) match the file exactly, including quirks
(T90_start = T0, T100 = T90) — confirming the inventory describes this file.

## 2d. Localization-quality robustness (2026-09-24)
The original analysis used pos_error for filtering/weighting, so the shuffle
null was re-run restricted to well-localized bursts (5,000 permutations each):

| pos_error cut | z-rows | observed in cap+z-slice | null mean ± sd | p |
|---|---|---|---|---|
| none | 734 | 34 | 22.69 ± 3.80 | 0.0024 |
| < 5° | 710 | 33 | 22.18 ± 3.76 | 0.0028 |
| < 2° | 707 | 32 | 22.01 ± 3.78 | 0.0060 |
| < 1° | 703 | 32 | 21.78 ± 3.73 | 0.0050 |
| < 0.5° | 703 | 32 | 21.78 ± 3.73 | 0.0050 |

(Median pos_error is 0.000° — most bursts are arcsecond Swift localizations;
only 31/734 are coarse GBM positions.) The signal is unchanged by removing
poorly localized bursts: not an artifact of coarse positions.

## 2e. Swift-exposure stratified null (2026-09-24) — the last GRB-data stone
The leading literature alternative is Swift/BAT sky-exposure anisotropy
(ecliptic poles get ~2× the exposure of the ecliptic plane; 157-month survey:
15–35 Ms). The cap center sits at ecliptic latitude 58.1° with modeled
exposure 29.1 Ms vs 25.3 Ms global — the concern is real, not hypothetical.
Direct checks on the GRBweb snapshot:
- Fraction of ALL bursts in cap: 0.1929 vs 0.1786 uniform expectation (mild).
- Redshift completeness in cap: 0.1117 vs 0.0799 global (+40% — real selection
  effect, already conditioned out by the position-fixed shuffle).
- Analytic exposure model E(β) = 15 + 20·|sin β| Ms, β = ecliptic latitude
  (calibrated to the published 15–35 Ms range; only the RANKING matters for
  stratification, and it is labeled approximate, not the measured map).

Key diagnostic — is the exposure↔z-slice link global or just the cap?
z-slice fraction by exposure tercile OUTSIDE the cap: lo 0.094, mid 0.079,
hi 0.110 (no meaningful gradient); INSIDE the cap (hi tercile): 0.202.
The apparent global correlation was the cap's overdensity leaking into the
tercile average — exposure does not predict z-slice membership elsewhere.

Stratified permutation (redshifts permuted WITHIN exposure terciles only,
10,000 shuffles): observed 34, stratified null 24.78 ± 3.64, **p = 0.0088**.
The overdensity survives Swift-exposure stratification.

Full null ladder on the GRBweb snapshot:
| null | p |
|---|---|
| fixed cap, plain redshift shuffle | 0.0030 |
| max-over-caps (look-elsewhere corrected) | 0.0175 |
| well-localized bursts only (pos_error < 1°) | 0.0050 |
| exposure-stratified shuffle | 0.0088 |

Remaining gaps (unchanged): no independent galaxy/lensing confirmation;
GRBweb redshifts used as published (no spec-z/photo-z separation); exposure
model analytic, not the measured BAT map. The GRB data alone cannot take this
further — the next step would be external data at z~2 in this sky region.

## 2c. Shuffle-null result (GRBweb snapshot, 2026-09-24)
Test: position-fixed redshift permutation among the 734 redshift rows;
count z∈[1.6,2.1] inside the FIXED 50° cap at (215.94°, +49.51°).
10,000 permutations (seed 42); look-elsewhere variant scans 126 cap centers
over the northern sky, 2,000 permutations.

| test | observed | null mean ± sd | p |
|---|---|---|---|
| fixed cap (recorded geometry) | 34 | 22.64 ± 3.85 | **0.0030** |
| max-over-caps (look-elsewhere corrected) | 34 (max at recorded center) | 26.02 ± — | **0.0175** |

The overdensity survives the redshift-shuffle null: p=0.003 at the recorded
geometry, p≈0.018 after correcting for the post-hoc cap placement — the
latter close to the recorded p≈0.0125. The shuffle controls for sky-position
selection effects (e.g., better redshift follow-up in the north: 198/734 =
27% of z-rows lie in the cap vs 17.9% of sky area).

What this null does NOT test: whether the GRB *sky positions themselves*
carry an instrument selection function (Swift exposure anisotropy is the
leading literature alternative — positions are held fixed by construction).
No independent galaxy/lensing confirmation exists. Result files:
`~/workspace/grb/grb_catalog.csv` (734 z-rows), `shuffle_result.json`,
pipeline `redshift_shuffle_test.py` (self-test passes on uniform data).

## 3. Null-test design (for when the catalog is recovered)
1. Take the redshift subset (entries with measured z); keep positions fixed.
2. Permute the redshift labels among these entries (≥10,000 shuffles).
3. For each shuffle, count entries with z∈[1.6,2.1] inside the FIXED 50°-radius
   cap centered at (RA 215.94°, Dec +49.51°).
4. p = fraction of shuffles with count ≥ observed (82).
5. Caveats to carry: (a) if the cap center was chosen after seeing the data,
   the fixed-cap p understates the look-elsewhere penalty — also run a
   max-over-caps variant; (b) redshift follow-up itself has a sky selection
   function (northern telescopes), which the position-fixed shuffle controls
   for only insofar as positions are held fixed — it does NOT correct the
   z-measurement selection; (c) use spectroscopic z only, matching Horváth et
   al.'s practice (exclude photo-z and Ly-α limits).

## 4. Literature status of the HCBGW claim (checked 2026-09-24)
- **Discovery:** Horváth, Hakkila & Bagoly (2013, 2014): angular clustering of
  GRBs at z≈1.6–2.1 (~19 GRBs in the original sample); proposed a ~2–3 Gpc
  structure, the largest claimed at the time.
- **Re-tests by proponents:** Horváth et al. (2015) strengthened the case;
  Horváth et al. (2020, MNRAS 498, 2544; arXiv:2008.03679) re-examined with
  487 GRBs, answered criticisms, and discussed observational bias
  (Ukwatta & Woźniak 2016); an April-2025 study used 542 GRBs with redshifts
  and reported a fourth, larger cluster (110–120 GRBs, z 0.33–2.43) while
  explicitly acknowledging unresolved biases.
- **Criticisms:** Swift sky-exposure anisotropy (ecliptic poles scanned ~1.83×
  more) is the leading alternative explanation; Horváth et al. countered with
  a χ² exposure/extinction test (p=0.025). Notably, Christian (2020)'s
  attempted rebuttal using Greiner's table reproduced p≈0.002 with the
  point-radius method — consistent with, not against, Horváth et al. (2014);
  Horváth et al. (2020) separately argued Greiner's table is a subjective
  compilation mixing spectroscopic, photometric, and limit redshifts.
- **Community verdict:** still debated, not settled either way. No independent
  confirmation from galaxy surveys or lensing exists; the GRB overdensity is
  best treated as a *candidate* structure. The proponents' own 2025 wording:
  "large-scale anomalies in the GRB spatial distribution can exist which are
  not necessarily seen in other cosmic objects" and "further detailed
  observations are necessary."

## 5. Bottom line
- The 9,180-row catalog is re-identified as the GRBweb Summary table at an
  earlier snapshot (today: 9,187 rows; z-slice 84 vs 82 recorded).
- The redshift-shuffle null was run on today's snapshot: the angular
  overdensity at the recorded cap survives — p=0.003 fixed geometry,
  p≈0.018 after look-elsewhere correction (close to the recorded p≈0.0125).
  This rules out "redshift follow-up happened to target that sky region" as
  the explanation; it does NOT rule out instrument exposure anisotropy in
  the positions themselves.
- The literature does not settle the HCBGW question; this result keeps the
  overdensity a *candidate* structure, now with one more selection-effect
  hypothesis tested and rejected. The two missing pieces from the portfolio
  audit (full selection-function correction, independent galaxy/lensing
  cross-check) remain missing. Nothing here is a detection.
- Refinements available if pursued: separate spectroscopic vs photo-z rows;
  rerun on Jase's original file if found (exact snapshot); Swift-exposure
  weighting of the null.
