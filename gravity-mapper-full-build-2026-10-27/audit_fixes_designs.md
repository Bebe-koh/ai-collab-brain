# Audit-fix designs (Phase 1 — designs + regression tests only)

**Date:** 2026-10-25. **Status:** Phase 1 complete; Phase 2 STAGED, waiting
on the closure-validation re-run (see §0). **No live file was edited in
Phase 1** — only `tracker_solver.py` and `validate_pipeline.py` (both
legacy, neither imported by the validation run) plus NEW files.
**Audit source:** `perplexity_review_audit.md` (§§1–12, §A).

## 0. Sequencing: why Phase 2 waits

The leaner closure-validation re-run is still in flight (note
`rom_loop_closure_note.md` §6 TBD; `sealed_runs/rom_closure_validation_results.json`
absent at Phase 1 time). It imports `rom_closure`, `rom_loop`,
`checker_brain`, `optimizer_brain`, `particle_brain`, `rails_brain`,
`hypothesis_tracker`, `hypothesis_inventor`, `rom_history`,
`secular_elements`. Editing any of those mid-run would corrupt its
results (new processes load changed code). Phase 2 starts ONLY when
both completion artifacts exist:
`sealed_runs/rom_closure_validation_results.json` AND
`rom_loop_closure_note.md` §6 filled in. The regression tests in
`audit_fixes_regression_tests.py` are written to FAIL on current code
and PASS after the Phase 2 fixes; they encode the interfaces specified
below, so Phase 2 must implement these designs, not improvise new ones.

## 1. Fix #1 — Checker holdout isolation + fit_state success filtering

**Problem (audit §§2, 9):** `check_fit` refits on the training split
but starts from the full-data fit state (`x_hint` = full-data r0+v0);
`fit_state` builds ALL starts from the hint, so the "refit" never does
a cold training-only start. In the N-body rung, early-stop at 2σ means
the refit stops at start 0 — it barely moves. Additionally
`train_rms` is the FULL-data fit's RMS, not the training refit's, and
it feeds both the `noise_consistent` gate and the holdout threshold
`max(5σ, 3·train_rms)`. Separately, `fit_state` picks the lowest-cost
start BEFORE checking `sol.success`, so an unconverged run can displace
a converged one, and early stopping is success-blind.

**Design (Phase 2):**
- `check_fit`: NEVER pass `x0_hint` to the training refit. The refit
  uses cold/data-driven starts only (`fit_state(ts_tr, obs_tr, ...)`
  with no hint). The refit must use the SAME `predict_fn` (fixed model,
  no re-selection) — withheld data is predicted exactly once, after the
  refit, and only then does the conductor act on the gates.
- `train_rms` := the training refit's `rms_au` (from the refit dict),
  never `fit['rms_au']`. Both the `noise_consistent` gate
  (`train_rms <= 5σ`) and the holdout threshold
  (`max(5σ, 3·train_rms)`) use this value. The returned dict keeps the
  key name `train_rms_au` (now correctly defined) and the note must say
  the definition changed.
- `fit_state`: filter to successful starts BEFORE best-cost selection
  (a start counts only if `sol.success` AND its predicted state is
  physical via `predict_fn(sol.x) is not None` AND finite residuals).
  Early stopping requires the current best start to be successful AND
  below `early_stop_rms`. If no start succeeds, return `success: False`
  as today.
- Interaction: the conductor's warm-start use of `x0_hint` for the
  N-body FIT itself is unchanged — only the checker's refit loses the
  hint. Warm-starting a fit is legitimate; warm-starting a holdout
  validation is not.

**Pre-registered pass/fail (Phase 2):**
- P1a: with `fit_state` mocked, `check_fit`'s refit call carries
  `x0_hint=None` (regression test T1a).
- P1b: `check_fit`'s returned `train_rms_au` equals the mocked refit's
  RMS, and the `noise_consistent` gate follows the refit value (T1b).
- P1c: `fit_state` with a mocked optimizer returning a low-cost
  unsuccessful start then a higher-cost successful start returns the
  successful state with `success: True` (T1c).
- P1d: `fit_state` with a mocked optimizer whose start 0 is below the
  early-stop RMS but unsuccessful does NOT stop early; it tries
  further starts and returns the successful one (T1d).
