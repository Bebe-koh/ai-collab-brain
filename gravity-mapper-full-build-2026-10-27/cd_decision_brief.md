# C-d Decision Brief — Deferred-Mass Disposition (D1) — DECISION BRIEF, NOT A DECISION

**Status:** BRIEF ONLY. This document lays out the C-d failure, the mechanism,
and the options for disposing of it, so Jase can decide. It decides nothing.
No code is written or modified by this brief.

**Decision requested (D1):** Option A (explicit unknown/deferred bucket),
Option B (criterion revision with re-registration), or a Hybrid (bucket
mechanism + new re-test criteria). Sub-variants are listed under each option;
the top-level choice is the decision, the sub-variant can be picked with it.

## 1. The failure, stated precisely

**Criterion C-d (pre-registered, absolute):** on a scratch tracker, the null
posterior must not bind the 0.99 posterior cap as an artifact of bookkeeping.

**Observed result (closure validation §3b/§3e, Ammonite scratch tracker):**
FAIL. After 3 kills and deferral of 2 abstained hypotheses, the null posterior
is exactly 0.99 (capped).

**Mechanism (confirmed in code, not hypothesized):**

1. The tracker holds 6 hypotheses: null (prior 0.5) + 5 invented (prior 0.01
   each). A kill subtracts exactly the verdict log-odds cap (5.0); an
   abstention adds nothing.
2. After 3 kills, the weights are: null log-weight −0.693, each killed
   −9.605, each abstained −4.605. Normalized pre-deferral posteriors:
   null ≈ 0.961, killed ≈ 0.0004 total, abstained ≈ 0.0384 total.
   The cap is NOT bound at this point.
3. Deferral (`_defer_abstained`) then REMOVES the 2 abstained hypotheses
   from the active tracker, saves their metadata, and renormalizes over
   what remains: null vs 3 killed. Normalized post-deferral null ≈ 0.9996
   → capped to 0.99.

**What this is, and what it is not:**

- It is NOT a likelihood explosion. No posterior is 1.0 or 0.0, and the cap
  worked as a guardrail. The live-ROM belt stages never bound the cap
  (null ≈ 0.44 throughout).
- It IS a probability-accounting leak: deferred hypotheses' mass (0.0384 in
  this case) vanishes by normalization instead of being held anywhere. The
  null inflates by exactly the deferred share (0.961 → 0.9996) on every
  tracker where deferral removes a non-negligible share.
- Scale matters: on the live ROM (27 consolidations, large hypothesis set),
  a single deferral removes a tiny share and the inflation is negligible.
  On small trackers — scratch trackers, novel-case trackers, early-stage
  open questions — the inflation is large. The failure is therefore
  worst exactly where a new discovery case starts: small.

**Why it gates more than C-d:** the same deferral path runs in
`close_invented` and `run_novel_case`. Any ROM ingestion that follows a
deferral inherits inflated nulls. That is why D1 gates ladder Gate 0 and
ROM ingestion of multi-body verdicts — but NOT the joint-interface
prototype, which never consolidates into the ROM or uses deferral paths
(review Amendment 1, §7.3).

## 2. Option A — Explicit unknown/deferred bucket (fix the mechanism)

**Design:** deferred hypotheses' probability mass is held as an explicit
allocation — an "unknown" bucket — instead of vanishing by normalization.

- **On deferral:** the pre-deferral posterior mass of each deferred
  hypothesis moves into the bucket. Post-deferral posteriors are computed
  over active hypotheses PLUS the bucket, so pre-deferral posteriors are
  preserved exactly. Worked example (the C-d case): post-deferral null =
  0.961 (unchanged), killed ≈ 0.0004, bucket = 0.0384. The null no longer
  inflates; the unresolved share is visible instead of hidden.
- **Bucket semantics (must be specified, not improvised):**
  - The bucket is NOT a hypothesis. It cannot be promoted, killed, or
    fitted. It is a reserved share labeled "unresolved."
  - The bucket is reported alongside every posterior (active posteriors +
    bucket share always sum to 1.0). A reader who sees only active
    posteriors is misled; the bucket is part of the number.
  - The 0.99 cap applies to the null's share INCLUDING the bucket in the
    denominator (i.e., the bucket competes with the null). Capping the
    null on active-only posteriors would reintroduce the inflation.
