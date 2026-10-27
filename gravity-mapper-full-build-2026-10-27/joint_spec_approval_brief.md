# Joint-Interface Spec Approval Brief — DECISION BRIEF, NOT A DECISION (D9)

**Status:** BRIEF ONLY. This document lays out what approving the
joint-interface specification would authorize, what it would not, and
the risks, so Jase can decide D9. It decides nothing. No code is written
or modified by this brief.

**Decision requested (D9):** approve the joint-interface specification
(`hidden_files/joint_interface_spec_design.md`, 2026-10-26) as the basis
for a bounded prototype build — or approve with changes, or defer.
Implementation of the prototype is a separate dispatch AFTER approval.

## 1. What the spec is (grounded, not aspirational)

The spec was verified against the live code before drafting (per the
cost-measurement circularity correction: spec approval BEFORE
implementation, cost measured AFTER the prototype exists):

- **Current limitation (verified):** `fit_state` fits 6 parameters only
  (tracer state); `NBodyParticle.planet_mu` is fixed; `check_fit` uses
  full-data train RMS plus a full-data hint refit; `ExtraRails` masses
  are fixed at construction. There is currently NO driver that fits
  tracer state + perturber masses jointly.
- **Spec core:** θ = tracer state (6) + log10 masses (k masses, solar
  masses internally, Earth masses for display only). Fixed context =
  inventor radii/phases, rails, t_ref, tolerances. **Stage B frees
  MASSES only** — radii and phases stay at inventor values.
- **Per-trial rebuild:** perturber accelerations are rebuilt per trial
  (geometry fixed, masses are the trial variables) — the joint fit
  varies masses, not geometry.
- **Driver discipline (reused from `fit_state`):** multi-start,
  best-cost among COMPLETED starts only, success filtering before any
  early stop. The joint driver inherits the single-body driver's
  honesty rules; it does not invent new optimizer semantics.
- **Checker discipline (spec-driven):** train-refit RMS gates, NEVER
  full-data RMS; MSE ratio (Phase 2 definition); verbatim reporting
  including the start rule. The Phase 2 checker fix (no full-data hint)
  is built into the spec, not bolted on after.
- **Starts:** strict mass-start default (training-only). Full-data
  starts are permitted ONLY labeled as corroboration, never as the
  primary fit.
- **Removal:** removal = refit on the same partition. Frozen removal
  (removing a body without refitting) is prohibited; an unconverged
  removal refit → abstain, never a verdict.
- **Scoring:** log MSE ratio capped at 5.0 + prior offset −5.87/body at
  creation, with the four numbers reported verbatim (same scoring
  discipline as the single-body ROM path).

## 2. What approval authorizes (bounded prototype only)

Per the spec §6 and the review's Amendment 1 permission table
(prototype = measurement instrument, not integrated-design approval):

- **NEW FILES ONLY.** The prototype lives in new files; it does not
  modify existing brains, the checker, the optimizer, or any live code.
  Live code never imports the prototype until a SEPARATELY authorized
  promotion decision. A prototype failure cannot break the live fitter.
- **Deliverables:** (a) generalized driver + spec-driven checker entry;
  (b) k = 0 regression proof — the prototype with zero perturbers must
  reproduce `fit_state` within a pre-declared tolerance (D11, see §4);
  (c) k = 1 synthetic demo (known-truth case, sealed, strict starts);
  (d) removal test on the same partition; (e) measured cost table
  (wall time, nfev, predict time, checker-refit time vs k).
- **Cost measurement is the prototype's PURPOSE.** The veto v2 draft
  figure "5–10× Stage A" is UNMEASURED and is superseded by the measured
  table. No cost claim may be made before the table exists.

## 3. What approval does NOT authorize (explicitly out of scope)

- Integrated multi-body design approval (the fitter + veto as a
  validated whole — still NOT READY, awaiting ladder + survey +
  partition + D1).
- Open-question Stage B use (needs measured cost + caps re-confirmed
  (D12) + cost acceptance (D14) + the ladder gates).
- Live ROM ingestion of multi-body verdicts (needs D1 implemented +
  re-tested, i.e., ladder Gate 0).
