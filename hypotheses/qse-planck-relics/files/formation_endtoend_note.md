# QSE formation: full end-to-end calculation — all targets, both channels

Date: 2026-10-06. Code: `formation_endtoend_calc.py` (this calculation),
`endtoend_calc.py` (shared machinery; main-guarded 2026-10-06 — verified
byte-identical output before/after, safe to import). Companion results:
`formation_endtoend_results.npz`.

**Scope:** formation only. Replaces every [EST] formation margin in
`nongaussian_formation_survey.md` (§3 curvaton table, §4 USR table, §7 bottom
line) with rigorous end-to-end numbers. Does NOT touch the conversion side
(evaporation/bounce/fragmentation no-gos). Methodology is the one established
in `marginal_beta_case_note.md` §§1–2; only the extensions are described here.

## 1. Method (extensions beyond the marginal-case note)

- **Targets:** T&L illustrative β=10⁻⁵ (calibration); briefing low-mass end
  β=2×10⁻¹⁹ at M=10⁹ kg; briefing high-mass end β=1.5×10⁻¹² at M=6×10²² kg.
- **Curvaton:** σ₀√r = 1.97·T/erfcinv(2β) (Pi & Sasaki Eq. 28, T = threshold
  multiplier, T=1 their Δ_cr=0.23); floor Ω_GW,0 = 10⁻⁶·(4/81)·(σ₀√r)⁸
  (Eq. 32). Scanned T ∈ {0.87, 1.00, 1.10, 1.20, 1.50, 2.00, 2.61}
  (literature Δ_cr 0.2–0.6; T ∝ Δ_cr). Flip point T_flip = margin(1)^{1/8}.
- **USR:** exact tail integral inverted per (β, ζ_c), ζ_c ∈ {0.5, 0.7, 1.0, 1.3};
  Ω_GW,USR = C·(A_g^tail)², C = 0.822·Ω_r,0 (corrected variance-ratio form).
- **O3 comparison:** 95% bound 5.8×10⁻⁹ (α=0 @25 Hz) AND the PI envelope
  Ω_PI(f) = max_α limit_α·(f/25)^α. For f_* outside the O3 band the PI
  number is reported as formal only; the operative constraint is the
  BBN/CMB integral bound Ω_GW,0·h² ≲ 10⁻⁶ (no direct stochastic bound
  exists at μHz).
- **f_* is fixed by the target mass** (not a free placement): 57.6 Hz for
  M=10⁹ kg (in-band — the binding case), 7.44×10⁻⁶ Hz for M=6×10²² kg.

## 2. Consistency checks (all PASS)

Against `marginal_beta_case_note.md` and the corrected ledger:

| check | got | expected | tol | result |
|---|---|---|---|---|
| curvaton floor @10⁻⁵ | 1.637×10⁻⁹ | 1.64×10⁻⁹ | 3% | PASS |
| curvaton margin @10⁻⁵ | 3.54× | 3.5× | 6% | PASS |
| USR Ω @10⁻⁵, ζ_c=1 | 2.557×10⁻⁹ | 2.56×10⁻⁹ | 4% | PASS |
| USR margin @10⁻⁵, ζ_c=1 | 2.27× | 2.3× | 6% | PASS |
| USR Ω, low-mass end | 1.199×10⁻¹⁰ | 1.20×10⁻¹⁰ | 5% | PASS |
| USR margin, low-mass end | 48.4× | 48× | 6% | PASS |
| USR Ω, high-mass end | 3.244×10⁻¹⁰ | 3.24×10⁻¹⁰ | 5% | PASS |
| USR margin, high-mass end | 17.9× | 18× | 6% | PASS |

The calculation reproduces the marginal-case numbers and the bug-corrected
briefing-target USR verdicts exactly.

## 3. Framework (per target)

| target | β | M (kg) | T_f (GeV) | f_* (Hz) | O3 band? |
|---|---|---|---|---|---|
| T&L illustrative | 10⁻⁵ | 10⁹ | 2.17×10⁹ | 57.6 | yes (binding case) |
| briefing low-mass end | 2×10⁻¹⁹ | 10⁹ | 2.17×10⁹ | 57.6 | yes (binding case) |
| briefing high-mass end | 1.5×10⁻¹² | 6×10²² | 281 | 7.44×10⁻⁶ | no |

## 4. Curvaton results (threshold scan)

Nominal (T=1, P&S threshold Δ_cr=0.23):

