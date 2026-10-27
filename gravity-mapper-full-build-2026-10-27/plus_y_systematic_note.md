# The +y Systematic — Diagnosis Note
**Date:** 2026-10-13
**Status:** RESOLVED 2026-10-13 — cause identified via independent SPICE+DE440 check.
See `spice_indirect_check.md`. (This note below is the diagnosis trail; the resolution
supersedes the "cause unidentified" position.) This is a pipeline finding, not a detection.
**Working dir:** `~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/`

## The systematic, precisely

When 74 extreme TNOs (real JPL Horizons DE441 vectors, 15 yr, 183 epochs) are
integrated as test particles under Sun + 8 planets on interpolated true
ephemerides, every residual points the same way:

- **Form:** uniform (common-mode) acceleration, constant direction over 15 yr
- **Magnitude:** 1.14e-5 AU/yr² (median per-TNO quadratic fit)
- **Direction (ecliptic J2000):** (0.227, 0.972, 0.056), |m|=0.9998 alignment
  across 74 TNOs (positions themselves have |m|=0.125 — not a sky-selection effect)
- **Growth:** quadratic (last/mid-epoch norm ratio 4.02; linear would be 2.0)
- **Residual at t=15:** 1.24e-3 AU mean

A uniform acceleration is the signature of the *indirect term*
(−Σ μ_j r_j/|r_j|³, the Sun's acceleration reflected onto tracers) — the only
term in the heliocentric equations that is identical for all test particles.
For TNOs at 150+ AU, planetary perturbations are ~99.9% indirect term, making
TNOs pure indirect-term probes.

## Ruled out (with numbers)

| Hypothesis | Test | Result |
|---|---|---|
| Integrator error | Independent re-integration (scipy DOP853, rtol=1e-12, direct spline eval, no P_fine) | Agrees to 0.2%; same systematic. NOT the integrator. |
| Ephemeris interpolation | Spline vs fresh Horizons pulls at 15 mid-interval epochs | Max err 1.15e-4 AU (Jup), 8.3e-5 (Sat) → indirect-term error ~1e-7. 100× too small. |
| Linear-interp chord bias | Analytic estimate for all planets | Total ~2e-7, rotating at planet frequencies. NOT constant. |
| GM☉ error | Would be purely radial; measured systematic has \|m\|=0.9998 directional alignment | Ruled out (radial would give \|m\|~0.125). |
| Planet mass errors | Would rotate with each planet's orbital period | Systematic is constant over 15 yr. Also DE440=DE441 GMs verified. |
| Moon / EMB handling | Moon CSV verified heliocentric, correct; shared with inner hunt (which is clean); EMB good to 1.5e-9 | Ruled out. |
| Time-grid misalignment | All CSVs share t=0 to 14.9487, identical rounding | Ruled out. |
| Frame mixup | All pulls use identical Horizons params; fresh pull confirms ecliptic J2000 | Ruled out. |
| Barycentric vs heliocentric | Would give 0.04 AU linear + 0.005 AU periodic, not 5e-4 quadratic | Ruled out. |
| Missing physics (asteroids, Pluto, GR, J2, galactic tide) | All ≤1e-8 AU/yr² or wrong form | 1000× too small. |
| TNO data corruption | Fresh Horizons pull for 82158 matches CSV exactly (DE441) | Data is genuine. |
| Planet ephemeris corruption | Jupiter t=0 matches fresh pull exactly | Data is genuine. |
| Distant massive body (P9-like) | Would need 29 M☉ at 10,000 AU for uniformity; inner hunt clean rules out universal acceleration | Ruled out. |

## Leading hypothesis (incomplete)

The systematic behaves like the model's indirect term being **~1–2.4% too
strong** relative to Horizons' TNO dynamics:
- Scaling the indirect term by 0.99 reduces the 6-yr residual 2.0e-4 → 1.2e-4.
- Double integral of the model indirect term explains 76.7% of the mean-residual
  variance (best-fit excess fraction 2.43%, anti-aligned at −0.949).
- The systematic aligns (8°, 86% magnitude) with +0.146 × Saturn's time-averaged
  indirect term.

**But:** the direction match is not perfect, 23% of variance is unexplained,
and no mechanism has been found that would make the indirect term 1–2% too
strong with DE441-verified inputs. Every specific mechanism tested (mass errors,
distance errors, double-counting, interpolation bias) is ruled out by orders
of magnitude or by predicting rotation that isn't observed.

**The honest position:** the cause is unidentified. The systematic is real,
robust (two independent integrators), TNO-specific (inner hunt clean), and not
explained by any standard force-model difference tested.

## What would decide it

1. **JPL SPICE + DE441 direct check:** compute the indirect term from SPICE
   planet positions (bypassing our CSV/spline entirely) and compare with our
   spline-based value at 1e-9 level. Exonerates or implicates the ephemeris chain.
2. **Horizons documentation:** determine whether small-body vector generation
   uses a truncated force model vs major bodies. The 1–2% level suggests a
   subtle dynamical-model difference, not a bug.
3. **Simultaneous re-pull:** pull planet + TNO vectors in one session with
   explicit ephemeris version pinned, rebuild null. Rules out any temporal
   inconsistency (both pulls were DE441, but this closes the loop).
4. **High-cadence Sun acceleration:** pull the Sun's barycentric vector at
   2-day steps (resolving the 27-day lunar aliasing that contaminated the
   30-day measurement) and compare its acceleration directly with the model
   indirect term.

## Pragmatic path (with caveats)

**Option:** fit a constant uniform acceleration as a nuisance parameter in the
null model, then search residuals for *non-uniform* (geometry-dependent) Planet
Nine signals. A real P9 would produce differential perturbations that survive
uniform removal.

**Caveat:** only valid if the systematic is truly uniform and not itself a
distant-mass signal (ruled out above: would need 29 M☉). Do not apply blindly;
document the nuisance fit explicitly. The disciplined path is to identify the
cause first (tests 1–4 above).

## What this unblocks

Once resolved (or robustly modeled as nuisance), the 74 TNOs become a clean
Planet Nine constraint dataset: 15-yr baseline, 30-day cadence, ~1e-4 AU
sensitivity after null subtraction. The current 5e-4 AU systematic floor must
be removed first — it is 5× larger than the residual noise.

## Related

- Full hunt results: `full_data_hunt_note.md`
- **v2 re-run with Mercury fix (2026-10-13): `tno_hunt_v2_note.md` — systematic CONFIRMED GONE** (1.14e-5 → 1.2e-7 AU/yr², 95× reduction; growth 4.02 → 1.07 flat; noise floor 80,126 km → 3,282 km holdout). v2 hunt is a clean null: 480-candidate grid best 1.00× null, all dBIC negative, spurious 12 M⊕ candidate absent. 74 TNOs now a clean Planet Nine search dataset at 3,282 km noise floor. One sub-noise-floor stacked residual (~7.5e-6 AU peak) flagged for follow-up, not a detection.
- Labeled attributions (pattern → label → reason): `../attribution_labels.json`
- Parent ROM (654 bytes, 19 hypotheses, 3 consolidations): `real_data/parent_rom.json`
