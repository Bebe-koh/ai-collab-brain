# Chain-vs-binned reconciliation — tech note (2026-09-24, corrected)

## Question
Timing-chain red-noise amplitudes appeared to underpredict binned low-frequency
variance by large factors (reported as ~400× J1909, ~10× B1937, ~5× B1855).
Hypothesis under test: enterprise chains trade low-frequency power with F0/F1/DMX
while fixed-par bins retain it — or the chains genuinely miss low-frequency power.

## Method
Direct per-pulsar two-component maximum-likelihood fit to the 30-day binned
residual series, with GLS projection of quadratic (timing-model) directions:

    C = s_red * C_red(chain median log10_A, gamma; 30-freq Fourier basis)
        + s_white * I

C_red uses the enterprise convention S(f) = A^2/(12π^2) (f/f_yr)^-γ yr^3.
s_red measures the red-amplitude discrepancy; s_white absorbs the true binned
white level (the binned product's formal errors are NOT used — see §3).

## Results (chain_binned_step2.json)

| pulsar   | s_red | amplitude factor | fitted white (ns/bin) |
|----------|-------|------------------|-----------------------|
| J1909    | 0.56  | 0.75×            | 31                    |
| B1937    | 0.74  | 0.86×            | 205                   |
| B1855    | 1.18  | 1.08×            | 463                   |
| J0437    | 1.23  | 1.11×            | ~0 (degenerate: γ=0.52 ≈ white) |

**The chains' red-noise amplitudes are fine — all within ~25% of the binned data.**
The reported 400×/10×/5× underpredictions do not survive direct measurement and
are withdrawn.

## The real bug: white noise, not red noise
The binned product's formal errors vs the fitted white level:

| pulsar | formal err median (ns/bin) | true white (ns/bin) |
|--------|---------------------------|---------------------|
| J1909  | 0.3                       | 31                  |
| B1937  | 0.0                       | 205                 |
| B1855  | 10.6                      | 463                 |
| J0437  | 6.2                       | —                   |

The formal bin errors omit jitter/EQUAD/ECORR and are underestimated by ~10–100×
in amplitude (~100–10,000× in variance). Every χ² significance ever computed from
the binned product with these errors was correspondingly inflated.

## Reframed diagnosis of the monopole hallucination
The original 14-epoch "detection" (χ²=406/14) was doubly spurious:
(a) the GLS estimator put ~93% weight on J1909, reading her private variance as
    a common mode; AND
(b) the white noise was underestimated ~100× in amplitude, inflating every χ²
    by ~10,000× in variance terms.
Either flaw alone kills the detection. The wide-array stage-3 result (ΔlnL=0 for
all spatial components with honest per-pulsar variances) stands and is now
understood as the consequence of fixing both flaws at once.

## Provenance of the withdrawn 400× figure
It came from the wide-array stage-3 ULDM test, where a free-scale red-noise fit
settled at 1.7×10^5 × chain variance. That fit did not include a proper free
white-noise component and was degenerate/misspecified. The direct two-component
fit here (s_red=0.56 for J1909) supersedes it.

## What remains genuinely anomalous (not withdrawn)
- B1937's drift is deterministic-like (consistent with the published ~31-yr
  sinusoid); a stationary power law is the wrong *shape* even though its
  amplitude is right. A deterministic component belongs in the noise model.
- B1855's fitted white (463 ns/bin) is inflated by the incoherent ASP-era spike
  epochs — the data-hygiene issue stands.
- J1909's 8.8-yr wobble is a mild shape mismatch (projected χ²/dof ≈ 2.1), not
  an amplitude crisis.

## Repair implications for the pulsar timing work
1. Never trust the binned product's formal errors. Fit the white level or
   propagate it from the chain white-noise parameters (EFAC/EQUAD/ECORR).
2. The estimator-weighting fix (fit per-pulsar variances; don't fix noise at
   chain point estimates in spatial fits) is unchanged and already demonstrated.
3. B1937 needs an explicit deterministic (sinusoidal) component competing with
   the power-law red noise — the literature (Vivekanand 2020) already provides
   the hypothesis; our achromaticity measurement (r≈0.999) constrains it.

Status: completed-toy (direct likelihood measurement on existing products;
no new data, no independent validation). The correction itself is the deliverable:
it stops a false "chains are broken" narrative from propagating into the repair.
