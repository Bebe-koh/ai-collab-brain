#!/usr/bin/env python3
"""Regression tests for the Phase 2b follow-up correctness batch.

Item 1 (T7): invalid comparison must abstain, never kill.
Item 2 (T8): ledger identity contract (dataset/model/scoring binding,
candidate parameter binding, rejection on mismatch).

Additive: the existing 16-test suite is NOT modified and must still pass
16/16 alongside this file. Run: python3 phase2b_regression_tests.py
Exit code 0 iff all tests pass.
"""
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))

import rom_closure
import rom_history
from rom_history import (ParentROM, ChildROM, consolidate,
                         LedgerIdentityError)

RESULTS = []


def test(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 — failure mode is the signal
        RESULTS.append((fn.__name__, False, f"{type(e).__name__}: {e}"))
    else:
        RESULTS.append((fn.__name__, True, ""))
    return fn


def _fr(check, ratio=None, b=None, c=None, converged=True, physical=True):
    d = {'candidate_check': {'verdict': check,
                             'gates': {'converged': converged,
                                       'physical': physical}}}
    if ratio is not None:
        d['holdout_mse_ratio'] = ratio
    if b is not None:
        d['baseline_holdout'] = b
    if c is not None:
        d['candidate_holdout'] = c
    return d


def _det(*a, **k):
    return rom_closure.verdict_for_candidate_detailed(*a, **k)


# ---- Item 1: invalid comparison abstains, never kills ----

@test
def T7a_missing_key_abstains():
    out, ratio, reason = _det(_fr('PASS'))
    assert out == 'abstained', f"got {out}, expected abstained"
    assert reason == 'comparison_invalid', f"reason={reason}"
    w_out, _ = rom_closure.verdict_for_candidate(_fr('PASS'))
    assert w_out == 'abstained', "wrapper must agree: abstained"


@test
def T7b_nan_ratio_abstains():
    out, _, reason = _det(_fr('PASS', float('nan')))
    assert out == 'abstained', f"got {out}"
    assert reason == 'comparison_invalid', f"reason={reason}"


@test
def T7c_inf_ratio_abstains():
    out, _, reason = _det(_fr('PASS', float('inf')))
    assert out == 'abstained', f"got {out}, expected abstained (not promoted)"
    assert reason == 'comparison_invalid', f"reason={reason}"


@test
def T7d_baseline_unavailable_beats_favorable_ratio():
    # Baseline check precedes the ratio: even a favorable hand-built
    # ratio cannot promote when the baseline produced no holdout.
    out, _, reason = _det(_fr('PASS', 1.5, b=float('inf'), c=1e-4))
    assert out == 'abstained', f"got {out}"
    assert reason == 'baseline_holdout_unavailable', f"reason={reason}"


@test
def T7e_candidate_pass_invalid_baseline():
    # The realistic triggering path: candidate PASS, baseline holdout
    # unavailable, ratio NaN (as fit_candidate produces it).
    out, _, reason = _det(_fr('PASS', float('nan'), b=float('inf'),
                              c=1e-4))
    assert out == 'abstained', f"got {out}"
    assert reason == 'baseline_holdout_unavailable', f"reason={reason}"


@test
def T7f_candidate_holdout_invalid():
    out, _, reason = _det(_fr('PASS', 1.5, b=1e-4, c=float('inf')))
    assert out == 'abstained', f"got {out}"
    assert reason == 'comparison_invalid', f"reason={reason}"


@test
def T7g_valid_mapping_unchanged():
    cases = [
        (_fr('PASS', 1.21, b=1e-4, c=9e-5), 'promoted'),
        (_fr('PASS', 1.1, b=1e-4, c=9e-5), 'abstained'),
        (_fr('PASS', 0.9, b=1e-4, c=1.1e-4), 'killed'),
        (_fr('FAIL', 0.9, b=1e-4, c=1.1e-4), 'killed'),
        (_fr('FAIL', 0.9, b=1e-4, c=1.1e-4, converged=False),
         'abstained'),
        (_fr('ABSTAIN', 0.9, b=1e-4, c=1.1e-4), 'abstained'),
    ]
    for d, want in cases:
        out, _, reason = _det(d)
        assert out == want, f"got {out}, expected {want} for {d}"
        assert reason is None, f"valid outcome must carry no reason: {reason}"


@test
def T7h_wrapper_two_tuple_compat():
    # Frozen callers (lean driver, pilot, T2b/T2c) unpack two values.
    r = rom_closure.verdict_for_candidate(_fr('PASS', float('nan')))
    assert isinstance(r, tuple) and len(r) == 2, f"got {r}"
    assert r[0] == 'abstained'
    r = rom_closure.verdict_for_candidate(_fr('PASS', 1.21))
    assert r[0] == 'promoted' and abs(r[1] - 1.21) < 1e-12


# ---- Item 2: ledger identity contract ----

ID1 = {'dataset_id': 'D1', 'model_version': '1', 'scoring': 'mse:1.2'}
ID2 = {'dataset_id': 'D2', 'model_version': '1', 'scoring': 'mse:1.2'}


def _mk(name, bodies, ll, post=0.5):
    ch = ChildROM(name, bodies)
    ch.log_likelihood = ll
    ch.posterior = post
    return ch


def _bin(p, m, r):
    return p.bins[p._bin_key(m, r)]


@test
def T8a_same_name_different_params_rejected():
    p = ParentROM(path=None)
    consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                event_id='E1', event_identity=ID1)
    before = dict(_bin(p, 1e-3, 10.0))
    try:
        consolidate(p, [_mk('h1', [(2e-3, 10.0, 0.5)], 2.0)],
                    event_id='E1', event_identity=ID1)
    except LedgerIdentityError:
        pass
    else:
        raise AssertionError("same-name-different-params NOT rejected")
    after = _bin(p, 1e-3, 10.0)
    assert after['n_tried'] == before['n_tried'], "rejection must not mutate"
    assert abs(after['sum_loglike'] - before['sum_loglike']) < 1e-12


