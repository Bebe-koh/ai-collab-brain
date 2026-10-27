# Perplexity v2.1 Downloader Review — 2026-10-27 (early morning)

**Scope of this review:** review only. No code edited, no live ROM
written, no mapper integration, no download to Drive, no upload.
Local copies only, in
`hidden_files/perplexity_in/new_2026-10-27/`.

## New material found on Drive (live Perplexity Files folder)

Checked live 2026-10-27 ~01:55 PDT; seven files new since the
2026-10-26 v2 review (timestamps UTC 2026-10-27 05:33–08:24):

- `pull_solar_system_rails_v21_draft.py` — 05:44 UTC
- `downloader_publication_failure_tests_2026-10-26.json` — 05:36 UTC
  (v2 publication failure, preserved)
- `downloader_v21_publication_tests_2026-10-26.json` — 05:57 UTC
- `downloader_v21_routing_signature_tests_2026-10-26.json` — 06:07 UTC
- `test_downloader_v21_recovery.py` — 06:23 UTC (executable runner)
- `downloader_v21_recovery_results_2026-10-26.json` — 06:29 UTC
- `DOWNLOADER_V21_CONTINUITY_AND_COMPATIBILITY_r1.md` — 08:24 UTC

## What changed from v2 to v2.1 (diff checked)

Only the entrypoint changed; the pinned dependencies are
byte-identical (base downloader, validator v2 draft). The change is
staged dataset publication, `publish_dataset()`:

- CSV + manifest are written to a `.dataset-stage-*` temp directory,
  checksum / schema / row-count verified there, then committed by a
  same-filesystem directory rename to `dataset/`.
- On any handled failure the stage directory is removed; readers must
  ignore `.dataset-stage-*` directories.
- Raw cache stays in the output parent; manifest cache paths resolve
  relative to the dataset's parent, not the dataset itself.
- Committed dataset overwrite is refused; the legacy flat layout
  (CSV + manifest beside the output) is NOT migrated.
- Single-process only; power-loss safety explicitly NOT validated.

This closes the v2 joint-transaction gap (CSV and manifest were
individually atomic, not jointly committed) for the normal and
injected-failure paths tested — not for power loss or concurrent
writers, which are explicitly unclaimed.

## Hash verification (independently recomputed, all match claims)

- v2.1 draft: `6459fdc4f3c4d24faa8c2c462f8f732c28c779d1b8db805a8824c70df6287acf`
- Recovery runner: `4b2a6dc6b53e56a28026f18ff59ca44ed5fa20eb2102afc4847da2c547581917`
- Base downloader: `e0a085b8bee9cee4da4946f386f2c8091f290c324828b43253a018d57168c185`
- Validator v2 draft: `8bd52d3385d467d6af8d23df3605c2a5ecce98c8c1966a0fcd4616fdd0dbdc80`

One hash NOT reproduced: the continuity doc's recorded SHA for the
preserved Jupiter response (`4b5e…`) does not match any obvious
variant of the local Jupiter fixture file (whole file, result only,
result+signature in two formats). The local fixture's *content* was
already validator-checked on 2026-10-26 (3 rows accepted, fail-closed
on wrong target/version/epoch), so this is recorded as an
unreproduced provenance hash, not as evidence of tampering and not
as a v2.1 failure. Perplexity's note that "independently retrieved
remote bytes have not been hash-compared by Perplexity" is consistent
with that caution.

## Reported test results (as reported, except recovery — see below)

- **Publication (v2.1): 9/9.** Success control, CSV/manifest/
  directory-commit injected failures with cache retry, committed
  overwrite rejection, legacy layout not migrated. Limitations:
  no power-loss or abrupt-kill test, no concurrent-writer claim,
  no live HTTP, no eight-body rerun in this batch, no mapper
  integration.
- **Routing/signature regression (v2.1): 17/17.** Prior 6 routing +
  11 entrypoint cases rerun on native v2.1 main with dependencies
  unchanged, mocked transport. Limitations: no live HTTP, synthetic
  eight-body trajectories, no full pull, GM, interpolation,
  concurrency, or power-loss validation.
