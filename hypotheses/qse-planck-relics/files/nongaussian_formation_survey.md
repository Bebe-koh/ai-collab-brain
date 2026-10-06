# Non-Gaussian PBH Formation for QSE: Literature Survey

**Date:** 2026-10-03
**Status:** Literature survey only — no new calculations, nothing validated.
**Parent context:** `briefing_bearing_assessment.md` (2026-09-25). Gaussian formation is ruled out:
LIGO/Virgo/KAGRA stochastic bound (Ω_GW ≲ 5×10⁻⁹, O3) excludes the Gaussian-induced
GW background by factors ~10–1000. Non-Gaussianity is the remaining channel.

## 1. Framework numbers (from briefing + Trivedi & Loeb)

| Quantity | Value | Source |
|---|---|---|
| β target, low-mass end | ≈ 2×10⁻¹⁹ at M ~ 10⁹ kg | briefing |
| β target, high-mass end | ≈ 1.5×10⁻¹² at M ~ 6×10²² kg | briefing |
| β, T&L illustrative | ~ 10⁻⁵ | Trivedi & Loeb, arXiv:2509.20533 |
| Gaussian requirement | P_R(k_c) ≈ 5.6×10⁻² → Ω_GW^peak ~ 10⁻⁷–10⁻⁶ at f ~ 100–1000 Hz | T&L |
| LIGO O3 stochastic bound | Ω_GW ≲ 5×10⁻⁹ | LIGO/Virgo/KAGRA |
| Gaussian fine-tuning | 1% amplitude shift → 50–80% abundance shift | briefing |

**Why NG helps (general argument):** the binding signal is second-order scalar-induced GWs
from the formation-era curvature bump, Ω_GW ∝ P_R². Non-Gaussian heavy tails let the same
collapse fraction β be reached at much lower P_R, suppressing the GWs. T&L quantify the
escape route in-paper: heavy-tailed NG (lognormal with shift d₀~σ, or power-law tail α~5)
reaches β~10⁻⁵ with P_R ~ 10⁻³ instead of 5.6×10⁻², pushing induced GWs below the bound.

**Critical cross-cutting result:** NG barely changes the induced-GW physics itself.
Abe et al. (arXiv:2209.13891) compute the GW spectrum with full non-perturbative
exponential-tail NG via the diagrammatic approach: the leading "vanilla" O(A_g²) term
dominates, NG corrections are subdominant, and at fixed abundance the GW amplitude is
*slightly lower* than Gaussian. The suppression comes from the reduced P_R, not from
NG modifying the GW emission. (Consistent with the review arXiv:2404.06151: NG
"mildly" affects induced GWs.)

## 2. Mechanism-by-mechanism verdict table

| # | Mechanism | β(M) prediction | Survives LIGO bound? | Fine-tuning | Verdict |
|---|---|---|---|---|---|
| A | Perturbative local f_NL (Edgeworth) | Unreliable at required enhancement | N/A | N/A | **Not a solution.** f_NL>0 helps qualitatively, but the needed boost breaks perturbation theory. Qualitative sign only. |
| B | Curvaton, exact non-perturbative PDF | β_tot ≈ ½ erfc(1.97/(σ₀√r)) for r≲0.1; tunable to any β target | **Marginal at β~10⁻⁵** (floor Ω_GW~2×10⁻⁹, bound 5×10⁻⁹); **comfortable at briefing targets** (floor ~10⁻¹¹–10⁻¹²) | Exponential sensitivity in σ₀√r (similar to Gaussian) + model-building tuning (peaked spectator spectrum, small r_dec) | **Strongest concrete candidate.** Exact PDF, quantified GW floor. Floor exists but sits below bound for QSE targets. |
| C | Ultra-slow-roll / non-attractor exponential tail | P(ζ) ∝ e^{−3ζ}; required A_g reduced ~4× vs Gaussian (Abe et al.: 5.17→1.32×10⁻³ for f_PBH=1) | **Marginal at β~10⁻⁵** (Ω_GW ~10⁻⁹–10⁻⁸, touches bound); **OK at briefing targets** (~10⁻¹⁰) | Milder A_g sensitivity than Gaussian per Abe et al.; but inflection-point potential tuning | **Co-strongest candidate.** Best-quantified β↔GW mapping in the literature. Tail slope Λ=3 is model-dependent; heavier tails do better. |
| D | Stochastic inflation / quantum diffusion (general) | Exponential to super-exponential tails depending on potential (stochastic-δN) | Not quantified for relic-DM case | Potential-shape tuning | **Promising, unquantified.** No end-to-end β+GW calculation at QSE targets. Gap. |
| E | Modulated reheating | No direct PBH-abundance calculation in literature | N/A | N/A | **Disfavored.** Typically gives near-scale-invariant ζ, not the required narrow bump. Gap recorded. |
| F | Multi-field / hybrid waterfall, tachyonic instability | Exponential tails possible (Zhang & Huang); ρ correlation matters | Not quantified | Narrow-spectrum requirement | **Qualitative support only.** Gap. |

