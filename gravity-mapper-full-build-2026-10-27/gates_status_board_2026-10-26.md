# Gravity Mapper — Gates Status Board (2026-10-26, late evening)

**Purpose:** one page showing where the whole project stands, what is
decided, what awaits Jase, and what is queued. Plain language; file
names point to the depth. Nothing on this board is a decision — Jase
decides, and only Jase.

## 1. Done and verified (the ground everything else stands on)

- **ROM calibration fix** — tempering + complexity penalty + caps +
  null-safe prune; 13/13 calibration, 7/7 validation replays.
  (`hidden_files/rom_integration_note.md`)
- **Live belt run** — phantom killed, Ceres/Vesta/Pallas promoted,
  belt improvement 1.227× in holdout. (`rom_live_run_belt_inventory.md`)
- **Closure validation** — 64 sealed records; belt 21/21 resolved (9
  killed, 10 deferred, 2 null-verdicted, 0 promoted); regression and
  gate PASS. (`rom_loop_closure_note.md` §6)
- **Audit fixes Phase 2 + 2b** — checker holdout isolation, MSE ratio
  unification (ACCEPT_RATIO 1.2), evidence ledger, atomic save, invalid
  comparison abstains, ledger identity contract. 16/16 + 16/16 tests.
- **Correctness batch A–G** — ledger model identity, consolidate
  atomicity, baseline guard, fit history, gate reasons, size reporting,
  checkpoint eras. 38/38 tests.
- **Atlas's fresh personal rerun (2026-10-26)** — audit fixes 20/20,
  phase2b 16/16, correctness 38/38, calibration 13/13: **87/87 pass**.
  (`fresh_rerun_2026-10-26.md`)
- **Gemini cross-check** — Ammonite Variant A + B PASS 3/3 both sides;
  measured rail load: mean-element Keplerian planets cost ~0.60 AU bias
  in a at ~250 AU. Criterion-level corroboration, not precision proof.
- **Prior-art audit** — the four-feature conjunction not located
  (medium confidence, public-web search); every component has prior
  art. Patent-attorney consult required before any public disclosure.

## 2. Why the closure verdict is still CONDITIONAL (not a failure — a gate)

Three clearing conditions, all still open:

- **(a) C-d fix + re-test** — deferred probability mass must be held
  as an explicit bucket (Hybrid direction chosen; spec v2 drafted).
- **(b) Redesigned novel case** — the old novel case could not reward
  recovery even in principle (ceiling ~1.106 < 1.2 threshold; true
  signal max 1.09σ). A new case with signal above threshold reach,
  run to termination with recovery, is needed.
- **(c) Refit-cost fix + own validation** — each outer round refits
  all accumulated abstained hypotheses (~110 fits / ~4.5 h for 5
  rounds). The loop cannot practically complete as shipped.

Until (a)–(c) land, the ROM is cleared for **tracking and gating on
decided history only** — not as a standalone discovery judge.

## 3. Ready for Jase's decision (prepared, not pressured)

| Decision | Prepared work | What it unlocks |
|---|---|---|
| **Hybrid bucket spec v2 approval** | Spec v2 + dispatch plan (separate-paths reconciliation, scratch-state rule, md5 assertion all stated in writing) | Bounded implementation batch (3 files + 1 test file, T-C1–T-C15) → then a NEW, BOUNDED C-d disposition (original failure stays on record) |
| **D9: joint-spec approval** | Approval brief (prototype scope, risks, D10/D11 prospectivity condition) | Bounded new-files-only prototype + measured cost table → then caps re-confirmation (D12) + cost acceptance (D14) |
| **Perplexity check prompt** | Counterpart Rev 9 (flag live since Rev 6) | Perplexity reads the Rev 6 inventory correction before relying on Rev 1/5 claims |
| **Version policy** | Validator mechanism ready (caller-supplied allowlist); test used ["1.2"] only | Final allowlist for the downloader (live response carries 1.2; docs claim 1.3) |

