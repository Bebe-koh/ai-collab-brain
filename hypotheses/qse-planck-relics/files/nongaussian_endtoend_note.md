# QSE Round 2: End-to-End Non-Gaussian Formation Calculation

**Date:** 2026-10-03
**Status:** Calculation complete. Reproducible numbers from published formalisms — this is
a `completed-toy` level result (theoretical calculation, not validated against data).
**Code:** `endtoend_calc.py` (this directory). All numbers below are its output.
**Round 1:** `nongaussian_formation_survey.md` (literature survey; its `[EST]` mappings are
superseded by the numbers here).

## 0. What "end-to-end" means here

For each of the two surviving mechanisms — **(B) small-r curvaton** (Pi & Sasaki,
arXiv:2112.12680) and **(C) USR exponential tail** (Kitajima et al. 2109.00791;
Abe et al. 2209.13891) — I take the briefing's abundance targets
(β ≈ 2×10⁻¹⁹ at M ≈ 10⁹ kg; β ≈ 1.5×10⁻¹² at M ≈ 6×10²² kg),
solve for the model parameters that produce them using each paper's own
β-formula, compute the induced stochastic GW spectrum from each paper's own
GW-formula, and compare against the LIGO/Virgo/KAGRA O3 stochastic bound
(Ω_GW,0 ≲ 5×10⁻⁹). Where a published formula does not directly apply, I derive
the extension and flag it. Fine-tuning is quantified as d ln β / d ln(param).

## 1. Framework (recomputed, not inherited)

**Mass ↔ frequency.** For PBH mass M (M = γM_H, γ = 0.2):

| M | t_f | T_f | f_* (peak) | k_* |
|---|---|---|---|---|
| 10⁹ kg | 5.0×10⁻²⁶ s | 2.2×10⁹ GeV | **58 Hz** | 3.7×10¹⁶ Mpc⁻¹ |
| 6×10²² kg | 3.0×10⁻¹² s | 2.8×10² GeV | 7.4×10⁻⁶ Hz | 4.8×10⁹ Mpc⁻¹ |

The low-mass end sits squarely in the LIGO band; the high-mass end does not
(§6). (With γ = 1, f_* shifts ×2.2; the verdicts are unaffected.)

**Relic-abundance consistency check — new insight.** The briefing's β targets
were sanity-checked against the relic density, and the check *fails* for the
evaporation picture but *passes* for the shatter picture:

- Evaporation (one m_Pl relic per PBH): Ω_relic ≈ 10⁻¹⁷. **Wrong by 16 orders.**
- Shatter (progenitor mass fully converts to Planck-mass relics at/near
  formation): Ω_relic ≈ 0.5 × (β/2×10⁻¹⁹). **Matches Ω_DM ≈ 0.25 to factor ~2.**

**The briefing's β targets therefore require the shatter/bounce picture, not
evaporation.** (The factor ~2 is f_sh, shatter efficiency/timing, or g_*
details.) This is consistent with the briefing's own statement that the bounce
graft removes evaporation constraints — but it sharpens it: without
near-complete mass-to-relic conversion, the quoted β values underproduce DM by
~10¹⁶. Any future revision of the β targets must state the assumed conversion
explicitly.

## 2. Gaussian baseline (recomputed for calibration)

β = ½ erfc(ζ_c/(√2σ)), σ² = P_R, ζ_c = 1. Induced GW (monochromatic peak):
Ω_GW,0^peak ≈ 0.822 × Ω_r,0 × P_R², Ω_r,0 = 9.24×10⁻⁵.

| Target | β | P_R needed | Ω_GW,0 | vs LIGO 5×10⁻⁹ | f_* |
|---|---|---|---|---|---|
| T&L benchmark | 10⁻⁵ | 5.5×10⁻² (paper: 5.6×10⁻² ✓) | 2.4×10⁻⁷ (paper: 10⁻⁷–10⁻⁶ ✓) | **48× above** | ~58 Hz |
| Briefing low-mass | 2×10⁻¹⁹ | 1.25×10⁻² | 1.2×10⁻⁸ | **2.4× above** | 58 Hz, in-band |
| Briefing high-mass | 1.5×10⁻¹² | 2.05×10⁻² | 3.2×10⁻⁸ | 6.4× above (no bound in-band) | 7×10⁻⁶ Hz |

**Threshold caveat (important).** The Gaussian exclusion is threshold-dependent:

