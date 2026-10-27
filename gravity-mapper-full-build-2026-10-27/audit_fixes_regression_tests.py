#!/usr/bin/env python3
"""Regression tests for the audit fixes (Phase 1).

Each test FAILS on current (pre-fix) code and PASSES after the Phase 2
fix specified in audit_fixes_designs.md. Expected Phase 1 outcome: ALL
FAIL (with the documented failure mode). Any test passing in Phase 1
means either the design is wrong or the code already changed — report
it, do not quietly adjust the test.

Run: python3 audit_fixes_regression_tests.py
Exit code 0 iff all tests pass (i.e. Phase 2 is done).
"""
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))

import checker_brain
import optimizer_brain
import rom_closure
import rom_history
from hypothesis_tracker import Hypothesis, HypothesisTracker
from secular_elements import cart_to_elements, elements_to_cart, MU_SUN

RESULTS = []


def test(fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 — failure mode is the signal
        RESULTS.append((fn.__name__, False, f"{type(e).__name__}: {e}"))
    else:
        RESULTS.append((fn.__name__, True, ""))
    return fn


# ---- Fix #1a: checker refit must NOT receive the full-data hint ----
def _check_fit_setup():
    ts = np.linspace(0.0, 10.0, 20)
    obs = np.zeros((20, 3))
    fit = {'success': True, 'a': 1.0, 'e': 0.1, 'rms_au': 1e-3,
           'r0_au': [1.0, 0.0, 0.0], 'v0_au_yr': [0.0, 6.28, 0.0]}
    predict = lambda x, t_, t_ref: np.zeros((len(np.atleast_1d(t_)), 3))  # noqa: E731
    return ts, obs, fit, predict


@test
def T1a_refit_gets_no_hint():
    calls = {}

    def fake_fit_state(ts, obs, predict_fn, **kw):
        calls.update(kw)
        return {'success': True, 'r0_au': [1.0, 0.0, 0.0],
                'v0_au_yr': [0.0, 6.28, 0.0], 'rms_au': 5e-5}

    orig = checker_brain.fit_state
    checker_brain.fit_state = fake_fit_state
    try:
        ts, obs, fit, predict = _check_fit_setup()
        checker_brain.check_fit(fit, ts, obs, predict, sigma=7.04e-5)
    finally:
        checker_brain.fit_state = orig
    assert calls.get('x0_hint') is None, \
        f"refit received full-data hint x0_hint={calls.get('x0_hint')}"


@test
def T1b_train_rms_comes_from_refit():
    def fake_fit_state(ts, obs, predict_fn, **kw):
        return {'success': True, 'r0_au': [1.0, 0.0, 0.0],
                'v0_au_yr': [0.0, 6.28, 0.0], 'rms_au': 7.5e-5}

    orig = checker_brain.fit_state
    checker_brain.fit_state = fake_fit_state
    try:
        ts, obs, fit, predict = _check_fit_setup()
        out = checker_brain.check_fit(fit, ts, obs, predict, sigma=7.04e-5)
    finally:
        checker_brain.fit_state = orig
    assert out['train_rms_au'] == 7.5e-5, \
        f"train_rms_au={out['train_rms_au']}, expected refit 7.5e-5"
    assert out['gates']['noise_consistent'] is True, \
        "noise gate must follow the refit RMS, not the full-data RMS"


# ---- Fix #1b: fit_state success filtering + success-gated early stop ----
class _FakeSol:
    def __init__(self, x, fun, success):
        self.x = np.asarray(x, float)
        self.fun = np.asarray(fun, float)
        self.success = success
        self.cost = float(np.sum(self.fun ** 2))
        self.nfev = 10


def _circ_state(phase):
    n = math.sqrt(MU_SUN)
    return np.array([math.cos(phase), math.sin(phase), 0.0,
                     -n * math.sin(phase), n * math.cos(phase), 0.0])


@test
def T1c_successful_start_beats_cheap_unsuccessful():
    sols = [
        _FakeSol(_circ_state(0.0), np.full(15, 0.1), False),   # cheap, failed
        _FakeSol(_circ_state(1.0), np.full(15, 1.0), True),    # dear, converged
    ]
    calls = {'n': 0}

    def fake_ls(residuals, x0, **kw):
        sol = sols[calls['n']]
        calls['n'] += 1
        return sol

    orig = optimizer_brain.least_squares
    optimizer_brain.least_squares = fake_ls
    try:
        ts = np.linspace(0.0, 5.0, 5)
        obs = np.zeros((5, 3))
        out = optimizer_brain.fit_state(
            ts, obs, lambda x, t_, t_ref: np.zeros((len(np.atleast_1d(t_)), 3)),
            n_starts=2, seed=0)
    finally:
        optimizer_brain.least_squares = orig
    assert out['success'] is True, "must return the converged start"
    assert np.allclose(out['r0_au'], _circ_state(1.0)[:3]), \
        f"r0={out.get('r0_au')}, expected successful start's state"


@test
def T1d_early_stop_requires_success():
    sols = [
        _FakeSol(_circ_state(0.0), np.full(15, 1e-4), False),  # below stop, failed
        _FakeSol(_circ_state(1.0), np.full(15, 1.0), True),
    ]
    calls = {'n': 0}

    def fake_ls(residuals, x0, **kw):
        sol = sols[calls['n']]
        calls['n'] += 1
        return sol

    orig = optimizer_brain.least_squares
    optimizer_brain.least_squares = fake_ls
    try:
        ts = np.linspace(0.0, 5.0, 5)
        obs = np.zeros((5, 3))
        out = optimizer_brain.fit_state(
            ts, obs, lambda x, t_, t_ref: np.zeros((len(np.atleast_1d(t_)), 3)),
            n_starts=2, seed=0, early_stop_rms=1e-3)
    finally:
        optimizer_brain.least_squares = orig
    assert calls['n'] == 2, f"stopped early after {calls['n']} start(s)"
    assert out['success'] is True, "must reach the converged start"


# ---- Fix #2: ratio contract, MSE domain ----
@test
def T2a_mse_ratio_helper():
    # Fails pre-fix with AttributeError (helper does not exist yet).
    ratio = rom_closure.holdout_mse_ratio(1.1, 1.0)
    assert abs(ratio - 1.21) < 1e-12, f"got {ratio}, expected 1.21"


@test
def T2b_promoted_at_mse_1_21():
    # Fails pre-fix with KeyError (old code reads bare 'ratio').
    outcome, _ = rom_closure.verdict_for_candidate({
        'candidate_check': {'verdict': 'PASS',
                            'gates': {'converged': True, 'physical': True}},
        'holdout_mse_ratio': 1.21})
    assert outcome == 'promoted', f"got {outcome}, expected promoted"


@test
def T2c_abstained_at_mse_1_1():
    outcome, _ = rom_closure.verdict_for_candidate({
        'candidate_check': {'verdict': 'PASS',
                            'gates': {'converged': True, 'physical': True}},
        'holdout_mse_ratio': 1.1})
    assert outcome == 'abstained', f"got {outcome}, expected abstained"


# ---- Fix #2b: validity gate — an undefined comparison never kills ----
# These pin the Phase 2b validity gate in verdict_for_candidate_detailed
# (already implemented): missing/NaN/infinite ratio, or a non-finite
# holdout, yields 'abstained' with an explicit reason. They use the
# detailed variant because the reason is the informative part; the
# 2-tuple wrapper drops it. No orbit integration: synthetic dicts only.
def _pass_check():
    return {'verdict': 'PASS',
            'gates': {'converged': True, 'physical': True}}


@test
def T2d_pass_nan_ratio_abstains():
    # The reported defect: pre-gate, PASS + NaN fell through to 'killed'.
    outcome, _, reason = rom_closure.verdict_for_candidate_detailed({
        'candidate_check': _pass_check(),
        'holdout_mse_ratio': float('nan')})
    assert outcome == 'abstained', f"got {outcome}, expected abstained"
    assert reason == 'comparison_invalid', \
        f"reason={reason}, expected comparison_invalid"


@test
def T2e_pass_missing_ratio_abstains():
    outcome, _, reason = rom_closure.verdict_for_candidate_detailed({
        'candidate_check': _pass_check()})
    assert outcome == 'abstained', f"got {outcome}, expected abstained"
    assert reason == 'comparison_invalid', \
        f"reason={reason}, expected comparison_invalid"


@test
def T2f_pass_infinite_ratio_abstains():
    outcome, _, reason = rom_closure.verdict_for_candidate_detailed({
        'candidate_check': _pass_check(),
        'holdout_mse_ratio': float('inf')})
    assert outcome == 'abstained', f"got {outcome}, expected abstained"
    assert reason == 'comparison_invalid', \
        f"reason={reason}, expected comparison_invalid"


@test
def T2g_nonfinite_baseline_holdout_abstains():
    # Baseline reason is checked first, even with a promotable ratio.
    outcome, _, reason = rom_closure.verdict_for_candidate_detailed({
        'candidate_check': _pass_check(),
        'holdout_mse_ratio': 1.3,
        'baseline_holdout': float('nan')})
    assert outcome == 'abstained', f"got {outcome}, expected abstained"
    assert reason == 'baseline_holdout_unavailable', \
        f"reason={reason}, expected baseline_holdout_unavailable"


# ---- Fix #3: evidence ledger / delta-only consolidation ----
def _ledger_parent_child(loglik):
    parent = rom_history.ParentROM(path=None)
    child = rom_history.ChildROM('h1', [(1e-3, 10.0, 0.5)], parent=parent)
    child.log_likelihood = loglik
    child.posterior = 0.5
    return parent, child


@test
def T3a_same_event_consolidates_once():
    parent, child = _ledger_parent_child(2.0)
    rom_history.consolidate(parent, [child], event_id='E1')
    rom_history.consolidate(parent, [child], event_id='E1')
    key = parent._bin_key(1e-3, 10.0)
    assert parent.bins[key]['n_tried'] == 1, \
        f"n_tried={parent.bins[key]['n_tried']}, expected 1"


@test
def T3b_replay_adds_only_delta():
    parent, child = _ledger_parent_child(2.0)
    rom_history.consolidate(parent, [child], event_id='E1')
    child.log_likelihood = 3.0
    rom_history.consolidate(parent, [child], event_id='E1')
    key = parent._bin_key(1e-3, 10.0)
    assert parent.bins[key]['n_tried'] == 1
    assert abs(parent.bins[key]['sum_loglike'] - 3.0) < 1e-12, \
        f"sum_loglike={parent.bins[key]['sum_loglike']}, expected 3.0"


@test
def T3c_new_event_counts_fully():
    parent, child = _ledger_parent_child(2.0)
    rom_history.consolidate(parent, [child], event_id='E1')
    rom_history.consolidate(parent, [child], event_id='E2')
    key = parent._bin_key(1e-3, 10.0)
    assert parent.bins[key]['n_tried'] == 2, \
        f"n_tried={parent.bins[key]['n_tried']}, expected 2"


# ---- Fix #5: atomic ROM save ----
@test
def T5a_save_uses_atomic_replace():
    replaced = []
    orig_replace = os.replace

    def spy_replace(src, dst):
        replaced.append((src, dst))
        return orig_replace(src, dst)

    rom_history.os.replace = spy_replace
    try:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'rom.json')
            parent = rom_history.ParentROM(path=p)
            parent.save()
            assert replaced, "save() never called os.replace"
            assert replaced[0][1] == p, "replace target must be the ROM path"
    finally:
        rom_history.os.replace = orig_replace


