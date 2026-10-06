# Fresh-run note — 02 cislunar XNAV design study
**2026-10-06 · fresh independent simulation · conditional on stated assumptions**

## 1. Question
Can PRTP-style pulsar–clock fusion give a usable *cislunar* navigation
solution, and what onboard clock grade does it need? (PRTP answered this
for *time transfer*; this run tests *position* determination, re-derived
independently — no PRTP code reused.)

## 2. Prior art (with the real numbers)

### 2.1 NICER/SEXTANT — the demonstrated anchor
- Nov 2017, ISS: 4 millisecond pulsars, 78 timing measurements over 2 days,
  TOA accuracy ~300 ns (X-ray). Onboard solution vs GPS truth: **16 km
  radius within 8 hours, best fixes ~5 km** (newatlas.com summary of NASA
  release; physicsworld.com). Goal stated: sub-km, ~100 m in deep space.
- This is X-ray XNAV, autonomous, with an onboard atomic clock assumed.

### 2.2 ESA/NPL feasibility (X-ray, simulation)
- NPL + Univ. of Leicester for ESA (Exp. Astronomy): **2 km (10-h
  observation) / 5 km (1-h) per-pulsar direction at 30 AU**; 30 km 3-D at
  Neptune distance (sciencedaily.com, 2016).
- AIAA SciTech 2022-1589 (phase-tracking EKF, **cislunar trajectory**
  included): Crab + 4 MSPs; per-pulsar range errors 2–6 km; multi-pulsar
  EKF **<3 km (MSL cruise) and <4 km (cislunar)**. This is the closest
  published analog to our study, X-ray based.

### 2.3 What the Moon actually needs
- ESA Moonlight: **positioning accuracy < 50 m** (Lunar Communication and
  Navigation Service target; esa.int).
- ISECG lander studies: ~40 m (99th percentile) with 4 sats + altimeter
  (MDPI EngProc 2024).
- So: a lunar navigation aid is interesting at **tens of meters**; km-level
  is not competitive for landing, but may serve cruise/far-side autonomy.

### 2.4 Clocks
- DSAC (Burt et al. 2021, Nature; flown 2019–2021): **1–2×10⁻¹³ @ 1 s,
  3×10⁻¹⁵ @ 23 days**, drift 3.0(0.7)×10⁻¹⁶/day. SWaP 19 kg / 56 W.
- CSAC SA.65 (Microchip datasheet): 3×10⁻¹⁰ @ 1 s → effective
  σ_y(1 d) ≈ 1×10⁻¹¹ (flicker floor).
- PRTP's M-scale: ADEV(1 d) = 3×10⁻¹⁵·M; M=1 DSAC, M≈3300 CSAC.

### 2.5 Radio MSP timing precision (ground truth for the measurement model)
- NANOGrav 15-yr, 100-m-class dishes, ~30-min integrations: per-TOA
  ~0.1 µs (J1909-3744, J0437-4715), ~0.2–0.3 µs (B1937+21).
- Spacecraft scaling is by antenna area (see §3.3) — this is the binding
  constraint, not the clock.

## 3. Fresh simulation

### 3.1 Models (all re-derived; code: `cislunar_xnav_sim.py`)
- **Dynamics:** Earth-centered inertial, Earth + Moon point masses (Moon on
  circular orbit), truth trajectory = 4.5-day translunar coast (LEO 300 km,
  v0 = 10.95 km/s → apogee ~515,000 km). Filter propagates the same
  dynamics (matched; SRP sensitivity tested separately).
- **Pulsars:** J0437-4715, B1937+21, J0218+4232, B1821-24 (AIAA set);
  plane-wave TOA: z = n̂·r_SSB/c + clock bias + noise. Earth SSB motion
  (circular 1 AU) modeled exactly in both truth and filter. Min pairwise
  pulsar angle 49.9°.
