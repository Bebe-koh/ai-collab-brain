# Review: Perplexity's New Downloader-Track Material (2026-10-26, evening)

**Reviewer:** Muse (Atlas). **Method:** read-only audit + independent
execution. Drive originals untouched; mirrors in
`hidden_files/perplexity_in/new_2026-10-26/` (audit mirrors only).
**Status of reviewed material:** DRAFT + OFFLINE TESTS. Not installed,
not integrated, not production validation. This review is advisory
only — it approves nothing and decides nothing.

## Files read (Drive IDs, retrieved bytes, SHA-256 of mirror)

| File | Drive ID | Mirror SHA-256 |
|---|---|---|
| `horizons_response_validator_v2_draft.py` (5,310 B) | `19pcyQ4_IfzQEufZP6Fm31wVmiOG3hGZJ` | `8bd52d33…f0dbdc80` |
| `downloader_parser_baseline_2026-10-26.json` (2,032 B) | `19-N42kYmla5Jgb_MOqPBWM-ByZz9oJSJ` | `0c16b9a5…38cc635e4` |
| `validator_v2_offline_results_2026-10-26.json` (4,548 B) | `1TlaTtNJLzmdWG_VJeb_zSsT7nKkelNem` | `2d9ba7e3…74c97f97d` |
| `downloader_transport_cache_tests_2026-10-26.json` (2,815 B) | `1OGyD6L4lSwlY9P12VRkEzcjEu6lzQZFC` | `2644efac…69d9f535` |

Retrieval note: the three JSON files' bytes arrived via the CLI's
stdout, not its `--output` file (first `--output` attempts wrote 0
bytes; stdout capture wrote the full content). The `.py` arrived
normally. Mirror hashes above are Atlas's hashes of the retrieved
bytes.

## Headline

**The validator draft closes all five baseline failures in offline
tests, and Atlas independently reproduced the decisive cases.**
Perplexity's own baseline (4/9) confirms Atlas's earlier audit
exactly, including the silent X/Y swap on reordered columns. The
validator (15/15) fixes every one of those failures, and the
transport/cache mocks (11/11) match the agreed retry/cache discipline.
What is NOT shown: live-response compatibility, integration, chunk
joining, full download, version policy, or small-body identity. The
material is a genuine step on Perplexity's track, still far from
promotion.

## 1. Baseline (4/9) — confirms Atlas's audit, honestly labeled

- Failures: wrong_target ACCEPTED, wrong_timescale ACCEPTED,
  wrong_correction ACCEPTED, duplicate_column_label ACCEPTED,
  reordered_columns SILENT X/Y SWAP (first returned XYZ [2,1,3]).
  These are exactly Atlas's gaps (a), (b), (c) from the Rev 1 audit.
- Passes: valid_control, wrong_origin, missing_epoch,
  nonfinite_coordinate — consistent with the old parser (origin,
  frame, units + epoch-count checks only).
- Discipline (good): status `NEW_OFFLINE_BASELINE_TEST_NOT_A_FIX`;
  fixture labeled "New synthetic parser fixture, not a Horizons
  response"; scope "No network, no source edits, no fits, no ROM
  access"; `source_sha256` = `e0a085…` = the downloader hash Atlas
  verified; `source_unchanged: true`.
- `prior_record_recovery`: "Prior parameter-check JSON not located in
  searched Drive sources; this record is a different newly executed
  test, not a reconstruction." Correct discipline per the Rev 2
  agreement (locate originals, never recreate). The preservation gap
  on Perplexity's side remains OPEN in the sense that the original
  record is still unlocated — this new record does not fill it, and
  does not claim to.

## 2. Validator v2 draft — the five treatments, checked in source

Read in full (5,310 bytes). Docstring: "Draft planetary Horizons
response validator; not installed or tested. Separate from
pull_solar_system_rails.py. Supports explicit major-body system
barycenter IDs 1..9 only; small-body identity handling is excluded.
The caller must supply a reviewed API version allowlist."

- **(1) Target identity: COVERED for major bodies.** `expected_target_id`
  must be int 1..9; `body_id()` parses the numeric ID from
  "Target body name: … (N)" and "Center body name: … (N)"; center
  must be exactly 10. Wrong target → "Target identity mismatch";
  wrong center → "Center identity mismatch". Small-body IDs are
  EXPLICITLY excluded (documented) — the agreed "separate ID
  conventions" for small bodies are still unwritten. Not a failure of
  this draft; a boundary of it.
- **(2) Time/corrections: COVERED.** Start/Stop time lines must each
  appear exactly once and end with " TDB"; "Output type" must be
  exactly "GEOMETRIC cartesian states"; units must be "AU-D"; frame
  must be "Ecliptic of J2000.0" or "Ecliptic of J2000".
- **(3) Columns: COVERED, label-driven.** Exactly one JDTDB label row;
  duplicates/empty rejected; label set must equal exactly {JDTDB,
  Calendar Date (TDB), X, Y, Z, VX, VY, VZ}; indices taken from labels
  (never fixed positions); row width must match labels; values
  float-parsed with D→E conversion and required finite; epoch count
  exact; each record epoch within 1e-8 days of its expected epoch
  (tolerance capped at 1e-8).
- **(4) Versions: MECHANISM covered, POLICY still open.** Signature
  source must equal "NASA/JPL Horizons API"; version must be in the
  caller-supplied nonempty allowlist; empty allowlist rejected. The
  draft sets NO policy itself — correct. The test allowlist ["1.2"]
  is labeled `test_only_api_allowlist`. Final policy still needs
  Jase's word (live response carries 1.2; documentation claims 1.3).
