# Audit of Perplexity's static review of the Gravity Mapper build

**Date:** 2026-10-26. **Type:** audit only — no code modified, no fits run.
**Auditor:** Atlas (subagent). **Review under audit:** Perplexity's static
review of the Drive snapshot `gravity-mapper-full-build-2026-10-25`
(pasted by Jase 2026-10-25). **Norm applied:** "Review 1, me 1" — every
outside claim checked against primary code evidence before acceptance.
**Scope note:** the closure-validation re-run in progress was NOT
interfered with; its results will need reconciliation with finding 3
below (it uses the RMS ratio definition as written).

## Verdict table

| # | Claim | Verdict | Scope | Changes a delivered verdict? |
|---|-------|---------|-------|------------------------------|
| 1 | Phase loss in tracker rescoring | CONFIRMED | Legacy `tracker_solver.py` only; live path unaffected | No |
| 2 | Holdout contamination + mislabeled train_rms | CONFIRMED (both halves) | Checker brain (live gate chain) | No — see §2 |
| 3 | Closure RMS ratio vs tracker MSE ratio | CONFIRMED | Closure subsystem only | No — direction is conservative; belt numbers unaffected |
| 4 | Repeated consolidation double-counts | CONFIRMED + quantified | ROM bins only, NOT posteriors | No |
| 5 | Legacy scorer silently skips off-grid rows | CONFIRMED (latent) | Legacy drivers only; live path never calls it | No |
| 6 | Hardcoded /home/hatch paths, import-time chdir | CONFIRMED | Legacy drivers + hardcoded HERE in live modules | No (portability only) |
| 7 | `n_hypotheses` ignored for TOP_K | CONFIRMED | Legacy `tracker_solver.py` only | No |
| 8 | `update_sequential` replaces, not accumulates | CONFIRMED | Legacy tracker method, documented simplification | No |
| 9 | `fit_state` picks lowest cost before checking success | CONFIRMED | Optimizer brain (live gate chain) | No — all delivered fits converged |
| 10 | Non-atomic `ParentROM.save()` | CONFIRMED | ROM persistence | No (no corruption observed) |
| 11 | Duplicate hypothesis names not rejected | CONFIRMED | Tracker `add()` | No (no duplicates in delivered runs) |
| 12 | `ExtraRails` works around circular-phase bug | CONFIRMED | Shared `cart_to_elements` bug; workaround is correct | No |
| (a) | `source_upload/` exclusion = packaging gap | PARTIAL | Real for legacy drivers; live build has NO `gravity_mapper` import — BUT the snapshot has a different, worse gap (§A) | No on disk; yes for the snapshot's importability |
| (b) | Closure implementation IS present | CONFIRMED | — | — |
| (c) | Absent closure-validation outputs ≠ failed tests | CONFIRMED (correct reading) | — | — |

**Headline: 11 of 12 code claims confirmed, 1 confirmed-latent, 0 refuted;
both framing self-corrections confirmed; the packaging claim is partial
and understates the snapshot's actual import gap. No delivered verdict
changes** (Ammonite §11, ROM calibration, live belt run all stand — each
for a stated reason below, not on trust). Perplexity's review is
substantially accurate; its gaps are scope (it does not separate live
path from legacy drivers) and one missed snapshot defect (§A).

## 1. Phase loss — CONFIRMED, legacy-only

Evidence:
- `tracker_solver.py`: refined candidates are converted with phase
  dropped:
  `bodies = [(jc1.mass_solar, jc1.radius_au), (jc2.mass_solar, jc2.radius_au)]`
- `hypothesis_tracker.py` `Hypothesis.__init__`:
  `self.bodies = [tuple(list(b) + [0.0] * (3 - len(b))) for b in bodies]`
  — a 2-tuple silently becomes phase 0.0.
- The refined candidates DO carry phase: `Candidate` is a dataclass with
  `mass_solar, radius_au, phase_rad`, and `catalog_two_body_recovery.
  build_system` passes `candidate.phase_rad` into `circular_body`, so
  phase sets the body's position. Rescoring a phase-0.0 body scores a
  different orbit from the refined one.
