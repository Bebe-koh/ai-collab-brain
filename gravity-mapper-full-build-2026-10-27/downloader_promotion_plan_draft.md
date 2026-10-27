# Downloader Promotion Plan — DRAFT, NOT APPROVED

**Status:** Draft plan only. Promotion of Perplexity's downloader into the
mapper's working source is **not approved** by this document. Each stage
below ends at a gate; advancing past a gate needs Jase's explicit word
in his own words. A bare "continue" is not approval for any gated item.

**Drafted:** 2026-10-27, on Jase's tap "Draft the downloader promotion plan".
**Subject:** Perplexity's Solar System downloader, v2.1 draft track.
**Owner split (standing workflow):** Perplexity owns the downloader;
Atlas owns audit/verification; only Jase decides promotion. Review never
edits the other's files and never approves anything.

## What promotion would mean — and would not mean

Promotion means: the downloader (plus its validator and test suites) is
accepted as a **working source in the mapper's workspace**, its files
moved from Perplexity's folder into the main folder, with hashes and
version recorded.

Promotion does **not** mean: validated science, a production claim, a
live-ROM write, a threshold or evaluator-default change, a Mac-project
merge, or permission for any new orbit fit. The current REBOUND-based
rails builder (`rails_brain.py`) stays as the fallback; promotion adds a
source, it does not delete the existing one.

## Promotion baseline (verified 2026-10-27 ~01:10 PDT)

All files in the top-level gravity-mapper folder's Perplexity Files
folder (`1uIVI1wf-_IhQcb07Np8cQVrfh0uMC7AH`). Atlas independently
re-ran the recovery suite offline: **12/12 pass**, all hashes below
match the results file exactly.

| File | Drive ID | SHA-256 (first 16) | Size |
|---|---|---|---|
| `pull_solar_system_rails.py` (v1) | `1d7QM8j7LmiHh37yQr_pc0VeLm6MLvGqZ` | `e0a085b8bee9cee…` | 13,238 |
| `horizons_response_validator_v2_draft.py` | `19pcyQ4_IfzQEufZP6Fm31wVmiOG3hGZJ` | `8bd52d3385d467d6…` | 5,310 |
| `pull_solar_system_rails_v21_draft.py` | `1NqDMsecCfZmuc71KbxWYm2RW3ahLDo3n` | `6459fdc4f3c4d24…` | 9,611 |
| `test_downloader_v21_recovery.py` | `1ZuPjx__X_fG7OyjMtVyKdh-tQsgnIV4H` | `4b2a6dc6b53e56a28…` | 9,441 |
| `downloader_v21_recovery_results_2026-10-26.json` | `1vDDIBJB0xLh3ykSQ41nRj2YwLhOjciEO` | schema `v21_recovery_regression_v1`, 12/12 | 3,264 |

Verified already closed: target-ID enforcement (header-parsed, must
equal requested 1–9), label-driven columns (rejects duplicates,
unrecognized layouts, row-width mismatch, non-finite values, epoch
mismatch), TDB suffix, GEOMETRIC mode, AU-D units, explicit API-version
allowlist, staged publication with checksum/schema/row-count checks,
transport-error reject-and-resume (400/503/timeout, overlap
disagreement, cache tampering).

