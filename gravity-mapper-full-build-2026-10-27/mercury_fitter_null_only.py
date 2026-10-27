#!/usr/bin/env python3
"""Null-only completion of the v2 fitter validation.

Two full v2 runs died on runtime restarts during the null case
(mercury + heavy already reproduced identically twice; see
mercury_fitter_results_v2_partial.json). This runs ONLY the null case
with the EXACT v2 config — same truth, same per-case noise seed (2),
same tracers/span/gate/uninformative starts — via the v2 harness's own
make_case/score_case plus perturber_fitter.run_blind_fit. Per-case
seeds make this the identical computation the full run would have
performed, not a different test.

Output: mercury_fitter_results_null_only.json (to be merged with the
partial record into the full v2 record when it lands).
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mercury_fitter_test_v2 import CASES, make_case, score_case  # noqa: E402
from perturber_fitter import run_blind_fit  # noqa: E402


def main():
    truth, noise_seed = CASES['null']
    print('case null (standalone, v2 config) ...', flush=True)
    case = make_case(truth, noise_seed)
    t0 = time.time()
    report = run_blind_fit(case['tracer_states'], case['ts_train'],
                           case['obs_train'], case['ts_hold'],
                           case['obs_hold'])
    dt = time.time() - t0
    scored = score_case('null', truth, report)
    scored['runtime_s'] = dt
    scored['full_report'] = report
    record = {'config': {'case': 'null', 'truth': [list(b) for b in truth],
                         'noise_seed': noise_seed,
                         'note': 'standalone rerun of the v2 null case '
                                 'after two full runs died on runtime '
                                 'restarts during null; identical config '
                                 'and per-case seeds to '
                                 'mercury_fitter_test_v2.py'},
              'cases': {'null': scored}}
    out_path = Path(__file__).resolve().parent / \
        'mercury_fitter_results_null_only.json'
    out_path.write_text(json.dumps(record, indent=1))
    print(f"  verdict={scored['verdict']} "
          f"ratio={scored['holdout_ratio']:.3e} ({dt:.0f}s)", flush=True)
    print(f'saved {out_path}', flush=True)


if __name__ == '__main__':
    main()