- Deduplication key (`tracker_solver.py`) is
  `(log10 m1, r1, log10 m2, r2)` — no phase: two refined candidates
  differing only in phase collapse to one hypothesis.

Scope (Perplexity does not state this, and it matters): the live path
does NOT use `tracker_solver.py`. The five-brain conductor fits full
Cartesian state `(r0, v0)` — there is no phase parameter to lose — and
`rom_loop.py` consumes verdicts, never tracker bodies. `tracker_solver`
callers are only legacy drivers (`v2_redo.py`, `test_j4_v2r.py`,
`diag_from_truth.py`). The defect is real but quarantined to a retired
path. Cheapest correct action may be to mark `tracker_solver.py`
deprecated rather than repair it; if repaired, Perplexity's prescription
(preserve 3-tuples, phase in dedup key, regression check comparing
refined vs tracker predictions) is correct and complete.

## 2. Holdout contamination — CONFIRMED, both halves; verdicts stand

Evidence:
- `checker_brain.py` `check_fit`:
  `x_hint = np.array(fit['r0_au'] + fit['v0_au_yr'])` (the FULL-data fit
  state), then `fit_state(ts_tr, obs_tr, ..., n_starts=3, x0_hint=x_hint)`.
- `optimizer_brain.py` `fit_state` builds ALL starts from `x_base`
  (the hint when given; `data_driven_start` only when no hint). So the
  "training refit" never does a cold, training-only start — every start
  is the full-data solution or a perturbation of it. LM is local, so the
  basin is chosen by full-data information, including withheld points.
- In the conductor's N-body rung the leak is strongest:
  `check_fit(..., early_stop_rms=2.0 * sigma)` — the refit stops at
  start 0 as soon as the hinted state reaches 2σ on train, which a
  full-data solution at the noise floor essentially always does. The
  "refit" then barely moves from the full-data state.
- `train_rms = float(fit.get('rms_au', np.inf))` (`checker_brain.py`
  line 67) — the FULL-data fit's RMS, not the training refit's. It feeds
  both the `noise_consistent` gate and the holdout threshold
  `max(5σ, 3*train_rms)`. The label is wrong and the gate mixes a
  full-data statistic into a holdout test. (Whether that threshold is
  looser or tighter case-by-case is not determined; the advertised
  isolation is false either way.)

Precision Perplexity misses: there is no TRUTH leakage here (the
conductor docstring's "no truth leakage" claim is true) — the leakage is
of withheld OBSERVATIONS through the starting state. Different flaw,
same consequence for gate independence.

Impact on Ammonite §11: NONE of the three PASS/FAIL outcomes change,
because the rung's scored criterion (`|Δq|/q < 1%` AND `|Δa|/a < 1%`
against sealed truth, `sealed_runs/nbody_fitter_rerun_results.json`:
variant A `dq_rel ~1e-6`, `da_rel ~3e-5`, `keplerian_check: PASS`) does
not depend on the checker at all. Specifically: variant B Keplerian
ABSTAIN was driven by the `noise_consistent` gate (train rms 41× σ) —
a model-bias signal present on train data alone, so a clean refit would
also fail it; variant A Keplerian PASS and variant B N-body PASS are
independently confirmed by the sealed-truth errors. What DOES change:
the checker's PASS must no longer be cited as independent corroboration
on an open question until the refit is fixed (cold/data-driven starts,
train RMS from the train refit, withheld data evaluated only after
model choices freeze). Perplexity's recommended correction is correct
and complete.

## 3. Ratio contract — CONFIRMED; direction is conservative

Evidence:
- `rom_closure.py` `fit_candidate`: `ratio = b_ho / c_ho` where both
  are `holdout_rms_au` — an RMS ratio.
- `hypothesis_tracker.py` `add_verdict` docstring: "`holdout_ratio`:
  holdout MSE without the body / with it (>1 = better)" — an MSE ratio.