- **How mass leaves the bucket (re-test trigger):** when new evidence
  arrives that re-opens a deferred hypothesis (re-test, new data, or a
  redesigned case), that hypothesis re-enters the active set and its mass
  returns from the bucket for re-scoring. The trigger and the re-entry
  rule are part of the implementation spec, not left to ad-hoc judgment.
- **What the bucket does NOT do:** it does not decay, expire, or get
  redistributed without evidence. Silent decay would be the same leak in
  slower motion. If a retention/compaction rule is ever wanted, it needs
  its own specification and tests (same discipline as the ledger).
- **Ledger interaction (Phase 2b identity):** bucket movements are ledger
  events with identity (case ID, dataset/model/scoring identity, deferred
  hypothesis parameters). A bucket movement without identity is a rejected
  write under the Phase 2b contract.
- **Grandfathering:** the 10 existing belt deferred entries (and the 4
  synthetic-novel consolidations) were deferred under the old path — their
  mass is already normalized away and cannot be reconstructed without
  re-running. Under Option A they are flagged as legacy-deferred with
  unknown mass, never retro-fitted with invented numbers. New deferrals
  use the bucket; old ones stay flagged.

**What Option A fixes:** the accounting leak itself, on trackers of every
size. Post-deferral posteriors stay honest; the unresolved share is visible
and quantified; C-d can be re-tested against the fixed mechanism.

**What Option A costs:** a tracker change (bucket state, deferral path,
renormalization, cap interaction), ledger events for bucket movements,
re-test trigger rules, and a test suite (see §5). Moderate implementation,
larger than a criterion edit, smaller than a fitter build. It also changes
the tracker's state schema — existing persisted ROMs need the
grandfathering rule above, not a migration that invents history.

**What Option A leaves unaddressed:** it does not, by itself, define the
new C-d re-test criterion. The re-test needs a criterion (see §5): the
natural one is "post-deferral null equals pre-deferral null within a stated
tolerance, and bucket share equals deferred pre-deferral mass within the
same tolerance."

## 3. Option B — Criterion revision with re-registration (fix the test)

**Design:** leave the deferral mechanism as-is; revise C-d so it tests
something defensible, with a new rationale, new pre-registration, and a
re-test. The original C-d failure STAYS on the record under either
sub-variant — revision never erases it.

**Sub-variants (pick one with the option):**

- **B1 — Scope restriction.** C-d applies only to trackers above a minimum
  hypothesis count (or below a maximum deferred share), where deferral
  depletion is negligible by construction. Rationale: C-d was meant to
  catch likelihood explosions, and on large trackers it does; on small
  scratch trackers it measures a different phenomenon (depletion).
  Risk: the threshold itself needs justification, or it looks like it was
  drawn to exclude the failing case. The threshold must be set from the
  depletion arithmetic (deferred share vs cap distance), not from the
  observed failure.
- **B2 — Pre-deferral assessment.** C-d is assessed on pre-deferral
  posteriors (cap binding checked before pruning, not after). Rationale:
  the cap's purpose is guarding likelihood accounting, and pre-deferral
  posteriors are where likelihood accounting lives; post-deferral
  posteriors are a different quantity (active-set-conditional). Risk:
  this redefines the criterion to test a quantity the loop never reports
  — pre-deferral posteriors would need to be recorded alongside
  post-deferral ones, or the test is unverifiable.
- **B3 — Null-inflation bound (recommended if B is chosen).** C-d is
  replaced by a direct bound on the wrinkle itself: post-deferral null
  minus pre-deferral null ≤ stated tolerance (e.g. 0.01, TBD by Jase).
  Rationale: this tests the mechanism that actually failed, rather than
  the cap that happened to bind. Under B3, the C-d scratch case FAILS
  by 0.0386 (0.9996 − 0.961) — the failure is preserved as a finding
  about the mechanism, and the criterion now names what must be fixed
  (the bound) rather than what happened to trip (the cap).

**What Option B fixes:** the criterion's defensibility. It stops grading
the loop against a test that measures the wrong quantity.

**What Option B costs:** almost no implementation — a criterion document
change + re-registration + re-test. The cheapest option by far.

