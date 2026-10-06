# Q1: Glitch avalanche universality test

**Status:** exploratory / observational analysis. NOT a detection claim. Date: 2026-09-24.
**Question:** do pulsar glitch statistics (quantum vortex avalanches in a neutron star)
match avalanche statistics seen elsewhere — laboratory quantum turbulence, other
astrophysical avalanches, and self-organized-criticality (SOC) benchmarks?
**Answer in one line:** the avalanche-class glitchers sit in the same exponent band
(α ≈ 1.2–2.0) as earthquakes, solar flares, magnetar bursts, sandpiles, and
Gross–Pitaevskii vortex-avalanche simulations — but that band is generic to
slowly-driven threshold systems, and a second glitcher class (Vela-like,
quasiperiodic) is not scale-free at all.

---

## 1. Data

- **Jodrell Bank glitch catalogue**, snapshot fetched 2026-09-24 from
  `http://www.jb.man.ac.uk/pulsar/glitches/gTable.html`
  (table page for Basu et al. 2022, MNRAS 510, 4049).
  Snapshot: **728 glitches in 224 pulsars** (up from ~670/208 in Basu et al. 2022).
  Columns used: pulsar J-name, glitch number, epoch (MJD), Δν/ν (catalogue units
  1e-9; all numbers below converted to dimensionless Δν/ν).
- **1E 2259+586 glitch #5** (MJD 54880.0, Δν/ν = −1.4×10⁻⁸) is the published
  **anti-glitch** (Archibald et al. 2013, Nature 497, 591) — a magnetar phenomenon
  with different physics. Excluded from the (positive) size fits; counted separately.
- No ATNF cross-match was needed: Δν/ν and epochs come straight from the catalogue.
- Raw parse: `q1_work/glitch_catalog.csv`; fit outputs: `q1_work/fit_results2.json`;
  scripts: `q1_work/analyze.py`, `q1_work/analyze2.py`.

## 2. Methods (no log-log regression)

Power-law PDF p(x) ∝ x^(−α), x ≥ xmin, fitted by **maximum likelihood**
(Clauset–Shalizi–Newman): α = 1 + n/ln-sum, σ = (α−1)/√n, xmin chosen by
minimum Kolmogorov–Smirnov distance. Implemented independently, then
**cross-checked with the `powerlaw` package (v2.0.0)** — the two agree wherever
the distribution is genuinely scale-free (see §3). `powerlaw`'s
`distribution_compare` gives the log-likelihood ratio R (power law vs
lognormal / vs exponential; R > 0 favors the power law) with a significance p.
Waiting times tested against an exponential (Poisson process) with a KS test
(`scipy.stats.kstest`, exact p-values). Only pulsars with n ≥ 10 glitches are
fitted individually — 9 pulsars qualify.

## 3. Results: glitch size exponents (this work)

| Pulsar | n | α (own MLE) | α (`powerlaw`) | xmin (Δν/ν) | R: PL vs lognormal (p) | Waiting times vs Poisson |
|---|---|---|---|---|---|---|
| B1046-58 | 12 | 1.20 ± 0.06 | 1.20 ± 0.06 | 9.1e-10 | −1.17 (0.24) | p = 0.82 ✓ |
| B1758-23 | 15 | 1.28 ± 0.07 | 1.28 ± 0.07 | 1.7e-09 | −1.33 (0.18) | p = 0.40 ✓ |
| J0631+1036 | 17 | 1.35 ± 0.10 | 1.38 ± 0.10 | 1.1e-09 | −0.31 (0.76) | p = 0.50 ✓ |
| B1338-62 | 33 | 1.56 ± 0.12 | 1.56 ± 0.12 | 9.6e-08 | −1.71 (0.09) | **p = 0.017 ✗ (quasiperiodic)** |
| B0531+21 (Crab) | 32 | 1.61 ± 0.11 | 1.61 ± 0.11 | 1.7e-09 | −0.57 (0.57) | p = 0.32 ✓ |
| J1413-6141 | 14 | 1.88 ± 0.28 | 1.88 ± 0.28 | 2.0e-07 | −0.51 (0.61) | p = 0.18 ✓ |
| B1737-30 | 38 | 1.98 ± 0.31 | 1.33 ± 0.06 | xmin-sensitive | −1.47 (0.14) | p = 0.38 ✓ |
| B0833-45 (Vela) | 26 | 5.70 ± 1.26† | 2.66 ± 0.38† | xmin-sensitive | **−1.98 (0.05) lognormal favored** | **p = 0.005 ✗ (quasiperiodic)** |
| J0537-6910 | 65 | 6.26 ± 1.36† | 2.22 ± 0.17† | xmin-sensitive | **−2.34 (0.02) lognormal favored** | **p = 0.010 ✗ (quasiperiodic)** |

† For Vela and J0537 the "exponent" is **xmin-dependent and not a real
measurement of scale-free behavior**: the two fitters pick different xmin and
disagree. The distributions are narrow/peaked (preferred size), and lognormal
is favored over power law. These two are the quasiperiodic class, as in
Melatos et al. 2008.

**Two classes, confirmed on current data:**
- **Avalanche class** (7 pulsars): α ≈ 1.2–2.0, waiting times consistent with
  Poisson (exponential not rejected). The hallmark SOC signature:
  power-law sizes + exponential waits.
- **Quasiperiodic class** (Vela, J0537-6910; B1338-62 marginal on waiting
  times): peaked sizes, regular waits (CV ≈ 0.55–0.57 < 1). Different dynamical
  regime — rapid driving / whole-reservoir discharge ("snowplow"), not
  avalanches.

