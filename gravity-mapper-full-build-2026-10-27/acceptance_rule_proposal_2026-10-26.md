# Prospective acceptance rule for evaluator substitution (spline → analytic circular extras)

Status: APPROVED for a bounded development-only test, 2026-10-26 (Jase's
own-words approval, following Perplexity's amended recommendation).
This file states the rule the test runs under. It is not a switch
decision, and it changes no threshold, default, or production state.

## Scope guards (hard)

- Development acceptance only. The final untouched partition is NOT used.
- ACCEPT_RATIO = 1.2, the Phase 2b validity gate, and all scientific
  thresholds are unchanged.
- Spline extras remain the default implementation. No production state
  changes.
- The original failed comparison (novel case, ratio rel diff 1.119e-05
  vs the predeclared 1e-6 bar) stays recorded as failed. This test
  answers a different, explicitly defined acceptance question.
- In-grid spline evaluation only. Anything outside the [0, 27] yr grid
  is out of scope; extrapolation stays unvalidated.

## Q1 — Do the evaluators calculate equivalent results?

At identical states, compare held-out residual vectors, holdout RMS,
MSE components, and the resulting ratio, in full precision (repr, not
rounded prints).

Pass/fail checks:
- Residual vectors: max component difference < 1e-7 AU. Justification:
  ~700x below the noise floor (7.04e-5 AU) and ~6x above the known
  spline interpolation error (1.57e-8 AU) — a band between known error
  and decision relevance.
- Fixed-state MSE ratio: relative difference < 1e-9, where relative
  difference = |a - b| / |spline reference|, and if the spline
  reference is exactly zero the absolute difference is used against
  the same tolerance. Justification: four orders below the observed
  refit sensitivity (1.1e-5), so passing Q1 cleanly separates
  evaluation equivalence from refit effects.

Diagnostic outputs (recorded full-precision, no separate gate):
holdout RMS and MSE components at fixed states. This is not a
weakening: the RMS difference is bounded by the residual-vector bound,
and the ratio subsumes the MSE components since it is computed from
them.

## Q2 — Does substitution preserve fitting behavior sufficiently?

Under matched settings (same dataset, seed, starts, reused baseline),
compare checker validity, scores, and decisions.

Hard requirements (no tolerance): checker verdict identical, gates
identical, final outcome and reason identical.

Score agreement:
- d = min(|r_spline - 1.0|, |r_spline - 1.2|), the distance from the
  pre-run spline baseline ratio to the nearest decision threshold.
- Require |r_analytic - r_spline| <= 0.1d. Justification: at least 10x
  margin against any threshold flip, stated generally — deliberately
  not a number tuned to clear the observed 1.12e-5.
- If the spline ratio sits exactly on a threshold, d = 0 and the
  permitted ratio difference is zero. Stated explicitly.
- Candidate RMS relative difference <= 1e-6 (same relative-difference
  definition and zero-reference rule as Q1).

Boundary rule: any threshold crossing between variants (checker
verdict, any gate, decision outcome, or ratio crossing 1.0 or 1.2) is
a FAIL that triggers investigation, regardless of how small the score
shift is.

## Same-path control (runs first)

Spline path twice under identical settings. Pass criterion: identical
verdicts, gates, and decisions, ratio relative difference < 1e-9, and
candidate RMS relative difference < 1e-6. If the control fails, halt
and investigate before any variant comparison.

Narrowed claim: exact control reproduction removes observed same-path
variability in this test; remaining variant differences will be
investigated as substitution-associated effects. It does not prove a
unique causal mechanism. Environment is fixed and recorded for the
control and both variants.

## Fresh case

Belt development dataset (TRACER + BIG3, preserved configuration from
rom_closure_lean.py), with known inventory = first two BIG3 bodies and
candidate = the third BIG3 body. Seed 0. Baseline computed once in the
spline run and reused for the analytic run (same structure as the
original comparison). The pre-run spline-path verdict, ratio, and
distance to thresholds are reported as part of the record, so boundary
proximity is documented rather than assumed.

## Pre-flight (before any fit runs)

Verify: belt configuration file present, planet-rails cache present,
rebound importable, save route writable. Stop and report any failure;
no new work is generated until pre-flight passes.

## Records (saved JSON per run)

Per run: nfev, cost, best_start, n_starts, success, wall runtime,
environment (Python, numpy, scipy, rebound versions, platform).
Termination status/message are NOT available from fit_state (it drops
the LM solver's status and message); this test does not change
fit_state to add them, and the JSON notes them as unavailable rather
than pretending otherwise. Adding them is a separate decision.

## What a pass would mean

A pass is evidence supporting evaluator substitution for this
specified development case and configuration only — not proof of
universal equivalence, extrapolation safety, or automatic permission
to change production. Any implementation switch is a separate
decision, reported on after the result, not bundled with it.
