# Eccentric fitter validation — diagnosis (2026-10-27)

## Result (predeclared bar: 20/20 within mass ≤10%, a ≤5%, e ≤0.05)

**9/20 recovered.** Means: mass 44.29%, a 21.02%, e 0.0759.
Full record: `eccentric_fitter_results.json` (per-case JSONs
`eccentric_case_XX.json`). Runtime 77 min total (~230 s/case).

## Per-case table (truth -> fitted; R = recovered)

| case | truth m / a / e | fitted m / a / e | R | holdout ratio |
|------|-----------------|------------------|---|---------------|
| 00 | 2.81e-06 / 3.66 / 0.168 | 1.32e-07 / 0.35 / 0.187 | no | 29.3 |
| 01 | 4.25e-06 / 4.66 / 0.318 | 4.25e-06 / 4.66 / 0.318 | YES | 50673 |
| 02 | 1.95e-06 / 4.06 / 0.247 | 1.95e-06 / 4.06 / 0.248 | YES | 2532 |
| 03 | 1.69e-06 / 4.77 / 0.230 | 1.69e-06 / 4.77 / 0.230 | YES | 5507 |
| 04 | 4.05e-06 / 4.98 / 0.187 | 4.05e-06 / 4.98 / 0.186 | YES | 50245 |
| 05 | 1.79e-06 / 4.92 / 0.158 | 1.79e-06 / 4.92 / 0.158 | YES | 5365 |
| 06 | 1.60e-06 / 3.60 / 0.266 | 2.04e-07 / 2.43 / 0.176 | no | 3.0 |
| 07 | 2.84e-06 / 4.90 / 0.371 | 2.84e-06 / 4.90 / 0.372 | YES | 19404 |
| 08 | 4.00e-06 / 4.90 / 0.136 | 4.00e-06 / 4.90 / 0.135 | YES | 38113 |
| 09 | 3.99e-06 / 3.55 / 0.304 | 5.47e-08 / 1.18 / 0.711 | no | 3.3 |
| 10 | 1.86e-06 / 3.51 / 0.192 | 4.25e-07 / 2.62 / 0.225 | no | 2.9 |
| 11 | 4.04e-06 / 4.14 / 0.060 | 1.47e-07 / 2.55 / 0.276 | no | 2.9 |
| 12 | 2.06e-06 / 3.53 / 0.003 | 2.61e-07 / 2.63 / 0.167 | no | 7.1 |
| 13 | 1.71e-06 / 3.76 / 0.226 | 3.13e-08 / 1.43 / 0.065 | no | 0.003 |
| 14 | 3.28e-06 / 3.05 / 0.151 | 1.74e-06 / 2.70 / 0.219 | no | 13.9 |
| 15 | 1.72e-06 / 3.51 / 0.381 | 1.56e-07 / 2.45 / 0.448 | no | 15.6 |
| 16 | 3.88e-06 / 3.84 / 0.214 | 3.88e-07 / 2.50 / 0.113 | no | 8.6 |
| 17 | 2.53e-06 / 4.64 / 0.191 | 2.09e-06 / 4.49 / 0.000 | no | 8.2 |
| 18 | 2.87e-06 / 4.38 / 0.088 | 2.88e-06 / 4.38 / 0.088 | YES | 21900 |
| 19 | 2.85e-06 / 4.59 / 0.203 | 2.85e-06 / 4.59 / 0.203 | YES | 21082 |

## Pattern 1 — bimodal: exact or wrong-basin, nothing in between

Recovered cases are essentially exact (mass 0.01–0.09%, a ≤0.01%,
e ≤0.0006). Failed cases are wildly wrong (mass 17–99%, a 3–90%).
This is a SEARCH failure (basin identification), not a precision
failure. The fitter's optimizer works fine once it is in the right
basin.

## Pattern 2 — the split is by semi-major axis, not eccentricity

Recovered: ALL truth a >= 4.06 AU. Failed: 10 of 11 truth a <= 3.84 AU.
Truth eccentricity spans the full range on both sides (failures
include e = 0.003, nearly circular; recoveries include e = 0.371).
Eccentricity is NOT the discriminator. The one exception, case 17
(a = 4.64), got close on mass (17%) and a (3.3%) but circularized the
orbit (fitted e = 0 vs truth 0.191) — the e-dimension can trap even
near the right basin.

## Pattern 3 — the failure alias cluster

Seven failures fit a ≈ 2.4–2.7 AU with mass ≈ truth/10 (cases 06, 10,
11, 12, 14, 15, 16). Their holdout ratios are 2.9–15.6, versus
2500–50000 for recovered cases, and their two-body holdouts sit at
1e-11–1e-9 versus the ~1e-14 noise floor. The data DO discriminate
the right basin by ~1000x on holdout — the search just never reaches
it. This rules out a genuine degeneracy: it is a missed basin, not
an equally-good alternative. Case 13 is the worst failure (holdout
ratio 0.003 — the two-body fit is worse than one-body on holdout).

## Root-cause hypothesis (measured, not guessed)

