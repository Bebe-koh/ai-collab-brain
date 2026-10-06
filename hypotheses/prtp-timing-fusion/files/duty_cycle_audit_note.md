# PRTP duty-cycle audit — gates the NICER pilot (2026-09-24)

**Status: simulation-only, conditional reporting. No hardware-readiness or
validation claims.** This audit checks whether the X-ray PRTP simulation's
observing-duty assumptions survive contact with NICER/SEXTANT flight reality,
and specifies exactly what a public-data NICER pilot must demonstrate.

---

## 1. The concept's duty-cycle assumptions (extracted from the sim)

From `results.md` Round 4 (X-ray recast) and `xray.py`, all **SIMULATION ONLY**:

- **Instrument**: one pointed X-ray timing payload; two classes — NICER-class
  (1900 cm², ISS-proven) and probe-class (10× smaller area, plausible deep-space).
- **Dwell pattern**: 15- or 60-min dwells (bracketing SEXTANT's 5–15 min ops) +
  **5-min slew/settle**; the single instrument cycles the array sequentially, so
  per-pulsar cadence = full cycle time.
- **Cycle times**: bright-four 80 min (15-min dwell) / 260 min (60-min);
  full-ten 200 min / 650 min.
- **Implied on-source fraction**: 75% (15-min dwell: 60/80, 150/200) to 92%
  (60-min dwell: 240/260, 600/650) of **wall-clock time collecting pulsar
  photons**. Overhead modeled = slew/settle only.
- **What is NOT modeled**: zero Earth occultation, zero SAA/polar-horn loss,
  zero Sun/Moon exclusion, zero competing targets or science modes, zero missed
  dwells in the headline runs. (Round 6 S6 stress-tested 10% and 25% missed
  dwells: 1.03× / 1.10× RMS degradation — graceful.)
- **TOA precision**: Cramér–Rao per-dwell model, validated 0.87–1.06× against a
  photon Monte Carlo. NICER 60-min per-dwell: 16.5–169 µs across the 10-pulsar
  SEXTANT catalog set (bright four: 16.5–26.3 µs).
- **Architectural finding the duty cycle feeds**: with one pointed instrument,
  stare at the 4 brightest (J0437-4715, J0030+0451, B1821-24, J0218+4232 —
  exactly the SEXTANT 2017 demo set); faint pulsars are not worth the slew time.
  Cadence dominates over per-dwell precision (60-min ≈ 15-min for the Kalman).

The headline value proposition is clock-relative: NICER-class + causal Kalman
vs DSAC-class clock holdover = 618 ns vs 3795 ns over 3 yr (**~4–6× win**);
against a 100×-degraded clock, ~250× win (Round 5 S5: 10× win crossed at
~2.5× DSAC noise).

---

## 2. Literature: what NICER/SEXTANT actually achieved

- **SEXTANT demo (Nov 2017, ISS)**: 4 MSPs (J0218+4232, B1821-24, J0030+0451,
  J0437-4715), 78 timing measurements over 2 days, 5–15 min dwells. At ~10 min
  mean dwell → **~27% on-source fraction** over the 2-day experiment, vs the
  sim's 75–92%. Converged to 16 km in 8 h, best ~5 km
  (NASA Goddard release; newatlas/space.com/astronomy.com coverage).
- **NICER ISS good-time**: SAA + polar-horn radiation cuts reduce typical
  overall good time on targets to **~65%**; NICER tracks targets 80–90% of
  wall clock (balance mostly slews), <5% idle. Avoidance: Sun >45°, Moon >15°,
  Earth limb >30° (NICER Mission Guide, HEASARC; NICER Mission Overview:
  ">65% observing efficiency").
- **Uninterrupted exposures**: at most ~2.4 ks per 92-min ISS orbit, typically
  ~half that (~1.2 ks) — so the sim's 60-min (3.6 ks) dwells exceed the longest
  ISS-uninterrupted dwell, but are uninterrupted-exposure limits, not dwell
  limits; consecutive orbits re-acquire (NASA NSPIRES NICER Cycle 4 doc).
- **Realized TOA precision**: SEXTANT 1-hr TOA uncertainties ~2–35 km (1σ)
  across the four pulsars ≈ **~7–117 µs** (Springer 10.1007/s40295-021-00290-z,
  empirical S_τk coefficients). The sim's Cramér–Rao numbers (16.5 µs for
  J0437 at 60 min) sit inside this envelope — conservative by ~2–3× on the
  brightest, which is the safe direction.
- **Timing reference**: NICER GPS time-tagging better than 100 ns absolute
  (LaMarr et al. 2016; arXiv 2405.00087v1 processing notes) — usable as pilot
  ground truth.

---

## 3. Verdict: does the duty-cycle assumption survive?

**Partially — and the gap is not load-bearing.**

| Item | Sim assumed | Reality | Gap |
|---|---|---|---|
| On-source fraction | 75–92% of wall clock | NICER/ISS: ~65% good time; SEXTANT demo ~27% on-source over 2 days | ISS losses (occultation, SAA, polar horns) **do not apply** to a deep-space probe. Realistic dedicated deep-space: **~50–70%** after Sun exclusion (45°), slews, safe modes, competing modes |
| Dwell length | 15/60 min | Max uninterrupted ~2.4 ks ISS (1.2 ks typical); 60-min dwell = 3.6 ks | Fine in deep space (no orbit occultation); 60-min dwells need no ISS-style re-acquisition |
| Slew/settle | 5 min | NICER tracks 3–6 targets/orbit → ~15–30 min per target incl. slew | 5-min slew for 45°+ deep-space slews is optimistic but plausible for a gimballed dedicated instrument; flag as assumption |
| Missed dwells | 0% (headline) | SAA/occultation/Sun guarantee nonzero | **S6 already priced this**: 25% missed → 1.10× RMS. Graceful, not a cliff |
| TOA precision | Cramér–Rao, conservative ~2–3× | 7–117 µs/hr empirical | Sim is on the safe side |

