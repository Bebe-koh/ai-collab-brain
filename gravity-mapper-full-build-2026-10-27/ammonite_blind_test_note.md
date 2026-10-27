# Ammonite (2023 KQ14) blind-recovery test — Gravity Mapper benchmark ladder

**Date:** 2026-10-14. **Status:** COMPLETE.
**Headline:** the briefed Stage-1 grid + Nelder-Mead pipeline **FAILS** this rung
(0/3 noise seeds; |da|/a = 1.1–7.6% vs the 1% criterion). A diagnostic
Cartesian-state + Levenberg-Marquardt fitter on the same data **PASSES**
decisively (3/3 seeds; |dq|/q ~ 1e-4%, |da|/a ~ 1e-3%, converging in ~10
function evaluations). The failure is an **optimizer inadequacy**, not an
information limit — the data contain the orbit to far better than 1%, and a
proper orbit-determination parameterization recovers it.
**Code:** `hidden_files/ammonite_test.py` (venv `~/.venv-p9`, rebound 5.2.2).
**Results:** `hidden_files/sealed_runs/ammonite_results.json`.

## 1. Pre-registered criterion (falsification discipline)

- **PASS:** |Δq|/q < 1% **and** |Δa|/a < 1% on the blind fit.
- **FAIL:** either ≥ 1%; optimizer non-convergence; unphysical result
  (e outside [0,1), a ≤ 0). Non-convergence = fail, not "needs tuning".
- Robustness: 3 independent noise seeds; all must pass.

## 2. Adopted elements (primary source)

JPL Small-Body Database API, queried 2026-10-14
(`https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=2023%20KQ14`):

| element | value | σ |
|---|---|---|
| a | 248 AU | 0.16 AU |
| e | 0.734 | 0.00016 |
| q | 65.9 AU | 0.0068 AU |
| i | 11° | 0.00054° |
| Ω | 72.1° | 0.00069° |
| ω | 199° | 0.015° |
| M | 357° | 0.0039° |

Epoch JD 2461200.5 (= 26.435 yr after J2000). Orbit solution: 102
observations, arc 2005-04-11 → 2026-07-20 (7770 d), rms 0.22″, condition
code 3, solution date 2026-10-13.

**Perihelion-discrepancy flag:** the candidate brief noted secondary sources
disagreeing (66 vs 71 AU). JPL SBDB gives **q = 65.9 ± 0.0068 AU** — the
66 AU value wins; the 71 AU figure in some secondary sources is outdated/
superseded. Adopted q = 65.9 AU.

## 3. Synthetic observations — assumptions (all documented)

- **Truth trajectory:** REBOUND ias15, Sun + massless particle, G = 4π²
  (AU³/yr²/M☉, matching the element conventions of
  `real_data/secular_elements.py`), sim.t initialized to the element epoch.
  Self-consistency guard in code: REBOUND truth vs analytic Keplerian
  propagation agree to < 1e-9 AU at all observation times (assertion).
- **Arc:** 2005.27–2026.55 (matches the real 102-observation arc).
- **Cadence:** 102 observations clustered within ±75 d of yearly opposition
  (outer object unobservable near conjunction) — a proxy for survey cadence,
  not a reproduction of the actual observation dates.
- **Noise:** isotropic Gaussian σ = 7.0e-5 AU per Cartesian component.
  Justification: JPL fit rms = 0.22″; at 66 AU, 0.22″ = 66×0.22/206265 AU
  ≈ 7.0e-5 AU. Calibrated to the real solution's rms.
- **Frame:** heliocentric ecliptic J2000 Cartesian — the mapper's real-data
  convention (cf. `tno_vectors.csv`), **not** geocentric RA/Dec.
- **Blind discipline:** truth sealed in
  `sealed_runs/ammonite_truth.json`; the fitter receives only (t, x, y, z).
  Scoring opens the truth file only after fitting.

## 4. Pipeline configuration

**Primary (as briefed — adapted sealed_scenarios pattern):** Stage-1 coarse
grid 8×8 over (log10 a ∈ [30, 1000 AU], e ∈ [0.05, 0.95]) with (i, Ω, ω, M0)
from a data-driven start (first-epoch position + finite-difference velocity
→ `cart_to_elements`); top-5 grid points → Nelder-Mead refine on all 6
parameters (log10 a, logit e, i, Ω, ω, M0), maxiter 600. 70/30 train/holdout
time split; model selected by holdout MSE.

**Diagnostic (standard orbit-determination parameterization):**
Levenberg-Marquardt (`least_squares`) in Cartesian state-vector space
(r0, v0 at epoch) → elements via `cart_to_elements`. Same blind inputs.
This mirrors the established `sparse_orbit_fitter.py` approach
(multi-start least squares) rather than inventing new machinery.

## 5. Results

