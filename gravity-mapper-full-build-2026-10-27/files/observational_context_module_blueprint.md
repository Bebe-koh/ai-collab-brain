# GRAVITY MAPPER — OBSERVATIONAL-CONTEXT MODULE
Blueprint for Mews review
Status: PROPOSAL ONLY — not implementation approval

Source note: drafted by Perplexity; pasted by Jase in main chat, 2026-10-26. Text below is verbatim as pasted. Correction 2026-10-26: authorship corrected per Jase — this is Perplexity's draft, not Jase's own writing.

1. PURPOSE AND OWNERSHIP

This extends Jase’s universal gravity lab concept.

The gravity mapper asks:
“What mass distribution explains the observed tracer motions?”

One complementary observational-context module asks:
“What other observations support, contradict, or fail to constrain
the proposed explanation?”

Its purpose is to help interpret inferred mass—not to replace the
gravity solver, manufacture certainty, or infer composition from
gravity alone.

Mews: review and sharpen this proposal. Identify contradictions,
missing interfaces, unjustified assumptions, and the smallest useful
implementation scope before recommending a build.


2. ARCHITECTURAL BOUNDARY

Preserve the existing separation:

A. Physics modules
- Represent mass distributions or force laws.
- Return acceleration vectors under the existing module contract.
- Example: a physically specified gas distribution.

B. Observational-context module — this proposal
- Reads measurements, catalogs, spectra, and scientific maps.
- Associates observations with candidate regions and trajectories.
- Compares observed quantities with candidate-model predictions.
- Returns structured evidence and limitations.
- Does NOT return acceleration merely because it ingests a gas map.

C. Central inference and validation
- Owns parameter fitting, evidence combination, model comparison,
  validation partitions, and final scientific decisions.
- Accounts for dependencies between datasets.
- Records the basis of each decision.

D. Visualization
- Separate files, reading saved outputs.
- May display aligned observations and gravitational predictions.
- Must not modify scientific results.
- An image overlay is a display, not an evidence calculation.


3. ONE TOP-LEVEL MODULE, MULTIPLE INTERNAL ADAPTERS

Expose one observational-context interface to the central program.

Internally, support adapters as needed:

observational_context/
    common_measurement_schema
    astrometry_adapter
    radio_adapter
    infrared_adapter
    optical_adapter
    spectroscopy_adapter
    association_and_alignment
    prediction_comparison
    evidence_report

These names describe responsibilities, not required filenames.

Do not implement every adapter at once. Add ultraviolet, X-ray,
lensing, plasma, range/Doppler, or other specialized observations only
when an identified science case requires them.

Sonification, if added, belongs in visualization/accessibility.
It is derived from existing data and is NOT independent evidence.


4. PROPOSED INPUT CONTRACT

The central program supplies:

- Stable case ID and candidate ID.
- Candidate type or competing model types.
- Candidate parameters and units.
- Relevant position/trajectory and epoch range.
- Coordinate frame and time standard.
- Distance constraints or an explicit “distance unresolved” state.
- Parameter uncertainty representation, if available.
- Model/source version.
- Requested observational checks.

The observation module must not silently invent missing distance,
uncertainty, trajectory, or composition information.

If inputs are insufficient, return the specific unresolved item
and the checks it prevents.


5. COMMON MEASUREMENT RECORD

Each observation or derived product must retain:

- Stable dataset and measurement identifiers.
- Source/archive reference.
- Data release/version and retrieval provenance.
- Measured quantity and units.
- Observation time or time interval and time standard.
- Coordinate frame.
- Observer location where relevant.
- Wavelength/bandpass or spectral-line definition.
- Spatial and spectral resolution where relevant.
- Measurement uncertainty and available covariance.
- Calibration assumptions and quality flags.
- Footprint, masking, and usable coverage.
- Sensitivity or selection/recovery information where available.
- Detection, upper-limit, or unavailable-data status.
- Links to parent data products and shared dependencies.
- Transformations applied.
- Which values are directly measured versus model-derived.

Missing uncertainty or selection information must be exposed,
not replaced with invented precision.


6. BASIC WORKFLOW

Step A — Candidate query
Use the candidate’s allowed region and relevant epochs to identify
potentially useful observations.

Step B — Association
Check whether the observations plausibly belong to the candidate:
- sky position and extent;
- epoch compatibility;
- distance constraints;
- motion/velocity compatibility where available;
- resolution, blending, and foreground/background ambiguity.

An overlapping sky position alone does not establish physical
association.

Step C — Measurement extraction
Use catalogs, spectra, maps, or data cubes through a documented
extraction method. Record uncertainty and background assumptions.

Step D — Forward comparison
Where a validated observation model exists:
candidate physical model → predicted observable → comparison with
the actual measurement.

Do not compare quantities with incompatible units, bandpasses,
epochs, or frames.

Step E — Structured output
Return measurements, comparison results, coverage, assumptions,
limitations, and provenance to central inference.

Step F — Central decision
The central program decides how the evidence affects the competing
explanations and the next bounded investigation.


7. OUTPUT CONTRACT

Return separate fields for:

A. Coverage
- usable coverage;
- partial/ambiguous coverage;
- no usable coverage.

B. Observation status
- detection;
- characterized upper limit;
- measurement inconclusive;
- unavailable.

C. Association
- compatible;
- incompatible;
- unresolved.