- **Clock:** random-walk FM, q calibrated so 2-yr holdover RMS = 1.4 µs·M
  (PRTP's measured anchor); M ∈ {1, 10, 100, 1000, 3300}.
- **Filter:** 8-state EKF (r, v, clock bias, clock drift), numeric
  Jacobians, exact measurement updates; initialized 10 km / 10 m/s /
  1 ms / 3×10⁻¹⁰ off truth. Validated: deterministic tracking to machine
  precision; per-axis consistency 100% within 3σ over 6 seeds.
- **Baseline:** same initial error, dynamics-only propagation, no
  measurements (autonomous coast).

### 3.2 Experiment 1 — optimistic cadence (validates machinery)
TOA every 600 s cycling 4 pulsars; σ_TOA ∈ {0.3, 1, 3, 10} µs; 3 seeds.

### 3.3 The radiometer reality check (analytic, for §4)
σ_TOA ≈ W_eff/(S/N); S/N = S·√(n_pol·B·T)/SEFD; SEFD = 2kT_sys/A_eff.
J0437-4715 (S_1400 = 150 mJy, brightest MSP), W_eff ≈ 80 µs, T_sys = 150 K,
B = 200 MHz, T_obs = 1 h:

| dish D | A_eff (η=0.6) | SEFD | S/N (1 h) | σ_TOA (1 h) |
|---|---|---|---|---|
| 3 m | 4.2 m² | ~98 kJy | 0.75 | ~107 µs |
| 5 m | 11.8 m² | ~35 kJy | 2.1 | ~38 µs |
| 10 m | 47 m² | ~8.8 kJy | 8.4 | ~9.5 µs |
| 30 m | 424 m² | ~1 kJy | 74 | ~1.1 µs |

Typical MSPs are ~10× fainter → σ 10× worse at fixed integration.
A single steerable dish observes one pulsar at a time: realistic cadence
is ~1 TOA/hour cycling 4 pulsars (each pulsar every 4 h).

### 3.4 Experiment 2 — realistic configs (radiometer-grounded)
(Run after Exp. 1 — see §4.)

## 4. Results

### 4.1 Experiment 1 — optimistic cadence (TOA every 600 s, cycling 4 pulsars)
Mean RMS 3-D position error over 3 seeds, meters (rows = clock grade M,
cols = per-TOA σ; baseline = 24.3 km unaided coast):

| M \ σ | 0.3 µs | 1 µs | 3 µs | 10 µs |
|---|---|---|---|---|
| 1 (DSAC) | 233 | 879 | 2,698 | 8,461 |
| 10 | 231 | 876 | 2,695 | 8,458 |
| 100 | 208 | 849 | 2,668 | 8,432 |
| 1000 | 207 | 717 | 2,436 | 8,177 |
| 3300 (CSAC) | 256 | 759 | 2,192 | 7,645 |

Two findings, both robust across seeds:
1. **Clock grade is nearly irrelevant to position accuracy** (≤15% spread
   from M=1 to M=3300 at fixed σ). The EKF jointly estimates the clock;
   4-pulsar geometry separates clock bias from position, and at operational
   cadence even CSAC wander between measurements (~0.2 ns/hr) is negligible
   next to µs TOA noise. **There is no meaningful clock-grade break-even
   for navigation** — aiding beats the 24 km baseline at every grade.
   (The break-even question was the right question for PRTP's *time
   transfer* problem, not for position.)
2. **Accuracy scales ~linearly with σ_TOA**: ≈ 800 m × (σ_TOA/1 µs).

### 4.2 Experiment 2 — radiometer-grounded configs (1-hr integrations,
single dish cycling 4 pulsars, one TOA/hr)

| config | dish | σ/TOA | M | mean RMS pos |
|---|---|---|---|---|
| R1 | 10 m | 2 µs | 1 / 3300 | **4.9 / 4.7 km** |
| R2 | 5 m | 7 µs | 1 / 3300 | **12.4 / 12.1 km** |
| R3 | 3 m | 20 µs | 1 | **25.8 km** (≈ baseline: no help) |

