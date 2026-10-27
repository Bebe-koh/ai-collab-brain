# Gravity Mapper: System-GM Fix + Barycenter Consistency + −y Drift Diagnosis

**Date:** 2026-10-13  
**Status:** GM fix applied and verified; barycenter vectors installed; −y drift diagnosed (inner-planet spline bias); candidate-indirect verified essential.

## 1. The System-GM Fix (x-drift eliminated)

**Problem:** Pipeline integrated TNOs with planet BODY GMs; JPL/Horizons uses planet SYSTEM GMs (body + moons). Jupiter's δμ/μ = 2.07e-4 (moons' mass fraction) produced a 299 km common-mode x-drift.

**Fix applied** to `tno_hunt.py`, `residual_hunt.py`, `diag_per_tracer.py`, `diag_mutual.py` (GM_SI dict):
- Jupiter 1.267127639e17, Saturn 3.79405862e16, Uranus 5.7951574e15, Neptune 6.83667731e15 m³/s² (JPL system GMs).
- Earth: (GM_Earth + GM_Moon)/MU_SUN — EMB rail paired with EMB mass (no double-count; verified consistent).
- Mercury/Venus/Mars: unchanged (no significant moons).

**Before/after (TNO null, 74 TNOs):**
| Metric | Before (body GM) | After (system GM) |
|--------|------------------|-------------------|
| Stacked x-drift at t=15 | 299 km | 13.2 km RMS (gone) |
| Train RMS (median) | — | 194 km |
| Holdout RMS (median) | — | 540 km |

The decisive test predicted 5.5 km agreement with Horizons using system GMs; we achieve 13.2 km stacked x-RMS (residual is the −y drift, see §3).

## 2. System-Barycenter Vectors (Jase's "everything we know")

**Problem:** `planet_ephemerides.csv` used Horizons COMMAND='599' etc. (planet BODY centers). Paired with system GMs, this leaves the moons' barycenter wobble (~184 km for Jupiter at 2010-01-01, up to ~227 km) in the positions — right at the 239 km noise floor.

**Verification:**
- Horizons '599' vs '5' at 2010-01-01: diff = (−149.7, −107.6, −5.7) km, |d| = 184.4 km. Confirmed body-center.
- Horizons '5' vs SPICE DE440 ID 5: agree to 2e-9 km (same ephemeris).

**Fix:** Replaced outer-planet rows in `planet_ephemerides.csv` with SPICE DE440 system-barycenter vectors (IDs 5,6,7,8) at the same epochs. Inner planets unchanged (no moons; Earth via EMB). Original backed up to `/tmp/planet_ephemerides_bodycenter.bak`.

**Effect:** Null RMS unchanged (194/540 km) — the wobble is high-frequency (1.8–16.7 d periods, aliased by 30-d sampling) and averages out for TNOs. But the physics is now consistent: system-mass at system-barycenter for all four outer planets.

## 3. The −y Drift: Diagnosis

**Symptom:** After the GM fix, a common-mode −y drift was exposed: (pipeline null − validated integration) = −1176 km at t=15 yr, quadratic (R²=1.0000), identical across TNOs. Implied constant acceleration: −6.88 km/yr² in y. Also a −27.6 km/yr y-velocity offset (linear term).

**Ruled out:**
- GM errors (δμ fit ≈ 0; x-drift gone).
- Integrator (RK4 vs DOP853: 0.07 km).
- Planet rails, outer (indirect-term DC ≈ 0 per planet).
- EMB construction (DC = −0.33 km/yr², negligible).
- Initial conditions (t=0 matches to 0.00 km; V0 identical).
- 66-s epoch offset (real, but only ~26 km oscillatory).

**Found:** The pipeline's 30-day cubic-spline rails for Venus/Earth have systematic biases. Direct measurement (pipeline spline vs SPICE, correct TDB epoch):
- Venus spline midpoint error: mean 182,431 km, max 1,306,676 km.
- At t=0, pipeline vs reference accel agree (+0.07 km/yr²). At t=0.1, they differ by +725 km/yr² in y — the spline interpolation introduces huge high-frequency errors that average to a −6.88 km/yr² DC bias in y.

