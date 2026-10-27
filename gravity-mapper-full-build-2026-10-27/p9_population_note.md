# Planet Nine population forward model — can P9 sculpt the extreme-TNO apsidal clustering?

**Status:** DRAFT — production runs in progress (results pending).
**Date:** 2026-10-14. **Author:** Atlas (subagent session 74e99e15).

## Question

The observed extreme-TNO "apsidal clustering" (longitude of perihelion ϖ
concentration) is the primary dynamical evidence for Planet Nine. This
experiment tests, in a controlled forward model, three distinct questions:

1. **Can P9 sculpt clustering?** Starting from an unclustered population,
   does a P9-mass perturber produce ϖ clustering over Gyr timescales?
2. **Would it survive selection?** Does the clustering persist under a
   documented observability cut applied identically to P9 and no-P9 runs?
3. **Does it explain observations better than no-P9?** Do the P9 survivor
   distributions match the observed (ϖ, Ω, i) better than the no-P9 control?

A positive answer to (1) alone is **not** a detection claim.

## Setup

**Integrator:** REBOUND WHFast, dt=8 yr, corrector=0. Symplectic; energy
conservation dE/E ~ 1e-6 over 20 Myr; Lz conserved to ~1e-12 (J2 axisymmetry).

**Force model:** Sun + live Neptune (DE440 GM, ephemeris state at 2010-01-01)
+ J2-averaged Jupiter/Saturn/Uranus (J2=0.0341 at R_ref=1 AU, per
Batygin & Morbidelli 2017), implemented via REBOUNDx `gravitational_harmonics`
(C speed). Optional Planet Nine as a live massive body.

**P9 configurations** (4, spanning the published hypothesis range;
Batygin et al. 2019; Brown & Batygin 2021):
| config | mass | a (AU) | e | i |
|---|---|---|---|---|
| fiducial | 10 M⊕ | 400 | 0.30 | 15° |
| close | 10 M⊕ | 300 | 0.20 | 15° |
| far | 10 M⊕ | 500 | 0.40 | 15° |
| lowmass | 5 M⊕ | 400 | 0.30 | 15° |
All with Ω=90°, ω=158°, M0=180° (ϖ9=248°; anti-aligned shepherding
direction 68°). Control: noP9.

**Particles:** 150 synthetic extreme TNOs; (a,e,i) drawn with replacement
from the empirical catalog (90 objects, extreme_tnos_full.csv); Ω, ω, M
uniform. **Matched ICs:** the draw depends only on (seed=101, n_part) —
bit-identical t=0 across all 5 configs (max |Δa|=2.3e-13 AU).

**Runtime:** 1 Gyr, snapshots at 0/250/500/750/1000 Myr. Barycentric
osculating elements via secular_elements.py.

**Performance engineering (documented):** 150 test particles in one WHFast
sim run at 147 steps/s (O(N²) kick). Two changes, both validated bit-exact:
(1) batch into 10×15-particle sims (117k steps/s; batch/full agree to
0.00e+00); (2) corrector=0 (the 11th-order corrector cost 30× per
integrate() call for identical conservation). Checkpoint/resume every
snapshot (bit-exact) survives VM restarts.

## Validation (all pass, 2026-10-14)

- REBOUNDx J2 vs analytic dΩ/dt: 0.003% (circular test); exact to 4 s.f. on
  e=0.8 test (8.3274e-9 vs 8.33e-9 rad/yr).
- J2+Neptune vs full 4-giant N-body: dϖ/dt = 1.641e-8 rad/yr in both (<1%
  agreement). The initial 28% mismatch was traced to an under-resolved dt=1.0
  in the *reference* (Jupiter at 12 steps/orbit), not the J2 — at dt=0.5 the
  full model matches the J2 exactly. Lesson: validate the validator.
- Energy: dE/E = -1.52e-6 over 20 Myr; Lz conserved to 4.5e-12, confirming
  the J2's axisymmetry (the physically conserved quantity).
- Timestep convergence (dt=8 vs 4, 20 particles, 50 Myr, fiducial P9):
  final (ϖ,Ω,i) distributions statistically indistinguishable (KS p=0.98).
