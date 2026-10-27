# Discovery-Reliability Ladder for the Parent ROM — DESIGN DOC (v1, DRAFT)

**Status:** DESIGN ONLY. No code written, no live file modified, no threshold decided.
This document specifies how the ROM earns reliability as a *standalone discovery
adjudicator* — the step beyond its current clearance (tracking/gating duty on
decided history). It is input to a future build decision, not approval to build.

**Authorship note:** The ROM, the inventor loop, and the conductor competition are
Jase's ideas. This document is Atlas's design work on Jase's architecture.

## 0. What "reliable on independent discovery" means — and what it does not

**Independent discovery** = the ROM, fed only by conductor verdicts on a case whose
truth is unknown to everyone in the loop, promotes the right hypothesis, kills the
wrong ones, or abstains — without a human adjudicating the outcome.

**Reliability** is a property of the ROM *across a battery of cases*, never of a
single case. A single promotion is a posterior: a bet with stated odds, not a proof.
No battery, however large, converts one promotion into a certainty.

**Two claims this ladder keeps separate** (the precision-vs-threshold lesson from
the Gemini cross-check):

- *Criterion-level verification:* the promoted hypothesis beats the bar (e.g. MSE
  ratio ≥ 1.2, posterior above the promotion threshold).
- *Model fidelity:* the winning model reaches the noise floor, and the ROM's stated
  posteriors match empirical frequencies.

A ROM that passes the first while failing the second is a ranking machine, not a
discovery adjudicator. This ladder requires both.

**What this ladder does NOT establish:**

- That the inventor's hypothesis space contains the truth. The ROM can only choose
  among generated hypotheses. If the true explanation is outside the space, the
  correct ROM behavior is abstention (or a flagged expansion request), never a
  confident promotion of the least-wrong body.
- That any single future promotion is correct. Batteries bound error *rates*.
- That systematics are understood. On real open data the systematics are unknown
  by definition; the ladder measures robustness to *modeled* systematics and
  requires conservative behavior (abstain) under *unmodeled* ones.

## 1. Prerequisites — Gate 0 (all must be verified before any battery runs)

Gate 0 is not part of the ladder; it is the ground the ladder stands on. Nothing
below runs until every item is verified in source and in tests.

