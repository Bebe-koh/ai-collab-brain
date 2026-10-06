# Observing requirements for the Kerr/CS calibrator-differential transient test
**Date:** 2026-10-03 · **Status:** planning memo, no new data.
**Prereads:** `blindspot_free_observable_note.md` (round 1, patched [C2]),
`blindspot_synthetic_test_note.md` (round 2), `eht_kerrcs_null_bound_note.md`,
`closure_phase_derivation_note.md` (+2026-09-24 addendum).

## 0. The one-paragraph version

To execute the blind-spot-free transient test for real, a future EHT/ngEHT
run needs: **(1)** interleaved scans of ≥1 bright polarized calibrator — the
piece missing from the 2017 public release — cycled as fast as operations
allow; **(2)** a calibrator-only step search run as the *primary*
instrumental-jump veto, because the differential construction cannot suppress
jumps that fall between calibrator scans; **(3)** dump sampling Δt ≲ τ/5 for
guaranteed transient resolution (10-s dumps for Sgr A*'s τ=46.9 s), with
coarser sampling degrading detection per a sample-phase lottery
(P ~ 2τ/Δt) rather than re-blinding; **(4)** multi-band (86/230/345 GHz)
coverage for the achromaticity-vs-Faraday identification check; **(5)** the
amplitude-aware least-squares estimator for parameter recovery, not the
amplitude-normalized matched filter. Nothing here requires ngEHT, but ngEHT
helps on every axis.

## 1. Calibrator program (the missing piece)

- **Which calibrators:** bright and strongly polarized — 3C 279, J1924-2914,
  NRAO 530. Prefer **≥2** for the A3 consistency check (a calibrator must not
  itself carry a slip-like transient on the τ timescale; AGN variability is
  broadband, not a 46.9-s tanh, but two calibrators make this checkable rather
  than asserted).
- **Brightness is a selection criterion, not a nice-to-have.** The round-2
  simulation assumed a bright calibrator (2× target amplitude). A weakly
  polarized calibrator needs the jump-subtraction variant (round-1 note §4),
  which was not covered by the synthetic test.
- **Cadence: as fast as operations allow — but understand what it buys.**
  Round-2 Exp D (60-s calibrator scans) found:
  - jumps *within* calibrator scans: suppressed ×13–17, stay silent, at
    120/300/600-s cadence;
  - jumps *between* calibrator scans (mid-gap): **unsuppressed** — ×1 at
    300-s cadence (residual step 1.97 of 2.00, spurious matched-filter
    detections at 100%), ×7 at 120-s cadence (residual 0.28, still spuriously
    detected).
  So cadence does **not** buy differential suppression of mid-gap jumps.
  What faster cadence buys: (a) a smaller corrupted window per jump,
  (b) a smaller fraction of observing time exposed (vulnerable fraction ≈
  1 − scan/cadence — e.g. ~80% at 60-s scans every 300 s), and (c) more
  pre/post samples for the calibrator-only step search that actually rejects
  them. **Design the schedule for veto efficiency, not interpolation
  fidelity.**
- Interleaving itself costs little sensitivity: slip detection with an
  interleaved (jump-free) calibrator degraded only 0.97 → 0.86 (det@1%).

## 2. The veto chain is the primary defense (design it first)

Run vetoes in this order; a candidate transient must survive all:

1. **Calibrator-only step search (PRIMARY jump veto).** Search Q_cal(t) alone
   for inter-scan steps. Any calibrator step flags the surrounding gap as
   contaminated; those windows never reach the matched filter. This is what
   catches mid-gap jumps — the differential cannot. Build and validate this
   pipeline on synthetic jumps *before* the run.
2. **Swapped differential** (calibrator as "target"): any transient here =
   instrumental, veto.
3. **RR/LL closures and the RL+LR sum channel** (slip-invariant per
   derivation note §5): steps here veto as gain glitches or source structure.
4. **Multi-band achromaticity:** identical −12Δχ(t) winding at 86/230/345 GHz.
   A λ²-scaling step is Faraday rotation — it rules out the θ *model*, not
   just the event.
5. **Sign/rate consistency:** the slip winding direction is fixed by the
   model; instrumental jumps are random-sign.

Significance throughout: circular time-shift surrogates of r(t),
look-elsewhere corrected over the (γ_t, t₀) grid (EHT pipeline practice).
Detection *fractions* at fixed empirical FPR are the honest metric — the
null is max-over-grid, so raw margins are modest by construction.

## 3. Sampling guidance: the lottery table

- **Guaranteed resolution:** Δt ≲ τ/5. Sgr A* (τ=46.9 s) with 10-s dumps —
  standard EHT dump rates already qualify.
- **Coarser sampling:** sample-phase lottery, not a hard blind spot.
  Heuristic from the round-2 grid: P(detect) ~ 2τ/Δt (order-of-magnitude;
  blind only when the full 2πk winding falls inside one inter-sample
  interval). Worked examples for Sgr A* (τ=46.9 s):

  | Δt | 10 s | 100 s | 200 s | 600 s |
  |---|---|---|---|---|
  | regime | resolved | lottery | lottery | lottery |
  | P(detect) ~ | ~1 | ~0.9 | ~0.5 | ~0.16 |

- **M87*** (τ=18 h): sampling is trivially fine at any realistic dump rate;
  the binding constraint is red noise over the long ramp, not the sampling.
- Budget rule: if operations force coarse sampling, the lottery math — not
  a blind-spot claim — sets the sensitivity loss.

## 4. Analysis pipeline (round-2 corrections baked in)

- **Detection:** max-over-(γ_t,t₀)-grid matched filter of (r−1) against the
  exact nonlinear tanh template, empirical FPR from null surrogates.
- **Estimation:** amplitude-aware least squares,
  χ²(γ_t,t₀) = Σ_t|r(t)−1 − u(t;γ_t,t₀)|², template at natural amplitude.
  Do **not** use the round-1 Eq. 10 amplitude-normalized form — it discards
  amplitude information and is flat in the linear regime, which is exactly
  the information that breaks the mod-1/12 aliasing. Round-2: zero alias
  picks at per-sample σ ≤ 0.4.
- **Ambiguity lifting at high S/N:** continuous phase unwrapping through the
  ramp (valid while |ΔΦ|<π per sample; γ≲0.39 at 10-s sampling; synthetic:
  γ̂=0.0809±0.0006 at σ=0.05).
- **Do not use the free-t₀ step search as an identification cross-check:**
  it is *not* blind at k/12 (~100% detection via the partial-winding
  amplitude dip) but the detection carries the wrong morphology — the
  transient leaking into a step statistic. Detection-only sanity check at
  best.

## 5. Multi-band: needed for identification, not detection

- 86/230/345 GHz. Neither the blind-spot fix nor the degeneracy fix needs
  multi-band; distinguishing a θ slip from Faraday rotation does.
- Requires coordinated multi-band campaigns (not standard single-band EHT
  tracks) — an operational cost to budget in the proposal.

## 6. Which arrays can do this

- **EHT (current):** 10-s dumps already satisfy the Sgr A* sampling
  requirement. The binding constraints are operational, not hardware:
  interleaved calibrator scans at the fastest sustainable cadence, the
  pre-built veto pipeline, and multi-band coordination. A first execution
  needs no new hardware.
- **ngEHT:** faster cadence (smaller vulnerable fraction, sharper veto),
  more stations (better S/N on the stacked phasors), longer tracks, better
  per-sample S/N (helps phase unwrapping). Improves every axis; not required
  by the construction.
- **2017 public Sgr A* data:** cannot run this test — no calibrator scans in
  the release. The data requirement is structural, not a reprocessing gap;
  do not attempt a re-analysis.

## 7. Shopping list (checklist for the observing proposal)

- [ ] ≥1 bright polarized calibrator (3C 279 / J1924-2914 / NRAO 530),
      ideally 2, interleaved at fastest sustainable cadence
- [ ] Calibrator-only step-search veto pipeline built and validated on
      synthetic jumps *before* the run
- [ ] Dump sampling Δt ≲ τ/5 (10 s for Sgr A*); lottery budget if coarser
- [ ] Amplitude-aware LS estimator in the analysis chain (not Eq. 10
      normalization)
- [ ] Multi-band (86/230/345 GHz) for the Faraday identification check
- [ ] Null-surrogate significance machinery (circular shifts, look-elsewhere
      over the (γ_t,t₀) grid)
- [ ] Swapped-differential + RR/LL + sum-channel vetoes
- [ ] Pre-registered (γ_t, t₀) grid and FPR thresholds

## 8. What would change this memo

- A measured instrumental-jump rate/profile from EHT engineering data would
  turn the cadence guidance from heuristic to quantitative (how much
  observing time the veto actually eats).
- A real noise propagation for closure-phase stacking (open item A6 in the
  round-1 note) would turn the lottery heuristic and the detection fractions
  into proper sensitivity forecasts.
- If the tanh/τ model inputs are revised, §§3–4 rescale directly —
  everything is stated in units of τ.
