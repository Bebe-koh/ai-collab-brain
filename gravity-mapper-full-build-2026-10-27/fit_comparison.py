#!/usr/bin/env python3
"""Fit comparison: spline extras vs analytic extras (proposal 2 stage 2).

Harness only — no mapper source is modified. The analytic variant is
injected by monkeypatching rom_closure.ExtraRails during the analytic
run only; the spline run uses the real code path untouched.

Preserved configuration from rom_closure_lean.py: TRACER + BIG3 known
inventory + NOVEL_TRUTH as the candidate to recover. The same baseline
is reused for both variants, so only the candidate model differs.

Predeclared pass criteria:
  - same final verdict outcome (and reason) from
    verdict_for_candidate_detailed;
  - same candidate_check verdict;
  - candidate fitted-state max abs diff < 1e-6 (AU / AU-yr units);
  - holdout_mse_ratio relative diff < 1e-6.
Actual values are printed regardless of pass/fail.
"""
import math
import sys
import time

import numpy as np

HERE = '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files'
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + '/real_data')

import rom_closure
from rom_closure import (build_synthetic_dataset, fit_candidate,
                         verdict_for_candidate_detailed,
                         baseline_fingerprint_for)
from secular_elements import MU_SUN

MEARTH = 1.0 / 332946.0
BIG3 = [(1.571e-4 * MEARTH, 2.78, 0.0), (4.336e-5 * MEARTH, 2.37, 0.0),
        (3.419e-5 * MEARTH, 2.85, 0.0)]
TRACER = {'a': 40.0, 'e': 0.1, 'i': 0.087, 'Omega': 1.2, 'omega': 3.5,
          'M': 5.0}
NOVEL_TRUTH = (1e-4, 8.0, 1.0)
RAILS = HERE + '/sealed_runs/planet_rails.npz'


class AnalyticExtraRails:
    """Drop-in replacement for ExtraRails: direct circular formula."""

    def __init__(self, bodies, t_ref):
        self.bodies = list(bodies)
        self.t_ref = t_ref
        self.n = len(bodies)

    @classmethod
    def from_bodies(cls, bodies, t_ref, t_min, t_max, dt_days=0.5):
        return cls(bodies, t_ref)

    def positions(self, t):
        out = []
        for (m, r, p) in self.bodies:
            n = math.sqrt(MU_SUN / r ** 3)
            th = p + n * (float(t) - self.t_ref)
            out.append([r * math.cos(th), r * math.sin(th), 0.0])
        return np.array(out)


def summarize(tag, fres):
    cf = fres['candidate_fit']
    cc = fres['candidate_check']
    outcome, ratio, reason = verdict_for_candidate_detailed(fres)
    state = np.array(cf['r0_au'] + cf['v0_au_yr'])
    print(f"[{tag}] success={cf.get('success')} "
          f"rms={cf.get('rms_au')} check={cc['verdict']} "
          f"gates={cc['gates']} mse_ratio={fres['holdout_mse_ratio']} "
          f"verdict={outcome} reason={reason} "
          f"t_cand={fres['t_candidate_s']:.1f}s", flush=True)
    return state, outcome, reason, fres


def main():
    ds = build_synthetic_dataset(TRACER, BIG3 + [NOVEL_TRUTH],
                                 rails_cache=RAILS)
    # Novel body is the candidate to recover, not known inventory.
    ds['known_inventory'] = list(BIG3)
    print("dataset built; known=BIG3, candidate=NOVEL_TRUTH", flush=True)

    t0 = time.perf_counter()
    spline = fit_candidate(ds, [NOVEL_TRUTH], seed=0)
    print(f"spline run wall: {time.perf_counter() - t0:.1f}s", flush=True)
    s_state, s_out, s_reason, _ = summarize('spline', spline)

    baseline = (spline['baseline_fit'], spline['baseline_check'])
    baseline_prov = baseline_fingerprint_for(ds,
                                             spline['extra_evaluator'])
    orig = rom_closure.ExtraRails
    rom_closure.ExtraRails = AnalyticExtraRails
    try:
        t0 = time.perf_counter()
        analytic = fit_candidate(ds, [NOVEL_TRUTH], seed=0,
                                 baseline=baseline,
                                 baseline_provenance=baseline_prov)
        print(f"analytic run wall: {time.perf_counter() - t0:.1f}s",
              flush=True)
    finally:
        rom_closure.ExtraRails = orig
    a_state, a_out, a_reason, a_fres = summarize('analytic', analytic)

    state_diff = float(np.max(np.abs(s_state - a_state)))
    r_s = spline['holdout_mse_ratio']
    r_a = analytic['holdout_mse_ratio']
    rel_ratio = abs(r_s - r_a) / abs(r_s) if r_s else float('nan')
    print(f"state max abs diff: {state_diff:.3e}", flush=True)
    print(f"mse_ratio rel diff: {rel_ratio:.3e}", flush=True)
    ok = (s_out == a_out and s_reason == a_reason
          and spline['candidate_check']['verdict']
          == analytic['candidate_check']['verdict']
          and state_diff < 1e-6 and rel_ratio < 1e-6)
    print(f"FIT COMPARISON: {'PASS' if ok else 'FAIL'}", flush=True)


if __name__ == '__main__':
    main()
