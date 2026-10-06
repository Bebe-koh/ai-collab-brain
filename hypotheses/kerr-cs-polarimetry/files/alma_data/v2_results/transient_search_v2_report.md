# EVPA transient search v2 — 3 of 8 EBs, ALMA 2017-04-07 (3 EBs)

**Implementation:** `evpa_transient_search_v2.py`. Repairs vs v1: temporal unwrapping (axis=0); residual-based surrogates (baseline fit + shifted residuals); campaign-level null (max over grid x segments per EB, n=1000 campaigns); injection-recovery calibration; enforced achromaticity veto (per-SPW S/N coincidence + dilution-ratio test).

## SGRA2017_X4947
- Integrations: 429 in 5 segments; 4-s cadence; SPWs 213.1, 215.1, 227.1, 229.1 GHz.
- Campaign null (residual-shift): 95th=26.3, 99th=26.6.
- Observed campaign max |S/N|=25.3 (below null 99th).
- Top candidates (veto applied):
  - seg2 t0+16.4min tau=120s A=+3.0 S/N=+25.3 veto=FAIL (chi2/3=24.7, Faraday chi2/3=22.4)
  - seg3 t0+29.5min tau=100s A=+4.5 S/N=+14.8 veto=FAIL (chi2/3=12.3, Faraday chi2/3=11.2)
  - seg0 t0+1.9min tau=47s A=+0.7 S/N=+8.8 veto=PASS (chi2/3=0.7, Faraday chi2/3=0.8)
- Injection-recovery P(detect) vs amplitude (full pipeline):
  - tau=10s: A_90=19.7 deg, A_99=30.0 deg, P(detect 55.6 deg)=1.000
  - tau=47s: A_90=19.6 deg, A_99=30.0 deg, P(detect 55.6 deg)=1.000
  - tau=120s: A_90=28.0 deg, A_99=49.2 deg, P(detect 55.6 deg)=1.000
- Single-SPW-jump control: 20deg: det=0.16, veto-pass=0.00, 40deg: det=0.28, veto-pass=0.00, 80deg: det=0.36, veto-pass=0.00
- True-signal dilution ratio max|A_spw|/|A_bar|: median 1.16, max 1.99 (veto passes <= 2.0; single-SPW artifacts score ~4)

## SGRA2017_X448f
- Integrations: 424 in 4 segments; 4-s cadence; SPWs 213.1, 215.1, 227.1, 229.1 GHz.
- Campaign null (residual-shift): 95th=19.0, 99th=20.2.
- Observed campaign max |S/N|=16.9 (below null 99th).
- Top candidates (veto applied):
  - seg0 t0+7.3min tau=120s A=-2.1 S/N=-16.9 veto=FAIL (chi2/3=7.0, Faraday chi2/3=7.1)
  - seg1 t0+14.9min tau=120s A=+2.4 S/N=+14.5 veto=FAIL (chi2/3=11.3, Faraday chi2/3=11.0)
  - seg3 t0+45.7min tau=32s A=+0.7 S/N=+13.8 veto=FAIL (chi2/3=5.0, Faraday chi2/3=4.9)
- Injection-recovery P(detect) vs amplitude (full pipeline):
  - tau=10s: A_90=6.7 deg, A_99=10.0 deg, P(detect 55.6 deg)=1.000
  - tau=47s: A_90=6.9 deg, A_99=11.0 deg, P(detect 55.6 deg)=1.000
  - tau=120s: A_90=9.8 deg, A_99=12.0 deg, P(detect 55.6 deg)=1.000
- Single-SPW-jump control: 20deg: det=0.60, veto-pass=0.00, 40deg: det=0.56, veto-pass=0.00, 80deg: det=0.88, veto-pass=0.00
- True-signal dilution ratio max|A_spw|/|A_bar|: median 1.08, max 1.98 (veto passes <= 2.0; single-SPW artifacts score ~4)

## SGRA2017_X4227
- Integrations: 527 in 5 segments; 4-s cadence; SPWs 213.1, 215.1, 227.1, 229.1 GHz.
- Campaign null (residual-shift): 95th=35.6, 99th=37.5.
- Observed campaign max |S/N|=35.7 (below null 99th).
- Top candidates (veto applied):
  - seg3 t0+46.1min tau=120s A=-4.1 S/N=-35.7 veto=PASS (chi2/3=4.6, Faraday chi2/3=5.0)
  - seg2 t0+25.0min tau=68s A=+1.4 S/N=+25.0 veto=FAIL (chi2/3=106.2, Faraday chi2/3=106.7)
  - seg0 t0+5.4min tau=68s A=-1.2 S/N=-17.4 veto=FAIL (chi2/3=2.0, Faraday chi2/3=2.1)
