# Eccentric validation, search v4 — verdict 2026-10-27
Predeclared bar (harness header, before any run): 20/20 recovered, where recovered means mass rel err <= 10%, a rel err <= 5%, e abs err <= 0.05. Same cases, truths, noise, tracers, span, and train/holdout split as v1; only the search changed (search v4: 4D eccentric screen, 0.25-dex MASS_GRID_FINE, 3+3 joint seeds). Record: `eccentric_fitter_results_v2.json`, per-case `eccentric_case_v2_{00..19}.json`.

## Result: 19/20 — legacy tolerances NOT met, by one case
- Recovered: 19/20. Mean mass rel err 3.47%, mean a rel err 0.06%, mean e abs err 0.0021. The means are dominated by the single failure; the 19 recovered cases are essentially exact (mass <= 0.12%, a <= 0.01%, e <= 0.0006 in every recovered case).
- v1 comparison: 9/20 -> 19/20. The fine-mass grid fix recovered all 10 v1 failures except case 15, plus case 17 (v1's circularized case) now recovers exactly.
- Run history: launched 2026-10-27 ~06:31 PDT, killed by a runtime restart during case 10, resumed ~07:47 PDT from the per-case checkpoints (cases 00-09 all recovered, checkpoints intact), completed ~08:58 PDT, exit 0. Total per-case runtimes ~400-470 s each.
- Holdout diagnostic (not the criterion, parameters are): recovered cases have holdout ratios from ~2,500 to ~730,000 and two-body holdouts at the ~1e-14 noise floor. Case 15's ratio is only 39.6, with two-body holdout 8.04e-11 — about 8,000x above the recovered cases' floor.

## The single failure: case 15
- Truth: secondary (1.719e-06 Msun, a 3.506 AU, e 0.381, phase 2.202 rad), plus Saturn (2.86e-4, 9.58, 4.75).
- Fitted (v2): (5.384e-07, 3.542, 0.420, 4.164). Errors: mass 68.68% (fails the 10% bar), a 1.03% (passes), e 0.0390 (passes). Phase is off by 1.96 rad. Fitted primary is slightly off (9.574 vs 9.58 AU).
- v1 fitted for the same case: (1.565e-07, 2.448, 0.448, 3.073), mass err 90.90%, a err 30.17%, e err 0.0668, holdout ratio 15.55. So v4 improved every parameter and the holdout (ratio 15.55 -> 39.59, two-body holdout 2.05e-10 -> 8.04e-11), but did not reach the basin.
- Decisive test (run after completion, same case-15 data, train only): train MSE at truth = 9.26e-15 (the 1e-14 noise floor); train MSE at the fitted pair = 2.87e-11 (~3,100x worse); at truth Saturn + fitted secondary = 3.16e-11. The truth IS the global minimum by a large margin, so this is a SEARCH failure, not a degeneracy or an identifiability wall — the same pattern as case 16 under searches v1-v3, which v4 then fixed.
- What is special about case 15, as far as the record shows (not a proven cause): it has the highest eccentricity in the set (e = 0.381; next highest is case 7 at 0.371, which recovered), at a mid-low a = 3.506 AU. Its perihelion is 2.17 AU, still outside Mars aphelion, so no tracer crossing explains it.
- What was NOT done: no screen-ranking or NM-from-truth test for case 15 yet. Those are the next diagnostics, following the case-16 playbook, before any new search redesign is proposed. No redesign is proposed in this note.

## Verdict wording (preserved exactly)
Under the predeclared rule, the verdict is: legacy tolerances not met on real dynamics (19/20, not 20/20). That wording does NOT mean the legacy test was wrong — the legacy test fitted a 1D analytic harmonic signal, not N-body orbits, so this test is strictly harder. It also does NOT mean search v4 failed in general: v4 recovered 19/20 essentially exactly, including every case that defeated v1-v3 except one. The remaining work is one case, with a proven search-failure signature, not a new degeneracy claim.
