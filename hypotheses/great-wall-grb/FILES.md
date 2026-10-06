# great-wall-grb — files index

**Question:** is the Hercules–Corona Borealis Great Wall a Gpc-scale matter
overdensity?
**Status (2026-10-03):** KILLED. 116k DESI DR1 quasars in the exact cap/slice
show δ=+1.6%, p=0.22 vs 500 control caps; reconciling with the 50% GRB
excess needs b_GRB>27. Ruled out as a Gpc-scale matter overdensity.

## Layout

- `files/desi_planck_crosscheck_note.md` — **the kill note** (full numbers).
- `files/desi_cap_test.py`, `files/kappa_xcheck.py`, `files/build_kappa.py`,
  `files/redshift_shuffle_test.py`, `files/parse_greiner.py` — analysis code.
- `files/grb_catalog.csv`, `files/grb_catalog_greiner.csv`,
  `files/grb_catalog_grbweb_raw.csv` — GRB catalog compilations.
- `files/crosscheck_products/` — control-cap CSVs and JSON result files.
- `files/Summary_table.txt`, `files/PROVENANCE.md` — catalog provenance.
- `files/crosscheck_scout_note.md`, `files/hcbqw_shuffle_note.md` — supporting.

## Deliberately excluded

- `desi_data/*.fits` (1.2 GB randoms etc.): public DESI DR1
  (https://data.desi.lbl.gov).
- `PR42018like_maps.tar`, `PR4_variations/*.fits`: Planck PR4 products,
  Planck Legacy Archive.
- `venv/`: rebuild from `pip install astropy scipy numpy`.
