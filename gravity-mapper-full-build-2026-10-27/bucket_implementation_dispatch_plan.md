# Bucket Implementation — Pre-Written Dispatch Plan (spec v2 §9)

**Status:** PLAN ONLY. This document is the written pre-implementation
plan that spec v2 §9 requires BEFORE any code is edited. It authorizes
nothing. The implementation batch starts ONLY on Jase's explicit
approval of hybrid bucket spec v2 — a bare "continue" is not approval
(deliberate non-action, stated 2026-10-26). If Jase amends v2, this
plan is revised to match the approved version before dispatch.

## 1. Trigger and approval semantics

- **Trigger:** Jase's explicit approval of `hybrid_bucket_spec.md` v2,
  in his own words, for implementation (not just for review).
- **What approval authorizes:** the bounded batch in §3–§5 below, and
  nothing else. No live-ROM migration, no threshold change, no
  evaluator-default change, no dependent work (C-d re-test disposition,
  ladder Gate 0, standalone adjudication) until their own decisions.
- **What approval does NOT do:** it does not erase the original C-d
  failure (the failure stays on record; a successful batch supports a
  NEW, BOUNDED disposition only), does not establish novel-body
  recovery, and does not clear unrelated discovery gates.

## 2. Pre-implementation plan statement (spec §9, items (a)–(c))

This section IS the statement the spec requires in writing before
editing code. If any item below cannot be stated at dispatch time, the
batch does not start.

### (a) §1.4 rule 6 reconciliation — DECIDED HERE: separate paths

**Decision: separate paths, legacy labeled.** The existing
`_compute_posteriors` proportional-redistribution loop stays EXACTLY
as-is for trackers WITHOUT a deferred bucket (legacy path, labeled as
such in code and in the batch record). A NEW bucket-aware posterior
path is used whenever a deferred bucket exists, implementing spec v2
§1.4/§1.5 exactly:

- Single scientific distribution: uncapped softmax over active +
  deferred together, single shared max-offset (§1.5), sums to 1.0,
  persisted and cited.
- Cap as display only: when uncapped null > 0.99, report
  `null_display = 0.99` flagged `display_only: true` + full uncapped
  distribution + `cap_excess = uncapped_null − 0.99` as a scalar
  annotation, redistributed to NOBODY. MUST-NOT-COMBINE rule: capped
  null + uncapped others never presented/persisted as a distribution.
  Capped values NEVER persisted as posteriors (persist uncapped +
  `cap_applied` + `cap_excess`); load rejects a capped value stored as
  a posterior.
- Bucket counts as a second component for cap purposes (the legacy
  single-hypothesis cap exemption does NOT apply when a bucket exists).

**Why separate, not unified:** a unified path would change existing
test expectations — the 87/87 suites (audit fixes 20/20, phase2b
16/16, correctness 38/38, calibration 13/13) pin legacy behavior — and
would require justifying every changed expectation. Separate paths
preserve ALL existing results exactly and confine new behavior to
bucket-bearing trackers, where the new tests (T-C1–T-C15) pin it. The
legacy path's cap behavior is documented as legacy, not as the
scientific rule for bucket trackers. No silent reconciliation: the
two paths are named, labeled, and separately tested.

### (b) Scratch-state confirmation

ALL §5 tests (T-C1–T-C15) and ALL existing suites run against scratch
state ONLY: scratch trackers + scratch ParentROM in temp directories.
The live ROM (`hidden_files/real_data/parent_rom.json`) is READ-ONLY
during the batch. Any test writing to the live path FAILS the batch
(the batch record must show the live-path guard active, not merely
asserted). No test in the batch reads live-ROM entries as fixtures
except for the read-only legacy-classification checks (T-C11: L-D vs
L-C classification on a COPY, never on the live file).

### (c) Live-ROM md5 assertion

- **Expected md5 at dispatch:** `4c77b723ff5770566a85ed4e580aed2c`
  (byte-identical through Phase 2, 2b, correctness batch, and the
  2026-10-26 fresh rerun).
- **Before the batch starts:** assert the live file's md5 matches. If
  it differs, STOP — the baseline moved and the batch does not start
  until the difference is explained in writing.
