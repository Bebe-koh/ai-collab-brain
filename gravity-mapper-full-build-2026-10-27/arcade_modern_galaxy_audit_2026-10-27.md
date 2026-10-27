# Arcade / modern / galaxy-scale proposals — audit against the current build
Date: 2026-10-27. Authorized by Jase in his own words (widget tap, "Audit all three against the current build", 07:09 PDT).
Inputs treated as review input, not as Jase's decisions: (1) the arcade/console translation paste, (2) the modern-techniques paste (multi-fidelity, JAX, GPU, Bayesian active learning), (3) the galaxy/cluster/supercluster scaling paste.
Method: read the workspace code, not the pastes' citations. No code was changed by this audit. The eccentric search-v4 re-run was not touched and its per-case files were not used as audit evidence.
Code base audited (all under `hidden_files/` unless noted): `rails_brain.py`, `particle_brain.py`, `rom_closure.py`, `rom_history.py`, `hypothesis_tracker.py`, `hypothesis_inventor.py`, `checker_brain.py`, `optimizer_brain.py`, `perturber_fitter.py`, `real_data/tno_hunt_40yr_seg.py`, `real_data/tno_hunt_40yr_seg_inject.py`, `real_data/secular_elements.py`, `real_data/belt.py` (belt softening only).

## Headline verdict

All three pastes are directionally compatible with the project and all three preserve the governing rule — cheap models rank or schedule, full physics alone promotes — but none is a drop-in, and several claimed wins are already present while several claimed tiers are missing entirely.

- Already present, so not a new win: TNO sprite batching, ROM rails caching, TNO segmented-null reuse, TNO fixed timestep, ROM baseline reuse with a provenance guard.
- Present in pieces, incomplete as a ladder: the LOD / multi-fidelity tiers. F0 and F3 exist; F1 exists only in the TNO hunt; F2 (a secular candidate model) does not exist as a fit model.
- Absent, i.e. a new build with its own spec and validation: POD reduced-order baselines, JAX/GPU execution, Gaussian-process / Bayesian active learning, error-aware trust regions, autodiff, and every galaxy-scale solver and module in paste 3.
- Still a compliance gap, not a new idea: broad/narrow screening that "prioritizes, never eliminates" is not yet what the code does everywhere (see §1.5).

Nothing in this audit authorizes implementation. Each slice below needs its own spec and Jase's decision, as with the ROM-efficiency audit of the same day (`rom_efficiency_audit_2026-10-27.md`).

## 1. Arcade / console tricks

### 1.1 Tilemaps: cache reusable tiles — PRESENT, with the same key gap as the earlier audit
- ROM: `rails_brain.PlanetRails` builds CubicSplines over a 0.5-day grid and can load/save them (`build(..., dt_days=0.5, cache_path=...)`; the sealed cache is `sealed_runs/planet_rails.npz`). `PlanetRails.positions(t)` raises outside `[t_min, t_max]` — no silent extrapolation.
- TNO: planet positions come from ephemeris-CSV splines via `planet_pos_at(t)` in `tno_hunt_40yr_seg.py`.
- Tidal tensors: only in the TNO hunt. `seg_T` holds per-segment `(T_var, t_var, r_var_T)`, built in memory; `rom_closure.py` contains no tidal-tensor model. So "cache the tidal tensors" is a TNO-side item, not a ROM-closure item.
- Key gap (carried from the earlier audit): the TNO null file `_tno40_seg_null.npz` stores `t_epochs, null_pred, seg_rms, tn` with no input fingerprint, and the ROM rails fingerprint probes only 3 epochs, not full coefficients. Tiles exist; a persistent, cross-run tile cache key does not yet exist in full.

### 1.2 Sprite batching: shared terms once per timestep — CORRECTION: already realized in the TNO hunt, not an untapped win there
- TNO `accel_full(rs, t, cand)` takes all tracers at once (`rs` is `(NT, 3)`, `NT == 340`, asserted in the file). It calls `planet_pos_at(t)` once per RK4 stage, computes `r3i = 1/|rp|^2^1.5` once per stage, and the indirect term `-rp[j] * r3i[j]` is therefore already shared across all 340 tracers. The per-tracer work is only the direct term `d / |d|^3`.
- ROM is the opposite case: `particle_brain.NBodyParticle._rhs` is a single-tracer right-hand side, so the indirect term `-rj / rn_j^3` is recomputed per tracer per DOP853 step, and `rom_closure.PerturbedParticle._rhs` adds extras the same way. Batching would only help a ROM multi-tracer path that used `particle_brain`; the validated multi-tracer fitter does not — `perturber_fitter.predict_positions` puts all tracers in one REBOUND simulation.
- Verdict: batching is a real but narrow ROM-particle optimization, not a TNO win and not a verdict change. Do not budget it as a TNO speedup.

