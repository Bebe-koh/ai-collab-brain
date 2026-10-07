# Blind optimizer test — result

**Date:** 2026-10-06 · **Scenario:** `solar_catalog_seed_20260919_visible_3_hidden_2`
**Method:** coarse grid (2,304 candidates, same grid as the original) → top-12 by train MSE →
Nelder-Mead local refinement each → best by train MSE → holdout validation (15% gate) →
truth unsealed only for scoring. Script: `blind_optimizer_test.py`.

## Verdict: RECOVERED ✓

| | Selected | Truth | Error |
|---|---|---|---|
| mass (M☉) | 2.860e-4 | 2.858e-4 | **0.069%** |
| radius (AU) | 9.5830 | 9.5826 | **0.0037%** |
| phase (rad) | 4.7507 | 4.75 | **0.00074** |

Holdout improvement over the no-hidden-body baseline: **99.99999%**. Accepted: yes.
Recovery criteria (≤50% / ≤35% / ≤0.55 rad): passed by ~3 orders of magnitude.

## What the run shows

- Train MSE: coarse-grid best 2.97e-6 → refined 2.06e-11 (5 orders of magnitude).
- **9 of 12** refinement starting points converged to the identical minimum (2.064e-11).
  The sharp truth valley is easy to descend once located approximately; only 3 starts got
  trapped in a secondary minimum (6.36e-6).
- The winning refinement started from coarse rank #7, not #0 — the coarse grid's best
  point was not the closest to the valley, and it didn't matter.

## Interpretation

The original catalog failure (213% radius error) is confirmed as a pure optimizer-resolution
failure. The data constrain the answer tightly; brute-force grid search cannot resolve the
sharp valley; grid + local refinement recovers the hidden body to 0.07% in mass, blind.
No new observable, longer baseline, or prior was needed.

## Full numbers

See `blind_optimizer_test.py` output; raw result JSON is archived with the analyst.
Sealed-truth discipline held: truth file read only after fitting and holdout scoring.
