# Coarse-to-fine integration: secular scan + N-body pipeline + v9 classifier

**Date:** 2026-10-12
**Status:** DESIGN — specifies how the three components combine.

## The three stages

```
Real TNO/asteroid data
      ↓ Stage 1 (secular): fast quadrupole scan over (mass, a, inc)
Candidate regions (minutes)
      ↓ Stage 2 (N-body): J4 joint refinement on candidate regions
Precise masses + orbits (tens of minutes)
      ↓ Stage 3 (v9): planet vs black hole via optical/gamma
Classification (seconds)
```

## Why this division

| Stage | Physics | Speed | Precision | Role |
|---|---|---|---|---|
| Secular scan | Quadrupole-averaged | Minutes (118 objects) | Coarse (finds regions) | Triage |
| N-body (J4) | Direct integration | 15-25 min | 0.1% mass (Mercury) | Weighing |
| v9 classifier | Flux thresholds | Seconds | Correct-or-abstains | Classify |

The secular approximation is 100-1000× faster than N-body because it
averages over orbits instead of integrating them. It's too coarse for
precise masses (misses eccentricity, resonances, higher multipoles) but
ideal for finding *where to look*. J4 then does the expensive precise
fit only in promising regions.

## Interface between stages

**Stage 1 → Stage 2:** The secular scan outputs a ranked list of
(mass, semi-major axis, inclination) cells by Δχ². The top-K cells are
converted to J4 informed starts:
- mass → log-uniform within the cell
- semi-major axis → uniform within the cell
- inclination → currently unused (J4 assumes coplanar; v4 upgrade)
- phase → uniform random (secular theory is phase-averaged)

This REPLACES the current "uninformative random starts" in J4 with
physically-motivated starts, reducing the search space by orders of
magnitude.

**Stage 2 → Stage 3:** J4 outputs (mass, distance) of the recovered
secondary. v9 takes these and computes optical (planet) vs gamma (PBH)
flux predictions against survey thresholds. No changes needed — the
interface already exists.

## What was integrated today (2026-10-12)

From the secular pipeline's operational code, two components were
adapted into the N-body pipeline's codebase:

1. **`tracer_attribution.py`** (from `candidate_ranking.py` concept):
   Per-tracer MSE breakdown after fitting. Flags outliers via
   median + MAD threshold. Answers "which tracer is driving the
   residual?" — critical for diagnosing bad fits vs bad data.

2. **`input_validation.py`** (from `ingest_real_residuals.py` concept):
   Schema checks, finite-value checks, bounds checks, minimum time
   coverage per tracer. The pipeline now refuses bad data loudly
   instead of producing confident wrong answers.

## What was NOT integrated (and why)

- **`pbh_gamma_classifier_v10.py`**: Misnamed — it's a Δχ² threshold,
  not a PBH/gamma classifier. v9 is strictly better (actual physics).
- **The secular kernel itself** (`lagrange_kernel.py`): Correct physics
  but parameterized for distant perturbers acting on TNOs. Our validated
  scenario is inner-system (Mercury). Direct port doesn't apply; the
  *concept* (fast pre-filter) is what's adopted above.
- **The v3 grid results**: Null result (Δχ² = -396), no candidates to
  follow up. Nothing to hand off yet.

## Prerequisites for real-data operation

1. **Uncertainty calibration.** The secular run shows reduced χ² ≈ 7-9
   (should be ≈ 1). Error bars are underestimated ~3×. Both pipelines
   need calibrated uncertainties before real-data results mean anything.
2. **Eccentricity.** J4 assumes circular hidden bodies; TNOs have e up
   to 0.85. Required for the Stage 1 → Stage 2 handoff to work on real
   TNOs.
3. **N-body verification adapter** (already on their v4 list): convert
   J4 outputs to REBOUND/WHFast initial conditions for independent
   verification.

## Files

- `hidden_files/tracer_attribution.py` — per-tracer diagnostics (NEW)
- `hidden_files/input_validation.py` — input validation (NEW)
- `hidden_files/j4_blind_pipeline_v2.py` — N-body stage (existing)
- `hidden_files/pbh_gamma_classifier_v9.py` — classifier stage (existing)
