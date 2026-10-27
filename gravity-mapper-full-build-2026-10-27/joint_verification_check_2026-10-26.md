# Joint Prototype Verification Check — 2026-10-26 (Atlas)

**Purpose:** check the joint prototype batch's records and its
regression impact, in the same spirit as the bucket verification
rerun. This is NOT a re-execution of the prototype's own fits.

## What Atlas checked directly

- **Files:** only new files under `hidden_files/` —
  `joint_prototype_plan_2026-10-26.md` (22:46),
  `joint_model_spec.py`, `joint_driver.py`, `joint_checker.py`,
  `joint_prototype_tests.py`, `joint_prototype_results_2026-10-26.json`
  (23:06). No existing file carries a joint-batch timestamp;
  `hypothesis_tracker.py`, `rom_closure.py`, `rom_history.py` still
  carry the bucket batch's times.
- **Scope:** grep finds no `rom_closure` import and no live-ROM
  contact in the joint files; the results file itself records
  `live_rom_contact = False`, `existing_files_modified = []`,
  `rom_closure_imported = False`.
- **Prospectivity:** the plan (22:46) predates the results file
  (23:06), and the D10/D11 values in the results file match the plan
  exactly — D11 rel RMS / rel a ≤ 1e-4, abs e ≤ 1e-4; D10 scan
  offsets [0, −1, +1, −2, +2] decades, bounds ±3 decades.
- **Results-file cross-check:** every number in the batch report
  matches `joint_prototype_results_2026-10-26.json` exactly —
  k=0 proof differences all 0.0; k=1 fitted mass 9.846175782370942e-05
  Msun (−0.00673 decades); checker PASS; holdout MSE ratio
  78.06005585096727; removal claim `contribution_supported`.
- **Regression suites, newly executed by Atlas after both batches:**
  audit fixes 20/20, phase2b 16/16, correctness 38/38, calibration
  13/13, bucket conservation 85/85 — **172 checks, 0 failures**.
- **Live ROM md5 after both batches:**
  `4c77b723ff5770566a85ed4e580aed2c` — unchanged.

## What Atlas did NOT do

- **Did not re-execute the prototype's proof/demo fits** (k=0 ~54 s,
  k=1 fit ~235 s, checker ~362 s in the batch's run). Those numbers
  rest on the batch's run, cross-checked above against its results
  file and plan — not on an independent Atlas fit run. The batch
  itself did re-run the harness once after fixing a prototype bug
  (see below), and that re-run reproduced the k=0 proof exactly.
- Did not assess D12/D14 (caps / cost acceptance) — those are Jase's
  decisions after measurement, not part of this check.

## Batch-disclosed items carried over, not hidden

- **First demo run crashed** with `ValueError: incompatible
  dimensions for cross product` — a prototype slicing bug
  (`sol.x[3:]` fed a 4-vector to `cart_to_elements`). Fixed in the
  new `joint_driver.py` only (`sol.x[3:6]`), harness re-run, k=0
  proof reproduced exactly before the demo passed. Not a D10/D11
  failure and not a plan change.
- **Convention flag:** the prototype computes μ_j =
  10^(logmass_j) × MU_SUN, while `rom_closure.PerturbedParticle`
  passes inventor masses directly as `extra_mus` (no MU_SUN factor).
  The demo is self-consistent under the prototype convention only
  and must not be quoted as a rom_closure candidate-fit result.
  Reconciliation is a promotion-time item.
- **Cost reading:** predict cost flat in k (~1.4 s; rail propagation
  dominates). Fit/checker cost is LM-evaluation count × predict
  cost, not k itself at these sizes. k=2/3 fits were not run and no
  k=2/3 cost is extrapolated here.
- **No uncertainties:** fitted-mass uncertainties are null ("not
  available from LM driver").

## What this does and does not do

This check confirms the prototype batch stayed in scope, set its
bars before running, and did not regress the existing suites. It
does NOT accept the prototype, promote it into live code, authorize
open-question Stage B use, ingest anything into the live ROM, or
upload anything to Drive. All of those remain separate decisions.

---

*Check, 2026-10-26 late evening. No code changed, no thresholds
changed, no ROM entries modified by this check.*