A bare "continue" is NOT approval for spec v2 or D9 — both need Jase's
explicit word, and the batches wait until then.

## 4. Drafted, awaiting its gate (design only — no code, no data touched)

- **Test-partition reservation draft (D15)** — how the final untouched
  partition will be reserved (pool, eligibility, hash-split or stride,
  coverage check, sealed record, void/replacement rules). Selection +
  sealing is a separate pre-registration action before the first
  open-question run. (`test_partition_reservation_draft.md`)
- **Bucket dispatch plan** — the §9 written plan for the batch above.
  (`bucket_implementation_dispatch_plan.md`)
- **Veto v2 design + post-Phase-2 review + Amendment 1** — visibility
  as diagnostic ladder, not a gate; integrated approval NOT READY
  (survey pass, cost table, test partition, D1 all still open).
- **Joint-interface spec + discovery ladder + ranker design** — all
  design-only; build decisions (D9/D19/D18) still Jase's.

## 5. Perplexity's track — moving fast tonight (reviewed Rev 8 + Rev 9)

- Downloader (JSON, manifest, cache, overwrite protection) — audited;
  parser gaps found by Atlas, confirmed by Perplexity's own baseline.
- Validator v2 draft — closes all five baseline failures offline
  (15/15); Atlas independently reproduced 11 decisive cases.
- Transport/cache mocks — 11/11, matching agreed retry/cache discipline.
- **Real-response test (tonight)** — validator ACCEPTs a preserved
  Jupiter response; row 1 digit-identical to Atlas's own live
  retrieval. Live-response compatibility CLOSED for one major-body case.
- **Still open:** integration, chunk joining, full download, 8-body
  coverage, version policy, small-body IDs, GM compatibility,
  interpolation accuracy, original parameter-check record (unlocated).
- Perplexity's files stay Perplexity's; promotion to the main folder
  needs maturity + Jase's approval. Atlas never edits them.

## 6. Queued behind the sequence (nothing starts early)

- **Survey-table literature pass (D13)** — Perplexity's track item #1
  when Jase directs it; until it lands, all veto outcomes stay
  `visibility_unverified`. Longest non-code pole.
- **Ladder batteries (D19), ranker (D18), conductor competition
  (D21), veto + multi-body build (D20)** — each needs its own build
  decision after the §5A gates clear.
- **Thresholds + caps (D2/D3/D5/D6/D7/D8/D12/D14)** — Jase sets, at
  their respective gates, never tuned on held-out data.
- **Live-ROM synthetic cleanup (D22)** — separate the 4 synthetic-novel
  consolidations from decided history before standalone adjudication.
  Spec v2 only FLAGS them; the cleanup is not part of bucket work.

## 7. Invariants (checked tonight, still true)

- Live ROM `real_data/parent_rom.json` md5
  `4c77b723ff5770566a85ed4e580aed2c` — byte-identical through Phase 2,
  2b, correctness batch, fresh rerun, and all of tonight's design +
  review work. No live ROM writes tonight. No thresholds changed. No
  sealed records modified. No evaluator defaults changed.

## Standing rules (so the board stays honest)

- Jase is the only decider. A recommendation, draft, or review is not
  a decision until Jase says so in his own words.
- Reviews never edit the other's files, never approve, never decide.
- Atlas messages Perplexity as judged needed and flags Jase when a
  check is worth prompting; Jase does the prompting.
- **Checking:** Atlas checks the live Perplexity Files folder during
  active work (Jase endorsed this 2026-10-26). No background poller
  is created — checks happen on active turns, not on a schedule.
- On contradiction, the Drive document (or the code, for code claims)
  governs until Jase decides otherwise.

---

*Status board, 2026-10-26, continuation work. A snapshot, not a
verdict. It goes stale as work lands — the register
(`open_decisions_register.md`) and the counterpart file
(`MUSE_TO_PERPLEXITY.md`) carry the running record.*
