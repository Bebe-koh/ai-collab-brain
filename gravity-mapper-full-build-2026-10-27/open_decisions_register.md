# Open Decisions Register — Gravity Mapper (living document)

**Purpose:** one place for every decision that is currently TBD, who owns it,
and what gate it blocks. Nothing in this file decides anything — it records
what is undecided so nothing slips through silently.

**How to use it:** when a decision is made, move its row to the "Decided"
section with the date, the decision, and where it is recorded (note/doc). Do
not delete rows — the history of what was open, and when it closed, is part
of the audit trail.

**Last updated:** 2026-10-26 (after validation closeout, Phase 2 dispatched).

## Open decisions

| # | Decision | Owner | Needed before | Blocks |
|---|---|---|---|---|
| D1 | C-d disposition: explicit unknown/deferred bucket (Option A) vs formally re-registered criterion revision (Option B) | Jase | Any battery; Gate 0 | Ladder Batteries 1–4; standalone adjudication | **DIRECTION DECIDED 2026-10-26: Hybrid** (Jase: "Do hybrid") — deferred-bucket mechanism + B3-style conservation re-test criteria. Tightened spec `hidden_files/hybrid_bucket_spec.md` (v1, 2026-10-26) PENDING Jase's approval; implementation NOT authorized until spec approval. Brief's B3-only fallback WITHDRAWN (stop-report-separate-decision rule). D1 gates ladder Gate 0 + ROM ingestion; does NOT gate the joint prototype (review Amendment 1 §7.3). |
| D2 | Promotion posterior threshold (ROM) | Jase | Battery 1 | Any promotion claim on a new case |
| D3 | Kill posterior threshold (ROM) | Jase | Battery 1 | Any kill claim on a new case |
| D4 | Calibration tolerance (binned posterior vs empirical frequency) | Jase | Battery 1 | Gate 1 calibration metric |
| D5 | Battery sizes (cases per battery, Batteries 1–4) | Jase | Battery 1 | All ladder gates |
| D6 | Gate bars: precision / recall / kill accuracy / false-promotion rate | Jase | Respective gates | Gates 1–4 |
| D7 | Shadow-mode length and agreement rate | Jase | Shadow mode | Gate 5 / standalone grant |
| D8 | Standalone drift tolerance (rolling calibration check) | Jase | Standalone grant | Ongoing monitoring (§10 of ladder) |
| D9 | Joint-interface spec approval (spec + prototype scope + preservation route) | Jase | Prototype build | Joint-interface prototype |
| D10 | Log-mass scan design and bounds (inventor value ± decades vs fixed grid) | Prototype design | Prototype build | Joint prototype |
| D11 | Regression tolerance for k = 0 reproduction proof | Prototype plan | Prototype acceptance | Joint prototype acceptance |
| D12 | Stage B budget caps (re-confirm after measured cost; current draft: 3 bodies / 5 candidates / 60 min) | Jase (after measurement) | Open-question use of Stage B | Multi-body open questions |
| D13 | Survey-table literature pass (per-survey limits, footprints, verification status) | Research tier (Perplexity / web) | Veto design finalization (v2 §5A gate 2) | Build decision on veto + multi-body fitter |
| D14 | Stage B cost measurement acceptance (measured table vs caps) | Jase | Open-question use of Stage B | Multi-body open questions |
| D15 | Test-partition reservation (untouched partition for final validation) | Design (v2 §5A gate 4) | Build decision | Veto + multi-body build |
| D16 | Ranker minimum coverage fraction for lower-ranked candidates/regions | Jase | Ranker advisory-mode design | Ranker first experiment |
| D17 | Ranker NN-vs-simpler-models margin; advisory duration; drift tolerance | Jase | Ranker promotion test / control | Ranker promotion to control |
| D18 | Ranker build decision (advisory mode only, first experiment) | Jase | Any ranker training | Ranker first experiment |
| D19 | Battery-harness build decision | Jase | Ladder battery execution | Batteries 1–4 |
| D20 | Veto + multi-body fitter build decision (separate, after §5A gates) | Jase | Any multi-body implementation | Multi-body fitter |
| D21 | Conductor-competition build decision (specialist brains, scored answers, tie → abstain) | Jase | Any competition implementation | Conductor competition |
| D22 | Live-ROM synthetic-evidence cleanup (separate 4 synthetic-novel consolidations from decided-case history?) | Jase / Atlas | Standalone adjudication | Clean adjudication record |

## Decided (history — do not remove)

| # | Decision | Date | Record |
|---|---|---|---|
| — | (none yet in this register; prior decisions live in their design docs and notes) | — | — |

## Standing sequence (for reference — this register does not change it)

1. Validation closeout — DONE 2026-10-26 (verdict: STILL CONDITIONAL).
2. Phase 2 fixes — RUNNING (dispatched 2026-10-26).
3. Verify changed source + regression results.
4. Review v2 against the verified implementation and outstanding audit qualifications.
5. Separate build decision for any implementation.
6. Queued improvements afterward (ranker, batteries, competition, identifiability proposals).

## Notes

- D1 is the next decision Jase faces after Phase 2 verification: it gates the
  ladder, and the ladder gates everything discovery-related. It should not be
  decided during a battery run.
- D9 is the next build-approval decision in line: the joint-interface spec is
  drafted and waiting; approving it does not authorize the prototype build
  beyond the bounded scope in that spec.
- D22 is newly surfaced by the validation closeout (note §5): the live ROM now
  mixes synthetic-novel consolidations with decided history. It does not block
  tracking/gating duty, but it should be resolved before standalone
  adjudication.
