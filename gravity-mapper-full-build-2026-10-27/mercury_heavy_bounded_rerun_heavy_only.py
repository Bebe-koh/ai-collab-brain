#!/usr/bin/env python3
"""Heavy-only rerun with the BOUNDED fitter (bounds added 2026-10-27).

The mercury+heavy bounded rerun was killed by a runtime restart during
the heavy two-body stage; mercury (bounded) had already completed and
reproduced the pre-bounds result exactly (TWO_BODY, ratio 1.004e+05).
This runs ONLY heavy with the same v2 config (truth, noise seed 1,
tracers, span, gate, uninformative starts) via the harness's own
make_case/score_case + perturber_fitter.run_blind_fit. Per-case seeds
make this the identical computation the full rerun would have
performed. Output: mercury_fitter_results_heavy_bounded.json.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mercury_fitter_test_v2 import CASES, make_case, score_case  # noqa: E402
from perturber_fitter import run_blind_fit  # noqa: E402


def main():
    truth, noise_seed = CASES['heavy']
    print('case heavy (bounded fitter, v2 config) ...', flush=True)
    case = make_case(truth, noise_seed)
    t0 = time.time()
    report = run_blind_fit(case['tracer_states'], case['ts_train'],
                           case['obs_train'], case['ts_hold'],
                           case['obs_hold'])
    dt = time.time() - t0
    scored = score_case('heavy', truth, report)
    scored['runtime_s'] = dt
    scored['full_report'] = report
    out_path = Path(__file__).resolve().parent / \
        'mercury_fitter_results_heavy_bounded.json'
    out_path.write_text(json.dumps({'heavy': scored}, indent=1))
    print(f"  verdict={scored['verdict']} "
          f"ratio={scored['holdout_ratio']:.3e} ({dt:.0f}s)", flush=True)
    print(f'saved {out_path}', flush=True)


if __name__ == '__main__':
    main()
