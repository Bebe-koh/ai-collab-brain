# Audit fixes — application of the Perplexity review audit, in ranked order

**Date:** 2026-10-25 (Phase 1). **Status:** PHASE 1 COMPLETE; PHASE 2
STAGED, waiting on the closure-validation re-run (see §0).
**Audit source:** `perplexity_review_audit.md`.
**Designs:** `audit_fixes_designs.md`.
**Regression tests:** `audit_fixes_regression_tests.py`.
**Fix #4 (snapshot packaging) was ALREADY DONE** (real_data/*.py
delta-uploaded to the Drive folder 2026-10-25) and is skipped here.

## 0. Sequencing (binding constraint)

The leaner closure-validation re-run was still in flight at Phase 1
time (`rom_loop_closure_note.md` §6 TBD;
`sealed_runs/rom_closure_validation_results.json` absent; checkpoint
file `sealed_runs/rom_closure_validation_results.jsonl` present with
stage results). It imports `rom_closure`, `rom_loop`, `checker_brain`,
`optimizer_brain`, `particle_brain`, `rails_brain`,
`hypothesis_tracker`, `hypothesis_inventor`, `rom_history`,
`secular_elements`. Phase 1 therefore edited ONLY files the validation
run does not import, plus NEW files. Phase 2 starts ONLY when both
completion artifacts exist:
`sealed_runs/rom_closure_validation_results.json` AND
`rom_loop_closure_note.md` §6 filled in. No live file was touched in
Phase 1; the regression tests below prove it (they fail on current
code exactly as designed).

## 1. Phase 1a — Legacy phase decision (fix #6) + validate_pipeline hygiene

**Decision: DEPRECATE `tracker_solver.py`, do not repair it.**
Justification (cost/benefit):
- The live path never uses it (confirmed: zero importers outside
  itself; its only historical callers were legacy drivers). Repairing
  a rescoring path nothing calls would spend validation effort on a
  dead path and risk implying it is supported.
- It depends on `source_upload/` modules excluded from the Drive
  snapshot, so it cannot run from the snapshot anyway; a repair that
  cannot be exercised from the distributed build is not a repair.
- The defect is preserved in the record: the file stays on disk with
  a deprecation header stating the phase-loss reason, the
  supersession (five-brain conductor + `rom_loop` verdicts), and
  exclusion from future snapshots. Importing it now emits a
  `DeprecationWarning`; the solver logic itself is untouched.
- Additionally, its import-time `os.chdir` side effect was removed
  (replaced with `dirname(__file__)`-based `sys.path` entries, same
  importability, no CWD change). Verified: module compiles, imports
  with exactly one DeprecationWarning, CWD unchanged after import.
- The other audit items on this file (`n_hypotheses` ignored for
  `TOP_K`, phase in dedup key) die with the deprecation — recorded
  here so they are not mistaken for open live items.

**`validate_pipeline.py` (legacy J4 V1–V3 suite):** import-time
`os.chdir` + hardcoded `/home/hatch/...` paths replaced with
`dirname(__file__)`-based paths; the dead `.jarvis` path dropped.
Behavior note: `main()` previously wrote `validation_results.json`
into `source_upload/` as a side effect of the import-time chdir; it
now writes to the caller's working directory (standard behavior —
callers must run from their intended directory). Module compiles;
no hardcoded paths or `os.chdir` remain in either file (grep-verified).
This file is also marked legacy (superseded by the Ammonite rung +
five-brain fitter) but NOT deprecated with a warning, since legacy
drivers (`v2_redo.py`, `test_j4_v2r.py`, `diag_from_truth.py`) still
import `simulate_bodies` from it — a warning would spam record-only
runs. If those drivers are retired, this file follows.

## 2. Phase 1b — Designs + regression tests (new files, no live edits)

`audit_fixes_designs.md` specifies, each with pre-registered pass/fail:
- Fix #1: checker refit with cold/data-driven starts (never the
  full-data hint); `train_rms` from the training refit; withheld data
  predicted once after the refit; `fit_state` filters to successful
  starts before best-cost selection and requires success before early
  stopping. Conductor warm-starting of the FIT itself is unchanged.
- Fix #2: `fit_candidate` returns `holdout_mse_ratio` (and
  `holdout_rms_ratio`); the bare `ratio` key is removed;
  `verdict_for_candidate` compares the MSE ratio against 1.2.
  STATED CONSEQUENCE: squaring LOOSENS closure promotion (MSE 1.44 →
  1.2); previously decided closure cases and the in-progress
  validation's RMS-unit promotion decisions must be re-read under
  MSE before any verdict is final.
- Fix #3: `consolidate(parent, children, event_id=...)` with a
  persisted per-event ledger (`parent.extra['consolidated_events']`)
  plus per-child `last_consolidated_loglik`; replay adds only
  deltas; `n_tried` increments once per event. Call sites must pass
  a stable case id (rounds of one case share one id — retries ≠
  independent confirmations). Pre-fix inflated bins are NOT
  hand-rewritten (that would invent history); the ledger stops
  further inflation, and the note must carry the caveat until fresh
  ledgered consolidations dominate.
- Fix #5: atomic ROM save (temp sibling + fsync + validate +
  `os.replace`; original untouched on failure).
- Hygiene: `dirname(__file__)` paths in live modules; duplicate-name
  rejection in `tracker.add()`; central `cart_to_elements` circular
  fix (`M = u`, angle from node in the orbital plane, `omega = 0`)
  with round-trip test — `ExtraRails` workaround retired ONLY after
  that test passes, otherwise kept (it is sound);
  `update_sequential` contradiction resolved by rename (recommended)
  or true accumulation.

