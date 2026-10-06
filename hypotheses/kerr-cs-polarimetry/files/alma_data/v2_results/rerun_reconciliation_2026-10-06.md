# Reconciliation note — v2 reproducibility re-run, 2026-10-06

## 1. What was wrong and what was changed

Grok's audit found three parameter mismatches between the committed source
(`evpa_transient_search_v2.py`) and the published methodology:

1. `N_CAMP = 500` (line 55) vs "1000 campaigns" in `transient_search_v2_report.md`.
2. `injection_recovery(trials=25)` (line 303; call site did not override) vs
   "100 trials per EB, 100/100 detections" in `v2_audit_repair_note.md`.
3. Default file list omitted X4227 (lines 544–545).

Additionally, no run log recorded the original invocation, so the published
numbers could not be regenerated from the committed code even in principle.

**Fix (values only, no structural changes; md5 of corrected script:
`eb55f47a98d3431dd0bc9a933a7575fb`):**
- `N_CAMP`: 500 → 1000 (flows into `campaign_null`, `analyze_eb`, `--ncamp` default).
- `injection_recovery` default `trials`: 25 → 100.
- Default file list: added `SGRA2017_X4227_IQUV.npz`.
- Docstring: PARAMETER CORRECTION block dated 2026-10-06.

## 2. The re-run

Exact command, parameters, environment, and outputs are logged in
`v2_results/RUN_LOG.md`. Summary: all three EBs, explicit file paths,
n=1000 campaigns (fixed seed 1234), 100-trial injections (fixed seed 7),
83 s wall time, report in `v2_results/rerun_2026-10-06/rerun_report.md`.

## 3. Published vs regenerated — comparison table

Null99 = per-EB campaign-null 99th percentile (the detection threshold).
Obs = observed campaign max |S/N|. P(55.6°) = exact detection fraction for
55.6° tanh at tau=46.9 s through the full pipeline incl. veto
(95% Clopper-Pearson lower bound 0.9705 for 100/100 in all cases).

| EB | quantity | published | regenerated | verdict |
|---|---|---|---|---|
| X4947 | null95 / null99 | 26.3 / 26.6 | 26.3 / 26.6 | REPRODUCED (exact) |
| X4947 | obs camp_max | 25.3 | 25.3 | REPRODUCED (exact) |
| X4947 | A90 (tau=10/47/120 s) | 19.3 / 23.8 / 28.8 | 19.7 / 19.6 / 28.0 | CHANGED (see note) |
| X4947 | A99 (tau=10/47/120 s) | 28.8 / 29.4 / 52.4 | 30.0 / 30.0 / 49.2 | CHANGED (see note) |
| X4947 | P(detect 55.6°) | 1.000 (100/100) | 100/100 | REPRODUCED |
| X448f | null95 / null99 | 19.0 / 20.2 | 19.0 / 20.2 | REPRODUCED (exact) |
| X448f | obs camp_max | 16.9 | 16.9 | REPRODUCED (exact) |
| X448f | A90 (tau=10/47/120 s) | 5.7 / 7.2 / 9.5 | 6.7 / 6.9 / 9.8 | CHANGED (see note) |
| X448f | A99 (tau=10/47/120 s) | 7.8 / 11.0 / 11.8 | 10.0 / 11.0 / 12.0 | CHANGED (see note) |
| X448f | P(detect 55.6°) | 1.000 (100/100) | 100/100 | REPRODUCED |
| X4227 | null95 / null99 | 35.6 / 37.5 | 35.6 / 37.5 | REPRODUCED (exact) |
| X4227 | obs camp_max | 35.7 | 35.7 | REPRODUCED (exact) |
| X4227 | A90 (tau=10/47/120 s) | 11.3 / 11.3 / 11.8 | 11.4 / 11.5 / 11.7 | REPRODUCED (≤0.2°) |
| X4227 | A99 (tau=10/47/120 s) | 18.0 / 19.0 / 19.0 | 18.4 / 18.9 / 18.9 | REPRODUCED (≤0.4°) |
| X4227 | P(detect 55.6°) | 1.000 (100/100) | 100/100 | REPRODUCED |

**Notes on the CHANGED cells:**
- The null percentiles and observed maxima reproduce *exactly* because the
  detection and null use fixed seeds; the exact null match confirms the
  original run was indeed made with ~1000 campaigns (an uncommitted
  override), not 500.
- A90/A99 shift by 1–4° because the injection grid now uses 100 trials
  instead of 25: finer, less noisy P(detect) curves change the linear
  interpolation slightly. This is Monte-Carlo realization noise, not a
  methodology change. All regenerated values stay inside the published
  ranges (X4947: 19.6–28.0 vs 19–29; X448f: 6.7–9.8 vs 6–12;
  X4227: 11.4–11.7 vs 10–12).