| # | Prerequisite | Verification |
|---|---|---|
| G0.1 | Phase 2 fixes verified: checker holdout isolation (fix #1), ratio unification (fix #2), evidence ledger (fix #3), atomic ROM save (fix #5), live hygiene | 16/16 regression tests; ROM calibration 13/13; belt replay; Ammonite sealed-truth |
| G0.2 | Closure validation §6 verdict landed (novel case + full verdict) | `rom_loop_closure_note.md` §6 filled; results JSON sealed |
| G0.3 | C-d disposition decided (see §2) | Written decision, pre-registered before batteries |
| G0.4 | MSE-domain contract in force everywhere | All battery metrics computed in MSE domain; RMS used only for display, never for decisions |
| G0.5 | Checker PASS meaning post-Phase-2 | Checker PASS is an independent gate (training-only starts, refit RMS reported, `sol.success` filtered) — not pre-Phase-2 corroboration |

**PROVISIONAL:** Any section below that assumes G0 items is provisional until its
Gate 0 row is verified. Provisional sections are marked.

## 2. The C-d disposition (decision required at Gate 0)

The closure validation found, on a small scratch tracker, that deferral prunes
abstained hypotheses and renormalization then inflates the null (0.961 → 0.9996,
capped at 0.99). The cap worked as designed; the criterion still failed. Two
dispositions are on the table. Choosing one is a Gate 0 decision, made before any
battery, never during one:

- **Option A — explicit unknown/deferred bucket.** Deferred hypotheses' mass is
  held as an explicit "unknown" allocation instead of vanishing by normalization.
  The null then competes with a visible unknown, and promotions must beat both.
  Requires: bucket accounting in the tracker, a rule for when unknown mass converts
  back into a hypothesis (re-test trigger), and a cap on unknown share above which
  the case abstains.
- **Option B — criterion revision with re-registration.** If the unknown bucket is
  judged unnecessary, C-d is revised explicitly (new criterion, new rationale,
  new pre-registration) and the scratch-tracker case is re-run under the revised
  criterion. The original C-d failure stays on the record; it is not erased.

Whichever option is chosen, the disposition is recorded in the closure note and
this document is updated to match. Silent revision is not an option.

## 3. The tuning problem (PROVISIONAL on G0.1–G0.5)

The ROM's behavior is set by knobs, not learned weights. "Training" the ROM means
calibrating these knobs and measuring the result:

| Knob | Current value | Status |
|---|---|---|
| Tempering T (evidence cap) | N/50 | Stated assumption, NOT a measurement |
| Verdict log-odds cap | 5.0 | Guardrail, set by design |
| Posterior cap | 0.99 | Guardrail, set by design |
| Complexity penalty | 0.5·k·log(N_eff) | Design choice |
| Promotion threshold (posterior) | TBD | **Jase to set** |
| Kill threshold (posterior) | TBD | **Jase to set** |
| Surprise trigger thresholds | Coherent split-half structure AND no promotion at holdout ratio ≥ 1.2 | Design choice, to be measured |
| Unknown-bucket allocation | TBD (pending §2) | **Jase to set** |

**Train/test discipline (non-negotiable):**

1. Every battery is split into a TUNING split and a HELD-OUT split before any
   knob is touched. The split is sealed and recorded.
2. Knobs are tuned on the tuning split only, to optimize pre-registered metrics
   (§4.4). The tuning record (knob values tried, metric values, rationale) is kept.
3. The held-out split is run exactly once per knob configuration, with the final
   configuration, and its metrics are the reported result.
4. No knob is ever tuned on the held-out split. If held-out metrics fail the gate,
   the failure is reported, the knobs return to the tuning split, and the held-out
   split is replaced (new cases, new seal) — never re-tuned against the same
   held-out cases.

This is the same discipline as the pre-registered validation criteria: tuning to
pass is the failure mode this ladder exists to prevent.

**How to set the TBD thresholds (guidance, not decisions):** promotion and kill
thresholds trade false discoveries against missed discoveries. The cost asymmetry
is Jase's call: a false discovery costs credibility and downstream work; a missed
discovery costs only delay (the case stays open, the hypothesis stays tracked).
That asymmetry argues for conservative promotion thresholds and liberal abstention.
The numbers themselves are Jase's, set before Battery 1 runs.

## 4. Battery 1 — Synthetic blind discovery

**Purpose:** Measure promotion precision, recall, kill accuracy, and calibration on
cases where truth is known exactly and the loop is fully blind.

### 4.1 Case taxonomy (each case: sealed truth, synthetic observations, inventor
starts from residuals only — never from truth)

- **Single-body cases:** one hidden point mass, spanning mass (sub-Pluto to
  multi-Earth), distance (inner system to 500 AU), and eccentricity. Truth varies;
  the inventor must generate, not be handed, the candidates.
- **Multi-body cases:** two and three hidden bodies, including a co-orbital pair
  and a close pair (separation near the resolution limit). Tests the joint fitter
  and the per-body evidence accounting.
- **Null cases:** no hidden body; residuals are noise only, at the calibrated
  noise level. The correct outcome is null promotion, no body promoted.
- **Systematics cases:** no hidden body, but residuals contain a modeled
  systematic — timing offset, frame offset, correlated noise at a stated level.
  The correct outcome is null promotion OR promotion of a systematics-brain
  hypothesis (§6), never promotion of a body.
- **Incomplete-inventory cases:** a known body omitted from the inventory (the
  phantom lesson, in synthetic form). The correct outcome is the promotion gate
  vetoing single point-mass candidates until inventory is repaired — or a kill
  by inventory, never a confident phantom promotion.

### 4.2 Sealing protocol

- Truth sealed per case (hash recorded) before the loop runs; the checker never
  sees truth; scoring is done by a separate sealed-truth scorer after the loop.
- Per-case checkpoints (conductor verdicts, ROM states, posterior trajectories)
  saved to `sealed_runs/` as the case completes — the same discipline as the
  closure validation.
