# Reduction log — ALMA 2016.1.01404.V Sgr A* 2017-04-07 IQUV time series
**Project:** 2016.1.01404.V (PI Shep Doeleman, "Imaging the shadow of a supermassive black hole", TRACK_C VLBI)
**Date:** 2026-10-05 · **Operator:** Atlas (subagent) · **Purpose:** research-only transient search (Kerr/CS polarimetry)

## 1. What was downloaded (all public, QA2 PASS, public since 2018-10-20)

Member OUS: `uid://A001/X11b3/X35` (2017-04-07, 04:02–14:25 UT, MJD 57850.17–57850.60).
Archive source name: `Sagittarius_A_star`.

| File | Size (bytes) | Size check |
|---|---|---|
| `2016.1.01404.V_uid___A001_X11b3_X35_auxiliary.tar` (QA2 package) | 227,878,912 | matches DataLink metadata exactly |
| `2016.1.01404.V_uid___A001_X11b3_X35_001_of_001.tar` (member OUS) | 31,719,424 | matches DataLink metadata exactly |
| `member.uid___A001_X11b3_X35.README.txt` | 13,633 | — |

**QA2 verification (before any 107 GB download):** the auxiliary tar contains
`script/scriptForPI.py`, per-EB `uid___A002_Xbec3cb_*.ms.scriptForCalibration.py`
(8 scripts, APP QA2 v2.0), and `calibration/TRACK_C.calibration.tgz` with the
**polarization calibration tables**: `TRACK_C.calibrated.ms.Df0gen.APP`
(D-terms), `.Gpol2.APP`, `.Gxyamp.APP`, `.XY0.APP`, plus bandpass / flux_inf.APP /
phase_int.APP.XYsmooth. Correction to the assessment playbook: the member OUS
tar (`..._001_of_001.tar`) holds **only product FITS images**, NOT scriptForPI.py —
the script + calibration package live in the **auxiliary tar**.

### Raw ASDMs (8, via DataLink `#progenitor` links — verified URLs)

| # | ASDM UID | tar size (bytes) | status (2026-10-06) |
|---|---|---|---|
| 1 | uid://A002/Xbec3cb/X3d77 | 17,565,952,000 | pending |
| 2 | uid://A002/Xbec3cb/X3fe6 | 13,223,675,904 | queued (earlier ESO copy was tar-corrupt; needs fresh single-stream re-download) |
| 3 | uid://A002/Xbec3cb/X4227 | 13,597,136,896 | **DONE — IQUV extracted, raw+MS deleted** |
| 4 | uid://A002/Xbec3cb/X448f | 10,986,210,304 | **DONE — IQUV extracted, raw+MS deleted** |
| 5 | uid://A002/Xbec3cb/X468b | 15,457,030,144 | pending |
| 6 | uid://A002/Xbec3cb/X4947 | 10,585,548,800 | **DONE — IQUV extracted, raw+MS deleted** |
| 7 | uid://A002/Xbec3cb/X4bca | 11,977,251,840 | pending |
| 8 | uid://A002/Xbec3cb/X4de4 | 13,163,095,040 | pending |
| | **Total** | **106,555,900,928 (~99.2 GiB)** | |

DataLink endpoint used: `https://almascience.org/datalink/sync?ID=uid://A001/X11b3/X35`
(redirects to almascience.eso.org). NOTE: archive TAP (`/tap/sync`) rejects POST
through this network's proxy — GET-based TAP queries work.
Disk: only 95 GB free on /home/hatch → **sequential per-EB processing**
(download → restore → extract IQUV → delete raw). Network: ESO archive throttles
this route to ~0.7–3 MB/s per IP (5 parallel streams shared one ~3 MB/s cap; a
5th stream did not raise the aggregate). Strategy: 3 ALMA mirrors in parallel
(ESO / NRAO / NAOJ dataPortal, one stream each, ~0.7–0.9 MB/s each), X4947 from
ESO (resumed partial) + NRAO (fresh) racing for the chain test, X448f from NAOJ.

## 2. CASA installation (documented workaround chain)

