# Blind two-body test — result: NOT recovered

**Date:** 2026-10-06 · **Scenario:** `solar_catalog_seed_20260919_visible_3_hidden_2`
**Method:** sequential grid+NM (body 1, then body 2 with body 1 fixed) → joint 6D Nelder-Mead →
holdout gate (two-source must beat one-source by ≥20%) → truth unsealed for scoring.
Script: `blind_two_body_test.py`.

## Verdict: NOT recovered

Sealed truth: **Saturn** (2.858e-4 M☉, 9.58 AU) and **Mercury** (1.66e-7 M☉, 0.387 AU).
Visible tracers: Sun, Ceres, Mars, Earth.

| Stage | Result |
|---|---|
| A: body 1 | (2.860e-4, 9.583 AU) — Saturn recovered to 0.07% ✓ |
| B: body 2 (Saturn fixed) | (1e-6 M☉, 35 AU) — **spurious**, pinned at radius bound |
| C: joint 6D | pushed the spurious body to 40 AU (bound); Saturn held |
| D: holdout | two-source **worse** than one-source (−1307%) → correctly rejected |

## Why it failed

Not an optimizer-resolution problem — a **weak-signal trapping** problem. Mercury is ~1700×
less massive than Saturn; its coherent signal (~1e-6 AU) sits just above the effective noise
floor after 1,400 epochs. The sequential grid+NM for body 2 locked onto a spurious
low-frequency solution: a tiny mass at 35 AU is nearly static over the 4-yr baseline, so it
acts as a constant offset that absorbs low-frequency train-residual structure better than the
true high-frequency Mercury signal (0.24 yr period, ~16 orbits in baseline).

The holdout gate worked correctly — it rejected the spurious two-source model. The *search*,
not the *validation*, is what needs help.

## What would fix it

The second body needs a better initialization, not just a better local optimizer:
**residual periodogram**. After fitting the dominant body, run Lomb-Scargle on the train
residuals; Mercury's 0.24-yr period (or the ~0.32-yr synodic period) should appear as a peak.
Convert period → radius via Kepler III and seed the Stage B grid there. This is the standard
astronomical approach to weak-signal detection and directly addresses the trapping mechanism.

Alternative: multi-start joint 6D from random initializations (avoids sequential commitment).

## Status of the program

- One-body catalog recovery: **solved** (blind, 0.07% mass).
- Two-body catalog recovery: **open** — weak secondary detection is the new binding constraint.
- The original MacBook run's second body (3e-6 M☉, 0.75 AU, 46% holdout gain) was also wrong;
  no run has yet recovered Mercury.