### 1.3 Lookup tables — the rails spline IS the table; no sin/cos or 1/r^3 table exists
- Live computation in the main paths: `math.cos/sin` and `np.cos/sin` for candidate phases (`perturber_fitter.py`, `tno_hunt_40yr_seg.py`), and `1/r^3` via `|d|^3` / `**1.5` norms. No precomputed sin/cos or `1/r^3` grid was found in the audited files.
- The rails spline is the existing lookup table for planet positions, validated (per the particle-brain header) to <1e-6 AU vs REBOUND over 21 yr. The paste's caveat is the binding rule for any new table: spacing must be validated below the applicable noise floor, and there are two different floors in play — 1e-7 AU noise in the fitter harness, 7.04e-5 AU in the ROM synthetic datasets. A table validated against one floor is not automatically valid against the other.

### 1.4 Fixed timestep — SPLIT: true for the TNO hunt, false for the ROM particle
- TNO: fixed `DT_FINE = 0.004` yr RK4 for the null and injections, `DT_VAR = 0.04` yr for the variational model. Segment bounds `b_idx` and the sorted tracer list `TN` give deterministic ordering.
- ROM: `NBodyParticle` uses adaptive DOP853 (`rtol=1e-9, atol=1e-11`), not a fixed step. The paste's "your RK4 already uses a fixed DT_FINE" is true only of the TNO code.
- Reproducibility items from the paste: deterministic seeds exist in the fitter/checker paths (`seed` arguments), and the ROM ledger identity exists, but the ledger's `model_version` is a constant "1" — software/library versions are not recorded in the identity. That is a small, real gap for a "replay-safe" claim.

### 1.5 Broad phase then narrow phase — the paste states the rule correctly; the code does not yet obey it everywhere
This repeats the earlier audit's finding, because it is the finding that matters most here:
- Eccentric fitter: top-K screens (case 16: the truth ranked 25th/34th on the coarse screen, then recovered only under the fine-mass search v4).
- TNO `run_grid`: top-5 refinements; non-refined candidates are not carried forward.
- Tracker `prune(min_prob=1e-6)`: drops hypotheses with no bucket-ledger entry (the null is never pruned, and pruning never leaves fewer than 2 hypotheses — those are the only guards).
- Until a ScreenRecord + coverage accounting + defined reentry trigger design lands, "broad phase prioritizes" is a design requirement, not a description of the code. The arcade paste's formulation ("a low rank means evaluate later") is compatible with that design and does not by itself fix the three elimination sites.

### 1.6 Level of detail — tiers exist in pieces; the ladder as stated does not
- LOD 0 (cached baseline/rails): yes — ROM rails cache, TNO segmented null.
- LOD 1 (linear tidal perturbation): TNO only, via `var_eval` on `T_var`. The ROM closure has no linear tidal candidate model; its candidate fit is full DOP853 integration.
- LOD 2 (secular element-drift model): NO fit model. `real_data/secular_elements.py` provides only `cart_to_elements` / `elements_to_cart` conversions (plus a barycentric helper). A drift-rate model is not a candidate evaluator in either codebase.
- LOD 3 (full nonlinear N-body): yes — REBOUND ias15 in the fitter, DOP853 in the ROM, RK4 in the TNO hunt.
- The "promote, never discard" rule for the ladder is the same rule as §1.5 and has the same current gap.

### 1.7 Object pooling — real but unprofiled
- The code allocates fresh arrays per call in the hot paths: `traj = np.empty(...)` per segment, `ep = np.empty(...)` per `var_eval`, `deltas` per `var_eval`, and `sample_epochs` builds a new CubicSpline per tracer per segment. ROM `ExtraRails` builds its splines once per object; `positions()` allocates per call.
- Pooling/reuse is therefore a plausible low-risk optimization, but no profile in this audit shows allocation is the bottleneck (the measured bottlenecks elsewhere are integration steps and NM evaluations). Do not claim a win before profiling.

### 1.8 Update only what changed — PRESENT in both codebases
- TNO inject: `inject_and_recover` computes `sig = s_inj - null_pred` with the comment that re-integrating the null would be redundant; the production segmented null is computed once and shared by injections.
- ROM: `fit_candidate` computes the baseline once and reuses it (with the enforced `baseline_provenance` guard from the correctness batch), and warm-starts the candidate fit from the baseline state via `x_hint`. The candidate evaluator need not match the baseline evaluator, and the mismatch is labeled (`baseline_extra_evaluator`), not hidden.

