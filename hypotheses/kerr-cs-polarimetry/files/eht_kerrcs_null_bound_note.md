# Kerr/CS Public-EHT Null/Bound Experiment — Technical Note
**Date:** 2026-09-25  
**Status:** Null result. No detection. 95% CL bound NOT achieved (systematic background).  
**Data:** Public EHT Sgr A* polarimetric UVFITS (Apr 6/7 2017, HOPS, high+low band, 10-s).  
**Code:** `~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/`

## Headline
We searched public EHT Sgr A* closure-phase data for the Kerr/CS-predicted global
EVPA phase-slip (tanh step, τ=46.9 s, RL triangle response −6Δχ, LR +6Δχ).
**No signal found.** Differenced search: Apr 6 p=0.47, Apr 7 p=0.10 (2,000
surrogates, look-elsewhere corrected). Undifferenced: Apr 6 p=0.80, Apr 7 p=0.56.
**This is a null, not a detection.**

**Bound:** A 95% CL exclusion on γ is **not achieved**. Injection calibration shows
that even maximal-amplitude slips (|sin(12πγ)|≈1) exceed the 95th-percentile
systematic background in only ~60% of trials (Apr 7) and ~10–20% (Apr 6).
The limiting factor is step-like systematics in slip-invariant veto channels
(SUM Z≤10.1, RR Z≤11.4, LL Z≤11.1), which coincide with the diff-channel maxima.
We report sensitivity (efficiency curves) but **no 95% CL γ upper bound**.

**Exact blockers for a full instrumental bound:**
1. **Calibrator scans missing.** The Sgr A* release contains target-only UVFITS
   (README confirms: "Only Sgr A* high/low target data for April 6/7 are released").
   The synchronized all-station R–L phase jump is exactly degenerate with a global
   slip and **cannot be bounded** without calibrator scans. Any γ result is
   conditional on no synchronized R–L jump.
2. **Systematic background.** Slip-invariant channels show step-like features
   comparable to the search channel, precluding 95% detection efficiency.
3. **R/L gains assume V=0.** The release calibrates R/L gains assuming intrinsic
   Stokes V=0; a real circular component would leak into the observable.
4. **Weight convention unverified.** UVFITS weights converted to phase variance
   via Var(φ)≈0.5/(|V|²·weight) (high-S/N approx); not verified against EHT docs.

## Theory Locked (verified 2026-09-24/25)
- RL → RL·exp(−2iΔχ), LR → LR·exp(+2iΔχ) per baseline.
- Δχ(t) = 2πγk·0.5·[1+tanh((t−t0)/τ)], k=1, τ=46.9 s (Sgr A*), 18.0 h (M87*).
- RL triangle closure response: −6Δχ. LR: +6Δχ.
- At γ=0.15, Δχmax=54° (not 27°). Prior γ labels were 2× optimistic.
- **Fundamental periodicity:** The observable is a phase (mod 2π). The permanent
  offset is |1−exp(−24iπγ)| = 2|sin(12πγ)|. The experiment is **blind at
  γ=k/12** (k integer) and measures |sin(12πγ)|, not γ directly. For small γ,
  |sin(12πγ)|≈12πγ.

## Data
- 26 UVFITS downloaded from CyVerse (EHTC_FirstSgrAPol_Mar2024, EHTC_M87pol2017_Nov2023).
- Primary: Sgr A* HOPS Apr 6/7, hi+lo, 10-s, D-term calibrated.
  - Apr 6 hi: 9,304 groups, 1,099 timestamps, 6.15 h span, 10.00 s median cadence.
  - 15 baselines, 20 unique triangles (Apr 6), 26 (Apr 7).
  - Median per-visibility S/N: RL≈2.0 (39% >3), RR≈4.2 (59% >3).
- STOKES axis: RR, LL, RL, LR (verified from CRVAL3/CDELT3).

## Pipeline (corrected)
**Critical fix applied:** Baseline reversal for cross-hands now swaps products
(reversed RL uses conjugated LR; reversed LR uses conjugated RL). RR/LL use
same-product conjugation. Verified with synthetic directed-baseline identities.

Per day, per band:
1. Load UVFITS → per-baseline visibilities (RR, LL, RL, LR).
2. Form directed triangle closures (20–26 triangles).
3. Stack: inverse-variance weighted mean of triangle phasors, with per-triangle
   circular-mean derotation (removes static source phase; |·| makes Z invariant).
4. **Differenced (primary):** e(t)=d(t+1)·conj[d(t)], mask gaps >15 s.
   Observable: D(t)=S^RL·conj[S^LR] (slip adds: −6Δχ−(+6Δχ)=−12Δχ).
5. **Undifferenced (cross-check):** d(t) directly.
6. Matched-filter bank: tanh-step templates at γ∈{0.15,0.3,0.6}, t0 grid 20 s.
   Z = |Σ e·conj(v)| / √(Σ|v|²/2) (complex, phase-invariant).
