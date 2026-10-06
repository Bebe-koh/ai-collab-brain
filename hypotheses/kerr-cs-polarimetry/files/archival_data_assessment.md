# Archival data assessment: fastest public dataset for a calibrator-differential R(t) transient search in Sgr A*

**Date:** 2026-10-05 · **Status:** research-only assessment, no multi-GB downloads performed; all sizes from public directory listings and archive metadata.
**Goal:** find the fastest *public* dataset on which to run the calibrator-differential transient search (R(t) statistic) for ~47 s, ~55.6° EVPA transients in Sgr A*. The test needs (a) full-polarization visibilities or light curves at ≤10 s sampling, and (b) interleaved calibrator scans (3C 279 / J1924-2914 / NRAO 530) for the instrumental-jump veto.

**Bottom line:** No pre-made downloadable 4-s IQUV light-curve table exists for 2017. The fastest *verified* route today is Path C: re-derive Stokes IQUV light curves from ALMA project 2016.1.01404.V (2017-04-07; ~107 GB raw + ~260 MB of pre-made QA2 calibration products, CASA restore, then the public `calminispiral` pipeline). Path B (2026-D01-01) is a dead end — it is M87\*-only. Path A has verified calibrator scans but costs ~100 GB minimum plus a full VLBI calibration chain.

---

## PATH A — EHT 2018/2021 "Complete L1 Data Products" (public, raw correlator output)

### What it is
L1 = VLBI correlator output converted to circular polarization basis (PolConvert v1.7.9, ALMA QA2 input), fringe-fit QA'd (fourfit) — but **not** amplitude/phase/leakage calibrated. Described in EHTC et al. 2024, A&A 681, A79 (arXiv:2312.03505).

### Verified locations
- **2018:** ESO `https://almascience.eso.org/almadata/ec/eht-2018/Apr2018/2017.1.00797.V/` and CyVerse DOI **10.25739/v7hh-6244** (published 2026-04-08; data product code 2024-D03-01). Description doc: `.../2017.1.00797.V/group.uid___A001_X12d1_X75.ec_sdoeleman.description.pdf`.
- **2021:** ESO `https://almascience.eso.org/almadata/ec/eht-2021/2019.1.01812.V/` and CyVerse DOI **10.25739/vddx-w132** (published 2026-04-08). Description doc: `.../2019.1.01812.V/group.uid___A001_X1528_X20b.ec_doeleman.description.pdf`.

### File naming (verified from description docs)
`{groupuid}.ec_{nick}.e{YY}{track}{DD}-{rev}-b{1-4}-{project}-{TARGET}-{type}.tar`
- e.g. `e18c21` = 2018, track c, April 21; `e21a14` = 2021, track a, April 14.
- b1–b4 = 213.1 / 215.1 / 227.1 / 229.1 GHz band centers.
- project `sgra` = ALMA SGRA-project scans (ALMA in array, PolConvert applied); `na` = scans **not** involving ALMA (smaller, fewer baselines).
- type: `fits` (FITS-IDI, loadable in AIPS/CASA), `hops` (Mk4/HOPS), `swin` (raw DiFX), `4fit` (fringe QA), `dxin` (correlator inputs incl. VEX + `.v2d`), `pcin`/`pcqk` (PolConvert), `haxp` (mixed-pol ALMA-only). Plus `*.app_deliverables.tgz` (ALMA QA2, ~300 MB/track) and `EHTmetadata_*.tar.gz` (ANTAB a-priori gains, ~453 MB for Apr 2018).

### Calibrator scans — VERIFIED present (from actual listings)
- **2018-04-21 (e18c21):** SGRA + **NRAO 530** (sgra-project, with ALMA) + OJ287. No 3C279/J1924-2914 found on this day.
- **2018-04-24 (e18a24):** SGRA + **3C279** + **J1924-2914** + **NRAO 530** (all sgra-project, with ALMA) + BLLAC, CYG-A, J1800-7828, J2015-3710, J2257-3627 (na-project).
- **2021-04-14 (e21a14, "no major issues"):** SGRA + **J1924-2914** + **NRAO 530** + **3C279** + J1743-0350. (2021-04-16 had only 5 stations — avoid.)
- Multiple revision numbers exist per band (e.g. e18c21 rev -1/-2/-5); use the latest revision available for each band.

