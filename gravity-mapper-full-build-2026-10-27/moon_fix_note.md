# Moon Sampling Fix — Investigation Note
**Date:** 2026-10-13
**Status:** COMPLETE. Suspected bug investigated and closed: measured effect exactly 0.0 AU. Loader hardened as a safeguard.
**Working dir:** `~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/`
**Related:** `tno_hunt_v2_note.md` (Mercury fix), `full_data_hunt_note.md` (v1 hunt), `../attribution_labels.json` (`moon_sampling_check`)

## The suspected bug

During the TNO v2 investigation a bonus suspect was flagged: `moon_ephemeris_vel.csv`
samples the Moon's position every 30 days, but the Moon orbits Earth every 27.3 days —
the same corner-cutting spline class as the Mercury bug (fixed via `mercury_fine.csv`
at 2-day cadence). The Moon data feeds the Earth–Moon barycenter (EMB) construction in
`tno_hunt.py` and `residual_hunt.py` (`planets['Earth']` := EMB, combined mass).
Estimated effect on the inner hunt: ~3e-5 AU.

## Investigation: not actually a bug

Traced every use of the Moon data in both hunt scripts:

- `residual_hunt.py`: `_moon_pos` / `_moon_vel` are used **only** to build
  `_bary_pos` / `_bary_vel` on the planet epoch grid, from exact Horizons samples
  at those epochs. The lunar orbit itself is never splined or interpolated
  between samples. What gets splined downstream is the EMB trajectory — smooth,
  driven only by the Sun and planets — which is exactly what cubic splines handle well.
- `tno_hunt.py`: same, positions only.
- Mercury differed structurally: its 30-day positions **were** splined (for the
  indirect term), corner-cutting the 88-day e=0.206 orbit → −7.5% mean-radius bias →
  fake 1.07e-5 AU/yr² acceleration. There is no analogue here — no code path
  interpolates the Moon between its samples.

## Measurement (before/after)

- Re-pulled the Moon at 2-day cadence → `real_data/moon_fine.csv`
  (2740 rows, Horizons `COMMAND='301'`, `CENTER='500@10'`, AU-D vectors —
  same convention as the original pull; `pull_moon.py '2d' moon_fine.csv`).
  Originals (`moon_ephemeris.csv`, `moon_ephemeris_daily.csv`,
  `moon_ephemeris_vel.csv`) untouched.
- Interpolated the 2-day Moon pos+vel onto the 30-day planet epoch grid and
  rebuilt the EMB both ways:

| Quantity | old (30 d) vs new (2 d) |
|---|---|
| max \|Δ EMB position\| | **0.0 AU** (bit-identical) |
| max \|Δ EMB velocity\| | **0.0 AU/yr** (bit-identical) |

- Why exactly zero: 30 = 15 × 2, so the 2-day grid contains every 30-day node
  (both round to 4 decimals: 15×round(2/365.25,4) = round(30/365.25,4) = 0.0821, …);
  `np.interp` returns the exact sample at coincident nodes. The "correction" is
  provably a no-op for this pipeline — well below the inner null RMS (~1e-4 AU),
  in fact identically zero.

## Fix applied anyway (safeguard)

- `residual_hunt.py`: new `_load_moon_on_grid(t_grid)` prefers `moon_fine.csv`,
  interpolates pos+vel onto the planet epoch grid (same pattern as the Mercury fix).
  The stale `assert moon/planet epoch grids differ` is gone (grids now legitimately differ).
- `tno_hunt.py`: same for positions (`_load_moon_pos_on_grid`).
- Measured effect of the loader change: none (EMB bit-identical). It exists so the
  loader stays correct if the Moon is ever used at sub-orbital cadence in the future.

## Incidental find: stale uniform-grid assert in residual_hunt.py

The v1 inner hunt ran **before** `mercury_fine.csv` existed, when all 8 planets shared
one 183-row grid. Its `assert all(planets[n]['t'] == t_epochs)` went stale the moment
Mercury moved to a 2740-row grid — the first re-run crashed on it
(`ValueError: broadcast (2740,) vs (183,)`). Relaxed to a span-coverage check
(each planet grid must cover the analysis epochs); splines are built per-planet on
their own grids, so the fine Mercury grid is handled correctly (and is the point
of the Mercury fix).

## Inner hunt re-run (Mercury fine grid + Moon loader)

