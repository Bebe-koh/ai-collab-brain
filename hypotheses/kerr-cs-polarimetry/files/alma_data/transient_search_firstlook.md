# EVPA transient search — first look (2 of 8 EBs, ALMA 2017-04-07)

**Data:** SGRA2017_X4947_IQUV.npz (432 int, 11:08-11:55 UT) + SGRA2017_X448f_IQUV.npz (428 int, 08:36-09:22 UT); 4.0 s cadence, 4 SPWs 213.1/215.1/227.1/229.1 GHz. Read-only inputs.
**Usable contiguous coverage:** 64 min in 9 segments (gaps >20 s split; 3 integrations masked with median I<1 Jy in X4947).

**Method:** per segment, LS fit of y(t)=c0+c1*(t-tc)+A*0.5*(1+tanh((t-t0)/(tau/2))) on band-averaged (inv-var) EVPA; grid tau=[10,15,22,32,46.9,68,100,120] s, all t0 with t0+/-tau inside segment. Null: 200 circular shifts + time reversal per segment, same max-over-grid search.

## Top candidates (detection grid)

| EB | seg | t0 (UT) | tau (s) | A (deg) | sigma_A | S/N | sign |
|---|---|---|---|---|---|---|---|
| X4947 | 2 | 11.41 | 120 | +3.0 | 0.1 | +25.3 | + |
| X4947 | 2 | 11.41 | 120 | +3.1 | 0.1 | +25.3 | + |
| X4947 | 2 | 11.41 | 120 | +3.0 | 0.1 | +25.2 | + |
| X448f | 0 | 08.72 | 120 | -2.1 | 0.1 | -16.9 | - |
| X448f | 0 | 08.72 | 120 | -2.1 | 0.1 | -16.6 | - |
| X448f | 0 | 08.72 | 120 | -2.1 | 0.1 | -16.4 | - |

## Achromaticity (per-SPW amplitude fits at candidate t0, tau)

Genuine theta-slip: common amplitude across SPWs (chi2 ~ 3 dof). Faraday rotation: A proportional to lambda^2 (fit shown for comparison).

- X4947 cand1 (seg2, tau=120s): A_spw=[+3.2, +1.5, +4.7, +0.4] deg, sigma_spw=[0.1, 0.5, 0.4, 0.4], common-A chi2=74.1/3dof, Faraday(lam^2) chi2=67.3/3dof
- X4947 cand2 (seg2, tau=120s): A_spw=[+3.2, +1.5, +4.7, +0.5] deg, sigma_spw=[0.1, 0.5, 0.4, 0.4], common-A chi2=72.1/3dof, Faraday(lam^2) chi2=65.7/3dof
- X4947 cand3 (seg2, tau=120s): A_spw=[+3.2, +1.6, +4.7, +0.3] deg, sigma_spw=[0.1, 0.5, 0.4, 0.4], common-A chi2=76.0/3dof, Faraday(lam^2) chi2=68.7/3dof
- X448f cand1 (seg0, tau=120s): A_spw=[-1.9, -3.6, +5.1, -3.1] deg, sigma_spw=[0.1, 0.5, 2.4, 1.6], common-A chi2=21.0/3dof, Faraday(lam^2) chi2=21.2/3dof
- X448f cand2 (seg0, tau=120s): A_spw=[-1.8, -3.6, +5.1, -3.3] deg, sigma_spw=[0.1, 0.5, 2.5, 1.6], common-A chi2=20.8/3dof, Faraday(lam^2) chi2=21.1/3dof
- X448f cand3 (seg0, tau=120s): A_spw=[-1.8, -3.6, +5.1, -3.4] deg, sigma_spw=[0.1, 0.5, 2.5, 1.6], common-A chi2=20.7/3dof, Faraday(lam^2) chi2=21.0/3dof

## Null assessment

- Null max|S/N| over identical grid: 95th pct=40.7, 99th pct=43.1 (n=1809 surrogates).
- Strongest observed candidate: |S/N|=25.3.
- Verdict: consistent with the null — **no detection**.

## Sensitivity / upper bound

- Median amplitude uncertainty at tau=46.9 s: sigma_A=0.1 deg.
- Approx. 95%-detection amplitude at tau=46.9 s: A_95 ~= 40.7 x 0.1 = 6 deg.
- **Upper bound (first look):** no tanh transients with |A| > ~6 deg and tau in [10,120] s detected in 64 min of usable 4-s ALMA Sgr A* polarimetry. A 55.6-deg slip at tau~47 s would have S/N ~ 383, ABOVE the 99th-percentile null threshold — i.e. such slips are EXCLUDED at >>99% per-epoch in these two EBs if they occurred during coverage.

## Single-sample jump check (unresolved-step cross-check)

Largest |dEVPA| between adjacent 4-s samples within contiguous data:
- X4947: 75.5 deg (sample 430, SPW1 215.1 GHz) and 47.3 deg (sample 267, SPW3
  229.1 GHz). Both vetoed: the 75.5-deg event is the final integration of the
  EB with per-SPW jumps [3.6, 75.5, 61.5, 4.3] deg (not common-mode) at
  polarized flux 0.013-0.035 Jy (~1%, EVPA noise-dominated); the 47.3-deg
  event is SPW3-only ([0.2, 3.3, 4.1, 47.3] deg) at 0.034 Jy polarized flux
  with erratic neighbors — single-SPW low-S/N EVPA noise, not an achromatic
  step. A genuine theta-slip must be identical in all 4 SPWs.
- X448f: 11.3 deg maximum — no single-sample event near 55.6 deg.

## Caveats

- First look: 2 of 8 execution blocks (~25% of the 2017-04-07 data); the 2017-04-06/11 EBs and the remaining 04-07 EBs are not yet reduced.
- Band-averaged detection weights SPWs by measured EVPA noise; one SPW per EB is noisier (X4947 SPW1-3 ~10 deg/sample, X448f SPW0 ~8 deg/sample vs ~2 deg typical) — downweighted, not removed.
- A 55.6-deg *unresolved* step (tau << 4 s) would appear as a single-sample jump, not a tanh; this search targets resolved ramps 10-120 s.
- Surrogate null assumes stationary noise within a segment; slow drifts are absorbed by the linear baseline in the fit.
- Two large single-sample EVPA jumps in X4947 (75.5 deg, 47.3 deg) were individually vetted and rejected as single-SPW low-polarized-flux noise / edge artifact (see section above) — neither is achromatic.

## Plots

- `SGRA2017_X4947_track.png`, `SGRA2017_X448f_track.png`: EVPA track + polarized flux
- `SGRA2017_X4947_candidates.png`, `SGRA2017_X448f_candidates.png`: top-3 candidate waterfalls (per-SPW data + tanh model)
- `SGRA2017_X4947_null.png`, `SGRA2017_X448f_null.png`: null histograms