- Existing-brain behavior changes; freeing radii/phases; the full
  ladder; survey work; the battery harness; any threshold change
  (ACCEPT_RATIO, caps, N_EFF_CAP); any evaluator-default change.
- Any claim that joint fitting "works" — the prototype demo is a
  measurement on synthetic data, not a validation of the design.

## 4. Open items inside the approval (set before or during prototype work)

- **D11 — k = 0 regression tolerance (prototype plan):** the spec
  leaves the tolerance TBD. It MUST be set in the approved prototype
  plan BEFORE the regression proof runs — otherwise the proof has no
  bar. The tolerance must be justified from optimizer noise scale
  (the fit-comparison work showed ratio differences ~1e-5 from
  optimizer stopping paths alone), not chosen after seeing the result.
  Setting it after the fact would be criterion-shopping.
- **D10 — log-mass scan design + bounds (prototype design):** the
  prototype plan must state the mass scan (inventor value ± decades vs
  fixed grid) and bounds before demo runs.
- **D12 — Stage B budget caps (re-confirm AFTER measurement):** draft
  caps (3 bodies / 5 candidates / 60 min) are placeholders until the
  measured table exists. Approval of the spec does not approve the
  caps.
- **D14 — cost-measurement acceptance:** Jase accepts (or rejects) the
  measured table as the basis for caps. The table alone does not
  authorize open-question use.

## 5. Risks and mitigations

1. **Prototype drift.** If the prototype diverges from `fit_state`
   discipline, its cost numbers do not transfer to the real fitter.
   Mitigation: the k = 0 regression proof gates everything else — if
   it fails, the prototype stops, it does not proceed to demo.
2. **Start leakage.** A full-data start smuggled into a primary fit
   would repeat the Phase 2 checker flaw the spec was written to avoid.
   Mitigation: strict training-only default + corroboration labeling
   enforced in the prototype's reporting (start rule verbatim).
3. **Scope accretion.** A prototype that quietly grows into the fitter
   bypasses the ladder. Mitigation: new-files-only + no live imports +
   promotion as a separate decision with its own gates. Any prototype
   change that touches live code is out of scope and stops the batch.
4. **Cost surprise.** If measured cost explodes with k, open-question
   Stage B may be impractical regardless of correctness. Mitigation:
   none needed at approval time — that is exactly what the measurement
   is for, and D12/D14 exist to act on it.

## 6. Relationship to other pending work (no hidden dependencies)

- **D1 (bucket) does NOT block this.** Per review Amendment 1 §7.3,
  the prototype takes explicit candidate inputs on synthetic
  sealed-truth data, never consolidates into the live ROM, and never
  uses deferral paths. Prototype work and bucket work proceed in
  parallel.
- **Survey pass (D13) does NOT block this.** The survey table gates
  veto trust, not prototype construction.
- **Test partition (D15) does NOT block this.** The partition gates
  final evaluation / open-question runs, not prototype demos on
  synthetic data.

## 7. Assessment (recommendation, not a decision)

Atlas recommends APPROVAL of the spec as the prototype basis: it is
grounded in verified code limitations, its scope is bounded to new
files, its acceptance is measurable (regression proof + demo + removal
test + cost table), and its failure modes have gates (regression proof
first, no live imports, promotion separate). The one condition Atlas
would attach: D11 (regression tolerance) and D10 (mass scan) must be
set in the prototype plan BEFORE their respective runs execute — set
prospectively, never after seeing results. If Jase prefers, those two
can be decided alongside this approval rather than deferred into the
plan.

**What happens next for each decision:**

| Decision | Immediate next step |
|---|---|
| Approve | Bounded prototype implementation batch (new files, §6 scope), then cost table → D12/D14 |
| Approve with changes | Spec amended per Jase's changes, then prototype batch on the amended spec |
| Defer | Nothing changes; joint work stays at design; prototype, cost, and caps all stay pending |

---

*Decision brief, drafted 2026-10-26, continuation work. Decides
nothing. Prototype implementation requires a separate dispatch after
Jase's D9 decision. No thresholds, code, or ROM entries are changed by
this brief.*