| β target | σ₀√r | floor Ω_GW,0 | vs 5.8×10⁻⁹ | vs PI(f_*) | tuning dlnβ/dln(σ₀√r) | σ_ζ² | verdict |
|---|---|---|---|---|---|---|---|
| 10⁻⁵ | 0.6532 | 1.64×10⁻⁹ | 3.5× below | 3.6× below | 18.2 | 0.040 | MARGINAL, threshold-fragile |
| 1.5×10⁻¹² | 0.3993 | 3.19×10⁻¹¹ | 182× below | 182× below (formal) | 48.7 | 0.0057 | SURVIVES, threshold caveat |
| 2×10⁻¹⁹ | 0.3117 | 4.40×10⁻¹² | 1317× below | 1347× below | 79.9 | 0.0021 | SURVIVES, robust |

Validity at all targets: σ_ζ² ≪ 0.1 ✓ (quadratic approx holds);
r=10⁻³ → σ₀ = 9.9–20.7 ≫ 1 ✓. Tuning ≈ Gaussian (79.9/48.7 vs 80/49) —
the erfc structure is identical; NG relocates the amplitude, not the tuning.

Threshold scan (margin vs 5.8×10⁻⁹; EXCLUDED = margin < 1):

| T (Δ_cr≈) | β=10⁻⁵ | β=1.5×10⁻¹² | β=2×10⁻¹⁹ |
|---|---|---|---|
| 0.87 (0.20) | 10.8× | 554× | 4012× |
| 1.00 (0.23) | 3.5× | 182× | 1317× |
| 1.10 (0.25) | 1.7× | 85× | 614× |
| 1.20 (0.28) | 0.8× EXCL | 42× | 306× |
| 1.50 (0.35) | 0.1× EXCL | 7.1× | 51× |
| 2.00 (0.46) | EXCL | 0.7× EXCL | 5.1× |
| 2.61 (0.60) | EXCL | 0.1× EXCL | 0.6× EXCL |

Flip points (margin erased): β=10⁻⁵ at **T=1.17 (+17%)**; β=1.5×10⁻¹² at
**T=1.92 (+92%, Δ_cr≳0.44)**; β=2×10⁻¹⁹ at **T=2.45 (+145%, Δ_cr≳0.56)**.

Reading: the low-mass end is robust across the literature threshold range
(fails only at its extreme upper edge); the high-mass end survives on P&S's
threshold choice but fails in the upper-middle of the literature range —
a genuine caveat, milder than the β=10⁻⁵ fragility.

## 5. USR results (ζ_c scan)

Margins vs 5.8×10⁻⁹ (nominal ζ_c=1.0; PI(f_*) in parentheses):

| β target | ζ_c=0.5 | ζ_c=0.7 | ζ_c=1.0 | ζ_c=1.3 | tuning dlnβ/dlnA_g | verdict |
|---|---|---|---|---|---|---|
| 10⁻⁵ | 5.6× | 3.4× | 2.3× (2.56×10⁻⁹) | 1.7× | 8.5 | MARGINAL, ζ_c-sensitive |
| 1.5×10⁻¹² | 40× | 25× | 17.9× (3.24×10⁻¹⁰) | 15× | 24.6 | SURVIVES |
| 2×10⁻¹⁹ | 108× | 67× | 48× (1.20×10⁻¹⁰) | 42× | 40.4 | SURVIVES |

Tail amplitudes (ζ_c=1): A_g^tail = 5.80×10⁻³ (10⁻⁵), 2.07×10⁻³
(1.5×10⁻¹²), 1.26×10⁻³ (2×10⁻¹⁹) — all ≪ 1, vanilla dominance holds.
Tuning is ~2× milder than Gaussian at briefing targets (40/25 vs 80/49),
confirming Abe et al.'s "insensitive to small f_PBH changes" remark in
quantitative form. (Numerical note: brentq emits a benign log10(0)
RuntimeWarning at the bracket edge; results verified against the validated
baseline — all 8 consistency checks pass.)

## 6. Band treatment (read this before quoting a margin)

- **Low-mass end (f_*=57.6 Hz): in-band — the binding case.** PI-envelope
  margins (1347× curvaton, 49.5× USR at nominal) ≈ headline margins; the
  comparison is physically meaningful.
- **High-mass end (f_*=7.4 μHz): no direct stochastic bound exists**
  (PTA covers nHz, LISA 0.1 mHz–0.1 Hz — μHz is the gap). The "182×/18×
  below O3" figures are number-to-number only, NOT constraints. The
  operative constraint is the BBN/CMB integral bound Ω_GW,0·h² ≲ 10⁻⁶:
  curvaton peak 69019× below it, USR peak 6787× below it. Physically the
  high-mass end is the *safest* target, not the riskiest — the O3
  comparison understates its headroom.

