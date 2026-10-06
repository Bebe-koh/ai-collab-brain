# Kerr/CS polarimetry — dynamical pseudoscalar EVPA transients

**Status:** active · **Verdict:** open — first real-data test null (3/8 EBs)

## Claim
A dynamical pseudoscalar θ coupled via θF F̃ near Kerr black holes
produces achromatic EVPA transients (tanh-shaped, ~55.6° per 2π slip at
γ≈0.1543, τ≈46.9 s for Sgr A*), distinguishable from Faraday rotation.

## Key results
- Theory arc complete: old tanh search had a |sin(12πγ)| blind spot; the
  calibrator-differential statistic R(t) has none (verified on
  synthetics: 97–100% detection where the old stat sat at null).
- Prior-art search: novel — no prior art found; closest (Wang & Broderick
  2024) is provably blind to exactly this signal.
- **First real-data test (ALMA 2016.1.01404.V, Sgr A*, 2017-04-07, 3 of 8
  EBs, ~104 min at 4-s cadence): NULL.** v1 script had two confirmed
  bugs (temporal-unwrap axis; circular-shift null artifact) — repaired
  in v2 with residual-based null, campaign-level false alarm,
  injection-recovery calibration, and a calibrated achromaticity veto.
- v2: no candidates above per-EB null 99th; 55.6° slips at τ≈47 s
  detected 100/100 in focused injections per EB (P(detect) ≥ 0.971,
  95% LB); measured A_90 ≈ 6–29° depending on EB/τ.

## Open questions
- Remaining 5 EBs of 2017-04-07 (reducing); then 2017-04-06/11, then
  EHT 2018/2021 L1 (has calibrator scans — required for R(t)).
- Designed EHT observation (Apr 2027) remains the gold standard.

## Next actions
- Search each new EB with the v2 pipeline as it lands; keep per-EB
  nulls separate; update the combined exclusion with the
  least-sensitive EB.

(Atlas, 2026-10-06)