### 1.9 Scroll windows — PRESENT, and the paste's warning is already demonstrated
- The TNO hunt is 4 x 10-yr segments, re-initialized from Horizons at each segment start; the variational state re-initializes to zero at each segment start, and the code comment states the candidate's pre-segment effect is absorbed into the Horizons re-initialization.
- The earlier sensitivity finding stands: segmentation improves systematics but truncates coherent long-arc signals. A moving window is therefore not a free efficiency win; segment boundaries are reinitializations with a known signal cost, and any window design must carry that cost in its spec.

### 1.10 What the paste says not to borrow — AGREED, with one note
Fixed-point arithmetic, palette compression, hardware timing exploits, aggressive culling, and frame-rate stepping are all correctly rejected. The culling point is the only one with live code consequences (§1.5): in this codebase "cull" must mean `defer_to_bucket` (recorded, re-enterable), never `prune` (dropped) and never a screen rank treated as a verdict.

## 2. Modern techniques

### 2.1 Multi-fidelity search — the table is aspirational, not current
Using the paste's own F0–F3 labels: F0 (cached rails/null/tidal) exists in pieces (§1.1); F1 (first-order tidal) exists only in the TNO hunt; F2 (secular drift) does not exist as a fit model (§1.6); F3 (full nonlinear) exists. There is no formal model of how F1 and F3 disagree — no learned discrepancy, no correction, no cost-aware acquisition. The discipline the paste states (F1/F2 rank, F3 alone promotes) is correct and is the same rule as §1.5; the machinery to enforce it as a scheduler does not exist yet.

### 2.2 Reduced-order baselines — ABSENT in the POD sense
No principal trajectories, POD modes, compressed coefficients, reconstruction operator, or error estimator was found in the audited files. The segmented null is a baseline, not a reduced-order model in this sense, and `T_var` is a sensitivity (Jacobian) along that baseline, not a reduced state. Calling the null a ROM overstates what exists; a true reduced-order baseline would be a new component with its own validation (reconstruction error vs the full model, validity region, escalation rule).

### 2.3 Differentiable, compiled kernels (JAX) — ABSENT
A scoped grep over the audited pipeline files (`*.py`, TNO seg/inject, `rom_closure.py`, `rails_brain.py`, `particle_brain.py`, `perturber_fitter.py`) found zero uses of JAX, GPU, or CUDA. (An unscoped recursive grep over the whole tree returns hits only from vendored third-party packages under `source_upload/.venv`, which are not project code.) A JAX kernel would therefore be a new execution path, not a patch: same equations, compiled and batched, but requiring an equivalence study against the existing NumPy/RK4, DOP853, and REBOUND paths at the applicable tolerances before it could be authoritative. The paste's GPU-reduction caveat applies equally to CPU XLA fusion: fused operations can change floating-point results, so "same equations" is not the same as "same numbers."

### 2.4 GPU acceleration — ABSENT, and the paste's own scope limit is correct
No GPU code exists in the audited files. The structural point stands: 340 tracers, 11 rail bodies, fixed rails, and the dominant cost is repeated candidate evaluation, not an O(N^2) many-body problem — so Barnes–Hut is not the bottleneck's answer (§3 also). A GPU batch candidate evaluator is a plausible screening device, but only under the §1.5 rule: it ranks, the CPU full-physics path confirms, and a low GPU rank never eliminates a region.

### 2.5 Bayesian active learning — ABSENT
The inventor is surprise-triggered and rule-based (`hypothesis_inventor.py`: `invent_from_best`, `invent_grid_fill`, perturb/swap/add-body variants), not a Gaussian process, and there is no acquisition function (expected improvement, uncertainty reduction, cost-adjusted information gain) anywhere in the audited files. There is also no maintained uncertainty over mass/distance/phase/eccentricity as a scheduler input. The safeguard the paste states is already the design constraint for any such addition: the scheduler chooses what to evaluate next; it must not feed posteriors, which today derive only from calibrated verdicts (a safeguard by absence that a GP design must preserve explicitly).

### 2.6 Active learning for the surrogate — ABSENT
There is no surrogate training loop: high-fidelity results are not fed back into a cheap model. The TNO grid + refine is a fixed grid, not adaptive, and the ROM inventor loop is verdict-driven, not surrogate-driven. The feedback loop in the paste ("the more the ROM runs, the better it becomes at deciding where expensive compute is worth spending") would be a new component, and its training data would need the same provenance discipline as the ledger — a surrogate trained on screened results inherits the screen's biases unless coverage is recorded.