- **After the batch ends:** assert again. Any change = batch failure:
  restore from backup, report, do not proceed to preservation or
  Drive upload.

## 3. Scope (spec §9, restated for the dispatch brief)

**Files to change (only):**

- `hypothesis_tracker.py` — bucket-aware posterior path + cap
  metadata (new path per §2(a); legacy path untouched).
- `rom_closure.py` — `_defer_abstained` weights + identity (~line
  472); `close_invented` fit-history handling as specified (append-only
  preserved, not altered in semantics).
- `rom_history.py` — two-class flags (L-D / L-C) + ledger identity
  path. Atomic save mechanism UNCHANGED (temp + flush + fsync +
  re-read + `os.replace()`).
- ONE new test file carrying T-C1–T-C15 (conservation, cap display,
  persistence exactness, replay no-op, rejection atomicity,
  legacy classification, log-domain normalization, offset invariance,
  underflow/sentinel handling).

**Explicitly NOT changed:** fitter brains, `rom_loop.py`, validation
artifacts, sealed records, live-ROM existing entries (flags only,
on copies — never in place), thresholds (ACCEPT_RATIO, caps,
N_EFF_CAP), evaluator defaults. No new packages. No redundant codebase
copies.

**Baselines + backups:** verified post-Phase-2b working copy in
`hidden_files/` + Drive full-build + existing backups. Each edited
file backed up as `.pre_bucket_bak`, verified byte-identical before
editing (per the selector-integration precedent).

**Durable save route:** existing `ParentROM.save()` atomic path only.
Deferred list persists via the `parent.extra` unknown-key path. No new
save mechanism is built in this batch.

## 4. Test execution and reporting rules

- **Preregistered tests first:** T-C1–T-C15, all newly executed on
  scratch state. No test is added, removed, or reinterpreted mid-batch
  without stopping and reporting.
- **Existing suites second:** audit fixes 20/20, phase2b 16/16,
  correctness 38/38, calibration 13/13 — newly executed, results
  reported SEPARATELY from historical results. Old numbers are never
  copied forward as new evidence.
- **On any required-test failure or contract conflict:** STOP that
  dependent path, report the exact failure. Do NOT relax a tolerance,
  reinterpret a failed test, or substitute B3-only clearance without
  a SEPARATE decision (B3-only fallback was WITHDRAWN and replaced by
  stop-report-separate-decision).
- **Verification after the batch:** Atlas verifies source + tests
  personally afterward (per the 2026-10-26 fresh-rerun precedent:
  agent outputs + data recomputation alone left a verification gap;
  a personal rerun closed it). The batch is not "verified" until that
  rerun lands.

## 5. Preservation and continuity (after results approval, not before)

- Preserve actual changed source, complete test outputs, and
  provenance BEFORE any dependent work begins.
- Update the applicable continuity record after approved durable
  saves: Drive milestone backup + delta-sync into the full-build
  folder (code AND docs), only after Jase approves the results — the
  same order as the correctness batch (which waited for a separate
  tap before uploading).
- **Continuity-manifest note:** no local continuity-manifest file
  exists (finding from spec v2 §9 work); the continuity record for
  this batch is the Drive milestone backup + delta-sync + complete
  test-output record. Manifest creation remains a separate decision.

## 6. Dispatch shape

- Single bounded batch (approval ergonomics: batch outward-facing
  work; one dispatch, not N calls) with THIS plan attached as its
  brief, plus spec v2 itself.
- The batch's first deliverable is the §2 statement re-confirmed
  against the actual baseline (md5 check output + legacy-path
  identification in source), before any edit. If that confirmation
  fails, the batch stops before editing anything.
- On completion, the batch reports: changed files + diffs, full test
  outputs (T-C1–T-C15 + existing suites, newly executed), live-ROM
  md5 before/after, and any failure with its exact text. Atlas then
  runs the personal verification rerun and reports that separately.

---

*Plan, 2026-10-26, continuation work. Conditional on Jase's explicit
approval of spec v2. Decides nothing, edits nothing, moves nothing to
Drive until results approval. If v2 is amended, this plan is revised
to match before dispatch.*