Known gaps at baseline (from the draft's own limitations plus audit):
GM is `None` (`REQUIRED_BEFORE_DYNAMICAL_USE`); no interpolation
validation; no full live-HTTP pull; single-process only; power-loss
behavior unvalidated; planetary barycenters 1–9 only (no small bodies).

Reference the promoted rails must eventually stand against:
`rails_brain.py` — Sun + 8 planets at J2000 from JPL Table 1, REBOUND
ias15, CubicSplines on a 0.5-day grid, validated <1e-6 AU vs REBOUND
over 21 yr. The mapper consumes rails through `positions(t)` plus
`t_min`/`t_max` and a provenance fingerprint (the ledger's model
identity hashes rails provenance — see correctness batch finding A).

## Stage 1 — Close the functional gaps (Perplexity's track)

**Entry:** this plan exists. **Owner:** Perplexity. **Gate:** Jase
commissions Stage 1; Atlas reviews on delivery, approves nothing.

1. **GM per body.** Horizons vector responses do not carry GM, so the
   source must be named explicitly (e.g. JPL Table 1 / DE441 constants)
   and each value validated against an independent reference — never
   invented, never copied silently from an unpinned source. The
   manifest's `gm_status` must flip from `REQUIRED_BEFORE_DYNAMICAL_USE`
   to a stated, sourced value per body, or the body stays excluded.
2. **Interpolation validation.** Name the interpolator, the sampling
   step, and the error tolerance. The bar to beat is the current rails'
   <1e-6 AU vs REBOUND over 21 yr. Measure interpolation error against
   direct Horizons queries at off-grid epochs; report max error per
   body, not just RMS.
3. **Bounded live-HTTP pull.** Scope must be stated before it runs:
   bodies (8 planets + Pluto?), span, step, chunking. Raw responses
   preserved with hashes alongside the published dataset — a pull whose
   raw responses are not preserved is not a verifiable pull. No full
   production pull happens inside this stage without a separate scope
   approval.
4. **Small bodies stay out.** The 1–9 exclusion is a scope limit, not a
   defect to fix inside this promotion. A small-body convention (the
   asteroid-number vs major-body-ID question from Rev 2) is a separate
   track if Jase ever commissions it.

**Exit criterion:** a new versioned draft (not an overwrite of v2.1)
with GM sourced, interpolation measured, and a bounded live pull
preserved — plus updated tests covering each new claim.

## Stage 2 — Independent verification (Atlas's track)

**Entry:** Stage 1 delivery lands in Perplexity's folder. **Owner:**
Atlas (audit only, workspace copy, read-only on Perplexity's files).
**Gate:** Jase commissions the verification; results are reported,
not approved, by Atlas.

1. Re-run every suite on the VM (as was done for recovery 12/12),
   including any new Stage 1 tests, and confirm hashes match the
   delivery's own record.
2. Independent live spot-check: query Horizons directly for one body
   at epochs the pull claims, and compare positions — an independent
   query, not a re-read of the delivered CSV.
3. Cross-check against the current rails: compare Horizons-pulled
   positions against `rails_brain.py`'s JPL Table 1 rails over the same
   span. Differences must be **explained** (different ephemeris
   version? different center? different epoch handling?) — "small"
   without an explanation is not a pass.
4. Re-verify the validator fails closed on the same adversarial cases
   (wrong target, wrong version, wrong epoch, reordered columns,
   malformed layout).

**Exit criterion:** a verification note stating, per claim, verified /
not verified / failed — with numbers, not adjectives.

## Stage 3 — Interface adaptation (Atlas's workspace copy only)

**Entry:** Stage 2 verification is clean. **Owner:** Atlas, in Atlas's
own workspace copy, labeled Atlas-authored — never presented as
project-side shipped code. **Gate:** Jase commissions the adapter;
this stage writes code, so it needs explicit commission, not just
plan approval.

1. An adapter from the published dataset (`solar_system_vectors.csv` +
   `manifest.json`) to the rails interface the mapper consumes:
   `positions(t)`, `t_min`/`t_max`, and a provenance fingerprint the
   ledger can hash (rails source, span, step, GM source, dataset hash).
2. The adapter must fail closed on a dataset whose manifest hash,
   CSV checksum, or row count does not match — the same discipline as
   the staged publication itself.
3. No changes to the mapper's fitter, verdict, thresholds, or
   evaluator default inside this stage. The adapter is a source plug,
   not a behavior change.

**Exit criterion:** adapter code + a smoke test (positions at known
epochs match the dataset within rounding) in the workspace copy.

## Stage 4 — Side-by-side validation (the promotion gate)

**Entry:** Stage 3 adapter exists. **Owner:** Atlas (runs), Jase
(judges). **Gate:** Jase names the exact validation cases before they
run; cases are not chosen after seeing results.

1. Run the same mapper checks twice: once on the current REBOUND
   rails, once on the Horizons-pulled rails through the adapter.
   Proposed case set (Jase to confirm or replace): the fitter
   validation cases (Mercury, heavy, null) and at least one
   holdout-gated verdict case.
2. Pass bar, predeclared: identical verdicts on every case, and
   fitted parameters agreeing within tolerances stated before the run
   (tolerances to be set by Jase, not by whoever runs the cases).
3. No threshold, gate, or evaluator change may be made to achieve a
   pass. If a case fails, the failure is reported and the promotion
   stops — the gate is not redefined around the result.

**Exit criterion:** a side-by-side record with per-case verdicts and
parameter deltas, plus Jase's explicit promotion decision.

## Stage 5 — Promotion (Jase's tap only)

**Entry:** Stage 4 record is clean and Jase taps promotion. **Owner:**
Atlas executes the move; Perplexity is told via the collaboration
markdown (Atlas tells Perplexity, per the standing workflow — Jase
does not relay).

1. Move the versioned draft + validator + suites from Perplexity's
   folder into the main folder (full-build folder, delta-only per the
   standing rule — never a whole-set re-upload).
2. Record file IDs, hashes, version, and the Stage 4 record in the
   project notes; update the collaboration markdown so Perplexity can
   check what changed.
3. Keep the REBOUND rails builder in place as fallback. The promoted
   downloader becomes an available source, not the only source.

**Exit criterion:** files in the main folder, hashes recorded, fallback
intact, collaboration markdown updated.

## Open questions (answered by Jase, not assumed)

1. **GM source.** Which reference supplies GM, and who validates it?
2. **Live-pull runner.** Perplexity's sandbox has no network (live HTTP
   only via its web-fetch tool); the VM has network. Who runs the
   bounded live pull — Perplexity, Atlas, or Jase's machine?
3. **Stage 4 case set and tolerances.** Which cases, which agreement
   tolerances? Set before the runs, not after.
4. **Span and step.** What time span and sampling step does the first
   promoted dataset cover? (The v2.1 defaults are 2455197.5–2460676.5
   at 720 minutes — adopted only if Jase says so.)

## Explicitly out of scope

Live-ROM writes; threshold, gate, or evaluator-default changes; any new
orbit fit or discovery claim; small-body support; Mac-project merge;
production or validated-science language; deleting or replacing the
current rails builder; regenerating existing data (e.g. `tno_vectors.csv`)
to settle wording disputes.

## Decision record

- 2026-10-27: plan drafted on Jase's tap. Promotion NOT approved.
- Stage 1: not commissioned.
- Stage 2: not commissioned.
- Stage 3: not commissioned.
- Stage 4: cases and tolerances not set.
- Stage 5: not approved.