### 2.7 Error-aware trust regions — ABSENT
No trust radius, no cheap-model error estimator, and no escalation rule based on estimated error vs signal or noise floor was found. The checker gives holdout RMS vs sigma, but that is a verdict on a completed fit, not a trust-region decision during a search. "Near the noise floor or outside its trust region, escalate" is a sound rule to write into a future spec; it is not a rule the code currently implements.

### 2.8 Sparse derivatives and adjoints — ABSENT
The optimizers are derivative-free or numeric-Jacobian: Nelder–Mead for perturber parameters (`perturber_fitter.refine`), and scipy `least_squares` (method LM) for tracer states (`optimizer_brain.fit_state`), whose Jacobian is numeric. There is no autodiff, no adjoint, and no analytic Jacobian of a trajectory with respect to candidate parameters. A differentiable integrator + rails + scoring stack is a separate prototype, as the paste says — not a patch to the ROM.

### 2.9 What the paste says to avoid for now — AGREED
Neural surrogates as the primary physics model, Barnes–Hut now, GPU as default authority, and Bayesian optimization without a guardrail are all correctly deferred. Each would need the validation and guardrail work described above before it could be more than a scheduler.

## 3. Galaxy / cluster / supercluster scale

### 3.1 The scale change is real, and the paste's table is accurate about the current code
Current scope: a handful of known perturbers, 340 TNO tracers (TNO hunt) or a few synthetic tracers (ROM/fitter), over decades, with fixed rails + test particles. Galaxy/cluster/cosmological scope (millions to billions of particles/cells over gigayears) is not a parameter change to this code; it is a different solver, representation, and time model, as the paste says.

### 3.2 Representation — a field component type does not exist
- Current bodies are (mass, radius, phase) circular coplanar triples in the tracker/inventor, plus (mass, a, e, M0) eccentric bodies in the fitter v3. There is no field-component type: no particle cloud, no grid field, no analytic halo profile. A scoped grep found no NFW/Einasto profile in the mapper code (the only "halo" hits are the unrelated gamma-ray halo flux in the PBH classifier).
- The paste's three-way split (resolved body / field component / tracer) is therefore a new type system, not a relabeling. The hard rule from the module program applies unchanged: a field component earns a blind-fit place only with its own validated physics.

### 3.3 Solvers — only direct/small-N integration exists
- Present: REBOUND ias15 (fitter), DOP853 (ROM particle), fixed RK4 (TNO hunt). These are direct integrations of a few bodies plus test particles.
- Absent (scoped grep, zero hits in the audited pipeline files): Barnes–Hut tree, particle–mesh, tree-PM, AMR. The paste's mapping is sound — direct for validation/small systems, tree-PM as the general production candidate, PM for broad tidal fields, AMR where local resolution matters — but every one of those is a new solver to validate, not an existing capability to invoke.

### 3.4 Field brain — rails_brain is an analogy, not a generalization
`rails_brain.PlanetRails.positions(t)` returns fixed positions for exactly 8 planets, and `particle_brain.NBodyParticle._rhs` hardcodes 8 planet rails. Generalizing that to a `field_brain` means a new interface (field evaluation at a position/time, not a fixed planet list), plus provenance per field (solver, force tolerance, softening, resolution, particle count where applicable). Renaming `rails_brain` would not do it; the interface and its validation are the work.

### 3.5 Cosmological time — ABSENT
Time throughout the current code is years since J2000 (`rails_brain` contract; `t_ref` in ROM datasets). A scoped grep found no scale factor, comoving coordinates, redshift, Hubble parameter, or cosmology parameters (H0, matter/dark-energy density, curvature) in the audited files. The paste's comoving equation of motion is new physics for this codebase, and adopting it would require a new time/coordinate layer, not a unit conversion.

### 3.6 Softening — only the belt exception exists, and it is not a galaxy policy
The only softening in the audited code is in `real_data/belt.py`: Plummer softening eps = 1.0 AU, explicitly representing the belt's vertical scale height, with the comment that it removes the log-cusp. That is belt physics, not a softening policy. There is no `softening_policy` module, no recorded kernel/resolution limit for other paths, and the point-mass paths are intentionally unsoftened. The paste's requirement — record softening length, kernel, fixed/comoving/adaptive choice, force-accuracy target, resolution limit, and mass sensitivity — is correct and currently unmet for any galaxy-scale field.

