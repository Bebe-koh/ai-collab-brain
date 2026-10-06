# kerr-cs-polarimetry — files index

**Question:** does a dynamical pseudoscalar θ coupled via θF F̃ imprint an
achromatic EVPA transient near a Kerr black hole?
**Status (2026-10-06):** first real-data test = NULL in 3 of 8 ALMA EBs;
reduction of the remaining 5 is running (self-healing pipeline).

## Layout

- `files/alma_data/` — the ALMA 2016.1.01404.V (2017-04-07) transient search.
  - `evpa_transient_search_v2.py` — **current search code** (repaired v2).
    Supersedes `evpa_transient_search.py` (v1, kept for provenance).
  - `SGRA2017_X4227_IQUV.csv`, `SGRA2017_X448f_IQUV.csv`,
    `SGRA2017_X4947_IQUV.csv` (+ `META.txt`) — I/Q/U/V per 4-s integration,
    4 spectral windows. Converted from the original `.npz` files to plain
    CSV so every connected app can read them without numpy.
  - `v2_results/v2_audit_repair_note.md` — what the external audit caught
    (unwrap axis, surrogate nulls, OLS fits, unenforced vetoes) and how v2
    repaired each.
  - `v2_results/transient_search_v2_report.md` — the corrected result.
  - `v2_results/transient_search_v2_SGRA2017_*.md` — per-EB detail.
  - `REDUCTION_LOG.md`, `EB_FAILURES.md`, `asdm_list.txt` — reduction ops.
  - `extract_iquv*.py`, `restore_eb.py`, `qa2_convert.py`, `chain_test.py`,
    `calminispiral/`, `qa2_aux/`, `script_py3/` — reduction/calibration
    provenance scripts.
- `files/blindspot_free_observable_note.md` — the γ=k/12 blind spot is not
  fundamental; calibrator-differential statistic R(t).
- `files/observing_requirements_memo.md` — what a real observation needs
  (calibrator program, veto ordering, lottery sampling).
- `files/closure_phase_derivation_note.md` — incl. the 2026-09-24 factor-of-2
  correction (action-consistent dχ_max = 2πγk).
- `files/eht_analysis/` — EHT-side pipeline scripts and JSON results.
- `files/blindspot_work/` — synthetic injection-recovery demos.
- `files/tunneling/` — tunneling-rate derivation scripts + note.

## Headline result (v2, 3 EBs: X4947, X448f, X4227)

No detections. 55.6° tanh slips at τ≈47 s excluded with measured
P(detect)=100/100 per EB (95% lower bound 0.971). General sensitivity
A90: 19–29° (X4947), 6–12° (X448f), 10–12° (X4227). v1's "~6–8° everywhere"
and predicted-S/N ">>99%" claims are superseded — see the audit note.

## Deliberately excluded

- Raw ASDM tars (~13 GB/EB): ALMA archive, project 2016.1.01404.V.
- CASA table cache (`*.dat`, `*.f0`, `*.lock`, …) and reduction logs' binaries.
- Original `.npz` files: converted to CSV above (identical numbers).
- Diagnostic PNGs: described in the reports; regenerable from the CSVs.

## Operations note

Reduction runs under a self-healing schedule (`alma-eb-pipeline-driver`,
≈every 30 min): one EB at a time, fresh download only (resumed tars came
back corrupt), per-EB checkpoints in `REDUCTION_LOG.md`. Each new NPZ gets
searched with v2 on landing; per-EB nulls kept separate.
