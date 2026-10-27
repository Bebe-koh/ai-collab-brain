# Supplement: Perplexity's Assembly Test (2026-10-26, late evening)

**Supplement to** `perplexity_new_material_review_2026-10-26.md` (Rev 8)
and `perplexity_real_response_supplement_2026-10-26.md` (Rev 9).
**Reviewer:** Muse (Atlas). **Method:** read-only audit of the
evidence record + consistency checks against verified values. The
assembly harness itself is NOT a Drive file, so Atlas cannot re-run
it — this review verifies the record's internal consistency and its
agreement with independently verified values, not the harness
execution. Drive original untouched. Advisory only — approves nothing,
decides nothing.

## File

- `downloader_assembly_evidence_2026-10-26.json` (Drive ID
  `1fsLCBWAeNo7lvDdywDCC7lo2rPGXu_yG`, Drive size 3,720 B; Atlas
  stdout-capture mirror SHA-256
  `effd9490bc233e7ad406744c5f642a0b6fae2c374e8ab35735bda69a6453f719`
  — same JSON re-serialization caveat as Rev 9: mirror hash is not
  byte-verification against Drive).

## What it is (and what it is not)

**Status in the record itself: `NEW_HARNESS_ONLY_ASSEMBLY_TEST`.**
Original downloader `main()` with a runtime-only single-Jupiter
inventory, plus a `parse_vectors` bridge to the separate validator
draft. urllib transport mocked with the preserved real payload or
explicitly derived two-chunk fixtures. Source files unchanged
(`source_unchanged: true`; downloader hash `e0a085…` and validator
hash `8bd52d33…f0dbdc80` both match Atlas's verified values).

**This is the first INTEGRATED test** — downloader + validator
together, where Rev 8's tests were separate components. It is NOT
production wiring: the record states plainly that the bridge
"supplies signature from trusted fixture; not production wiring."
That distinction is the whole story of this batch: assembly works in
harness; the production signature path is still open.

## Cases (6/6 pass) — what each one proves

1. **completed_output_overwrite_rejected** (exit code 2, 0 mock
   calls) — overwrite protection holds inside the assembly, not just
   in the unit tests. No network call is made when outputs exist.
2. **real_single_chunk** — 1 request (2455197.5→2455198.5), checks:
   outcome, request count, `gm_still_unset` (manifest GM discipline
   holds through assembly), manifest CSV hash, three unique epochs,
   time origin, velocity conversion. The time/velocity conversions
   are the verified ones (JD−2451545.0)/365.25 and AU-D ×365.25.
3. **derived_two_chunks** — 2 requests sharing endpoint 2455198.0;
   same checks; **same CSV hash as the single chunk
   (`1e1b8b5d…`)** with 2 cache entries vs 1 and 3 total rows in
   both. Chunk joining with overlap dedup produces output identical
   to the single-chunk pull. (On derived fixtures — see limits.)
4. **overlap_disagreement** — second-chunk X perturbed by 1e-6 AU
   (4.510651577295796 → 4.510652577295796) → rejected with
   "Overlapping chunk states disagree", no final outputs. Consistent
   with the downloader's 1e-12 AU overlap-agreement rule: a 1e-6
   disagreement MUST reject, and did.
5. **wrong_target_second_chunk** — Saturn (6) in the second chunk →
   "Target identity mismatch" from the validator bridge, no final
   outputs. The validator catches a body swap INSIDE the assembly,
   not just standalone — this is the gap (a) failure mode, closed in
   the integrated path.
6. **wrong_epoch_second_chunk** — epoch 2455198.1 for 2455198.0 →
   "Epoch mismatch", no final outputs.

**Derivation method (explicit, reproducible in principle):** retain
original header/footer, filter vector rows to the requested inclusive
JD interval, replace both start/stop TDB strings with DERIVED FIXTURE
TDB; second-chunk-only perturbations as listed above. Derived
fixtures are labeled derived, not separately acquired responses.

**Honest scoping (good):** "Reproducible cached response copies and
temporary-path manifests are excluded from this compact durable
record. The longer run snapshot is attached in chat and is not
claimed durably saved." A chat-attached snapshot is correctly NOT
claimed as durable evidence.

## Updated unproven list (Rev 8 §5 → Rev 9 → now)

- CLOSED by this batch: chunk joining (derived fixtures, identical
  CSV hash single vs two-chunk); validator operating inside the
  assembly path (target/epoch/overlap failures all fail closed with
  no final outputs); overwrite protection in assembly.
- STILL OPEN: **production validator/signature wiring** (the bridge
  supplies signature from trusted fixture — the live response path
  must carry its own signature through, untrusted, and the validator
  must check it there); live network; 8-body coverage / full pull;
  final version policy (Jase's word; test allowlist still ["1.2"]);
  small-body identity conventions; GM compatibility; interpolation
  accuracy; original parameter-check record (still unlocated).
- What would close the next items: the same assembly test with the
  bridge replaced by production signature wiring on a live pull; then
  8-body coverage; then the stated version policy — each preserved
  with hashes, as this batch was.

---

*Supplement, 2026-10-26, continuation work (mutual-review-always-on).
Perplexity's files remain Perplexity's; promotion to the main folder
requires maturity + Jase's approval, per the collab rules.*
