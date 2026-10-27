# Joint-Interface Specification for the Multi-Body Fitter — DESIGN DOC (v1, DRAFT)

**Status:** DESIGN ONLY. No code written, no live file modified.
This document is the pre-implementation approval package for the joint
fit/check interface: the interface specification, the bounded prototype scope,
and the preservation route. Per the circularity correction, these are approved
BEFORE implementation; cost is measured AFTER the prototype exists; validation
plus acceptable cost are required BEFORE any open-question use.

**Why this document exists:** the multi-body design (v2 §2.3) requires a Stage B
joint fit — tracer state plus one free mass per candidate body (6 + k
parameters). No such routine exists. `optimizer_brain.fit_state` optimizes exactly
6 parameters; `rom_closure.PerturbedParticle` fixes candidate masses at
construction via `ExtraRails`; the current checker refits tracer state only and
closes over full-data masses in `predict_fn`, so joint holdout is never
validated. Phase 2 fix #1 (checker holdout isolation) does NOT cover this: it
repairs the 6-parameter checker, while this interface generalizes to 6 + k.
Without this interface, Stage B has no optimizer and no refit, the fitter
degrades to Stage A only, and the multi-body rows of the ladder's Batteries 1–2
are NOT YET TESTABLE.

**Authorship note:** The five-brain architecture and the multi-body fitter are
Jase's ideas. This specification is Atlas's design work on Jase's architecture.

## 1. Current machinery (grounding — what exists today)