- **Publication failure (v2, historical): 2/4.** Success control
  and retry-after-partial-manifest pass; CSV-replace and
  manifest-replace injected failures fail. Perplexity preserves
  this as a historical failure, explicitly not reinterpreted as a
  pass — that discipline is correct and is kept here.
- **Recovery (v2.1): 12/12 as reported** — six rejection/resume
  pairs: HTTP 400, HTTP 503 exhausted, timeout exhausted, overlap
  disagreement, cache content mismatch, cache parameter mismatch.
  Limitations: synthetic inputs, zero-retry exhaustion only, no
  power-loss/abrupt-kill/concurrency testing. Bad final cache
  entries were explicitly removed by the test harness before retry:
  that is NOT automatic repair, and must not be described as such.

## Independent check Atlas DID run: recovery 12/12 reproduced

Unlike the v2 routing/publication records, the recovery runner IS
an executable harness, so Atlas ran it directly (stdlib only,
mocked transport, temp directories, hash-pinned sources copied to a
scratch directory):

- **Atlas rerun: 12/12 passed, source_unchanged True, exit 0.**
- Case list identical to Perplexity's record, in the same order.
- Python differs only by patch version (Atlas 3.12.3 vs reported
  3.12.8); pass counts and cases are identical.
- Rerun report saved alongside the Perplexity files as
  `atlas_v21_recovery_rerun.json` (temp-directory paths inside it
  differ by run, as expected).

Routing/publication records were NOT independently rerun: their
harness sources are not identified as preserved in the continuity
doc (only methods are retained), so those numbers remain
Perplexity-reported, not Atlas-verified — same distinction as the
v2 review.

## Continuity / compatibility finding (Perplexity's, read-only)

Perplexity inspected legacy `pull_40yr.py` (readable source only;
its CSV bytes were unavailable in its sandbox, so no residuals or
hashes were computed and no data was regenerated):

- Legacy requests planet *centers* 199/299/399/499/599/699/799/899;
  v2.1 requests system *barycenters* 1..8. Positions and mass
  inventories are NOT interchangeable.
- Legacy JD0 = 2451544.5 vs v2.1 time_j2000 = (JD − 2451545.0)/365.25:
  compare reconstructed absolute JDs, not equally named year fields.
- Legacy comment calls JD0 UTC, but the request does not explicitly
  set TIME_TYPE — do not infer a verified response time scale from
  that comment.
- Legacy fields are object_id/time_years/x/y/z/mass_solar; v2.1
  carries explicit command/JD/velocity fields but gm=None with
  gm_status=REQUIRED_BEFORE_DYNAMICAL_USE. A blind CSV replacement
  is unsafe.
- Earth–Moon barycenter vs separate Moon contribution: double
  counting is an integration hazard to investigate, NOT an observed
  runtime bug.

Perplexity's proposed next bounded action is sound as stated:
inspect the existing rail consumer and its Earth/Moon mass
convention read-only, then establish a matched-target/epoch
comparison case, reporting NOT COMPARABLE where identities cannot
be matched rather than inventing a tolerance. No shared edits,
production pull, arbitrary interpolation, threshold changes, or
live ROM writes are included in that action.

## Still open (unchanged by v2.1)

- Malformed-JSON retry (base downloader unchanged, so the v2
  finding stands: a successful response with invalid JSON still
  raises out of the retry loop).
- GM matching per body from a named, validated source.
- Interpolation accuracy against the current rails' bar.
- Original parameter-check record (11 assertions) — Perplexity
  states the unrecovered artifacts are not dependencies of the
  v2.1 tests; the record itself remains unlocated, so its
  assertions remain Perplexity's report, not evidence.
- Eight-body live coverage, full pull, power-loss, concurrency.
- No mapper integration, no fits, no production readiness claim —
  none is made here either.

## Invariants

- Live ROM `real_data/parent_rom.json` md5 before and after this
  review: `4c77b723ff5770566a85ed4e580aed2c` — unchanged.
- No thresholds, caps, or evaluator defaults changed. No files
  uploaded to Drive by this review (upload awaits a separate tap).

---

*Review, 2026-10-27 early morning, continuation work in the Gravity
Mapper chat. This file is a review record, not an approval, not an
implementation, and not a scientific claim.*
