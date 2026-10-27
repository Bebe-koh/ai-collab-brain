# Gravity Mapper Full-Data Residual Hunt — Tech Note
**Date:** 2026-10-13
**Working dir:** `~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/`

## What was done
Ran the gravity-mapper residual hunt on real JPL Horizons data:
1. **Inner hunt** (`residual_hunt.py`): Ceres, Earth (as Earth-Moon barycenter), Mars, Vesta as massless tracers; Sun + 8 planets on interpolated true ephemerides ("on rails", never integrated).
2. **TNO hunt** (`tno_hunt.py`): 74 extreme TNOs (a > 150 AU or scattered/extended) with full state vectors from Horizons, same null model.

Method (both): RK4 null integration (dt=0.004 yr) → residuals = observed − predicted → first-order variational candidate evaluation (validated vs exact re-integration at 1.011×) → 990-point log grid on train split → Nelder-Mead refine top-15 → holdout BIC-style scoring → hypothesis tracker wiring.

Train/holdout split: first 10.5 yr train (128 epochs), last 4.5 yr holdout (55 epochs). N_ho(inner)=660, N_ho(TNO)=12210.

## Data files used
- `planet_ephemerides.csv` — 8 planets × 183 epochs, 15 yr, 30-day steps, true Horizons vectors (heliocentric, 500@10).
- `horizons_tracers_full.csv` — Ceres, Earth, Mars, Vesta × 183 epochs, with velocities.
- `tno_vectors.csv` — 74 extreme TNOs × 183 epochs, pulled 2026-10-13 via `pull_tno_vectors.py` (16 of 90 designations failed: Horizons can't resolve those provisional IDs).
- `moon_ephemeris_vel.csv` — Moon × 183 epochs with velocities (for Earth-Moon barycenter).

## Inner-hunt results
Null residuals (train/holdout RMS): Ceres 2.07e-4/3.90e-4 AU; Earth(EMB) 1.11e-4/1.16e-4; Mars 9.07e-5/1.05e-4; Vesta 1.19e-4/3.42e-4 AU.

Best candidate cand_00: m=2.08e-6 M☉ (0.69 Earth masses), r=3.20 AU, phase=2.79 rad. Holdout 4.03× improvement, dBIC=+901.

**Verdict: NULL STANDS.** Per-tracer diagnostic (`diag_per_tracer.py`): cand_00 improves Ceres 5.35× and Vesta 6.41× but *worsens* Earth (0.98×) and Mars (0.84×). A real body must perturb all tracers coherently; this one doesn't. Its mass (0.69 M_earth at 3.2 AU) is observationally ruled out. It's an epicycle fit to main-belt systematics (unmodeled Pallas/Hygiea/diffuse belt mass), not a body. All 16 candidates scatter across 0.12–7.79 AU with similar dBIC (degeneracy ridge).

## TNO-hunt results
Null residuals: train median 1.56e-4 AU (23,334 km), holdout median 5.36e-4 AU (80,126 km). Residual growth 4.02× (quadratic → constant-acceleration systematic).

**Uniform +y systematic:** All 74 TNO residuals point in +y (mean unit vector (0.245, 0.968, 0.054), |m|=0.9996). TNOs are NOT clustered in +y (their mean position |m|=0.125, 47% have y>0), so this is a genuine common-mode acceleration, not a sky-selection effect.

**Best candidate (TNO):** m=3.59e-05 M☉ (12.0 Earth masses), r=11.1 AU, phase=3.94 rad (226°). Holdout 15.29× improvement, dBIC=+33267.

**Verdict: CANDIDATE IS SPURIOUS — NULL STANDS.** 
1. A 12-Earth-mass planet at 11.1 AU (between Saturn and Uranus) would be easily visible; ruled out observationally.
2. The candidate sits at phase 226° (-x,-y quadrant). Its *indirect* acceleration (-μ_c r_c/|r_c|³) points in direction (0.695, 0.719, 0) — mostly +y. The indirect term is a *uniform* acceleration applied to all TNOs. The optimizer placed the candidate to maximize the +y indirect component, fitting the common-mode +y systematic. A real planet would perturb TNOs via direct gravity (geometry-dependent), not via a uniform indirect term.
3. The +y systematic itself (5e-4 AU, uniform, quadratic growth) is not consistent with any gravitational point source (would require ~0.11 M☉ at 1000 AU — a visible star). It remains an unexplained common-mode, likely a subtle force-model or ephemeris systematic, NOT a hidden body.

The hypothesis tracker was wired for the inner hunt (posterior 1.0 on cand_00, "not surprised"). For TNOs, the candidate was rejected by the indirect-term coherence test before tracker scoring — a uniform-acceleration fit is not a planetary hypothesis.

## Bugs found and fixed
1. **Solar GM:** Was using 4π² (3.8e-5 fractional error → 1e-3 AU spurious drift). Fixed to DE440: 39.476926 AU³/yr².
2. **Earth's Moon wobble:** Geocenter wobbles ±3e-5 AU due to Moon; 30-day sampling aliases the 27.3-day orbit. Fixed by using Earth-Moon barycenter (EMB) — observed EMB from real ephemerides, predicted with smooth model; wobble cancels identically.
3. **Moon velocity:** Spline derivative at t=0 boundary was off ~0.6 AU/yr → 0.06 AU drift. Fixed with Horizons direct velocities.
4. **Indirect term:** Was dropping it for the skipped body; fixed to drop only the direct self-term.
5. **TNO var_eval:** `deltas[:, 0]` uninitialized (np.empty garbage) → 5e6 AU divergence. Fixed by setting to 0.
6. **TNO shapes:** Multiple broadcasting bugs in candidate evaluation (`r_var`, `D`, `T_var` axes). Fixed.

## What is NOT claimed
- No detections. No validations. No discoveries.
- The inner-hunt candidates are epicycles (proven by per-tracer incoherence).
- The TNO +y systematic is unexplained and is NOT claimed as a body.
- All "candidates" are coherent residuals awaiting physical interpretation, not detections.

## Addendum (2026-10-13): +y systematic diagnosis + ROM consolidation

**Systematic diagnosis:** The uniform +y acceleration (1.14e-5 AU/yr²) was
investigated exhaustively. It is real (two independent integrators agree to
0.2%), TNO-specific (inner hunt clean), and not explained by: integrator error,
interpolation error (spline accurate to 1e-7), GM/mass errors, Moon/EMB, time
grids, frame mixup, barycentric confusion, or missing physics (all <1e-8).
Leading hypothesis: model's indirect term ~1–2.4% too strong vs Horizons' TNO
dynamics, but no mechanism identified. Full analysis:
`../plus_y_systematic_note.md`. **Cause unidentified; NOT claimed as physics.**

**ROM consolidation:** Both rejected candidates consolidated into ParentROM
(582 → 654 bytes, 16 → 18 hypotheses, 2 consolidations) with attributed
posterior 0.0 (recorded as explored-but-rejected, n_good NOT incremented).
Rich labels (pattern → label → rejection reason) in
`../attribution_labels.json`:
- Inner epicycle (0.69 M⊕ @ 3.2 AU): unmodeled main-belt mass, coherence FAIL.
- TNO artifact (12 M⊕ @ 11.1 AU): indirect-term fit, would be visible.
- +y systematic: unexplained common-mode, must resolve before P9 constraints.

## Commands run
```bash
cd ~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data/
python3 residual_hunt.py > hunt.log 2>&1          # inner hunt
python3 diag_per_tracer.py                        # per-tracer coherence check
python3 diag_mutual.py                            # Ceres↔Vesta mutual gravity check
python3 tno_hunt.py > tno_hunt_full.log 2>&1     # TNO hunt
```

## Files produced
- `hunt_results.json` — inner-hunt candidates with train/holdout MSE, dBIC.
- `parent_rom.json` — ParentROM with consolidated learnings (582 bytes).
- `_tno_null.npz` — TNO null residuals (t_epochs, obs, null_pred, masks).
- `tno_hunt_results.json` — TNO candidates (when hunt completes).

## Follow-up pointer (2026-10-13): Moon sampling investigation + inner-hunt re-run
- `moon_fix_note.md`: the suspected 30-day Moon sampling "bug" was investigated and closed —
  measured effect exactly **0.0 AU** (the EMB is built from exact epoch samples; the lunar
  orbit is never splined, unlike Mercury). `moon_fine.csv` (2-day) pulled as a loader safeguard.
- The re-run was the first inner hunt with the Mercury 2-day ephemeris active: null tightened
  ~2.8×/10× (train/holdout), the v1 "0.69 M⊕ @ 3.2 AU" candidate did **not** reproduce
  (grid best 1.00× null, all dBIC negative) — it was an artifact-assisted fit. Clean null stands.
