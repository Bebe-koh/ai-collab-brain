# B1937+21 deterministic-wobble test + rigorous achromaticity (2026-09-24)

## Context
B1937+21 shows a large slow wander (ptp ~17.6 µs over 15.5 yr). Vivekanand (2020),
arXiv:1908.03026v2, analyzing 31 yr of combined data, found the timing noise is
close to a sinusoid with P ≈ 31.5 yr (11,493 days), amplitude a1 ≈ 131.5 µs,
best explained by a Moon-sized planetary companion (precession also possible
with reduced confidence), plus unexplained excess noise near steep DM gradients.
Literature-first: the phenomenon is known; the incremental question is what the
NANOGrav 15-yr data alone can say.

## Test 1: deterministic sinusoid vs stochastic power law (b1937_wobble_fit.py)
Models for the 167-bin 30-day series, quadratic timing-model profiled via GLS,
red noise = chain power-law shape (free scale) + free white level:
- M0 red-only: lnL = −1024.06, BIC = 2058.4 (s_red = 0.74, white = 205 ns/bin)
- M1 + free sinusoid: ΔlnL = 1.79, BIC = 2070.1
  (P ran to the 60-yr bound with unphysical 560 µs amplitude — the optimizer
  exploiting the quadratic↔long-period-sinusoid degeneracy)
- M2 + sinusoid P fixed at 31.47 yr: ΔlnL = 1.75, BIC = 2065.1, A ≈ 52 µs

Verdict: on 15.5 yr of data the deterministic 31.5-yr sinusoid is NOT preferred
over stochastic power-law red noise (ΔlnL ≈ 1.8; BIC prefers M0). This is a
fundamental degeneracy, not a data flaw: half a cycle of a 31-yr sinusoid is
nearly a quadratic over this span, and the quadratic is already profiled.
Vivekanand's 31-yr baseline breaks the degeneracy; ours cannot. This neither
confirms nor falsifies his model — it sets the limit of what 15-yr data can say.

## Test 2: rigorous cross-band achromaticity (b1937_achromaticity.py)
Post-fit residuals from the published PINT par (no refit), split by receiver,
30-day bins per band, correlations on ONLY genuinely contemporaneous native
bins (same grid, both bands present), inverse-variance weighted:

| pair | overlap bins | weighted corr |
|------|--------------|---------------|
| 800 MHz × 1.4 GHz | 135 | 0.9987 |
| 800 MHz × S-band  | 68  | 0.9976 |
| 1.4 GHz × S-band  | 84  | 0.9997 |

The wander is achromatic to <0.3% correlation deficit across ~0.8–3 GHz.
A DM-gradient/ISM origin scales as 1/f² (≈14× between 800 MHz and S-band) and
is excluded for the main wander. This favors Vivekanand's achromatic hypotheses
(planet companion or precession / intrinsic spin noise) and specifically
constrains his "unexplained excess near steep DM gradients": the dominant
wander component is not that.

## Net contribution vs the literature
Not a discovery of the wander (known since before NANOGrav; quantified by
Vivekanand 2020). The incremental, defensible contributions:
1. On NANOGrav 15-yr data alone, deterministic 31.5-yr sinusoid vs stochastic
   red noise is undecidable (ΔlnL 1.8) — the degeneracy is quantified.
2. The wander is rigorously achromatic (wcorr ≥ 0.9976 on contemporaneous bins),
   excluding a DM-gradient origin for the dominant component.

## Repair implication
B1937's noise model wants an explicit low-frequency deterministic-component
option competing with the power law — but the 15-yr data cannot decide between
them, so the honest model is a mixture with the degeneracy acknowledged, not a
forced choice.

Status: completed-toy (post-fit residuals, simplified likelihoods, no refit;
no independent validation). Literature comparison done before analysis per the
standing rule. Novelty claim: only the two numbered points above, and (2) is a
constraint, not a detection.