`audit_fixes_regression_tests.py` results on current code (2026-10-25,
exit code 1 — expected): **1/16 pass.** The 15 failures are the
designed pre-fix failures, each with the documented failure mode:
T1a (refit received full-data hint), T1b (train_rms 0.001 = full-data
value), T1c (unconverged cheap start won), T1d (early stop after 1
start), T2a (no `holdout_mse_ratio` helper), T2b/T2c (KeyError
`'ratio'`), T3a–T3c (TypeError: no `event_id` parameter),
T5a (no `os.replace` call), T6a (hardcoded paths present),
T6b (duplicate silently accepted), T6c (round-trip moved state
0.959 AU), T6d (doc/body contradiction present). The single pass,
T5b (no temp files left behind + round-trip), passes trivially
pre-fix because the current direct write leaves no temp files; its
real value is post-fix (guards the atomic path's cleanup).

## 3. Phase 2 — STAGED, not started (what it waits on exactly)

Phase 2 applies fixes #1, #2, #3, #5 + live hygiene to the live
files, runs the regression suite (all 16 must pass), the ROM
calibration suite (13/13 must still pass), the belt live-run replay
(verdicts reproduce within tolerance), the Ammonite sealed-truth
scoring (must still pass), and the validation reconciliation
(re-read every re-run promotion/abstention under MSE; enumerate any
verdict change; re-run affected cases if changed). It then
delta-syncs only changed files into the full-build Drive folder and
backs up milestones (batched, one exec call each).

**Phase 2 start condition (both must exist):**
1. `sealed_runs/rom_closure_validation_results.json`, AND
2. `rom_loop_closure_note.md` §6 (verdict) filled in.
Until then, Phase 2 is staged: designs + tests are written and
waiting, and no live file has been touched.

## 4. What remains unvalidated

- All Phase 2 fixes (by design — designs and failing tests only).
- The validation reconciliation outcome (depends on Phase 2).
- Whether the in-progress validation's RMS-unit decisions change
  under MSE (enumerated in Phase 2, not assumed here).
- The pre-fix inflated ROM bins (caveat carried until ledgered
  consolidations dominate; no hand-rewrite).

## 5. Phase 2 — APPLIED 2026-10-26 (fixes #1, #2, #3, #5 + live hygiene)

**Dispatch:** Jase-approved, after closure-validation closeout
(`rom_loop_closure_note.md` §6 filled, verdict STILL CONDITIONAL;
`sealed_runs/rom_closure_validation_results.jsonl`, 64 fits).
Start-condition note: Phase 1 §0 named
`sealed_runs/rom_closure_validation_results.json`; the validation
agent delivered the `.jsonl` checkpoint log (64 records) plus §6 plus
a 10-file Drive milestone backup. Substance satisfied; proceeding per
Jase's dispatch. No `.json` was fabricated to satisfy the letter.

**Safety record:**
- Live ROM backed up BEFORE any persistence-code touch:
  `real_data/parent_rom.json.pre_phase2_20261026`. After all changes,
  the live ROM is byte-identical to that backup (md5-verified):
  27 consolidations, 10 deferred belt entries, phantom lesson intact,
  0 ledger entries (no ledgered consolidation has run against the
  live ROM yet — verification replays ran against temp copies).
  No hand-edit of ROM state anywhere.
- Originals of every edited file preserved in `pre_phase2_backup/`
  (`*.pre_phase2`), so each fix reverts individually.
- Pre-fix inflated ROM bins/priors were NOT hand-rewritten (that
  would invent history). The ledger stops further inflation; fresh
  ledgered consolidations must dominate before bins are trusted hard.
  This caveat carries forward unchanged.
- NOT modified: `sealed_runs/rom_closure_validation_results.jsonl`,
  `rom_loop_closure_note.md`, `rom_closure_lean.py`, or any validation
  artifact. Sealed files temporarily overwritten by verification runs
  (belt replay, Ammonite rerun) were restored and md5-verified
  byte-identical afterward (see §5.6).
- NOT touched (out of scope, separate follow-ons): joint interface,
  deferred-mass/unknown-bucket fix, novel-case redesign, refit-cost
  fix. No scope expansion.

### 5.1 Fix #1 — Checker holdout isolation + fit_state success filtering: LANDED

- `checker_brain.py`: training refit no longer receives `x0_hint`
  (cold/data-driven starts only); `train_rms` is now the training
  refit's `rms_au`, never the full-data fit's RMS; when no refit is
  attempted, `train_rms_au` is inf (undefined) and the verdict follows
  the holdout-unavailable ABSTAIN path. Module docstring records the
  definition change. The conductor's escalation rule is untouched —
  it reads the fit's own `rms_au`, not the checker's `train_rms_au`.
- `optimizer_brain.py`: starts with `sol.success == False` are
  filtered BEFORE best-cost selection; early stopping additionally
  requires the current best start to be successful. Docstring updated.
- Tests: T1a, T1b, T1c, T1d all PASS.
- Measured cost of the fix: Ammonite variant-B wall time rose from
  ~104 s/seed to ~153–163 s/seed (cold-start refits replace the
  warm-hint start-0 early stop). Fitted values unchanged (see §5.5).

### 5.2 Fix #2 — Ratio contract unification (MSE domain): LANDED

- `rom_closure.py`: new helpers `holdout_rms_ratio(b_ho, c_ho)` and
  `holdout_mse_ratio(b_ho, c_ho)` (MSE = RMS², NaN unless both
  holdout RMS values are finite and candidate holdout > 0).
  `fit_candidate` returns BOTH keys; the bare `ratio` key is REMOVED.
  `verdict_for_candidate` reads `holdout_mse_ratio` and compares
  against `ACCEPT_RATIO = 1.2` (numeric value unchanged, units now
  MSE, documented at the definition site). `close_invented` verdicts
  carry `holdout_mse_ratio`; reports carry both ratios.
  `run_novel_case`'s promotion check uses the MSE ratio.
- `hypothesis_tracker.py`: `update_from_verdicts` prefers
  `holdout_mse_ratio`, falling back to legacy `holdout_ratio`
  (add_verdict's documented MSE contract is unchanged). This keeps
  the lean driver, replays, and loop callers working: they feed
  MSE-domain values already or stated MSE assumptions.
- FLAG (stated, Jase-approved, eyes open): this LOOSENS closure
  promotion from MSE 1.44 to MSE 1.2. Reconciliation (§5.6) shows no
  validation verdict changes under the new definition.
- Tests: T2a, T2b, T2c all PASS. P2d grep: no remaining reader of
  fit_candidate's bare `ratio` key in live code. The one remaining
  `['ratio']` read is `rom_loop.py:133` `sim['ratio']` — the replay
  case's SIMULATED promotion dict schema (a labeled MSE-domain
  assumption), not the closure fit key; untouched by design.
- Staleness note (frozen artifact, NOT modified):
  `rom_closure_selftest.py:63` constructs a verdict dict with the old
  bare `ratio` key; it tested the pre-Phase-2 interface and is now
  stale. Do not run it against post-Phase-2 code expecting a pass;
  its mapping-table cases are superseded by T2b/T2c. The lean driver
  (`rom_closure_lean.py`) stays compatible: it threads
  verdict_for_candidate's return values, never the removed key — but
  its old checkpoint file mixes RMS-era records, so do NOT re-run it
  against post-Phase-2 code with the old checkpoint present without
  clearing it (checkpoint reuse keys do not record the ratio
  definition).

### 5.3 Fix #3 — Evidence ledger / delta-only consolidation: LANDED

- `rom_history.py`: `consolidate(parent, children, event_id=None)`.
  With an event id, the parent keeps a persisted ledger in
  `parent.extra['consolidated_events'][event_id]` =
  `{child_name: {'loglik', 'good'}}` (JSON-safe; survives save/load
  via the unknown-key path). Replays add only deltas to
  `sum_loglike`, never re-increment `n_tried`, credit `n_good` at
  most once per event; zero-delta replays are idempotent no-ops and
  are not counted. A different event id consolidates fully.
  Without an event id, behavior is unchanged (legacy callers).
  `ChildROM` gains `last_consolidated_loglik` /
  `last_consolidated_event` as a second guard: if the ledger entry
  is lost, a same-event replay stays delta-only from the object's
  stored loglik, and `n_good` is conservatively never re-credited
  by the backstop.
- Call sites (P3d grep-verified): `rom_loop.run_case` passes
  `event_id=case['id']`; `rom_closure.close_invented` passes its
  `case_id` (one id per case, NOT per round — round 2
  re-consolidation adds only deltas); `run_novel_case`'s final
  consolidation uses `'novel-case'`, the same id as its inner
  close_invented calls, so it adds only deltas.
- Tests: T3a, T3b, T3c all PASS.

### 5.4 Fix #5 — Atomic ROM save: LANDED

- `rom_history.py`: `ParentROM.save()` writes to
  `<path>.tmp.<pid>`, flush + fsync, validates by re-reading and
  json.load-ing the temp file, preserves the destination's
  permission bits (best-effort), then `os.replace()` to the
  destination. On any failure the original is untouched and the temp
  file is removed. `load()` unchanged.
- Tests: T5a, T5b both PASS.

### 5.5 Live hygiene: LANDED

- Paths: `rom_closure.py` and `rom_loop.py` now use
  `HERE = os.path.dirname(os.path.abspath(__file__))`; no hardcoded
  `/home/hatch` paths, no `os.chdir` in either file (T6a).
  (Data-pull scripts under `real_data/pull_*.py` still chdir at
  runtime inside their mains; they are not live modules and are
  outside T6a's scope — left untouched.)
- Duplicate names: `HypothesisTracker.add()` raises `ValueError` on
  a duplicate name (T6b). Verified safe for live callers: replays
  propose each name once per tracker; the inventor uses
  counter-suffixed names within one inventor lifetime; calibration
  tests use a fresh tracker per test.
- Circular phase, centrally: `cart_to_elements` now sets `M = u`
  (angle of r from the node direction in the orbital plane;
  e1 = n/nn or x-axis if equatorial; e2 = h-hat x e1) when
  e < 1e-12, with omega already 0. T6c passes (equatorial round-trip
  exact); additionally verified by hand: inclined circular
  round-trips at machine precision (dr ~1e-16, M recovered exactly).
  The `ExtraRails.from_bodies` direct-computation workaround is
  RETAINED deliberately (sound, validated path; retirement optional
  per design) with a docstring note recording that the central fix
  has landed and the workaround is now redundant belt-and-braces.
- `update_sequential` contradiction: RENAMED to `update_batches`
  with an honest batch-only docstring (no live caller used it;
  grep-verified). No alias kept — the misleading name is gone (T6d).

### 5.6 Verification results (all acceptance items)

- **Regression suite: 16/16 PASS** (pre-fix baseline 1/16, T5b only).
  Exit code 0. No test was adjusted to make it pass.
- **ROM calibration suite: 13/13 groups PASS**
  (`rom_calibration_tests.py`, "ALL 13 CALIBRATION TEST GROUPS
  PASSED"). Calibration tests do not call consolidate/save, so
  fixes #3/#5 cannot affect them except via imports — confirmed
  clean.
- **Belt live-run replay: VERDICTS REPRODUCE EXACTLY.** Run twice,
  both against temp ROM copies (live ROM untouched):
  (a) against a copy of the CURRENT live ROM: L1 flagged, L2
  phantom killed_by_inventory, L3 ceres/vesta/pallas all promoted,
  L4 clean null silent (surprised=False, invented=[]), persistence
  identical — but posterior shares differed numerically (e.g. L4
  null 0.4247 vs sealed 0.3866; ceres 0.1819 vs 0.1656).
  (b) against a copy of the PRE-BELT ROM
  (`parent_rom.json.pre_live_belt_20261025`): max posterior abs
  difference vs sealed = 0.0 — verdicts, invented lists, prior
  shares, and the E-b marginal share pattern (prior 0.164732 ->
  post 0.163408) reproduce EXACTLY. Conclusion: the (a) differences
  are entirely baseline-bin effects (invented priors are
  bin-driven; current bins reflect belt+closure+novel history,
  pre-belt bins do not) — NOT an effect of fix #3's ledger (replay
  stages are new events, so they consolidate fully, as pre-fix)
  or any other fix. Verification outputs saved as
  `phase2_belt_replay_results.json` (current-ROM run) and
  `phase2_belt_replay_prebelt_results.json` (pre-belt run); the
  sealed `rom_live_belt_results.json` was restored byte-identical.
- **Ammonite sealed-truth scoring: PASS 3/3 BOTH VARIANTS.**
  Post-fix rerun (`nbody_fitter_rerun.py`, 490 s total): variant A
  q errors <= 0.0001%, a errors 0.0010–0.0030%; variant B q errors
  <= 0.0001%, a errors 0.0010–0.0030%; all seeds, criterion
  |dq|/q < 1% AND |da|/a < 1%. Fitted values are IDENTICAL to
  pre-fix to 6 decimals (q_fit, a_fit, dq, da, rms all match) —
  the checker fix changed no fitted value, as designed (sealed-truth
  scoring is independent of the checker). Checker verdicts remain
  PASS. Full post-fix numbers saved as
  `phase2_ammonite_results.json`; the sealed
  `nbody_fitter_rerun_results.json` was restored byte-identical.
- **MSE reconciliation (from the JSONL directly, not summaries):
  NO VERDICT CHANGES.** All 64 records read; every record's RMS
  ratio recomputes from its baseline/candidate holdout RMS values
  within 1e-6 (confirming the JSONL `ratio` is the RMS ratio).
  Max RMS ratios: belt 1.0053, amm 1.0171, novel 1.0380 — all below
  sqrt(1.2) = 1.0954, the only window in which an RMS-abstain could
  promote under MSE. Zero records fall in [1.0954, 1.2). Max MSE
  ratio overall 1.0774 < 1.2. Outcome counts: 46 abstained,
  18 killed, 0 promoted under EITHER definition (killed/abstained
  boundary at 1.0 is invariant under squaring; FAIL/ABSTAIN checker
  outcomes do not depend on the ratio). No case re-run required.
  (Parent's closeout headline quoted belt max 1.02 -> MSE 1.040;
  the JSONL-exact belt max is 1.0053 -> MSE 1.0107. Same conclusion;
  the JSONL is authoritative.)
- **Live ROM integrity:** byte-identical to its pre-Phase-2 backup
  after all work; loads cleanly (27 consolidations, 10 deferred,
  phantom lesson intact).

### 5.7 Files changed (Phase 2)

- Modified: `checker_brain.py`, `optimizer_brain.py`,
  `rom_closure.py`, `rom_history.py`, `hypothesis_tracker.py`,
  `rom_loop.py`, `real_data/secular_elements.py`,
  `audit_fixes_note.md` (this appendix).
- Added (verification artifacts, NOT sealed records):
  `phase2_belt_replay_results.json`,
  `phase2_belt_replay_prebelt_results.json`,
  `phase2_ammonite_results.json`.
- Added (local revert insurance, NOT part of the build):
  `pre_phase2_backup/` (originals of all edited files +
  `real_data/parent_rom.json.pre_phase2_20261026` + sealed-file
  backups).
- Deliberately NOT changed: `sealed_runs/rom_closure_validation_results.jsonl`,
  `rom_loop_closure_note.md`, `rom_closure_lean.py`,
  `rom_closure_validate.py`, `rom_closure_pilot.py`,
  `rom_closure_selftest.py`, all five brain modules other than the
  checker/optimizer, `particle_brain.py`, `rails_brain.py`,
  `conductor_brain.py`, the full-build Drive folder (delta-sync
  below is the only exception, and it is updates-in-place, not a
  re-upload).

### 5.8 What Phase 2 does NOT clear (carried forward)

- The closure verdict remains STILL CONDITIONAL: C-d still fails on
  the scratch tracker (deferred-mass fix is a separate follow-on
  requiring Jase's disposition decision); novel recovery still
  undemonstrated (redesigned novel case is a separate follow-on);
  refit-cost fix is a separate follow-on. Phase 2 fixed the
  measurement machinery, not those three items.
- Pre-fix inflated ROM bins remain inflated and must be read with
  that caveat until fresh ledgered consolidations dominate them.
- The checker PASS is now an independent gate (training-only
  starts, refit RMS) for the 6-parameter path. The JOINT (6+k)
  interface is still missing — that is the joint-interface spec's
  prototype, a separate build decision, not Phase 2.

## 6. Phase 2b — Follow-up correctness batch (items 1–2 ONLY), APPLIED 2026-10-26

**Dispatch:** Jase-approved ("Continue" on the recommended next bounded
action from the Phase 2 source review). Scope is EXACTLY two items:
invalid-ratio verdict handling, then ledger identity. Nothing else.
No deferral/C-d fix, no novel-driver relabeling, no temp-filename
change, no size_bytes/doc wording, no joint interface, no ranker, no
structured decision record, no optimization. No other bug found during
this batch; none fixed.

**Safety record:**
- Every edited file backed up BEFORE changes in `pre_phase2b_backup/`
  (rom_closure.py, rom_history.py, rom_loop.py, audit_fixes_note.md,
  plus `parent_rom.json.pre_phase2b_20261026`).
- Live ROM byte-identical to that backup after all work (md5-verified):
  27 consolidations, 10 deferred belt entries, phantom lesson intact.
  All verification ran against temp copies or in-memory ROMs; the live
  ROM was never written by this batch.
- NOT modified: `sealed_runs/rom_closure_validation_results.jsonl`,
  `rom_loop_closure_note.md`, `rom_closure_lean.py`, or any validation
  artifact. The lean driver is a frozen artifact: it unpacks
  `verdict_for_candidate` as a 2-tuple (line 147) and calls
  `_consolidate_tracker` without event_id (lines 199, 384) — both
  preserved below by design, not by accident.
- No existing test was adjusted. New tests are additive
  (`phase2b_regression_tests.py`).

### 6.1 Item 1 — Invalid comparison abstains, never kills: LANDED

**Bug (verified in pre-change code):** `verdict_for_candidate` defaulted
a missing `holdout_mse_ratio` to NaN, and in the PASS branch both
comparisons against NaN are false, so it fell through to `'killed'`.
The old docstring defended this as "as before — an undefined
improvement is not a promotion." That reasoning is wrong: an undefined
comparison is not evidence AGAINST the candidate either, and the FAIL
branch already abstained on inconclusive tests, so PASS + NaN ->
killed was internally inconsistent as well as wrong. (A second,
unreported path: an infinite ratio would have PROMOTED, since
inf >= 1.2 is true. Both paths are now closed.)

**Change (`rom_closure.py`):**
- New `verdict_for_candidate_detailed(fit_result)` (line 239)
  returns (outcome, ratio, reason) with a VALIDITY GATE FIRST:
  present-but-non-finite `baseline_holdout` ->
  `'abstained', 'baseline_holdout_unavailable'`; missing/NaN/infinite
  ratio, or non-finite candidate holdout ->
  `'abstained', 'comparison_invalid'`. `'killed'` is reserved for a
  VALID comparison that disfavors the candidate (valid ratio < 1.0,
  or FAIL with converged + physical gates and a valid comparison).
  The gate applies to all branches: a FAIL kill on an invalid
  comparison now also abstains (brief-literal, conservative; the
  FAIL-inconclusive branches were already abstains).
- Holdout keys are checked only when present: synthetic checker-only
  dicts (regression tests T2b/T2c) carry no holdouts, and a finite
  ratio is itself the comparison. Real `fit_candidate` outputs always
  carry both holdouts, so the gate is complete on the live path.
- `verdict_for_candidate` (line 293) is now a 2-tuple wrapper around
  the detailed function (reason dropped) for frozen callers that
  unpack two values: the lean driver, the pilot, and tests T2b/T2c.
  New code needing the reason calls the detailed variant. The old
  "as before" justification is removed from both docstrings.
- `close_invented` uses the detailed variant, stores
  `'verdict_reason'` in each fitted record, and passes `'reason'` in
  the verdict dicts (ignored by `update_from_verdicts`, which reads
  only name/outcome/ratio/region/coherent — reconstructable without
  changing tracker math). NaN ratios never enter tracker math:
  abstained verdicts carry `holdout_mse_ratio=None`, as before.

**Tests (new file `phase2b_regression_tests.py`, T7a–T7h, 8/8 pass):**
missing key -> abstain `comparison_invalid`; NaN -> abstain
`comparison_invalid`; inf -> abstain `comparison_invalid` (not
promoted); baseline-unavailable beats even a favorable hand-built
ratio -> abstain `baseline_holdout_unavailable`; candidate-PASS with
invalid baseline (the realistic triggering path) -> abstain
`baseline_holdout_unavailable`; candidate-holdout-invalid -> abstain
`comparison_invalid`; valid mapping grid unchanged (1.21 promoted,
1.1 abstained, 0.9 killed, FAIL converged+physical killed,
FAIL non-converged abstained, ABSTAIN abstained, all with reason
None); wrapper returns a 2-tuple with identical outcomes.

**PROOF no valid verdict changes — JSONL re-map (from the log, not
summaries):** all 64 records of
`sealed_runs/rom_closure_validation_results.jsonl` were re-mapped
with the OLD function (loaded from the pre-Phase-2b backup) versus
the NEW detailed function. Validity gate fires on ZERO records (all
baseline/candidate holdouts and ratios finite). PASS records match
their recorded raw outcomes exactly. For FAIL/ABSTAIN records, whose
gates the log does not carry, old vs new were compared across ALL
gate combinations (converged ±, physical ±): ZERO disagreements.
Totals identical under old, new, and raw: 46 abstained, 18 killed,
0 promoted. No case re-run required; no valid outcome changed.

### 6.2 Item 2 — Ledger identity contract: LANDED

**Weakness (verified in pre-change code):** the ledger keyed evidence
as event_id -> child.name -> {loglik, good}, with no body parameters
and no dataset/model identity. Closure defaulted case_id='closure';
the novel path used the literal 'novel-case'. `rom_loop.py` already
passed real case['id'] and is the pattern followed here.

**Change (`rom_history.py`, `rom_closure.py`, `rom_loop.py`):**
- New constants/exceptions/helpers (`rom_history.py`):
  `LEDGER_MODEL_VERSION = "1"` (line 244; bump when consolidate()
  semantics change); `LedgerIdentityError(ValueError)` (line 255);
  `_normalize_bodies` (line 260; plain floats only — the save path
  uses json.dump without a default handler, so numpy floats in
  entries would break persistence); `_bodies_equal` (line 272; exact
  float equality after normalization, tolerant of tuple-vs-list
  across JSON round-trips); `_resolve_ledger_event` (line 285; pure
  check, no mutation).
- `consolidate(parent, children, event_id=None,
  event_identity=None)` (line 330). Identity is a dict
  {dataset_id, model_version, scoring}, stored in the sibling
  `parent.extra['consolidated_event_meta'][event_id]` (the
  {child_name: entry} ledger structure is UNCHANGED, so old readers
  keep working). Identified entries additionally carry 'bodies'
  (normalized plain floats), 'body_type', and 'units'
  ("mass_solar,radius_au,phase_rad"). Guard-created entries carry
  the same fields. `ChildROM` gains `last_consolidated_identity`
  (guard backstop now identity-checked too).
- Rejection rules (all validated BEFORE any mutation, so a rejected
  write leaves no partial state — tested in T8a):
  same event id + different dataset/model/scoring -> reject;
  same child name + different parameters/body_type -> reject;
  identified event + unidentified write -> reject; unidentified
  write to a legacy event is the legacy path (below).
- Legacy compatibility (required by frozen callers and the T3
  tests, which call consolidate with event_id and no identity):
  event_identity=None preserves the old behavior verbatim, with the
  event explicitly marked legacy-identity in the meta store. A
  legacy-identity event can NEVER be upgraded to identified, and an
  identified event can NEVER accept an unidentified write.
- Grandfathering: existing entries keyed 'closure' / 'novel-case'
  are left untouched. A new identified write to an event id that
  already exists in the ledger without identity meta is REJECTED
  (the resolver checks pre-existence BEFORE creating the entry —
  an earlier draft checked after setdefault and misclassified every
  new event as pre-existing; caught by smoke test, fixed, and
  covered by the resolver's ordering comment). Migration proposal
  (NOT performed, per brief): a future migration could copy
  legacy entries under new case ids with identity meta derived
  from their recorded cases, leaving the originals intact; it needs
  its own decision and must never rewrite history in place.
- Persistent-path case IDs (`rom_closure.py`): `close_invented`
  (line 376) and `_defer_abstained` (line 328) now REQUIRE an
  explicit case_id. Implemented as default-None-plus-loud-ValueError
  (message names the rule) rather than a bare required parameter,
  so the failure names the violated rule; behaviorally identical
  (no silent default). `run_novel_case` (line 462) takes
  case_id=None and generates a real unique id per invocation
  (`novel-{seed}-{uuid12}`), recorded in the report as 'case_id',
  threaded to close_invented, deferral, and the final consolidation
  (same id + same dataset replays delta-only). An explicit case_id
  gives a reproducible, replayable run.
- Dataset identity (`rom_closure.py` line 360,
  `ledger_identity_for`): sha256 content hash of the dataset's
  times, observations, and sigma, so the same data always yields
  the same identity and different data can never share one.
  Scoring string: `holdout_mse_ratio:ACCEPT_RATIO=1.2`.
- `rom_loop.py` run_case (line 151): passes full identity with
  dataset_id = case['id'] (each replay case is a distinct scenario)
  and scoring 'rom_loop:verdict-loglik'. The only other live
  consolidate caller, `real_data/residual_hunt.py`, passes no
  event_id (legacy path, unaffected).

**Tests (new file, T8a–T8h, 8/8 pass):** same-name-different-params
rejected with bins unchanged; same-event-different-dataset rejected
while a distinct event consolidates fully; identical-event replay
still delta-only (n_tried 1, sum == new loglik, n_good not
re-credited); legacy event rejects an identified write;
identified event rejects an unidentified write; distinct unique ids
consolidate independently; guard replay under the same identity is
a no-op while a guard identity mismatch is rejected; JSON
round-trip replay is a no-op (persisted list-bodies match in-memory
bodies).

### 6.3 Verification results (all required items)

- **Existing regression suite: 16/16 PASS** (exit 0; no test adjusted).
  New Phase 2b suite: **16/16 PASS** (T7a–T7h + T8a–T8h), reported
  separately as required.
- **ROM calibration suite: 13/13 groups PASS** (script's own verdict).
- **Belt live-run replay: VERDICTS UNCHANGED.** Replicated
  rom_reconstruct_belt.py's L1–L4 run_case calls against temp copies
  of the pre-belt ROM and the current live ROM (live ROM and sealed
  files untouched; outputs in the new, non-sealed
  `phase2b_belt_replay_results.json`). Both copies: L1 flagged,
  surprised, 7 invented; L2 phantom killed_by_inventory; L3
  ceres/vesta/pallas promoted; L4 silent (surprised=False,
  invented=[]). Pre-belt L4 posteriors vs sealed: max diff 4.78e-07.
  That figure is the sealed file's own rounding floor (sealed L4
  posteriors are stored at 6 decimals, so any exact replay differs
  by up to 5e-7); it matches the C-c regression figure exactly.
  Phase 2 §5.6(b) reported 0.0 for the same comparison, presumably a
  rounded comparison — the unrounded measured value is 4.78e-07,
  under the 1e-6 bar, and the verdicts are identical either way.
  Current-ROM L4 diff 3.81e-02, as in Phase 2 (baseline-bin effects,
  not a fix effect).
- **JSONL re-map: NO CHANGES** (see §6.1: 46 abstained / 18 killed /
  0 promoted under old, new, and raw).
- **Live ROM integrity:** byte-identical to the pre-Phase-2b backup
  (md5-verified): 27 consolidations, 10 deferred, phantom lesson
  intact.
- **Ammonite rerun: NOT re-run in this batch.** Rationale: this batch
  touches verdict mapping and ledger code only; the fitter, checker,
  and particle paths are untouched, and the touched code is covered
  by the 16 new tests, the belt replay, and the JSONL re-map. A
  490 s rerun would re-verify untouched code.
- **Each fix verified IN SOURCE** (file/line cited above), not just
  by test output.

### 6.4 Files changed (Phase 2b)

Modified: `rom_closure.py` (verdict mapping + detailed variant,
required case_id, novel unique ids, identity helper),
`rom_history.py` (identity constants/exceptions/helpers, new
consolidate, ChildROM guard identity), `rom_loop.py`
(event_identity in run_case), `audit_fixes_note.md` (this §6).
Added: `phase2b_regression_tests.py` (16 tests),
`phase2b_belt_replay_results.json` (verification, non-sealed),
`pre_phase2b_backup/` (originals + ROM backup; revert insurance).
Deliberately NOT changed: `sealed_runs/rom_closure_validation_results.jsonl`,
`rom_loop_closure_note.md`, `rom_closure_lean.py`,
`rom_closure_validate.py`, `rom_closure_pilot.py`,
`rom_closure_selftest.py`, `checker_brain.py`, `optimizer_brain.py`,
`particle_brain.py`, `rails_brain.py`, `conductor_brain.py`,
`hypothesis_tracker.py`, `secular_elements.py`.

### 6.5 Caveats carried forward (not failures)

1. **Frozen-script behavior changes on re-run (loud, intended):**
   `rom_closure_validate.py` passes case_id to close_invented (fine)
   but calls run_novel_case without one — on any re-run it now gets
   a generated unique id instead of the shared 'novel-case' literal,
   which is the fix working as designed, but its ledger ids will
   differ from the original run. Do not re-run frozen scripts
   expecting identical ledger ids. The lean driver's 2-tuple unpack
   and event_id-less consolidations keep working unchanged.
2. **Self-test still stale:** `rom_closure_selftest.py:63` builds
   verdict dicts with the removed bare 'ratio' key (pre-Phase-2
   interface). Do not run it expecting a pass; superseded by
   T2b/T2c (ratio mapping) and T7 (validity mapping).
3. **Old checkpoints mix ratio eras:** the lean driver's old
   checkpoint records pre-date the MSE contract; do not re-run it
   against post-Phase-2b code with the old checkpoint present
   (Phase 2 caveat, unchanged).
4. **Pre-fix inflated ROM bins NOT hand-rewritten** (would invent
   history). The ledger — now identified — stops further inflation;
   bins not to be trusted hard until fresh ledgered consolidations
   dominate.
5. **Closure verdict remains STILL CONDITIONAL.** This batch fixed
   comparison validity and evidence identity, not the three
   clearing items: C-d still fails (deferred-mass fix needs Jase's
   disposition decision), novel recovery still undemonstrated
   (redesigned novel case is a follow-on), refit-cost fix is a
   follow-on. The joint (6+k) interface is likewise still missing
   — separate build decision, not this batch.
6. **Two splice errors caught during this batch (process note, not
   a code defect in the deliverable):** the first consolidate
   splice duplicated ChildROM/consolidate (wrong boundary anchor),
   which would have shadowed the new code with the old definitions;
   caught by structure grep before any test ran, rebuilt cleanly
   from backup, and verified each definition exists exactly once.
   The first identity resolver checked event existence after
   setdefault and misclassified every new event as pre-existing;
   caught by smoke test, fixed by resolving before creating the
   entry. Both are recorded here so a future reviewer does not
   mistake the final code for untested first-draft code.

## 7. Correctness batch — Drive-review findings A–G, APPLIED 2026-10-26

Jase authorized ("Fix the correctness batch", widget tap 2026-10-26
20:24 PDT). Scope is exactly the review's findings, each with its
proposed regression test. No thresholds changed (ACCEPT_RATIO = 1.2),
no defaults changed (spline remains the evaluator default), no
existing ledger identities rewritten, no sealed records modified,
nothing uploaded to Drive (the upload is a separate, still-pending
decision).

### 7.1 A — Ledger identity covers the model configuration: LANDED
`ledger_identity_for(dataset, extra_evaluator=None)` now returns
`{dataset_id, model_version, scoring, model_identity}`.
`dataset_id` is UNCHANGED (sha256 of ts/obs/sigma) — old entries keep
it. `model_identity` is a second hash over the known inventory,
`t_ref`, planet-rails provenance (range, grid size, positions at three
probe epochs), and the extra-body evaluator. Same observations +
different inventory/epoch/rails/evaluator now yield a different
identity, so the resolver rejects the write instead of letting two
different model fits share one ledger event. The resolver's mismatch
error names the case explicitly when `dataset_id` matches but
`model_identity` differs ("same observations under a different model
configuration"). Datasets without rails/inventory (synthetic test
dicts) record None / [] rather than failing.
Deliberate non-bump: `LEDGER_MODEL_VERSION` stays "1". The resolver
semantics are unchanged (dict equality); the new field carries the
scheme change, and a v1 stored identity (no `model_identity`) never
equals a v2 given identity, so old entries are grandfathered by
construction. Bumping would ALSO have broken rom_loop replays (see
7.6), which is what settled it.

### 7.2 B — Consolidate validation before ANY mutation: LANDED
`consolidate()` previously setdefault'ed both ledger dicts before the
resolver ran (so an identity rejection left two new empty dicts) and
created the event entry before child validation (so a parameter
mismatch rejection left an empty event entry). Both leaks are closed:
the resolver and the identified child-validation loop now run against
non-creating views, and the stores + event entry are created only
after all validation passes. The legacy branch and the identified
mutation loop are otherwise unchanged (same delta rules, same
guard backstop).

### 7.3 C — Baseline reuse guarded by provenance: LANDED
`fit_candidate()` gains `baseline_provenance`, built by
`baseline_fingerprint_for(dataset, extra_evaluator)` (the ledger
identity under the baseline's evaluator + that evaluator's name).
A baseline without provenance raises immediately; a malformed
provenance raises; a mismatched provenance raises (data, inventory,
epoch, rails, or baseline evaluator changed). The candidate evaluator
is NOT required to match the baseline evaluator: an intentional
shared-baseline comparison is accepted and LABELED — the result now
carries `baseline_extra_evaluator` alongside `extra_evaluator`.
`close_invented` builds and passes provenance for its reused baseline
and records the baseline evaluator in every fitted record.
Migrated callers (same 2-line pattern each): `rom_closure_lean.py`
(baseline cache now stores `{'fit', 'check', 'extra_evaluator'}`; a
bare-tuple cache is recomputed, not silently reused — the cache is
regenerable, unlike the JSONL records below), `fit_comparison.py`,
`diagnostic_identical_state.py`, `acceptance_test_belt.py`,
`selector_end_to_end.py`. `rom_closure_pilot.py` passes no baseline
and is untouched.

### 7.4 D — Per-round fit history: LANDED
`close_invented`'s report gains append-only `fit_history`
(`{name: [record, ...]}`); `fitted` keeps the latest record per
hypothesis for compatibility. A round-2 retry no longer overwrites
the round-1 record. `run_novel_case` round records also carry
`fit_history`.

### 7.5 E — Promotion-gate decision reasons: LANDED
The gate is extracted as `apply_promotion_gate()` (same §1f logic):
a blocked promotion returns `('abstained',
'promotion_blocked_by_inventory')`; every other outcome passes
through with decision_reason None. `close_invented` stores BOTH
fields: `verdict_reason` (the comparison reason, untouched) and
`decision_reason` (the gate hit). A blocked promotion no longer
stores an abstention with reason None. The verdicts passed to
`update_from_verdicts` carry `decision_reason` too; the tracker
ignores the extra key (it reads specific keys via `.get`).

### 7.6 What was deliberately NOT changed
- `rom_loop.py` identities: rom_loop builds its own 3-key identity
  (`dataset_id` = case id, scoring = verdict-loglik) — a separate
  identity domain from closure fits. Changing it would break R1–R5
  replay idempotency (stored 3-key vs new 4-key → reject on fixed
  case ids). Left untouched; cross-domain event-id collisions are
  still caught by the resolver (different shapes → mismatch).
- Lean driver's `apply_round` gate mirror: same §1f logic, separate
  copy, no `decision_reason` field in its records. Left untouched
  (its JSONL/summary shapes are sealed outputs; the batch's D/E
  fixes target `close_invented`'s report).
- `rom_closure_validate.py`: still a long live-ROM run, not a smoke
  test. Not launched, not modified.

### 7.7 G — Checkpoint era markers: LANDED
Lean-driver checkpoint records now carry `ckpt_schema = 1` and
`ratio_domain = 'mse'` (stamped in `append_ckpt`, so every record
including TIMEOUTs). `load_ckpt()` REFUSES any record lacking both
markers or carrying a foreign era (`CheckpointEraError`, naming the
file, line, and key, with remediation: move the file aside and
rerun; do not hand-edit markers onto old records). Consequence, by
design: the current sealed
`sealed_runs/rom_closure_validation_results.jsonl` (pre-marker,
written 2026-10-26 01:42) is now refused on load — verified live
(raises, file untouched at 24,721 bytes). The sealed validation
verdict is unaffected (its records + summary JSONs are untouched);
only a future lean-driver rerun must regenerate or set aside the
file. Baseline pickles are the opposite case (regenerable cache):
stale bare-tuple pickles recompute on next use, no failure.

### 7.8 Verification results
- New suite `correctness_batch_tests.py`: 38/38 pass (A1–A8, B1–B3
  with exact-equality snapshots, C1–C5, D1–D3, E1–E5, F1–F3, G1–G4,
  G6–G7). Includes the review's proposed tests verbatim in intent:
  same-obs + changed-inventory → reject; snapshot + rejected write →
  exact equality; baseline guard accept/reject/label; round-2 history
  preserved; gate reason recorded; bins vs total size; checkpoint
  era refusal.
- Existing suites, all still green: `audit_fixes_regression_tests.py`
  20/20, `phase2b_regression_tests.py` 16/16,
  `test_extra_evaluator_selector.py` ALL PASS,
  `rom_closure_selftest.py` ALL PASS (T1–T4).
- `rom_loop.replay_all()` on a scratch ROM: R1a–R5 all run
  (consolidate restructure did not break real-tracker consolidation).
- Backups: `rom_closure.py.pre_correctness_bak`,
  `rom_history.py.pre_correctness_bak` (verified identical before
  editing).

### 7.9 Files changed (correctness batch)
- `rom_history.py`: consolidate validation-before-mutation;
  resolver model-configuration message; `size_bytes()` docstring
  corrected (bins-only) + `size_bytes_total()` + `_persisted_data()`
  shared with `save()` (save output byte-identical by construction).
- `rom_closure.py`: `ledger_identity_for` (+ `_rails_fingerprint`,
  `baseline_fingerprint_for`); `fit_candidate` guard + result
  fields; `close_invented` provenance plumbing, `fit_history`,
  `decision_reason` (via `apply_promotion_gate`); `run_novel_case`
  round records carry `fit_history`.
- `rom_closure_lean.py`: checkpoint era markers + strict loader;
  baseline cache format + stale recompute; provenance pass-through.
- `fit_comparison.py`, `diagnostic_identical_state.py`,
  `acceptance_test_belt.py`, `selector_end_to_end.py`: provenance
  pass-through only (no logic changes; sealed records untouched).
- New: `correctness_batch_tests.py` (38 tests).