7. Null: 2,000 circular-shift surrogates (common roll hi+lo), look-elsewhere p.

**Veto channels:** SUM=S^RL·S^LR (slip cancels: −6Δχ+6Δχ=0; station R–L cancels),
RR, LL (slip-invariant). Any slip candidate must be absent in all three.

## Null Results
### Differenced (primary)
| Day | Obs max Z | Null mean | Null 95th | p (look-elsewhere) |
|-----|-----------|-----------|-----------|-------------------|
| Apr 6 | 3.24 | 3.25±0.05 | 3.34 | 0.4725 |
| Apr 7 | 3.48 | 3.30±0.14 | 3.54 | 0.0985 |

### Undifferenced (cross-check)
| Day | Obs max Z | Null mean | Null 95th | p |
|-----|-----------|-----------|-----------|---|
| Apr 6 | 7.71 | 9.07 | 11.85 | 0.7965 |
| Apr 7 | 6.67 | 6.82 | 7.86 | 0.5570 |

**No evidence for a slip. Null, not detection.**

## Veto Results (undifferenced, per-band max Z)
| Data | DIFF | SUM | RR | LL |
|------|------|-----|----|----|
| Apr 6 hi | 6.89 | 6.49 | 5.03 | 4.45 |
| Apr 6 lo | 8.86 | 9.66 | 4.38 | 4.59 |
| Apr 7 hi | 7.06 | 5.22 | 7.70 | 7.41 |
| Apr 7 lo | 7.45 | 10.10 | 11.40 | 11.05 |

**Smoking gun:** Apr 7 lo diff max (Z=7.45 at t0=9761 s) coincides with
SUM=9.90, RR=9.53, LL=9.87 at the same t0. The diff "candidate" is a systematic.
Veto channels show step-like activity comparable to the search channel,
confirming the background is systematics-dominated.

## Injection Calibration (undifferenced)
Verified slip injected at baseline-visibility level
(RL·exp(−2iχ), LR·exp(+2iχ)), 30 trials per γ, t0 random. Efficiency = fraction
with recovered Z (in ±3τ window) exceeding threshold.

T95 (null 95th): Apr 6=11.85, Apr 7=7.86. Tobs: Apr 6=7.71, Apr 7=6.67.

Apr 7 efficiency vs T95 (amp=|sin(12πγ)|):
- γ=0.06 (amp 0.77): 0.83
- γ=0.12 (amp 0.98): 0.63
- γ=0.21 (amp 1.00): 0.63
- γ=0.30 (amp 0.95): 0.60
- γ=0.39 (amp 0.84): 0.77

Apr 6 efficiency vs T95: 0.00–0.27 (T95=11.85 too high; systematics worse).

**Even at maximal amplitude, efficiency does not reach 95%.**
The systematic background precludes a 95% CL bound.

## M87* Assessment
M87 Apr 5 HOPS: span=7.40 h, τ=18 h → span/τ=0.41. The tanh step is not resolved;
the signal would be a slow drift (Δχ≈1.24γ rad across track), not a step.
The step matched filter is inapplicable. **M87 cannot set a useful bound with
this method.** (A drift search would be red-noise dominated; not attempted.)

## CASA Pipeline
Not analyzed (HOPS primary). CASA/HOPS comparison is future robustness work;
not counted as independent data.

## Conclusion
- **Null:** No Kerr/CS phase-slip detected in public EHT Sgr A* data.
- **Bound:** 95% CL exclusion on γ **not achieved** due to systematic background.
  Sensitivity characterized via injections; maximal slips detected at ~60%
  efficiency (Apr 7) above 95th-percentile background.
- **Conditional:** Any γ inference is conditional on (i) no synchronized all-station
  R–L jump (unbounded without calibrator scans), (ii) V=0 R/L gain assumption,
  (iii) weight-to-variance convention.
- **Fundamental limit:** Experiment measures |sin(12πγ)|; blind at γ=k/12.

## Files
- Code: `~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/`
  - `load_eht.py` (UVFITS loader, corrected baseline reversal)
  - `pipeline.py` (stacking, Bank, DiffBank)
  - `run_null.py`, `run_null2.py` (null searches)
  - `run_inject.py` (injection calibration)
  - `run_veto.py` (veto channels)
- Data: `~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data/`
- Results: `null_surrogates.json`, `null2_surrogates.json`, `inject_results.json`

## Recommended Next Steps
1. Obtain calibrator scans (or a release including them) to bound the
   synchronized R–L jump degeneracy.
2. Implement veto-cut (exclude t0 with high SUM/RR/LL Z) and re-run; may recover
   95% efficiency.
3. Verify UVFITS weight convention from EHT/AIPS memo.
4. CASA pipeline robustness check.
5. If systematics can be modeled, a joint likelihood may set a proper bound.