@test
def T5b_no_temp_left_behind_and_round_trips():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'rom.json')
        parent = rom_history.ParentROM(path=p)
        parent.save()
        leftovers = [f for f in os.listdir(d) if f != 'rom.json']
        assert not leftovers, f"temp files left behind: {leftovers}"
        reloaded = rom_history.ParentROM(path=p)
        assert reloaded.total_consolidations == \
            parent.total_consolidations


# ---- Hygiene: paths, duplicate names, circular phase, sequential doc ----
@test
def T6a_no_hardcoded_paths_in_live_modules():
    for fname in ('rom_closure.py', 'rom_loop.py'):
        src = open(os.path.join(HERE, fname)).read()
        assert '/home/hatch' not in src, f"{fname} still hardcodes a path"
        assert 'os.chdir' not in src, f"{fname} still changes directory"


@test
def T6b_duplicate_hypothesis_name_rejected():
    tr = HypothesisTracker()
    tr.add(Hypothesis('dup', []))
    try:
        tr.add(Hypothesis('dup', []))
    except ValueError:
        return
    raise AssertionError("duplicate name silently accepted")


@test
def T6c_circular_orbit_phase_round_trips():
    r = np.array([math.cos(1.0), math.sin(1.0), 0.0])
    v = np.array([-math.sqrt(MU_SUN) * math.sin(1.0),
                  math.sqrt(MU_SUN) * math.cos(1.0), 0.0])
    el = cart_to_elements(r, v)
    r2, _ = elements_to_cart(el)
    assert np.linalg.norm(r2 - r) < 1e-9, \
        f"round-trip moved the state by {np.linalg.norm(r2 - r):.2e} AU"


@test
def T6d_sequential_doc_contradiction_gone():
    src = open(os.path.join(HERE, 'hypothesis_tracker.py')).read()
    if 'def update_sequential' not in src:
        return  # renamed: contradiction gone by construction
    body = src.split('def update_sequential', 1)[1]
    body = body.split('\n    def ', 1)[0]
    assert not ('cumulative' in body and 'batch only' in body), \
        "docstring still claims cumulative while body scores batch-only"


def main():
    # Run in definition order (decorator already executed each test).
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, reason in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {reason}")
    print(f"\n{n_pass}/{len(RESULTS)} pass")
    return 0 if n_pass == len(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
