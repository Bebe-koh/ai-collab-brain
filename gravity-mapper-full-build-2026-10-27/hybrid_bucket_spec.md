# Hybrid Deferred-Bucket — Finalized Bounded Implementation Specification (v2, AMENDED)

**Status:** SPECIFICATION ONLY. No code written, no code modified, no
implementation authorized by this document.

**Version history:** v1 (2026-10-26) drafted from Jase's Hybrid direction +
Perplexity's four corrections. **v2 (2026-10-26) amends v1** with the five
gaps Jase specified before approving implementation. v2 supersedes v1 in
full; where v1 and v2 disagree, v2 governs. Implementation still requires
Jase's explicit approval of THIS (v2) version.

## 0. Change list (v1 → v2) — sections and tests affected

| Gap (Jase's specification) | Sections changed | Tests changed/added |
|---|---|---|
| 1. Legacy consolidations ≠ legacy deferrals (10 deferred are ALL belt-closure; 4 novel consolidations are consolidated history, not deferred) | §3 rewritten (two legacy classes L-D / L-C); §6 scope wording | T-C11 rewritten (two-class test) |
| 2. Complete cap-reporting rule (display-only capped null; no phantom distribution) | §1.4 rewritten | T-C10 updated; NEW T-C15 (cap display-only) |
| 3. Stable log-domain normalization (shared-offset algorithm; extreme-weight + common-offset behavior) | NEW §1.5 | NEW T-C13 (common-offset invariance), T-C14 (extreme weights) |
| 4. Tightened persistence (exact round-trip for finite log-weights; -inf sentinel; absolute handling; scale-dependent tolerance justification) | §4 rewritten | T-C6 rewritten (exact equality, sentinel cases) |
| 5. No-op vs audit-note semantics (replay changes no scientific state or persisted ledger; attempt log separate and excluded from equality) | §2 table (repeated-deferral + rejection rows); §2.1 NEW (state definition) | T-C5 rewritten (state-tuple equality, attempt log excluded) |
| Implementation proposal (files, baseline, scratch setup, save route) | NEW §9 | — (proposal, not tests) |

**Supersession notes (carried from v1):** this spec CORRECTS
`cd_decision_brief.md` on the inflation formula (§1.3) and WITHDRAWS its
B3-only fallback (§7). **New in v2:** this spec also CORRECTS v1 §3, which
described the legacy entries as "belt 10, novel 4" deferred — wrong. The
10 deferred entries are all belt-closure; the 4 novel entries are
consolidations, not deferrals (see §3 for the verified evidence).

**Decision context:** Jase chose the Hybrid disposition ("Do hybrid") for
the C-d deferred-mass failure, with the condition that the bucket's
mathematical definition be tightened before implementation. This document
is the tightened specification + preregistered tests. It returns for
Jase's approval; implementation is a separate dispatch AFTER approval of
v2.

## 1. Corrected mathematics

### 1.1 State model (the core definition)

The tracker holds hypotheses, each with:

- **Identity:** a stable identifier + parameters + parameter convention
  (Phase 2b identity contract: case ID, dataset/model/scoring identity for
  events; candidate parameters for entries).
- **Unnormalized log-weight** `w_i` (log-domain, never a frozen percentage).
- **Status:** `active` or `deferred`.

The **deferred bucket** is defined as the AGGREGATE of deferred
hypotheses' weights:

```text
W_active = Σ_{i active} exp(w_i)
W_deferred = Σ_{j deferred} exp(w_j)
W_total = W_active + W_deferred
share_i = exp(w_i) / W_total        (for any hypothesis, active or deferred)
bucket_share = W_deferred / W_total
```

**Naming:** call it the **deferred bucket**. It aggregates TRACKED
unresolved hypotheses. It does NOT represent a probability for all
unimagined alternatives, and must never be described as "the unknown" in
that sense.

### 1.2 Normalization under change

Normalization is always over active + deferred TOGETHER. The bucket is not
a frozen percentage: its unnormalized weight is preserved, so its
normalized percentage CHANGES when other weights change. That is correct
behavior, not a leak:

- **New evidence on active hypotheses:** active weights update by the
  verdict log-odds; deferred weights are UNCHANGED (same unnormalized
  values). All shares renormalize over the new total. The bucket's
  percentage shifts because the total shifted; its weight did not move.
- **Candidate insertion:** a new hypothesis enters ACTIVE with its prior
  weight. Deferred weights unchanged; all shares renormalize. The bucket's
  percentage shifts; its weight did not move.
- **Deferral (active → deferred):** the hypothesis's weight moves from the
  active sum to the deferred sum. Its unnormalized weight is UNCHANGED.
  No share changes at the instant of deferral, because the total is
  unchanged: deferral changes STORAGE/ACTIVE STATUS only, never the
  distribution. (This is the conservation invariant §5 tests.)
- **Re-entry (deferred → active):** the hypothesis's EXISTING contribution
  TRANSFERS back to the active sum. Its unnormalized weight is unchanged.
  Re-entry must NEVER duplicate the contribution (no second copy added,
  no re-adding of a prior). Re-entry without new evidence restores the
  original distribution exactly (up to floating-point tolerance, §4).
- **Repeated deferral:** deferring an already-deferred hypothesis is a
  NO-OP on scientific state and persisted ledger (see §2.1 for the
  attempt-log separation). It must not move weight twice.
- **Rejection:** any operation rejected (identity mismatch, invalid input)
  leaves the COMPLETE state unchanged — weights, statuses, bucket, ledger
  — verified by deep comparison in tests, not by absence of an error.

### 1.3 The C-d fixture, full precision (supersedes rounded headlines)

Fixture: null prior 0.5; 5 invented prior 0.01 each; 3 killed (−5.0
log-odds each); 2 abstained (no change). Unnormalized weights: null 0.5,
each killed 0.01·e^(−5), each abstained 0.01.

```text
S (total)              = 0.520202138410
p_null pre-deferral    = 0.9611648301
deferred share d       = 0.0384465932
killed total share     = 0.0003885767
```

**Old path (active-only renormalization after deferral):**

```text
p'_null = p_null / (1 − d) = 0.9995958866
raw inflation Δ   = p'_null − p_null = p_null·d/(1 − d) = 0.0384310564
displayed increase after 0.99 cap = 0.99 − p_null = 0.0288351699
```

Three distinct numbers, not to be conflated: raw inflation
(0.0384310564) ≠ deferred share (0.0384465932) — close here because the
null already dominates the survivors, but NOT equal in general
(Δ = p₀·d/(1−d), which equals d only in the limit p₀ → 1); and the
displayed increase after capping (0.0288351699) is smaller than the raw
inflation, because the cap conceals part of it. Tests MUST use these
full-precision values, and MUST test uncapped accounting and cap-adjusted
reporting SEPARATELY, so the cap can never conceal an accounting error.

**Hybrid path (this spec):** post-deferral null = 0.9611648301
(UNCHANGED), killed = 0.0003885767, bucket = 0.0384465932, sum = 1.0.
The null does not inflate; the unresolved share is visible.

### 1.4 Cap reporting rule — COMPLETE (v2: display-only, no redistribution)

**Decision (this spec adopts the display-only alternative):** the capped
null value is a DISPLAY-ONLY value. It must not be combined with uncapped
shares, and the cap difference is redistributed to NOBODY.

**Rationale:** redistribution would move evidence-free mass into other
hypotheses' shares, violating the conservation invariant this spec
exists to enforce. The existing tracker code (`hypothesis_tracker.py`
`_compute_posteriors`) redistributes cap excess proportionally among
uncapped hypotheses — that rule is NOT adopted for bucket-aware reporting,
because under bucket semantics it would change scientific shares without
evidence (including, potentially, the bucket share). There is exactly ONE
scientific distribution: the uncapped distribution over active + deferred,
which sums to 1.0. The cap is a reporting guardrail annotation on top of
it, never a second distribution.

**Normative rules:**

1. **Scientific distribution (always):** uncapped softmax over active +
   deferred (§1.5). Sums to 1.0. This is the distribution that is
   persisted, compared in tests, and cited in verdicts.
2. **Capped display (only when the null's uncapped share exceeds 0.99):**
   the report carries `null_display = 0.99` flagged `display_only: true`,
   AND the full uncapped distribution, AND `cap_excess =
   uncapped_null − 0.99` as a scalar annotation. The difference is
   reported, not redistributed: no other share changes, the bucket share
   does not change, and no "capped distribution" is constructed.
3. **MUST-NOT-COMBINE rule:** `null_display` (0.99) + uncapped other
   shares do NOT sum to 1.0 and must never be presented, tabulated, or
   persisted as a distribution. Any consumer, report, or test that
   combines them is in violation. Reports that show the capped value
   must show the uncapped distribution adjacent to it with the
   `display_only` flag visible.
4. **Persistence:** capped values are NEVER persisted as posteriors.
   Persisted state carries uncapped shares + `cap_applied: bool` +
   `cap_excess` (when applicable). A load that finds a capped value
   stored as a posterior rejects the record.
5. **Component count for the cap:** the cap applies to the null's share
   of the full distribution (active + bucket). A single active hypothesis
   plus a non-empty bucket is a TWO-component distribution for cap
   purposes (the legacy single-hypothesis exemption in `_compute_posteriors`
   — "a single hypothesis exhausts the space" — does NOT apply when a
   bucket exists, because the bucket is the second component).
6. **Reconciliation with existing code (implementation-proposal item,
   §9):** the implementation must state, before editing code, how the
   bucket-aware path coexists with `_compute_posteriors`' existing
   redistribution loop (separate paths with the legacy path labeled
   legacy, or a unified path with updated expectations — either is
   acceptable ONLY if the calibration suite's expectations are checked
   and any change to them is justified in the implementation record, not
   silent). The scientific-distribution rule above is non-negotiable
   either way.

### 1.5 Stable log-domain normalization (v2: numerical implementation)

The exponential-sum formulas in §1.1 are the MATHEMATICAL definition,
not the numerical implementation. The implementation MUST use a shared
log-weight offset (max-subtraction), matching the existing tracker's
practice and extended to deferred weights:

```text
Given log-weights w_1..w_n over ACTIVE + DEFERRED together:
  m = max(w_i)                          # single shared offset; MUST be finite
  u_i = exp(w_i − m)                    # each u_i in (0, 1]; never overflows
  share_i = u_i / Σ_j u_j               # sums to 1.0 within floating-point rounding
```

**Normative requirements:**

- **Single shared offset:** the offset `m` is computed over active AND
  deferred weights TOGETHER. Computing active and deferred with separate
  offsets breaks conservation and is prohibited.
- **No overflow:** since w_i − m ≤ 0, `exp` never overflows. Any
  implementation that exponentiates raw log-weights directly fails
  acceptance.
- **Underflow is documented, not an error:** a weight with
  w_i − m < −745 underflows to u_i = 0.0 (share 0.0). The finite weight
  is preserved; only its computed share is 0.0. Underflow must not
  produce NaN, inf, or an exception.
- **The −inf sentinel:** a zero-weight hypothesis is stored as w = −inf
  (see §4). −inf − m = −inf → u = 0.0, which is correct. If ALL weights
  are −inf, m = −inf and the distribution is undefined: that state is
  invalid and must be rejected, never normalized.
- **Common-offset invariance:** adding the same constant c to every
  log-weight must not change the shares (up to the §4 share tolerance),
  because (w_i + c) − max(w + c) = w_i − max(w) up to floating-point
  rounding. Tested by T-C13.
- **Pre-existing reporting floor (disclosed):** the existing tracker
  applies a 1e-12 floor to reported posteriors with renormalization.
  That floor is a REPORTING transformation applied AFTER the scientific
  distribution is computed. It is far below the §4 share tolerance
  (1e-9) and therefore does not break conservation tests at that
  tolerance — but the floor must never be presented as part of the
  accounting, and conservation tests assert on the pre-floor
  distribution where the implementation exposes it (or within the 1e-9
  tolerance where it does not).

## 2. Operations specification (pre/postconditions)

| Operation | Precondition | Postcondition (exact) |
|---|---|---|
| `defer(h)` | h active, identity valid | h deferred; h's weight unchanged; all shares unchanged (total unchanged); bucket weight += h's weight; ledger event recorded with identity |
| `reenter(h)` | h deferred, identity valid, re-test trigger recorded | h active; h's weight unchanged (TRANSFER, no duplication); shares restored to pre-deferral values if no new evidence intervened; ledger event recorded |
| `defer(h)` on already-deferred h | h deferred | NO-OP on scientific state + persisted ledger: no weight moved, no share changed, no new ledger event (see §2.1 for attempt logging) |
| `insert(h_new)` | identity valid, name/params not colliding | h_new active with prior weight; deferred weights unchanged; all shares renormalized over new total |
| `apply_evidence(active set)` | verdicts valid (Phase 2b validity gate: invalid → abstain, never kill) | active weights updated by verdict log-odds; deferred weights unchanged; shares renormalized; bucket percentage shifts only via total |
| `reject(op)` (any reason: identity mismatch, invalid input) | — | COMPLETE state unchanged (weights, statuses, bucket, ledger) — verified by deep comparison, not by error absence |
| `save/load` | state valid | round-trip per §4 (finite log-weights exact; −inf sentinel preserved; +inf/NaN rejected); identities, statuses, bucket, ledger preserved; legacy entries load per §3 |

**Re-test trigger (required, not ad-hoc):** re-entry requires a recorded
trigger: new evidence about h, a redesigned case naming h, or an explicit
re-test decision recorded with reason. The trigger, the hypothesis, and
the pre/post weights are ledger events. Re-entry without a recorded
trigger is rejected.

### 2.1 State definition + attempt-log separation (v2)

**Scientific state** (the tuple covered by every equality test in §5) is
exactly: `(weights, statuses, bucket, persisted ledger)`. Nothing else.

**Attempt logging is explicitly separate:** an implementation MAY log
attempts (including repeated-deferral attempts and rejected operations)
to a diagnostic attempt log, but that log is NOT part of scientific
state, NOT part of persisted ROM state, and NOT covered by any equality
test. A true replay (same movement identity) changes NO scientific state
and NO persisted ledger entries; if it writes anything, it writes only
to the separate attempt log. An implementation that records a replay
attempt as a ledger event, or that persists the attempt log through the
ROM save path, FAILS the replay-idempotency test — even if all shares
are correct. If an implementation persists an attempt log at all, it
must be a separate artifact that state-equality tests explicitly ignore.

## 3. Ledger identity + legacy handling (v2: two classes, verified)

**Verified evidence (checked 2026-10-26 against the live ROM and the
closure record):** the live ROM's `deferred` list has 10 entries, ALL
with `case: 'belt-closure'`, reason `'abstained in all closure rounds'`.
The closure record states explicitly: "no novel deferrals exist in the
live ROM (deferral happens only at loop end). The live ROM's 10 deferred
entries are all belt-closure" (§6), and the novel loop "was stopped per
§2d after 2 full outer rounds + round 3's first fit" with "final novel
deferral NOT exercised." The 4 novel entries are consolidations
(ROM consolidations 23 → 27 during the novel run), NOT deferrals.

**Legacy therefore splits into TWO classes, which must never be merged:**

- **Class L-D — legacy-deferred (10 entries, all belt-closure):** load as
  legacy-deferred. Their stored `posterior` field is a HISTORICAL
  annotation (the share at deferral time under the old active-only
  normalization), NOT a live bucket weight: it must not be converted into
  a bucket weight, because the live mass that would reproduce that share
  under the current total is not recoverable from the share alone without
  the then-total. Their live mass is UNKNOWN. They contribute NO bucket
  weight. They are flagged `legacy-deferred` in every report that touches
  them.
- **Class L-C — legacy synthetic consolidations (4 entries, novel run):**
  these are CONSOLIDATED decided-history entries, not deferrals. Load
  NORMALLY as consolidations with their recorded values untouched. Flag
  them for SYNTHETIC PROVENANCE (the D22 cleanup flag: synthetic-novel
  provenance, kept distinct from decided history in adjudication
  contexts). Do NOT load them as legacy-deferred. Do NOT assign them
  unknown mass. Do NOT alter their recorded values. The D22 cleanup
  (separating synthetic from decided history) remains its own flagged
  task and is NOT performed by the bucket implementation.

**New deferrals (post-implementation):** full bucket semantics with
preserved weights + identity (§1–§2). New deferrals coexist with both
legacy classes without disturbing either.

**Ledger identity for bucket movements (Phase 2b contract):** case ID
(explicit, required — no silent default), dataset identity (content hash
per `ledger_identity_for`), model version, scoring definition (MSE
domain, ACCEPT_RATIO, checker version marker), deferred hypothesis
parameters + convention. A movement without identity is rejected
(complete state unchanged, §2).

**Grandfathering rule (normative):** the implementation must not rewrite
any existing persisted entry. It adds bucket state for NEW operations
and flags for OLD entries. Any implementation that edits historical mass
values — including retro-filling legacy-deferred weights or reclassifying
L-C consolidations as deferred — fails acceptance regardless of test
results.

## 4. Numerical tolerances + persistence (v2: exact round-trip, sentinel)

**Share conservation (acceptance bound, proposed):** absolute tolerance
1e-9 on shares for all conservation tests in §5. This bound is retained
from v1 as the PROPOSED acceptance bound. Its justification is
SCALE-DEPENDENT, not universal: it is adequate for the fixture regime
(hypothesis counts of order 10–10², weight magnitudes of order 10) where
double-precision accumulation rounding is ~1e-15 relative. The v1 claim
that the rounding justification is a general guarantee is WITHDRAWN. If
a future tracker regime differs substantially in count or weight
magnitude, the bound must be re-justified for that regime; the
implementation must not silently carry 1e-9 into a regime where it is
unjustified.

**Log-weight persistence (tightened — exactness required):**

- **Finite stored log-weights MUST round-trip EXACTLY** through the
  chosen serialization: loaded log-weight == saved log-weight (exact
  float equality, no tolerance). Justification: the serialization is
  JSON via Python's `json`, whose float repr round-trips IEEE doubles
  exactly (shortest repr that reproduces the value). Exactness is
  therefore achievable and is REQUIRED, not approximated. A
  serialization route that cannot guarantee exactness for finite values
  must not be used for log-weights.
- **Zero weight:** a hypothesis with weight exactly 0 is stored as the
  log-weight sentinel `−inf` (share exactly 0.0 via §1.5). Zero is
  handled by the sentinel, never by a near-zero finite substitute.
- **Permitted non-finite sentinel: −inf ONLY**, meaning exactly-zero
  weight. `+inf` and `NaN` are NOT permitted in persisted state: a save
  encountering +inf/NaN must reject (state unchanged), and a load
  encountering +inf/NaN must reject the record. A state with ALL weights
  −inf is invalid (no distribution) and must be rejected.
- **Underflow vs sentinel (distinct, do not conflate):** a finite very
  negative weight whose exp underflows to share 0.0 keeps its finite
  weight on round-trip (exactness applies); only a true zero weight uses
  the −inf sentinel. Tests assert both cases separately (T-C6).
- **"Relative tolerance on log-weights" is WITHDRAWN:** it is ambiguous
  near zero (a relative error on a log-weight near 0 is meaningless) and
  depends on an otherwise arbitrary common offset (shifting all
  log-weights by a constant changes every relative error while changing
  no share). No relative log-weight tolerance appears in §5.

**Cap reporting persistence:** per §1.4 rule 4 — persisted state carries
uncapped shares + `cap_applied` + `cap_excess`; capped values are never
persisted as posteriors.

## 5. Preregistered tests (all required before implementation is accepted)

T-C1. **C-d fixture, full precision:** the §1.3 fixture through deferral.
  Assert post-deferral null = 0.9611648301 ± 1e-9, bucket = 0.0384465932
  ± 1e-9, killed = 0.0003885767 ± 1e-9, cap not bound. Assert separately
  that the OLD path on the same fixture gives 0.9995958866 (proves the
  test distinguishes the fix from the bug).
T-C2. **Conservation across deferral:** every surviving hypothesis
  retains its share immediately across deferral (± 1e-9); bucket increase
  equals transferred deferred share (± 1e-9); active + bucket = 1.0
  (± 1e-9).
T-C3. **Re-entry restoration:** deferral then re-entry with NO new
  evidence restores the original distribution (± 1e-9 on every share).
  Re-entry transfers (weight count: contribution appears exactly once
  in active sum, zero times in deferred sum).
T-C4. **Repeated deferral:** deferring an already-deferred hypothesis
  changes NO scientific state and NO persisted ledger entry (state-tuple
  equality per §2.1; attempt-log entries, if any, excluded from the
  comparison and verified to be absent from persisted state).
T-C5. **Replay idempotency (v2 rewritten):** replaying the same
  deferral/re-entry movement (same identity) leaves the state tuple
  `(weights, statuses, bucket, persisted ledger)` EXACTLY equal (deep
  comparison). Any attempt logging from the replay must be confined to
  the separate attempt log (§2.1); a replay that adds a ledger event or
  alters persisted state FAILS, even if shares are correct.
T-C6. **Persistence round-trip (v2 rewritten):** save → load preserves
  FINITE log-weights EXACTLY (loaded == saved, float equality, no
  tolerance); −inf sentinel preserved as −inf with share 0.0;
  underflow case (finite very-negative weight, share 0.0) preserves the
  finite weight exactly; +inf/NaN rejected at save (state unchanged) and
  at load (record rejected); all-−inf state rejected. Identities,
  statuses, bucket, ledger preserved.
T-C7. **Rejection atomicity:** each rejection case (identity mismatch:
  same name different params; same event different dataset; movement
  without identity; re-entry without trigger) leaves the COMPLETE state
  unchanged (deep comparison before/after equal, including ledger).
T-C8. **New-evidence renormalization:** active weights updated by
  evidence; deferred weights bit-unchanged; bucket percentage shifts by
  exactly the total-change arithmetic (assert deferred WEIGHT equal,
  bucket SHARE recomputed from new total).
T-C9. **Candidate insertion:** new active hypothesis inserted; deferred
  weights unchanged; shares renormalized correctly.
T-C10. **Cap separation (v2 updated):** uncapped accounting asserted
  WITHOUT the cap active; cap-adjusted reporting asserted WITH
  pre-cap values preserved alongside, per the §1.4 display-only rule
  (capped null flagged, cap_excess reported, no redistribution). A test
  where the cap binds must show both numbers.
T-C11. **Legacy two-class loading (v2 rewritten):** a tracker/ROM
  containing BOTH legacy classes loads correctly: (a) the 10
  belt-closure deferred entries load as legacy-deferred with NO bucket
  weight, their stored `posterior` preserved as a historical annotation
  only, flagged in reports; (b) the 4 novel consolidations load as
  consolidations with values untouched, flagged for synthetic provenance
  (D22), and are NOT present in the deferred list; (c) a NEW deferral in
  the same tracker uses full bucket semantics without disturbing either
  legacy class. Any implementation that loads an L-C consolidation as
  deferred, or assigns a bucket weight to an L-D entry, FAILS.
T-C12. **Original C-d regression:** the original cap-based fixture
  passes post-fix (null not bound by deferral) AND the conservation
  tests pass on the same fixture. The original failure stays on the
  record; the fixture now passes because the mechanism changed, not
  because the test changed.
T-C13. **Common-offset invariance (v2 NEW):** adding the same constant
  c to every log-weight (tested at c = +100, −100, +1000) leaves every
  share unchanged within 1e-9, for active + deferred together.
T-C14. **Extreme weights (v2 NEW):** a weight spread exceeding 745 log
  units (smallest weight underflows to share 0.0) computes without error,
  without NaN/inf, with shares summing to 1.0 within 1e-9; the smallest
  finite weight is preserved exactly on round-trip (T-C6 underflow case).
T-C15. **Cap display-only (v2 NEW):** a fixture where the null's uncapped
  share exceeds 0.99 produces: uncapped distribution summing to 1.0
  (± 1e-9); `null_display = 0.99` flagged `display_only`; `cap_excess`
  equal to uncapped_null − 0.99 (± 1e-9); NO other share changed by the
  cap; NO capped value persisted as a posterior; and a MUST-NOT-COMBINE
  assertion (capped null + uncapped others do not sum to 1.0 and are
  never emitted as a single distribution).

## 6. Implementation scope boundary (for the FUTURE dispatch — not this doc)

When (and only when) Jase approves this spec, the implementation batch
scope is:

- **In scope:** tracker deferral/re-entry paths + bucket state;
  renormalization (active + deferred together, §1.5 algorithm); cap
  reporting per §1.4 (display-only) + pre-cap preservation; ledger events
  for bucket movements (Phase 2b contract); two-class legacy loading
  (§3); the §5 tests.
- **Out of scope:** any change to validation artifacts, sealed records,
  or the closure §6 verdict; any rewrite of existing persisted entries;
  any change to fitter/checker/optimizer code; the joint interface; the
  ranker; the novel redesign; the refit-cost fix; the D22 synthetic
  cleanup (flagging only, §3 — separation itself is a separate task). A
  bug found outside scope is reported, not fixed in the batch.
- **Acceptance:** all §5 tests pass + existing suites still pass
  (audit fixes 20/20, Phase 2b 16/16, correctness batch 38/38,
  calibration 13/13 — newly executed results reported separately from
  historical results) + live ROM byte-identical except for the specified
  legacy-flag additions (if any — flagged additions only, mass values
  untouched) + Drive milestone backup + delta-sync.

## 7. No-fallback rule (normative — replaces the brief's fallback)

If implementation encounters a conflict with the ledger identity work
(or any other specified contract), the implementation STOPS, reports the
specific conflict with evidence, and proposes a bounded resolution for a
SEPARATE decision. There is NO automatic fallback to B3-only clearance.
A ledger implementation difficulty is not a reason to treat inflated
nulls as cleared for downstream use. This rule binds the future
implementation batch; violating it (silently downgrading to B3-only)
fails acceptance regardless of test results.

## 8. What approval of this spec authorizes (and does not)

- **Authorizes (on Jase's approval of v2):** dispatch of the bounded
  implementation batch in §6, per the §9 proposal, under this spec +
  §5 tests + §7 no-fallback rule.
- **Does NOT authorize:** any code edit before that approval; any
  relaxation of ladder Gate 0 (which completes only when the
  implementation lands + re-tests pass); any ROM ingestion of
  multi-body verdicts; any change to the closure verdict; any
  B3-only clearance under any circumstance; any live-ROM migration
  (flagging only); any claim of novel-body recovery or clearance of
  unrelated discovery gates.

## 9. Implementation proposal (PROPOSAL ONLY — part of this spec for approval)

This section identifies what the future implementation batch will touch,
so Jase can approve it as a bounded unit. It authorizes nothing by itself.

**Exact files to change (all in
`~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/` —
the verified working copy; no new packages, no redundant copies):**

| File | Change |
|---|---|
| `hypothesis_tracker.py` | Bucket-aware posterior path: `_compute_posteriors` extended (or a sibling method, if the legacy path must stay frozen) to normalize over active + deferred together per §1.5, return uncapped distribution + cap metadata (`cap_applied`, `cap_excess`, `display_only` flag) per §1.4, and expose calibrated log-weights for deferred hypotheses. Reconciliation with the existing proportional-redistribution loop per §1.4 rule 6, stated in the implementation plan before edits. |
| `rom_closure.py` | `_defer_abstained` (line ~472): record deferred WEIGHTS + identity alongside the existing record fields (name, bodies, body_type, reason, case, posterior-as-annotation); repeated-deferral no-op per §2.1; `close_invented` reporting to carry bucket state + cap metadata. No change to verdict mapping, thresholds, or `ACCEPT_RATIO`. |
| `rom_history.py` | `ParentROM` extra-schema handling for the two legacy classes (§3 flags: `legacy-deferred` on the 10 belt entries, synthetic-provenance flag on the 4 novel consolidations — flags only, values untouched); ledger-event identity for bucket movements via the existing `consolidate()` identity path; NO change to the atomic save mechanism itself. |
| NEW test file (one file, alongside existing suites) | The §5 tests (T-C1–T-C15) as a single new suite file (e.g. `bucket_conservation_tests.py`), reusing the existing test harness conventions. No new package, no copied source. |

**Files explicitly NOT changed:** fitter brains (`rails/particle/optimizer/
checker/conductor_brain.py`), `rom_loop.py` (loop control), validation
artifacts (`sealed_runs/rom_closure_validation_results.jsonl`,
`rom_loop_closure_note.md`), the live ROM's existing entries (flags only,
§3), thresholds (`ACCEPT_RATIO`, caps, `N_EFF_CAP`), evaluator defaults.

**Accessible source baseline:** the verified post-Phase-2b working copy in
`hidden_files/` (audit fixes 20/20, Phase 2b 16/16, correctness batch
38/38, calibration 13/13 — freshly re-executed by Atlas 2026-10-26, record
`fresh_rerun_2026-10-26.md`), mirrored in the Drive full-build folder
(`gravity-mapper-full-build-2026-10-25`, ID
`1KauPTvlHWX8B1_XBtq-UgvM-S0iKTgkb`, plus deltas). Backups reused, not
recreated: `rom_closure.py.pre_selector_bak`,
`rom_closure.py.pre_correctness_bak`, `rom_history.py.pre_correctness_bak`,
`pre_phase2b_backup/`, `pre_phase2_backup/`, live-ROM backups
(`parent_rom.json.bak`, `.pre_live_belt_20261025`, `.pre_closure_20261025`,
`.pre_phase2_20261026`). The implementation batch must back up each
edited file as `.pre_bucket_bak` (verified identical before editing,
per the selector-integration precedent) and must not create a second
copy of the codebase.

**Scratch-state setup:** ALL implementation tests run against scratch
state, never the live ROM: scratch trackers constructed directly with the
§1.3 fixture weights (no fitter runs needed for conservation tests);
scratch `ParentROM` instances with `path` pointing at a temp directory;
scratch deferred/consolidation records synthesized to mirror the two
legacy classes (10 belt-style + 4 novel-style) for T-C11. The live ROM
(`real_data/parent_rom.json`, md5 `4c77b723ff5770566a85ed4e580aed2c`)
is READ-ONLY during implementation; its md5 is asserted before and after
the batch. Any test that would write to the live path fails the batch.

**Existing durable save route (reused, not replaced):** `ParentROM.save()`
(`rom_history.py` ~lines 142–168: temp sibling in the same directory +
flush + fsync + re-read + `os.replace()`), and the deferred list's
existing persistence via the `parent.extra` unknown-key path. No new
save mechanism is introduced. Durable saves in the batch are limited to:
edited source files' `.pre_bucket_bak` backups, the new test file, and —
only after Jase's approval of the implementation RESULTS — the Drive
milestone backup + delta-sync of changed files.

**Continuity manifest (verified finding):** NO local continuity-manifest
file exists for this project (only unrelated real-data manifests; the
Drive final-manifest is quarantined and untouched). There is therefore
no manifest to update; the continuity record for this batch is the Drive
milestone backup + delta-sync + the complete test-output record. If Jase
wants a manifest created, that is a separate decision — the
implementation must not invent one.

**Pre-implementation plan requirement:** before editing code, the
implementation dispatch must state in writing: (a) the §1.4 rule 6
reconciliation (legacy redistribution path vs bucket-aware path), (b)
confirmation that all §5 tests run against scratch state, and (c) the
live-ROM md5 assertion. If any of (a)–(c) cannot be stated, the batch
does not start.

---

*Specification v2, amended 2026-10-26 from Jase's five specified gaps.
Supersedes v1 in full; corrects v1 §3 (legacy classes) and the brief
(inflation formula, B3 fallback). No code written. Implementation
requires Jase's explicit approval of THIS (v2) version, as a separate
decision. Successful implementation and tests would support a new,
bounded C-d disposition only — they would not erase the original
failure, authorize live-ROM migration, establish novel-body recovery,
or clear unrelated discovery gates.*
