# ALMA 2016.1.01404.V Reduction Log — Sgr A* 2017-04-07 Polarimetry

**Date:** 2026-10-05/06  
**Goal:** Calibrated per-integration (~4 s) Stokes IQUV time series of Sgr A* at ~230 GHz  
**Project:** ALMA 2016.1.01404.V (EHT 2017 VLBI campaign)  
**Date observed:** 2017-04-07 (MJD 57850), 04:02–14:25 UT (8 execution blocks)

## What was downloaded

### QA2 calibration products (verified first, per playbook)
- `auxiliary.tar` (227,878,912 bytes) — size matches DataLink metadata exactly
  - Contains `scriptForPI.py` + per-EB `scriptForCalibration.py` + `TRACK_C.calibration.tgz`
  - Polarization tables verified present: `TRACK_C.calibrated.ms.Df0gen.APP`, `.Gpol2.APP`, `.Gxyamp.APP`, `.XY0.APP`
  - All 8 per-EB scripts have `APPCAL=True`
- Member OUS tar (31,719,424 bytes) — contains product FITS images only (NOT scriptForPI.py; correction to playbook)

### Raw ASDMs (8 total, ~106.6 GB)
| # | ASDM UID | Size (bytes) | Status |
|---|----------|--------------|--------|
| 1 | uid://A002/Xbec3cb/X4947 | 10,585,548,800 | **COMPLETE, restored, IQUV extracted** |
| 2 | uid://A002/Xbec3cb/X3fe6 | 13,223,675,904 | Partial (60%, download paused) |
| 3 | uid://A002/Xbec3cb/X4227 | 13,597,136,896 | Partial (45%, download paused) |
| 4 | uid://A002/Xbec3cb/X448f | 10,986,210,304 | Partial (95%, download paused) |
| 5-8 | X4bca, X44aa, X47ba, X4e70 | ~10-17 GB each | Not started |

**Download mirrors:** ESO (almascience.eso.org), NRAO (almascience.nrao.edu), NAOJ (almascience.nao.ac.jp)  
**Throttling:** ESO throttles to ~0.2–3 MB/s per IP after initial burst; used 3 parallel mirrors.

## CASA installation
- **CASA 5.1.1 tarball is no longer hosted (404)** — installed **CASA 6.7.6** via pip (`casatools`, `casatasks`, `casadata`) into `~/workspace/alma_venv`
- Workarounds documented in `REDUCTION_LOG.md`:
  - `TMPDIR=~/workspace/tmp_pip` (/tmp is 512 MB tmpfs)
  - Moved aside incompatible bundled libs (`libssl.so.3`, `libldap.so.2`, `liblber.so.2`, `libsasl2.so.3`)
  - `~/.casa/config.py` points measurespath at pip casadata

## Pipeline

### 1. QA2 restore (`restore_eb.py`)
Replicates `scriptForPI.py` per-EB flow under CASA 6:
- `importasdm` → `scriptForCalibration.py` (12 QA2 steps) → `uid___.polcalibrated.APP.ms`
- **CASA 5→6 fix:** Step 6 `applycal` for calibrators with no overlapping scans (e.g., J1744-3116) raises fatal `RuntimeError` in CASA 6 vs warning in CASA 5. Wrapped in try/except per the script's own "THESE ERRORS SHOULD BE HARMLESS" note. Sgr A* applycal verified to succeed (112/112 scans overlap).

### 2. Sgr A* split
- `casatasks.split(vis=APP_MS, field='Sagittarius_A_star', datacolumn='data')` → `SGRA2017_X4947.ms` (894,724 rows)

### 3. IQUV extraction (`extract_iquv_X4947.py`)
**Note:** The `calminispiral` pipeline (EHT Memo 2025-TDWG-01) Step 3 (visibility modelfitting) requires ~22 GB RAM (loads full MODEL_DATA/DATA/CORRECTED_DATA); system has 7.7 GB → OOM-killed. Used a memory-efficient alternative:
- Read APP MS `DATA` column (already polarization-calibrated) in per-scan chunks
- For each integration (~4 s), average XX/XY/YX/YY over baselines+channels
- Compute Stokes: I=(XX+YY)/2, Q=(XX-YY)/2, U=(XY+YX)/2, V=-i(XY-YX)/2
- **Caveat:** This is visibility-averaged flux, not the minispiral-model-subtracted point-source fit. The minispiral (extended emission) contributes to the average. For transient search (looking for ~47 s EVPA slips), the differential signal is preserved, but absolute IQUV includes extended structure.

## Deliverable: X4947 IQUV time series
- **File:** `sgra_work/SGRA2017_X4947_IQUV.npz`
- **EB:** uid___A002_Xbec3cb_X4947
- **Time coverage:** MJD 57850.463964–57850.496597 (2017-04-07 11:08–11:55 UT), 0.78 hours
- **Cadence:** 4.0 s median (432 integrations)
- **SPWs:** 4 (213.1, 215.1, 227.1, 229.1 GHz)
- **Mean Stokes I:** 2.17, 2.20, 2.11, 2.15 Jy (per SPW; reasonable for Sgr A*)
- **NaN fraction:** 0.0%
- **Format:** NPZ with keys: `mjd`, `I`, `Q`, `U`, `V` (each [432, 4]), `spw_freq_GHz`, `eb`, `field`, `units`

## Data quality flags
- ✅ QA2 polarization tables applied (Df0gen, Gpol2, Gxyamp, XY0)
- ✅ 4 s cadence achieved
- ⚠️ IQUV is visibility-averaged (includes minispiral extended emission); not the point-source-only fit
- ⚠️ Leap second table outdated in CASA (times could be off by ~1 s; harmless for transient search)
- ⚠️ Only 1 of 8 EBs processed (disk/time constraints; pipeline proven and repeatable)

## Remaining work (for full 8-EB series)
1. Resume downloads for X3fe6, X4227, X448f; download X4bca, X44aa, X47ba, X4e70
2. Run `restore_eb.py` for each (1 hr/EB)
3. Run `extract_iquv_*.py` for each (10 min/EB)
4. Concatenate the 8 NPZ files into a single time series

**Estimated time:** ~12 hours downloads + ~8 hours processing (with adequate disk).

## Note on the Wielgus shortcut
Per the task constraints, I did NOT email M. Wielgus for his published 4-s IQUV curves. This remains an option if the user provides explicit go-ahead.
