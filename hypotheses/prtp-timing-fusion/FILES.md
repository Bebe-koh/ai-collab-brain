# prtp-timing-fusion — files index

**Question:** does covariance-aware pulsar timing fusion (GLS) actually beat
holdover once oracle noise parameters are removed?
**Status (2026-10-06):** simulation arc COMPLETE — X-ray NO-GO stands for
DSAC-class clocks; radio rescue survives all realism tests. Only oracles
left are red-noise PSD shapes. NANOGrav radio pilot designed, pending go.

## Layout — notes (`files/*.md`)

- `csac_trade_study.md` — clock-grade break-even (M*≈860–1000; CSAC SA.65
  wins ~4× at 2 yr on X-ray data; radio wins for all clock classes).
- `chain_binned_note.md` — the chain-vs-binned reconciliation: withdrew the
  "chains underpredict red noise" claim; the real bug was WHITE noise
  (binned formal errors omit jitter/EQUAD/ECORR; true white 31/205/463
  ns/bin). Repair rule: never trust binned formal errors.
- `b1937_wobble_note.md` — 31.5-yr sinusoid vs power law undecidable on
  15.5-yr data; cross-band achromaticity (wcorr≥0.9976) excludes DM/ISM
  origin for the dominant component.
- `nanograv_radio_pilot_note.md` — the designed radio pilot (pending).
- `radio_pilot_robustness_note.md`, `radio_pilot_joint_estimation_note.md` —
  robustness under data gaps and joint white+qf estimation.
- `unified_gls_audit_note.md`, `kf_prior_art_note.md` (adaptive-KF
  over-whitening: partial prior-art overlap — Brown & Rutan state the
  mechanism; the quantified fixed point appears new), `duty_cycle_audit_note.md`,
  `nicer_pilot_note.md`, `nicer_pilot_repair_note.md`, `monopole_ranking_note.md`,
  `wide_array_note.md`, `spatial_template_note.md`, and others.

## Layout — code and results (`files/`)

- `radio_pilot_joint.py`, `radio_pilot_robustness.py`, `wide_array*.py`,
  `wander_investigate.py`, `prtp_verify.py` (+ `*.json` result files) —
  the simulation/verification battery.
- `nicer_pilot/` — NICER pilot scripts and JSON products (event data excluded).

## Deliberately excluded

- `nanograv15yr/NANOGrav15yr_PulsarTiming_v2.0.1.tar.gz` (579 MB) and the
  extracted chain `.txt` files: public NANOGrav 15-yr data release
  (https://data.nanograv.org). Filenames referenced in `chain_binned_note.md`.
- `nicer_pilot/data/` NICER event files: HEASARC archive.
- `venv_pint/` (pint 1.1.7 environment): rebuild with `pip install pint==1.1.7`.
