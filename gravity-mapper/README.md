# Gravity Mapper — degeneracy diagnosis + blind optimizer test

**Date:** 2026-10-06 · **Analyst:** Atlas · **Source code:** Jase's MacBook Air (`/Users/xaliux/gravity-mapper`), code-only export (not included here — this repo holds the analysis, not the private source).

## The question

The catalog one-body recovery benchmark selected a hidden body at (5e-4 M☉, 30 AU) against a
sealed truth of (2.86e-4 M☉, 9.58 AU): 96% holdout improvement, but 213% radius error.
Was this a physical mass–distance degeneracy, or an optimizer failure?

## The answer

**Optimizer failure — there is no degeneracy.** See `degeneracy_note.md` and `degeneracy_landscape.png`.

Mapping the holdout-MSE landscape over mass × radius (phase fixed at truth for the diagnostic)
reveals an extremely sharp global minimum sitting exactly on the truth (MSE 9.7e-10; a 0.44 AU
radius error costs 3 orders of magnitude). The original 2,304-candidate brute-force grid stepped
clean over it — the truth falls *between* grid points in mass, radius, and phase, all three.
The grid's "winner" sits in a broad, shallow, phase-insensitive valley ~1e5× worse.

The fitted ridge scaling (k = 0.36 ± 0.02) is 112σ from the tidal k=3 — definitively not a
tidal degeneracy.

## The fix (tested blind)

`blind_optimizer_test.py`: coarse grid → top-12 candidates → Nelder-Mead local refinement on
train MSE → holdout validation (same 15% gate) → truth unsealed only for scoring.
See `blind_result.md` for the outcome.

## Reproduce

```bash
# needs: numpy, scipy, and the gravity-mapper source tree
cd /path/to/gravity-mapper          # Jase's source export
python3 /path/to/blind_optimizer_test.py   # script inserts source_upload/ on sys.path
```

## Caveats

- The landscape diagnostic fixed phase at the truth value — it is a diagnostic, not a blind result.
  The blind result is `blind_optimizer_test.py`, which never touches truth until scoring.
- Absolute MSE values drift slightly vs the 2026-09-19 run logs; the landscape shape is the robust finding.