- Battery size: TBD (Jase to set). Guidance: large enough that a 95% binomial
  interval on promotion precision is narrower than the gate margin — i.e. size
  follows from the gate, not from round numbers.

### 4.3 What the loop must do per case (PROVISIONAL on the joint interface)

- Inventor generates candidates from residuals (no truth input).
- Conductor fits each candidate (Stage A single-body; Stage B joint where the
  multi-body design specifies it — joint interface required, see §8).
- Checker gates each fit (post-Phase-2 independent gate).
- ROM ingests verdicts, updates posteriors, promotes / kills / abstains per the
  §3 thresholds.
- Surprise trigger fires only on coherent split-half structure with no promotion
  at holdout ratio ≥ 1.2; noise never triggers (verified per case).

### 4.4 Metrics (all pre-registered before Battery 1; all in MSE domain)

- **Promotion precision:** of promoted hypotheses, fraction true (truth = within
  pre-registered mass/radius/phase tolerances of a real hidden body).
- **Promotion recall:** of true hidden bodies, fraction promoted.
- **Kill accuracy:** of killed hypotheses, fraction false.
- **False-promotion rate:** promoted hypotheses that are false, per case and overall.
- **Abstention rate:** fraction of cases ending in abstain (reported, not penalized
  — abstention is the safe outcome, and a high abstention rate with high precision
  beats a low abstention rate with false promotions).
- **Calibration curve:** binned ROM posterior vs empirical frequency of truth in
  that bin, across all cases. A calibrated ROM has bins on the diagonal within a
  pre-registered tolerance (TBD).
- **Brier score** (optional summary): mean squared error of posteriors against
  truth indicators, reported alongside the calibration curve, never instead of it.
- **Surprise-trigger audit:** every trigger classified as true novelty / false
  alarm / missed novelty (a case where invention should have fired but didn't).

**Gate 1 (to pass):** precision, recall, kill accuracy, false-promotion rate, and
calibration each meet their pre-registered bars (TBD, Jase to set) on the HELD-OUT
split. Failing any one metric fails Gate 1.

## 5. Battery 2 — Known-body blind recovery

**Purpose:** The closest thing to independent discovery where ground truth is free
and the dynamics are real, not synthetic.

- **Hide-and-rediscover:** remove one known body at a time from the inventory
  (Ceres, Vesta, Pallas, a planet, the belt ring) and require the loop to
  rediscover it blind from residuals. Success = promotion of a hypothesis within
  pre-registered tolerances of the hidden body.
- **Multi-body hide:** remove two bodies simultaneously (e.g. Vesta + Pallas) and
  require both rediscovered — tests joint fitting on real dynamics.
- **Belt replay extension:** the live belt run is Battery 2's pilot case (already
  passed, conditionally). Battery 2 generalizes it: same protocol, more bodies,
  blind starts.
- **Scoring:** same metrics as §4.4, restricted to recovery (precision/recall on
  hidden bodies). Calibration curve extends across Batteries 1+2 pooled.

**Gate 2 (to pass):** all hidden bodies recovered within tolerances on the
held-out set, no phantom promoted, calibration pooled with Battery 1 still within
tolerance. (Thresholds TBD, Jase to set.)

## 6. Battery 3 — Adversarial null and systematics (the false-discovery guard)

**Purpose:** This battery matters most, because false discoveries are the failure
mode that costs credibility. It is also the battery most likely to fail first —
which is information, not embarrassment.

- **Pure-null cases:** real-data residuals with the full inventory modeled
  (planets, Ceres/Vesta/Pallas, belts). Correct outcome: no promotion.
- **Systematics-injection cases:** timing offsets, frame offsets, and correlated
  noise injected at stated levels into real or synthetic residuals. Correct
  outcome: no body promoted. If the systematics-brain hypotheses exist (null as
  competing failure explanations — a queued identifiability proposal), promotion
  of a systematics explanation counts as correct; promotion of a body counts as
  a false discovery.
