# Mutual friction in neutron stars: an empirical B compilation (Q2)

**Date:** 2026-09-25 · **Status:** completed-toy (compilation + reproducible calculation; no new fits)
**Prerequisites:** `study_note.md`, `glitch_universality_note.md`
**Data products:** `q2_work/dong105_tau.csv` (105 pulsars), `q2_work/dong5_glitch.csv` (11 glitch events),
`q2_work/parse_dong.py` (reproducible parser), `q2_work/dong2026.pdf` + `q2_work/eprint/` (source paper)

---

## Lay summary

A neutron star is (in the simplest working picture) two things spinning together: a solid crust and a
superfluid interior, gripping each other through friction between the superfluid's quantum vortices and
the star's charged particles. The strength of that grip is summed up in one dimensionless number, **B**,
the mutual-friction parameter. Microphysical theory says B should be around 10⁻⁴ (from electrons
scattering off vortices).

I compiled every published handle on B I could defend, and the honest result is a split picture:

- **Slow recoveries (days to years after glitches, 11 events in 5 pulsars + timing-noise coupling in
  105 pulsars):** effective B comes out at **10⁻¹⁰ to 10⁻⁶** — thousands to millions of times *weaker*
  than theory predicts. These slow timescales are evidently not clean measurements of microscopic
  friction; something (vortex pinning, creep, extra internal components) is getting in the way.
- **Fast probes (seconds, from the 2016 Vela glitch rise and overshoot):** B ≳ 6×10⁻⁶, and model fits
  give 3×10⁻⁵–10⁻⁴ for the core — **right where microphysics says it should be**. The fast coupling
  sees the real friction; the slow recoveries see something else.

So the data do not hand us "the" mutual friction of neutron-star matter. They hand us a fast component
consistent with theory and a slow component that theory, as currently applied, cannot explain without
extra ingredients. For the superfluid-vacuum question, the takeaway is negative but useful: pulsar
timing gives us the best *effective* coupling numbers in nature, and they say the textbook
microphysical B is not what the long-timescale observables are measuring.

---

## 1. What B is, and the formulas used

In the HVBK two-fluid picture the force of mutual friction on the superfluid is parameterized by
dimensionless coefficients **B** (dissipative) and **B′** (non-dissipative), with B = R/(1+R²) where R
is the drag-to-lift ratio of a vortex. For electron–vortex scattering in the outer core,
R ≈ 4×10⁻⁴ (Andersson et al. 2006), so **B_mf ≈ 4×10⁻⁴** is the microphysical benchmark used
throughout this note.

The crust–superfluid coupling time associated with mutual friction is (Haskell & Melatos 2015;
Montoli et al. 2020; Dong et al. 2026, eqs. 28–29)

    τ_mf = 1 / (2 Ω_c B_mf)  =  1.25×10³ s · (Ω_c/1 rad s⁻¹)⁻¹ · (B_mf/4×10⁻⁴)⁻¹.

In the classic two-component glitch model (Baym et al. 1969; Alpar et al. 1993; Dong et al. 2026,
App. C) the observed post-glitch exponential recovery time τ_g obeys

    τ_g⁻¹ = (1 + I_s/I_c) τ_s⁻¹,      q_heal = Δν_d/Δν_g ≈ I_s/(I_s+I_c),

so that τ_s = τ_g/(1−q_heal) and

    **B_mf = (1 − q_heal) / (2πν τ_g)**        (glitch recovery → B)

with ν the spin frequency. Where only a timescale τ is published (no q_heal), I quote

    **B_eff = 1 / (2πν τ)**                      (timescale only → B)

and state explicitly what it assumes. Every entry below is one of: (a) a direct model fit to B,
(b) an inferred B under a stated two-fluid formula, or (c) a timescale only. Nothing here is a
*direct measurement* of the microphysical B — that number has never been measured; it is always
inferred through a model.

## 2. Method and sources

- **Core dataset:** Dong et al. 2026, MNRAS 545, 1–30 (arXiv:2511.15134), "Measuring the
  crust-superfluid coupling time-scale for 105 UTMOST pulsars with a Kalman filter." I downloaded
  the arXiv e-print source and parsed its LaTeX tables machine-readably (`papertabs/`), cross-checked
  the parsed counts against the paper text (105 two-component candidates, 28 sharply-peaked τ
  posteriors — both match), and took spin frequencies from the ATNF psrcat v2.8.1 database
  (4393 pulsars; every one of the 105 matched). Parser: `parse_dong.py`.
