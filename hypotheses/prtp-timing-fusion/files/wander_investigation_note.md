# The B1937+21 x B1855+09 wander — deep investigation note

Date: 2026-09-24. Status: **archival-data analysis. Not a detection of
anything.** Builds on `b1937_b1855_note.md` (2026-09-22); new here is the
full-resolution (167/112-bin) analysis, the look-elsewhere-corrected
chance test, and the backend-transition timeline.

## Question

Two pulsars' 30-day binned residuals correlate at r = 0.916 over the 14
common epochs (MJD 57212–58952), while their red-noise models predict
~10x less wander. This correlation has now fooled two spatial templates
(Hellings-Downs quadrupole, annual-dipole ephemeris). What is it — a
shared physical/systematic cause, or a chance alignment of red noise?

## Method

- 14-epoch common data: leave-one-epoch-out correlation; correlation
  after common-mode removal; correlation after cubic detrending;
  lag-1 autocorrelations (redness).
- Full-resolution binned series (B1937: 167 bins, B1855: 112 bins,
  MJD 53282–59072): overlap correlation (104 common bins); sliding
  4.8-yr window correlation across the 15-yr span; jump scan;
  yearly means for shape.
- Chance test: phase-randomized surrogates preserving the empirical
  spectrum; test statistic = max |r| over sliding 4.8-yr windows
  (look-elsewhere-corrected, 2000 sims).
- Backend timeline from `.tim` backend flags (ASP/PUPPI/GASP/GUPPI
  transitions per pulsar).

## Results

**1. The correlation is the shared slow drift — nothing else.**
r = 0.916 raw; 0.968 after common-mode removal (so it is not the
monopole); **−0.148 after cubic detrending**. Post-cubic residual rms:
B1937 148 ns, B1855 116 ns — within ~2x of the chain predictions
(301/107 ns). The *entire* excess over the noise model lives in the
cubic-scale drift. Leave-one-epoch-out r stays 0.906–0.931: no single
epoch drives it.

**2. It is confined to the 2015–2020 window.** Over the full 15 years
(104 overlapping bins) the pair correlates at r = **−0.18**. Sliding
4.8-yr windows: only the common-epoch window itself ever exceeds
|r| = 0.9 (max 0.932). The "shared wander" does not persist outside
2015–2020.

**3. B1937's rise is smooth and fully sampled; B1855's is not.**
B1937 climbs +5519 → +9694 ns smoothly across MJD 57872–58562
(~4.2 µs over 700 days, no jumps), then plateaus. B1855's bins have a
gap MJD 57992–58442 exactly where its rise occurs — smooth vs jump is
unresolvable for B1855. The two rises are not demonstrably
synchronized; both are simply "higher late than early."

**4. Chance-alignment test: p = 0.045** (look-elsewhere-corrected over
the 15-yr span, redness matched to the data). I.e., in ~1-in-22
phase-randomized worlds, *some* 4.8-yr window reaches |r| ≥ 0.93.
Marginal: too likely to claim a shared cause, too rare to dismiss
comfortably. (Under the chain-median noise params the prior note found
0.3% — but those params underpredict the binned variance 6–12x, so
that null is misspecified.)

**5. Both pulsars are extremely red.** Lag-1 autocorr: B1937 0.912,
B1855 0.860 (J1909 0.763, J0437 −0.376). Effective dof ~2. B1937 shows
a giant quasi-cyclic ~15-yr wander, 17 µs peak-to-peak
(+5.4 → −7.4 → +9.5 µs in yearly means) — vastly beyond its
chain-median red model, and the dominant feature of its 15-yr record.

**6. No backend transition aligns.** B1855: ASP → PUPPI at MJD 55990
(pre-window; 100% PUPPI inside the window). B1937: GASP → GUPPI
~55275, ASP → PUPPI ~56020 (both pre-window); inside the window its
data interleaves AO/PUPPI and GBT/GUPPI throughout with no clean
split. A backend systematic would also more naturally make jumps,
not a smooth multi-year ramp — and the observed rise *is* smooth
(where resolved).

**7. Side findings.** (a) B1855 has a wild jump episode MJD
55112–55772 (±3000 ns swings between adjacent 30-day bins, ASP era)
— predates the window, likely unrelated, flagged as a data-quality
note. (b) J1909×B1937 = −0.98 after common-mode removal is a
**mathematical artifact**: subtracting a common mode 89%-weighted on
J1909 injects an inverted copy of B1937's drift into J1909's
leftover; both leftovers are ~pure drift with opposite signs. Not
physical. The raw −0.83 is chance anti-alignment of drift vs common
mode in this window.

## Interpretation

The most economical reading, unchanged from the prior note but now
better evidenced: **chance alignment of two independent steep-red-noise
processes on ~2 effective degrees of freedom.** The new evidence
for it: window-confinement (r = −0.18 outside), smoothness of the
resolved rise, cubic-detrend collapse, and a look-elsewhere-corrected
p = 0.045 under empirically-matched redness.

What would change this verdict: a *synchronized* feature — e.g., if
B1855's rise (currently in a data gap) were resolved and showed a
jump at the same MJD as a B1937 feature, or a backend/clock log
event at a shared MJD. None exists in this data. The clock-file
cross-check (separate thread) independently disfavored observatory
clock coherence, and the ephemeris/GWB templates already failed —
leaving no surviving shared-cause candidate with any positive
evidence behind it.

## The deeper open question (reframed)

Why do binned residuals carry ~10x the red variance the TOA chains
predict? New framing from this work: after cubic detrending, the
residuals match the chains within ~2x — so the discrepancy *is* the
slow drift. Either the TOA-level power-law red model underfits
very-low-frequency/quasi-deterministic wander (B1937's 15-yr
quasi-cycle is not well described by a stationary power law), or the
timing-model fit absorbs the slowest component differently at TOA
level than in this binned representation. Resolving it needs the
TOA-level analysis, not more binning.

## Caveats (read before quoting)

- N = 14 clustered epochs for the headline correlation; the
  look-elsewhere test uses the full 15-yr binned data but the bins
  are 30-day averages with heterogeneous errors.
- Phase-randomized null assumes stationarity; B1937's quasi-cycle
  may violate it mildly.
- B1855's rise is unresolved (data gap 57992–58442): smoothness of
  the *shared* component is established only for B1937.
- DM/chromatic tests impossible with this frequency-averaged binned
  product; DMX-mismodeling as a contributor is not excluded, though
  correlated DM errors across 13°-separated sightlines are unlikely.
- Backend census: per-epoch .tim flags confirm the timeline above;
  backend *calibration drifts* (as opposed to jumps) cannot be ruled
  out from flags alone, but no mechanism is proposed.

## Files

- `wander_investigate.py` — characterization script (A/B/C/D/E/F/G blocks)
- `wander_investigation.json` — all numbers: LOO table, detrends,
  autocorrs, surrogate p, sliding windows, jump scans, yearly means,
  backend transitions
- inputs unchanged: `nanograv_binned.npz`, `aldm_real_results.json`,
  `nanograv15yr/extracted/narrowband/tim/*.nb.tim`