- `close_invented` passes the closure ratio straight into
  `update_from_verdicts` as `holdout_ratio`, and `verdict_for_candidate`
  applies `ACCEPT_RATIO = 1.2` to the RMS ratio. The inventor's
  `is_surprised` default `accept_ratio=1.2` compares against
  `last_holdout_ratio`, which for closure verdicts is likewise the RMS
  ratio. The whole closure subsystem is self-consistent in RMS units
  and inconsistent with the tracker's documented MSE units.

Direction (Perplexity states the mismatch but not its direction):
RMS ratio = √(MSE ratio). Consequences:
- The closure's 1.2 threshold is STRICTER than the documented one:
  RMS 1.2 ↔ MSE 1.44.
- Promoted closure verdicts contribute HALF the intended log-odds:
  `log(RMS ratio) = 0.5 · log(MSE ratio)` (e.g. log 1.2 = 0.18 instead
  of log 1.44 = 0.36). The error under-counts evidence; it cannot
  inflate a closure promotion.
- Concrete illustration: the live belt run's 1.227× improvement is an
  MSE ratio (`rom_live_belt_run.py`: `BELT_RATIO = 3.206e-15 /
  2.612e-15`). As an RMS ratio that is 1.108 — BELOW the closure's 1.2
  bar. Same evidence, different verdict under the two definitions.

Impact: the live belt numbers are UNAFFECTED — the belt run went
through `rom_loop` verdicts in MSE units, consistent with
`add_verdict`'s documentation, and never touched `rom_closure`. No
delivered verdict used a closure ratio (closure validation had not
completed at snapshot time). Fix: square at the interface (pass MSE
ratio into `add_verdict`) and rename explicitly (`holdout_mse_ratio`
vs `holdout_rms_ratio`), as Perplexity recommends — BUT note what
Perplexity omits: squaring LOOSENS closure promotion (MSE 1.44 → 1.2),
so previously decided closure cases must be re-read under the new
definition, and the in-progress validation re-run's promotion decisions
are currently in RMS units and must be reconciled with this audit
afterwards (not by interfering mid-run).

## 4. Repeated consolidation — CONFIRMED + quantified; bins only

Evidence:
- `rom_closure.py` `_consolidate_tracker`: `ch.log_likelihood =
  h.verdict_loglik` — the CUMULATIVE verdict log-odds — for every
  retained hypothesis, then `consolidate()` adds it to `sum_loglike`
  and increments `n_tried` (and `n_good` if posterior > 0.1).
- `close_invented` calls `_consolidate_tracker` after EVERY round, and
  `run_novel_case` calls it once more at the end. `rom_loop.py`
  `run_case` consolidates once per case from the same cumulative field.
  Since `verdict_loglik` only accumulates (`+=` in `add_verdict`) and
  is never reset or snapshotted per case, every consolidation re-adds
  all prior verdicts. There is no event ID, no delta, no idempotency
  check anywhere in `rom_history.py` `consolidate()`.

Quantification (current `parent_rom.json` vs pre-live-run backup;
spans belt run + dead validation attempt + in-progress re-run, so read
as mechanism evidence, not a pure belt-run delta):
- `total_hypotheses`: 131 → 231 (+100) for far fewer distinct
  hypotheses ever tried; `total_consolidations`: 13 → 19.
- Phantom bin `-17,3`: `n_tried` 3 → 8, `sum_loglike` −10.0 → −16.0,
  while `n_good` stayed 1 — one phantom hypothesis, counted five extra
  times. Bin `-16,3`: 0 → 10 tried.

Impact, precisely scoped (Perplexity says "increase learned confidence"
without saying WHERE): tracker POSTERIORS are unaffected — they are
computed from `verdict_loglik`, never from bins. What inflates is the
ROM's numeric memory: `n_tried`/`n_good`/`sum_loglike`, hence
`learned_prior` (prior adjustment up to ±log 10, confidence-scaled)
and `promising_regions` rankings. So delivered posteriors stand, but
inventor priors driven by these bins are currently overconfident and
must not be trusted hard until the fix lands. Perplexity's recommended
correction (stable event IDs, delta-only consolidation, idempotent
replay, distinguish retries from independent confirmations) is correct
and complete; add one point: consolidation should snapshot
`verdict_loglik` per event (store last-consolidated value per
hypothesis) so even without full event IDs the delta is exact.