- Single-SPW-jump controls reproduce identically; dilution medians change
  only in the second decimal.

**Bottom line:** the headline claims — no detections, null thresholds,
and the 100/100 exclusion of 55.6° slips at tau≈47 s — are confirmed by
the committed code as corrected. Grok's reproducibility defect is closed.

## 4. Diagnostic A — the X4227 veto-passing candidate (|S/N|≈35.7)

From a fresh analysis of the X4227 data (detection path, n_camp=10 for
speed — detection is seed-independent):

- **Location:** segment 3 (735.7 s long), t0 = 46.12 min into the EB,
  tau = 120 s, fitted amplitude A = −4.14°, |S/N| = 35.67.
- **Per-SPW amplitudes (deg):** [−4.01, −5.54, −2.50, −5.78]
  (all same sign, similar magnitude).
- **Per-SPW S/N:** [−33.41, −12.28, −2.13, −4.04] — 3 of 4 exceed |S/N|>3,
  all 4 agree in sign with the band average → coincidence rule satisfied.
- **Dilution ratio** max|A_spw|/|A_bar| = 5.78/4.11 = **1.41 ≤ 2.0** → veto PASSES.
- chi2/3 = 4.6, Faraday chi2/3 = 5.0 (poor fit to a common amplitude or a
  Faraday λ² law — the abandoned chi² vetoes would have failed it; the
  surviving veto is the sign-coincidence + dilution design).

**Interpretation:** a genuine-looking ~4° step at tau=120 s present in all
four bands, in the quietest segment (fitted sigA ≈ 0.12°, hence the huge
S/N despite the small amplitude). It is *below* the campaign null99
(37.5), so it is not a detection — the threshold is set by the noisier
segments. It is exactly the kind of feature the campaign-max calibration
is designed to absorb: achromatic, sub-threshold, and rare. Flagged here
for the record; it warrants a look when the remaining five EBs are
searched (does anything similar recur at tau≈120 s?).

For contrast, the veto correctly rejects X4227 seg2's |S/N|=25.0 feature
(per-SPW A = [+1.35, +8.6, −6.21, +8.87], dilution 6.33 > 2.0 — a
mixed-sign multi-SPW artifact).

## 5. Diagnostic B — linear-baseline surrogate vs quadratic drift

Grok flagged that the surrogate null removes only a linear baseline.
Synthetic test: X4227-seg3-like segment (184 samples, 4-s cadence),
band-average white noise σ=0.5°/sample, drift of 3° across the segment;
case B adds a further ~3° of quadratic curvature. Residual-null
percentiles over 5×300 campaigns:

| drift | null95 | null99 |
|---|---|---|
| linear | 2.57 ± 0.37 | 2.96 ± 0.35 |
| linear + quadratic | 6.10 ± 1.01 | 6.32 ± 1.06 |

**Result:** quadratic curvature of amplitude comparable to the drift
inflates the residual null by **~2.1× at the 99th percentile**. The
mechanism is real: after linear-baseline removal, residual curvature is
partially matched by the tanh template at large tau.

**Caveats:** this is a per-segment effect on a quiet segment; the real
campaign null99 (20–37) is dominated by noisier segments and is an order
of magnitude larger than this inflation. It does not change any verdict,
but it is an unquantified bias direction on real data: if any segment
carries strong curvature, the null is *under*-dispersed there (threshold
too low). Recommendation for the five pending EBs: fit a quadratic
baseline in `baseline_fit` and re-check null percentiles; if they move
<10%, the linear choice stands as documented.

## 6. Doc amendments needed (DRAFTS — not applied; orchestrator to review)

(a) `transient_search_v2_report.md` — update the four injection rows that
changed (X4947 and X448f A90/A99 lines), e.g.:

```
X4947 (was):  tau=47s: A_90=23.8 deg, A_99=29.4 deg
X4947 (now):  tau=47s: A_90=19.6 deg, A_99=30.0 deg
X448f (was):  tau=10s: A_90=5.7 deg,  A_99=7.8 deg
X448f (now):  tau=10s: A_90=6.7 deg,  A_99=10.0 deg
```
(full regenerated values in the table above and in
`v2_results/rerun_2026-10-06/rerun_report.md`).

(b) `v2_audit_repair_note.md` — append a short "Reproducibility re-run
2026-10-06" section recording: the parameter correction (500→1000,
25→100, X4227 added), the exact null99/obs reproduction, the 100/100
confirmation per EB, and the A90/A99 updates.

(c) `hypotheses/kerr-cs-polarimetry/FILES.md` (repo copy) — no change
needed for this fix, but the repo copy of the script and report should be
re-synced to these corrected versions before the next audit wave.

(d) Open follow-up (not a doc change): quadratic-baseline sensitivity
check on the remaining five EBs (see §5).