D. Model comparison
- supports the specified prediction;
- conflicts with the specified prediction;
- insufficient information;
- comparison unavailable.

E. Scientific limitations
- geometry/distance uncertainty;
- conversion assumptions;
- calibration/systematic uncertainty;
- unresolved degeneracies.

These are proposed labels, not calibrated probabilities.

Do not produce a single “gas probability” or “object probability”
unless a separately specified and validated inference method
justifies it.


8. EXAMPLE: GAS INTERPRETATION

Keep these questions distinct:

1. Is gas observed along this direction?
2. Is it associated with the inferred gravitational structure?
3. What gas mass and geometry do the observations support?
4. Does that supported distribution explain the tracer dynamics?
5. Is additional unexplained mass or model error still required?

Illustrative output:

Gas detected: yes
Physical association: unresolved
Supported gas mass: estimate with stated assumptions
Explains dynamical mass requirement: not established
Alternative explanations: remain open

A successful extended-mass fit is not, by itself, identification
of the material as gas.

If observations support only part of the required mass, retain the
unexplained remainder. Do not inflate gas-conversion parameters
arbitrarily to force agreement.


9. SAFETY AND EVIDENCE RULES

- No coverage is not a nondetection.
- Nondetection is not exclusion without appropriate sensitivity
  and selection/recovery characterization.
- Catalog absence is not automatically evidence of absence.
- A catalog match is not automatically a physical association.
- Shared or derived data products must not be counted as
  independent observations.
- A visualization or sonification supplies no additional evidence
  beyond its source data.
- Diagnostic flags do not automatically become negative evidence.
- Invalid comparisons return unavailable/inconclusive, not a kill.
- Preserve the distinction between rejecting a candidate and
  explaining the residual case.
- Observation-derived constraints used to construct a candidate
  must not later be presented as independent validation of that
  same construction.
- Reserve genuinely untouched data for final validation where
  repeated model selection would otherwise consume the holdout.
- Hypothesis rejection, model ranking, and physical identification
  must remain separately reportable.


10. MINIMUM FIRST IMPLEMENTATION — PROPOSED

Do not begin with a universal all-spectrum system.

Milestone 1 — Schema and alignment
- One shared measurement record.
- Explicit units, frames, epochs, provenance, and missing-data states.
- One real dataset adapter.
- Read-only ingestion and retrieval.

Milestone 2 — One bounded science case
- Choose one documented object/region and one observational dataset.
- Declare the physical model and observation model.
- Test association and parameter identifiability.
- Return a structured comparison.
- Do not claim blind discovery.

Milestone 3 — Link to gravity inference
- Compare the observationally supported model against tracer data.
- Keep construction data separate from validation data.
- Report whether the additional observations constrain composition,
  geometry, mass, or only association.

Milestone 4 — Separate viewer
- Display measurements, model predictions, uncertainty, coverage,
  and remaining mismatch.
- Read saved scientific outputs only.

Milestone 5 — Expansion decision
- Add another adapter only after the first case is reproducible
  and the scientific benefit is demonstrated.


11. REQUIRED ACCEPTANCE TESTS

Mews should propose numerical tolerances appropriate to the selected
dataset before execution. Do not invent universal tolerances now.

Required test categories:

- Unit/frame/time transformations against known reference cases.
- Record round-trip without provenance or uncertainty loss.
- Missing coverage never interpreted as nondetection.
- Invalid measurements/comparisons never interpreted as rejection.
- Foreground/background ambiguity remains unresolved when distance
  information is insufficient.
- Bandpass and resolution mismatches handled explicitly.
- Duplicate/derived evidence detected.
- Synthetic forward-model inputs recover expected observables.
- Null and mismatched-association controls behave correctly.
- Data-derived parameter uncertainty propagates into predictions.
- Integration does not alter gravity-only results when the module
  is disabled.
- Observational conclusions can be reproduced from saved inputs
  and declared transformations.


12. WHAT MEWS SHOULD RETURN

Return a design review containing:

1. What is sound and should be preserved.
2. Necessary corrections, ranked by scientific consequence.
3. Recommended smallest first science case and dataset.
4. Proposed interfaces and ownership boundaries.
5. Required observation models and physical assumptions.
6. Identifiable versus unresolved parameters.
7. Evidence-dependency and double-counting controls.
8. Acceptance tests with justified tolerances.
9. Dependencies on existing verified mapper capabilities.
10. Bounded implementation stages and estimated costs, explicitly
    labeled estimates.
11. Open questions and unresolved scientific limitations.

Cite authoritative documentation for physical formulas, dataset
interpretation, instrument behavior, and numerical acceptance claims.


13. AUTHORIZATION AND PRESERVATION

This blueprint authorizes review only.

It does NOT authorize:
- source changes;
- new fits or simulation ensembles;
- AI training;
- new scientific verdicts;
- enabling unvalidated physics;
- external writes;
- replacing the active baseline;
- bypassing outstanding validation or preservation requirements.

Before any later implementation:
- identify the approved baseline and dependencies;
- inspect current continuity records;
- verify access to required source and inputs;
- verify the preservation route for changed source and results;
- obtain applicable approval;
- preserve and verify actual changes before dependent work.

Do not create redundant packages merely to record that a review
occurred. Existing exact durable copies may satisfy preservation.
