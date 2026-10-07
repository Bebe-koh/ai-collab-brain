# Degeneracy Diagnosis: catalog_one_body_recovery
**Date:** 2026-10-06 · **Method:** grid mapping with phase fixed at truth (diagnostic, not blind)

## Method and scope

Reused `gravity_mapper/catalog/catalog_recovery.py` machinery verbatim
(`load_solver_inputs`, `split_rows`, `score_candidate`, `Candidate`).
Scenario `solar_catalog_seed_20260919_visible_3_hidden_2`, split 70/30 train/holdout.
Mapped a 25×30 grid (mass log-spaced 1e-4–1e-3 M☉, radius 5–35 AU) with **phase fixed
at the truth value 4.75 rad**, read from the sealed truth file. This is legitimate for a
diagnostic (it isolates the m–r plane) but means this is NOT a blind result — stated here
explicitly. Truth file was otherwise read-only. No source files modified.
Grid saved to `degeneracy_landscape.npz`; plot in `degeneracy_landscape.png`.

## What the landscape shows

1. **There is no flat m–r degeneracy valley.** At fixed truth phase, the holdout landscape has a
   sharp global minimum at truth (MSE 9.7e-10 at exactly 2.858e-4 M☉, 9.5826 AU, 4.75 rad).
   A 0.44 AU radius error costs 3 orders of magnitude; a 0.04 rad phase error costs 3 orders
   of magnitude. The data DO constrain (m, r, phase) tightly — when the optimizer can find it.

2. **The "valley" is a broad ridge of suboptimal fits**, not a degeneracy. Fitting
   log10(m) = k·log10(r) + c along the per-radius minima gives **k = 0.360 ± 0.024**
   (R² = 0.89) — 112σ away from the tidal k=3, 70σ from k=2. The ridge rises 1.1 dex in MSE
   from truth (r≈9.6) to r=33. It is the locus of least-bad fits, not a true degeneracy.

3. **The original winner lives in a different, 3D valley.** At (5e-4 M☉, 30 AU) the holdout MSE
   is ~1.3e-4 — flat in phase (4.5–5.0 rad changes it by <2×). This broad, shallow,
   phase-insensitive valley is what the coarse 3D grid search fell into. It is 5 orders of
   magnitude worse than truth, but the grid couldn't resolve the sharp truth valley
   (truth falls between mass grid points 2.5e-4/5e-4 and radius points 7.5/10.0, and between
   phase steps).

4. **Phase is the sharpest dimension.** This was not obvious from the run logs: at truth (m, r),
   phase 4.71 vs 4.75 (0.04 rad) degrades holdout MSE from 9.7e-10 to 1.5e-6.

## Interpretation

The `catalog_one_body_recovery` failure (213% radius error) is **computational, not physical**.
There is no fundamental mass–distance degeneracy in these data — the 40-year baseline pins the
orbital period, which pins the radius, and the perturbation amplitude then pins the mass. The
failure is grid-resolution vs. valley-sharpness: a brute-force coarse grid cannot resolve a
valley that narrow, so it settles into a broad wrong valley. The 355,680-candidate Mercury grid
failed for the same reason — resolution, not coverage.

## What breaks it

NOT a new observable or longer baseline — the current data already constrain the answer. What is
needed is a **smarter optimizer**:
- Grid + local refinement: evaluate the coarse grid, then run gradient-free local optimization
  (Nelder-Mead / L-BFGS) from the top-K grid points. The sharp valley is easy to descend once
  located approximately.
- Or adaptive mesh refinement on the grid itself.
- The `MINIMUM_HOLDOUT_IMPROVEMENT` gate (15%) is fine; the problem is purely in the search,
  not the acceptance criterion.

Secondary: the stage-gate `PASS_RULES` only cover toy benchmarks. The catalog benchmarks need
coded pass/fail policies so `recommend_next.py` stops returning `REVIEW_REQUIRED`.

## Caveats

- Phase was fixed at the truth value — this map cannot be quoted as a blind-benchmark result.
- Absolute MSE values computed here do NOT match the historical `runs/` JSONs (e.g. the selected
  candidate's train MSE is 4.8e-5 here vs 2.66e-8 in the log), suggesting code or data drift between
  the Mac run and this export. The landscape SHAPE (sharp truth valley, broad wrong valley, k≈0.36
  ridge) is the robust finding; absolute thresholds should be re-baselined.
- The k≈0.36 ridge scaling has no clean physical interpretation (it is not tidal, not
  period-matching); treat it as an empirical description of the least-bad ridge, not a law.
