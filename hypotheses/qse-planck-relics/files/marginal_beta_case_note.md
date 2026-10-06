# QSE marginal case: β = 10⁻⁵, rigorous end-to-end redo

Date: 2026-10-06. Companion code: `marginal_beta_case_note.md` (this file),
`marginal_beta_calc.py` (this case), `endtoend_calc.py` (shared machinery, bug-fixed — see §5).

## 1. What the [EST] case assumed (reconstructed chain)

The formation survey (`nongaussian_formation_survey.md`, 2026-10-03) carries one
illustrative benchmark from T&L at **β ≈ 10⁻⁵** — far above the briefing relic targets
(2×10⁻¹⁹, 1.5×10⁻¹²) — where both non-Gaussian channels were estimated "marginal":

**Curvaton (small decay fraction r, Pi & Sasaki 2112.12680).**
- Abundance: β_tot ≈ ½ erfc(1.97/(σ₀√r)) (their Eq. 28, small-r fit; 1.97 encodes
  their adopted collapse threshold Δ_cr ≈ 0.23 from Yoo et al. peak theory).
- At β=10⁻⁵: erfc argument must equal erfc⁻¹(2×10⁻⁵) ≈ 3.02, so σ₀√r ≈ 0.66.
- Induced-GW floor (their Eq. 32, small-r limit, quadratic local-NG computation
  following the standard references): Ω_GW,0^floor ≈ 10⁻⁶·(4/81)·(σ₀√r)⁸.
- [EST] arithmetic: 10⁻⁶ × 0.0494 × 0.66⁸ ≈ 1.7×10⁻⁹ vs the O3 number 5×10⁻⁹
  → "~3× below, marginal."

**USR exponential tail (Abe et al. 2209.13891).**
- Abundance from the exponential-tail integral (their peak-theory + critical collapse);
  Gaussian would need P_R ≈ 5.6×10⁻² at β=10⁻⁵ (T&L), the tail needs only
  A_g^tail ~ 4×10⁻³ [EST guess].
- Induced GW: Abe et al. show the vanilla (Gaussian) diagram dominates, so
  Ω_GW,USR = (A_g^tail/A_g^Gauss)² × Ω_GW,Gauss(A_g^Gauss) — the variance ratio squared.
- [EST]: (4×10⁻³/5.6×10⁻²)² × (10⁻⁷–10⁻⁶) ≈ 10⁻⁹–10⁻⁸ → "marginal, touches the
  bound at the top of the range."

**O3 mapping in the [EST].** Compared peak Ω_GW,0 directly against the headline
O3 stochastic number Ω_GW ≲ 5×10⁻⁹ (flat spectrum, 95%). No frequency dependence,
no confidence-level bookkeeping, no threshold systematics.

## 2. Rigorous redo — methods

Second-order scalar-induced GWs, standard radiation-era transfer functions.
Approximations stated per channel:

- **Gaussian baseline (calibration):** monochromatic-peak coefficient
  Ω_GW,0^peak ≈ 0.822·Ω_r,0·P_R², Ω_r,0 = 9.24×10⁻⁵ (Kohri & Terada). Validated
  against T&L's independent numbers (2.4×10⁻⁷ vs their 10⁻⁷–10⁻⁶ at P_R=5.6×10⁻² ✓).
- **Curvaton:** Pi & Sasaki Eqs. 28/31/32 used verbatim. I re-verified Eq. 32
  against the paper source: Ω_GW ∼ 10⁻⁶σ_ζ⁴ = 10⁻⁶(4/81)(σ₀√r)⁸, with their
  quoted "∼10⁻¹¹" check reproduced (σ₀√r=0.36 → 1.4×10⁻¹¹ ✓) and their
  "σ_ζ² ≳ 2×10⁻³" reproduced (3.7×10⁻³ ✓). Their floor is validated to ~2× by
  their own numerics (Fig. 3). Validity conditions checked at the new parameters:
  r ≪ 1, σ₀ ≫ 1, σ_ζ² ≲ 0.1 (quadratic approximation).