**Mechanism:** 30-day sampling is inadequate for Venus (225-d period; 7.5 samples/orbit). The cubic spline oscillates between samples; the oscillation has a non-zero time-mean (DC component) that appears as a constant −y indirect-term error. This integrates to the quadratic −y drift.

**Impact on hunt:** The hunter fits the −y drift with a phantom candidate: 2.3e-7 M⊕ @ 9.4–9.7 AU, 10–11× holdout improvement, dBIC +28,000. This is NOT a real body — it's the fitter exploiting the candidate's rotating indirect term to mimic the systematic drift. Same artifact class as v1's 12 M⊕ phantom.

**Fix required (future work):** Finer ephemeris sampling for inner planets (2-day, like Mercury) or direct SPICE queries. The 30-day splines are the limiting systematic.

## 4. Candidate Indirect Term: Verified Essential

**Check:** All three candidate models (`tno_hunt.py:var_eval`, `residual_hunt.py`, `sealed_scenarios.py:propagate_delta`) include the candidate's indirect term: `a_cand = mu_c * (d/|d|³ − rc/|rc|³)`. The `−rc/|rc|³` is the Sun's reflex motion, appearing as a common-mode +μ_c·r_c/|r_c|³ on tracers. **Not omitted.**

**Test:** Sealed scenario `distant_heavy` (truth: m=1e-4 M☉, r=100 AU, phase=1.0 rad), solved with and without the indirect term:

| Model | Recovered m | Recovered r | Recovered phase |
|-------|-------------|-------------|-----------------|
| With indirect | 0.000101 (+1%) | 99.88 (−0.1%) | 0.9975 (−0.0025) |
| Without indirect | 0.000075 (−25%) | 96.61 (−3.4%) | 0.9857 (−0.014) |

**Verdict:** Omitting the candidate indirect term causes a 25% mass underestimate and 3.4% radius underestimate. The indirect term is essential for accurate recovery and is correctly included.

## 5. Hunt Re-verdict

**TNO hunt with system GMs + barycenter vectors (74 TNOs, 480 candidates):**
- Null: train 194 km / holdout 540 km (median).
- Grid best: 1.30× train improvement (vs null).
- Refinement finds: **m=2.36e-07 M⊕ @ 9.7 AU, 11.0× holdout, dBIC +29,288.**

**Verdict:** The hunter fits the −y systematic drift with a phantom candidate. This is NOT a real body — it's the fitter exploiting the candidate's rotating indirect term to mimic the −6.88 km/yr² systematic acceleration from the inner-planet spline bias (§3). The "detection" is an artifact of the unmodeled systematic.

**True verdict:** Clean null for real bodies, CONTAMINATED by the −y systematic. The hunt cannot distinguish a real 2e-7 M⊕ @ 10 AU body from the systematic drift. Sensitivity is limited by systematics, not noise.

## Explicit Non-Claims

- The 2.3e-7 M⊕ @ 9.4 AU "candidate" is a systematic artifact (fits the −y spline-bias drift), NOT a detection.
- The −y drift is a pipeline systematic (inner-planet ephemeris interpolation), NOT evidence for a hidden body.
- The null result (no hidden body) is bounded by the −y systematic, not just the 239 km noise floor. Sensitivity claims must account for this.
- Planet Nine (10 M⊕ @ 400 AU) remains unrecoverable in this data (proven earlier); this null does not disprove it.

## Files Changed

- `real_data/tno_hunt.py`, `residual_hunt.py`, `diag_per_tracer.py`, `diag_mutual.py`: system GMs.
- `real_data/planet_ephemerides.csv`: outer planets → system-barycenter vectors (backup: `/tmp/planet_ephemerides_bodycenter.bak`).
- This note: `hidden_files/gm_fix_note.md`.