- **(5) Malformed JSON: OUTSIDE this component.** The validator takes
  a parsed dict payload; JSON parsing is the caller's job. The draft
  does not claim otherwise. The transport tests cover the safe-stop
  half (see §4); bounded retries for malformed responses are NOT
  implemented (stated in limitations — acceptable: the agreement was
  that bounded retries are "acceptable", not mandatory).
- **Nits (not failures):** (i) a dead loop iteration — `for key in
  ("Start time", "Stop  time", "Stop time")` with `continue` on
  "Stop  time" — harmless; the `Stop\s+time` pattern already matches
  multi-space, and the `realistic_stop_spacing` test shows the intent
  (tolerate "Stop  time      :"). (ii) Frame leniency: accepting
  "Ecliptic of J2000" alongside "Ecliptic of J2000.0" is a spelling
  leniency for the same frame, not a different frame slipping through
  — defensible, noted. (iii) Calendar-date column VALUES are not
  checked (labels only) — epochs are the authority; fine.

## 3. Validator results (15/15) — independently reproduced on decisive cases

Perplexity's record: all 9 baseline cases now pass in the validator
(reordered_columns accepts AND preserves XYZ [1,2,3] — the label
mapping works), plus blank_header_lines, realistic_stop_spacing,
missing_target_header, unknown_api_version (9.9 rejected under
allowlist ["1.2"]), wrong_signature_source, empty_allowlist.
`payload_unchanged: true` throughout (validator does not mutate
input). Fixture = exact synthetic fixture from the baseline upload;
no live HTTP. Scope: "Offline validator component only; no source
edits, downloader integration, network, fits, or ROM access."

**Atlas's independent check (stronger than read-through):** Atlas ran
the retrieved validator draft locally (sandbox, no network, no project
state) against the same synthetic fixture on 11 decisive cases —
valid_control, wrong_target, wrong_timescale, wrong_correction,
wrong_origin, duplicate_label, reordered_columns, unknown_version,
wrong_source, empty_allowlist, missing_epoch. **All 11 outcomes match
Perplexity's recorded outcomes exactly**, including the two subtle
ones: reordered_columns ACCEPTS with XYZ preserved [1.0, 2.0, 3.0],
and wrong_timescale REJECTS. Perplexity's 15/15 is corroborated at
the execution level for the decisive cases.

**Atlas also closes one of Perplexity's own caveats:** the results
file states "Not independent byte-for-byte Drive verification" for
its source restoration. Atlas's independently retrieved validator file
hashes to `8bd52d33…f0dbdc80`, EXACTLY the `validator_sha256` in the
results record. The file on Drive is the file that was tested.

## 4. Transport/cache tests (11/11, mocked) — matches agreed discipline

Method: unchanged `fetch()` with urlopen mocked (BytesIO JSON /
HTTPError / URLError), sleep replaced by a recorder, isolated temp
cache dirs, retries=2. Parameters match Atlas's verified builder
config (COMMAND '5', CENTER '500@10', VECTORS, TDB, AU-D, ICRF /
ECLIPTIC, VEC_TABLE 2, VEC_CORR NONE, STEP '720 m').

- fresh_fetch (1 call), cache_hit_no_network (0 calls),
  cache_result_corruption_rejected, cache_parameter_mismatch_rejected
  (parameter+result-hash validation on hit, as designed).
- 429 → success with Retry-After=7 honored (sleeps [0,7,0]); 503 →
  success; URLError → success; 400 no retry; retry_exhaustion (3
  calls, backoff [0,5,0,10,0]).
- malformed_json_safe_stop (JSONDecodeError, 1 call, no retry — safe
  stopping, retries not implemented, stated); semantic_api_error_no_retry.
- Limitations stated honestly: no live network; no live-response
  compatibility test of the new validator; no integrated
  validator/cache test; no chunk joining or full download; cache
  wrapper signature metadata integrity not tested.

## 5. What remains unproven (nothing here changes these)

1. Live-response compatibility of the NEW validator (a real Horizons
   JSON response through `parse_response`, not the synthetic fixture).
2. Integration: validator wired into the downloader's fetch/cache path
   (currently separate components tested separately).
3. Chunk joining at full span + full download + 8-body live coverage
   (unchanged from the Rev 1 audit).
4. Version policy (final allowlist — Jase's word, not the test's
   ["1.2"]).
5. Small-body identity conventions (explicitly excluded from this draft).
6. GM compatibility + interpolation accuracy (unchanged).
7. The original parameter-check record: still unlocated on
   Perplexity's side; this batch correctly does not reconstruct it.

**What would change the conclusion:** a live-response test (real
Horizons JSON → validator accept with correct XYZ), an integrated
validator+cache test, the stated version policy, and a small-body ID
convention — each preserved with hashes, as this batch was.

## 6. Standing flag (unchanged by this batch)

This batch is Perplexity's own track (validator) and shows no reliance
on the inventory claim — but it also shows no awareness of Rev 6's
correction. The Rev 6/7 check prompt to Perplexity is STILL worth
sending: Rev 6 corrects a claim (planetary retrieval) that future
Perplexity work could otherwise rely on.

---

*Review, 2026-10-26, continuation work (mutual-review-always-on).
Advisory only. Drive originals untouched. Perplexity's files remain
Perplexity's; promotion to the main folder requires maturity +
Jase's approval, per the collab rules.*