| ζ_c | P_R (β=2×10⁻¹⁹) | Ω_GW,0 | vs LIGO |
|---|---|---|---|
| 0.5 | 3.1×10⁻³ | 7.4×10⁻¹⁰ | 0.15× — **not excluded** |
| 0.7 | 6.1×10⁻³ | 2.9×10⁻⁹ | 0.57× — not excluded |
| 1.0 | 1.25×10⁻² | 1.2×10⁻⁸ | 2.4× — excluded |
| 1.3 | 2.1×10⁻² | 3.4×10⁻⁸ | 6.8× — excluded |

T&L's β = 10⁻⁵ benchmark is robustly excluded at any plausible threshold, but
**for the briefing's own β = 2×10⁻¹⁹ target, the Gaussian LIGO exclusion holds
only for ζ_c ≳ 0.8.** At ζ_c ≲ 0.7 (plausible for some profiles), even Gaussian
formation survives LIGO at these β values. The briefing's "ruled out" should be
read as "ruled out at the standard threshold"; it is not threshold-robust the
way T&L's benchmark is.

## 3. Mechanism B: curvaton, small-r — END-TO-END

**Formulas used (verbatim from Pi & Sasaki):**
- Abundance, r ≲ 0.1 (their Eq. 28): β_tot ≈ ½ erfc(1.97/(σ₀√r)).
  The 1.97 encodes their Δ_cr ≈ 0.23 (Yoo et al. 2018 peak-theory threshold).
- Variance, σ₀ ≫ 1 (from their Eq. 31): σ_ζ² ≈ (2/9)(σ₀√r)⁴.
- GW floor, r → 0 (their Eq. 32, validated to ~2× by their numerics):
  Ω_GW^floor ≈ 10⁻⁶ × (4/81)(σ₀√r)⁸. This is Ω_GW,0 (today), directly
  comparable to the LIGO bound.

**Results** (solved for σ₀√r from Eq. 28 at each β target):

| Target | β | σ₀√r required | e.g. (r, σ₀) | σ_ζ² | Ω_GW floor | vs LIGO |
|---|---|---|---|---|---|---|
| Low-mass | 2×10⁻¹⁹ | **0.312** | (10⁻³, 9.9), F_NL = 750 | 2.1×10⁻³ | **4.4×10⁻¹²** | **1100× below** |
| High-mass | 1.5×10⁻¹² | **0.399** | (10⁻³, 12.6), F_NL = 750 | 5.7×10⁻³ | 3.2×10⁻¹¹ | 160× below (no in-band bound) |

**Validity checks (all pass):** r = 10⁻³ ≲ 0.1 ✓ (Eq. 28 regime); σ₀ ≈ 10–13 ≫ 1 ✓
(Eq. 31 regime); σ_ζ² ≈ (2–6)×10⁻³ ≲ 0.1 ✓ (quadratic-NG approximation for the
GW calculation, as required by Pi & Sasaki).

**Threshold robustness:** even if the true collapse threshold were 2× higher
than Pi & Sasaki's (1.97 → 2.8), the floor rises by (1.4)⁸ ≈ 15× to 6.6×10⁻¹¹,
still 75× below LIGO. **The curvaton verdict is threshold-robust.**

**Fine-tuning:** d ln β/d ln(σ₀√r) = 2x² = **80** (low-mass), **49** (high-mass) —
*identical* to Gaussian. The curvaton buys GW suppression, not tuning relief.
A 1% shift in σ₀√r moves β by ~80%/~49%. The tuning is relocated to
model-building: a sharp dip in the spectator kinetic coupling f(φ) placing a
narrow peak (Σ ≲ 0.1) at k_* ≈ 4×10¹⁶ Mpc⁻¹, plus r_dec ~ 10⁻³.

**Verdict: WORKS.** Both β targets are hit with the GW floor 2–3 orders of
magnitude below the LIGO bound, robust to threshold systematics. The price is
Gaussian-level fine-tuning plus the peaked-spectrum model-building.

## 4. Mechanism C: USR exponential tail — END-TO-END

**Formulas used:**
- Tail PDF (Abe et al. Eq. 2.6, from the δN mapping ζ = −⅓ln(1−3ζ_g)):
  P(ζ) = e^{−3ζ} · N(ζ_g(ζ); 0, σ_g²), ζ_g(ζ) = (1−e^{−3ζ})/3.
- Abundance: β(σ_g) = ∫_{ζ_c}^∞ P(ζ)dζ, computed numerically here
  (Press–Schechter-style; Kitajima et al. use peak theory + critical collapse —
  see calibration below).