Truth: q = 65.968 AU, a = 248.000 AU, e = 0.7340 (all seeds).

| seed | fitter | \|Δq\|/q | \|Δa\|/a | e_fit | converged | verdict |
|---|---|---|---|---|---|---|
| 7 | grid+NM | 0.076% | **1.10%** | 0.7312 | No (nit=600) | **FAIL** |
| 777 | grid+NM | 0.14% | **7.59%** | 0.7126 | No (nit=600) | **FAIL** |
| 20261014 | grid+NM | 0.26% | **4.76%** | 0.7214 | No (nit=600) | **FAIL** |
| 7 | cart+LM | 0.0000% | 0.0028% | 0.73401 | Yes (nfev=9) | PASS |
| 777 | cart+LM | 0.0001% | 0.0014% | 0.73400 | Yes (nfev=9) | PASS |
| 20261014 | cart+LM | 0.0001% | 0.0006% | 0.73400 | Yes (nfev=11) | PASS |

**Verdict:** the briefed pipeline FAILS (0/3). Perihelion q is recovered to
0.08–0.26% (passes alone), but a misses at 1.1–7.6% with a systematic
low bias (229–245 AU) along the q ≈ const degeneracy valley, and
Nelder-Mead never converges (all seeds hit maxiter 600, success=False).

## 6. Diagnosis: optimizer failure, not information failure

- The Cartesian+LM diagnostic recovers q to ~1e-4% and a to ~1e-3% on the
  **same data**, converging in ~10 evaluations / 0.3 s. The information is
  present; the Keplerian-element parameterization presents Nelder-Mead with
  a narrow curved (a, e) valley it cannot navigate.
- Independent check: from (r, v) error propagation, σ_a ≈ 0.003 AU is the
  information limit — the observed 10-AU scatter is ~1000× larger, i.e. pure
  optimizer shortfall.
- The real JPL solution achieves σ_a = 0.16 AU (0.06%) from the actual
  102 observations, consistent with recoverability.

**Recommendation for the ladder:** the orbit-recovery rung should use a
Cartesian (or equinoctial) + Levenberg-Marquardt fitter — the standard
orbit-determination parameterization, already the pattern in
`sparse_orbit_fitter.py` — not Nelder-Mead in Keplerian elements. The rung
itself is sound and achievable; the implementation was wrong, and the test
caught it before it mattered. That is the ladder working as designed.

## 7. Bugs found and fixed during this test (both caught by checks, not by luck)

1. **REBOUND epoch bug:** `sim.t` defaults to 0, but the initial state vector
   was osculating at the element epoch (+26.4 yr) — all observations were
   silently shifted 26.4 yr into the future. Caught because the train MSE at
   the *true* elements was 224 instead of ~5e-9. Fix: `sim.t = T_EPOCH_YR`.
2. **REBOUND G-unit bug:** REBOUND defaults to G = 1; the element machinery
   uses μ = 4π² AU³/yr². The simulation integrated a physically wrong orbit
   (self-consistent, so nothing crashed — the most dangerous kind of bug).
   Caught by the energy/element cross-check (a=640 vs 248). Fix: `sim.G = MU_SUN`
   on every simulation; a REBOUND-vs-analytic assertion now guards it.

## 8. Limitations

- Heliocentric Cartesian proxy with isotropic 3D noise: real astrometry is
  geocentric angles-only (radial distance unconstrained per observation).
  Our test is *easier* than reality in this respect.
- Two-body truth: planetary perturbations over the arc measure 2.3e-3 AU
  (≈ 32× the noise σ) in a Sun+8-planets check — **not** negligible. The
  clean same-model result stands, but a follow-up rung should use N-body
  truth (or a full N-body fitter) per the "everything we know" directive.
- White Gaussian noise: no survey systematics, no outliers, no
  phase-function or trailing effects.
- This tests **orbit recovery of a known body from its ephemeris**, not
  discovery of an unknown body from residuals — a different (easier) problem
  than the mapper's hidden-body inference.
- Elements are osculating at the JPL epoch; no claim about long-term
  dynamical behavior.

## 9. Explicit non-claims

- "Grid+NM fails this orbit fit" ≠ "the mapper's hidden-body inference is
  broken" — different problem, different machinery (the sealed-scenarios
  (m, r, phase) solver was never asked to fit 6 Keplerian elements).
- "Cartesian+LM recovers Ammonite" ≠ "Ammonite's published orbit is
  validated" — the truth was synthetic by construction.

## 10. Fixed rung (Cartesian+LM promoted to ladder standard, 2026-10-17)

