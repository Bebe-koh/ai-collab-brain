# Inner Hunt v4 — Full Inventory + Sampling Fix
**Date:** 2026-10-14
**Status:** COMPLETE. Null 24× tighter (2,800 → 118 km). No credible detection; v1 0.69 M⊕ candidate stays dead. Marginal candidates are numerically suspect or physically inconsistent (see §5).
**Working dir:** `~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/`
**Related:** `inner_hunt_v3_note.md` (v3 baseline), `belt_inventory_note.md` (inventory), `y_drift_fix_note.md` (cubic-eval fix)

## 1. What changed since v3

The complete inventory per Jase's directive, plus two bug fixes found during this run:

**(a) Full inventory** (already wired per `belt_inventory_note.md` §6, first full run here):
- System GMs for outer planets (Jupiter/Saturn/Uranus/Neptune body+moons)
- System-barycenter vectors for outer planets (SPICE DE440)
- 2-day rails + direct cubic evaluation for Mercury/Venus/Earth/Mars/Moon
- Ceres/Vesta/Pallas as individual perturbers (NB=11, SELF_SKIP for Ceres/Vesta tracers)
- Asteroid ring at 2.8 AU (KB ring fitted mass 0 → skipped)

**(b) EMB grid bug (found & fixed):** `residual_hunt.py` assigned the 2740-row fine-grid `_bary_pos` directly to the 183-epoch Earth tracer → `ValueError` broadcast crash. Fixed by cubic-spline evaluation of the fine-grid barycenter at tracer epochs (verified 0.0 km vs exact coincident rows; linear `np.interp` would inject a 0.033 AU chord error).

**(c) Epoch-sampling artifact (found & fixed — the big one):** `sample_epochs()` used linear `np.interp` to sample the 1.46-day null trajectory at 30-day epochs. For inner-planet orbits this injects a **64.6-day, 7839 km radial chord artifact** (proven by direct FFT: measured residual top periods [64.6, 63.8] d match the predicted [64.6, 63.8] d; cubic gives 0.155 km). Same artifact class as the P_fine y-drift bug. Fixed in three places: `sample_epochs`, `r_null_var` construction, candidate-delta epoch interpolation — all now cubic.

## 2. Before/after null

| Tracer | v3 holdout | v4 holdout | Change |
|--------|-----------|-----------|--------|
| Ceres  | 933.7 km  | 65.9 km   | 14× |
| Earth  | 5002.0 km | 124.1 km  | 40× |
| Mars   | 2204.3 km | 160.2 km  | 14× |
| Vesta  | 937.0 km  | 99.5 km   | 9× |
| **Pooled MSE** | 3.533e-10 | **6.179e-13** | **571×** |
| **Pooled RMS** | ~2,800 km | **~118 km** | **24×** |

The 24× improvement is dominated by the sampling fix (c), not the belt. The belt's own contribution is visible in Ceres (934→663 km in the pre-sampling-fix v4 run) — modest but real. The ~470 km Mars belt signal was absorbed into the general tightening.

## 3. Hunt results

- **Grid:** 990 candidates. Best train 1.139e-13 vs null 1.647e-13 → **1.45×**.
- **Refined (15):** top distinct solutions:
  - m=2.81e-09 M☉ (9.3e-4 M⊕) @ 0.12 AU, ph 5.79: ho 2.04×, dBIC +449.5
  - m=5.25e-09 M☉ (1.75e-3 M⊕) @ 0.42 AU, ph 5.86: ho 1.89×, dBIC +399.6
  - m=4.28e-12 M☉ @ 1.46 AU, ph 1.77: ho 1.83×, dBIC +378.2
  - m=6.54e-03 M☉ (2.18 M⊕) @ 189.7 AU, ph 3.32: ho 1.81×, dBIC +371.3 (×5 duplicates)
- **Exact re-integration** (best candidate, DT_FINE): first-order 3.036e-13 vs exact 5.052e-13 (ratio **1.664**) — the variational theory overestimates. True improvement: 2.04× → **1.23×**.
- **Fine-dt exact check** (DT_FINE/4, top-3 distinct): 0.12 AU → **0.89×** (worse than null!), 0.42 AU → 1.04×, 190 AU → 1.12×. **All candidates' improvements vanish at adequate time resolution — definitive numerical artifacts, not bodies.** (Note: the fine-dt null itself measures 1.477e-12 vs 6.179e-13 at std dt — the null does not converge monotonically with dt, indicating the 118 km floor is dominated by numerical integration noise rather than stable physical residuals.)
- **Tracker:** posterior 1.0 on cand_00 (0.12 AU), 0.0 elsewhere; 0 invention rounds (not surprised). **Caveat:** posteriors use first-order holdout likelihoods, which §4 shows are inflated.
- **ROM:** 16 children consolidated → 2033 bytes, 7 consolidations.
- **v1 "0.69 M⊕ @ 3.2 AU" candidate stays dead.** Nothing in the refined set within orders of magnitude of (2.08e-6 M☉, 3.2 AU).