- **Glitch-recovery table:** the paper's Table "tau_comparison_with_glitch_recovery"
  (`glitched_pulsars.tex`): 11 glitch events with resolved τ_g and literature q_heal in
  5 pulsars (J1048−5832, J1141−6545, J1452−6036, J1803−2137, J1833−0827), with per-event
  references (Wang et al. 2000; Manchester et al. 2010; Espinoza et al. 2011; Yu et al. 2013;
  Lower et al. 2021).
- **Literature B values / timescales:** Ashton et al. 2019 (Vela 2016 rise + overshoot);
  Graber et al. 2018 (Vela 2016 rise-shape fits); Haskell & Antonopoulou 2013 (Vela glitch fits);
  Lyne et al. 2015 (Crab); Dodson et al. (Vela 1999 small glitch); Weltevrede et al. 2011
  (J1119−6127); Yuan et al. 2017 (J1757−2421 three components, via Dong et al.).
- The JBO glitch catalog (`q1_work/glitch_catalog.csv`) carries glitch sizes and epochs but **no
  recovery timescales**, so it could not be used for B; published recovery fits were used instead.

## 3. Results

### Table A — B_mf from resolved glitch recoveries (Dong et al. 2026 compilation, 11 events)

B_mf = (1−q_heal)/(2πντ_g). Uncertainties on τ_g, q_heal are in the CSV; τ_g values are medians.

| Pulsar | Glitch epoch (MJD) | τ_g | q_heal | log₁₀ B_mf | Ref |
|---|---|---|---|---|---|
| J1048−5832 | 49034(9) | 146 d | 0.025 | −8.82 | Wang+2000 |
| J1048−5832 | 50788(3) | 58 d | 0.0079 | −8.41 | Wang+2000 |
| J1048−5832 | 56756(4) | 46 d | 0.0040 | −8.31 | Lower+2021 |
| J1141−6545 | 54277(20) | 461 d | 0.0040 | −8.81 | Manchester+2010 |
| J1452−6036 | 55055.22(4) | 2309 d | 0.12 | −9.96 | Lower+2021 |
| J1803−2137 | 48245(11) | 146 d | 0.013 | −8.78 | Espinoza+2011 |
| J1803−2137 | 50777(4) | 12 d | 0.010 | −7.68 | Espinoza+2011/Yu+2013 |
| J1803−2137 | 50777(4) | 73 d | 0.0032 | −8.47 | Yu+2013 |
| J1803−2137 | 53429(1) | 146 d | 0.0063 | −8.78 | Espinoza+2011/Yu+2013 |
| J1803−2137 | 55775(2) | 37 d | 0.0079 | −8.18 | Lower+2021 |
| J1833−0827 | 48051(4) | 183 d | 0.0010 | −9.07 | Espinoza+2011 |

Range: **B_mf ≈ 10⁻¹⁰–10⁻⁷.⁷**. All 2–4 orders of magnitude below the microphysical 4×10⁻⁴.
Note the paper's own finding: the timing-noise-based x_s = (1+τ_c/τ_s)⁻¹ ≈ 1 while q_heal ≲ 0.1 —
the relation q_heal ≈ x_s predicted by the two-component model is **violated**, implying extra
angular-momentum reservoirs participate in glitches (Dong et al. §6.3). The B values above inherit
that model tension.

### Table B — B_eff upper bounds from timing-noise coupling times (105 pulsars)

For the 105 UTMOST pulsars favoring the two-component model (ln BF ≥ 5), the Kalman filter measures
the composite coupling time τ = (1/τ_c + 1/τ_s)⁻¹. Since τ ≤ τ_s always, **B_eff = 1/(2πντ) is an
upper bound** on the mutual-friction B (pinning ignored). Full per-pulsar values in
`dong105_tau.csv`.

- All 105: log₁₀ B_eff ∈ **[−9.87, −5.88]**
- 28 with sharply peaked τ posteriors: log₁₀ B_eff ∈ **[−8.85, −6.46]**
- Population scaling (hierarchical): τ ∝ Ω_c^0.19±0.5 |Ω̇_c|^0.18±0.18 — i.e. no strong spin dependence.