| Component | Current capability | Limitation for joint fitting |
|---|---|---|
| `optimizer_brain.fit_state(ts, obs, predict_fn, t_ref, n_starts=8, seed, max_nfev=500, mu, x0_hint, early_stop_rms)` | Multi-start LM fit of Cartesian state (r0, v0) at t_ref; best-cost selection among COMPLETED starts; early stop at noise floor; unphysical trial → predict returns None | Parameter vector is exactly 6; `predict_fn` signature is `predict(x, ts, t_ref)` with x 6-dimensional |
| `particle_brain.NBodyParticle(rails, mu, rtol=1e-9, atol=1e-11)` | DOP853 propagation against planet rails; `_rhs` sums fixed `planet_mu` (PLANET_MU) terms | Planet masses fixed; no candidate-perturber term with variable mass |
| `checker_brain.check_fit(fit, ts, obs, predict_fn, sigma, t_ref, holdout_frac=0.30, seed, early_stop_rms)` | Gates: converged, physical (a > 0, 0 ≤ e < 1), noise_consistent (train_rms ≤ 5σ), holdout via train refit from full-data state hint | `train_rms` is the full-data fit's RMS, not the refit's (Phase 2 fix #1 addresses this for 6-param); refit closes over full-data masses in `predict_fn` for joint models |
| `rom_closure.ExtraRails` / `PerturbedParticle` | Candidate bodies as fixed Keplerian rails added to the N-body propagation | Masses fixed at construction (`from_bodies`); cannot serve masses that change during a fit |

**Design rule following from this table:** the joint interface is ADDITIVE. It
adds a generalized driver and a spec-driven checker entry point. It does not
change `fit_state`, `check_fit`, `NBodyParticle`, or `PerturbedParticle`
behavior. Existing 6-parameter paths keep working exactly as they do, and the
generalized driver must reproduce `fit_state` results on 6-parameter cases
within tolerance (prototype acceptance, §6).

## 2. The model specification (the interface itself)

A joint model is described by a **spec object** — plain data, not code
behavior — that every brain consumes. The optimizer fits it, the particle
propagates it, the checker gates it, the conductor sequences it, and the ROM
scores it. No brain may close over spec values the others cannot see.

### 2.1 Parameter vector

```text
θ = [ tracer state (6): rx, ry, rz, vx, vy, vz  (AU, AU/yr, at t_ref),
      log10 masses (k): log10(m_1), ..., log10(m_k)  (masses in solar masses) ]
```

- **Tracer state:** identical conventions to `fit_state` (Cartesian state at
  `t_ref`, same physicality test as `particle_brain._physical`).
- **Masses:** log10-transformed for positivity. Internal unit is solar masses,
  consistent with `MU_SUN` / `PLANET_MU`; display conversion to Earth masses
  (1 M⊕ = 3.003e-6 M☉) is presentation only and never enters the fit.
- **Fixed context (NOT parameters, carried by the spec):** each candidate body's
  radius and phase at inventor values (Stage B frees masses ONLY — radii/phases
  stay fixed per v2 §2.3; freeing full orbits is a later extension, not this
  interface), the planet rails, `t_ref`, integrator tolerances
  (rtol/atol, same defaults as `NBodyParticle` unless the spec overrides with
  justification), and the data partition (train/holdout split definition).
- **Bounds:** log-mass bounds are part of the spec (default: a stated decade
  range around the inventor value, TBD by the prototype — see §8). Trials
  outside bounds or failing physicality are REJECTED, not fitted (same
  discipline as `fit_state`'s None-predict → residual penalty pattern).

### 2.2 Prediction function of the FULL parameter vector

```text
predict_joint(θ, ts, t_ref) -> (n, 3) positions, or None if unphysical
```

- **Per-trial rebuild (the core requirement):** perturber accelerations are
  rebuilt from the CURRENT trial masses on every evaluation. Candidate bodies
  are propagated as Keplerian orbits from their fixed inventor elements
  (radius/phase fixed, geometry fixed); only their masses vary. The tracer's
  acceleration sums the Sun, the planet rails (fixed), and the candidate terms
  with trial masses:
  `a += Σ_j μ_j(θ) · (d_j/|d_j|³ − r_j/|r_j|³)`, same direct+indirect form as
  `NBodyParticle._rhs`.
- **Why fixed `ExtraRails` cannot serve this:** `ExtraRails` bakes masses into
  rails at construction. A trial mass change must change the acceleration
  without rebuilding rails geometry — geometry (positions) is fixed, masses
  are trial variables. The generalized driver owns this rebuild.
- **Unphysical handling:** unphysical tracer state OR non-finite/out-of-bounds
  mass → predict returns None → the trial is rejected (optimizer penalty
  path, identical in spirit to `fit_state`'s `_BIG` handling).

### 2.3 Generalized driver

```text
fit_model(ts, obs, spec, n_starts, seed, max_nfev, early_stop_rms) -> fit dict
```

- **Multi-start LM over arbitrary-length θ**, reusing `fit_state`'s discipline
  verbatim: best-cost selection among COMPLETED (successful) starts ONLY;
  success required before early stopping; early stop at the noise floor;
  deterministic given seed.
- **Starts (training data only — see §3):** tracer state from the existing
  data-driven start (`cartesian_lm_fitter.data_driven_start`) plus perturbations;
  masses from a training-only scan (design: inventor value plus decade-bracketing
  values, exact scan TBD in prototype — see §8). The conductor's `x0_hint`
  warm-start pattern is available for the tracer state ONLY when the hint comes
  from training data (a Stage A training fit, never a full-data fit).
- **Fit dict:** same shape conventions as `fit_state`'s return (success flag,
  best parameters, RMS, elements for the tracer, per-start record), extended
  with the fitted masses and the spec identity (so the checker and the ledger
  can verify they are gating the same model that was fit).

### 2.4 Spec-driven checker

```text
check_model(fit, ts, obs, spec, sigma, holdout_frac=0.30, seed, early_stop_rms)
  -> verdict dict (PASS / FAIL / ABSTAIN, gates, reasons, numbers)
```

Gates keep their meanings from `check_fit`; their implementation becomes
spec-driven:

- **Converged:** optimizer success flag from the generalized driver.
- **Physical:** tracer elements physical (a > 0, 0 ≤ e < 1) AND all fitted
  masses finite and positive (in linear mass, after inverse log transform).
- **Noise-consistent:** the TRAINING REFIT's RMS ≤ 5σ — computed from the
  refit itself, never from the full-data fit's RMS. (This is the Phase 2 fix #1
  correction, applied to the joint case. The full-data RMS may be reported for
  display but must never gate.)
- **Holdout:** the data are split by the spec's partition (default: last 30%
  by time, as `check_fit`); the model is REFIT on training data only through
  the generalized driver under the §3 mass-start rule; holdout predictions are
  evaluated on the held-out split; the MSE ratio (null holdout MSE / joint
  holdout MSE) is reported in MSE domain (post-Phase-2 fix #2 contract).
- **What is reported verbatim (never summarized away):** train-refit RMS,
  holdout RMS, holdout MSE ratio, fitted masses with uncertainties if available,
  start rule used (strict vs pragmatic, §3), and the spec identity.

### 2.5 Conductor entry point (design-level name)

`run_multibody_ladder` (design-level name; actual name TBD in prototype) wraps
the existing `run_ladder` for rung 1 and adds rungs 2–3. The conductor does NOT
fit; it sequences spec construction → Stage A → (Stage B if Stage A promotes)
→ spec-driven checker → verdict. Rung-to-rung escalation follows v2 §2.1–2.2.

## 3. Mass-start rule (decided, restated normatively from v2 §2.3)

- **STRICT by default for acceptance.** All 6 + k parameters are cold-started
  or training-scan-started, and the refit runs on training data only. This is
  the true independent gate: no full-data information enters the refit through
  starts, hints, or closed-over masses.
- **PRAGMATIC variant permitted ONLY as labeled corroboration:** full-data
  Stage B masses as starts, refit on training data only, permitted ONLY when
  the strict refit fails to converge. Its result is recorded as corroboration,
  never as acceptance.
- **The design picks strict, not both.** Any acceptance verdict resting on
  pragmatic starts is a record-keeping bug, detectable from the checker's
  verbatim start-rule report (§2.4).

## 4. Per-body contribution test (removal refit — needs this interface)

From v2 §2.4(iii), restated as an interface requirement:

- Removing ANY single body from the joint model must worsen holdout MSE by
  ≥ 1.2× (each body earns its place).
- **The reduced model is REFIT:** remaining masses re-optimized through the
  generalized driver on TRAINING data only, evaluated on the SAME partition as
  the joint test.
- **Frozen-parameter removal is PROHIBITED.** It handicaps the reduced model
  (its remaining masses were optimized jointly, not for the reduced model) and
  OVERSTATES the removed body's contribution, making the test too easy to pass.
- **Unconverged reduced refit → abstain everywhere** for that body's
  contribution claim (never kill, never promote on an unconverged comparison).

## 5. Scoring interface (ROM ingestion)

- **Verdict contribution:** log(joint MSE ratio), capped at 5.0 — exactly as
  `add_verdict` implements. No penalty is subtracted from the verdict.
- **Prior offset:** each added body carries −5.87 log-odds at hypothesis
  CREATION (0.5·k·log(N_eff), k = 3 search dimensions, N_eff = 50), applied
  ONCE, never per verdict or per round. The evidence ledger (Phase 2 fix #3)
  prevents re-application.
- **Four numbers recorded verbatim per joint verdict:** MSE ratio, prior
  penalty, net (prior + evidence), posterior before/after. A model CAN be
  promoted on evidence (ratio ≥ 1.2) while ranking below the null on posterior;
  that outcome is reported verbatim as "promoted on evidence,
  posterior-declined on prior", never smoothed over.

## 6. Bounded prototype scope (what gets built first, and what it must show)

The prototype is the smallest build that proves the interface works and lets
cost be measured. It is NOT the multi-body fitter.

**Prototype deliverables:**

1. **Spec object + generalized driver** (§2.1–2.3) as NEW files (e.g.
   `joint_driver.py`, `model_spec.py` — names TBD in prototype). No edits to
   `optimizer_brain.py`, `particle_brain.py`, or `checker_brain.py` except
   through Phase 2's own changes.
2. **Spec-driven checker entry point** (§2.4) as a NEW function (e.g.
   `check_model` in a new module or alongside `check_fit` without altering
   `check_fit` behavior).
3. **Regression proof:** the generalized driver reproduces `fit_state` results
   on 6-parameter cases (k = 0) within a stated tolerance (TBD — e.g. RMS
   agreement to 1e-9 AU or parameter agreement to 1e-6 relative; exact bar TBD
   in prototype plan). This proves the generalization did not break the base case.
4. **Two-body joint demonstration (k = 1):** a synthetic case with known truth
   (one hidden body, sealed truth): strict-start joint fit + spec-driven checker
   gate, end to end, with the §4 removal test (k = 1 removal = null comparison)
   and verbatim reporting (§2.4, §5).
5. **Cost measurement** (§7) on the demonstration cases.

**Explicitly OUT of prototype scope:** open-question use; live ROM ingestion;
changes to existing brains' public behavior; freeing radii/phases (Stage B
frees masses only); the full rung ladder (`run_multibody_ladder` is specified
here but built only after the prototype is accepted); survey-table work;
battery-harness construction.

**Prototype acceptance (all required):** regression proof passes; k = 1
demonstration passes its checker gate with strict starts; removal test behaves
as specified (refit, same partition, abstain on non-convergence); cost measured
and reported (§7); no existing test regresses (16/16 Phase 2 regressions still
pass, ROM calibration 13/13, belt replay, Ammonite sealed-truth).

## 7. Cost measurement protocol (measured AFTER the prototype exists)

Per the circularity correction, cost is NOT a pre-build prerequisite — it is a
post-prototype measurement that gates open-question use.

**Measure, on the demonstration cases and on k = 0/1/2/3 synthetic cases:**

- Wall seconds per joint fit (total and per-start), vs Stage A single-body fit
  on the same data.
- Number of function evaluations (nfev) per fit and per start.
- Per-predict cost (single trajectory propagation with trial masses).
- Scaling with k (fit time vs number of free masses) and with data size.
- Checker cost: strict refit wall time (the gate's price, not just the fit's).

**Report as:** a table (k, wall s, nfev, predict s) plus the scaling trend, on
stated hardware (VM here vs Mac grind tier — both if available). The v2 §2.6
"5–10× Stage A" estimate is UNMEASURED and predates this interface; it is
superseded by the measured table, not adjusted by opinion.

**Decision the measurement informs:** whether Stage B fits within the v2 budget
caps (3 bodies / 5 candidates / 60 min per case — caps themselves TBD for
re-confirmation once measured). If measured cost exceeds the caps, the options
are: reduce candidates, reduce starts, tighten tolerances with re-validation,
or raise the caps with Jase's approval — in that order, never silent overrun.

## 8. Preservation route

- **Prototype location:** new files under `hidden_files/` (same directory as
  the brains), never overwriting existing modules. Live code never imports the
  prototype until the prototype is accepted AND its promotion is separately
  authorized.
- **Sealing:** prototype test cases sealed (truth hash recorded); results in
  `sealed_runs/`; per-fit checkpoints as they complete (closure-validation
  discipline).
- **Drive backup:** milestone backup on prototype acceptance (prefixed files,
  as with prior milestones); delta-sync into the full-build folder if any
  live file changes (none expected from the prototype itself).
- **Failure handling:** if the prototype fails acceptance, it is discarded or
  revised under a new plan. Live code is untouched by the failure either way —
  that is what "preservation" means here: the prototype cannot break the
  working fitter, because the working fitter does not depend on it.
- **Promotion path (separate decision):** prototype acceptance does NOT promote
  the interface into live code. Promotion requires: prototype acceptance +
  cost within caps (or caps re-approved) + Phase 2 verified + a separate
  go-ahead. Until then, the interface is a proven prototype, not live machinery.

## 9. Dependencies and degradation (what happens without this interface)

| Without the interface | Consequence |
|---|---|
| No generalized driver | Stage B cannot run; fitter is Stage A only (fixed-perturber fits) |
| No spec-driven checker | Joint holdout is never validated; any joint claim is corroboration at best |
| No removal refit | Per-body contribution is unverified; rung-k promotion must not rely on it |
| No cost measurement | Stage B budget caps are guesses; open-question use is not costed |

With the interface (and Phase 2 verified): Stage B acceptance becomes possible;
the ladder's Batteries 1–2 multi-body grading becomes possible; v2 §6 joint rows
become gradeable. None of that is true today, and this document does not pretend
otherwise.

## 10. Open decisions for Jase (nothing here is decided by this doc)

| Decision | Needed before |
|---|---|
| Approve this spec + prototype scope + preservation route | Prototype build |
| Log-mass scan design (inventor value ± decades vs fixed grid) and bounds | Prototype build |
| Regression tolerance for the k = 0 reproduction proof | Prototype plan |
| Prototype file names and module layout | Prototype build |
| Stage B budget caps (re-confirm after cost measurement) | Open-question use |
| Promotion of the accepted prototype into live code | After prototype acceptance |

---

*Design v1, drafted 2026-10-26, Jase-authorized (continuation of the ladder
design work). No code written. No live file modified. Approval of this spec is
a separate decision from authorization to build the prototype.*