## 7. Verdicts (formation only)

| target × channel | verdict |
|---|---|
| curvaton β=10⁻⁵ | MARGINAL, threshold-fragile (3.5× nominal; flips at +17%) — unchanged |
| curvaton β=1.5×10⁻¹² | SURVIVES (182× nominal) **with threshold caveat** (fails for Δ_cr≳0.44) |
| curvaton β=2×10⁻¹⁹ | SURVIVES, robust (1317× nominal; fails only at Δ_cr≳0.56) |
| USR β=10⁻⁵ | MARGINAL, ζ_c-sensitive (2.3×/1.7× at ζ_c=1/1.3) — unchanged |
| USR β=1.5×10⁻¹² | SURVIVES (18× nominal, 15–40× across ζ_c; no in-band bound) |
| USR β=2×10⁻¹⁹ | SURVIVES (48× nominal, 42–108× across ζ_c) |

Net for the parked status: formation is now **rigorously** viable-with-margin
at the briefing targets for both channels. The [EST] flags on formation are
retired. The parked status itself is unchanged (conversion impasse stands),
but its formation half no longer rests on estimates.

## 8. Uncertainty ledger

| # | uncertainty | size | quantified? | verdict-flipping? |
|---|---|---|---|---|
| 1 | Δ_cr, curvaton (P&S 0.23 vs lit. 0.2–0.6) | floor ∝ T⁸; flip at +17%/+92%/+145% per target | yes (§4) | yes at 10⁻⁵; caveat at 1.5×10⁻¹²; no at 2×10⁻¹⁹ (except edge) |
| 2 | ζ_c, USR tail | margins ×[0.73, 2.4] rel. to ζ_c=1 | yes (§5) | no at briefing targets |
| 3 | PS vs peak-theory+critical-collapse (USR A_g) | ~30% in A_g, ~70% in Ω | partially (Abe cross-check) | no |
| 4 | P&S floor numerics | ~2× (their Fig. 3) | cited | no (vs T⁸) |
| 5 | Abe vanilla-dominance / monochromatic approx at k_*~10¹⁶ Mpc⁻¹ | O(1) | no | no at briefing margins |
| 6 | O3 bound conventions (5 vs 5.8×10⁻⁹, flat vs PI, h²) | ≲1.2× | yes | no |
| 7 | Narrow-peak assumption (Σ≲0.1), r_dec≲0.1 CMB compatibility | unquantified | no — inherited from P&S/Abe | model-building, not computed |

## 9. Exact ledger replacement text

### 9a. Survey §3 — replace the [EST] table

OLD:
```
| β target | σ₀√r needed | Ω_GW floor [EST] | vs LIGO 5×10⁻⁹ |
|---|---|---|---|
| 10⁻⁵ (T&L) | ≈ 0.66 | ≈ 1.7×10⁻⁹ | below by ~3× — marginal |
| 1.5×10⁻¹² (briefing top) | ≈ 0.40 | ≈ 3×10⁻¹¹ | below by ~160× |
| 2×10⁻¹⁹ (briefing bottom) | ≈ 0.31 | ≈ 4×10⁻¹² | below by ~1000× |
```
NEW:
```
| β target | σ₀√r | Ω_GW floor (end-to-end) | vs O3 95% (5.8×10⁻⁹) | threshold span T∈[0.87, 2.61] |
|---|---|---|---|---|
| 10⁻⁵ (T&L) | 0.6532 | 1.64×10⁻⁹ | 3.5× below — marginal | 10.8× below → excluded (flips at +17%) |
| 1.5×10⁻¹² (briefing top) | 0.3993 | 3.19×10⁻¹¹ | 182× below (threshold caveat: fails for Δ_cr≳0.44) | 554× below → excluded |
| 2×10⁻¹⁹ (briefing bottom) | 0.3117 | 4.40×10⁻¹² | 1317× below (robust) | 4012× below → excluded only at extreme edge |
```

### 9b. Survey §4 — replace the [EST] table