Dong et al. note the tension explicitly: for a typical UTMOST pulsar the microphysical prediction
gives τ_mf ~ 10³ s, while measured τ ~ 10⁴.⁶–10⁸.⁶ s — **four-plus orders of magnitude slower**.
Their suggested resolution: vortex pinning (τ_mf → ∞ as B_mf → 0 under perfect pinning), i.e. the
measured coupling is the *pinned* effective value, not the microscopic one.

### Table C — literature B values and timescales

| Source | B (or timescale → B_eff) | Kind |
|---|---|---|
| Vela 2016 rise, Ashton+2019 (Nature Astron. 3, 1143) | **B ≳ 5.7×10⁻⁶** (log −5.24) | lower bound; 2-fluid, τ_r ≤ 12.6 s (90%) |
| Vela 2016 overshoot, Ashton+2019 | τ_d = 54 s → B_eff ≈ 2.6×10⁻⁴ (log −3.58) | timescale only; naive conversion, model-dependent |
| Vela 2016 rise shape, Graber+2018 (ApJ 865) | **3×10⁻⁵ ≲ B_core ≲ 10⁻⁴**; crust B ≳ 10⁻³ | 3-component fit; core range matches microphysics |
| Vela 2004, Newton+2015 via Dong+2026 | B_mf = 4×10⁻⁵ | quoted second-hand; primary not re-verified here |
| Vela glitch fits, Haskell & Antonopoulou 2013 | B̃_gl = 10⁻³ | effective model input, not a fit result |
| J1757−2421, Yuan+2017 (3 components) | 10⁻⁷.⁵⁴ / 10⁻⁸.³⁶ / 10⁻⁹.¹⁹ (τ_g = 15/98/672 d) | timescale-only upper bounds |
| Crab, Lyne+2015 | τ = 320±20 d → B_eff ≈ 1.9×10⁻¹⁰ | slow component (46% of Δν̇); not prompt friction |
| Vela 1999 small glitch, Dodson+ | τ_d = 31±1 d → B_eff ≈ 5×10⁻⁹ | slow component |
| J1119−6127 2004, Weltevrede+2011 | ~3 months → B_eff ≈ 8×10⁻⁹ | slow component |
| Theory: e–vortex scattering (Andersson+2006) | ~10⁻⁴ | microphysical prediction |
| Theory: crust phonon scattering | ~10⁻¹⁰ | microphysical prediction |
| Theory: Kelvin-wave damping (rapid) | ~10⁻² | microphysical prediction |

### The split picture

- **Fast (seconds):** Vela 2016 rise (B ≳ 5.7×10⁻⁶) and rise-shape fits (B_core ~ 3×10⁻⁵–10⁻⁴)
  are **consistent with the microphysical 10⁻⁴**. The rapid core coupling sees something close to
  textbook mutual friction.
- **Slow (days–years):** every recovery-derived or timing-noise-derived effective B
  (10⁻¹⁰–10⁻⁶) sits far below it. These slow timescales cannot be the microscopic mutual-friction
  time; they must be set by pinning/creep/repinning dynamics or multi-component exchange — or,
  equivalently, the "B" they imply is the *pinned* effective value.

## 4. Coverage and omissions (honest accounting)

- **Done:** 11 glitch events with full (τ_g, q_heal, ν) → B_mf in 5 pulsars (Table A); 105 pulsars
  with τ → B_eff upper bounds (Table B, full CSV); 9 literature anchor points (Table C); spin
  frequencies from psrcat for every pulsar (no guessed values).
