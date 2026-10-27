# Mac-source adoption note — stage gate, sealed scenarios, recommendation controller

**Date:** 2026-10-13
**Task:** Adopt three Mac-source components into the Atlas pipeline (adapt, don't transplant).

## 1. What was adopted, from where

| # | Component | Mac source | Atlas port | Lives at |
|---|---|---|---|---|
| 1 | Stage-gate runner | `source_upload/engine/stage_gate.py` (PASS_RULES / STAGE_ORDER / evaluate_stage_gate, PASS/HOLD, next_stage); ingest pattern from `engine/benchmark_ingest.py` + `adapters/benchmark_adapter.py` | `hidden_files/stage_gate_runner.py` | report: `hidden_files/stage_gate_report.json` |
| 2 | Sealed-truth scenarios | `source_upload/gravity_mapper/catalog/scenarios.py` (sealed `_inference.json` / `_truth.json`, "truth open only after inference"); recovery criteria from `catalog/catalog_recovery.py` (mass ≤50%, radius ≤35%, phase ≤0.55 rad) | `hidden_files/sealed_scenarios.py` | manifests+scores: `hidden_files/sealed_runs/`; null-model cache: `hidden_files/sealed_cache.npz` |
| 3 | Recommendation controller | `source_upload/gravity_mapper/controller/recommend_next.py` (recommendation-only; status/reason/next_action/command; auto_run_allowed=False; unknown → REVIEW_REQUIRED) | `hidden_files/recommend.py` | — (prints only) |

Supporting: `hidden_files/stage_inputs/` (machine-readable attestations for S2/S3/S5, each with a `source_note` pointer to the verified note it came from).

Provenance labels: every ported file's docstring names the Mac source file it was adapted from; Atlas-authored logic is not presented as Mac-derived. The four protected files (`real_data/residual_hunt.py`, `real_data/tno_hunt.py`, `hypothesis_tracker.py`, `pbh_gamma_classifier_v9.py`) were **not modified** (mtimes verified old).

## 2. What was adapted and why

**Stage gate.** The Mac gate ran over 2D synthetic-sim logs. The Atlas gate defines five stages for the real 3D workflow and reads REAL pipeline outputs:
- **S1 null_validation** — inner + TNO nulls from `hunt_results.json` / `tno_hunt_results.json`. Thresholds sit between verified-good and known-bad: inner holdout MSE ≤1e-7 (verified 7.2e-9; v1-bad was 8e-2), TNO growth ≤2.5 (verified 1.58; the +y systematic was 4.02 — the gate would have caught it).
- **S2 known_body_recovery** — V3 Mercury blind recovery (attested): mass err ≤1% (verified 0.11%), radius err ≤2% (verified 0.026%).
- **S3 blind_model_selection** — V1 null must not false-positive; V2 must detect (attested).
- **S4 real_data_hunt** — per-hunt verdict from refined candidates: **CLEAN_NULL** (best ho_improvement <1.05 and all dBIC <0 → PASS, "null trustworthy"), **EARNED_DETECTION** (ho ≥2.0 and dBIC >10 → PASS with detection flag; coherence confirmed in hunt note), else **GRAY_ZONE → HOLD**. A clean null passing is deliberate: the gate certifies pipeline health, and the verified outcome *is* the null.
- **S5 classifier** — v9 benchmark zero misclassifications + 19/19 wrapper regression (attested).
- `next_stage`: `advance` (all pass) / `investigate_gray_zone` / `hold_and_fix`.

**Sealed scenarios.** The Mac framework withholds catalog planets from a 2D sim. Here scenarios inject a synthetic hidden body into the REAL TNO null residuals (74 TNOs, v3 cleaned null, 239 km noise floor) via the Atlas 3D variational propagator; the solver is grid + Nelder-Mead + `HypothesisTracker` with a 3D scorer subclass (the base class's `score_hypothesis` is hardwired to the Mac 2D sim, so it is overridden — base-class propose/update/posteriors/prune reused unchanged). Seal discipline: `solve` never opens the truth file (separate CLI subcommands; `truth_manifest_open_only_after_inference` flag in the inference manifest, same as Mac).

**Recommendation controller.** Same contract as Mac (suggest-only, never executes). Policies wired to Atlas artifacts: stage HOLD/MISSING → investigate (with the failing metric); sealed null_control failure → HALT (solver invents bodies; nothing downstream trustworthy); sealed miss → expand solver; v9 domain warnings → fold real observations; all green → advance.

## 3. Sealed scenarios created

| Scenario | Truth | Result |
|---|---|---|
| `mercury_like` | 1.6e-7 M☉ @ 5 AU, φ=2.0 (mirrors verified V3) | **RECOVERED** — mass err 1.9%, radius err 1.0%, phase err 0.020 rad; tracker MAP posterior 1.0 |
| `distant_heavy` | 1.0e-4 M☉ @ 100 AU, φ=1.0 | **RECOVERED** — mass err 1.1%, radius err 0.1%, phase err 0.002 rad; tracker MAP posterior 1.0 |
| `null_control` | none | **RECOVERED** (correct null) — null posterior 0.99999999997, no false positive |

Note: an earlier draft scenario (10 M⊕ @ 400 AU, Planet-Nine-like) was dropped before running: its 15-yr residual signal (~124 km) sits far below the 3,282 km noise floor, so it could not be recovered at any grid density — recorded here as a sensitivity bound, not a scenario.

## 4. Verification (no-regress)

- `test_v9_wrapper_fix.py`: **19/19 pass** (classifier untouched by this work).
- `stage_gate_runner.py`: all 5 stages PASS on current artifacts; report written.
- `sealed_scenarios.py all`: 3/3 recovered end-to-end (make → solve → score), ~2 min total.
- `recommend.py`: returns ALL_GREEN_ADVANCE on current state; auto_run_allowed=False.
- Protected files unmodified: `residual_hunt.py`, `tno_hunt.py`, `hypothesis_tracker.py`, `pbh_gamma_classifier_v9.py` (mtimes predate this task).
- New files only: `stage_gate_runner.py`, `stage_inputs/*.json`, `sealed_scenarios.py`, `sealed_cache.npz`, `sealed_runs/`, `recommend.py`, this note.

## 5. Honest limits

1. **Same-model tests.** Injection and solving share the variational propagator, so the sealed scenarios verify *inference* (can the solver recover truth?) not the *forward model* (is the propagator right?). Same limitation as the Mac catalog tests. Forward-model validation remains S1/S2's job.
2. **Attestations are human-verified records, not live checks.** S2/S3/S5 read JSON attestations transcribed from verified notes. If the underlying runs are superseded, the attestations must be re-issued by hand — the gate cannot detect stale attestation.
3. **S4's "earned detection" bar is untested.** No real hunt has produced a candidate clearing ho≥2.0 + dBIC>10, so that branch has never fired; the coherence requirement it references lives in hunt notes, not in code.
4. **Controller policies are narrow.** Like the Mac original, anything outside the coded policies is not specially handled (though the stage-gate checks run first and catch most unknown-bad states as HOLD).
5. **Circular-ecliptic candidates only.** The scenario propagator assumes circular prograde ecliptic orbits, matching the hunts' candidate model — eccentric/inclined hidden bodies are outside the tested envelope.
6. **Inner tracers not covered.** Scenarios run on the TNO null model only; the inner (Ceres/Earth/Mars/Vesta) hunt has no sealed-scenario counterpart yet.
