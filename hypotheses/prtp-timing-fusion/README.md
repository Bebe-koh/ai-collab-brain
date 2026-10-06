# PRTP — covariance-aware pulsar timing fusion for spacecraft clocks

**Status:** active · **Verdict:** simulation arc complete; engineering /
real-data work is next, not more sims

## Claim
Fusing pulsar timing with an onboard clock via covariance-aware
estimators can extend deep-space clock stability.

## Key results
- **X-ray: NO-GO** for DSAC-class clocks (monopole hallucination was
  doubly spurious: 93% estimator weight on one pulsar + white noise
  underestimated ~100× from binned formal errors).
- **Radio rescue:** survives all realism tests — estimated-qf matches
  oracle 1.00×, G3 survives 40% data gaps, joint white+qf estimation
  costs ≤1.00×. CSAC trade study: break-even M*≈860–1000; radio wins
  for all clock classes.
- B1937's 31-yr wobble: deterministic sinusoid vs stochastic power law
  undecidable on 15.5-yr data; wander is achromatic (excludes DM/ISM
  origin for the dominant component).
- Repair rule: never trust binned formal errors; fit white level or
  propagate from chain white params.

## Open questions
- Red-noise PSD shapes remain the only oracles; hybrid modeling not real.

## Next actions
- NANOGrav radio pilot designed — pending Jase's go.

(Atlas, 2026-10-06)
