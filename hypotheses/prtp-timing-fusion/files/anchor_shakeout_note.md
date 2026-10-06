# Anchor-pulsar shake-out — tech note
2026-09-24. Same diagnostic as the J1909 achromaticity test: published
NANOGrav 15-yr PINT par + TOAs, post-fit residuals (no refit; DMX included),
split by frontend flag, 60-day bins per band. Archival-data analysis.

## B1937+21 — the wander is intrinsic, achromatic, enormous
| band | TOAs | bins | rms | ptp | quad-drift ptp |
|---|---|---|---|---|---|
| 800 MHz | 7,726 | 84 | 6,088 ns | 17,601 ns | 20,983 ns |
| 1.4 GHz | 12,702 | 86 | 5,939 ns | 17,394 ns | 20,877 ns |
| S-band | 2,595 | 59 | 5,870 ns | 17,406 ns | 20,150 ns |

Cross-band correlations (92 common bins): 800×1400 = 0.9989,
800×S = 0.9983, 1400×S = 0.9993. The ~21 µs quadratic drift is IDENTICAL
at three widely separated frequencies. Post-DMX rules out interstellar
dispersion; achromaticity rules out receiver/backend effects (ISM would be
strongly chromatic: DM ∝ ν⁻², scattering ∝ ν⁻⁴).
**Verdict: genuine intrinsic spin noise, ~21 µs peak-to-peak over 15 yr.**
The 10× chain underprediction is real unmodeled physics, not an artifact.
B1937 is the pulsar most in need of a long-timescale noise component.

## B1855+09 — the "jump episode" dissolves into bad epochs
ASP era (MJD 54800–55600), 30-day bins:
- 1.4 GHz: baseline +1500–3000 ns with isolated single-bin spikes to
  +5666 ns (MJD 55195, n=8), +5831 ns (MJD 55525, n=8), +3022 (n=4), +4020 (n=8)
- 430 MHz: smooth +2300–3200 ns through the same window, no spikes

Three strikes against a physical/ISM origin:
1. Wrong frequency scaling — a DM/ISM event would be ~10× BIGGER at 430 MHz
   ((1400/430)²); it is smaller there.
2. Not achromatic — a backend clock jump would shift all bands equally.
3. Incoherent within the epoch — spike bins show 5–9 µs intra-epoch scatter
   (e.g. −943…+8064 ns in one 8-TOA bin). A real jump shifts TOAs coherently;
   this is scattered, noisy data: RFI-contaminated or mis-calibrated
   L-band ASP observations.
Cross-band correlation is only 0.58 (vs 0.999 for B1937) — the bands share
some slow structure but the spikes are L-band-only garbage.
**Verdict: data-quality issue in early L-band ASP epochs, not a physical
signal.** Those epochs should have been cut; B1855's 5× "underprediction" is
partly outlier-driven. Underlying red noise is otherwise smooth.

## J0437-4715 — quiet
1.5 GHz: 9 bins, rms 284 ns, ptp 993 ns. 3 GHz: 13 bins, rms 132 ns,
ptp 462 ns. Cross-band correlation −0.36 (uncorrelated — no shared wander).
**Verdict: no anomaly.** Its chain noise model is roughly adequate; nothing
to chase here.

## Shake-out summary
| pulsar | verdict | nature |
|---|---|---|
| J1909-3744 | intrinsic quasi-periodic wobble, 8.8 yr, ~330–420 ns, achromatic | real spin noise |
| B1937+21 | intrinsic drift, ~21 µs ptp, achromatic (r=0.999) | real spin noise, huge |
| B1855+09 | ASP-era spikes = bad L-band epochs (incoherent, wrong ν scaling) | data quality |
| J0437-4715 | no coherent wander | clean |

Implications for the variance discrepancy profile: two pulsars carry genuine,
huge, unmodeled intrinsic red components (J1909's wobble, B1937's drift);
B1855's apparent excess is inflated by bad early epochs; J0437 is fine.
Timing-chain calibration needs (a) explicit long-timescale intrinsic
components, not just power-law red noise, and (b) robust outlier rejection
for early-backend epochs. Any spatial/stochastic fit that trusts the chains
as-is will keep hallucinating.

## Files
- `anchor_shakeout.py`, `anchor_shakeout.json` (per-band series, correlations)
