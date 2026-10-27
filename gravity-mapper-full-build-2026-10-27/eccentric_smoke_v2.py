#!/usr/bin/env python3
"""Smoke gate for the eccentric search v2 fix (2026-10-27).

Runs ONE previously-failed case (16: truth 3.88e-06 / 3.84 AU / 0.214,
v1 fitted 3.88e-07 / 2.50 AU / 0.113 -- the archetypal mid-gap failure)
under the improved search. If it recovers, the mechanism is proven
and the full 20-case v2 run is launched; if not, diagnose before
burning ~100 min. Case definition is imported from the v1 harness,
so the truth is identical to the v1 run -- only the search changed.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eccentric_fitter_test import make_ecc_case, score_ecc_case  # noqa: E402
from perturber_fitter import run_eccentric_fit  # noqa: E402


def main():
    i = 16
    case = make_ecc_case(i)
    t0 = time.time()
    report = run_eccentric_fit(case['tracer_states'],
                               case['ts_train'], case['obs_train'],
                               case['ts_hold'], case['obs_hold'])
    scored = score_ecc_case(i, case['truth'], report)
    scored['runtime_s'] = time.time() - t0
    print(f"SMOKE case {i}: recovered={scored['recovered']} "
          f"mass={scored['mass_rel_err']:.2%} "
          f"a={scored['a_rel_err']:.2%} "
          f"e={scored['e_abs_err']:.4f} "
          f"holdout_ratio={scored['holdout_ratio']:.3e} "
          f"({scored['runtime_s']:.0f}s)", flush=True)
    print(f"  truth={case['truth'][1]}", flush=True)
    print(f"  fitted={scored['fitted_secondary']}", flush=True)


if __name__ == '__main__':
    main()