**What changed:** the diagnostic Cartesian-state + Levenberg-Marquardt fitter
was promoted to a reusable module, `hidden_files/cartesian_lm_fitter.py`
(`fit_orbit`: multi-start LM on (r0, v0) at epoch, best-cost selection,
elements out via the validated `cart_to_elements`; follows the
`sparse_orbit_fitter.py` multi-start pattern). The Stage-1 grid + Nelder-Mead
in Keplerian elements is retired from the orbit-recovery rung. Module
self-test passes (|dq|/q=1.6e-6, |da|/a=3.7e-5 on a synthetic Ammonite-like
orbit). Blind discipline unchanged: the fitter receives only (t, x, y, z).

**Re-run, variant A (two-body truth, same setup as §3):** PASS, 3/3 seeds.

| seed | \|Δq\|/q | \|Δa\|/a | nfev |
|---|---|---|---|
| 7 | 0.0001% | 0.0030% | 12 |
| 777 | 0.0000% | 0.0023% | 14 |
| 20261014 | 0.0001% | 0.0010% | 13 |

Truth: q=65.968 AU, a=248.000 AU. The promoted fitter reproduces the
diagnostic's decisive pass through the clean module interface.

**New rung, variant B (N-body truth):** FAIL, 0/3 seeds — reported honestly,
not tuned.

| seed | \|Δq\|/q | \|Δa\|/a | nfev |
|---|---|---|---|
| 7 | 0.0303% | 3.1096% | 14 |
| 777 | 0.0310% | 3.1379% | 11 |
| 20261014 | 0.0310% | 3.1348% | 12 |