## 4. Why the marginal candidates are not credible

**The 0.12 AU candidate (2.8e-9 M☉):** 15.2-day orbital period vs DT_VAR = 2.92 days (~5 steps/orbit) — the variational machinery is under-resolved for this fast candidate. Exact integration cuts its improvement 1.66× (2.04× → 1.23×). Numerically suspect.

**The 190 AU candidate (2.18 M⊕):** well-resolved (2618-yr period), 1.71× exact. BUT — decisive physical argument: in the heliocentric formulation the candidate's direct and indirect terms cancel to leading order, leaving only the tidal signal: 2μ_c·r/a_c³ ≈ 7.5e-8 AU/yr² → **~1.3 km over 15 yr**. A 1.3 km physical signal cannot explain 76 km of holdout variance (1.71× of 118 km RMS). The "improvement" must be fitting numerical noise, not a planet. The data are inconsistent with a real 2.18 M⊕ @ 190 AU body. Same conclusion for the 0.42 AU candidate (signal below floor).

**General lesson:** formal dBIC is meaningless when the candidate's physical signal lies far below the null's numerical noise floor. The 118 km floor is dominated by integration truncation error (Richardson: Earth 389 km at dt vs dt/2), not physics.

**Multiple inconsistent solutions** (0.12, 0.42, 1.46, 190 AU) — the "fitting systematics/noise" pattern, not a single body.

## 5. Verdict

**Clean null. No credible detection.** The v1 0.69 M⊕ @ 3.2 AU candidate remains dead. The marginal candidates that appeared at the new 118 km floor are definitively numerical artifacts:
- The 0.12 AU candidate (best first-order: 2.04×, dBIC +449): exact integration at std dt gives 1.23×; at fine dt it goes to **0.89× (worse than null)**. Its 15-day period was under-resolved by the variational grid (DT_VAR = 2.92 d). Dead.
- The 0.42 AU candidate: 1.89× → 1.54× (std exact) → **1.04×** (fine exact). Dead.
- The 190 AU candidate (2.18 M⊕): 1.81× → 1.71× (std exact) → **1.12×** (fine exact). Its physical tidal signal is only ~1.3 km (direct/indirect cancel to leading order in the heliocentric formulation) — far below the floor. Dead.
- The tracker posterior (1.0 on cand_00) inherited the inflated first-order likelihoods and is not independently credible.

**Key lesson:** formal dBIC is meaningless when (a) the candidate's physical signal lies far below the numerical noise floor, or (b) the candidate's timescale is under-resolved by the integration grids. Always validate with exact re-integration at finer dt — a real signal must survive it.

## 6. Explicit non-claims

- No hidden body is claimed. The candidates above are not detections.
- The 24× null improvement is the removal of the pipeline's own sampling artifact, not new physics.
- The 118 km noise floor is an upper bound on unmodeled effects, dominated by numerical integration error.
- A Planet Nine (10 M⊕ @ 400 AU) remains far below detectability here (its 15-yr tidal signal is ~meters at 1 AU).

## Commands (exact)

- Fixes: `residual_hunt.py` (EMB cubic eval; `sample_epochs`/r_null_var/candidate-delta cubic interp)
- Backup: `hunt_results.json` → `hunt_results_v3_exacttime.json`
- Hunt: `cd real_data && nohup python3 residual_hunt.py > residual_hunt_v4.log 2>&1 &` (~46 min; results → `hunt_results.json`)
- Fine-dt check: `exact_check_fine.py` (standalone model replica, DT_FINE and DT_FINE/4)

## Files

- This note: `hidden_files/inner_hunt_v4_note.md`
- `real_data/residual_hunt.py` (fixed), `real_data/exact_check_fine.py` (new)
- `real_data/hunt_results.json` (v4), `real_data/hunt_results_v3_exacttime.json` (v3 backup)
- `real_data/residual_hunt_v4.log`