### Sizes (from listings; `fits.tar` = FITS-IDI per band)
- 2018-04-21 SGRA (sgra): **55–65 GB/band** → ~240 GB all 4 bands. NRAO530: ~12–13 GB/band.
- 2018-04-24 SGRA (sgra) b1: **88 GB**; J1924-2914: 4.7 GB; NRAO530: 8.6 GB; 3C279: 206 MB (per band).
- 2021-04-14 SGRA (sgra) b1: **85 GB**; J1924-2914: 11 GB; J1743-0350: 9.1 GB; NRAO530: 413 MB; 3C279: 772–798 MB (per band).
- **Minimal useful VLBI download (one day, one band, SGRA + one bright calibrator): ~70–100 GB.** Full 4-band day: ~300–400 GB.

### Calibration burden (concrete)
1. Fringe fitting + a-priori amplitude calibration (ANTAB metadata supplied) + network calibration + polarimetric leakage (d-term) calibration, using either:
   - **eht-hops** (Blackburn et al. 2019; https://github.com/sao-eht/eat), or
   - **rPICARD** (Janssen et al. 2019, A&A 626 A75; open source, https://bitbucket.org/M_Janssen/Picard, dockerized CASA-VLBI build; calibration strategy for 2018/2021 in von Fellenberg et al. 2025).
2. Average to 10 s, form closure phases / the R(t) statistic.
3. Correlator dump interval is **not** stated in the description docs (verify from the small `dxin` `.v2d` files, 5–100 MB); fine-grained dumps are expected (DiFX output), so 10-s averaging is safe.
4. Realistic effort: weeks of VLBI-methods work even with the pipelines; ~100 GB download minimum.

### Path A verdict
Calibrator scans verified, but this is the **slowest** path: hundreds of GB and a full VLBI calibration chain before the first R(t) value exists.

---

## PATH B — "2018 and 2021 Calibrated polarimetric data" (2026-D01-01, released 2026-06-29, CyVerse)

**Verdict: DEAD END for the Sgr A* R(t) search — the release is M87*-only.**

### Release identity (verified)
- EHT data portal (https://eventhorizontelescope.org/for-astronomers/data) row: `2026-D01-01 | 2018 and 2021 Calibrated polarimetric data | The EHT Collaboration et al. | Jun 29, 2026 | Cyverse Data Commons` — notably, **no DOI listed** (every other release has one).
- Reference paper: EHTC et al. 2025, A&A 704, A91 — "Horizon-scale variability of M87* from 2017–2021 EHT observations" (arXiv:2509.24593). Three epochs of **M87\*** polarized images at 230 GHz (2017/2018/2021). **No Sgr A\*.**
- Expected contents (from the paper + the 2023-D01-01 polarimetric-release precedent): M87\* 2018 (Apr 21/22/27) and 2021 (Apr 17–18), four bands, full-pol circular basis, 10-s averaging, calibrated via EHT-HOPS (2017/2018) and rPICARD (2021); D-terms from Themis leakage solutions solved **on M87\* itself** — i.e., the polarimetric calibration did not use calibrator scans, so there was no reason to ship them.

### Calibrator scans — NO (high confidence, indirect)
- Every EHT calibrated release to date is **target-only**: 2019-D01-01 (M87), 2023-D01-01 (M87 2017 polarimetric, "M87 in 2017" per its README), 2024-D01-01 (M87 2018 Stokes-I), 2022-D02-01 (Sgr A\* only). Calibrators get separate dedicated releases (e.g. 2020-D01-02 "First 3C279 EHT Results").
- Caveat: the actual CyVerse folder listing could **not** be reached — the folder is not indexed by search engines, is absent from the dc.cyverse.org CKAN catalog (15 EHT datasets listed, none the 2026 release; consistent with the missing DOI — the catalog entry appears still pending), and no `eventhorizontelescope/2026-D01-01` GitHub inventory repo exists yet. To verify directly: a live-browser session on the Data Commons curated browse tree, or the CyVerse/iRODS API. But the reference paper pins the contents to M87\*, so the listing is not expected to change this verdict.

### What would need downloading for "one day of Sgr A\* + one calibrator"
Nothing exists for that combination in this release. The request is unsatisfiable from Path B.

### Upside note
If the team ever wants a transient/EVPA test on **M87\*** (2021 data, better (u,v) than 2017, 10-s integrations, already D-term- and EVPA-calibrated), 2026-D01-01 would be the fastest VLBI path — but without calibrator scans, R(t) would need a self-differential or single-dish-reference adaptation.

---

## PATH C — ALMA archival full-polarization Sgr A* monitoring (integrated-EVPA search)

### C1. Project 2016.1.01404.V (2017 EHT campaign; archive source name `Sagittarius_A_star`)
- **Verified via ALMA TAP + DataLink (2026-10-05):** Band 6, full-pol `/XX/XY/YX/YY/`, three days: 2017-04-06, 2017-04-07, 2017-04-11 (MJDs 57849/57850/57854). Public since 2018-10-20, QA2 PASS.
- **2017-04-07** (member OUS `uid://A001/X11b3/X35`, 04:02–14:25 UT): **8 raw ASDM tars ≈ 106.6 GB** (10.6–17.6 GB each) + `..._auxiliary.tar` (**227.9 MB**, QA2 products) + member OUS tar (**31.7 MB**: calibration dir, `scriptForPI.py`, QA2 weblog, README).
  - Small-file URLs (verbatim from archive DataLink):
    - https://almascience.eso.org/dataPortal/2016.1.01404.V_uid___A001_X11b3_X35_auxiliary.tar
    - https://almascience.eso.org/dataPortal/member.uid___A001_X11b3_X35.README.txt
- **ASDM → calibrated Q/U time series:** calibrated in CASA 5.1.1-5 via the EHT-VLBI QA2 process (Goddi et al. 2019, PASP 131, 075003). The README states the PI **cannot reproduce** the polarization calibration tables — they are supplied pre-made; `scriptForPI.py` applies them to the raw EBs. Then per-integration IQUV extraction (minispiral-model self-cal + point-source fit, as in Wielgus et al. 2022 ApJL §2 / the A2 pipeline). Closest public implementation: the CASA pipeline from EHT Memo 2025-TDWG-01, https://github.com/ealruiz/calminispiral (produces Stokes I, linear-pol intensity, EVPA, Stokes V light curves; demonstrated on 2018 data, method applies to 2017).
- Effort: ~107 GB download + CASA restore + light-curve extraction. No polarimetric-calibration expertise needed (tables pre-made). Days of compute, not weeks of methods work.

### C2. Published light-curve tables (checked 2026-10-05)
- **Wielgus et al. 2022, ApJL 930, L19** (arXiv:2207.06829): Stokes **I only**, 4-s cadence, Apr 6/7/11. **No downloadable table found** (no VizieR `J/ApJ/930/L19`, no Dataverse, no arXiv ancillary; EHT CyVerse release doi:10.25739/m140-ct59 is VLBI visibilities with polarization explicitly removed — useless for EVPA). IOP machine-readable supplement: could not verify (journal page fetch failed).
- **Wielgus et al. 2022, A&A 665, L6** (arXiv:2209.09926): **full-Stokes IQUV**, 4-s cadence, four 2-GHz bands, Apr 6/7/11 — exactly the needed product. **No downloadable table found** (no VizieR `J/A+A/665/L6`, no arXiv ancillary, no Dataverse). Follow-on groups (Yfantis et al. 2024 A&A 685 A142; Ricarte et al. 2025 arXiv:2504.01114) obtained it from the authors.
- **Goddi et al. 2021, ApJL 910, L14:** polarimetric survey; no Sgr A* light-curve tables. Its deliverable is the QA2 process embodied in the archive auxiliary tars.
- **Albentosa-Ruiz et al. 2026, A&A 708, A179** (arXiv:2604.10287): EXISTS — "Full-polarization millimeter wavelength variability of Sgr A* during the **2018** EHT campaign" (not 2017). No VizieR catalog; downloadable light curves not confirmed. Companion: EHT Memo 2025-TDWG-01 (arXiv:2503.11258) + `calminispiral` pipeline above.
- **Shortcut worth one email (not sent):** ask M. Wielgus for the A1/A2 4-s IQUV light curves from A&A 665 L6 — already shared with Yfantis/Ricarte groups; if shared, the search runs on an MB-scale CSV with zero calibration work.

### C3. Project 2023.1.01243.V (EHT 2024 campaign)
- **The main 2024-04-08 ASDM is NOT public.** Verified via TAP: ASDM `uid://A002/X115643f/X960d` (MJD 60404, full-pol `SgrA_star`, qa2_passed=T) shows `data_rights=Proprietary`, `obs_release_date=2027-07-29` — locked until **July 2027**.
- The 2026-06-13 release date applied only to the **2024-04-12** ASDM (`uid://A002/X1158102/X18933`, Public since 2026-06-13), which **does** contain full-pol `SgrA_star` (06:26–14:23 UT). Usable for the same test, but no speed advantage over 2017 (same calibration route; raw volume not quantified).

### Path C verdict
**No pre-made downloadable 4-s IQUV table exists.** Fastest verified route: re-derive from 2016.1.01404.V (~107 GB + 260 MB QA2, CASA restore, `calminispiral` extraction). The Wielgus A&A 665 L6 data-by-email shortcut could collapse this to an MB-scale CSV.

---

## Ranked recommendation (final)

1. **Path C first** — fastest to a running search: single-dish/interferometer IQUV light curves, pre-made calibration tables, public extraction pipeline; ~107 GB download, days of work. Try the Wielgus email shortcut in parallel (A&A 665 L6 4-s IQUV curves, already shared with other groups — could collapse this to an MB-scale CSV).
2. **Path A** — the only VLBI route with verified Sgr A\* + calibrator scans (2018-04-24: SGRA + 3C279 + J1924-2914 + NRAO530, all with ALMA; 2021-04-14 similar). Price: ~100 GB minimum (one day, one band, SGRA + one calibrator; ~400 GB for a full 4-band day) and a full eht-hops/rPICARD calibration chain (weeks of methods work).
3. **Path B — NO-GO** for Sgr A\*: M87\*-only release; target-only releases never carry calibrator scans. (Upside: fastest VLBI path if the test is ever adapted to M87\*.)

## Concrete next commands (recommended path = C)

```bash
# 1. Small QA2 package first (verify contents before the big download)
curl -L -o auxiliary.tar "https://almascience.eso.org/dataPortal/2016.1.01404.V_uid___A001_X11b3_X35_auxiliary.tar"
curl -L -o README.txt  "https://almascience.eso.org/dataPortal/member.uid___A001_X11b3_X35.README.txt"
# 2. Then the 8 raw ASDM tars for 2017-04-07 (~106.6 GB total) via the ALMA archive
#    (DataLink URLs from the archive query for member OUS uid://A001/X11b3/X35)
# 3. Restore in CASA 5.1.1: execfile('scriptForPI.py') from the member OUS tar
# 4. Extract per-integration IQUV light curves with https://github.com/ealruiz/calminispiral
# 5. In parallel: email M. Wielgus requesting the A&A 665 L6 4-s IQUV light curves (Apr 6/7/11 2017)
```

## Could not verify
- Correlator dump interval of L1 products (check small `dxin` `.v2d` files).
- IOP machine-readable supplements for ApJL 930 L19 (journal fetch failed).
- Electronic light-curve tables for A&A 708 A179.
- Exact contents of the 227.9 MB auxiliary tar (not downloaded; metadata-only).
- Raw data volume for 2023.1.01243.V 2024-04-12.
- The actual CyVerse folder listing of 2026-D01-01 (not indexed; CKAN catalog entry appears pending; no DOI). The reference paper pins it to M87\*, so this is not expected to change the verdict.
