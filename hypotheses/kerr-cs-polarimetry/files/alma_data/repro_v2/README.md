# ALMA EVPA transient search — reproducibility package (v2)

Search for tanh-shaped EVPA transients (classically driven pseudoscalar
phase slips) in ALMA 2016.1.01404.V Sgr A* 2017-04-07 polarimetry, 3 of 8 EBs.

## Contents
- `evpa_transient_search_v2.py` — the repaired implementation (current).
- `evpa_transient_search.py` — the v1 implementation (SUPERSEDED; kept for
  provenance — see the audit findings below).
- `SGRA2017_*_IQUV.npz` — compact per-EB products: mjd, I/Q/U (Jy, 4 SPWs),
  spw_freq_GHz, eb id. No CASA needed.
- `transient_search_v2_report.md` — v2 results.
- `transient_search_firstlook.md`, `transient_search_X4227.md` — v1 notes
  (claims SUPERSEDED by the v2 report).

## Reproduce the v2 result
```bash
python3 evpa_transient_search_v2.py --selftest   # synthetic validation first
python3 evpa_transient_search_v2.py --ncamp 1000 \
  SGRA2017_X4947_IQUV.npz SGRA2017_X448f_IQUV.npz SGRA2017_X4227_IQUV.npz \
  --label "3 of 8 EBs, ALMA 2017-04-07" --report transient_search_v2_report.md
```
Dependencies: Python 3, NumPy, Matplotlib. Runtime ~2 min.

## Why v2 (audit 2026-10-06)
An independent audit of v1 found: (1) `np.unwrap` without `axis=0` unwrapped
across spectral windows instead of time — confirmed and fixed; (2) the
circular-shift null shifted the raw series including baseline drift,
manufacturing template-matching discontinuities (null 99th inflated to
~40-46; v2 residual-shift null gives 20-38) — confirmed on synthetics and
real data, fixed; (3) per-segment null maxima were pooled instead of a
campaign maximum — fixed; (4) ">>99% exclusion" was predicted S/N vs a null
percentile, not measured — replaced by injection-recovery; (5) the
achromaticity check computed statistics but enforced no threshold —
replaced by a calibrated coincidence + dilution-ratio veto.
v1's sensitivity claims are superseded. The null verdict (no detections)
survives; the exclusion is now weaker but measured: A_90 ~ 4-29 deg
depending on EB and tau; 55.6-deg slips at tau~47 s detected 100/100 in
focused injections per EB (95% lower bound on P(detect) = 0.971).
