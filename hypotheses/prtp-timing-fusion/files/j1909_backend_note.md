# J1909-3744 8-year excursion vs backend flags — tech note
2026-09-24. Archival-data analysis; not a detection claim.

## Question
Is J1909's ~8.8-yr, ~330–420 ns quasi-periodic excursion intrinsic
(astrophysical timing noise) or instrumental (backend/receiver artifact)?

## Data
- `nanograv_binned.npz` → binned_J1909: 154 thirty-day bins, MJD 53282–58952 (15.52 yr)
- `J1909-3744_PINT_20220303.nb.tim`: 35,037 TOAs with per-TOA `-be` (backend)
  and `-f` (frontend) flags
- Published NANOGrav 15-yr PINT par solution (PINT 0.8.4 stack in `venv_pint`);
  post-fit residuals computed from the par WITHOUT refitting (includes DMX,
  so interstellar dispersion variations are already removed)

## Backend eras from flags (TOA MJD ranges)
| backend | n TOAs | MJD range |
|---|---|---|
| GASP  | 1,674  | 53292–55390 |
| GUPPI | 29,838 | 55275–58943 |
| YUPPI | 3,525  | 57164–58951 |
GUPPI and YUPPI overlap heavily in time (parallel backends, not sequential).

## Test 1 — direct residual-to-flag cross-correlation
Per-bin backend fractions from the tim file; models fit to binned residuals:
- M0 null: r = const
- M1 wave: r = const + A·sin(2πt/P + φ), P free
- M2 backends: r = const + Σ frac_b·off_b (backend level jumps)
- M3 wave + backends

| model | ΔlnL vs null | params |
|---|---|---|
| M1 wave | +10,766 | A=333 ns, P=8.82 yr |
| M2 backends only | +849 | offs +105/+160/−265 ns |
| M3 wave+backends | +11,088 | A=330 ns (unchanged); wave adds +10,239 over backends-only |

Backend level offsets are real but small (~±100–150 ns once the wave is
included: +12/+132/−144; M3 beats M1 by ΔlnL=321, 2 params) — a correction,
not an explanation. The wave survives backend offsets essentially untouched.

Wave extrema (MJD): max 53540 (deep in GASP era), min 55151 (~4 months BEFORE
the GASP→GUPPI handover 55275–55390), max 56763 (mid-GUPPI, no transition
near), min 58375 (late). No extremum sits at a backend transition; a step at a
transition would put an extremum AT the step, not months away, and could not
produce the mid-era maximum.

## Test 2 — GUPPI-era-only fit
120 bins, MJD 55275–58943 (9.94 yr > one 8.8-yr period), all within one backend:
A=421 ns, P=8.84 yr, ΔlnL=+13,310 vs null. The wave is *stronger* with GASP
excluded. It is not a transition artifact and not a GASP/YUPPI artifact.
Combined with Test 1's GASP-era maximum (53540), the same quasi-sinusoid spans
both GASP and GUPPI continuously — ruling out a GUPPI-internal clock drift
(which could not produce the GASP-era half).

## Test 3 — achromaticity (the decisive split)
Post-fit PINT residuals split by frontend, 60-day bins, 8.84-yr wave per band:

| band | TOAs | A (ns) | phase φ (rad) | ΔlnL wave |
|---|---|---|---|---|
| 800 MHz (Rcvr_800) | 10,265 | 328 | 1.16 | +296 |
| 1.4 GHz (Rcvr1_2) | 21,247 | 383 | 1.27 | +841 |
| 3 GHz (YUPPI) | 3,525 | 452 | 2.53 | +31 (11 bins only) |

800 MHz and 1.4 GHz agree in phase to 0.11 rad (~6°, ~2 months at this period)
and in amplitude to ~15%. The excursion is achromatic → not receiver-specific,
and not interstellar DM (residuals are post-DMX). 3 GHz spans only 5.2 yr
(< 1 period, 11 bins) so its phase is weakly constrained, but its amplitude is
in the same ballpark — consistent, not contradictory.

## Verdict
The instrument is not talking. J1909's ~8.8-yr, ~330–420 ns excursion is
intrinsic to the pulsar — astrophysical timing noise (spin/magnetospheric),
achromatic across 800 MHz–1.4 GHz, continuous across the GASP→GUPPI backend
change, with no jump at any backend transition. Small backend level offsets
(~±150 ns) exist but are a minor correction on top of the wave, not its cause.

## Caveats (kept honest)
- <2 full cycles observed (15.5-yr span, 8.8-yr period): "quasi-periodic" vs a
  red-noise excursion is a modeling choice; a longer baseline sharpens this.
- A hypothetical clock drift common to GASP *and* GUPPI identically would also
  be achromatic and continuous — but the 2026-09-24 clock-file cross-check
  found observatory clock events do not match residual movements, and the
  wide-array analysis found no array-common signal, so that alternative is
  already disfavored on independent grounds.
- This kills the instrumental explanation of the excursion; it does NOT revive
  the common monopole — that was falsified separately (J1909's private excess
  seen through ~93% estimator weight).

## Files
- `j1909_backend_check.py`, `j1909_backend_check.json` (Tests 1–2)
- `j1909_achromaticity.py`, `j1909_achromaticity.json` (Test 3)