*Estimates in §3–4 marked [EST] are my back-of-envelope mappings of published formulas to
QSE β targets — not published numbers.*

## 3. Curvaton (mechanisms B) — detail

**Exact PDF (Farooq et al., arXiv:2509.10851):** sudden-decay mapping gives the full
non-perturbative PDF of ζ. Non-linearity parameter f_NL ≈ 5/(4r_dec) − 5/3 − 5r_dec/6 —
large and positive for small curvaton decay fraction. For Ω_χ,dec ≲ 0.1 the tail boosts β
by many orders of magnitude vs Gaussian and the required variance drops drastically.
Perturbative Edgeworth f_NL fails in exactly this regime (valid only when S_n σ^{n−2} ≪ 1).

**Induced GWs + the floor (Pi & Sasaki, arXiv:2112.12680):** non-minimal curvaton
(non-trivial field metric → peaked spectator spectrum), quadratic local NG
ζ ≈ ζ_g + F_NL(ζ_g² − ⟨ζ_g²⟩) with F_NL = 3/(4r), arbitrarily large as r→0.
Key structural result: for r ≲ 0.1 both β_tot and σ_ζ² depend only on the combination
σ₀√r, so **as r→0 (F_NL→∞) the induced GW levels off to a nonzero floor**:

Ω_GW^floor ~ 10⁻⁶ σ_ζ⁴ ~ 10⁻⁶ × (4/81)(σ₀√r)⁸

(Their asteroid-mass example: floor 2.95×10⁻¹¹ at f_* = 6.7×10⁻³ Hz — a *lower bound*,
well above LISA sensitivity, i.e. still detectable but that band is not LIGO-constrained.)

**[EST] Mapping to QSE β targets** (using their Eqs. 28, 32; narrow-peak, threshold
assumed comparable — extrapolation flagged):

| β target | σ₀√r | Ω_GW floor (end-to-end) | vs O3 95% (5.8×10⁻⁹) | threshold span T∈[0.87, 2.61] |
|---|---|---|---|---|
| 10⁻⁵ (T&L) | 0.6532 | 1.64×10⁻⁹ | 3.5× below — marginal | 10.8× below → excluded (flips at +17%) |
| 1.5×10⁻¹² (briefing top) | 0.3993 | 3.19×10⁻¹¹ | 182× below (threshold caveat: fails for Δ_cr≳0.44) | 554× below → excluded |
| 2×10⁻¹⁹ (briefing bottom) | 0.3117 | 4.40×10⁻¹² | 1317× below (robust) | 4012× below → excluded only at extreme edge |

**Fine-tuning:** d ln β / d ln(σ₀√r) ≈ 2x² ~ 18 at β=10⁻⁵ — exponential sensitivity in the
combination, comparable to Gaussian. The extra cost is model-building: a sharp dip in the
spectator kinetic coupling f(φ) to place a narrow peak (Σ ≲ 0.1) at k_* matching
T_f ~ 10⁹–10¹¹ GeV, plus r_dec ≲ 0.1 (curvaton subdominant at decay — must be reconciled
with CMB-scale constraints, which the peaked spectrum evades by construction).

## 4. Ultra-slow-roll exponential tail (mechanism C) — detail

**The tail (standard USR δN result):** ζ = −(1/3)ln(1−3ζ_g), so
P(ζ) = e^{−3ζ} P_g(ζ_g(ζ)) — exponential, not Gaussian, at ζ ≳ 1. The decay rate
Λ ≡ −d ln P/dζ (= 3 here) is model-dependent; heavier tails (Λ→0) exist in the
literature.