This re-run is therefore the first inner hunt **with the Mercury spline fix active**
(the Moon change contributes 0.0). Null residuals:

| Quantity | v1 (30-day Mercury) | re-run (2-day Mercury) |
|---|---|---|
| NULL pooled MSE, train | 1.939e-08 | 6.950e-09 |
| NULL pooled MSE, holdout | 7.334e-08 | 7.222e-09 |
| Ceres RMS (train/holdout) | 2.07e-4 / 3.90e-4 AU | 6.25e-5 / 6.41e-5 AU |
| Earth RMS (train/holdout) | 1.11e-4 / 1.16e-4 AU | 1.09e-4 / 1.11e-4 AU |
| Mars RMS (train/holdout) | 9.07e-5 / 1.05e-4 AU | 8.53e-5 / 8.78e-5 AU |
| Vesta RMS (train/holdout) | 1.19e-4 / 3.42e-4 AU | 6.82e-5 / 6.89e-5 AU |

~2.8× tighter train null, ~10× tighter holdout null — entirely the Mercury
artifact's removal (the 1.07e-5 AU/yr² fake acceleration was inflating the v1
inner null too). Moon contribution: 0.0.

## Re-verdict: CLEAN NULL (stronger than v1)

- **Grid:** 990 candidates (1e-10–1e-4 M☉, 0.3–80 AU, 6 phases). Best train MSE
  6.946e-09 vs null 6.950e-09 → **1.00× null**. No candidate improves on the
  null at all — not even at grid resolution.
- **Refined (top 15, Nelder-Mead):** holdout improvements all **1.00×**;
  **all dBIC negative** (−18.5 to −21, decisively rejected). Masses 4e-11–3e-7 M☉,
  scattered radii — noise fits, not coherent bodies.
- **Tracker:** null posterior **62.8%**, remainder scattered (≤6.9% each, incl.
  the inventor's wild 1.1e6 M☉/103371 AU noise-chase at 0.7%).
- **The v1 "0.69 M⊕ @ 3.2 AU" candidate is GONE.** It does not reproduce against
  the cleaner null. It was an artifact-assisted fit: the v1 fitter was grabbing
  the Mercury-spline artifact *plus* unmodeled belt mass jointly (4.03×, dBIC +901
  against the noisier v1 null). With the artifact removed, the belt-mass signal
  alone cannot beat the null in this grid — the `inner_epicycle` attribution
  label stands as the explanation of what v1 was fitting, updated with this
  follow-up.
- **Sanity:** m=1e-12 test reproduces null exactly (ratio 1.0000); best-candidate
  first-order vs exact re-integration ratio 1.000.
- **Verdict: NULL STANDS — clean.** No hidden-body signal in 4 inner tracers
  over 15 yr at the ~1e-4 AU noise floor. No detection claimed.

## ROM + attribution labels

- `../attribution_labels.json` += `moon_sampling_check`: labeled **NOT a bug**
  (measured 0.0 AU), with root-cause analysis and the safeguard resolution.
- `real_data/parent_rom.json`: consolidated 1 `pipeline_lesson` child →
  20 hypotheses, 4 consolidations, 654 bytes (flat storage preserved).

## Non-claims

No astronomical detection is claimed or implied. The Moon sampling change is
verified to alter nothing (bit-identical EMB); the inner-hunt null improvement
in the re-run comes from the previously-fixed Mercury spline artifact, not from
the Moon. Any candidate verdict from the re-run is subject to the same
coherence discipline as v1 (per-tracer improvement required; dBIC on holdout).

## Commands (exact)

- Moon pull: `cd real_data && python3 pull_moon.py '2d' moon_fine.csv` (2740 records, ~3 s)
- Loader patch: `_load_moon_on_grid` / `_load_moon_pos_on_grid` in `residual_hunt.py` + `tno_hunt.py`; assert relaxed to span coverage
- EMB equivalence check: inline script (old loader vs new loader) → max |Δ| = 0.0 AU / 0.0 AU/yr
- Hunt: `cd real_data && nohup python3 residual_hunt.py > residual_hunt_moonfix.log 2>&1 &` (v1 artifacts backed up to `hunt_results_v1_moon30d.json`, `residual_hunt_v1_moon30d.log`)
- ROM: `rom_history.py` `consolidate()` of `moon_sampling_check` pipeline-lesson child → `real_data/parent_rom.json`