## 5. Legacy scorer grid skip — CONFIRMED, latent, legacy-only

Evidence (`hypothesis_tracker.py` `score_hypothesis`):
```
for step in range(steps + 1):
    t = round(step * DT, 10)
    if t in by_time:
        ...score rows at t...
```
Rows whose `time_years` is not exactly on the `step·DT` grid are never
scored; there is no check that scored rows equal input rows, and no
error for empty/nonfinite/unmatched times. The same pattern appears in
`validate_pipeline.py` `simulate_bodies`, but that is simulation at
template times, not scoring.

Scope: `rom_loop.py` NEVER calls `score_hypothesis` — it uses
`update_from_verdicts` only. Callers of the grid scorer are
`tracker_solver.py` (legacy), `hypothesis_inventor.py`
`expand_and_contract` (legacy; `rom_loop` uses `invent_from_best` +
`invent_grid_fill`, not this), and `sealed_scenarios.py` (own scorer
per the integration note). Current drivers generate rows on the grid,
so the defect is latent, not observed. Perplexity's correction
(evaluate at actual times, or validate alignment; require scored count
== input count; reject bad times) is correct. It is hygiene until an
off-grid dataset arrives.

## 6. Hardcoded paths — CONFIRMED (all three, plus one more)

- `tracker_solver.py`: `sys.path.insert(0, '/home/hatch/...')` AND
  `os.chdir('.../source_upload')` at IMPORT time — the worst instance:
  importing the module silently changes the process working directory,
  which can break relative paths elsewhere.
- `validate_pipeline.py`: same `os.chdir` + `sys.path` pattern, plus a
  stale third path (`~/.jarvis/idea-executions/7edd9420-.../scratch`)
  left over from another agent's run — that path is dead.
- `rom_closure.py` and `rom_loop.py`: `HERE = '/home/hatch/...'`
  hardcoded (no `os.chdir`, but non-portable).
- Contrast: `optimizer_brain.py` already does it right
  (`HERE = os.path.dirname(os.path.abspath(__file__))`). The fix is to
  copy that pattern everywhere. Portability only; no delivered verdict
  depends on these paths.

## 7. `n_hypotheses` ignored — CONFIRMED, legacy-only

`tracker_solver.py` `solve_with_tracker(..., n_hypotheses=10, ...)` never
references `n_hypotheses`; every count uses imported `TOP_K` from
`j3_blind_pipeline` (loop bound, prior split `log(0.7 / TOP_K)`).
Perplexity's fix (make the parameter authoritative, compute priors
after deduplication) is correct. Legacy-only; no live path affected.

## 8. `update_sequential` replaces — CONFIRMED, documented

`hypothesis_tracker.py` `update_sequential` resets each hypothesis's
`log_likelihood` and scores "this batch only", with an in-code comment
admitting it: "For simplicity, score on this batch only (true
sequential would accumulate)". The method's own docstring contradicts
itself ("rescoring on cumulative data (in practice, accumulate
batches)"). Perplexity's fix (rename as batch comparison or implement
cumulative updates) is correct. No delivered verdict used this method.

## 9. `fit_state` success ordering — CONFIRMED, live gate chain

`optimizer_brain.py` `fit_state`: best-start selection is purely by
cost (`if cost < best_cost: best = (sol, si)`); `sol.success` is only
checked at the end (`ok = bool(sol.success and ...)`). An unconverged
lowest-cost start therefore displaces a converged higher-cost start
and yields `success=False` for the whole fit. Early stopping is also
success-blind: it triggers on `rms < early_stop_rms` regardless of
`sol.success`. Fix: filter to successful starts before cost comparison
(and require success before early stopping). Impact on delivered
verdicts: none observed — sealed Ammonite results show
`converged: true` on the reported fits — but the defect sits in the
live gate chain and must be fixed before an open-question fit is
trusted to report failure correctly.

## 10. Non-atomic ROM save — CONFIRMED

