# EVPA transient search — X4227 (3rd EB, ALMA 2017-04-07)

Companion to `transient_search_firstlook.md` (which covered X4947 + X448f,
64 min, NULL). This note extends the **identical** search to the newly
reduced third execution block. Search-only; the reduction pipeline and other
EBs were not touched.

**Data:** SGRA2017_X4227_IQUV.npz (uid://A002/Xbec3cb/X4227), 532 integrations,
2017-04-07 07:09-08:20 UT; 4.0 s cadence, 4 SPWs 213.1/215.1/227.1/229.1 GHz.
Read-only input.
**Usable contiguous coverage:** 39.5 min in 5 segments (gaps >20 s split;
5 integrations masked with median I<1 Jy).

**Method:** identical to the first look — per segment, LS fit of
y(t)=c0+c1*(t-tc)+A*0.5*(1+tanh((t-t0)/(tau/2))) on band-averaged (inv-var)
EVPA; grid tau=[10,15,22,32,46.9,68,100,120] s, all t0 with t0+/-tau inside
segment. Null: 200 circular shifts + time reversal per segment, same
max-over-grid search. Script: `evpa_transient_search.py` (`analyze_eb` /
`plot_eb`, runner `/tmp/x4227_search.py`).

Segment EVPA noise (deg/sample): seg0 [0.2, 2.9, 4.4, 2.4], seg1 [0.2, 1.4,
0.6, 0.6], seg2 [0.2, 1.2, 0.6, 0.6], seg3 [0.2, 0.7, 1.4, 1.5], seg4
[0.3, 1.0, 1.4, 1.9]. SPW0 (213.1 GHz) is the quiet SPW in every segment
(~0.2 deg/sample); SPW2 (227.1 GHz) is the noisiest in seg0 (~4.4 deg/sample).

## Top candidates (detection grid)

| EB | seg | t0 (UT) | tau (s) | A (deg) | sigma_A | S/N | sign |
|---|---|---|---|---|---|---|---|
| X4227 | 3 | 07.92 | 120 | -4.1 | 0.12 | -35.7 | - |
| X4227 | 3 | 07.92 | 120 | -4.2 | 0.12 | -35.6 | - |
| X4227 | 3 | 07.92 | 120 | -4.1 | 0.12 | -35.3 | - |

(The three rows are the same fitted feature sampled at adjacent t0 grid
points.)

## Achromaticity (per-SPW amplitude fits at candidate t0, tau)

Genuine theta-slip: common amplitude across SPWs (chi2 ~ 3 dof). Faraday
rotation: A proportional to lambda^2 (fit shown for comparison).

- X4227 cand1 (seg3, tau=120s): A_spw=[-4.0, -5.5, -2.5, -5.8] deg,
  sigma_spw=[0.1, 0.5, 1.2, 1.4], common-A chi2=13.9/3dof,
  Faraday(lam^2) chi2=15.1/3dof
- X4227 cand2 (seg3, tau=120s): A_spw=[-4.0, -5.6, -2.4, -5.9] deg,
  sigma_spw=[0.1, 0.5, 1.2, 1.4], common-A chi2=15.1/3dof,
  Faraday(lam^2) chi2=16.3/3dof
- X4227 cand3 (seg3, tau=120s): A_spw=[-4.0, -5.5, -2.6, -5.6] deg,
  sigma_spw=[0.1, 0.5, 1.2, 1.4], common-A chi2=12.6/3dof,
  Faraday(lam^2) chi2=13.8/3dof

The candidate is not achromatic either (common-A chi2 ~13-15/3dof, p~0.003),
but this is moot: it does not clear the null threshold (below).

## Null assessment

- Null max|S/N| over identical grid: 95th pct=42.3, 99th pct=45.6 (n=1005 surrogates).
- Strongest observed candidate: |S/N|=35.7 (below the 95th percentile).
- Verdict: consistent with the null — **no detection**.

## Sensitivity / upper bound (X4227 alone)

- Median amplitude uncertainty at tau=46.9 s: sigma_A=0.19 deg.
- Approx. 95%-detection amplitude at tau=46.9 s: A_95 ~= 42.3 x 0.19 = 8 deg.
- A 55.6-deg slip at tau~47 s would have S/N ~ 293, ABOVE the 99th-percentile
  null threshold (45.6) — i.e. such slips are EXCLUDED at >>99% per-epoch in
  X4227 if they occurred during coverage.

## Single-sample jump check (unresolved-step cross-check)

Largest |dEVPA| between adjacent 4-s samples within contiguous data:
- 39.6 deg at sample 17 (07.18 UT, seg0), SPW2-dominated: per-SPW jumps
  [0.0, 1.0, 39.6, 14.7] deg. The next sample (18) jumps back 39.2 deg
  ([0.1, 0.7, 39.2, 14.0]) — a single-sample excursion in SPW2, not a step.
  Polarized flux at the sample: [0.162, 0.176, 0.088, 0.122] Jy (SPW2 lowest).
  VETOED: not common-mode across SPWs (SPW0/SPW1 show ~0-1 deg), occurs in the
  noisiest SPW of the segment (~4.4 deg/sample), returns the following sample.
  Single-SPW outlier spike, not an achromatic step.
- Next largest: 12.9 deg (sample 54, SPW1-only), 11.9 deg (sample 44,
  SPW1-only), 10.1 deg (sample 82, SPW3-only) — all single-SPW, all well below
  55.6 deg.
- No single-sample event near 55.6 deg in X4227.

## Combined statement (X4947 + X448f + X4227, 3 of 8 EBs)

- Usable contiguous coverage: 64 + 39.5 = **~104 min** (14 segments).
- Per-EB nulls: X4947/X448f combined 95th=40.7, 99th=43.1 (n=1809);
  X4227 95th=42.3, 99th=45.6 (n=1005). Strongest candidates: |S/N|=25.3
  (first look), 35.7 (X4227) — both below their 95th-percentile nulls.
- **Combined verdict: no tanh transient with |A| > ~6-8 deg and tau in
  [10,120] s detected in ~104 min of usable 4-s ALMA Sgr A* polarimetry.
  55.6-deg slips at tau~47 s would appear at S/N ~290-380, far above the
  99th-percentile null thresholds (43-46) — such slips are EXCLUDED at >>99%
  per-epoch in all three EBs if they occurred during coverage.**
- This is a per-epoch bound, not a global rate limit for Sgr A* (that would
  require the observation duration plus an event-process model). Searched
  morphology is tanh only, tau 10-120 s; unresolved steps (tau << 4 s) are
  covered only by the single-sample jump check above and in the first look.

## Caveats

- Now 3 of 8 execution blocks (~37% of the 2017-04-07 data); the remaining
  04-07 EBs and 2017-04-06/11 are not yet searched.
- Same caveats as the first look: band-averaged detection downweights (not
  removes) the noisiest SPW; surrogate null assumes stationary noise within a
  segment with slow drifts absorbed by the linear baseline; one large
  single-sample jump (39.6 deg, SPW2-only spike) was vetted and vetoed as
  single-SPW noise, not an achromatic step.

## Plots

- `SGRA2017_X4227_track.png`: EVPA track + polarized flux
- `SGRA2017_X4227_candidates.png`: top-3 candidate waterfalls (per-SPW data + tanh model)
- `SGRA2017_X4227_null.png`: null histogram
