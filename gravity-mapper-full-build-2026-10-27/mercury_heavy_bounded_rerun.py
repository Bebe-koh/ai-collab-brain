#!/usr/bin/env python3
"""Mercury+heavy rerun with the BOUNDED fitter (bounds added 2026-10-27).

The twice-confirmed mercury/heavy console results were computed with
the pre-bounds fitter. Their solutions lie inside the bounds, but the
paths may have differed, so this reruns both cases with the current
bounded fitter to give the v2 record a single code version. Same v2
config as mercury_fitter_test_v2.py (truths, per-case noise seeds,
tracers, span, gate, uninformative starts). Output:
mercury_fitter_results_mercury_heavy_bounded.json (merged with the
post-bounds null result into mercury_fitter_results_v2.json).
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mercury_fitter_test_v2 import CASES, make_case, score_case  # noqa: E402
from perturber_fitter import run_blind_fit  # noqa: E402


def main():
    out = {}
    for name in ('mercury', 'heavy'):
        truth, noise_seed = CASES[name]
        print(f'case {name} (bounded fitter, v2 config) ...', flush=True)
        case = make_case(truth, noise_seed)
        t0 = time.time()
        report = run_blind_fit(case['tracer_states'], case['ts_train'],
                               case['obs_train'], case['ts_hold'],
                               case['obs_hold'])
        dt = time.time() - t0
        scored = score_case(name, truth, report)
        scored['runtime_s'] = dt
        scored['full_report'] = report
        out[name] = scored
        print(f"  verdict={scored['verdict']} "
              f"ratio={scored['holdout_ratio']:.3e} ({dt:.0f}s)",
              flush=True)
    out_path = Path(__file__).resolve().parent / \
        'mercury_fitter_results_mercury_heavy_bounded.json'
    out_path.write_text(json.dumps(out, indent=1))
    print(f'saved {out_path}', flush=True)


if __name__ == '__main__':
    main()