`rom_history.py` `ParentROM.save()`: `with open(self.path, 'w') as f:
json.dump(...)` — direct overwrite, no temp file, no validation, no
fsync. An interrupted write corrupts the persistent record (bins,
lessons, hypotheses history). No corruption has been observed; the
live ROM round-trips today. Fix as Perplexity recommends (temp sibling
+ validate + atomic replace). Cheap, do it with the next ROM change.

## 11. Duplicate names — CONFIRMED, hygiene

`HypothesisTracker.add()` appends without any uniqueness check, while
`posteriors()` returns `{h.name: ...}` — two hypotheses sharing a name
silently overwrite each other in every posterior dict, and
`add_verdict` targets the FIRST match only. No delivered run contained
duplicates (inventor names are counter-suffixed). Fix: require unique
IDs (or key posteriors by object identity and report names separately).
Hygiene.

## 12. Circular-phase workaround — CONFIRMED, workaround is correct

`rom_closure.py` `ExtraRails.from_bodies` docstring states it
deliberately bypasses `kepler_predict` because `secular_elements.py`
`cart_to_elements` sets `M = 0.0` for `e < 1e-12` (lines 59–60),
destroying circular-orbit phase. The direct computation
(`angle = phase + n·(t − t_ref)`) is correct for the circular coplanar
representative, and the docstring honestly records the workaround.
Perplexity is right that the shared bug is unfixed: any OTHER caller
that round-trips circular elements through `cart_to_elements` →
`elements_to_cart` loses phase. Scoping: the live fitter is safe — it
propagates state vectors, and its elements output is reporting-only
(the conductor never feeds fitted elements back as states). The
exposed callers are synthetic-dataset builders that pass circular
elements (e.g. a tracer with e=0 and M≠0 through
`tracer_elements_to_state`). Fix centrally in `cart_to_elements`
(preserve the phase angle for circular orbits, e.g. carry the
longitude) with a regression test, then the workaround can be retired.
Until then, the workaround is sound, not a defect in the closure.

## A. Packaging framing — PARTIAL, and Perplexity missed the worse gap

Perplexity's claim: the manifest excludes `source_upload/`, and legacy
drivers import `gravity_mapper.catalog` from it. True for legacy
drivers (`tracker_solver.py`, `validate_pipeline.py`,
`sealed_scenarios.py`, the j-series, `residual_hunt.py` — all import
from `source_upload`). BUT: no live module imports `gravity_mapper`
at module level (verified across `rails_brain`, `particle_brain`,
`optimizer_brain`, `checker_brain`, `conductor_brain`, `rom_loop`,
`rom_closure`, `rom_history`, `hypothesis_inventor`); the only live
reference is the LAZY import inside `hypothesis_tracker.
score_hypothesis`, which the live path never calls. The on-disk live
build does not need `source_upload`.

However, the Drive snapshot has a DIFFERENT import gap Perplexity did
not identify: the snapshot copied `real_data/*.json` and `*.csv` but
NOT `real_data/*.py`. `real_data/secular_elements.py` is imported by
`rails_brain`, `particle_brain`, `optimizer_brain`, and
`cartesian_lm_fitter` — the whole live fitter chain. A clean extraction
of the snapshot therefore fails to import the fitter (the first import
error would be `secular_elements`, not `gravity_mapper.catalog`).
This is a snapshot-packaging error, not a code defect: the on-disk
build is complete. Remedy (delta upload, per the standing rule):
upload `real_data/*.py` — at minimum `secular_elements.py` — into the
full-build folder, and add a clean-environment import check as a
snapshot acceptance step, as Perplexity recommends.

## B. Closure present — CONFIRMED

`rom_closure.py` exists (385 lines: `ExtraRails`, `PerturbedParticle`,
`fit_candidate`, `verdict_for_candidate`, `close_invented`,
`run_novel_case`). The integration note's "not yet pipeline-fitted" is
historical, as Perplexity says. Presence is not validation: closure
validation had not completed at snapshot time (and the re-run is still
in progress separately).

## C. Absent validation outputs ≠ failed tests — CONFIRMED

The manifest states closure-validation outputs were excluded while
validation was running. Reading their absence as failure would be
wrong; the correct reading is "not yet produced". Perplexity's caution
is right and is adopted here.

