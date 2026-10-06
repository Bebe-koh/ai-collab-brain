# Ranking the monopole's source: clock vs ULDM vs ephemeris — run note

Date: 2026-09-24. Status: **archival-data analysis. Not a detection of
anything.**

## Question

The 14-epoch NANOGrav common mode (±350 ns swings, chi2 = 406/14 vs the
white+red noise model) is a robust array-wide monopole — but its source is
open: clock error, ephemeris error, or ultralight-dark-matter (ULDM)
waveform. This note fits one signature model per candidate and ranks them.

## Method

Two families, same inputs as the prior notes (`nanograv_binned.npz`;
white variances from the bins; red variances = chain-median values from
`aldm_real_results.json`, [218, 33, 301, 107] ns for
J0437/J1909/B1937/B1855):

**Time domain** — fits to the published vetted common-mode series
(14 epochs, mean-subtracted, formal errors ~32–50 ns), ranked by BIC:
- M0 null (no common signal)
- M_clock: epoch-uncorrelated common variance, 1 param (sigma_c).
  Signature of clock jumps/corrections — or any array-wide white-ish
  systematic.
- M_uldm: coherent common sinusoid (ULDM Earth-term-like), 3 params
  (A, f, phi); frequency on an 80-point grid, periods 60 d–20 yr.
- M_smooth: smooth common red process, gamma = 4.5 fixed, free
  amplitude, 1 param. Control for any smooth source (slow clock drift,
  smooth ephemeris-like time dependence).

**Spatial** — fits to the full 56-point residual vector (per-pulsar
mean-subtracted), ranked by BIC:
- E0: per-epoch monopole only (14 params)
- E1: monopole + annual dipole n_a·(s·sin(2πt) + d·cos(2πt)) (14+6
  params). An Earth-orbit ephemeris error must appear as an annual,
  in-ecliptic dipole — this is its smoking-gun signature.
- Pulsar unit vectors from standard timing positions; validated by
  reproducing the note's HD matrix to 0.005 (their convention is the
  Earth-term ORF normalized to 1 at zero lag, i.e. 2x the raw ORF).

Jackknives: drop-one-pulsar and drop-pair on the spatial test.

## Results

Time domain (BIC; lower is better):
1. **M_clock: 188.4** — sigma_c = 181 ns, dlnL 173 vs null
2. M_uldm: 191.5 (ΔBIC 3.1) — best P = 6.7 yr, A = 345 ns
3. M_smooth: 262.4 (ΔBIC 73.9)
4. M0: 532.2

Spatial:
- E1 beats E0 by dlnL 184 (ΔBIC 344) — but the fitted dipole amplitude
  is **7638 ns**, ~100x any plausible ephemeris error, and its two
  components sit at ecliptic latitudes **−12° and −72°** (an Earth-orbit
  error must be in-ecliptic, ~0°).
- Pair jackknife: dropping B1937+B1855 collapses the E1 advantage
  184 → 6.9. Dropping J0437+J1909 leaves 73.3. The "dipole" lives
  entirely in the B1937/B1855 pair.

## Interpretation — the ranking

1. **Clock-like (epoch-uncorrelated common variance) wins.** The
   decisive feature is the sharp epoch-to-epoch jumps (+352 to −138 ns
   between adjacent 30-day epochs). Nothing smooth can produce them;
   nothing coherent is needed to explain them. sigma_c = 181 ns
   matches the series RMS (184 ns) from the earlier note.
2. **ULDM is not ruled out, but not detected either.** ΔBIC 3.1 is
   within noise — and that flatters ULDM, since the frequency was
   grid-selected (true penalty larger than k=3). Worse: the best-fit
   "period" (6.7 yr) **exceeds the data span (4.8 yr)**. That is not a
   periodicity detection; it is half a sine wave fitting a slow
   drift. A credible ULDM claim needs multiple cycles inside the span.
   The periodogram shows one broad hump at P > span, not a coherent
   peak.
3. **Smooth common processes are dead** (ΔBIC 74). Whatever the source
   is, it is not smooth.
4. **Ephemeris is disfavored on three independent grounds:**
   (a) it predicts a dipole, but the robust signal is a monopole;
   (b) real ephemeris uncertainties are ~10s of ns, not 350 ns;
   (c) the apparent annual-dipole excess is the *same* unexplained
   B1937/B1855 correlated wander (r = 0.94) that fooled the HD test —
   the pair jackknife proves it (184 → 6.9 without them). Same trap,
   different template.

## The honest caveat

"Clock-like" is a *signature*, not an identification. Clock
jumps/corrections are the leading physical candidate for
epoch-uncorrelated common variance — but backend changes, processing
jumps, RFI excision, or any array-wide systematic looks identical in
this data. This analysis cannot separate "the clock was wrong" from
"the array did something together." What would break the tie:
observatory clock-correction logs and backend/processing change logs
aligned against the 14 epoch dates — not in this dataset.

## Caveats (read before quoting)

- N = 14 clustered epochs; red noise is diagonal-only (no inter-epoch
  correlations) — same limitation as the prior notes. Sharp jumps argue
  the excess is real common variance, but exact BIC values are
  model-dependent.
- 4 pulsars → weak spatial leverage by construction; the ephemeris
  verdict is suggestive, not conclusive.
- ULDM pulsar terms (per-pulsar sinusoids at the same frequency) not
  tested — Earth-term-only scope.
- Data quirks for the record: the npz's `sig2` field is *not* the
  chain-median red variance used in the published notes (6 ns vs
  301 ns for B1937 — stale or different estimate); the red values in
  `aldm_real_results.json` are the ones the earlier analyses used.

## Files

- `monopole_ranking.py` — analysis script
- `monopole_ranking_results.json` — all fits, BICs, jackknives,
  periodogram top-3, dipole ecliptic latitudes
- inputs unchanged: `nanograv_binned.npz`, `aldm_real_results.json`
