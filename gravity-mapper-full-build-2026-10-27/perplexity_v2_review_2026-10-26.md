# Perplexity v2 Downloader Review — 2026-10-26 (late evening)

**Scope of this review:** review only. No code edited, no live ROM
written, no mapper integration, no download to Drive, no upload.
Local copies only, in `hidden_files/perplexity_in/new_2026-10-26/`.

## New material found on Drive (Perplexity Files folder)

Checked live on 2026-10-26 ~22:34 PDT; these three files were NOT in
the local copy as of 22:22:

- `pull_solar_system_rails_v2_draft.py` — 22:23 PDT
- `downloader_v2_entrypoint_tests_2026-10-26.json` — 22:27 PDT
- `downloader_v2_multibody_tests_2026-10-26.json` — 22:33 PDT

## Hash verification (independently recomputed, all match claims)

- v2 draft: `ad6b7b48cda04d73f0d53426c4f97b59af9709ae24ce1f00c28c5b240d6d1a50`
- Base downloader: `e0a085b8bee9cee4da4946f386f2c8091f290c324828b43253a018d57168c185`
- Validator v2 draft: `8bd52d3385d467d6af8d23df3605c2a5ecce98c8c1966a0fcd4616fdd0dbdc80`

All three match the hashes pinned in the v2 draft's DEPENDENCIES
table and in the multibody test record. The base downloader and the
validator are byte-identical to the versions already reviewed — the
v2 change is the new entrypoint file only.

## Reported test results (as reported, NOT independently rerun)

- Entrypoint: 11/11 pass (single Jupiter body, 3 epochs, mocked
  transport, explicit allowlist [1.2]). Cases include actual success,
  cached/fresh wrong target, cached/fresh unknown version, wrong
  signature source, overwrite rejection, duplicate body, nonfinite
  start, required explicit allowlist, valid cache revalidation.
- Multibody routing: 6/6 pass (synthetic trajectories, mocked
  transport, chunk-intervals=2). Cases include default 8 bodies,
  explicit Pluto [9], explicit order [8,3], cache replay, late wrong
  target, late bad signature — the late-error cases assert no final
  outputs are written.

These cannot be independently rerun from the result JSONs alone: no
test harness was supplied. The case lists are consistent with the
v2 code paths (duplicate/nonfinite/overwrite all reach
`parser.error`, i.e. SystemExit 2; wrong target/version reach the
validator's ValueErrors), but consistency is not a rerun.

## Independent checks Atlas DID run (no live HTTP, no live ROM)

Using the saved Jupiter 3-epoch fixture and the validator v2 draft
directly:

- **ACCEPT:** Jupiter Barycenter (5), epochs 2455197.5 / 2455198.0 /
  2455198.5, allowlist [1.2] — 3 rows, columns read from the label
  row: `JDTDB, CALENDAR DATE (TDB), X, Y, Z, VX, VY, VZ`.
- **Fail closed, wrong target (4):** `ValueError: Target identity mismatch`
- **Fail closed, wrong version ([1.3]):** `ValueError: Unapproved API signature version`
- **Fail closed, wrong epoch:** `ValueError: Epoch mismatch`

## Hardening requests from MUSE_TO_PERPLEXITY Rev 1 — status

- (a) Target-ID validation against requested command: **CLOSED in
  validator** (header `Target body name` numeric ID must equal the
  expected ID; centre must be 10).
- (b) Timescale + correction-mode validation, or fail closed:
  **CLOSED in validator** (start/stop must end ` TDB`; output type
  must be `GEOMETRIC cartesian states`; units AU-D; frame Ecliptic
  J2000).
- (c) Header-driven column mapping: **CLOSED in validator** (label
  row must be unique, duplicate-free, and exactly the required set;
  indices are taken from the label row, not fixed positions).
- (d) Signature-version handling: **CLOSED as explicit allowlist**
  (source must be `NASA/JPL Horizons API`; version must be in the
  caller-supplied allowlist; `--allow-api-version` is required).
  The 1.2-vs-1.3 policy question itself remains Jase's (gates board
  §3: version policy, validator mechanism ready, final allowlist
  not yet set).
- (e) Malformed-JSON retry: **STILL OPEN, minor.** The base
  downloader is unchanged, and its `fetch()` only retries HTTP
  429/500/502/503/504 — a successful response with invalid JSON
  still raises out of the retry loop. Not a correctness risk for
  validated data, but the requested retry is not in v2.

## Scope boundaries — respected in v2

- Downloader-only: no mapper, tracker, bucket, ledger, or ROM edits;
  `gm: None` + `gm_status: REQUIRED_BEFORE_DYNAMICAL_USE` retained.
- IDs 1..9 only (planetary barycenters + Pluto system); no
  small-body support, no interpolation, no fitting.
- Overwrite refused when final outputs exist; duplicate bodies
  rejected; span must contain an integer positive number of
  intervals.
- Manifest states its own limits plainly, including: "Draft; not
  production-approved" and "CSV and manifest are individually
  atomic, not a joint transaction" — the joint-transaction test
  remains unclaimed, as in the entrypoint record's limitations.

## Still untested / unlocated (unchanged by v2)

- Eight-body LIVE coverage, full pull, chunk joining at full span.
- GM compatibility, interpolation accuracy.
- The original parameter-check record (11 assertions) — still not
  saved to Drive with a hash, so still Perplexity's report, not
  evidence.
- No production-readiness claim is supported, and none is made here.

## Invariants

- Live ROM `real_data/parent_rom.json` md5 before and after this
  review: `4c77b723ff5770566a85ed4e580aed2c` — unchanged.
- No thresholds, caps, or evaluator defaults changed. No files
  uploaded to Drive by this review (upload awaits a separate tap).

---

*Review, 2026-10-26 late evening, continuation work in the new
Gravity Mapper chat. This file is a review record, not an approval,
not an implementation, and not a scientific claim.*
