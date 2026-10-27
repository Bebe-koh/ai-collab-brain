# Bucket Verification Rerun — 2026-10-26 (Atlas, personally run)

**Purpose:** close the verification gap for the bucket implementation
batch the same way the 2026-10-26 fresh rerun closed it for Phase 2:
the batch's own outputs are not taken as verification. Atlas reran
the suites directly, no agent intermediary.

**Run:** 2026-10-26 late evening, Linux VM,
`~/workspace/.venv-p9/bin/python`, each suite run directly.

## Results (newly executed)

| Suite | File | Result |
|---|---|---|
| Bucket conservation | `bucket_conservation_tests.py` | **85 passed, 0 failed** (T-C1–T-C15) |
| Audit fixes | `audit_fixes_regression_tests.py` | **20/20 pass** |
| Phase 2b | `phase2b_regression_tests.py` | **16/16 passed** |
| Correctness batch | `correctness_batch_tests.py` | **38 passed, 0 failed** |
| ROM calibration | `rom_calibration_tests.py` | **ALL 13 CALIBRATION TEST GROUPS PASSED** |

**Total: 172 checks, 0 failures.**

## Source checks done in this rerun

- Live ROM `real_data/parent_rom.json` md5 before and after:
  `4c77b723ff5770566a85ed4e580aed2c` — byte-identical.
- Backups present: `hypothesis_tracker.py.pre_bucket_bak`,
  `rom_closure.py.pre_bucket_bak`, `rom_history.py.pre_bucket_bak`.
- Legacy `_compute_posteriors` body unchanged: the diff against the
  backup shows the new bucket-aware block appended after that
  function, with the legacy body itself untouched.
- Constants unchanged: `ACCEPT_RATIO = 1.2`, `N_EFF_CAP = 50`,
  `POSTERIOR_CAP = 0.99`.
- Correctness G7 note (same as the earlier fresh rerun): the suite
  recomputes a stale bare-tuple belt cache and saves the new format
  — designed behavior, not a ROM mutation (md5 above confirms).

## Scope limits carried over from the batch report (not re-tested here)

- The bucket-path cap rule is implemented for the null's share per
  spec §1.4; a non-null top hypothesis above 0.99 is reported
  uncapped in the bucket path (legacy capped reporting untouched).
- T-C11's L-C representation is the spec §9 scratch representation;
  the live ROM carries no consolidation list, only the
  `total_consolidations = 27` counter, so only the L-D half was
  checked against a live copy.
- `close_invented()`'s new `bucket_state`/`cap_metadata` report keys
  were exercised through `_defer_abstained()` + bucket methods, not
  end-to-end through a full fit in this batch.

## What this does and does not do

This verifies the bucket implementation batch: code + tests as
delivered. It does NOT decide a new C-d disposition, does NOT
migrate the live ROM, does NOT clear any ladder gate, and does NOT
upload anything to Drive. Those remain separate decisions. The
original C-d failure stays on record.

---

*Record, 2026-10-26. No code changed, no thresholds changed, no ROM
entries modified by this rerun.*
