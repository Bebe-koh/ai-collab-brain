# Prior-art search: Kerr R(t) blind-spot-free statistic
**Date:** 2026-10-03 · **Question:** has the R(t) construction (calibrator-differential transient polarimetric statistic for a dynamical-pseudoscalar birefringence step, lifting the γ=k/12 blind spot) been published before?
**Search venues:** arXiv (via web search), journal pages (IOP/ApJ), review of EHT polarimetry and VLBI calibration literature. This is a diligence search, not an exhaustive systematic review.

## Paper-by-paper

| # | Paper | What it did | Relation to R(t) |
|---|---|---|---|
| 1 | Chen et al. 2020, PRL 124, 061102 (arXiv:1905.02213) | Proposed EHT polarimetry as axion-cloud probe; signal = periodic EVPA oscillation from superradiant cloud. Theory proposal, no data-analysis method. | No overlap with the statistic. Different signal (oscillation vs one-time step). |
| 2 | Chen et al. 2022, Nature Astron. 6, 592 (arXiv:2105.04572) | M87\* 2017 data; differential EVPA analysis on polarimetric *images* across 4 days; axion-cloud oscillation fit. | Image-domain, not closure quantities. No blind-spot discussion, no calibrator differencing, no transient matched filter. |
| 3 | **Wang & Broderick 2024, ApJ 962, 121** | Axion-cloud constraints via closure traces + conjugate closure trace product (CCTP) on M87\*; MCMC fit of geometric EVPA-wave model. **Closest methodological prior art.** | **Complementary, not overlapping.** Paper states verbatim that CCTP is sensitive *only* to polarization substructure and *invariant* to a total/global EVPA rotation — i.e. closure traces are blind to exactly the global-slip signal R(t) targets. No blind-spot analysis (their signal is periodic, not a step), no calibrator referencing (closure quantities avoid calibrators by design), no transient matched filtering. |
| 4 | Gan, Wang & Xiao 2023, arXiv:2311.02149 | Axion-star EVPA modulation; theoretical sensitivity projections for EHT/ngEHT. | Theory only; no data-analysis method. |
| 5 | Jones et al. 2025, arXiv:2603.03244 | Axion signatures in M87 relativistic-jet polarimetry; morphological diagnostics vs Faraday rotation. | Image-domain; no closure/transient construction. |
| 6 | Broderick & Pesce 2020 | Introduced closure traces. | Already cited in our note as the reason closure traces are blind to the global slip. Foundation, not prior art for R(t). |
| 7 | VLBI polarimetry calibration literature (Martí-Vidal et al. 2016 PolConvert; Park et al. 2021/2023 GPCAL; PolSolve; LPCAL) | Calibrators used for D-term/leakage calibration and absolute EVPA (R–L phase) anchoring. | Standard *calibration* practice, not a differential *detection* statistic. The R–L phase degeneracy itself is textbook knowledge; no published work combines it into a calibrator-differential transient matched filter for birefringence steps. |
| 8 | arXiv:2609.09149, "Differential Polarization Calibration" | Consistency test for CMB cosmic birefringence via relative-calibration networks. | Different domain (CMB maps, not VLBI time series); terminological near-miss only. |

## Element-by-element check (the four search angles)

1. **EHT axion polarimetry (Chen+2022, etc.):** all target *oscillating, spatially-varying* EVPA from axion clouds, analyzed in image domain or via closure traces. None analyzes a global one-time step; none uses calibrator differencing.
2. **R–L degeneracy breaking via calibrator referencing:** the degeneracy is textbook VLBI knowledge, and calibrators are standard for absolute EVPA anchoring — but no paper found constructs a *time-dependent differential* (target÷calibrator) transient statistic for this purpose.
3. **Transient matched filter vs endpoint comparison:** no paper found applies matched filtering to a polarimetric step transient in VLBI/EHT data. All axion searches fit periodic or static models.
4. **|sin(12πγ)|-type blind spot:** not noted in any paper found. It is specific to endpoint-comparison of a *global 2π-periodic step* — a signal morphology no published search targets (published signals are periodic waves or static rotations).

**"Yuan+2024":** could not locate an EHT axion paper by this citation in the searches performed; may be a misreference. Not counted as prior art.

## Verdict

**NOVEL — no prior art found in searched venues** for the specific construction: a calibrator-differential (R = Q_tgt/Q_cal) finite-differenced transient statistic, matched-filtered against the exact nonlinear tanh template, designed to lift the γ=k/12 blind spot of endpoint-comparison closure observables and break the synchronized R–L jump degeneracy.

Closest prior art is Wang & Broderick (2024), and the relationship is complementary: their closure-trace method is *provably blind* to global EVPA rotations (their own text), which is precisely the signal class R(t) is built for. A future paper should cite W&B as the complementary approach and state this division explicitly.

**Caveats on this verdict:** (i) absence of evidence after a diligent web/arXiv search is not proof of absolute novelty — a full ADS/inSPIRE systematic review and a check of radio-astronomy methods literature (e.g., EVN memos) would strengthen it; (ii) the *components* (calibrator EVPA anchoring, matched filtering as a technique, closure quantities) are all standard — the novelty claim rests on their *combination* into this specific statistic for this specific signal, which was not found.

## Search terms used
- "axion birefringence Event Horizon Telescope polarimetry EVPA oscillation"
- "closure phase / closure trace axion birefringence EHT polarimetry search"
- "dynamical Chern-Simons gravity birefringence black hole polarimetry EVPA rotation"
- "VLBI polarimetry R-L phase gain calibration calibrator referencing cross-hand phase EHT"
- "calibrator differential polarimetry cosmic birefringence VLBI transient EVPA step matched filter"
- "EHT Sgr A* polarimetry 2024 axion time variability EVPA search birefringence"
- "arxiv 2024 axion black hole polarimetry EVPA time series Sgr A*"