### 3.7 The paste's module list, checked one by one
- `field_brain`: analogy only (§3.4).
- `tree_gravity`, `pm_gravity`, `tree_pm_gravity`: absent.
- `softening_policy`: absent except the belt exception (§3.6).
- `cosmology_clock`: absent (§3.5).
- `initial_conditions`: absent as a generator; Horizons ingestion is not initial-condition generation from a power spectrum.
- `halo_catalog`: absent.
- `observer_frame`: absent beyond the fixed ecliptic-J2000 frame; no comoving/physical/peculiar/observable conversion layer.
- `survey_model`: absent (no selection effects, no light-cone).
- `multi_fidelity_rom`: absent as defined in §2.1.
- `validation_suite`: partial only — `checker_brain` + holdout gates validate fits, but there is no energy/momentum/convergence/cross-code suite for a galaxy field.

### 3.8 Roadmap stages — Stage 1 is a new system, and it does not bypass the picked module order
- Stage 1 (galaxy prototype: halo particles or analytic profile, stellar disk, central black hole, tracer stars, tree or direct gravity, no gas) would be a new build whose tracer/ROM-ledger concepts transfer but whose validated results do not yet exist. It needs its own predeclared bar before any "inference works at galaxy scale" claim.
- Stages 2 (cluster) and 3 (cosmological volume) depend on Stage 1 validation and on modules (halo catalogs, survey model, IC generation) that do not exist.
- Sequence note: Jase's picked order is gas first (design brief only, no build), halo second, with cosmological hydrogen excluded from gas v1. A galaxy prototype does not automatically jump that queue, and a galaxy halo is not the same deliverable as the picked halo module unless Jase says it is. If he wants the galaxy prototype to reorder the queue, that is a decision to record explicitly, not an inference from this audit.

### 3.9 What the ROM uniquely adds — AGREED in principle, with a ledger extension required
The paste's distinction is right: most cosmological codes evolve given initial conditions; the ROM asks what unseen mass distribution best explains observed tracer behavior. That inference-layer role is consistent with the existing design (cheap proposes, full confirms, ledger records the tier). For galaxy fields, the ledger would additionally need to record the field solver, tolerance, softening, and resolution for every conclusion — the paste's preparation item 3 — because a "detection" from a tree-PM field is not interchangeable with one from a direct field without that record.

## 4. Corrections to the pastes (small, but recorded so they do not drift into the record)

1. Arcade paste, "your RK4 already uses a fixed DT_FINE": true for the TNO hunt only; the ROM particle is adaptive DOP853 (§1.4).
2. Modern paste, "your existing segmented null is already a kind of reduced-order baseline": overstated. It is a baseline; it is not a POD/reduced-order model, and the ROM closure has no tidal tensor at all (§2.2, §1.1).
3. Modern paste, "the existing first-order variational machinery is valuable" for update-only-changed: true for the TNO hunt; the ROM closure's reuse mechanism is baseline reuse + warm-start, not a variational model (§1.8).
4. Galaxy paste, "your current particle brain is already a tracer propagator": true, but it is a single-tracer propagator with 8 hardcoded rails, not a generic tracer through an arbitrary field (§3.4).
5. Arcade paste, sprite batching as a TNO win: corrected in §1.2 — the TNO code already batches by time; the remaining batching opportunity is ROM-particle only.

## 5. Recommended order if Jase commissions any of this (audit opinion, not authorization)

1. Finish the compliance gap first: ScreenRecord + coverage + reentry triggers for screens/subsets (§1.5), because every scheduler in pastes 1 and 2 (LOD, multi-fidelity, GPU batching, Bayesian scheduling) inherits the elimination bug if it lands first.
2. Then the cache items with the key extensions from the earlier audit (full rails-coefficient hash, TNO null fingerprint + cross-run loader, seed/n_starts/holdout_frac in ROM persistent keys).
3. Then, separately specced: a secular (F2) candidate model, or a JAX/CPU compiled-kernel prototype with an equivalence study — one at a time, not both at once.
4. Galaxy work only after a Stage-1 spec with a predeclared bar, and only in the module order Jase sets (gas, then halo, unless he reorders it explicitly).
5. Neural surrogates, Barnes–Hut as the production solver, GPU as authority, and any GP scheduler that feeds posteriors: not before items 1–3 and their validations.

## 6. What was NOT done

No code was written, modified, or deleted. No file was moved to Drive. No new solver, kernel, scheduler, or galaxy module was built. No verdict, promotion, or elimination was changed. The eccentric search-v4 re-run was not inspected for progress and its outputs were not used here.
