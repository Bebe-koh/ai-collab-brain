# Gravity Mapper two-body v3 verdict: alternating joint refinement FAILED

Run: 2026-10-09 03:35–03:53 PDT (background). Files: `blind_two_body_v3_test.py`,
`blind_two_body_v3_run.log`, `blind_two_body_v3_result.json` (this directory).
Sealed-truth blind test on the same scenario as v1/v2
(`solar_catalog_seed_20260919_visible_3_hidden_2`): Saturn + Mercury hidden.

## What v3 tried (new vs v1/v2)
Block-coordinate descent / alternating joint refinement from the outset, instead of
fixing body 1 and fitting body 2 against its residual. Stages:
A. one-body grid + Nelder–Mead → body 1 (dominant).
B. full secondary grid (mass × radius × phase, low-mass extension) + NM from top-K
   starts → top-3 (body1, body2) pairs. Periodogram seeding dropped (proven failure
   mode in v2).
C. per pair: alternating NM blocks (body1 | body2, roles separated by radius)
   until converged or max rounds; then one joint 6D NM on the best pair.
D. holdout gate (20% train): two-source must beat one-source by ≥ 20%.
E. unseal truth for scoring.

## Result: RECOVERED = false
- Alternation converged after **1 round** and made train MSE *worse*
  (2.06e-11 → 9.52e-11); joint 6D recovered it to 3.08e-11. Block-coordinate
  descent provided no benefit — the secondary was already trapped from stage B.
- Inner (Saturn): mass 2.8601e-4 M☉, radius 9.592 AU, phase 4.7523 rad
  (scorer: mass err 0.997%, radius err 3.17%, phase err 1.27).
- Outer (supposed Mercury): (1e-6 M☉, 40 AU, 3.48 rad) — mass at grid lower
  bound, radius at grid upper bound: trapped at the bounds, same trap as v1.
  Mercury (1.66e-7 M☉, 0.387 AU) missed; scorer reports mass err 1722%.
- Holdout gate: one-source 6.40e-11 vs two-source 9.00e-10 → **−1307%**
  "improvement", correctly rejected (identical −1307% as v1 — same valley).

## Diagnosis (sharpened, not changed)
The binding constraint is **not** the optimization ordering. Saturn's absolute fit
error (~2e-7 M☉) exceeds Mercury's entire mass (1.66e-7 M☉): Mercury's signal
sits below the primary's residual structure, and no amount of alternation digs
it out — alternating let body 2 "absorb" residual, but the joint optimum still
prefers the bound-trapped spurious source over the true Mercury.

## What would actually change the constraint
1. Reduce the primary's absolute error: finer integrator tolerance, tighter
   one-body fit, or more/longer tracer arcs — lower the floor itself.
2. Change the detection statistic: a residual-structure test on holdout with
   calibrated nulls (the ALMA v2 lesson), rather than a full parametric
   secondary fit that can always hide in the residual's valleys.
3. More tracers / longer observational arc — more signal above the floor.

Note: this run was never reported in main chat and the 2026-10-10 study note
missed it (it claims the alternating-refinement build still awaits Jase's green
light). Verdict delivered via proactivity, 2026-10-10.