- GW: Abe et al.'s diagrammatic result — the leading "vanilla" O(A_g²) diagram
  dominates, NG corrections subdominant, so
  Ω_GW,0^USR = (A_g^tail/A_g^Gauss)² × Ω_GW,0^Gauss(A_g^Gauss).

**Calibration against the literature.** At β ~ 10⁻¹⁴ (their f_PBH = 1 point),
my tail integral gives A_g^tail/A_g^Gauss = **0.317**; Abe et al.'s peak-theory
gives **0.255**. Same ballpark; the difference is the abundance method
(PS vs peak theory + critical collapse). I use my self-consistent 0.317 so the
comparison to my Gaussian baseline is apples-to-apples, and note theirs as the
more optimistic end. The ratio is β-independent across 10⁻¹⁹–10⁻¹² (verified),
confirming their "universal" claim in this regime.

**Results** (ζ_c = 1 baseline):

| Target | β | A_g^tail required | (Gaussian would need) | Ω_GW,0 | vs LIGO |
|---|---|---|---|---|---|
| Low-mass | 2×10⁻¹⁹ | **1.26×10⁻³** | 1.25×10⁻² (ratio 0.32) | **1.2×10⁻⁹** | **4.2× below** |
| High-mass | 1.5×10⁻¹² | **2.07×10⁻³** | 2.05×10⁻² (ratio 0.32) | 3.2×10⁻⁹ | 1.6× below (no in-band bound) |

**Threshold sensitivity** (low-mass target):

| ζ_c | A_g^tail | Ω_GW,0 | vs LIGO |
|---|---|---|---|
| 0.5 | 8.4×10⁻⁴ | 2.0×10⁻¹⁰ | 25× below |
| 1.0 | 1.26×10⁻³ | 1.2×10⁻⁹ | 4.2× below |
| 1.3 | 1.34×10⁻³ | 2.2×10⁻⁹ | 2.3× below |

**Fine-tuning:** d ln β/d ln A_g = **40** (low-mass), **25** (high-mass) —
about **2× milder than Gaussian** (80/49). This confirms Abe et al.'s remark
that A_g is "insensitive to small changes of f_PBH." The USR tail is the only
mechanism here that genuinely *reduces* the tuning, not just relocates it.

**Verdict: WORKS MARGINALLY.** It clears the LIGO bound at both targets, but
the low-mass margin is only ~4× at the standard threshold (2–25× across the
plausible threshold range), against O(few) systematics (induced-GW coefficient,
LIGO frequency dependence, PS-vs-peak-theory). A dedicated peak-theory +
critical-collapse calculation at the QSE mass scale (k_* ~ 10¹⁶ Mpc⁻¹) is needed
for a firm verdict. Heavier tails (Λ < 3, cf. Refs. [60–62] in Abe et al.)
would widen the margin and are the natural fallback.

## 5. Fine-tuning comparison (the honest ledger)

| Mechanism | d ln β/d ln(param), β=2×10⁻¹⁹ | d ln β/d ln(param), β=1.5×10⁻¹² | Tuning relocated to |
|---|---|---|---|
| Gaussian (P_R) | 80 | 49 | amplitude |
| Curvaton (σ₀√r) | 80 | 49 | tail/model params (peak position, f(φ) dip, r_dec) |
| USR tail (A_g) | 40 | 25 | inflection-point potential, tail slope Λ |

The curvaton does **not** improve fine-tuning — it is exponentially sensitive in
σ₀√r exactly like the Gaussian is in amplitude. Only the USR tail mildly
improves it (~2×). Neither mechanism eliminates tuning; the USR tail is the
only one that reduces it.

## 6. Where the LIGO bound does and doesn't apply

- **Low-mass end (10⁹ kg, f_* ≈ 58 Hz):** in the LIGO O3 band. The bound bites.
  This is the decisive check, and both mechanisms pass it.
- **High-mass end (6×10²² kg, f_* ≈ 7×10⁻⁶ Hz):** far below the LIGO band.
  Current constraints here are ΔN_eff (∫Ω_GW dlnf ≲ 10⁻⁶ — both mechanisms are
  3–5 orders of magnitude below) and, in the future, LISA (both mechanisms'
  signals at ~10⁻¹¹–10⁻⁹ are *above* projected LISA sensitivity — a future
  test, not a current bound). The "× below LIGO" numbers quoted for this end
  are against the numerical bound value only, for reference.

