# Gas module design brief — Gravity Mapper universal gravity lab

**For Perplexity: design review.** Paste this whole brief into Perplexity and ask it to return the specification in §6.

## Whose idea this is

The universal gravity lab and its toggleable modules are Jase's design. Your job is to review, sharpen, and extend the gas module's physics specification — not to redesign the mapper, and not to claim the idea. Where you disagree with the spec below, say so plainly and show your reasoning.

## Background in one paragraph

The Gravity Mapper infers hidden gravitating bodies from the motions of tracers (planets, TNOs, stars). Today its physics is Newtonian point masses plus rings. It is growing into a lab where different kinds of mass and different force laws are toggleable modules, so the fitter can do formal model selection (gas on vs gas off) instead of assuming one physics.

## The module contract (fixed — do not redesign)

- Each module takes a position and returns an acceleration vector, plus its own parameters.
- The fitter sums the acceleration fields of the enabled modules.
- The central program owns the integrator, units, coordinate frames, timestepping, the sum, and the verdict. It does not own module physics.
- Each module owns its local physics and may use its own best numerical method.
- The holdout gate decides: a module combination must beat the null on held-out tracer data and survive simplicity/plausibility checks, or the answer is abstain.
- Hard rule: a module earns a place in a blind fit only with its own validated physics. A gas module with a made-up profile is worse than no gas module.

## The job: specify the gas module

Gas is the first module to be designed (halo second, belt/ring later). Design its physics specification:

### 1. Representation

Gas is an extended mass distribution, not a point. Its acceleration field comes from its density distribution ρ(x) via the Poisson integral. Answer:

- Which density profiles are physically legitimate for the cases the mapper will actually meet? Consider, and rank by usefulness: molecular clouds, neutral-hydrogen (HI) clouds, galactic gas disks, and primordial hydrogen at cosmological scale.
- Which of these have analytic acceleration fields (e.g. Plummer sphere, uniform sphere, exponential disk)? Which require numerical integration, and what method (grid, multipole expansion, direct sum) is fast enough to live inside a fitter?
- What is the minimal honest representation: is a parametric profile enough, or must the module accept an observed density map as input?

### 2. Parameters the fitter sees

Propose the parameter set: total gas mass, scale radius/length, flattening or shape, profile index, center position. For each: is it identifiable from tracer motions alone, or degenerate with a point mass or another module? Flag any parameter that tracers cannot constrain — an unidentifiable parameter is a design defect, not a detail.

### 3. Physics subtleties — adjudicate these

- **Pressure:** gas is collisional and pressure-supported. For a gravity-only module, does pressure matter? Under what conditions can we take the mass distribution as given (observed or in equilibrium) and ignore hydrodynamics, and when does that break?
- **Self-gravity vs external field:** the module supplies the gas's pull on tracers. When must the gas's own response to the potential (its rearrangement) be modeled, and when is a static distribution adequate?
- **Time dependence:** gas moves, disperses, forms stars. Over what timescales is a static gas module valid — solar-system fits (years), galactic fits (Myr), cosmological fits (Gyr)? Where does the static assumption fail?
- **Two roles of hydrogen:** gas as gravitating mass (this module) vs gas as tracer of the potential (the primordial-hydrogen thread, where HI maps the wells). Keep these roles distinct in the spec — do not let the module confuse them.

### 4. Validation cases (required — no module without these)

Propose concrete, checkable cases the module must reproduce before it earns a blind-fit place. For each, give the numbers: the setup, the expected acceleration field or rotation curve, and the tolerance. Include at minimum:

- An analytic case (uniform sphere or Plummer sphere — exact inside/outside fields).
- A disk case (exponential disk — known rotation curve).
- A real observed cloud with measured mass and size, where the module's field can be checked against an independent estimate.
- A degeneracy case: a gas distribution whose field a point mass could mimic, and how validation distinguishes them.

### 5. Failure modes

List what would make a gas module worse than none: e.g. a profile chosen to fit residuals rather than from physics; double-counting gas already present in the known inventory; assuming sphericity for a flattened cloud; a static module applied where gas evolves. For each, give the safeguard.

### 6. What to return

A structured specification: representation, parameter set with identifiability notes, answers to the subtleties in §3, validation cases with numbers, numerical method, failure modes with safeguards, and open questions you could not resolve. Cite a textbook or paper for every profile and formula you rely on; flag anything you are unsure of rather than smoothing it over.

## Scope limits (do-not list)

- Do not redesign the mapper, the fitter, the holdout gate, or other modules.
- Do not write code or run fits — design review only.
- Do not invent a density profile to make the math easy. If no legitimate profile fits a case, say so.
- Do not treat the primordial-hydrogen cosmology thread as settled science; it is the motivation, not a result.

## Addendum — Perplexity design review (2026-10-26), adopted points

The review returned a design review, not code or fits, as requested. Its points below are adopted into this spec. The design remains Jase's; the review sharpened it.

### A. The core distinction: mass distribution vs identification as gas

Gravity measures a mass distribution, not composition. Two distributions with the same field produce the same effect on tracers, and a Plummer field approaches a point-mass field at distances large compared with its scale length. The module's verdict language must therefore distinguish three statements:

- "An extended mass model improves prediction."
- "Independent observations support interpreting that mass as gas."
- "These data cannot distinguish gas from another mass component."

This distinction belongs in the parameter-identifiability section. Key sentence for the specification:

> A successful gas-model fit supports the specified gravitational mass distribution; identification as gas requires independent observational evidence.

### B. Benchmarks vs physical models

A convenient analytic density law is not automatically a justified model of a particular gas cloud. Classifications:

| Representation | Intended status |
|---|---|
| Uniform sphere | Exact numerical benchmark |
| Plummer sphere | Smooth extended-mass benchmark; physical use requires justification |
| Bonnor–Ebert sphere | Conditional model for suitable pressure-confined, approximately isothermal cores |
| Exponential disk | Idealized disk benchmark or justified fitted approximation |
| Observation-derived density model | Object-specific representation, with geometry and measurement uncertainty recorded |

### C. Disk gravity is not spherical gravity

An exponential disk's midplane rotation curve involves modified Bessel functions; treating its enclosed mass as though spherical gives a different field. The disk test must explicitly catch that shortcut. Passing a midplane rotation-curve test does not validate the full three-dimensional vector field — off-plane and symmetry checks are separate acceptance items.

### D. Observed maps are evidence, not a complete 3D solution

Observations constrain projected (column) structure; the 3D density requires an adopted geometry. The specification must carry the adopted geometry and distance assumptions alongside any map, never label an inferred 3D density as directly measured.

### E. Reference object: Barnard 68, with a circularity warning

Published adopted values: mass ~2.1 solar masses, radius 12,500 AU, assumed distance 125 pc; extinction-derived density structure well described by a Bonnor–Ebert model. Reproducing the field calculated from those same adopted inputs is a consistency check, not an independent measurement of that field. The "independent estimate" required for a real-world validation pass needs an explicit definition before any such pass is claimed.

### F. First-implementation scope

Cosmological hydrogen stays in the scope-and-limitations section for v1; it is not promised to fit the same static cloud implementation. First scope is two layers, without changing the module contract:

1. A deterministic extended-mass field evaluator, validated against exact spherical and disk benchmarks.
2. A restricted set of gas interpretations, each admitted only with stated physical assumptions or observational support.

The first deliverable is the structured specification (§6). It is not yet a gas-enabled blind search.