- **The "~31 pulsars with measured recoveries" target was not reachable as stated.** The JBO
  catalog has no recovery timescales. The largest *published, per-event* resolved-recovery
  compilation I could verify is the 11 events / 5 pulsars in Dong et al. 2026, plus 4 more
  pulsars with ATNF-listed τ_g but no two-component fit (J1123−6259, J1757−2421, J1841−0425,
  J1852−0635; τ_g = 15–840 d — only J1757−2421's three components converted here). The rest of
  the "~31" have published glitch sizes but no published exponential-recovery fits I could locate;
  I did not manufacture B values for them.
- **Skipped:** per-pulsar refits of published Δν(t) curves (would need digitizing light curves from
  papers — weeks of work, marginal gain); the Vela "G1" vortex-bending oscillation paper (different
  phenomenon: bending-mode damping, τ = 266±8 d, not mutual friction); re-verifying Newton et al.
  2015's B_mf = 4×10⁻⁵ at the primary source (cited via Dong et al.; flagged).
- **Key caveat repeated:** no entry is a direct measurement of microphysical B. Entries labeled
  "slow component" (Crab, Vela 1999, J1119−6127) probe crustal creep/repinning, not prompt mutual
  friction, and should not be compared numerically with the Vela-2016 fast probes.

## 5. Lab hunt: superfluid-helium / BEC vortex-avalanche exponent

**Verdict: still missing.** No published event-resolved vortex-avalanche size exponent exists for
superfluid helium or BECs as of this search (2026-09-25). What the lab literature does contain:

- **Superconducting vortex avalanches** (the closest laboratory analog — pinned quantized
  vortices): Altshuler et al. 2002, Nb foil, ~200,000 events: P(s) ∝ s^−τ, **τ = 3.0±0.2**;
  Aegerter et al. 2003, YBCO film: τ ≈ 1.3; Behnia et al. 2000, Nb film: τ ≈ 2.05;
  Radovan & Zieve 2003, Pb film: τ ≈ 1.1–2.0; Josephson-junction avalanches: exponent ~1.
  I.e. lab vortex avalanches show power laws, but the exponent is **not universal** (1.1–3.0
  depending on material, geometry, temperature) — it overlaps the pulsar glitch range
  (1.2–2.0) the way earthquakes and solar flares do: generic SOC, not a vortex fingerprint.
- **Superfluid helium proper:** only indirect statistics — Kolmogorov k^−5/3 incompressible-energy
  spectra (Nore et al.; verified in BEC by Navon et al., Nature 2016), and v^−3 velocity tails at
  reconnection events (Paoletti et al. 2008). Neither is an avalanche-size distribution.
- **What would be needed:** event-resolved vortex-depinning/avalanche catalogs in rotating
  superfluid He or BECs (e.g. from vortex-line-density jump statistics or direct imaging),
  binned the same way as the JBO glitch sizes, to fit a size exponent α for direct comparison
  with the seven avalanche-class pulsars (α ≈ 1.20–1.98).

This closes the Q1 open gap as a *negative result with a specified experiment*, not as a found number.

## 6. Relevance to superfluid-vacuum ideas (plain language)

The honest relevance is thin but real. Pulsar timing gives the only *empirical* numbers for how
strongly a macroscopic superfluid grips its container — effective B ~ 10⁻¹⁰–10⁻⁶ on slow
timescales, ~10⁻⁵–10⁻⁴ on fast ones, versus 10⁻⁴ predicted. If the vacuum were a superfluid whose
vortices behave like neutron-star vortices, these numbers would be the calibration set — but
nothing in them points at the vacuum; they point at vortex pinning inside neutron stars, a
thoroughly conventional (if unsolved) condensed-matter problem. The Q1 avalanche-exponent overlap
with earthquakes/flares/sandpiles plus the non-universal lab vortex-avalanche exponents (1.1–3.0)
further weaken any "specifically quantum-vortex" reading of the glitch statistics. Kept as:
**observational** (numbers are real), not evidential for a superfluid vacuum.

## 7. Files

- `~/workspace/superfluid-vacuum/mutual_friction_note.md` — this note
- `~/workspace/superfluid-vacuum/q2_work/dong105_tau.csv` — 105 pulsars: τ, B_eff upper bound, F0, peaky flag
- `~/workspace/superfluid-vacuum/q2_work/dong5_glitch.csv` — 11 glitch events: τ_g, q_heal, B_mf, refs
- `~/workspace/superfluid-vacuum/q2_work/parse_dong.py` — reproducible parser (LaTeX → CSV)
- `~/workspace/superfluid-vacuum/q2_work/dong2026.pdf`, `q2_work/eprint/` — source paper + arXiv source
- `~/workspace/superfluid-vacuum/q2_work/psrcat_tar/psrcat.db` — ATNF catalog v2.8.1 (F0 source)