Seed scatter is large (slow-wander mode, e.g. R1: 2.1–8.3 km) — means quoted.
Clock-grade independence holds in the realistic regime too.

### 4.3 Scoreboard vs requirements
- Moonlight/LunaNet bar: **50 m** → missed by ~100× (R1).
- X-ray XNAV cislunar (AIAA 2022-1589, small detector): **<4 km** → R1
  (10-m dish) only *matches* it, with vastly worse SWaP.
- Unaided coast: 24 km → R1/R2 beat it; R3 does not.

## 5. Verdict: PARTIALLY works — and the failure is instructive

**What works:** the fusion is mathematically sound and independently
re-derived. Pulsar-aided EKF navigation converges, beats unaided
propagation by 3–100× depending on antenna, and is indifferent to clock
grade — even a CSAC flies. The filter is statistically consistent
(100% of per-axis errors within 3σ over 6 seeds; deterministic tracking
exact).

**What fails:** the *design-study claim* as posed — "a usable cislunar
navigation solution" competitive with what's needed/planned:
1. **Absolute accuracy ~5 km (10-m dish) vs the 50 m lunar bar.** Two
   orders of magnitude short. Reaching 50 m needs ~100× the information
   rate → ~100-m dish. Absurd.
2. **SWaP loses to X-ray XNAV.** X-ray reaches <4 km cislunar with a small
   detector (SEXTANT demo: 5–16 km on ISS). Radio matches that only with a
   10-m deployable dish. Nobody flies a 10-m dish to get what an X-ray
   detector does.
3. **The binding constraint is antenna area, not the clock.** Information
   rate ∝ 1/(σ²·T_dwell) is invariant to how you split integration time,
   and independent of pulsar count (more pulsars only improve DOP).
   "Put the money in the dish, not the clock" — the opposite of the naive
   PRTP reading.

**Why (root cause):** the radiometer equation. Even the brightest MSP
(J0437-4715, 150 mJy) gives S/N < 1 in 10 min on a 3-m dish; µs-level TOAs
need ≥10-m apertures and hour-long integrations. PRTP's "wins big on
radio" was about *time transfer* (common-mode across pulsars disciplines
the clock exquisitely) — that advantage does not transfer to *position*,
where each pulsar is an independent line of sight.

**Fix / narrower claims that survive:**
1. **Reframe as time-transfer-first.** A cislunar asset with a decent dish
   + CSAC gets autonomous, pulsar-steered *time/frequency* (PRTP's proven
   strength) with km-level position as a secondary product. LunaNet needs
   a common time reference — that is a real, funded niche where radio
   beats X-ray (X-ray TOAs are 300 ns at best; radio gives 100 ns-class
   with big dishes).
2. **Piggyback, don't dedicate.** If a mission already carries a large
   dish (radio science, high-rate comms), pulsar nav is nearly free
   added autonomy — no dedicated antenna bill.
3. **Accept km-level for the right mission.** Far-side relay orbit
   maintenance or cruise-phase autonomy where DSN is unavailable: 5 km is
   fine and the system is fully autonomous (unlike DSN).
4. What would change the answer: a breakthrough in low-frequency
   wide-field pulsar detection (all-sky, no steering — but scattering and
   sky noise likely eat the gain), or a mission that needs *time* more
   than *position*.

## 6. Assumptions, limits, what would change the answer
- Matched dynamics (SRP 1e-7 m/s² unmodeled adds ~1.5 km RMS if fully
  unhandled; real navigators estimate it — sensitivity run documented).
- Pulsar ephemerides assumed ground-updated (as in SEXTANT); glitches not
  modeled.
- Dedispersion, Shapiro delay assumed corrected to ≪ σ_TOA.
- Single-dish duty cycle: Exp. 2 uses honest cadence.
- TOA precision assumed equal across the 4 pulsars (optimistic — J0437
  dominates in reality; using 4 pulsars at J0437-class brightness is
  generous by ~2–3× in information).