- **Phantom-regeneration cases:** inventory deliberately left incomplete in a new
  way (different omitted body, different geometry). Correct outcome: gate veto or
  kill by inventory, never phantom promotion.
- **Metric that matters:** false-promotion rate on this battery alone, reported
  separately from Batteries 1+2. A ROM can have excellent precision on discovery
  cases and still be unfit if it promotes bodies on nulls.

**Gate 3 (to pass):** false-promotion rate on null/systematics cases at or below
its pre-registered bar (TBD, Jase to set — expected to be stricter than the
Battery 1 bar, because the cost of a false discovery exceeds the cost of a
missed one).

## 7. Battery 4 — Degeneracy and abstention

**Purpose:** The ROM must handle cases where the data cannot distinguish
explanations — by abstaining or splitting, never by confidently promoting one.

- **Template case:** the co-orbital degeneracy (mass overestimated 267× in the
  earlier validation). Correct outcome: abstain, or posterior split across the
  degenerate family with no single hypothesis above the promotion threshold.
- **Degenerate families:** same-residual families (mass/distance trades, phase
  degeneracies) generated synthetically. For each family, the ROM's posterior must
  spread across the family (measured: top-hypothesis posterior below the
  promotion threshold, family-total posterior reported) rather than collapsing
  onto one member.
- **Identifiability link:** this battery operationalizes the queued identifiability
  proposal — before "which body?", ask "what can these data distinguish?" A
  prediction-Jacobian diagnostic (if built) can pre-flag degenerate cases; the
  battery measures whether the ROM behaves correctly with or without it.
- **Removal-test discipline (from the veto audit):** any claim that a body is
  unnecessary must be a refit with the same data partition, and unconverged
  refits abstain everywhere — never kill.

**Gate 4 (to pass):** no confident promotion on any degenerate-family case
(top posterior below promotion threshold on every such case); family-total
posterior reported for each. (Thresholds TBD, Jase to set.)

## 8. Two memories: search ROM vs adjudication ROM

The single-tracker design conflates two jobs with different risk tolerances.
This ladder requires their separation before shadow mode:

- **Search ROM (aggressive):** guides the inventor — which candidates to fit
  next, where to spend compute. May use looser thresholds; its posteriors are
  search priorities, never discovery claims. May ingest provisional verdicts.
- **Adjudication ROM (conservative):** the only tracker whose posteriors can
  promote a discovery. Ingests only post-Phase-2 checker-gated verdicts (G0.5).
  Uses the §3 promotion/kill thresholds (Jase to set). Never ingests a verdict
  the search ROM produced without a checker gate.
- **Promotion path:** a hypothesis moves from search to adjudication only via a
  checker-gated verdict. There is no direct posterior transfer between the two
  trackers — transfer would launder un-gated evidence into the adjudication
  record.
