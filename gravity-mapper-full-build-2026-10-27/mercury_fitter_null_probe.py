#!/usr/bin/env python3
"""Diagnostic probe: why does the v2 null case never finish?

Single predicts are FAST (0.05-0.13 s even for extreme configs, see
probe 2026-10-26), so the null slowness is not per-eval cost. This
runs the exact v2 null pipeline with a timed wrapper around
predict_positions: every eval is counted, cumulative progress prints
every 250 evals, and any predict slower than 2 s logs its full
candidate configuration. If a predict hangs, the last log lines show
exactly which configuration stalled it (and how far the pipeline got).

Kill-proofing (added after the first probe died on a restart at eval
~1000): every eval is ALSO appended to null_probe_evals.log BEFORE
it runs (flushed), so even a restart leaves the exact stall point in
the file — the config that was running when progress stopped. The
stdout SLOW lines only fire for predicts that RETURN; the file log
covers predicts that never return.

Same null config as mercury_fitter_test_v2.py (truth Saturn only,
noise seed 2). Run in background; output is flushed so a hang still
leaves evidence in the log.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import perturber_fitter
from mercury_fitter_test_v2 import CASES, make_case  # noqa: E402

_orig_predict = perturber_fitter.predict_positions
_state = {'n': 0, 't0': time.perf_counter()}
_EVAL_LOG = (Path(__file__).resolve().parent / 'null_probe_evals.log')
_eval_f = open(_EVAL_LOG, 'w')


def timed_predict(states, cands, ts, mu=None):
    _state['n'] += 1
    # Logged BEFORE the call: if this predict never returns, the file
    # still names the culprit configuration.
    _eval_f.write(f"{_state['n']} "
                  f"{time.perf_counter() - _state['t0']:.1f}s "
                  f"n_bodies={len(cands)} cands={list(cands)}\n")
    _eval_f.flush()
    t0 = time.perf_counter()
    out = (_orig_predict(states, cands, ts) if mu is None
           else _orig_predict(states, cands, ts, mu))
    dt = time.perf_counter() - t0
    if dt > 2.0:
        print(f"SLOW predict #{_state['n']}: {dt:.1f}s cands={cands}",
              flush=True)
    if _state['n'] % 250 == 0:
        print(f"  ... eval #{_state['n']} "
              f"({time.perf_counter() - _state['t0']:.0f}s elapsed)",
              flush=True)
    return out


perturber_fitter.predict_positions = timed_predict


def main():
    truth, noise_seed = CASES['null']
    print('null probe: building case ...', flush=True)
    case = make_case(truth, noise_seed)
    print('null probe: running blind fit (watch for SLOW lines) ...',
          flush=True)
    report = perturber_fitter.run_blind_fit(
        case['tracer_states'], case['ts_train'], case['obs_train'],
        case['ts_hold'], case['obs_hold'])
    print(f"null probe DONE: verdict={report['verdict']} "
          f"ratio={report['holdout_ratio']:.3e} "
          f"evals={_state['n']} "
          f"({time.perf_counter() - _state['t0']:.0f}s total)", flush=True)


if __name__ == '__main__':
    main()