- P1e (live regression, Phase 2): the Ammonite rung's sealed-truth
  scoring still passes (it is independent of the checker — verify that
  remains true, don't assume it).

## 2. Fix #2 — Ratio contract unification (MSE domain)

**Problem (audit §3):** `rom_closure.fit_candidate` computes an RMS
ratio (`b_ho / c_ho` from holdout RMS values) but
`HypothesisTracker.add_verdict` documents `holdout_ratio` as an MSE
ratio. RMS ratio = √(MSE ratio). Consequences today: the closure's
1.2 bar is STRICTER than documented (RMS 1.2 ↔ MSE 1.44), and promoted
closure verdicts contribute HALF the intended log-odds.

**Design (Phase 2) — and its known consequence, stated plainly:**
- `fit_candidate` returns BOTH `holdout_rms_ratio` (= b_ho / c_ho) AND
  `holdout_mse_ratio` (= (b_ho / c_ho)², computed only when both
  holdout RMS values are finite and `c_ho > 0`, else NaN). The old
  bare `ratio` key is REMOVED (not kept as an alias — an ambiguous key
  is how this bug happened).
- `verdict_for_candidate` reads `holdout_mse_ratio` and compares it
  against `ACCEPT_RATIO = 1.2` (unchanged numeric value, now in MSE
  units). `close_invented` records `holdout_mse_ratio` in verdicts
  and reports; `run_novel_case`'s promotion check uses the MSE ratio.
- Every threshold's units are documented at its definition site:
  `ACCEPT_RATIO` (MSE), inventor `accept_ratio` (MSE, via
  `last_holdout_ratio` — audit and fix any RMS-fed path), tracker
  `add_verdict` docstring (MSE, already correct — unchanged).
- **CONSEQUENCE (Jase-approved, eyes open): squaring LOOSENS closure
  promotion from MSE 1.44 to MSE 1.2.** Previously decided closure
  cases must be re-read under the new definition (see §6
  reconciliation), and the in-progress validation re-run's promotion
  decisions (made in RMS units) must be re-read before its verdict is
  final. A case that promoted under RMS 1.2 still promotes under MSE
  (its MSE ratio is higher); a case that abstained at RMS 1.1–1.2 may
  promote under MSE 1.21–1.44 — those are the cases reconciliation
  must enumerate, not assume away.

**Pre-registered pass/fail (Phase 2):**
- P2a: `holdout_mse_ratio(1.1, 1.0) == 1.21` (pure helper, T2a).
- P2b: `verdict_for_candidate` with checker PASS and
  `holdout_mse_ratio = 1.21` returns `promoted` (T2b).
- P2c: same with `holdout_mse_ratio = 1.1` returns `abstained` (T2c).
- P2d: no remaining reader of a bare `ratio` key in the closure path
  (grep check in Phase 2).
- P2e (reconciliation): every validation re-run promotion/abstention
  re-read under MSE; any verdict change reported with numbers, and
  affected cases re-run if changed.

## 3. Fix #3 — Evidence ledger / delta-only consolidation

**Problem (audit §4):** `_consolidate_tracker` feeds each hypothesis's
CUMULATIVE `verdict_loglik` into `consolidate()`, which adds it to
`sum_loglike` and increments `n_tried` — every round, with no event
ID, delta, or idempotency check. Replaying the same case inflates
bins (`total_hypotheses` 131 → 231, phantom bin `n_tried` 3 → 8 with
`n_good` stuck at 1). Posteriors are NOT affected (they use
`verdict_loglik`, never bins); what inflates is `learned_prior` and
`promising_regions` — inventor priors.

**Design (Phase 2):**
- `consolidate(parent, children, event_id=None)`: when `event_id` is
  given, the parent keeps a ledger in
  `parent.extra['consolidated_events'][event_id] = {child_name:
  loglik_at_consolidation}` (persisted via the unknown-key path).
  On replay with the same `event_id`, each child contributes only the
  DELTA (`current verdict_loglik − stored`), and `n_tried` does not
  increment again; `n_good` is recomputed from the CURRENT posterior
  (a hypothesis crossing 0.1 on replay updates `n_good` at most once
  per event). A replay with zero deltas is a no-op (idempotent).
- Without `event_id` (legacy callers), behavior is unchanged — but all
  closure/loop call sites MUST pass one: `close_invented` passes a
  stable case id + round (`f"{case_id}:r{rnd}"` is WRONG — rounds of
  the same case are the same evidence; use `case_id` alone, so round
  2 re-consolidation of round 1 verdicts adds only deltas), and
  `run_case` passes its case id. Distinct datasets/cases get distinct
  ids; optimization retries of the same case share one id — that
  distinction is the whole point (retries ≠ independent confirmations).
- `ChildROM` gains `last_consolidated_loglik` (default None) as a
  second, per-object guard; `consolidate` updates it. Either guard
  alone suffices; both are kept so a ledger loss (e.g. hand-edited
  ROM file) still cannot silently double-count through the object.
- Existing inflated bins are NOT rewritten by hand (that would invent
  history). They decay naturally: the ledger prevents further
  inflation, and the note must state the pre-fix bins remain inflated
  and should be read with that caveat until enough fresh, ledgered
  consolidations dominate them. If Jase later wants a rebuild, that is
  a separate decision with its own criteria.

**Pre-registered pass/fail (Phase 2):**
- P3a: consolidating the same child twice under one event id
  increments `n_tried` once (T3a).
- P3b: growing the child's `verdict_loglik` from 2.0 to 3.0 and
  re-consolidating under the same event adds exactly +1.0 to
  `sum_loglike` (T3b).
- P3c: a different event id consolidates fully (independent evidence
  still counts) (T3c).
- P3d: all closure/loop call sites pass an event/case id (grep check).

## 4. Fix #5 — Atomic ROM save

**Problem (audit §10):** `ParentROM.save()` opens the destination
directly with mode `'w'`; an interrupted write corrupts the
persistent record (bins, lessons, hypotheses history). No corruption
observed; this is cheap insurance.

**Design (Phase 2):** write to a temp sibling in the same directory
(`<path>.tmp.<pid>`), `flush()` + `os.fsync()`, validate by
re-reading and `json.load`-ing the temp file, then `os.replace()` to
the destination (atomic on POSIX). On any failure, leave the original
untouched and remove the temp file. `load()` unchanged.

**Pre-registered pass/fail (Phase 2):**
- P5a: `save()` calls `os.replace` (monkeypatched recorder, T5a).
- P5b: no temp files remain after a successful save; saved JSON parses
  and round-trips (T5b).

## 5. Live hygiene (audit §§1, 5, 6, 7, 8, 11, 12)

- **Paths:** `HERE = os.path.dirname(os.path.abspath(__file__))` in
  `rom_closure.py` and `rom_loop.py` (copy `optimizer_brain.py`'s
  pattern); no import-time `os.chdir` anywhere; drop dead paths.
  Test T6a greps live modules for `/home/hatch` and `os.chdir`.
- **Duplicate names:** `HypothesisTracker.add()` raises `ValueError`
  on a duplicate hypothesis name (posteriors are keyed by name, and
  `add_verdict` targets the FIRST match — silent collision is a
  correctness bug, not a style point). All existing call sites use
  counter-suffixed inventor names; verify none relies on duplicates.
  Test T6b.
- **Circular phase, centrally:** `cart_to_elements` must preserve
  circular-orbit phase. Fix: when `e < 1e-12`, set `omega = 0` and
  `M = u`, where `u` is the angle of `r` from the node direction
  measured in the orbital plane (`e1 = n/nn`, or the x-axis if the
  orbit is equatorial; `e2 = ĥ × e1`; `u = atan2(r·e2, r·e1)`). Then
  `elements_to_cart` reproduces the state exactly (for e=0,
  position angle = `Om + M` through the rotation, and `M = u` gives
  the original direction). Regression test T6c round-trips a circular
  state with phase 1.0 rad. ONLY after T6c passes may the
  `ExtraRails.from_bodies` workaround be retired — and retirement is
  optional; the workaround is sound, so if in doubt, keep it and say so.
- **`update_sequential`:** resolve the docstring/body contradiction
  (docstring claims cumulative rescoring; body scores batch-only).
  Phase 2 decision: RENAME to an honest batch-comparison name
  (recommended — no live path uses it) OR implement true accumulation;
  do not leave the contradiction. Test T6d asserts the contradiction
  is gone (source check: not both 'cumulative' in the docstring and
  'batch only' in the body).
- **`n_hypotheses`:** legacy-only (`tracker_solver`, now deprecated) —
  no Phase 2 action beyond the deprecation. Recorded here so it is not
  mistaken for an open live item.
- **Grid scorer row-count:** legacy-only (`score_hypothesis` callers
  are legacy; `rom_loop` never calls it). If Phase 2 touches it at
  all, add the scored-count assertion; otherwise leave it with the
  deprecation. Not a live-path item.

## 6. Phase 2 regression suite (in addition to the tests above)

- ROM calibration suite (`rom_calibration_tests.py`): 13/13 groups
  must still pass.
- Belt live-run sequence replay: verdicts reproduce within stated
  tolerance (phantom killed, perturbers promoted, clean null silent;
  the E-b marginal share miss is expected to reproduce, not vanish —
  unless fix #3's ledger changes bin-driven priors, in which case the
  difference must be explained, not hidden).
- Ammonite rung sealed-truth scoring: still passes (independent of
  the checker — verify, don't assume).
- Closure-validation reconciliation: re-read every re-run promotion /
  abstention under MSE (§2); enumerate any verdict change; re-run
  affected cases if changed.
