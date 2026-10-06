# Prior-art search: adaptive-Kalman over-whitening finding
**2026-10-03 · subagent literature search (web search across adaptive-KF / noise-estimation literature; not a full systematic review — IEEE Xplore full text, dissertations, and textbooks not exhaustively checked)**

## The finding under test

From `radio_pilot_joint_estimation_note.md` §2: the textbook adaptive-KF white-noise update — per-pulsar innovation covariance matching, `f ← f·mean(NIS)` (Mehra-style) — **converges stably but to a non-ML fixed point** under model misspecification (real reds aren't random walks), **over-whitening ~2×** (B1855: f̂=4.96 vs pseudo-LL maximum at 2.42, verified by direct scan). Diagnosis: moment-matching dumps all residual misfit into white; the likelihood's log|S| term resists this, so the two objectives separate. A pseudo-likelihood line search was adopted instead.

Three distinct sub-claims: (a) stable (non-divergent) convergence to a wrong fixed point; (b) the fixed point is provably non-ML, quantified against a direct likelihood scan; (c) the mechanism — misspecified process model ⇒ all misfit absorbed into R.

## Paper-by-paper

| # | Paper | What it showed | Closeness |
|---|---|---|---|
| 1 | Brown & Rutan, "Adaptive Kalman Filtering" (PMC6644984), analytical-chemistry review | Covariance matching for R under model error: "In essence, this amounts to **'covering' the errors in the model with noise, then estimating the noise variance**." (Eq. 2.13 is exactly the Mehra update.) | **Related phenomenon — closest conceptual match.** States the mechanism (c) explicitly, but as a deliberate design choice to prevent divergence, in a different setting; no fixed-point analysis, no ML comparison, no quantification. |
| 2 | Berry & Sauer, "Adaptive ensemble Kalman filtering of nonlinear systems" (http://math.gmu.edu/~tberry/Publications/QR.pdf) | "As shown by Mehra and later (Daley 1992) and (Dee 1995), the innovation correlations are a **blended mixture of observation noise, predictability error** (due to state uncertainty), **and model error**. Disentangling…" | **Related phenomenon.** Names the confounding (c) as known since Mehra/Daley/Dee, but in the EnKF/nonlinear setting; no demonstration of (a) or (b). |
| 3 | Ge et al. 2019, Sensors 19(6):1371 (adaptive UKF, maneuvering targets) | Sage-Husa measurement-noise estimates "are **biased because the coupled innovation is contaminated**" when the system model changes (target maneuver). | **Related phenomenon, different setting.** Model mismatch ⇒ biased R, demonstrated — but framed as contamination/divergence during maneuvers, not a stable non-ML fixed point with quantified over-whitening. |
| 4 | Ge et al. 2020, Remote Sens. 12(21):3500 | "The matching method's convergence is **not always accurate and gives biased covariance estimates** [17]" ([17] appears to be Li & Bar-Shalom 1994 — a loose citation). | **Generic statement.** Asserts bias without mechanism, setting, or quantification. |
| 5 | Hashlamon & Erbatur, Turk. J. Elec. Eng. (IAE survey) | "The estimated covariances are **biased** [15]" listed among IAE drawbacks (alongside positive-definiteness, window size). | **Generic statement.** No mechanism or setting. |
| 6 | arXiv:2003.14022 (distributed noise-covariance estimation in sensor networks) | "Covariance matching is a technique to **provide biased estimates** of the true covariances based on the residuals." | **Generic statement.** No mechanism or setting. |
| 7 | Odelson, Rajamani & Rawlings 2006 (TWMCC TR 2003-04; Automatica) — ALS method | Reformulated correlation methods to yield **unbiased** noise-covariance estimates with uniqueness guarantees — **under correct LTI models**. | **Different setting.** Fixes method-induced bias assuming the model is right; says nothing about misspecification-induced fixed-point bias. |
| 8 | ai4fly-estimation project notes (GitHub, non-peer-reviewed) | Nonlinear KFs systematically underestimate posterior covariance ⇒ "Mehra's subtraction then **books that missing scatter as sensor noise and inflates R**"; "any adaptive method that reads R off the innovations inherits it." | **Related mechanism, different cause** (nonlinearity-induced P underestimation, not process-model misspecification). Not peer-reviewed. |
| 9 | Mehra 1970 (TAC 15:175–184); Mehra 1972 (symposium) | Original covariance-matching / correlation methods. No bias or fixed-point analysis under misspecification. | **Foundational, not anticipating.** |
| 10 | Mohamed & Schwarz 1999 (J. Geodesy) | ML-based noise estimation presented as the principled alternative to matching. | **Related (alternative method).** No head-to-head showing the two diverge under mismatch. |

## Verdict: PARTIAL OVERLAP

The **mechanism** — innovation-based matching absorbs model error into noise-variance estimates — is qualitatively anticipated, most explicitly by Brown & Rutan ("covering the errors in the model with noise") and Berry & Sauer ("blended mixture of observation noise, predictability error, and model error"), and bias-under-mismatch is widely asserted (papers 3–6). What I did **not** find anywhere: the specific demonstrated result — the textbook `f ← f·mean(NIS)` iteration converging **stably** (not diverging) to a **provably non-ML fixed point**, with **over-whitening quantified (~2×) against a direct likelihood scan**, plus the diagnosis that moment-matching dumps *all* residual misfit into white while the likelihood's log|S| term resists it. The literature treats the bias as folk knowledge or a qualitative warning; the fixed-point-vs-ML separation with a measured number appears new in the venues searched.

## Caveats

- Web search only; a systematic review (IEEE Xplore full-text, dissertations, textbook passages in Maybeck/Gelb/Jazwinski/Anderson-Moore) could still turn up an anticipation.
- "No exact match found" is not proof of absolute novelty.
- The Brown & Rutan passage is the one citation a careful reader would raise first; any write-up should cite it and distinguish the contribution as the quantified fixed-point/ML separation, not the mechanism itself.