## 7. Assumptions and systematics (explicit)

1. **Narrow peak** (Σ ≲ 0.1) at k_*(M) for each target; targets treated as
   monochromatic. An extended mass function would smear the GW peak but not
   change the order of magnitude.
2. **β_tot ≈ β(M)** up to an O(1) width factor; propagates to O(2) on Ω_GW.
   Absorbed in the quoted margins.
3. **Collapse threshold:** ζ_c = 1 baseline; sensitivity tabulated. Curvaton
   uses Pi & Sasaki's Δ_cr = 0.23 throughout (robust, §3).
4. **Induced-GW coefficient** 0.822 (monochromatic, Kohri & Terada): O(1)
   shape systematic, up to ~3×. Does not flip the curvaton verdict; relevant
   to the USR margin.
5. **LIGO O3 bound** 5×10⁻⁹ applied at f_*: the true frequency-dependent limit
   at ~58 Hz differs by O(2). Relevant to the USR margin, not the curvaton.
6. **γ = 0.2** (M_PBH = γM_H): affects f_* only (×2.2 vs γ = 1), not amplitudes.
7. **Shatter picture** for relic abundance (§1): near-complete progenitor-mass
   → relic conversion. If f_sh ≪ 1, the β targets must be revised upward and
   the GW signals rise accordingly (Ω_GW ∝ β-mapping, mechanism-dependent).
8. **No running of the NG parameters** across the (wide) mass range; each target
   treated independently.

## 8. Verdicts

| Mechanism | β targets hit? | LIGO bound cleared? | Tuning vs Gaussian | Verdict |
|---|---|---|---|---|
| **B. Curvaton (small r)** | Yes — σ₀√r = 0.31/0.40 | Yes — floor 10³×/10²× below | Same (80/49) | **WORKS.** Robust to threshold and O(few) systematics. Price: Gaussian-level tuning + peaked-spectrum model-building. |
| **C. USR exp. tail (Λ=3)** | Yes — A_g = 1.3/2.1×10⁻³ | Yes — 4×/1.6× below (low-mass in-band) | ~2× milder (40/25) | **WORKS MARGINALLY.** Clears the bound but the low-mass margin is thin against systematics. Needs a dedicated peak-theory calculation at k_* ~ 10¹⁶ Mpc⁻¹; heavier tails (Λ<3) are the fallback. |

**Nothing here is "validated"** — these are reproducible calculations from
published formalisms applied to the QSE targets, i.e. `completed-toy`. What
would promote them: (a) the dedicated peak-theory USR calculation at QSE
scales; (b) a concrete curvaton model realizing the Σ ≲ 0.1 peak at
k_* ~ 10¹⁶ Mpc⁻¹ with r_dec ~ 10⁻³; (c) confronting the predicted GW peak
(~58 Hz, Ω ~ 10⁻¹²–10⁻⁹) with future LVK runs — both mechanisms predict a
signal that is *below* O3 but potentially visible to next-generation
ground-based detectors, a genuine falsifiable handle.

## 9. The single most important secondary finding

The relic-abundance check (§1) shows the briefing's β targets are consistent
**only** with near-complete conversion of progenitor mass into Planck-mass
relics (the shatter/bounce picture), not with one-relic-per-evaporated-BH
(which underproduces DM by ~10¹⁶). This is a load-bearing constraint on the
bounce-vs-fragmentation fork: whichever mechanism is chosen must convert
O(1) of the progenitor mass into relics, not merely leave a Planck remnant
after evaporation. If a future version of the framework weakens this
(f_sh ≪ 1), the β targets — and these GW numbers — must be redone.

## References (formulas sourced)

- Trivedi & Loeb, arXiv:2509.20533 (benchmark β ~ 10⁻⁵, P_R = 5.6×10⁻²).
- Pi & Sasaki, arXiv:2112.12680 — Eqs. (28) β_tot, (31) σ_ζ², (32) GW floor.
- Kitajima, Tada, Yokoyama, Yoo, arXiv:2109.00791 — exponential-tail abundance.
- Abe, Inui, Tada, Yokoyama, arXiv:2209.13891 — Eq. (2.6) tail PDF; §§2,4
  β↔A_g calibration (0.255 ratio) and diagrammatic GW (0.065 reduction).
- Kohri & Terada, PRD 97, 123532 (2018) — induced-GW coefficient 0.822.
- LIGO/Virgo/KAGRA O3 isotropic stochastic search — Ω_GW,0 ≲ 5×10⁻⁹.