CASA 5.1.1 tarball is **no longer hosted** (old `casa-release-5.1.1-5.el7.tar.gz`
URL → 404; casa.nrao.edu now lists only current releases). Used **CASA 6.7.6**
via pip (`casatools`, `casatasks`, `casadata`) in `~/workspace/alma_venv`
(Python 3.12, Ubuntu 24.04). Workarounds required:
1. `/tmp` is a 512 MB tmpfs → `TMPDIR=~/workspace/tmp_pip` for pip.
2. Bundled `libssl.so.3`, `libldap.so.2`, `liblber.so.2`, `libsasl2.so.3` in
   casatools are incompatible with the container's OpenSSL (needs
   `OPENSSL_3.0.1`/`EVP_md2`, not provided) → renamed to `*.bak`, system libs
   used instead. Native table tool verified on a real QA2 cal table.
3. casaconfig measures auto-update blocked by proxy → `~/.casa/config.py`
   points `measurespath` at the pip `casadata` payload; no network updates.

## 3. Script ports (no science parameters changed)

- `qa2_convert.py`: converts each `uid___A002_*.ms.scriptForCalibration.py`
  (Python 2) → Python 3. ONLY changes: `print X`→`print(X)`; drop
  `import casadef` + the 5.1.1 version gate (references undefined `CASAVER`);
  `from recipes.almahelpers import fixsyscaltimes` → documented no-op
  (fixsyscaltimes only corrects SYSCAL/Tsys timestamps; verified **no Tsys
  calibration** in any of the 8 scripts, so this is a true no-op).
  All task calls, scan/antenna/spw selections, cal-table names/order identical
  (verified by diff). All 8 converted scripts parse.
- `restore_eb.py`: replicates `scriptForPI.py`'s per-EB flow under CASA 6:
  extract ASDM → `importasdm` → (skip fixsyscaltimes, see above) → flagging →
  split science SPWs → `applycal` bandpass/flux/phase → split `.ms.split.cal` →
  `applycal` pol tables (`XY0.APP`, `Gxyamp.APP`, `Df0gen.APP`, `parang=True`) →
  split `.polcalibrated.APP.ms`.
- `calminispiral/MINISPIRAL_CALIBRATION_DO_ALL_py3.py`: `print >> f` →
  `print(..., file=f)` (4×); fixed a stray extra tab on one line (Python 2
  tolerated it, Python 3 does not); tabs expanded. Needs `tb`/`ia` tools and
  CASA tasks injected into globals at run time.

## 4. Reduction steps run

### X4947 (uid://A002/Xbec3cb/X4947) — COMPLETE
- Downloaded 10,585,548,800 bytes (ESO; size-verified), tar integrity OK.
- `restore_eb.py X4947`: importasdm + 12 QA2 steps → `uid___A002_Xbec3cb_X4947.polcalibrated.APP.ms` (8.2 GB).
  - CASA 5→6 fix: Step-6 `applycal` wrapped in try/except RuntimeError for calibrator
    fields with zero overlapping scans (J1744-3116 etc.); the QA2 script itself notes
    "THESE ERRORS SHOULD BE HARMLESS". Sgr A* applycal verified unaffected (112/112 scans).
- Split Sgr A* → `SGRA2017_X4947.ms` (894,724 rows).
- `extract_iquv.py X4947` → `sgra_work/SGRA2017_X4947_IQUV.npz`:
  432 integrations, 4.0 s median cadence, MJD 57850.463964–57850.496597
  (2017-04-07 11:08–11:55 UT), 4 SPWs (213.1/215.1/227.1/229.1 GHz),
  mean Stokes I ≈ 2.1–2.2 Jy, 0% NaN.
- Post-product cleanup: raw tar + all X4947 MSs deleted (freed ~86 GB).

### X448f (uid://A002/Xbec3cb/X448f) — COMPLETE
- Downloaded 10,986,210,304 bytes (NAOJ; size-verified, tar integrity OK).
- `restore_eb.py X448f`: importasdm + 12 QA2 steps → `uid___A002_Xbec3cb_X448f.polcalibrated.APP.ms` (8.2 GB).
  (One service restart killed the first attempt at Step 6; re-ran to completion.)
- Split Sgr A* → `SGRA2017_X448f.ms`.
- `extract_iquv.py X448f` → `sgra_work/SGRA2017_X448f_IQUV.npz`:
  428 integrations, 4.0 s median cadence, MJD 57850.358196–57850.390347
  (2017-04-07 08:36–09:22 UT), 4 SPWs, mean Stokes I ≈ 2.1–2.2 Jy, 0% NaN.