- **USR:** exact numerical tail integral
  β(σ_g) = ∫_{ζ_c}^∞ e^{−3ζ} N(ζ_g(ζ); 0, σ_g²) dζ, ζ_g = (1−e^{−3ζ})/3,
  inverted for A_g^tail = σ_g² at β=10⁻⁵; GW via Abe's vanilla-dominance result
  Ω_GW,USR = C·(A_g^tail)², C = 0.822·Ω_r,0 (see §5 for why this is the correct
  reading of their (1.32/5.17)² ≈ 0.065). Scanned ζ_c ∈ {0.5, 0.7, 1.0, 1.3}.
- **O3 comparison:** proper 95%-credible power-law-integrated (PI) envelope from
  the published O3 limits (Abbott et al. 2021, arXiv:2101.12130, log-uniform prior):
  (α, limit at 25 Hz) = (0, 5.8×10⁻⁹), (2/3, 3.4×10⁻⁹), (3, 3.9×10⁻¹⁰);
  Ω_PI(f) = max_α limit_α·(f/25)^α. Narrowband peak at f_* compared against
  Ω_PI(f_*). Peak of induced spectrum sits at ≈1.15·f_* for a narrow scalar peak.
- **f_* anchor:** M = 10⁹ kg → f_* = 57.6 Hz (in-band; the conservative placement —
  O3 sensitivity degrades fast above ~100 Hz, so higher f_* only helps). Scanned
  f_* ∈ [20, 1000] Hz.

## 3. Results at β = 10⁻⁵

erfc⁻¹(2×10⁻⁵) = 3.0157. Gaussian calibration: P_R = 5.50×10⁻²,
Ω_GW,0 = 2.30×10⁻⁷ → **40× above** O3 (5.8×10⁻⁹): Gaussian robustly excluded ✓.