The circular screen's radius grid is [0.35, 0.5, 1.0, 1.5, 2.5, 5.0,
9.6, 20.0] — there is NO grid point between 2.5 and 5.0 AU. Truths
near 5.0 recover (NM walks a short distance); truths mid-gap (3.0–
3.9) leave the screen's best cell at 2.5 or 5.0, and the e-scan only
tries eccentricities AT those cells' (m, a, phase). NM in 7D from
there converges to the 2.5 AU local minimum instead of walking to
the true basin. The alias cluster sits exactly at the 2.5 grid point.

## Proposed fix (NOT started — needs Jase's word)

1. Denser radius grid in the 2–6 AU band (e.g. add 3.0, 3.5, 4.0,
   4.5, or a log-spaced grid there) so no truth sits mid-gap.
2. E-scan over more screen cells (top-6, or all cells above a
   threshold) instead of top-3.
3. More joint refined seeds (the 4-seed budget is thin for 7D).
Then re-run ALL 20 cases under the improved search (a single-version
claim needs all cases under one search version; ~80 min).
The 9 recovered cases are expected to re-recover (denser grid only
helps near-grid truths); the test is whether the 11 failures flip.

## Addendum — search v2 smoke FAILED identically (2026-10-27)

Search v2 (denser grid + top-6 e-scan + 3+3 seeds) was smoke-tested
on case 16 before any full re-run. Result: recovered=False, mass
90.00%, a 34.96%, e 0.1008, holdout ratio 8.611 — the SAME fitted body
as v1 to 4+ significant figures (3.881e-07 / 2.4998 / 0.113 / 1.467).
Grid resolution alone does NOT fix case 16.

Screen diagnostic (case 16 train data, truth Saturn): the circular
screen's top-15 cells span a = 0.35–3.0 with MSEs 1.5e-10 to 2.9e-10,
and the best cell per radius spans only 1.5e-10 to 3.3e-10 across ALL
radii — the screen is nearly flat, and its best cells carry wrong
phases (1.05/2.09 vs truth M0 5.34) and wrong masses (1e-7 vs truth
3.88e-6). E-scanning at wrong (m, a, phase) cannot reach the truth
basin, and the extra seeds evidently fall to the same 2.5 AU local
minimum. The top-K-clustering hypothesis is also refuted (top cells
do NOT cluster at 2.5 AU) — the problem is the circular proposal
itself, not its resolution or its selection.

Search v3 fix (implemented, re-smoke pending): eccentric_screen
searches (mass, radius, phase, e) jointly (2016 cells: 7 masses x
12 radii x 6 phases x 4 e-values) and the top-3 screen seeds go to
joint refinement. The circular screen + e-scan path is abandoned for
the secondary stage. If the v3 re-smoke on case 16 recovers, the full
20-case v2 run launches under search v3.

## Addendum 2 — search v3 ALSO failed identically; mass grid is the binding constraint (2026-10-27)

Search v3's re-smoke on case 16: recovered=False, mass 90.00%, a
34.96%, e 0.1008, ratio 8.611 — the SAME fitted body a third time.
Proposal breadth (4D joint screen) also does not fix it.

Three decisive tests on case 16 train data:
- Test A: train MSE at truth = 9.791e-15 (noise floor); at alias =
  8.401e-11. Truth beats alias ~8000x. Truth IS the global minimum;
  model and data generation are consistent.
- Test B: joint NM from truth (standard steps) STAYS at truth
  (9.709e-15, all parameters within tolerance). The truth basin
  exists and NM converges to it from truth. Step size is not the
  problem.
- Test C: same with small steps — also stays (9.708e-15).

Screen-ranking check (4D screen, truth Saturn): the truth
neighborhood (a 3.5/4.0, e 0.2, ph 5.24) ranked 25th/34th
(2.11e-10 / 2.28e-10) against a best cell of 1.42e-10. Why: the 1-dex
mass grid puts the nearest cell 3.88x off in mass (1e-6 vs truth
3.88e-6), leaving most of the signal unfitted — at that mass error
the expected MSE is ~(0.74)^2 x signal^2 ≈ 1.8e-10, matching
observation. MSE at grid resolution does NOT decrease monotonically
toward truth; the landscape is rugged with many comparable minima.

Fine-mass screen test (0.25-dex masses, 1e-7..1e-5 band): truth
neighborhood took ranks 0/1/3 — best cell (5.62e-6, 4.0, 0.2, 5.24)
at 7.55e-11, then (3.16e-6, 3.5, 0.2, 5.24) at 8.26e-11, then
(3.16e-6, 4.0, 0.2, 5.24) at 9.60e-11, against the old screen best
1.42e-10. The mechanism is proven: mass resolution makes the truth
basin visible to the screen.

Search v4 fix (implemented, re-smoke pending): MASS_GRID_FINE
(0.25-dex steps, full 1e-9..1e-3 range, 25 masses) in
eccentric_screen — 7200 cells (~4 min/case screen). Per-case total
~10 min; full 20-case run ~3.5 hr, background, checkpointed.