**Aggregate distribution is bimodal** — 376 glitches below Δν/ν = 10⁻⁷, 349 at
or above; histogram peaks near 2×10⁻⁶ (giant-glitch bump) and 1.6×10⁻⁹
(small-glitch bump). A single power law over the aggregate is the wrong model
(cf. Espinoza et al. 2011); the per-pulsar fits above are the correct unit of
analysis. (For reference only, MLE on the giant tail: α = 2.52 ± 0.27,
xmin = 4.8×10⁻⁶, n = 31 — descriptive, not a model claim.)

## 4. Comparison systems (literature, same α convention: PDF ∝ x^(−α))

| System | Observable | α (PDF) | Source |
|---|---|---|---|
| Pulsar glitches, avalanche class (this work) | Δν/ν | **1.20–1.98** | JBO catalogue, MLE, 2026-09-24 |
| Pulsar glitches (literature range) | Δν/ν | 0.4–2.4 | Melatos et al. 2008, ApJ 672; Fulgenzi et al. 2017 |
| GP vortex-avalanche simulations | simulated Δν/ν | power-law-like over ~1.5 dex | Warszawski & Melatos 2011 |
| GPPE self-gravitating superfluid | ΔJ_c/J_c0 (cumulative β=0.86±0.15) | **≈1.86 ± 0.15** | Verma/Shukla 2024–25 |
| Earthquakes (Gutenberg–Richter, b≈1) | seismic energy | **≈1.67** (= 1 + 2b/3) | standard |
| Solar flares | energy / fluence | **1.7–2.0** | Hudson 2010; Aschwanden (GOES: 2.03 fluence, 1.88 bkg-sub) |
| Magnetar bursts (SGR 1900+14, 1806-20) | burst energy dN/dE | **1.6–1.7** | Göğüş et al. 1999, 2000; Collazzi et al. 2012 |
| BTW sandpile (2D) | avalanche size | **≈1.20** | Sci. Rep. review (2021), citing numerical results |
| Lab superfluid-⁴He vortex avalanches | — | **no published exponent in comparable form** | data gap (see §5) |

## 5. Verdict on universality — honest version

**What matches:** the seven avalanche-class glitchers (α = 1.20–1.98) land
squarely in the band occupied by earthquakes (1.67), solar flares (1.7–2.0),
magnetar bursts (1.6–1.7), the BTW sandpile (1.20), and — most relevantly —
Gross–Pitaevskii simulations of quantum vortex avalanches (power-law-like;
GPPE gives 1.86 ± 0.15). The SOC signature (power-law sizes + Poisson waits)
holds for 6 of 9 well-sampled pulsars. This reproduces and extends the
Melatos et al. 2008 result on an up-to-date catalogue.

**What does NOT follow:**
1. **The band is generic.** α ≈ 1.2–2.0 is what almost any slowly-driven
   threshold system produces. Matching it does not fingerprint *quantum
   vortices* specifically — it fingerprints avalanches. A stronger,
   vortex-specific test needs a second statistic (this is Q3's job:
   dimensionless vortex-regime numbers).
2. **Power law vs lognormal is undecided.** For every avalanche-class pulsar,
   R favors neither model significantly (p = 0.09–0.76). The data are
   *consistent with* a power law; they do not *require* it. Small n is the
   binding constraint (12–38 events per pulsar).
3. **The quasiperiodic class breaks universality.** Vela and J0537-6910 are
   not scale-free; they sit in a different dynamical regime. Any
   vortex-based vacuum model must explain *both* regimes, not just the
   convenient one.
4. **The "lab" arm is thin.** There is no published laboratory
   superfluid-⁴He vortex-avalanche size exponent in directly comparable form
   (lab quantum-turbulence work reports Kolmogorov −5/3 energy spectra — a
   different statistic). The quantum-vortex comparison currently runs through
   GP *simulations*, which span only ~1.5 decades of size versus ~4 decades
   for the Crab. This is a genuine gap, not a confirmation.
5. **xmin sensitivity** (B1737-30: 1.33 vs 1.98; Vela/J0537: method-dependent)
   shows single-number exponents are fragile where distributions curve or are
   narrow. Uncertainties quoted are statistical only.

**Bottom line for the superfluid-vacuum question:** Jase's instinct is
half-right. The *number* that recurs across the universe is the avalanche
exponent α ≈ 1.2–2.0 — neutron-star vortex avalanches share it with
earthquakes, solar flares, magnetar bursts, sandpiles, and simulated quantum
vortices. That is a real universality signal for the *avalanche mechanism*.
It is not, by itself, evidence that the vacuum is a superfluid: the exponent
doesn't know what the vortices are made of. The value of this result for any
vortex-invoking vacuum model is as a **constraint** — its vortex statistics
must land in this band and must also produce the quasiperiodic regime — not
as a confirmation.

## 6. Next steps

- **Q2** (empirical mutual-friction compilation) is unaffected and still the
  highest-value follow-up: it yields numbers no other system provides.
- **Q3** (dimensionless vortex-regime comparison) is now better motivated:
  the exponent match says "same avalanche class"; Q3 asks "same vortex
  physics?" — the sharper question.
- If the quasiperiodic class is ever to be modeled, B1338-62's newly
  quasiperiodic waiting times (p = 0.017) deserve a dedicated look — it may
  be transitioning between regimes.
