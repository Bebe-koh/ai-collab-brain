# Fresh Regression Rerun — 2026-10-26 (Atlas, personally run)

**Purpose:** close Atlas's stated Phase 2 verification gap. In the Phase 2
delivery Atlas verified source markers + agent-recorded outputs + data
recomputation but did NOT personally rerun the regression suite. This run
closes that gap for the current suite set.

**Run:** 2026-10-26, Linux VM, `~/workspace/.venv-p9/bin/python`, each suite
run directly (no agent intermediary). Read-only test runs; no live state
modified.

## Results

| Suite | File | Result |
|---|---|---|
| Audit fixes (Phase 1 + 2 + validity-gate T2d–T2g) | `audit_fixes_regression_tests.py` | **20/20 pass** |
| Phase 2b (validity gate + ledger identity) | `phase2b_regression_tests.py` | **16/16 passed** |
| Correctness batch (A–G) | `correctness_batch_tests.py` | **38 passed, 0 failed** |
| ROM calibration | `rom_calibration_tests.py` | **ALL 13 CALIBRATION TEST GROUPS PASSED** (N_EFF_CAP=50, POSTERIOR_CAP=0.99) |

**Total: 87/87 pass.**

## State preservation

- Live ROM `real_data/parent_rom.json` md5 before: `4c77b723ff5770566a85ed4e580aed2c`
- Live ROM md5 after: `4c77b723ff5770566a85ed4e580aed2c` — byte-identical.
- One note from the correctness run: baseline belt cache was a stale
  bare-tuple cache (pre-provenance era); the suite recomputed it and saved
  the new format (test G7, PASS). That is the suite's designed behavior,
  not a ROM mutation — the ROM md5 above confirms no live state changed.

## Scope of this verification

This closes the "Atlas personally reran the suites" gap for unit/regression/
calibration suites. It does NOT re-run the belt replay, the Ammonite 3/3
fitter runs, or the closure validation fits (those remain covered by their
original agent-recorded outputs + Atlas's data recomputation, as stated in
their delivery notes). The stale-selftest caveat stands: `rom_closure_selftest.py`
was already corrected (T4 key fix) in the selector closeout; it is not part
of this rerun set.

---

*Record, 2026-10-26. No code changed, no thresholds changed, no ROM entries
modified.*
