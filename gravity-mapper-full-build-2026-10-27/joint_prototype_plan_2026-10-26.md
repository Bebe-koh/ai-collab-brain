# Joint-Interface Prototype Plan — 2026-10-26 (D9 batch)

**Status:** PLAN, written BEFORE the k=0 regression proof and before
any demo run. D10 and D11 below are set prospectively and must NOT be
changed after seeing results. If the k=0 proof fails against D11, the
batch STOPS: no demo, no demo cost table.

**Authorization:** Jase approved BOTH gated items on 2026-10-26
("Both", naming bucket implementation and joint prototype explicitly).
This batch is the joint-prototype half only.

**Scope — new files only, under hidden_files/:**

- `joint_model_spec.py` — spec object (candidates, bounds, rails,
  t_ref, tolerances, partition, spec identity).
- `joint_driver.py` — generalized driver: JointParticle propagator
  (ODE, per-trial perturber rebuild) + `fit_model` (multi-start LM
  mirroring `fit_state` discipline verbatim).
- `joint_checker.py` — spec-driven checker entry point `check_model`
  (train-refit RMS gates, NEVER full-data RMS; MSE ratio in Phase 2
  definition; verbatim reporting including start rule).
- `joint_prototype_tests.py` — k=0 proof + k=1 demo + removal test +
  cost measurement; writes `joint_prototype_results_2026-10-26.json`.
- This plan file.

**Forbidden, and how this batch avoids them:**