- IAS15 vs WHFast (5 particles, 50 Myr): regular orbit agrees to machine
  precision; Neptune-scattering (chaotic) orbits diverge as expected for any
  two integrations of a chaotic system.
- t=0 uniformity: all 5 configs, n=150, ϖ Rayleigh p=0.805, Ω p=0.372.
  The desired pattern is not seeded.
- Performance engineering (all validated bit-exact): corrector=0 (the
  11th-order corrector cost 30× per integrate() call for identical
  conservation); 10×15-particle batches (0.00e+00 vs full 150); checkpoint/
  resume every snapshot (0.00e+00, survives VM restarts).

## Observed clustering benchmarks (extreme_tnos_full.csv, n=90)

| sample | n | R | Z | p |
|---|---|---|---|---|
| full | 90 | 0.082 | 0.60 | 0.55 |
| a>250 | 45 | 0.049 | 0.11 | 0.90 |
| a>300 | 36 | 0.107 | 0.41 | 0.67 |
| q>40 | 31 | 0.108 | 0.36 | 0.70 |
| a>250,q>30 (BB16-like) | 45 | 0.049 | 0.11 | 0.90 |

No significant clustering in the full catalog or standard cuts. (The
"classic 7" famous objects: R=0.649, Z=2.95, p=0.047, n=7 — marginal,
post-hoc, tiny-n.)

## Results (COMPLETE — 50/50 jobs, 2026-10-17)

Production: 50/50 batch jobs complete (5 configs × 10 batches, 150 particles
each, 1 Gyr, WHFast dt=8 + REBOUNDx J2), driven by `launch_p9.py` with
bit-exact checkpoint/resume (survived one driver death mid-run; close_b6/b7
resumed from 500-Myr checkpoints). Final conservation: dE/E ~2e-6,
dLz/Lz ~1e-12 across configs. Merged per config: `p9_runs/merged_{cfg}.npz`
(150 particles × 5 snapshots); per-snapshot Rayleigh/Kuiper in
`p9_runs/{cfg}.json`; attrition + 2D KS + observability cut + FPR in
`p9_postprocess.log`.

### Preliminary: 60-particle no-P9 subset (batches 0-3 merged)

- Survival: 60 → 52 (86.7%); 9 ejections, median ejection time 750 Myr.
- Final (1 Gyr) ϖ: n=52, R=0.269, Z=3.77, p=0.022 — marginally significant.
  With 10 tests (5 snapshots × ϖ,Ω), expect ~20% chance of at least one
  p<0.022 by fluctuation. The full 150-particle FPR analysis will quantify this.
- Observable cut (q<40 AU): n=30, R=0.323, Z=3.13, p=0.043.
- dE/E max 1.9e-6; dLz/Lz ~1e-12 across batches.

This marginal signal in a 60-particle subset is *exactly* why the
pre-registered FPR analysis matters: it calibrates how often the no-P9
control produces "clustering" this strong by chance.

### Full results (COMPLETE — 2026-10-17)

**Survival at 1 Gyr (150 particles each):**

| config | survivors | ejected | median eject t |
|---|---|---|---|
| none | 131 (87.3%) | 20 | 750 Myr |
| fiducial | 58 (38.7%) | 92 | 250 Myr |
| close | 58 (38.7%) | 92 | 250 Myr |
| far | 70 (46.7%) | 80 | 250 Myr |
| lowmass | 75 (50.0%) | 76 | 500 Myr |

P9's dominant dynamical effect is **attrition**, not sculpting: it ejects
50–61% of the population (median ejection 250–500 Myr) vs 13% in the no-P9
control (median 750 Myr).

**Rayleigh/Kuiper on (ϖ, Ω) at 1 Gyr (survivors):**

| config | n | ϖ Z | ϖ p | ϖ KV | Ω Z | Ω p | Ω KV |
|---|---|---|---|---|---|---|---|
| none | 131 | 4.42 | 1.18e-2 | 0.185 | 0.12 | 0.89 | 0.098 |
| fiducial | 58 | 0.56 | 0.57 | 0.162 | 2.78 | 6.17e-2 | 0.203 |
| close | 58 | 5.01 | 6.26e-3 | 0.239 | 5.39 | 4.21e-3 | 0.253 |
| far | 70 | 1.86 | 0.16 | 0.157 | 4.46 | 1.11e-2 | 0.245 |
| lowmass | 75 | 0.23 | 0.79 | 0.090 | 4.29 | 1.33e-2 | 0.212 |

