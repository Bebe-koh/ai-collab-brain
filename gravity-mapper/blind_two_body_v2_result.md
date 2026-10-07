# Blind two-body test v2 (periodogram-seeded) — result: NOT recovered

**Date:** 2026-10-06 · **Scenario:** `solar_catalog_seed_20260919_visible_3_hidden_2`
**Method:** one-body grid+NM → Lomb-Scargle on train residuals → radius seed from peak
period → focused secondary grid+NM → joint 6D → holdout gate (20%) → truth unsealed.
Script: `blind_two_body_v2_test.py`. (Run crashed on JSON serialization *after* scoring;
verdict below is from the complete run log.)

## Verdict: NOT recovered

## What happened

| Stage | Result |
|---|---|
| A: body 1 | Saturn (2.860e-4, 9.583 AU) to 0.07% ✓ |
| A2: periodogram | **Peak at 1.881 yr, SNR 37.6** → radius seed 1.524 AU |
| B: secondary | (1e-6 M☉, 1.91 AU) — spurious |
| C: joint 6D | train MSE 2.05e-11; mercury still 94% mass / 385% radius off |
| D: holdout | −2.15% → correctly rejected |

## Why the periodogram failed

**The 1.881-yr peak is Mars's orbital period, not Mercury's.** After fitting Saturn to 0.07%,
the residual Saturn misfit (absolute mass error ≈ 2e-7 M☉) imprints each tracer's *own*
orbital period onto the residuals — and Mars's 1.88-yr period dominates because the misfit
projects most strongly there.

The deeper problem is arithmetic: **Saturn's fit error (2e-7 M☉) exceeds Mercury's entire
mass (1.66e-7 M☉).** Sequential detection has a noise floor set by the primary's fit error —
no secondary smaller than that can be seen, regardless of seeding. The periodogram cannot
dig out a signal buried under the primary's own misfit.

## What this means

The binding constraint has sharpened again:
- v1 showed: brute-force grid can't resolve sharp valleys → fixed by grid+NM (one-body solved).
- v2 shows: **sequential fitting can't detect secondaries below the primary's fit error**,
  and residual periodograms see tracer self-residuals, not the hidden body.

The way forward is not better seeding but **alternating joint refinement from the start**:
fit body 1, propose body 2, then *re-fit body 1 jointly* (it will shift slightly to
accommodate body 2), iterate — the toy layer's `refine_two_bodies` already does this
successfully. The catalog layer needs the same alternating structure, plus a secondary
proposal that doesn't rely on residuals dominated by primary misfit.

## Script bug (fixed after run)

`accepted`/`recovered` were numpy `bool_` and crashed `json.dumps` after scoring.
Fixed by casting to Python `bool`. The science result is unaffected (verdict from log).
Also: Stage B's initial grid point (1e-7 M☉) fell outside `ONE_BODY_BOUNDS` (floor 1e-6),
triggering an `OptimizeWarning`; bounds now extend to 1e-8 for secondary searches.
