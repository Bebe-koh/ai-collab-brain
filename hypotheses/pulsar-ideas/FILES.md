# pulsar-ideas — files index

Small feasibility studies spun off the pulsar program. Each idea is one
directory; `PARKED_FOR_LATER.md` holds the full briefs + resume plans.

## Active

- `files/02-cislunar-xnav/` — cislunar XNAV design study (the narrowed active
  thread). `fresh_run_note.md` has the verdict; `cislunar_xnav_sim.py`,
  `grid_run.py`/`grid_results.csv`, `grid2_run.py`/`grid2_results.csv`,
  `traj_check.py` are the simulation (grid CSVs converted from NPZ).
  **Verdict: PARTIALLY works.** Pulsar fusion navigates (beats unaided coast
  3–100× by antenna) and is indifferent to clock grade (≤15% spread
  DSAC→CSAC), but a realistic 10-m dish gives ~5 km RMS vs the 50 m lunar
  bar (~100× short); antenna area, not clock grade, is the binding
  constraint. Surviving reframe: time-transfer-first (LunaNet common time
  reference) or piggybacking existing large dishes.

## Parked (see PARKED_FOR_LATER.md for resume briefs)

- `files/01-glitch-precursors/` — glitch precursor search
  (`precursor_search.py`, `parse_crab.py`, `crab2.txt`).
- `files/03-cheap-pta-noise/` — cheap PTA noise experiments.
- `files/04-achromaticity-classifier/` — achromaticity classifier
  (`ng15.tar.gz` data excluded; public NANOGrav 15-yr release).
- `files/05-noise-metrology/` — noise metrology Fisher study.

## Awaiting confirmation

- `files/crypto-02-scintillation-key/prior_art_brief.md` — shared-key
  generation from common single-pulse structure + location-dependent
  scintillation. Key finding so far: pulse structure contributes zero
  secrecy; key rate is bounded by scintillation. Jase has not yet confirmed
  this is the "number 2" he meant; feasibility workup proposed, not started.