- NEVER edit `hypothesis_tracker.py`, `rom_closure.py`,
  `rom_history.py` (parallel bucket batch's files), or ANY existing
  file. No edits to existing brains, checker, or optimizer.
- The prototype does NOT import `rom_closure` at all (the bucket
  batch is editing it). It imports only `optimizer_brain.fit_state`
  (reference for the k=0 proof), `particle_brain.NBodyParticle`,
  `rails_brain.PlanetRails`, `secular_elements`, and
  `cartesian_lm_fitter.data_driven_start` — none of which are in
  the bucket batch's edit list.
- No live imports of the prototype by live code; no live ROM
  ingestion; no live ROM contact at all (no read, no write — the
  live ROM md5 is not even asserted here, because the batch never
  touches that path; non-contact is by construction, see the
  results file's import list).
- No open-question Stage B use; no freeing radii/phases (Stage B
  frees MASSES ONLY); no full rung ladder; no survey/battery work;
  no threshold, cap, or evaluator-default change; no Drive upload.
- No full existing regression suites in this batch (parent
  re-verifies after both batches land) — only the prototype's own
  tests plus the k=0 proof.
- No claim that joint fitting "works": the demo is a measurement
  on synthetic data, not validation. Prototype acceptance and any
  promotion are separate decisions.

## Conventions (fixed here, before runs)

- θ = [tracer state (6): rx, ry, rz, vx, vy, vz at t_ref] +
  [log10 masses (k), masses in solar masses].
- Perturber geometry FIXED: circular coplanar Keplerian orbits,
  radius and phase at inventor values, angle(t) =
  phase + sqrt(MU_SUN / radius^3) * (t - t_ref), positions analytic
  (no spline rails for perturbers — geometry is a formula, so a
  per-trial rebuild costs only the mass factor).
- Perturber acceleration (direct + indirect, same form as
  `NBodyParticle._rhs`):
  `a += Σ_j μ_j · (d_j/|d_j|³ − r_j/|r_j|³)`,
  with **μ_j = 10^(logmass_j) · MU_SUN**.
- **Convention flag (recorded, not hidden):** this μ convention
  follows the spec text ("masses in solar masses, consistent with
  MU_SUN / PLANET_MU"). The existing `rom_closure.PerturbedParticle`
  passes inventor masses directly as `extra_mus` (i.e. without the
  MU_SUN factor) in both its truth generation and its fits, so its
  nominal masses are internally consistent but are NOT the same
  physical μ as this prototype's. Reconciling the two conventions
  is a promotion-time item, NOT resolved by this prototype, and
  the demo below is self-consistent under the prototype convention
  only. No result from this batch may be quoted as a rom_closure
  candidate-fit result.
- Integrator: DOP853, rtol=1e-9, atol=1e-11 (NBodyParticle defaults),
  split at t_ref exactly as `NBodyParticle.predict` does.
  Unphysical tracer state (a ≤ 0, e ≥ 1, non-finite) or out-of-bounds
  log-mass → predict returns None → LM penalty path (same as
  `fit_state`'s `_BIG` handling).
- `fit_model` discipline, mirrored from `fit_state` verbatim:
  least_squares method='lm', ftol=xtol=gtol=1e-15, max_nfev=500 per
  start; best-cost selection among COMPLETED (successful) starts
  ONLY; early stop at the noise floor only after a successful start;
  deterministic given seed. Tracer starts: start 0 = data-driven
  start (or tracer x0_hint ONLY when the hint comes from training
  data); subsequent starts perturb tracer state by 3% position /
  10% velocity with the same rng sequence as `fit_state` (seed).
- Checker gates, mirrored from `check_fit` (Phase 2 definition):
  converged (driver success); physical (a > 0, 0 ≤ e < 1, all fitted
  masses finite and positive); noise_consistent (TRAIN-REFIT RMS ≤
  5σ); holdout_ok (holdout RMS ≤ max(5σ, 3 × train-refit RMS)).
  Verdict: FAIL if not converged/physical; ABSTAIN if holdout
  unavailable, or holdout_ok but not noise_consistent; PASS if
  holdout_ok and noise_consistent; else FAIL. Full-data RMS may be
  reported for display but NEVER gates.
- MSE ratio (Phase 2 definition): null holdout MSE / joint holdout
  MSE, where each holdout RMS comes from that model's own
  TRAINING-SPLIT refit evaluated on the SAME holdout partition.
  ACCEPT_RATIO = 1.2 is reported against, not decided here.
- Removal test (§4 of the spec): reduced model REFIT on training
  data only, same partition. Frozen-parameter removal is
  PROHIBITED. Unconverged reduced refit → abstain on that body's
  contribution claim. For k = 1, removal = the null model, so the
  removal refit IS the null train refit used for the MSE ratio
  (stated here so it is not double-counted as a second run).
- Fitted-mass uncertainties: NOT available from the LM driver
  (no covariance is computed); the checker reports masses without
  uncertainties and says so verbatim, rather than inventing them.

## D11 — k=0 regression tolerance (SET BEFORE THE PROOF RUNS)

**PASS iff, on the same data, seed, n_starts, and early-stop:**

1. Success flags agree (both True), AND
2. Relative RMS difference
   |rms_joint − rms_fit_state| / rms_fit_state ≤ 1.0e-4, AND
3. Relative semi-major-axis difference ≤ 1.0e-4 AND absolute
   eccentricity difference ≤ 1.0e-4.

**Justification:** prior fit-comparison work showed ~1e-5-level
differences in MSE ratio from optimizer stopping paths alone when
the model/evaluator changed. 1e-4 is one order above that observed
optimizer noise, so it does not demand bit-identity from two
different propagator paths (ODE joint driver vs the reference
propagator), while still being ~1000× below the noise floor in
absolute RMS terms (1e-4 × 7e-5 AU ≈ 7e-9 AU) and far below any
scientific criterion (1% scale). Fitted state-vector differences
are reported verbatim but are NOT gated: LM can trade r/v along
the orbit while holding RMS/a/e.

**k=0 proof configuration (fixed here):** reference =
`fit_state` with `NBodyParticle` (planet rails from the cached
`sealed_runs/planet_rails.npz`); joint = `fit_model` with k = 0,
same rails, same DOP853 tolerances. Data: tracer elements
a=40.0, e=0.1, i=0.087, Omega=1.2, omega=3.5, M=5.0 at t_ref,
propagated with the reference NBodyParticle, 60 obs on
ts = linspace(5.0, 20.0, 60), sigma = 7.04e-5 AU, noise seed
12345. n_starts = 3, seed = 0, max_nfev = 500,
early_stop_rms = 2 × sigma. (Proof data contain NO perturber:
k = 0 must reproduce the no-perturber fit.)

## D10 — log-mass scan design + bounds (SET BEFORE DEMO RUNS)

- **Scan (inventor-value ± decades, NOT a fixed grid):** mass
  starts cycle through inventor log-mass + offsets
  [0, −1, +1, −2, +2] decades, in that order, for starts
  0, 1, 2, 3, 4, … (start 0 = inventor value exactly; further
  starts repeat the cycle if n_starts exceeds 5). Each start's
  tracer perturbation follows the `fit_state` rng sequence, so
  the mass scan is the only new start dimension.
- **Bounds (hard):** inventor log-mass ± 3 decades. Trials
  outside bounds → predict returns None → penalty path.
- **Rationale:** a ±2-decade scan brackets a 1-decade inventor
  error with margin on both sides without exploding the start
  count; ±3-decade bounds keep LM from wandering to degenerate
  masses while still allowing recovery if the inventor is off
  by 2 decades. A fixed absolute grid would bake in a mass
  scale the inventor hypotheses do not share, so it is rejected
  here.

## k=1 demo — pre-declared truth and configuration (fixed here)

- **Sealed truth (prototype convention, μ = mass · MU_SUN):**
  tracer elements as in the k=0 proof; truth perturber
  mass = 1.0e-4 Msun, radius = 8.0 AU, phase = 1.0 rad.
- **Inventor candidate (geometry at truth, mass off by 1 decade):**
  mass = 1.0e-5 Msun, radius = 8.0 AU, phase = 1.0 rad.
  Radius/phase are NOT fitted (Stage B frees masses only).
  Inventor mass is deliberately NOT the truth mass: the demo
  must recover mass, not start on it. Scan offsets from the
  inventor value therefore include +1 decade = the truth mass.
- **Data:** same ts/sigma/noise-seed as the k=0 proof, but
  clean positions propagated with the joint driver at the TRUTH
  mass (planet rails + truth perturber). t_ref = 5.0.
- **Partition:** train = first 70% by time (42 obs), holdout =
  last 30% (18 obs), matching `check_fit` (round(0.30 × 60) = 18).
- **Full-data joint fit:** n_starts = 3, seed = 0, max_nfev = 500,
  early_stop_rms = 2 × sigma. Strict starts only (data-driven
  tracer start on the fitted data; mass scan per D10; NO
  full-data hint — there is no earlier full-data joint fit to
  hint from, and the checker refit below uses training data
  only by construction).
- **Checker:** `check_model` on the full-data joint fit:
  train refit n_starts = 3, seed = 0, early_stop_rms = 2 × sigma,
  strict starts (data-driven start on TRAIN data only, mass
  scan per D10). Null model: k = 0 driver, same partition,
  same starts/seed, train refit likewise. MSE ratio from the
  two train refits' holdout RMS values.
- **Removal test:** the null train refit above, same partition;
  contribution claim = MSE ratio ≥ 1.2 with a converged null
  refit, else abstain (unconverged null refit → abstain
  everywhere for the k = 1 contribution claim).
- **Pragmatic variant:** NOT run (strict refit is the acceptance
  path; pragmatic starts are corroboration only if strict
  fails to converge, and that branch is not exercised here
  unless the strict refit fails — in which case the demo
  verdict is reported as failed/abstained, not rescued by a
  pragmatic run in this batch).

## Cost measurement (measured after the prototype exists)

- Per fit: wall seconds, total nfev (sum over starts as reported
  by the winning start — stated, since `fit_state` reports only
  the winning start's nfev), winning-start nfev.
- Per predict: single-trajectory wall time for k = 0, 1, 2, 3
  (same tracer state, same ts, perturber masses 1e-4 Msun at
  radii 8/12/16/20 AU, phases 1.0/2.0/0.5/1.5) — predict-time
  scaling only; full k = 2/3 fits are NOT run (out of demo
  scope) and no k = 2/3 fit cost is extrapolated.
- Checker cost: wall time of the k = 1 `check_model` call
  (dominated by the joint train refit + null train refit),
  reported separately from the full-data fit time.
- Hardware: this Linux VM (stated in the results file).

---

*Plan written 2026-10-26, before any prototype run. D10/D11 as
above are the bars; results do not move them.*
