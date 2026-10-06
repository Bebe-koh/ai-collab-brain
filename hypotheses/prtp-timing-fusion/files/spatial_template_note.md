# Monopole vs Hellings-Downs on real NANOGrav residuals — run note

Date: 2026-09-22. Status: **archival-data analysis. Not a GWB detection.
Not an ALDM detection.**

## Question

Do the sharp ±350 ns common-mode swings prefer a spatial quadrupole
(Hellings-Downs, GWB-like) over a global monopole (clock/ALDM-like)?

## Method

Per-epoch Gaussian likelihood on the 14 common 30-day epochs x 4 pulsars:
C_e(A^2) = diag(white+red)_e + A^2 * T, with T = ones (monopole) or the
normalized HD matrix from the verified spec. Profile likelihood over
A^2 >= 0; joint 2-template grid; drop-one-pulsar jackknife. Diagonal
red noise from NANOGrav chain medians; epochs treated independent.

HD matrix used (J0437, J1909, B1937, B1855):
[[ 1.00 -0.30  0.17  0.13]
 [-0.30  1.00 -0.16  0.03]
 [ 0.17 -0.16  1.00  0.77]
 [ 0.13  0.03  0.77  1.00]]

## Results

1. **Nominal likelihood prefers HD by a landslide**: dlnL vs null =
   4178 (HD) vs 174 (monopole). Taken at face value this looks decisive.

2. **The HD fit is unphysical**: the preferred amplitude runs away --
   still rising at A = 3000 ns with no maximum. A real stochastic
   signal has a well-defined amplitude; an unbounded one means the
   model is absorbing variance it was never meant to explain.

3. **Drop-one-pulsar kills it**: removing B1937+21 collapses the HD
   advantage from ~4000 to 232 and the HD amplitude from runaway to
   423 ns. Removing any other pulsar leaves HD winning by ~2700-4000.
   The entire HD preference lives in one pulsar.

4. **Why**: B1937+21's empirical binned scatter is 3502 ns vs 301 ns
   predicted by the chain-based red model -- the noise model
   underestimates it ~12x (B1855+09: 609 vs 107 ns, ~6x). B1937xB1855
   correlate at 0.92-0.94 (robust to dropping hot epochs). The HD
   template's maximum (0.77) sits exactly on that pair, so the HD
   model soaks up the unexplained correlated wander of the two
   noisiest pulsars and calls it a gravitational-wave background.

5. **The monopole is the robust signal**: A = 181-221 ns, dlnL 174-285,
   stable across all drop-one tests. The ±350 ns common swings are a
   genuine array-wide monopole; only its *source* (clock, ephemeris,
   ALDM, systematics) remains open.

## Interpretation

The ±350 ns swings do **not** prefer a quadrupole. The HD likelihood
win is model misspecification: unexplained correlated variance in
B1937+21/B1855+09 aligning with the HD template peak by geometry luck.
A 3000+ ns HD-correlated component would also be wildly inconsistent
with published NANOGrav GWB levels (tens of ns), an independent red flag.

The unexplained B1937xB1855 correlation (0.94) is itself interesting
and not explained here -- candidates include shared backend/telescope
systematics or processing commonalities, not investigated.

## Caveats

- N = 14 clustered epochs; diagonal red; epochs independent.
- 4 pulsars / 6 pairs: weak spatial leverage by construction.
- The monopole excess (chi2 = 406/14) stands, but its source is
  unidentified. Nothing here is a detection of anything.

## Files

- `spatial_template_results.json` -- first-pass grids (note: joint grid
  hit its 500 ns edge; superseded by diagnostics below, kept for record)
- `../..` (scratch): /tmp/aldm/spatial_templates.py, spatial_robust.py
- inputs: `nanograv_binned.npz`, `nanograv_gls_red.py` (unchanged)
