# Inner Hunt v3 — Time-Rounding Fix + Re-run
**Date:** 2026-10-13
**Status:** COMPLETE. Clean null. Time artifact confirmed and eliminated.
**Working dir:** `~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/`
**Related:** `stacked_wiggle_note.md` (root-cause proof), `tno_hunt_v2_note.md`, `moon_fix_note.md` (v2 baseline)

## What changed

The stacked-wiggle investigation proved the 84-day TNO signal was a time-labeling
artifact: pull scripts wrote `time_years` with `round(t_yr, 4)`, creating ±26 min
errors beating at 84.4 days → per-epoch position errors of −v·δt. The fix (already
applied in `/tmp/fix_times.py`, backups as `*.bak`, pull scripts now use `repr`):

- `horizons_tracers_full.csv` (inner tracers): t = k·30/365.25 — verified old
  values are 4-decimal roundings of the new grid
- `planet_ephemerides.csv`: same 30-day exact grid (old = roundings, verified)
- `mercury_fine.csv`: t = k·2/365.25 exact (note: its `.bak` had 6-decimal, not
  4-decimal, rounding — a different pull-script precision, covered by the same fix)
- `moon_fine.csv`: t = k·2/365.25 exact (old = roundings, verified)

`residual_hunt.py` loads all four (mercury/moon fine files preferred by the
loader patches). No code changes to the hunt itself.

## Before/after: null

| Quantity | v2 (Moon-fix, rounded times) | v3 (exact times) |
|---|---|---|
| Null train MSE | 6.9496e-09 | **3.4518e-10** (20.1× better) |
| Null holdout MSE | 7.2221e-09 | **3.5332e-10** (20.4× better) |
| Pooled noise floor | ~12,470 km RMS | **~2,800 km RMS** |

## Mechanism confirmation (inner tracers)

Predicted −v·δt from the `.bak` rounding errors vs observed v2→v3 change:

- δt series: max ±26 min, RMS 911 s, dominant period **84.5 days** (same beat)
- Predicted pooled −v·δt RMS: **12,230 km** (Ceres 9,388 / Earth 15,662 / Mars 12,689 / Vesta 10,190)
- Observed removed RMS: sqrt(6.9496e-09 − 3.4518e-10) = **12,157 km**
- **Match to 0.6%.** The time-rounding artifact explains essentially all of the
  v2 null error. It is gone by construction (exact grids verified) and by
  measurement. As predicted, the effect was ~10× larger for inner tracers than
  TNOs (faster-moving), and the null improvement here (20×) exceeds the TNO
  v2→v3 gain (14×).

## v3 hunt results: CLEAN NULL

- **Grid:** 990 candidates. Best train MSE 3.433e-10 vs null 3.452e-10 → **1.01×**.
- **Refined (15, Nelder-Mead):** best holdout 1.0101× (m=5.76e-07 M☉ @ 5.83 AU);
  **all dBIC −12.9 to −20.7 (decisively rejected)**. The recurring solutions
  (~1e-07 M☉ @ 4.5 AU; ~5.8e-07 @ 5.8 AU; ~2e-08 @ 0.2–0.7 AU) are noise fits —
  none exceeds 1.01× holdout.
- **Tracker posteriors:** spread thin, no dominant hypothesis (null 8.2%,
  top candidate 14.9%). The "nothing there" signature.
- **Invention round:** 6 invented variants of the 4.5 AU spot, all with holdout
  MSE 3.512e-10 vs null 3.5332e-10 (1.006×) — correctly rejected by dBIC
  (−15.4); the parameter penalty exceeds the sub-1% gain.
- **The v1 "0.69 M⊕ @ 3.2 AU" candidate stays dead.** Nothing in v3 near
  (2.08e-06, 3.2); the entire grid tops out at 1.01× train. Its v1 appearance
  is fully accounted for (Mercury-spline artifact + time-rounding noise against
  the noisier v1 null).
- **ROM:** 24 children consolidated (all posterior ≈ 0.0) → parent ROM
  1600 bytes, 6 consolidations.

## Non-claims

No astronomical detection is claimed or implied. The v3 inner hunt is a null
result: no hidden body detected via Ceres/Earth/Mars/Vesta residuals at the
~2,800 km noise floor over 2010–2025. The 20× null improvement is the removal
of the pipeline's own time-labeling error, not new physics.

## Commands (exact)

- Fix: `/tmp/fix_times.py` (rewrote time columns; backups `*.bak`); `sed`
  round→repr on pull scripts (done during wiggle investigation)
- Verification: inline checks above (old-is-rounding-of-new; exact-grid;
  −v·δt prediction vs observed)
- Hunt: `cd real_data && nohup python3 residual_hunt.py > residual_hunt_v3.log 2>&1 &`
  (~940 s; results → `hunt_results.json`; v2 backed up as
  `hunt_results_v2_moonfix.json`). One launch was killed by an infra restart
  mid-refinement; relaunched detached, no effect on results.
