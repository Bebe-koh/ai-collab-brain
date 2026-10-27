# Arcade tricks: tried, then integrated early — 2026-10-27
Authorization: Jase, in his own words, 2026-10-27: first "try the other posts about game developers tricks, see which of any work well with the mapper", then "I figure adding these early would be better than later". The white-hole paste was set aside per his "Don't worry about the last paste".
Scope: Atlas workspace copy only. No Drive upload, no Mac merge, no threshold/gate/default change, no live-ROM change. The eccentric search-v4 re-run was not touched and its per-case files were not used here.
Backups before editing (verified identical with cmp): `particle_brain.py.pre_arcade_bak`, `rom_closure.py.pre_arcade_bak`.

## Measurements (scratch, accuracy first)
Timing caveat: the eccentric v4 run was running concurrently, so times are min-of-repeats and are relative, not absolute benchmarks. Accuracy verdicts do not depend on timing.

| Trick | Test | Accuracy result | Speed result | Verdict |
|---|---|---|---|---|
| Tilemaps / rails array call | 500 epochs, scalar loop vs `rails.positions(ts)` | max diff exactly 0.0 AU | 0.096 s scalar vs 0.00075 s array (~127x for that call) | INTEGRATED where it applies (see below). Note: ODE stepping is sequential, so it cannot batch across time; the win is for any call that needs many times at once. |
| Tilemaps / linear-interp lookup on the 0.5-day grid | Same 500 epochs, np.interp per body/component | max diff 9.67e-05 AU | 0.0013 s | NOT integrated. Fails both floors: 1e-7 AU (fitter) and 7.04e-05 AU (ROM). A lookup table is only safe below the floor, and this one is not. |
| Sprite batching / shared rails + indirect once | 20 tracers, `_rhs` loop vs batched accel, t=10 yr | max diff 2.78e-17 AU/yr^2 (machine precision) | 0.0034 s loop vs 0.00019 s batched (~18x) | INTEGRATED. |
| Sprite batching / stacked multi-tracer predict | 3 tracers, 5-yr arc, stacked DOP853 vs per-tracer loop | max diff 6.18e-09 AU | 1.31 s loop vs 0.34 s stacked (~3.9x) | INTEGRATED. Below the 1e-6 AU self-test bar and both noise floors. |
| Lookup sin/cos, nearest (3600-entry table) | 7200 phases, position at 5 AU | error 0.0038 AU | 10x faster than live | NOT integrated. Error is enormous vs both floors. |
| Lookup sin/cos, linear interp (3600-entry table) | Same | error 1.87e-06 AU | 0.00023 s vs 0.00026 s live (no gain) | NOT integrated. Passes the ROM floor but fails the 1e-7 AU fitter floor, and buys nothing in speed. A finer table could pass, but with no speed gain there is no reason to add the risk. |
| Object pooling / buffer reuse | Batched accel, fresh arrays vs reused buffers, 20 tracers | max diff 0.0 | 0.00019 s both (no gain) | NOT integrated. Complexity without a measured gain at this size. |

## What was integrated early
1. `particle_brain.NBodyParticle.accel_batch(r_xyz, t)` — accelerations for K tracers at one time, rails + indirect evaluated once and shared. Same formula as `_rhs`; `_rhs` itself is unchanged.
2. `particle_brain.NBodyParticle.predict_many(states, ts, t_ref)` — K tracers in one DOP853 run (stacked state), same split-at-t_ref logic and tolerances as `predict`. Returns `(len(ts), K, 3)` or None.
3. `rom_closure.PerturbedParticle._rhs_stack` — batched counterpart of `_rhs`, so `predict_many` on a perturbed particle keeps the extra bodies. This override is required, not optional: without it, `predict_many` would silently drop extras.
4. `rom_closure._rails_fingerprint` now evaluates its 3 probe epochs in one array call instead of a scalar loop. Measured identical (array vs scalar diff 0.0), so fingerprint values are unchanged — verified explicitly in the new test.

Already present, so no code change needed (recorded, not re-added): TNO `accel_full` already batches 340 tracers per RK4 stage; the TNO segmented null is already reused across injections; ROM baseline reuse with the provenance guard already exists; segmentation (scroll windows) already exists with its known long-arc cost.

## Tests (all pass, run 2026-10-27)
- New `test_arcade_batching.py`: rails array vs scalar 0.0; accel_batch vs loop 2.78e-17 (< 1e-14); predict_many vs loop 6.18e-09 AU (< 1e-6); perturbed predict_many extras effect 6.19e-05 AU (> 1e-6, so extras are not dropped) and perturbed predict_many vs loop 5.36e-09 AU (< 1e-6); fingerprint probes identical to the scalar loop.
- Existing suites, unchanged results: `rom_closure_selftest.py` ALL PASS; `test_extra_evaluator_selector.py` ALL PASS; `correctness_batch_tests.py` 38 passed, 0 failed; `audit_fixes_regression_tests.py` 20/20 pass.
- Scratch scripts (not live code, kept for the record): `arcade_try_2026-10-27.py` + `arcade_try_results_2026-10-27.json`, `arcade_predict_many_try.py`.

## What was NOT done, and why
- No lookup tables were added: the two tested tables either fail a noise floor or buy no speed (§ Measurements).
- No buffer pooling was added: no measured gain.
- No broad/narrow, LOD, or secular-model change was made: those are the compliance/design items from the earlier audit (`arcade_modern_galaxy_audit_2026-10-27.md`), not tricks that "work" on a try, and they need their own specs.
- No change to any verdict, gate, threshold, default evaluator, or live ROM entry. The new methods are additive: existing `_rhs`, `predict`, and fingerprint values are unchanged, and the new tests prove it for the paths they cover.
- No promotion: this is Atlas workspace code, not project-side shipped code, and not a Drive milestone. Promotion/merge is a separate decision by Jase.
