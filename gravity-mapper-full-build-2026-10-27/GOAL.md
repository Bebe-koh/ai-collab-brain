# Gravity Mapper hidden-body inference

Goal ID: goal_504fc2c41fb4
Goal slug: gravity-mapper-hidden-body-inference

## Description
Build a simulation-first system that infers hidden gravitating bodies from orbital and motion signals. Work proceeds through a gated benchmark ladder from known-body recovery to blind model selection, with a complete source-code handoff document as the near-term deliverable.

## What it is
Simulation-first system for inferring hidden gravitating bodies from observed
orbital/motion signals. Separate project from PRTP (pulsar timing) — do not
conflate them.

## Source files location
The code lives on Jase's MacBook Air (project dir `gravity-mapper/`), NOT in
this workspace. Jase said the data can be retrieved when needed — i.e. he will
provide a zip / the .py files when we need them. Do not claim to have the
source until he uploads it.

## Benchmark ladder (as reported 2026-09-19)
1. Known-body phase recovery: 20/20 — mass err 0.461%, radius err 0.145%, phase err 0.0282 rad
2. Two-body recovery: 20/20 — mass errs 2.406%/2.046%, radius errs 0.301%/0.266%
3. Two-body refinement: 20/20 — mass errs 0.702%/1.089%, radius errs 0.231%/0.248%
4. Eccentric-body recovery: 20/20 — mass err 0.449%, radius err 0.112%, ecc err 0.0049
5. Blind inner-system radius: 10 runs — mean phase err 0.04472, holdout MSE 1.096e-9
6. Blind model selection: 6 runs — 2-source model selected 6/6, correct config only 1/6, forecast improvement 77.24%
7. Catalog-constrained refinement: 1 run — FAILED on Mercury-like candidate (mass err 502%, radius err 55%, phase err 2.29 rad)

## Architecture (from handoff, unverified against source)
- `gravity_mapper/`: simulation.py, forward_model.py, inference.py, refinement.py,
  validation/ (7 benchmark scripts), catalog/
- `engine/`: benchmark_ingest.py, stage_gate.py, stage_report.py, recommend_next.py
- Stage-gate system: ingest CSV → summary stats → PASS/HOLD vs thresholds → next-stage recommendation. Deliberately constrained, not free-running.

## Binding constraint
Blind structural identification. Local parameter recovery is strong; the system
detects "the simple model is incomplete" but recovers the correct hidden
configuration in only 1/6 blind trials, and catalog-constrained refinement
failed badly once.

## Near-term deliverable
Complete Markdown handoff with real source embedded: every .py file, file-by-file
explanation, exact run commands, benchmark results, dependencies, continuation
plan. **DELIVERED 2026-10-13:** hidden_files/source_handoff.md (Mac source pulled from Drive, 67 .py files inventoried, diffed vs Atlas pipeline with canonical verdicts). Former blocker (project files from Jase's Mac) cleared.

## Recommended next work (from handoff)
1. Known-object catalog layer with orbital priors/masses/radii/phase conventions
2. Catalog matching as hypothesis ranking, not unconstrained optimization
3. Multi-start + global candidate proposals before local refinement
4. Top-k candidates evaluated on held-out forecast metric
5. Dual-eccentric-body benchmark before more complex source counts
6. Keep the milestone gate for object-identification capability

## Constraints
- Simulation-first; no claims about real astronomical data until blind benchmarks pass gates.
- Jase's communication preference: layperson language in chat, technical detail in files.
