# Null-case slowness: diagnosis (2026-10-27 ~01:30 PDT)

## What was observed

The instrumented null probe (`mercury_fitter_null_probe.py`, launched
2026-10-26 ~23:39 PDT) ran 107 minutes and reached eval 4152 of a
nominal ~6700 — then kept crawling, not hanging. Early evals ran at
~40/s (0.025 s each). By eval ~4100, **every eval took 82–90 s**.
Remaining evals at that rate: ~2500 × 87 s ≈ 60 hours, and worsening
if the drift continued. The probe was stopped: its diagnostic mission
was complete, and continuing it would have burned days for no new
information.

Evidence (preserved):
- `null_probe_evals.log` — all 4152 evals, flushed before each call,
  so the stall configuration is on record even though the probe was
  killed.
- Probe stdout (`agents/.../exec-logs/proc_8126da1159bb.log`) — SLOW
  lines for evals 4142–4151, each 82–90 s.

## Mechanism (measured, not guessed)

Nelder-Mead, on no-signal (null) data, has no gradient to follow, so
its simplex **drifts freely along flat directions** — and the fitter
put no bounds on its parameters. By eval ~4100 it had drifted the
"secondary" to:

- mass ~4.6e-13 Msun (negligible — it barely changes predictions, so
  nothing pulls it back), radius **~0.0027 AU**, phase ~4.32 rad,
  alongside Saturn (2.86e-4, 9.58, 4.75).

A body at 0.0027 AU orbits the Sun in ~1.2 hours. Over the 20-year
integration span that is **~142,000 orbits**, and ias15 must resolve
them all: ~87 s per predict. Eval cost scales as r^(-3/2) (orbit
count), so the slowdown is not a hang and not a bad integrator — it is
the optimizer wandering into a micro-orbit regime the fitter was never
designed to search. (For comparison: at the grid minimum 0.35 AU there
are ~97 orbits and evals cost ~0.06 s.) The killed probe's full stdout
confirms the scaling quantitatively: the drift runs smoothly from
radius 0.0336 AU / 2.0 s per eval (eval 3954) to 0.00236 AU / 110 s per
eval (eval 4100) — a 14× radius shrink predicting a ~54× slowdown by
r^(-3/2), against ~55× observed.

Contributing factors, all from the code:
- `refine()` passed no bounds to Nelder-Mead (parameters unbounded).
- `fatol=1e-18` essentially never triggers on noisy data, so null
  refines burn full `maxfev` instead of converging early.
- No per-predict timeout and no stage progress output (the probe was
  built to supply the missing visibility).
- The grid never goes below 0.35 AU and uninformative starts never
  below 0.3 AU — the 0.0027 AU configuration is far outside the
  designed search space. Mercury (0.39 AU) and the heavy case (2.5 AU)
  both converge inside the designed space, which is why they finish
  in ~4 minutes while null does not.

## Fix (applied 2026-10-27, `perturber_fitter.py`)

Bound Nelder-Mead to the **designed search space exactly** — this is a
bug fix, not a science change, because it excludes nothing the fitter
was designed to search:

- log10 mass in [-9, -3] (grid and uninformative range),
- log10 radius in [log10(0.3), log10(25)] (uninformative range;
  grid is 0.35–20),
- phase unbounded (already modulo 2pi).

With radii >= 0.3 AU, evals stay <= ~0.2 s and the null case returns
to its nominal ~11-minute budget. Mercury (1.66e-7, 0.39) and heavy
(3e-6, 2.5) truths and their fitted values all lie inside the bounds,
so the twice-confirmed mercury/heavy results are unaffected by the
fix in principle (their refines converged inside the designed space).

Deliberately NOT in this fix: a process-level per-predict timeout
(contingency if slow evals recur after bounding — e.g. close-encounter
slowdowns at orbit-crossing radii, which bounds alone do not prevent);
per-case checkpointing in the full harness (the null-only driver
sidesteps it for this rerun; the full harness still writes JSON only
at the end — a known follow-up).

## Status

- Probe stopped after serving its purpose (4152 evals logged).
- Bounds fix applied; direct bounds test passed (refine from an edge
  start returns parameters inside bounds).
- Null-only rerun launched with the fixed fitter (same v2 config:
  Saturn-only truth, noise seed 2, same harness functions). Expected
  ~15 minutes. Its verdict, merged with the twice-confirmed
  mercury/heavy console results, completes the v2 record.