## Perplexity's improvement ideas — assessment

- "Define one candidate-state schema" — sound; the phase defect (§1)
  and the RMS/MSE confusion (§3) are both symptoms of untyped
  interfaces. Adopt as part of fixes 1–2.
- "Structured evaluation record per fit" — sound; adopt with fix 1.
- "Evidence ledger with event IDs" — sound; this is fix 3.
- "Package runtime source independently of venvs; clean-environment
  import check" — sound and now urgent given §A.
- "Present capped/tempered values as model-comparison weights unless
  calibration is independently demonstrated" — reasonable caution, but
  note the caps are already documented as modeling choices (integration
  note §2/§7), not presented as measured uncertainties; the calibration
  test suite (13/13 groups) is the current evidence, and independent
  calibration on real pipeline verdicts is still open. Keep the
  caution, don't overstate it as a defect.
- "Keep a final untouched test partition" — reasonable future control
  for repeated invention/selection on the same data; not a defect in
  any delivered verdict (delivered verdicts used decided cases or
  sealed synthetic truth).
- "Representative rejected ≠ region excluded" — already documented in
  the closure docstring ("A killed verdict refutes the representative,
  not every eccentric/inclined body nearby"); not a new finding.
- "Reuse baseline fits with cache identity" — fine as optimization
  AFTER correctness fixes; the closure already reuses a baseline within
  a call.

## Ranked fix list (by consequence)

1. **Checker holdout isolation + `fit_state` success filtering** (§2,
   §9) — the only findings that weaken a LIVE gate on an open question.
   Cold/data-driven refit starts; train RMS from the train refit;
   withheld data evaluated only after model choices freeze; successful
   starts only in best-cost selection; success required before early
   stopping. Until done, checker PASS is corroboration, not an
   independent gate.
2. **Ratio contract unification** (§3) — square the closure ratio at
   the `add_verdict` interface (MSE domain), rename explicitly, and
   re-read the in-progress validation's promotion decisions (RMS units)
   under the corrected definition. Note squaring LOOSENS closure
   promotion (MSE 1.44 → 1.2).
3. **Evidence ledger / delta-only consolidation** (§4) — stable event
   IDs, snapshot-per-hypothesis last-consolidated value, idempotent
   replay. Until done, treat ROM bin statistics and learned priors as
   inflated; posteriors are unaffected.
4. **Snapshot packaging repair** (§A) — delta-upload `real_data/*.py`
   (at minimum `secular_elements.py`) to the full-build folder; add a
   clean-environment import check to snapshot acceptance. Unblocks
   Perplexity's (and anyone's) review of the live fitter.
5. **Atomic ROM save** (§10) — temp sibling + validate + replace.
   Cheap; do with the next ROM change.
6. **Phase handling decision** (§1) — either repair `tracker_solver`
   (preserve 3-tuples, phase in dedup key, regression check) or mark
   it deprecated and remove it from the build. Do not leave a known
   phase-dropping driver in the tree unlabeled.
7. **Hygiene batch** (§5, §6, §7, §8, §11, §12) — grid-scorer row-count
   validation; `HERE = dirname(abspath(__file__))` everywhere (remove
   import-time `os.chdir`, drop the dead `.jarvis` path); make
   `n_hypotheses` authoritative; rename `update_sequential` or
   implement accumulation; reject duplicate hypothesis names; fix
   `cart_to_elements` circular phase centrally with a regression test
   and retire the `ExtraRails` workaround.

## What does NOT change

- Ammonite §11 (fitter PASS 3/3 both variants): stands — sealed-truth
  scoring is independent of the checker.
- ROM integration calibration (13/13 groups, 7/7 replays): stands —
  the verdict path uses bounded log-odds, not the closure ratio or the
  ROM bins.
- Live belt run (conditionally cleared): stands — MSE-domain ratios,
  verdict-`loglik` posteriors, gate behavior all unaffected by §§3–4.
  Its "conditionally" qualifier remains exactly as stated (invented
  hypotheses need conductor-fit closure), and finding 3 means the
  closure validation now in progress must be reconciled in RMS-vs-MSE
  terms before its verdict is final.
