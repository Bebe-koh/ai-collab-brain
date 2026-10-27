# Inventor-Assist Proposal Ranker — DESIGN DOC (v1, DRAFT)

**Status:** DESIGN ONLY. No code written, no model trained, no live file modified.
This document specifies a small, specialized search assistant for the Gravity
Mapper: a proposal ranker that helps decide which candidate or optimizer start
to try next. It does NOT decide whether a discovery is real, and it does not
replace any physics, gate, or evidence rule.

**Authorship note:** The mapper, the ROM, and the inventor loop are Jase's ideas.
The ranker concept was developed jointly in discussion (Atlas's brain-by-brain
analysis plus Perplexity's proposal-ranker recommendation, agreed 2026-10-26).
This document is Atlas's design work on that agreed concept.

## 0. The problem it solves — and the problem it does not

**Solves:** search cost. The mapper generates hypotheses and spends expensive
physics fits testing them. Conductor fits cost ~2–3 s (Keplerian path) to
~60–100 s (N-body path) each, and the novel loop's quadratic refit pattern
(~110 fits / ~4.5 h projected for 5 rounds) shows what unprioritized search
costs at scale. A ranker that orders attempts by expected usefulness per unit
of computation can cut that cost without changing any verdict.

**Does not solve:** adjudication. The ranker never promotes, kills, or scores
evidence. It never sees an open question's answer, and it never trains on real
open-question data. If the ranker is wrong, the cost is wasted compute, never a
wrong discovery — provided the rules in §3 hold.

## 1. Placement (the pipeline)

```text
Inventor generates candidates
          ↓
Ranker orders candidates and starting states  (NEW — advisory first, §7)
          ↓
Existing physics fitter tests them (unchanged)
          ↓
Independent checker evaluates predictions (unchanged)
          ↓
Evidence ledger records the outcome (unchanged, and records the rank)
```

The ranker sits BETWEEN generation and fitting. It touches nothing downstream:
the fitter, the checker, the ROM's evidence accounting, and the promotion
criteria are exactly as they are. The conductor remains explicit orchestration;
the optimizer remains numerical fitting. The ranker's name is not a "brain" in
the mapper's sense — it is a search utility, and keeping that distinction
matters, because the mapper's brains are deterministic machinery, not trained
models.

## 2. Three roles (one build, three outputs — or three small models)

| Role | Output | Authority |
|---|---|---|
| **Candidate/start ranker** (first build) | An ordered list of candidates and/or initial guesses | Changes search order ONLY |
| **Compute-cost predictor** | Expected runtime and/or likelihood of optimizer difficulty for a candidate | Budget allocation ONLY; cannot reject, deprioritize-to-zero, or veto a physical hypothesis |
| **Residual-pattern assistant** | Diagnostic suggestions: "check timing", "check inventory", "try a multi-body explanation", "check frame" | Suggestions ONLY; never a scientific verdict, never a routing decision that bypasses a gate |

The first experiment builds the ranker only. The cost predictor and the
residual assistant are specified here so their interfaces match later, but
they are NOT built in the first experiment. The residual assistant's
"try a multi-body explanation" suggestion routes to Stage B machinery that
requires the joint interface — the suggestion does not execute anything and
does not substitute for that interface.

## 3. Rules (non-negotiable — violation of any one is a design bug)

1. **Proposal and ranking only, never adjudication.** The ranker proposes an
   order; the physics fitter, checker, and ROM decide. AI proposes, physics
   disposes.
2. **Prioritize, never silently eliminate.** Lower-ranked candidates and
   regions keep some search coverage (a stated minimum fraction of fits, TBD —
   see §8). Grid-fill and perturb strategies continue to run; the ranker
   reorders attempts, it does not replace systematic search.
3. **Fallback to the existing search strategy.** If the ranker is unavailable,
   uncertain, or out-of-distribution for a case, the loop runs exactly as it
   does today. Fallback is automatic, not a human rescue.
4. **A ranking score is NEVER displayed as a probability that a body exists.**
   Ranks live in the search record; posteriors live in the ROM. Those columns
   never merge, in any display, file, or summary. A rank shown as a probability
   is a laundering bug.
5. **Trained ONLY on synthetic data with known truth.** Never on real
   open-question data, never on decided-history outcomes used as answers, never
   on live ROM state. The physics generates its own unlimited labeled training
   set (§5); there is no reason to touch real data, and every reason not to.
6. **Judged on unseen cases, never on retries or variations of training cases.**
   The evaluation split is sealed before training (§5.3), following the
   ladder's train/test discipline. Tuning on the evaluation split invalidates
   the evaluation.
7. **Ledger-recorded.** Every ranking the loop acts on is recorded in the
   evidence ledger: which candidates were ranked, in what order, by which model
   version, and which were actually fit. A verdict whose search history cannot
   be re-derived is not auditable.
8. **Ablatable.** The loop with the ranker switched off must produce IDENTICAL
   verdicts to the loop with it on, given the same candidates and unlimited
   budget — because the ranker changes order, not outcomes. If removing the
   ranker changes a verdict (under unlimited budget), the ranker was
   load-bearing, and that is a design bug, not a feature.

## 4. What stays deterministic and auditable (never the ranker's job)

- Force calculations and units.
- Reference-frame and time conversions.
- Holdout partitioning (the checker owns the partition; the ranker never sees
  holdout data as training input and never influences the split).
- Evidence-event deduplication (the ledger owns this).
- Survey-coverage rules (the veto design owns these).
- Final promotion or rejection criteria (the ROM + conductor own these).
- Likelihoods and posteriors. A learned replacement for likelihoods or
  posteriors (simulation-based inference) is a substantially more demanding
  project needing its own calibration and validation; it is explicitly
  DEFERRED, not part of this design. Plausible-looking posterior predictions
  are not enough.

## 5. Training data (the labels problem — read this before anything else)

### 5.1 What the labels must be

For each training record: a residual pattern, a candidate description, and the
search history at decision time → the outcome of fitting that candidate
(useful fit? recovery within tolerances? cost in physics evaluations and wall
seconds?). The label is a SEARCH outcome, not a scientific verdict.

### 5.2 What the labels must NOT be (the critical warning)

**ROM posteriors and ROM regional counts are NOT suitable training labels.**
Two known artifacts prove why:

- **Belt-run dilution:** same-step invention diluted posterior shares while the
  underlying weights rose exactly as designed. A ranker trained on shares
  would learn the dilution artifact as if it were candidate quality.
- **Pre-fix bin inflation:** repeated consolidation inflated ROM bins/priors
  (total_hypotheses 131 → 231; phantom bin n_tried 3 → 8 with n_good stuck at
  1) without changing posteriors. A ranker trained on bin counts would learn
  consolidation history as if it were evidence.

This is why the search-efficiency memory and the scientific-evidence memory
must be separated BEFORE any ranker training: the ranker learns from the
search record (what was tried, what it cost, what fit), and the ROM keeps the
evidence record (what was proven). Mixing them corrupts both.

### 5.3 Generation and sealing

- Training cases are synthetic, generated by the same machinery as the ladder's
  Battery 1 (single-body, multi-body, null, systematics, incomplete-inventory
  cases) with sealed truth.
- Features are structured and tabular: residual-pattern descriptors (magnitude,
  coherence across split halves, spatial distribution), candidate descriptors
  (mass, radius, phase, distance from existing inventory), and search history
  (candidates tried, fits spent, best ratio so far). No raw language, no
  free-text features.
- The case set is split into TUNING and HELD-OUT before any training, sealed
  and recorded. The held-out set is evaluated exactly once per final model
  configuration. No tuning on held-out cases, ever (ladder §3 discipline).
- **Scale note:** the physics generates training data, so quantity is not the
  constraint — case diversity is. The training set must span the hypothesis
  space (masses, distances, eccentricities, multi-body geometries, nulls,
  systematics), not just the easy middle.

## 6. Model classes (first experiment — alternatives, not established winners)

The first experiment compares three model classes on the same sealed splits,
against a trivial baseline (e.g. inventor order, or mass/distance heuristic):

1. **Simple statistical baseline** (e.g. logistic/linear model on the §5
   features). If this matches the fancier models, it wins — simplest auditable
   model that does the job.
2. **Small tree-based model** (e.g. gradient-boosted trees). Tabular features,
   small, fast, inspectable feature importance.
3. **Small neural network** (small MLP on the same tabular features). Only if
   it beats (1) and (2) on held-out cases by a pre-registered margin (TBD).

**A language model is NOT a starting point** for these numerical tasks. The
inputs are numbers and the outputs are orderings; an LLM adds nothing except
opacity and cost.

**Sizing (M1 Air constraint):** all three classes are small by design —
tabular inputs, tens of features, training in minutes on a laptop, inference
in milliseconds. If a candidate model needs a GPU cluster, it is the wrong
model for this job.

## 7. Advisory mode first, then control (the promotion protocol)

1. **Advisory mode (mandatory first phase):** the ranker logs its rankings
   while the EXISTING search remains in control. No search order changes.
   Advisory logs are compared against what the existing search actually did:
   would the ranker have ordered the eventual winner earlier? How much compute
   would it have saved? What would it have deprioritized?
2. **Bounded comparison (the promotion test):** on unseen synthetic cases,
   does AI-assisted search achieve AT LEAST baseline recovery performance with
   FEWER full physics fits? Metrics, all pre-registered:
   - Total physics evaluations and wall-clock time.
   - Successful recovery rate (within pre-registered tolerances).
   - False-promotion rate (must not rise vs baseline — the ranker must not
     manufacture discoveries by steering search).
   - Missed cases the original search recovered (the ranker's blind spots,
     reported by case, not averaged away).
   - Performance sliced by case type: null, incomplete-inventory, ambiguous
     multi-body (the slices where a ranker is most likely to mislead).
3. **Promotion to control (separate decision):** only if the bounded
   comparison supports it, and only with rules §3.2 (minimum coverage) and
   §3.3 (fallback) active. Promotion is reversible: any regression on the
   monitored metrics returns the loop to advisory mode.
4. **Ongoing monitoring:** ranker version, training-set identity, and advisory
   vs control mode are recorded per case in the ledger. If the monitored
   metrics drift beyond a pre-registered tolerance (TBD), control reverts to
   advisory pending re-validation.

## 8. Relationship to the rest of the mapper

- **Search ROM vs adjudication ROM (ladder §8):** the ranker feeds the SEARCH
  side only. It reads search history; it never writes posteriors, never touches
  the adjudication tracker, and never ingests checker-gated verdicts as
  training labels (see §5.2 — verdicts are evidence, not search outcomes).
- **Joint interface:** the ranker may suggest multi-body attempts, but Stage B
  execution requires the joint interface (separate design, separate build
  decision). The ranker does not substitute for it.
- **Cost predictor (role 2):** feeds the same search budgeting the Stage B
  cost caps (§7 of the joint-interface spec) will govern. A predicted cost
  never overrides a cap decision made on measured cost.
- **Phase 2:** the ranker assumes post-Phase-2 machinery (isolated checker
  holdout, unified MSE ratios, evidence ledger). Pre-Phase-2 outputs are not
  training inputs, because their meanings are known to be off (holdout not
  isolated, RMS/MSE confusion).

## 9. Open decisions for Jase (nothing here is decided by this doc)

| Decision | Needed before |
|---|---|
| Minimum coverage fraction for lower-ranked candidates/regions (§3.2) | Advisory-mode design |
| Pre-registered margin for the small NN to beat simpler models (§6) | First experiment |
| Advisory-mode duration / case count before the promotion test (§7) | Promotion test |
| Drift tolerance for ongoing monitoring (§7.4) | Promotion to control |
| Training-set size and diversity requirements (§5.3) | Training |
| Build decision for the first experiment (advisory mode only) | Any training |

## 10. Status and sequence

**QUEUED** behind the agreed sequence: validation closeout (DONE 2026-10-26)
→ Phase 2 (RUNNING) → verification → design review → build decision. This
document is design input to the design-review step. No training, no
implementation, and no model inference on live cases is implied or authorized
by this document.

---

*Design v1, drafted 2026-10-26, Jase-authorized ("add whatever you think is
worth adding"). No code written. No model trained. Build decision separate.*