**Abundance (Kitajima et al., arXiv:2109.00791):** peak theory with critical collapse
and averaged compaction function. Exponential tail enhances β enormously — confirmed
even against the corresponding perturbative f_NL = 5/2. Bonus: the PBH mass spectrum
gets a characteristic maximal mass not seen in Press–Schechter.

**Induced GWs (Abe, Inui, Tada, Yokoyama, arXiv:2209.13891):** full diagrammatic
calculation to O(A_g⁴) with the non-perturbative tail. Findings:
- Required Gaussian-part amplitude drops: A_g = 5.17×10⁻³ (Gaussian) → 1.32×10⁻³
  (exponential tail) for f_PBH = 1 at M ~ 10²² g.
- GW amplitude reduced by (1.32/5.17)² ≈ 0.065 vs Gaussian. Still LISA-detectable
  (in their band), but the mechanism of suppression is the lower A_g.
- Leading vanilla diagram dominates; NG corrections to the GW spectrum proper are
  subdominant (one appears only on the high-frequency side, below LISA sensitivity).
- **Fine-tuning note:** "the perturbation amplitude A_g and hence the GW amplitude are
  really insensitive to the small change of f_PBH" — milder tuning than Gaussian.

**[EST] Mapping to QSE β targets** (USR tail Λ=3, ζ_c~1; Gaussian Ω_GW scaled as P_R²
from T&L's 10⁻⁷–10⁻⁶ at P_R=5.6×10⁻²):

| β target | Tail A_g (ζ_c=1, end-to-end) | Ω_GW (end-to-end) | vs O3 95% (5.8×10⁻⁹) | ζ_c∈[0.5, 1.3] span |
|---|---|---|---|---|
| 10⁻⁵ (T&L) | 5.80×10⁻³ | 2.56×10⁻⁹ | 2.3× below — marginal | 5.6× → 1.7× below |
| 1.5×10⁻¹² (briefing top) | 2.07×10⁻³ | 3.24×10⁻¹⁰ | 17.9× below (formal; no in-band bound — BBN integral bound 6787× below) | 40× → 15× below |
| 2×10⁻¹⁹ (briefing bottom) | 1.26×10⁻³ | 1.20×10⁻¹⁰ | 48× below | 108× → 42× below |

**Caveats:** USR needs an extremely flat inflection-point segment tuned to put the peak
at the right scale with the right amplitude; the Λ=3 slope is specific to the minimal
USR exit model. The ζ_g ≥ 1/3 region maps to eternally-inflating baby universes and is
excised by hand (noted in Abe et al.). Non-attractor positive-f_NL results
(Firouzjahi & Riotto, arXiv:2309.10536) point the same direction but are perturbative —
the USR tail is their non-perturbative completion.

## 5. Why perturbative f_NL alone fails (mechanism A)

Edgeworth estimate: ln β_NG ≈ ln β_G + (ζ_c³/6σ³)·S_3 with S_3 ~ (18/5)f_NL·σ.
At σ ~ 0.02, ζ_c ~ 1: the correction coefficient is ~(10⁵/6)·0.07·f_NL ~ 10³·f_NL.
Reaching β ~ 10⁻⁵ from a Gaussian β_G ~ 10⁻¹⁰⁰ needs Δlnβ ~ 200+ — the "correction"
dwarfs the leading term, i.e. the expansion has broken down. Positive f_NL is a
reliable *sign* (helps), never a *number* here. Any paper quoting a perturbative
f_NL as the solution to the QSE abundance should be treated as qualitative only.

## 6. Gaps (honest)

1. **No end-to-end NG calculation for the Planck-relic DM case exists.** T&L
   (arXiv:2509.20533, Sep 2025; published Phys. Dark Univ. Dec 2025) is recent; no
   follow-up applying curvaton/USR/stochastic NG specifically to relic-DM β targets
   with the LIGO bound was found. All numbers above are mappings, not validations.
2. **Frequency-band extrapolation.** The quantitative β↔Ω_GW mappings (Pi & Sasaki,
   Abe et al.) were computed for asteroid-mass windows (mHz, LISA band). The QSE
   formation bump sits at f ~ 100–1000 Hz (LIGO band). The amplitude scaling should
   carry over; the spectral shape details were not re-derived here.
3. **Modulated reheating:** no PBH-abundance calculation found; disfavored on
   spectral-shape grounds (near-scale-invariant, not peaked).
4. **Stochastic-δN:** tail slope Λ is tunable via the potential (Pattison et al.,
   arXiv:2210.03812 — stochastic tunnelling gives exponential to super-exponential
   tails), but nobody has run it to β ~ 10⁻⁵–10⁻¹⁹ + LIGO-bound numbers.
5. **Threshold/collapse systematics:** all β numbers inherit the usual Press–Schechter
   vs peak-theory, window-function, and critical-collapse uncertainties (factors of a
   few in the threshold propagate exponentially into β — the tuning problem in
   another guise).
6. **Bounce-vs-fragmentation fork** remains parked; both inherit these constraints.

## 7. Bottom line

- The literature contains **two fully non-perturbative, quantitatively worked**
  heavy-tail mechanisms — **small-r curvaton** and **USR exponential tail** — that
  provably reach fixed β at much lower P_R, with the induced-GW suppression
  computed (not hand-waved).
- For the **briefing's β targets (10⁻¹⁹–10⁻¹²)** both sit **below the bound
  with margin, now end-to-end** (2026-10-06, `formation_endtoend_note.md`):
  curvaton 182–1317× nominal (robust at 2×10⁻¹⁹; threshold caveat at
  1.5×10⁻¹² for Δ_cr≳0.44); USR 18–48× nominal, 15–108× across ζ_c (the
  1.5×10⁻¹² peak sits at 7 μHz with no direct bound — BBN integral bound is
  the operative constraint, 6787× below). For **T&L's illustrative β ~ 10⁻⁵**
  both are **marginal** (curvaton 3.5×, threshold-flips at +17%; USR 2.3× at
  ζ_c=1, 1.7× at ζ_c=1.3) — confirmed end-to-end; 'marginal' is the verdict.
- There is a **floor**: NG cannot suppress the induced GW arbitrarily (curvaton
  floor as r→0; USR floor set by Λ). The floor is below the LIGO bound for QSE
  targets, but the headroom is thinnest exactly where T&L put their benchmark.
- **Fine-tuning is not eliminated**, only relocated: from Gaussian amplitude tuning
  to tail-shape/model-parameter tuning (peak position, dip in kinetic coupling or
  inflection point, r_dec). The USR tail mildly *reduces* amplitude sensitivity
  (Abe et al.).
- **Nothing is validated.** The single most valuable next step is a dedicated
  end-to-end calculation: pick curvaton-small-r or USR-tail, put the bump at
  T_f ~ 10⁹–10¹¹ GeV, compute β(M) and the induced Ω_GW(f) at 100–1000 Hz against
  the O3 bound for the briefing's β(M) targets.

## 8. Key references

- Trivedi & Loeb, "Gaussian Planck Relics are Ruled-Out as Dark Matter by LIGO,"
  arXiv:2509.20533 (2025); journal: Phys. Dark Univ. 50, 102174.
- Farooq et al., "Primordial black holes from non-Gaussian curvaton perturbations"
  (exact PDF, sudden decay), arXiv:2509.10851 (2025).
- Pi & Sasaki, "Primordial Black Hole Formation in Non-Minimal Curvaton Scenario,"
  arXiv:2112.12680 (2021). — GW floor result.
- Kitajima, Tada, Yokoyama, Yoo, "Primordial black holes in peak theory with a
  non-Gaussian tail," arXiv:2109.00791 (2021). — exponential-tail abundance.
- Abe, Inui, Tada, Yokoyama, "Primordial black holes and gravitational waves induced
  by exponential-tailed perturbations," arXiv:2209.13891 (2022). — induced GW with
  full NG, diagrammatic.
- Firouzjahi & Riotto, arXiv:2309.10536 (2023). — non-attractor f_NL > 0 at the peak.
- Pattison et al., "Primordial black holes from stochastic tunnelling,"
  arXiv:2210.03812 (2022). — stochastic-δN tails.
- Review: arXiv:2404.06151 — NG effects on scalar-induced GWs ("mild").
- Zhang & Huang (ResearchGate) — exponential tails from tachyonic instability in
  multi-component inflation; narrow spectra required.