Some P9 configs show formally significant nonuniformity (close: both angles
p<0.01 at 1 Gyr; far/lowmass: Ω p~0.01; fiducial Ω was p=7.1e-6 at 250 Myr
but decayed to p=0.062 by 1 Gyr). But the **no-P9 control itself** reaches
ϖ p=0.0118 at 1 Gyr, and across 5 snapshots × 2 angles × 4 configs
(~40 tests) several p~0.01 events are expected by fluctuation. Kuiper V
tracks the same pattern.

**Observability cut (q < 40 AU, survivors):**

| config | n | ϖ Z | ϖ p |
|---|---|---|---|
| none | 72 | 1.65 | 0.19 |
| fiducial | 9 | 3.67 | 0.021 |
| close | 12 | 0.43 | 0.66 |
| far | 11 | 0.85 | 0.44 |
| lowmass | 20 | 2.08 | 0.12 |

The cut leaves P9 configs with only 9–20 particles (vs 72 in the control).
fiducial's n=9 formal significance is fragile — tiny-n and
selection-dominated; close/far/lowmass are null under the cut.

**2D KS (ϖ,Ω), no-P9 vs P9 (Fasano–Franceschini, permutation p):**
fiducial D=0.235 p_perm=0.084; close D=0.268 p_perm=0.026;
far D=0.233 p_perm=0.066; lowmass D=0.175 p_perm=0.367.
Only close is nominally significant, and across four config comparisons
that is weak.

**False-positive rate (the decisive calibration):** 97.8% of 2000 random
74-particle no-P9 subsamples (drawn from the n=131 control survivors) reach
Z ≥ 0.60 — the observed catalog's full-sample Rayleigh Z (n=90, Z=0.60,
p=0.55, itself not significant). In other words, the no-P9 model produces
observed-level "clustering" essentially every time. The observed signal
cannot discriminate P9 from no-P9.

## Verdict (COMPLETE — 2026-10-17)

1. **Can P9 sculpt clustering?** Mechanically yes — some configs show
   significant (ϖ,Ω) nonuniformity — but the signal is **not distinctive**:
   the no-P9 control produces clustering of the same strength (97.8% of
   control subsamples reach the observed Z). P9's dominant signature in
   these runs is depopulation, not sculpting.
2. **Would it survive selection?** Mostly no. The q<40 cut leaves only
   9–20 P9 survivors (vs 72 in the control); all P9 configs are null under
   the cut except the n=9 fiducial case, which is too small to carry a
   population claim.
3. **Does it explain observations better than no-P9?** No. 2D KS no-P9 vs
   P9 is at best marginal (close p=0.026, others ≥0.066), and the FPR
   analysis shows the observed clustering level is reached by no-P9
   dynamics essentially every time. There is nothing here for P9 to beat.

**Bottom line:** this study does not support a dynamical P9 origin for the
observed extreme-TNO orientation structure. What P9 mainly does in this
model is eject the population; what clustering remains is indistinguishable
from the no-P9 background — which itself reaches observed-level clustering
97.8% of the time. And the observed catalog as a whole shows no significant
clustering in the first place (Z=0.60, p=0.55). The bias limitation and
non-claims below stand unchanged: this tests the dynamical hypothesis in
a model, not the planet's existence.

## Bias limitation

Survey bias (where telescopes pointed) is **not modeled**. The observed
clustering itself is debated on these grounds: OSSOS's characterized sample
(Shankman et al. 2017) and debiased analyses (Napier et al. 2021) find the
underlying orientations consistent with uniform after selection correction.
Our q<40 cut is a crude proxy, not a survey simulator. This result must be
framed against that disagreement, not past it.

## Explicit non-claims

- "P9 can produce this clustering" ≠ "P9 exists."
- A negative ("this P9 configuration doesn't produce it") ≠ "no P9."
- Tests the DYNAMICAL hypothesis in a model, not the existence of the planet.