### Curvaton
- σ₀√r = 0.6532 ([EST] said ~0.66 ✓). Floor Ω_GW,0 = **1.64×10⁻⁹**
  ([EST] said ~1.7×10⁻⁹ ✓ — the estimate's arithmetic is confirmed almost exactly).
- Vs O3 5.8×10⁻⁹ (95%): **3.5× below**. Vs PI(58 Hz) = 5.96×10⁻⁹: **3.6× below**.
- Validity: r=10⁻³ → σ₀=20.7 ≫ 1 ✓; F_NL = 750; σ_ζ² = 0.040 < 0.1 ✓
  (nearer the quadratic-approximation boundary than the briefing targets'
  0.002–0.006, but inside).
- Tuning dlnβ/dln(σ₀√r) = 18.2 (milder than the 80/49 at briefing targets).
- **Threshold scan** (T multiplies the 1.97; Pi & Sasaki adopt Δ_cr=0.23,
  literature range 0.2–0.6 → T ∈ [0.87, 2.61]):

| T | σ₀√r | floor Ω_GW,0 | vs 5.8×10⁻⁹ |
|---|---|---|---|
| 0.87 (lit. low) | 0.568 | 5.4×10⁻¹⁰ | 10.8× below |
| 1.00 (P&S) | 0.653 | 1.64×10⁻⁹ | 3.5× below |
| 1.10 | 0.719 | 3.5×10⁻⁹ | 1.7× below |
| 1.20 | 0.784 | 7.0×10⁻⁹ | **1.2× above — excluded** |
| 2.61 (lit. high) | 1.705 | 3.5×10⁻⁶ | **600× above — excluded** |

  Floor ∝ T⁸. The verdict flips between T=1.1 and T=1.2 — a ~15% upward
  threshold shift erases the entire margin.

### USR exponential tail (corrected formula — see §5)
- A_g^tail(ζ_c=1.0) = 5.80×10⁻³ ([EST] guessed ~4×10⁻³; exact is 45% higher).
  Ω_GW,0 = **2.56×10⁻⁹** → **2.3× below** O3 (5.8×10⁻⁹); 2.3× below PI(58 Hz).

| ζ_c | A_g^tail | Ω_GW,0 | vs 5.8×10⁻⁹ | Abe-scaled |
|---|---|---|---|---|
| 0.5 | 3.69×10⁻³ | 1.03×10⁻⁹ | 5.6× below | 9.5× below |
| 0.7 | 4.74×10⁻³ | 1.70×10⁻⁹ | 3.4× below | 5.8× below |
| 1.0 | 5.80×10⁻³ | 2.56×10⁻⁹ | 2.3× below | 3.8× below |
| 1.3 | 6.72×10⁻³ | 3.43×10⁻⁹ | 1.7× below | 2.9× below |

  ("Abe-scaled": their absolute A_g^tail = 1.32×10⁻³ at f_PBH=1 vs my PS
  1.72×10⁻³ at β=10⁻¹⁴ — 30% lower — scaled to β=10⁻⁵ assuming common β-scaling.
  Their method is slightly more optimistic for the bound, not less; the old
  note's "0.255 vs 0.317" framing mixed variance ratio with rms ratio.)
- Validity: A_g^tail = 5.8×10⁻³ ≪ 1 ✓ (vanilla dominance holds).
  Tuning dlnβ/dlnA_g = 8.5.

### Frequency dependence (PI envelope)

| f_* (Hz) | Ω_PI,95% | curvaton margin | USR margin (ζ_c=1) |
|---|---|---|---|
| 20–58 | ~6×10⁻⁹ | 3.5–3.6× | 2.3× |
| 100 | 2.5×10⁻⁸ | 15× | 9.8× |
| 200 | 2.0×10⁻⁷ | 122× | 78× |

Margins grow fast with f_*; the in-band placement is the binding case.

## 4. Verdict

**The [EST] "marginal within ~3×" is confirmed rigorously — and "marginal" is the
verdict, not a stepping stone to one.** Neither channel closes, neither is safe:

- **Curvaton β=10⁻⁵: MARGINAL, threshold-fragile.** Survives 3.5× below O3 on
  Pi & Sasaki's threshold choice (Δ_cr=0.23, near the bottom of the literature
  0.2–0.6). A ~15% upward threshold revision flips it to excluded; across the
  literature threshold range it spans 11× safe → 600× excluded. **Undecidable
  from theory alone — the threshold choice is doing the work.**
- **USR β=10⁻⁵: MARGINAL, ζ_c-sensitive.** Survives 2.3× below at ζ_c=1.0
  (nominal), 1.7× at ζ_c=1.3; Abe's own absolute amplitudes give slightly more
  room. A pessimistic-but-plausible stack (high ζ_c + O(1) method systematics)
  can push it over. **Leans survive, not safe.**

**The β=10⁻⁵ sub-case stays OPEN.** It does not close (neither channel is
excluded nominally), but it must be carried with a fragility flag, not a margin.

## 5. Bug found in the shared machinery (corrects existing ledger numbers)

While re-deriving the USR comparison from Abe et al.'s text I found that
`endtoend_calc.py` implemented their GW reduction incorrectly. Abe et al. state
(verified against the paper source): f_PBH=1 needs A_g = 5.17×10⁻³ (Gaussian) vs
1.32×10⁻³ (exponential tail), "the leading order Vanilla contribution ∼ O(A_g²)
is dominant," and the GW amplitude "is reduced by (1.32×10⁻³/5.17×10⁻³)² ≃ 0.065
compared with the case where ζ is purely Gaussian." Since Ω_GW ∝ A_g² with A_g
the spectrum amplitude (variance), this means

  Ω_USR = (A_g^T/A_g^G)² · Ω_Gauss(A_g^G) = C·(A_g^T)² = Ω_GW,gauss(A_g^T).

The code defined ratio = √(A_g^T/A_g^G) (rms ratio) and computed
ratio²·Ω_Gauss(A_g^G) = C·A_g^T·A_g^G — **overestimating Ω_USR by A_g^G/A_g^T ≈ 10×**.
(Fixed in `endtoend_calc.py` with a documenting comment, 2026-10-06.)
The old note's "my ratio 0.317 vs their 0.255" comparison was additionally
mixing an rms ratio with their variance ratio; in comparable terms it is
variance ratio 0.100 (my PS) vs 0.255 (their peak theory), and the absolute
A_g^tail agrees to ~30% (1.72×10⁻³ vs 1.32×10⁻³ at β~10⁻¹⁴).

**Ledger impact:** the briefing-target USR verdicts in `nongaussian_endtoend_note.md`
(and anything downstream, e.g. the v3 salvage memo) were computed with the bug:
- low-mass end: Ω_GW was 1.19×10⁻⁹ (4.2× below) → **corrected 1.20×10⁻¹⁰
  (48× below)**. "WORKS MARGINALLY" → **"WORKS"**.
- high-mass end: was 3.22×10⁻⁹ (1.6× below; no in-band bound) → **corrected
  3.24×10⁻¹⁰ (18× below)**.
Tuning numbers, Gaussian baselines, and all curvaton numbers are unaffected.
(A cross-check: Jiang et al. 2409.07976's dedicated O1–O3 scalar-induced-GW
search limits the curvature amplitude to A ≲ 0.1 at 95% in 20–200 Hz; our
A_g^tail ~ 6×10⁻³ sits well under it — consistent.)

## 6. Uncertainty ledger

| # | Uncertainty | Size | Quantified? | Verdict-flipping? |
|---|---|---|---|---|
| 1 | Collapse threshold Δ_cr (curvaton): P&S use 0.23, lit. 0.2–0.6 | floor ∝ T⁸, ×[0.33, 2088] | yes (§3 table) | **yes** (flips at +15%) |
| 2 | ζ_c, USR tail integral | Ω ×[0.4, 1.34] rel. to ζ_c=1 | yes (§3 table) | at high ζ_c + other syst. |
| 3 | PS vs peak-theory+critical-collapse (USR A_g^tail) | ~30% in A_g, ~70% in Ω | partially (Abe cross-check) | no (sub-dominant) |
| 4 | P&S floor numerics | ~2× (their Fig. 3) | cited, not re-derived | no (vs threshold T⁸) |
| 5 | Abe vanilla-dominance / monochromatic approx | O(1) | no — needs dedicated calc at k_*~10¹⁶ Mpc⁻¹ | contributes at margin edge |
| 6 | O3 bound: 5 vs 5.8×10⁻⁹; flat vs PI; h² conventions | ≲1.2× combined | yes | no |
| 7 | f_* placement (58 Hz anchor vs 100–1000 Hz) | margins grow ≥4× by 100 Hz | yes (§3 table) | only helps |

## 7. What changes for the QSE ledger

1. **β=10⁻⁵ sub-case: stays open, fragility flag attached.** Replace "[EST]
   marginal ~3×" with the rigorous numbers above: curvaton 3.5× below but
   threshold-flips at +15% (Δ_cr choice doing the work); USR 2.3× below at
   ζ_c=1, 1.7× at ζ_c=1.3. Neither "safe" nor "closed."
2. **Correct the briefing-target USR entry** (bug §5): USR now WORKS (48×) at
   the low-mass end, not "marginally" (4.2×). Strengthens — not weakens — the
   parked QSE formation case.
3. **Method note for future work:** any re-examination of these numbers must use
   Ω_USR = C·(A_g^tail)² (variance ratio squared), not the rms-ratio form; and
   the curvaton case needs the Δ_cr assumption stated alongside the margin,
   since the margin is meaningless without it.

## 8. Follow-ups (noted, not started — out of scope)

- Dedicated peak-theory + critical-collapse abundance at k_* ~ 10¹⁶ Mpc⁻¹ to
  replace the PS tail integral for USR (the note's standing recommendation;
  would shrink uncertainty #3/#5).
- The Δ_cr = 0.23 choice traces to Yoo et al.'s optimized peak-theory criterion
  for one specific profile; a profile-appropriate threshold for the curvaton
  peak shape would collapse uncertainty #1, the dominant one.
- O4/O5 will improve the bound ~2–3× (already 2.0×10⁻⁹ at α=2/3 in the 2026
  update, arXiv:2608.23477) — at that point the nominal β=10⁻⁵ USR point
  (2.56×10⁻⁹) is within reach of exclusion even without threshold help.
