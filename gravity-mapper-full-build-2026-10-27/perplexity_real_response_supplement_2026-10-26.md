# Supplement: Perplexity's Real-Response Validator Test (2026-10-26, late evening)

**Supplement to** `perplexity_new_material_review_2026-10-26.md` (Rev 8).
**Reviewer:** Muse (Atlas). **Method:** read-only audit + independent
execution. Drive originals untouched. Advisory only — approves nothing,
decides nothing.

## Files

| File | Drive ID | Drive size | Atlas mirror SHA-256 (see retrieval note) |
|---|---|---|---|
| `jupiter_3epoch_horizons_response_2026-10-26.json` | `1TTt3yIRHauVAPEZFm3AHf7HvVK7xPNQ3` | 5,505 B | `ecc41fc9…cc57` |
| `validator_real_response_results_2026-10-26.json` | `1qw1BssBkg72Vd3x06HcSKS2qZ9CidQ9R` | 1,475 B | `c44c5dfc…696` |

**Retrieval note (tool limitation, not a finding against the files):**
for JSON files this CLI writes 0 bytes to `--output` and prints the
content to stdout, apparently re-serialized (Atlas's mirror of the
response file is 5,654 bytes vs Drive's 5,505). Mirror hashes above are
therefore hashes of Atlas's re-serialized copies, NOT byte-verification
against Drive. Content-level verification below is unaffected; byte-level
hash verification of JSON files via this CLI is not achievable, and no
claim about it is made either way.

## What Perplexity reports

- Status `PASS`: "Preserved real Horizons response against unchanged
  validator draft." Validator SHA-256 `8bd52d33…f0dbdc80` (same draft
  as Rev 8). Test-only allowlist ["1.2"]. Scope: "One preserved Jupiter
  response; no integration, no full pull, no fits, no ROM access."
- Rows: 3 epochs (2455197.5, 2455198.0, 2455198.5), target 5, center 10,
  signature NASA/JPL Horizons API 1.2, exact expected label set,
  `payload_unchanged: true`.
- Provenance (candid): "Exact approved full-response upload text
  restored locally after staged fixture was unavailable in execution
  filesystem. Not a fresh HTTP call or independently verified original
  HTTP bytes." Perplexity does NOT claim this test run was a fresh
  HTTP call. The preserved response itself carries a real Horizons
  header (DE441, TDB, GEOMETRIC, Ecliptic of J2000.0, AU-D, 720-minute
  steps) — including the genuine Horizons formatting quirk the
  validator tolerates: `Stop  time` with two spaces, which is why the
  draft's `Stop\s+time` pattern and the realistic_stop_spacing test
  exist.

## What Atlas verified independently

1. **Validator accepts the retrieved real response text.** Atlas ran
   the retrieved validator draft locally (sandbox, no network, no
   project state) on the retrieved response's `result` text with
   target 5, epochs [2455197.5, 2455198.0, 2455198.5], allowlist
   ("1.2",). Result: ACCEPT, 3 rows, target 5, center 10, exact label
   set — matching Perplexity's recorded PASS.
2. **Row 1 matches Atlas's own independent live retrieval
   digit-for-digit.** Atlas's earlier live 3-epoch Jupiter request
   (through the downloader's own transport, temp cache only) returned
   first row [2455197.5, 4.509064428733514, -2.16648147341248,
   -0.09190938984133282, 0.003176963098595231, 0.007166934873994769,
   -0.0001008519307674657]. Perplexity's preserved response row 1 is
   IDENTICAL, value for value. This is cross-confirmation from two
   independent retrievals of the same request (same body, same epochs,
   same step): the preserved response is consistent with a real
   Horizons response, not a fabrication. (Atlas's record holds only
   row 1, so rows 2–3 are confirmed by the validator run, not by
   Atlas's own retrieval.)
3. **What is NOT established:** byte-identity of the Drive file
   (retrieval note above); that Perplexity's test run itself used a
   fresh HTTP call (Perplexity explicitly says it did not — it used
   restored text); anything beyond one Jupiter response (no 8-body
   coverage, no chunk joining, no integration, no version policy,
   no small-body IDs — all still open).

## Updated unproven list (Rev 8 §5, revised by this supplement)

- CLOSED by this supplement: live-response compatibility of the new
  validator for one major-body case (Jupiter, 3 epochs) — at the
  content level, with the row-1 cross-confirmation above.
- STILL OPEN: validator+downloader integration; chunk joining / full
  download / 8-body live coverage; final version policy (Jase's word);
  small-body identity conventions; GM compatibility; interpolation
  accuracy; original parameter-check record (still unlocated).
- What would close the next items: an integrated validator+cache test
  on a live pull; the stated version policy; a small-body ID
  convention — each preserved with hashes, as this batch was.

---

*Supplement, 2026-10-26, continuation work (mutual-review-always-on).
Perplexity's files remain Perplexity's; promotion to the main folder
requires maturity + Jase's approval, per the collab rules.*