- Injection-recovery P(detect) vs amplitude (full pipeline):
  - tau=10s: A_90=11.4 deg, A_99=18.4 deg, P(detect 55.6 deg)=1.000
  - tau=47s: A_90=11.5 deg, A_99=18.9 deg, P(detect 55.6 deg)=1.000
  - tau=120s: A_90=11.7 deg, A_99=18.9 deg, P(detect 55.6 deg)=1.000
- Single-SPW-jump control: 20deg: det=0.32, veto-pass=0.08, 40deg: det=0.24, veto-pass=0.04, 80deg: det=0.32, veto-pass=0.00
- True-signal dilution ratio max|A_spw|/|A_bar|: median 1.10, max 1.89 (veto passes <= 2.0; single-SPW artifacts score ~4)

## Single-sample jump scan (unresolved tau << 4 s)
- SGRA2017_X4947:
  - seg span 172s: strongest jump dy=-0.3 deg (z=3.3, robust sig=0.10); per-SPW steps=[-0.3, +0.5, -0.5, -0.7]
  - seg span 158s: strongest jump dy=+0.3 deg (z=3.9, robust sig=0.08); per-SPW steps=[+0.1, +1.8, -0.1, +0.6]
  - seg span 612s: strongest jump dy=-1.2 deg (z=6.2, robust sig=0.18); per-SPW steps=[-1.5, -1.2, +1.0, +0.0]
  - seg span 426s: strongest jump dy=-1.5 deg (z=2.7, robust sig=0.54); per-SPW steps=[-1.8, -2.3, +7.4, +6.5]
  - seg span 554s: strongest jump dy=-8.2 deg (z=4.5, robust sig=1.80); per-SPW steps=[-3.6, -75.5, -61.5, +4.3]
- SGRA2017_X448f:
  - seg span 554s: strongest jump dy=+0.7 deg (z=3.1, robust sig=0.22); per-SPW steps=[+0.6, +1.1, -3.4, +3.0]
  - seg span 426s: strongest jump dy=+0.7 deg (z=4.0, robust sig=0.17); per-SPW steps=[+0.9, +0.4, -2.0, +0.9]
  - seg span 372s: strongest jump dy=+0.2 deg (z=2.2, robust sig=0.10); per-SPW steps=[+0.1, +0.3, +0.3, +0.2]
  - seg span 554s: strongest jump dy=-0.3 deg (z=2.6, robust sig=0.12); per-SPW steps=[-0.3, -1.5, -0.2, -0.2]
- SGRA2017_X4227:
  - seg span 408s: strongest jump dy=+0.6 deg (z=2.7, robust sig=0.21); per-SPW steps=[+0.5, +11.9, -1.3, +1.7]
  - seg span 208s: strongest jump dy=+1.0 deg (z=7.6, robust sig=0.14); per-SPW steps=[+1.5, -1.3, +0.1, -0.3]
  - seg span 517s: strongest jump dy=+0.4 deg (z=3.4, robust sig=0.12); per-SPW steps=[+0.4, +3.3, -0.6, +1.0]
  - seg span 736s: strongest jump dy=-0.5 deg (z=2.9, robust sig=0.18); per-SPW steps=[-0.2, -4.0, -0.8, +0.7]
  - seg span 499s: strongest jump dy=+2.6 deg (z=14.9, robust sig=0.17); per-SPW steps=[+2.7, +2.7, -1.0, +1.3]

## Caveats
- Surrogate null is conservative: any real coherent transient in the data also enters the residuals and inflates the null.
- Temporal unwrapping assumes no true >90-deg jump within one 4-s sample; unresolved steps are covered only by the jump scan above.
- Exclusion applies to resolved tanh ramps with tau in [10,120] s occurring inside analyzed segments.
- v1 claims (null percentiles ~40-46, 'excluded at >>99%' from predicted S/N) are SUPERSEDED by this v2 calibration.

## Reproducibility re-run (2026-10-06)

An independent audit (Grok) found the committed code defaulted to
N_CAMP=500 and trials=25 while this report described 1000 campaigns and
100 trials, with no run log of the original invocation. The code was
corrected (N_CAMP=1000, trials=100, X4227 added to the default file list;
values only, no structural changes) and the full analysis re-run on all
three EBs with fixed seeds (1000 campaigns, 100-trial injections).
Exact command and environment are logged in `v2_results/RUN_LOG.md`;
full comparison in `v2_results/rerun_reconciliation_2026-10-06.md`.

Result: null95/null99, observed campaign maxima, and the 100/100
detection fractions at 55.6 deg / tau=46.9 s reproduce exactly. A90/A99
above are the regenerated values (Monte-Carlo noise from 25->100 trials
moved them 1-4 deg; all remain inside the ranges quoted in the summary).