**Key judgment**: the sim's 75–92% is optimistic by ~1.2–1.8× in on-source time
for a realistic dedicated deep-space payload, and the SEXTANT demo's ~27% shows
what a time-shared ISS platform actually delivered. **But the concept's
qualitative conclusions do not depend on 75–92%**: the S6 missed-dwell stress
test (the closest thing the sim has to a duty-cycle sensitivity analysis)
shows 25% missed dwells cost only 10% RMS, and the architectural finding
(bright-four beats full-ten; Kalman beats holdover; worth-flying boundary at
~2.5× DSAC noise) is driven by cadence *ordering*, which survives a uniform
duty-cycle haircut. The assumption that would actually hurt — unmodeled
per-dwell white noise from slew jitter (+35%, S6) — is a **flagging/data-quality
problem, not a duty-cycle problem**, and it is exactly what a real-data pilot
must test.

---

## 4. NICER pilot specification (public data only)

**Feasibility: yes.** All inputs exist in the public archive.

1. **Data**: HEASARC NICER public archive, the 4 SEXTANT pulsars
   (J0218+4232, B1821-24, J0030+0451, J0437-4715). These are long-running
   NICER timing targets with deep multi-year coverage.
2. **Processing**: standard NICERDAS pipeline (nicerl2, nimaketime GTI
   filtering: outside SAA, ELV>20°, BR_EARTH>30°). The GTI structure **is**
   the duty-cycle reality — no need to simulate gaps; use them.
3. **TOAs**: fold photons per GTI/dwell with published ephemerides, extract
   TOAs exactly as the sim's front end assumes (matched-filter template).
4. **Filter**: run the Round 5 causal Kalman clock-aiding filter on the real
   TOA sequence. Truth reference: NICER's GPS-disciplined timestamps / ISS
   orbit solution (better than 100 ns absolute).
5. **Test**: (a) per-dwell TOA precision vs Cramér–Rao prediction;
   (b) achieved causal-filter clock RMS vs sim prediction **at the realized
   duty cycle** (interpolate the S6 missed-dwell curve);
   (c) graceful-degradation check across GTI gaps — look for cliffs.

## 5. Go / no-go criteria for the pilot

**GO** (proceed to full pilot analysis) if all hold:
- (G1) Realized per-dwell TOA precision within **2×** of the sim's
  Cramér–Rao prediction for ≥3 of the 4 pulsars.
- (G2) Causal Kalman clock RMS within **1.5×** of the sim prediction at the
  matched realized duty cycle (using the S6 missed-dwell interpolation).
- (G3) No divergence or holdover-underperformance: Kalman beats the
  GPS-truth holdover baseline on real data, and gap crossings show smooth
  (predict-only) behavior, not error spikes.

**NO-GO** (pilot falsifies the operational concept) if any hold:
- (N1) Sustained realizable on-source fraction on the 4-pulsar set **<25%**
  (below the S6-tested envelope; cadence collapses).
- (N2) Unmodeled per-dwell systematics dominate: real background variability,
  pointing/attitude jitter, or gain drifts break the white-noise model —
  i.e., the S6 "+35% slew-jitter threat" materializes and flagging cannot
  recover it (dwell-flagging catch <85% at 5% false positives, cf. Round 6).
- (N3) Causal filter diverges or underperforms holdover on real TOAs —
  the sim-to-real transfer fails at the estimator level.

**Conditional note**: even a GO does not validate flight readiness — it
validates the *simulation's transfer* to one real dataset (ISS environment,
GPS truth available, 4 pulsars, NICER-class aperture). Deep-space-specific
terms (no GPS truth, Sun-exclusion geometry, probe-class aperture, multi-year
unattended operation) remain simulation-only extrapolations and must stay
labeled as such.

---

## Sources
- NICER Mission Guide (HEASARC): https://galex.caltech.edu/~srk/XC/Notes/NICER_Mission_Guide.pdf
  (65% good time; 80–90% tracking; Sun/Moon/Earth avoidance; 2 SAA/EVA losses 2017–18)
- NICER Mission Overview (HEASARC): https://heasarc.gsfc.nasa.gov/docs/nicer/nicer_about.html
  (>65% observing efficiency; GPS time reference better than 300 ns)
- NASA SEXTANT announcement: https://www.nasa.gov/centers-and-facilities/goddard/nasa-team-first-to-demonstrate-x-ray-navigation-in-space/
  (78 measurements, 2 days, 16 km in 8 h, best 5 km)
- Empirical XNAV uncertainty model (TOA 2–35 km/hr): https://link.springer.com/content/pdf/10.1007/s40295-021-00290-z.pdf?error=cookies_not_supported&code_code=bb801029-a693-4c27-8406-ac67d3822564
- NICER data processing / GTI filtering example: https://arxiv.org/html/2405.00087v1
- NICER uninterrupted-exposure limits: https://nspires.nasaprs.com/external/viewrepositorydocument/cmdocumentid=807380/solicitationId=%7B39E83E26-27E5-F53C-A1E1-A577DE5FB03A%7D/viewSolicitationDocument=1/D.11%20NICER_Cycle_4_Amend29.pdf
- Sim side: `~/workspace/prtp/results.md` Rounds 4–6, `~/workspace/prtp/xray.py`,
  `~/workspace/prtp/PRTP_final_report.md`
