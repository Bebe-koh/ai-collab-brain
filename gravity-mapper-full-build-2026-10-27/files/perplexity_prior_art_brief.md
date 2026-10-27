# Perplexity handoff brief — Prior-art search for the Gravity Mapper

## What this is
You are doing a systematic literature search for a research project called the
Gravity Mapper. Your job is research only: find and assess prior art. Do not
write code, do not run anything, do not try to access private sources.

## The method to assess
A simulation-first pipeline that infers hidden gravitating bodies from orbital
and motion signals, with these specific features combined:
1. **Direct N-body fitting** of multiple tracer bodies simultaneously (not
   secular/analytic approximations) to detect an unseen perturber.
2. **Blind validation by known-body recovery**: the pipeline must recover
   known bodies (e.g. Mercury, Saturn) blind, from synthetic data, before it
   is trusted on real data.
3. **Holdout model selection**: a candidate body is only accepted if it
   improves predictions on data it was NOT fit to (an explicit gate against
   hallucinating planets).
4. **Staged, gated benchmark ladder**: null tests (must return "no body" when
   none is present), then known-body recovery, then blind model selection,
   then real-data hunts.

## What is NOT claimed as new (do not report these as novelty)
- Batygin/Brown Planet Nine forward modeling (population simulations).
- Exoplanet radial-velocity and transit-timing fitting.
- JPL ephemeris fitting.
- Stellar stream gaps as dark-substructure probes.
- Standard orbit determination (Gauss, Laplace, modern least-squares).

## Questions to answer
1. Has anyone published a pipeline combining ALL FOUR features above for
   hidden-body inference? If yes, cite it precisely.
2. Has anyone published blind known-body recovery as a validation step for a
   hidden-body inference pipeline? If yes, cite it.
3. What is the CLOSEST prior art to the combination, and exactly how does
   each item differ from it?
4. Are there papers that anticipate part of the combination (e.g. holdout
   model selection in orbital fitting, or multi-tracer N-body fitting for
   unseen masses) even if they don't combine everything?

## Output format
- A table: paper (authors, year, venue), what it does, which of the four
  features it has, how it differs.
- A verdict section: is the four-feature combination published or not, with
  your confidence (high/medium/low) and why.
- A gaps section: which databases/venues you searched and what you could NOT
  cover, so the search's limits are explicit.

## Do not
- Do not give legal or patentability advice; this is a literature search.
- Do not claim "nobody has done this" unless the search was systematic;
  say what you searched and what you found.
- Do not spawn other models or agents.
- Do not invent citations. Every paper cited must be real and checkable.