**What Option B leaves unaddressed:** the mechanism. The null still
inflates on every small tracker; it just no longer fails a criterion.
Every downstream consumer of post-deferral posteriors (ladder batteries,
shadow mode, standalone adjudication) inherits inflated nulls unless
they independently correct for deferral share. This is the central
objection to B alone: it fixes the test, not the accounting, and the
accounting is what future verdicts rest on.

**What would make B principled rather than criterion-shopping:** B must
be justified by an argument independent of the observed failure. B3
comes closest (it names the mechanism and bounds it). B1 needs the
arithmetic justification for its threshold. B2 needs the reporting
change. A revision whose only justification is "the old criterion
failed" is criterion-shopping and must not be accepted — including by
this brief's author.

## 4. Hybrid — Bucket mechanism + new re-test criteria (recommended)

**Design:** implement Option A (the bucket), and re-test under B3-style
criteria (null-inflation bound + bucket-conservation check: bucket share
equals deferred pre-deferral mass within tolerance).

**Why this is recommended:** A fixes the accounting that future verdicts
rest on; B3 gives the re-test a criterion that names the mechanism rather
than the cap. Neither alone is sufficient: A without a re-test criterion
leaves C-d undispositioned; B3 without A leaves the mechanism leaking
while the criterion documents the leak. Together, the mechanism is fixed
AND the test proves it.

**What would change this recommendation:** if the bucket implementation
proves to interact badly with the Phase 2b ledger identity work (e.g.
bucket movements cannot carry identity cleanly), the fallback is B3
alone with an explicit, recorded acknowledgment that small-tracker
post-deferral nulls remain inflated and must be corrected for (or
avoided) by downstream consumers. That fallback must be a conscious
decision, not a silent downgrade.

## 5. Tests required (pre-registered before implementation, either option)

1. **C-d reproduction (exact):** the 6-hypothesis scratch tracker, 3 kills,
   2 abstains → deferral. Under A/hybrid: post-deferral null = 0.961
   within tolerance, bucket = 0.0384 within tolerance, cap not bound.
   Under B3 alone: inflation 0.0386 reported (fails the bound, as the
   mechanism still leaks) — the test documents, not hides, the leak.
2. **Live-ROM-scale case:** large tracker, small deferred share →
   depletion negligible under all options (guards against over-correction
   that distorts large trackers).
3. **Re-test trigger (A/hybrid only):** a deferred hypothesis re-opened by
   new evidence re-enters with its mass returned; ledger shows the
   movement with identity; no mass created or destroyed (bucket +
   active sums to 1.0 before and after).
4. **Grandfathering:** old deferred entries (belt 10, novel 4) load as
   legacy-deferred with unknown mass; no invented numbers; new deferrals
   use the bucket.
5. **Ledger identity:** bucket movements carry case/dataset/model/scoring
   identity; a movement without identity is rejected (Phase 2b contract).
6. **Cap interaction (A/hybrid only):** a case constructed to bind the cap
   WITH the bucket present binds on the correct denominator (bucket
   included), not on active-only posteriors.

## 6. What happens next for each decision

| Decision | Immediate next step | Gate impact |
|---|---|---|
| A (bucket) | Bounded implementation batch (tracker + ledger + tests, per §5) | Ladder Gate 0 completes on the D1 leg once implemented + re-tested |
| B (any sub-variant) | Criterion document + re-registration + re-test (B3 documents the leak; B1/B2 need their justifications) | Ladder Gate 0 completes on the D1 leg ONLY if the revision is accepted as principled (see §3 objection); downstream consumers must handle inflation explicitly |
| Hybrid (recommended) | Bucket implementation batch + B3 re-test criteria | Ladder Gate 0 completes on the D1 leg; mechanism fixed AND proven |
| Defer the decision | Nothing changes; C-d stays failed; ladder Gate 0 stays open | All ROM-ingestion work stays gated; prototype work unaffected (Amendment 1, §7.3) |

**What this decision does NOT authorize:** implementation (a separate
dispatch after the decision), any change to the live ROM's existing
entries, any change to the closure validation record (§6 verdict stands),
or any relaxation of the ladder's other gates.

---

*Decision brief, drafted 2026-10-26, Jase-authorized continuation work.
Decides nothing. Implementation requires a separate dispatch after Jase's
decision. Original C-d failure stays on the record under every option.*
