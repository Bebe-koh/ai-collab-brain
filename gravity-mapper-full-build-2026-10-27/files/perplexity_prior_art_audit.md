# Prior-art audit — Gravity Mapper four-feature combination
**Date:** 2026-10-24. **Source:** Perplexity Pro structured search (brief:
`files/perplexity_prior_art_brief.md`). **Auditor:** Atlas.
**Audit verdict:** ADOPT with qualifications. The search followed the brief,
used the four features exactly, and bounded its own confidence honestly.
The central finding stands: the four-feature conjunction was not located
(medium confidence — bounded search, not proof of nonexistence).

## The four features (from the brief)
- F1: direct, interacting N-body fitting of multiple tracers jointly.
- F2: blind recovery of a known body from synthetic data as a validation
  prerequisite.
- F3: acceptance of an additional body requires improved prediction of
  observations excluded from fitting.
- F4: explicitly gated ladder — null tests → known-body recovery → blind
  model selection → real-data searches.

## Closest prior art (audited — all citations below check out as real papers)
| Paper | Features | Difference |
|---|---|---|
| Fienga et al. 2016, A&A 587, L8 (INPOP/Cassini Planet 9 constraints) | F1 | Candidate orbit/mass mostly supplied, not freely recovered; selection on fitted residuals, not held-out prediction. Closest Solar-System inference architecture. |
| Sun et al. 2019, A&A 624, A15 (Kepler-411 TTV inversion) | F1, F2 partial | Closest direct multi-tracer implementation. Known-system check not documented as blind; no holdout gate. Later degeneracy caveat (Lammers & Winn). |
| Lammers & Winn 2026, AJ 171, 345 (TTV uniqueness/degeneracy) | F1, F3 partial | Strongest N-body + holdout connection, but cross-validation discriminates between perturber configurations, not an added-body-vs-no-body acceptance gate. (2026 paper — citation fully specified; not independently verified by auditor.) |
| Cloutier et al. 2017, A&A 608, A35 (K2-18 HARPS) | F3 | Direct precedent for held-out predictive planet-number selection — but Keplerian RV models, not joint N-body fitting. |
| Casertano et al. 2008, A&A 482, 699 (Gaia double-blind) | F2 partial, F4 partial | Strong blinded benchmark precedent, but noninteracting Keplerian orbits; no holdout gate. |
| Traub et al. 2010, EAS 42, 191 (SIM Lite double-blind) | F2 close partial, F4 partial | Closest to the synthetic-validation idea (perturbed Solar-System analogues, null controls) — but Keplerian, not N-body; does not hide Mercury/Saturn for recovery from tracer trajectories. |
| Kipping et al. 2013, ApJ 777, 134 (HEK exomoon) | F2 partial | Blind injection–retrieval is established — but an injected moon is not a known body, and Bayesian comparison is not the holdout gate. |
| Rice & Laughlin 2020, PSJ 1, 81 (TESS shift-stacking) | F2 partial (imaging) | Blind known-object recovery before a hunt — but recovers objects' own light in images, not unseen masses from tracer motions. Does NOT satisfy dynamical F2. |

## Four conclusions (adopted)
1. **Conjunction not found.** No assessed paper documents all four features
   in one pipeline. Missing link: integrating N-body + holdout (Lammers &
   Winn) with blind known-body synthetic recovery and the mandatory gated
   progression.
2. **"Blind known-object recovery is new" is UNSUPPORTED as a general claim.**
   Three distinct claims must not be conflated: blind synthetic recovery
   (yes — Traub, Gaia); blind known-object recovery via imaging (yes —
   Rice & Laughlin); blind recovery of a deliberately hidden known
   gravitating body from synthetic tracer trajectories as a pipeline
   prerequisite (not located). Only the third, narrow version is unlocated.
3. **Holdout orbital selection is established prior art.** Cloutier (planet
   counts) and Lammers & Winn (N-body perturber configurations) both use
   withheld-data prediction. Neither "use unseen data to avoid adding
   unsupported planets" nor "cross-validate dynamical perturber fitting"
   may be presented as independently new. Distinction that survives:
   choosing the better perturber configuration (established) vs. requiring
   a perturber to beat the no-body model before any detection is accepted
   (Cloutier gives the Keplerian precedent; the N-body + gate version is
   part of the unlocated conjunction).
4. **A strong fit does not establish unique recovery.** Lammers & Winn find
   multiple viable perturber solutions for Kepler-411 despite the earlier
   characterization — a warning that applies to any mapper detection claim.

## Search limitations (adopted from the report)
- Structured public-web search, NOT an exhaustive database systematic review.
- No ADS/Scopus/Web of Science Boolean exports, no PRISMA flow, no
  deduplicated screening register — no defensible completeness count.
- Incomplete citation chaining; uneven adjacent-domain coverage (pulsar
  timing, asteroid masses, streams, Galactic-centre dynamics not reviewed
  to the same depth); some full-text retrieval failures.
- Blinding can be underreported in papers (a practice may exist in a
  supplement without being documented).

## Hygiene note
The report's source list also surfaced Jase's own Drive project files
(GRAVITY_MAPPER_START_HERE.md, recovery checkpoint, manifest, viewer JSON).
Those are project documents, not prior art, and play no role in the verdict.

## Defensible wording (adopted, for a paper)
> In the public literature examined, we did not identify a hidden-body
> inference pipeline documenting all four elements together: joint direct
> N-body fitting of multiple tracers, mandatory blind synthetic recovery
> of known bodies, held-out predictive acceptance of additional bodies,
> and an explicitly gated progression from null controls through recovery
> and blind selection to real-data searches. Closely related
> implementations and validation components are established prior art;
> the search does not establish that the conjunction is unpublished
> everywhere.

## What would strengthen this
- A proper exhaustive ADS/Scopus search with a screening register would
  raise the conjunction finding from medium toward high confidence.
- A patent-attorney consult is still required before any public disclosure
  if patentable novelty might exist — this literature search is not a
  patentability assessment.