Truth dynamics: Sun + 8 planets live (REBOUND ias15), planets initialized
from JPL approximate Keplerian elements Table 1 at J2000 (verified
2026-10-17 at ssd.jpl.nasa.gov/planets/approx_pos.html; valid 1800–2050,
covers the arc), Earth row = EM Bary. Observation times and the noise
realization are bit-identical to variant A, so the variants differ ONLY by
planetary perturbations. N-body vs two-body deviation peaks at 0.054 AU
(~780× the noise σ) — much larger than §8's 2.3e-3 AU estimate, which
compared sim-frame positions (dominated by the Sun's wobble) rather than
heliocentric ones. The §10 deviation is dominated by short-period
indirect-term oscillations (Jupiter's pull on the Sun, double-integrated in
the heliocentric frame); verified physical, not a bug (massless-planet limit
reproduces the two-body trajectory to 1e-13 AU).

**Diagnosis of the variant-B failure:** model-mismatch bias, not optimizer
failure. The fitter converges cleanly (nfev ~12, best of 8 starts) and
reduces rms 6.7× vs the adopted elements (2.9e-3 vs 1.9e-2 AU) — but the
best-fit Keplerian sits at a=255.7 (+3.1%, systematic across seeds, not
scatter) while q is recovered to 0.03%. Absorbing the interior-mass monopole
(mu → mu(1+m_planets)) only reduces the bias to 2.3%: the bulk is the
indirect term and higher-order planetary structure that no Keplerian can
absorb. A pure-Keplerian fitter on a 21-yr arc with perturbations at ~780σ
cannot recover the published a to <1% — the information is there (variant A
proves it) but the model is wrong.

**Consequence for the ladder:** the orbit-recovery rung needs an N-body
fitter (planets in the dynamics, per the "everything we know" directive)
for long arcs — or the pass criterion must be restated against N-body mean
elements rather than a Keplerian fit. That is the next fix; it was not
attempted here (pre-registered scope: two variants, honest reporting).

**New limitations (variant B):** planet initial states from approximate
(mean-fit) JPL elements, not a precision ephemeris — adequate for a
perturbation background, not for reconstructing the real solar system;
two-body fitter on N-body truth is an explicit documented mismatch; the
66-vs-71 AU resolution (§2) is unaffected (truth elements identical across
variants).

**Code:** `hidden_files/cartesian_lm_fitter.py` (module),
`hidden_files/cartesian_lm_rerun.py` (both variants),
`hidden_files/sealed_runs/cartesian_lm_rerun_results.json` (results),
`hidden_files/sealed_runs/ammonite_obs_nbody.npz` (variant-B observations).
REBOUND guards from §7 kept on every simulation (G=4π², sim.t=epoch at
particle injection, analytic cross-check for variant A).

## 11. Modular N-body fitter (five brains, 2026-10-24)

**Problem (from §10):** the pure-Keplerian Cartesian+LM fitter fails
variant B (N-body truth) at |Δa|/a = 3.1% systematic bias — model
mismatch, not optimizer failure. This section builds the fix Jase
approved: five modules with clean contracts, nobody grading their own
homework, mirroring the tracker's architecture.

**Architecture** (`hidden_files/`, all new):
1. **Rails brain** (`rails_brain.py`): planets on real ephemerides —
   REBOUND ias15 Sun + 8 planets from JPL Table-1 elements at J2000
   (same table as §10), sampled every 0.5 d, cubic-splined. Read-only;
   the fitter never integrates planets in the fit loop. Spline vs
   direct REBOUND: 5.75e-9 AU.
2. **Particle brain** (`particle_brain.py`): integrates ONLY the fitted
   object. Two interchangeable propagators, same signature:
   Keplerian (analytic) and N-body (heliocentric ODE with direct +
   indirect terms against the rails, DOP853). N-body vs independent
   REBOUND Sun+8-planets truth: 2.2e-7 AU (300x below noise).
   A sign error in the indirect term was caught by this self-test
   during the build (error 0.11 AU before the fix, 2.2e-7 AU after) —
   caught by checks, not by luck, the same lesson as §7.
3. **Optimizer brain** (`optimizer_brain.py`): model-agnostic multi-start
   LM on Cartesian state; it cannot tell which propagator it is
   driving. Reuses `cartesian_lm_fitter.data_driven_start`.
4. **Checker brain** (`checker_brain.py`): independent gates —
   convergence, physical elements, holdout prediction (70/30 time
   split), noise consistency (train rms ≤ 5σ). Verdict PASS / FAIL /
   ABSTAIN. Never sees truth.
5. **Conductor brain** (`conductor_brain.py`): runs Keplerian first and
   escalates to N-body ONLY on evidence — pre-registered rule: train
   rms > 5σ, or checker FAIL/ABSTAIN. Warm-starts the N-body fit from
   the Keplerian best state (observations only, no truth leakage).

**Validation (pre-registered criterion unchanged: |Δq|/q < 1% AND
|Δa|/a < 1% on all 3 seeds; blind throughout; truth opened only for
scoring).** Harness: `nbody_fitter_rerun.py`; results:
`sealed_runs/nbody_fitter_rerun_results.json`.

**Variant A (two-body truth): PASS, 3/3 — no regression.** Keplerian
path, no escalation, checker PASS. |Δq|/q ≤ 0.0001%, |Δa|/a =
0.0010–0.0030%. Wall ~2–3 s per seed.

| seed | path | \|Δq\|/q | \|Δa\|/a | checker | wall |
|---|---|---|---|---|---|
| 7 | keplerian | 0.0001% | 0.0030% | PASS | 3.4 s |
| 777 | keplerian | 0.0000% | 0.0023% | PASS | 3.1 s |
| 20261014 | keplerian | 0.0001% | 0.0010% | PASS | 1.8 s |

**Variant B (N-body truth): PASS, 3/3 — the fix works.** Conductor
escalated on every seed (Keplerian checker ABSTAIN: "holdout coherent
but above noise floor: escalate" — the checker correctly refusing to
promote a biased fit). N-body checker PASS. Recovered values are
identical to variant A to 4 decimals (same noise realization; the
model now matches truth). The 3.1% bias is gone.

| seed | path | \|Δq\|/q | \|Δa\|/a | N-body checker | N-body fit time | wall |
|---|---|---|---|---|---|---|
| 7 | nbody | 0.0001% | 0.0030% | PASS | 61 s | 104 s |
| 777 | nbody | 0.0000% | 0.0023% | PASS | 70 s | 122 s |
| 20261014 | nbody | 0.0001% | 0.0010% | PASS | 70 s | 121 s |

**Timing (honest):** the N-body fit is ~40x slower than the Keplerian
fit (~60–70 s vs ~2.5 s per fit). Two causes, both understood: (1) each
N-body predict integrates 21 yr with DOP853 resolving Mercury/Venus
short periods in the rails (~1.6 s per call at rtol=1e-9); (2) LM's
finite-difference Jacobians multiply that by ~7 per iteration. The
first validation attempt (8 full starts, rtol=1e-11, no early stop)
took ~22 min per variant-B seed and was killed; the shipped version
uses 4 starts, rtol=1e-9 (re-validated to 2.2e-7 AU), and early stop at
the noise floor (rms < 2σ), cutting it to ~2 min per seed. Early stop
does not change results (LM converged = converged) and the pass/fail
criterion is untouched. Further speedup (variational Jacobians) is
possible but not needed for single-object fits.

**Limitations:**
- Rails here are a Table-1 integration, not Horizons ephemerides; the
  real-data fitter must swap in Horizons rails (the main pipeline's
  machinery already does this).
- Heliocentric Cartesian proxy with isotropic 3D noise persists from
  §3 (real astrometry is geocentric angles-only) — the geocentric
  variant is still open.
- The conductor's escalation rule (5σ) is tuned to this noise level;
  other arcs/noise levels need their own calibration.
- This tests orbit recovery of a known body, not discovery of an
  unknown body from residuals.

**Status:** the orbit-recovery rung is now FIXED for both two-body and
N-body truth. The ladder's next rung is the N-body fitter on real
Horizons rails and geocentric observations.