OLD:
```
| β target | Gaussian P_R | Tail A_g [EST] | Ω_GW [EST] | vs LIGO 5×10⁻⁹ |
|---|---|---|---|---|
| 10⁻⁵ (T&L) | 5.6×10⁻² | ~4×10⁻³ | ~10⁻⁹–10⁻⁸ | marginal — touches bound at top of range |
| 1.5×10⁻¹² | ~2×10⁻² | ~1.7×10⁻³ | ~10⁻¹⁰–10⁻⁹ | below by ~5–50× |
| 2×10⁻¹⁹ | ~1.3×10⁻² | ~1.1×10⁻³ | ~10⁻¹¹–10⁻¹⁰ | below by ~10–100× |
```
NEW:
```
| β target | Tail A_g (ζ_c=1, end-to-end) | Ω_GW (end-to-end) | vs O3 95% (5.8×10⁻⁹) | ζ_c∈[0.5, 1.3] span |
|---|---|---|---|---|
| 10⁻⁵ (T&L) | 5.80×10⁻³ | 2.56×10⁻⁹ | 2.3× below — marginal | 5.6× → 1.7× below |
| 1.5×10⁻¹² (briefing top) | 2.07×10⁻³ | 3.24×10⁻¹⁰ | 17.9× below (formal; no in-band bound — BBN integral bound 6787× below) | 40× → 15× below |
| 2×10⁻¹⁹ (briefing bottom) | 1.26×10⁻³ | 1.20×10⁻¹⁰ | 48× below | 108× → 42× below |
```

### 9c. Survey §7 bottom line — replace the formation paragraph

OLD: "For the **briefing's β targets (10⁻¹⁹–10⁻¹²)** both sit **below the
LIGO bound with margin** (factors ~5–1000 depending on target and mechanism).
For **T&L's illustrative β ~ 10⁻⁵** both are **marginal** (within a factor of
a few of the bound)."

NEW: "For the **briefing's β targets (10⁻¹⁹–10⁻¹²)** both sit **below the
bound with margin, now end-to-end** (2026-10-06, `formation_endtoend_note.md`):
curvaton 182–1317× nominal (robust at 2×10⁻¹⁹; threshold caveat at
1.5×10⁻¹² for Δ_cr≳0.44); USR 18–48× nominal, 15–108× across ζ_c (the
1.5×10⁻¹² peak sits at 7 μHz with no direct bound — BBN integral bound is
the operative constraint, 6787× below). For **T&L's illustrative β ~ 10⁻⁵**
both are **marginal** (curvaton 3.5×, threshold-flips at +17%; USR 2.3× at
ζ_c=1, 1.7× at ζ_c=1.3) — confirmed end-to-end; 'marginal' is the verdict."

### 9d. v3 salvage memo — QSE entries

Registry row (line 24), replace
"Formation: curvaton ≈160–1000× [EST], USR ≈5–100× [EST] below LIGO O3 bound
at briefing targets"
with
"Formation: curvaton 182–1317×, USR 18–48× nominal (15–108× across ζ_c),
end-to-end 2026-10-06 (`formation_endtoend_note.md`); threshold caveat on
curvaton at 1.5×10⁻¹² (Δ_cr≳0.44); [EST] flags retired for formation".

Card Result paragraph, replace
"**≈160–1000× [EST]** at the briefing β targets (160× at 1.5×10⁻¹²,
1000× at 2×10⁻¹⁹)"
with
"**182–1317× (end-to-end 2026-10-06)** at the briefing β targets (182× at
1.5×10⁻¹² with threshold caveat for Δ_cr≳0.44; 1317× at 2×10⁻¹⁹, robust)",
replace
"**≈5–100× [EST]**\n  (5–50× at 1.5×10⁻¹², 10–100× at 2×10⁻¹⁹)"
with
"**18–48× nominal, 15–108× across ζ_c∈[0.5,1.3] (end-to-end)**\n  (17.9× at 1.5×10⁻¹², formal — no in-band bound; 48× at 2×10⁻¹⁹)",
and replace
"Briefing-target\n  margins remain **[EST]** pending the full end-to-end script (running);"
with
"Briefing-target\n  margins are now **end-to-end** (`formation_endtoend_note.md`,\n  2026-10-06); [EST] flags retired for formation. Parked status unchanged\n  (conversion impasse stands)."

Suggested: evidence-type "Analytic closure + corrected numerical estimate" →
"New analysis (end-to-end numerical) + analytic closure"; maturity stays
Medium (conditional on threshold/ζ_c choices and literature formulas).

## 10. Follow-ups (noted, not started — out of scope)

- Profile-appropriate Δ_cr for the curvaton peak shape (Yoo et al.'s 0.23 is
  for one specific profile) — collapses uncertainty #1, the dominant one,
  and decides the high-mass curvaton caveat.
- Dedicated peak-theory + critical-collapse USR abundance at k_*~10¹⁶ Mpc⁻¹
  (shrinks #3/#5).
- O4/O5 will tighten the in-band bound ~2–3×: low-mass margins (48× USR,
  1317× curvaton) are safe; β=10⁻⁵ USR (2.3×) is within reach of exclusion.
- The high-mass μHz peak has no foreseeable direct probe; BBN/CMB-S4
  N_eff is the operative constraint.