- Post-product cleanup: raw tar + all X448f MSs deleted.

### X4227 (uid://A002/Xbec3cb/X4227) — COMPLETE (2026-10-06, resumed after restart-drain)
- First download (NRAO, resumed multi-cycle) failed `tar -tf` despite exact size
  13,597,136,896 B → deleted; fresh single-stream NAOJ download completed,
  size-verified (13,597,136,896 B exactly).
- The restart-drain killed the first restore at Step 8/12. Re-ran `restore_eb.py X4227`
  cleanly (script wipes the partial workdir itself; raw ASDM re-used, no re-download).
- `restore_eb.py X4227`: importasdm + 12 QA2 steps → `uid___A002_Xbec3cb_X4227.polcalibrated.APP.ms`.
  (Same harmless Step-6 applycal warnings for J1924-2914/J1744-3116 as X4947.)
- `extract_iquv.py X4227` → `sgra_work/SGRA2017_X4227_IQUV.npz`:
  532 integrations, 4.0 s median cadence, MJD 57850.298127–57850.347354
  (2017-04-07 07:09–08:20 UT), 4 SPWs (213.1/215.1/227.1/229.1 GHz),
  mean Stokes I ≈ 2.136 Jy, 0% NaN.
- Post-product cleanup: raw tar + all X4227 MSs deleted. Disk back to 7%.

- Incident 2026-10-06 ~10:21 UTC: a stray X3fe6 restore was launched while its raw tar
  was absent/corrupt; tar extraction failed as expected and left garbage entries
  in restore/raw/ — cleaned (`rm -rf restore/raw`, recreated empty). X3fe6 remains
  queued for a FRESH re-download; no restore until its tar is size+tar-tf verified.

### Download integrity lesson (2026-10-06)
Resumed multi-cycle downloads can produce size-correct but tar-corrupt files
(X3fe6 ESO and X4227 NRAO both failed `tar -tf` despite exact byte sizes).
Policy: verify with `tar -tf` before restore; on corruption, delete and
re-download fresh single-stream (no resume).

## 5. Storage-driven sequential processing (2026-10-06)
Disk (/home/hatch, 100 GB) hit 94% with raw/ at 34 GB and restore/ at 80 GB.
Switched to strictly sequential per-EB processing effective immediately:
1. All download streams stopped; no new ASDM downloads until disk under control.
2. One EB at a time: download → restore → split → IQUV extract → verify →
   **delete raw tar + all EB measurement sets** → next EB.
3. Kept: QA2 auxiliary/member tars, scripts, logs, IQUV NPZ products, alma_venv.
4. Pipeline hardened for unattended sequential runs:
   - `restore_eb.py`: auto-handles ESO tars' deep nested ASDM path.
   - All 8 converted QA2 scripts: Step-6 applycal try/except patch.
   - `extract_iquv.py`: generalized to `extract_iquv.py <SFX>`.
   - Note: `calminispiral` Step 3 (visibility modelfitting) needs ~22 GB RAM;
     system has 7.7 GB → OOM. Using memory-efficient chunked visibility-averaged
     IQUV extraction instead (see §6).

## 6. Data-quality flags
- README (QA2): use **APP-mode scans only** for polarization; ALMA-mode scans
  have poorer parallactic-angle coverage of the pol calibrator. The restore
  selects APP scans/antennas per the QA2 scripts (phased array `&`).
- Flux scale: constant few-% amplitude bias (Tsys not used in APP QA2);
  absolute flux accuracy ~10% — irrelevant for a transient *search*.
- Shortcut NOT taken: emailing M. Wielgus for the published 4-s IQUV curves
  (A&A 665 L6) — needs the user's explicit go-ahead.

### X3fe6 (uid://A002/Xbec3cb/X3fe6) — FAILED at stage 'download' (2 attempts)
- size/curl failure after 2 attempts (see raw/dl_X3fe6.log)
- Moved on to next EB per failure policy.

### X3d77 (uid://A002/Xbec3cb/X3d77) — FAILED at stage 'download' (2 attempts)
- size/curl failure after 2 attempts (see raw/dl_X3d77.log)
- Moved on to next EB per failure policy.