- **Ledger (fix #3):** both trackers write to the evidence ledger; the ledger is
  what makes the separation auditable (which verdicts entered which tracker,
  when, from which fit).

**PROVISIONAL:** the joint interface (mass-start rule, 6+k optimization) is not
part of Phase 2 and is required for Stage B multi-body fits in Batteries 1–2.
Until it exists, multi-body battery cases are Stage-A-only and Gates 1–2 are
graded on single-body cases, with multi-body cases reported separately as
NOT YET TESTABLE. The joint interface does not get built inside this ladder;
it gets specified (interface spec + bounded prototype scope + preservation route
— the circularity correction) and then built under its own decision.

## 9. Shadow mode (the last gate before standalone use)

**Purpose:** Earn trust on real open questions without risking a false discovery.

- **Protocol:** on the first real open questions, the ROM runs in shadow. Its
  verdicts (promote / kill / abstain, with posteriors) are recorded and sealed,
  but NOT acted on: no discovery is announced, no hypothesis is treated as
  decided, no downstream work assumes the verdict.
- **Comparison:** each shadow verdict is compared against human adjudication
  (Jase + Atlas review of the same case, same evidence). Agreement and
  disagreement are both recorded, with reasons for disagreements.
- **Exit criteria (TBD, Jase to set):** agreement rate over a pre-registered
  number of consecutive shadow cases, with zero false promotions in shadow
  (a shadow false promotion resets the count — shadow mode exists to catch
  exactly that).
- **What shadow mode is not:** it is not a beta test of the thresholds. Thresholds
  are frozen during shadow mode; changing them restarts the shadow count. If a
  threshold change is needed, it goes back to the tuning split (§3), not into
  shadow.

**Gate 5 (to pass):** shadow exit criteria met with thresholds frozen.

## 10. Standalone adjudication — conditions and ongoing monitoring

Standalone adjudication is granted only when Gates 0–5 have all passed, in order,
with their artifacts sealed. It is granted per-case-type, not in general: a ROM
that passes on point-mass cases is not thereby cleared on belt cases or
multi-body cases. Each new case type earns its own battery pass.

**Ongoing monitoring (the ROM stays a living tracker, not a certified oracle):**

- Every standalone verdict is logged with its evidence ledger entries, so any
  verdict can be re-derived.
- A rolling calibration check: as new cases resolve (by later data or independent
  confirmation), posteriors are scored against outcomes. Drift beyond a
  pre-registered tolerance (TBD) triggers re-validation: the ROM returns to
  shadow mode for that case type until recalibrated.
- Any single false promotion in standalone mode triggers an immediate review:
  the case, the evidence, and the knob values are examined before the next
  standalone verdict of that case type. Two false promotions of the same type
  suspend standalone adjudication for that type pending re-battery.
- The unknown bucket (§2) is monitored: if unknown share grows across cases,
  that is evidence the inventor's hypothesis space is missing a class of
  explanation — an inventor problem, surfaced by the ROM, not a ROM failure to
  hide.

## 11. Cost and execution plan

Honest cost accounting, because this battery is heavy:

- A single N-body conductor fit costs ~60–100 s wall (Keplerian path ~2–3 s;
  N-body path ~60 s). A battery case needs several fits (candidates × seeds).
  A 50-case battery is therefore hours of compute, not minutes.
- **Staged execution (the closure-validation pattern):** lean subset first with
  a stated subset rule, checkpoint every fit to `sealed_runs/`, per-fit timeouts
  recorded as findings (not retried silently). Full battery only after the lean
  subset passes its gates.
- **Execution tier:** per the established division of labor, the grind runs on
  Jase's Mac (or a staged subset here for validation of the harness), while
  Atlas audits verdicts. The battery harness itself is a build decision separate
  from this design doc.
- **What is cheap:** the ROM update math itself (posterior arithmetic) is
  negligible. The cost is all in the conductor's fits — which is why the search
  ROM's candidate triage (§8) matters: it decides where the expensive fits go.

## 12. Open decisions for Jase (all TBD — nothing here is decided by this doc)

| Decision | Needed before |
|---|---|
| Promotion / kill posterior thresholds | Battery 1 |
| Calibration tolerance (bin deviation) | Battery 1 |
| Battery sizes (cases per battery) | Battery 1 |
| Gate bars for precision / recall / kill accuracy / false-promotion rate | Respective gates |
| C-d disposition (§2, Option A or B) | Gate 0 |
| Shadow-mode length and agreement rate | Shadow mode |
| Standalone drift tolerance | Standalone grant |
| Joint-interface build decision (separate from this ladder) | Multi-body battery grading |

## 13. What success looks like — and what it does not buy

**Success** = a ROM whose stated odds match measured frequencies across blind
batteries, that abstains on degenerate and null cases, that survives shadow mode
without a false promotion, and whose every verdict can be re-derived from its
evidence ledger.

**Success does not buy:**

- Certainty on any single case. A 0.95 posterior is still a 1-in-20 bet.
- Coverage of explanations the inventor never generates. The ROM is bounded by
  its hypothesis space, and the unknown bucket is the honest marker of that bound.
- Freedom from re-validation. Systematics change, data change, case types change;
  the monitoring in §10 is part of the design, not an afterthought.

---

*Design v1, drafted 2026-10-26, Jase-authorized. Provisional sections marked.
No code written. No thresholds decided. Build decision separate.*