@test
def T8b_same_event_different_dataset_separated():
    p = ParentROM(path=None)
    consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                event_id='E1', event_identity=ID1)
    try:
        consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                    event_id='E1', event_identity=ID2)
    except LedgerIdentityError:
        pass
    else:
        raise AssertionError("same-event-different-dataset NOT rejected")
    consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                event_id='E2', event_identity=ID2)
    assert _bin(p, 1e-3, 10.0)['n_tried'] == 2, \
        "distinct event must consolidate fully"


@test
def T8c_identical_replay_delta_only():
    p = ParentROM(path=None)
    ch = _mk('h1', [(1e-3, 10.0, 0.5)], 2.0)
    consolidate(p, [ch], event_id='E1', event_identity=ID1)
    ch.log_likelihood = 3.0
    consolidate(p, [ch], event_id='E1', event_identity=ID1)
    b = _bin(p, 1e-3, 10.0)
    assert b['n_tried'] == 1, f"n_tried={b['n_tried']}"
    assert abs(b['sum_loglike'] - 3.0) < 1e-12, f"sum={b['sum_loglike']}"
    assert b['n_good'] == 1, "n_good must not be re-credited"


@test
def T8d_legacy_event_rejects_identified_write():
    p = ParentROM(path=None)
    consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)], event_id='E9')
    try:
        consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                    event_id='E9', event_identity=ID1)
    except LedgerIdentityError:
        pass
    else:
        raise AssertionError("legacy->identified NOT rejected")


@test
def T8e_identified_event_rejects_unidentified_write():
    p = ParentROM(path=None)
    consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                event_id='E1', event_identity=ID1)
    try:
        consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                    event_id='E1')
    except LedgerIdentityError:
        pass
    else:
        raise AssertionError("identified->unidentified NOT rejected")


@test
def T8f_unique_ids_independent():
    # Simulates novel-case unique ids: distinct case ids with the same
    # dataset identity consolidate fully and independently.
    p = ParentROM(path=None)
    for cid in ('novel-0-aaa', 'novel-0-bbb'):
        consolidate(p, [_mk('h1', [(1e-3, 10.0, 0.5)], 2.0)],
                    event_id=cid, event_identity=ID1)
    assert _bin(p, 1e-3, 10.0)['n_tried'] == 2


@test
def T8g_guard_identity():
    p = ParentROM(path=None)
    ch = _mk('h1', [(1e-3, 10.0, 0.5)], 2.0)
    consolidate(p, [ch], event_id='E1', event_identity=ID1)
    ch.log_likelihood = 3.0
    consolidate(p, [ch], event_id='E1', event_identity=ID1)
    # Simulate ledger entry loss; guard must carry the replay.
    del p.extra['consolidated_events']['E1']['h1']
    ch2 = _mk('h1', [(1e-3, 10.0, 0.5)], 3.0)
    ch2.last_consolidated_event = 'E1'
    ch2.last_consolidated_loglik = 3.0
    ch2.last_consolidated_identity = dict(ID1)
    n = consolidate(p, [ch2], event_id='E1', event_identity=ID1)
    assert n == 0, f"guard replay must be a no-op, got n={n}"
    ch3 = _mk('h1', [(1e-3, 10.0, 0.5)], 3.0)
    ch3.last_consolidated_event = 'E1'
    ch3.last_consolidated_loglik = 3.0
    ch3.last_consolidated_identity = dict(ID1)
    try:
        consolidate(p, [ch3], event_id='E1', event_identity=ID2)
    except LedgerIdentityError:
        pass
    else:
        raise AssertionError("guard identity mismatch NOT rejected")


@test
def T8h_json_roundtrip_identity():
    # Persisted entries (lists after JSON) must still match in-memory
    # bodies, or every reload would false-reject replays.
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, 'r.json')
        p = ParentROM(path=None)
        ch = _mk('h1', [(1e-3, 10.0, 0.5)], 2.0)
        consolidate(p, [ch], event_id='E1', event_identity=ID1)
        p.path = path
        p.save()
        p2 = ParentROM(path=path)
        ch2 = _mk('h1', [(1e-3, 10.0, 0.5)], 2.0)
        n = consolidate(p2, [ch2], event_id='E1', event_identity=ID1)
        assert n == 0, f"reload replay must be a no-op, got n={n}"


if __name__ == '__main__':
    import sys
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {msg}")
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"{n_pass}/{len(RESULTS)} passed")
    sys.exit(0 if n_pass == len(RESULTS) else 1)
