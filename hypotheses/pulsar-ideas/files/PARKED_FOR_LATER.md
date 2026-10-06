# Pulsar ideas — parked for later (2026-10-06)

Jase chose to pursue idea 02 (cislunar XNAV) first. The four below are parked, not
abandoned. Each has a one-paragraph brief plus the verification plan that was
written for its fresh-run worker, so any of them can be resumed by spawning a
worker with the brief + plan.

Work directories exist (empty): `~/workspace/pulsar-ideas/01-*`, `03-*`, `04-*`, `05-*`.

---

## 01 — Glitch forecasting for pulsar timing arrays (PARKED)

**Brief:** Pulsar glitches corrupt gravitational-wave timing-array data. Jase verified
Vela's fast relaxation term (~1 min, B_eff≈2.0e-4) repeats identically 16 years apart
(2000 & 2016 glitches), and built a tanh-transient matched-filter + surrogate-null
pipeline for the Kerr project
(`~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data/evpa_transient_search.py`).
Test: point that machinery at pulsar timing residuals to detect *precursor*
signatures before glitches — an early-warning system with direct value to NANOGrav.

**Resume plan:** (1) Prior-art search: glitch precursors / pre-glitch behavior /
glitch forecasting literature; locate public data (NANOGrav public timing, ATNF
glitch table, Vela/Crab TOAs). (2) Fresh run: rebuild the transient-search core
(matched filter over template grid + surrogate null), adapted to red, irregularly
sampled timing residuals; run on 2–3 documented glitch epochs. (3) Verdict:
works/partial/fails + why + fix. Deliverable: `01-glitch-precursors/fresh_run_note.md`
+ script. Honest nulls required.

## 03 — Cheaper noise modeling for PTAs via covariance matching (PARKED)

**Brief:** PTA gravitational-wave detection needs exquisite per-pulsar noise models;
full Bayesian analysis (enterprise/temponest) is computationally brutal. Jase
quantified that an adaptive Kalman filter with covariance matching converges to a
stable non-ML fixed point absorbing model error into estimated noise (~2x separation
vs direct likelihood). Mechanism is folk knowledge — MUST cite Brown & Rutan and
frame the contribution as the quantified separation, not the mechanism. Test: a
"good enough, provably stable" noise-estimation shortcut at a fraction of the cost.

**Resume plan:** (1) Prior art: PTA noise-modeling practice + compute costs,
existing cheap approximations, Brown & Rutan's statement. (2) Fresh run: synthetic
PTA-like data with deliberately mismatched analysis model; compare adaptive
covariance-matching filter vs direct likelihood scan — stability, fixed-point
separation (~2x claim), wall-clock savings, downstream detection-power preservation.
(3) Verdict + why + fix (e.g., valid only for mild mismatch, or as initializer).
Deliverable: `03-cheap-pta-noise/fresh_run_note.md` + code.

## 04 — Automated achromaticity classifier (PARKED)

**Brief:** ISM noise is chromatic, spin noise achromatic, but classification is
hand-tuned per pulsar. Jase's B1937+21 method
(`~/workspace/prtp/hidden_files/b1937_wobble_note.md`): contemporaneous
native-bin cross-correlation across bands, inverse-variance weighted
(wcorr=0.9987/0.9976/0.9997). Test: turn it into an automated per-pulsar,
per-epoch classifier feeding PTA noise models.

**Resume plan:** (1) Prior art: PTA chromatic/achromatic separation (DMX, chromatic
GPs), existing classifiers, public multi-band data. (2) Fresh run: rebuild the
method independently; apply to ≥3 pulsars — one known achromatic (B1937+21),
one known chromatic (strong DM variations), one ambiguous; check controls land
correctly with calibrated uncertainty. (3) Verdict + why + fix (minimum data
requirements, restricted claims). Deliverable:
`04-achromaticity-classifier/fresh_run_note.md` + code.

## 05 — Pulsar noise metrology (PARKED)

**Brief:** Flip PRTP: use a top-grade clock under a dedicated pulsar campaign to
measure pulsars' *intrinsic* noise floors better than observatories can. From
Jase's repair (`~/workspace/prtp/hidden_files/chain_binned_note.md`): binned
products understate white noise up to ~100x; fit it or propagate from chains.
Test: quantify the gap — what clock grade + campaign design pushes below current
published red-noise floors?

**Resume plan:** (1) Prior art: what limits timing floors (radiometer, jitter,
ISM, clock — NANOGrav budgets, Shannon & Cordes), DSAC/maser performance,
existing attempts; is the clock ever the binding constraint? (2) Fresh run:
Fisher/simulation with radiometer + jitter + clock (Allan-deviation
parameterized) + intrinsic red noise, white level fit freely; map constrainable
red-noise amplitude vs clock grade; identify the binding constraint. (3) Verdict
+ why + fix (or narrower claim). Deliverable: `05-noise-metrology/fresh_run_note.md`
+ code. If the gap doesn't exist, that IS the result.
