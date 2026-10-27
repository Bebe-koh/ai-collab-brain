#!/usr/bin/env python3
"""Eccentric-secondary validation harness, SEARCH V2 (2026-10-27).

Identical cases to eccentric_fitter_test.py (same truths, same noise
seeds, same tracers, same span) -- ONLY the search changed (now
search v3, see below).

Search history:
  - v1: circular screen (2.5 -> 5.0 AU gap) + e-scan top-3 + 2+2
    joint seeds -> 9/20.
  - v2: ECC_RADIUS_GRID (3.0, 3.5, 4.0, 4.5 added) + e-scan top-6 +
    3+3 joint seeds -> smoke on case 16 FAILED IDENTICALLY to v1
    (same fitted body to 4+ figures), ruling out grid resolution.
  - v4 (current): 4D eccentric screen with 0.25-dex mass grid
    (MASS_GRID_FINE) + 3+3 joint seeds. A fine-mass screen test on
    case 16 put truth-neighborhood cells at ranks 0/1/3.

PREDECLARED ACCEPTANCE (written before any v2 run):
  20/20 cases recovered under this single search version, where
  recovered means mass <= 10%, a <= 5%, e <= 0.05 (legacy tolerances).
  The v1 record (9/20) is preserved separately and is NOT overwritten:
  outputs here are eccentric_case_v2_XX.json and
  eccentric_fitter_results_v2.json. If fewer than 20/20 recover, the
  verdict stays 'legacy tolerances not met on real dynamics' and the
  failure pattern is diagnosed again from the v2 per-case files.

Case design, checkpointing, and scoring are unchanged from v1
(see eccentric_fitter_test.py header for the legacy-bar correction
and the a-range adaptation rationale).
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eccentric_fitter_test import make_ecc_case, score_ecc_case  # noqa: E402
from perturber_fitter import run_eccentric_fit  # noqa: E402

N_CASES = 20
HERE = Path(__file__).resolve().parent


def case_path(i):
    return HERE / f'eccentric_case_v2_{i:02d}.json'


def write_summary(results):
    rec = sum(1 for r in results if r['recovered'])
    summary = {
        'n_cases': len(results),
        'recovered': rec,
        'mean_mass_rel_err': float(np.mean([r['mass_rel_err']
                                            for r in results])) if results else None,
        'mean_a_rel_err': float(np.mean([r['a_rel_err']
                                         for r in results])) if results else None,
        'mean_e_abs_err': float(np.mean([r['e_abs_err']
                                         for r in results])) if results else None,
        'search_version': 'v4 (4D eccentric screen, 0.25-dex mass grid, 3+3 joint seeds)',
        'cases': results,
    }
    (HERE / 'eccentric_fitter_results_v2.json').write_text(
        json.dumps(summary, indent=1))
    return summary


def main():
    results = []
    for i in range(N_CASES):
        if case_path(i).exists():
            r = json.loads(case_path(i).read_text())
            results.append(r)
            print(f'case {i:02d}: SKIPPED (result exists) '
                  f"recovered={r['recovered']}", flush=True)
            continue
        print(f'case {i:02d} ...', flush=True)
        case = make_ecc_case(i)
        t0 = time.time()
        report = run_eccentric_fit(case['tracer_states'],
                                   case['ts_train'], case['obs_train'],
                                   case['ts_hold'], case['obs_hold'])
        dt = time.time() - t0
        scored = score_ecc_case(i, case['truth'], report)
        scored['runtime_s'] = dt
        case_path(i).write_text(json.dumps(scored, indent=1))
        results.append(scored)
        write_summary(results)
        print(f"case {i:02d}: recovered={scored['recovered']} "
              f"mass={scored['mass_rel_err']:.2%} "
              f"a={scored['a_rel_err']:.2%} "
              f"e={scored['e_abs_err']:.4f} ({dt:.0f}s)", flush=True)
    summary = write_summary(results)
    print(f"TOTAL: {summary['recovered']}/{summary['n_cases']} recovered; "
          f"mean mass={summary['mean_mass_rel_err']:.2%} "
          f"a={summary['mean_a_rel_err']:.2%} "
          f"e={summary['mean_e_abs_err']:.4f}", flush=True)


if __name__ == '__main__':
    main()
