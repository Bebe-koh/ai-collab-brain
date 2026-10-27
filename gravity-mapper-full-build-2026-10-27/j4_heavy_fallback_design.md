# Blind-pipeline heavy-secondary fallback — design spec (v4)

**Date:** 2026-10-12
**Status:** DESIGN ONLY — implement on Jase's commission (audit-first discipline).
**Problem:** validation suite found V2-redo (Saturn + Earth-mass at 2.5 AU)
returned ONE_BODY. Root cause per `validation_verdict.md`: one-body train
MSE 1.7e-6 — the primary fit is garbage (doesn't find Saturn) and all 15
joint refinements seed from it. The "one-body first" init assumes a
perturbation-scale secondary; an Earth-mass at 2.5 AU is not one.

## Trigger (after existing step 1)

Compute `mse1 = score(train_rows, manifest, (c1,))` as today.
Noise floor: `SIGMA_AU = 2.0e-7` (empirical white-noise, `null_worker.py`),
so expected per-coordinate MSE ≈ σ² = 4e-14.

**Trigger when `mse1 > 1000 × SIGMA_AU²` (= 4e-11).** Rationale: the one-body
model is then rejected at >30σ per coordinate — seeding from its primary is
worse than useless.

Calibration against measured one-body train MSEs:

| case | one-body train | × noise (4e-14) | triggers? | outcome |
|---|---|---|---|---|
| J3 (real, Saturn+Mercury) | 2.07e-11 | ~520× | no → normal path | known good |
| V2-redo (Earth at 2.5 AU) | 1.7e-6 | ~4e7× | **yes → fallback** | currently missed |
| V1 null (Saturn only) | ~4e-14 (est.) | ~1× | no → normal path | known good |

Threshold sits ~2× above J3's real-data one-body MSE: real small-secondary
data stays on the cheap path; only grossly-broken primaries divert.

## Fallback algorithm (replaces steps 2–3 when triggered)

1. **Discard c1 entirely.** Do not run the sequential seed grid on a broken
   primary — garbage in, garbage out.
2. **20 uninformative joint starts**, all via existing
   `joint_refine_ext(train_rows, manifest, c1_init, c2_init)` (600 NM iters):
   - 10× full 6D random: m1 log10 ∈ [-5,-2], r1 ∈ [0.3,35];
     m2 log10 ∈ [-9,-3], r2 ∈ [0.2,40]; phases U[0,2π).
   - 5× heavy-secondary-biased: m2 log10 ∈ [-6,-3] (Earth is 3e-6 = -5.5).
   - 5× primary-biased: m1 log10 ∈ [-4,-3] (Saturn-scale anchor).
   All Candidates pass through the existing c2x/x2c (body1) and e2x/x2e
   (body2) transforms — no new transform code needed.
3. **Holdout selection unchanged** (step 4): best 2-body holdout vs the
   (broken) 1-body holdout. The gate is honest because the fallback must
   *beat* the one-body model on unseen data.

Why the null stays safe: J1 proved joint NM on planet-free data pushes the
secondary mass to the grid floor with holdout 100× worse than 1-body — so
even a mis-triggered fallback returns ONE_BODY. The critical control cannot
regress.

**Role-swap caveat:** in the fallback, "body 2" may end up the heavier one
(there is no privileged primary). The verdict is label-agnostic; when
reporting, sort bodies by mass. V2-redo success = TWO_BODY with some body
at m ≈ 3e-6 M☉, r ≈ 2.5 AU within ~10%.

## Validation plan (on commission)

Re-run the suite with the fallback wired in, ~15–20 min/run:
- V1 null → must stay ONE_BODY (fallback may or may not trigger; verdict
  must not change).
- V2-redo → must flip to TWO_BODY with the Earth recovered.
- V3 (Mercury-mass at 5 AU) → must stay TWO_BODY, marginal params (no
  regression on the distance edge).
- J3 (real data) → must stay TWO_BODY Mercury (no-trigger path; pure
  regression check).

## Cost

Fallback ≈ 20 joint refinements ≈ ~20 min, and only when triggered. The
normal path is untouched (same 15 refinements as J3).

## Files this would touch (on commission)

- New: `hidden_files/j4_heavy_fallback.py` (trigger + fallback + verdict).
- Reuse: `joint_refine_ext`, `one_body_fit`, `score`, `Candidate`, the
  c2x/x2c/e2x/x2e transforms — all existing.
- Re-run: extended `validate_pipeline.py` (V1, V2-redo, V3, J3).
