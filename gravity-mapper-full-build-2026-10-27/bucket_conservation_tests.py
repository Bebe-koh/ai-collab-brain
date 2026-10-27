#!/usr/bin/env python3
"""Preregistered bucket tests T-C1..T-C15 (spec v2 §5).

All tests run on SCRATCH state only: scratch trackers constructed
directly with fixture weights, scratch ParentROMs in temp directories.
The ONLY live-ROM contact is T-C11's read-only classification check
on a COPY of the live ROM (temp dir); the live file is never opened
for writing, and its md5 is asserted before and after the suite.

Run: python3 bucket_conservation_tests.py  (exit 0 iff all pass)
"""
import copy
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hypothesis_tracker import Hypothesis, HypothesisTracker
from rom_history import ParentROM
import rom_closure

LIVE_ROM = os.path.join(HERE, 'real_data', 'parent_rom.json')
EXPECTED_LIVE_MD5 = '4c77b723ff5770566a85ed4e580aed2c'
PASS = []
FAIL = []


def md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def check(name, cond, detail=''):
    if cond:
        PASS.append(name)
        print(f"PASS {name}")
    else:
        FAIL.append(name)
        print(f"FAIL {name} {detail}")


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def make_cd_tracker():
    """Spec §1.3 fixture: null 0.5, 5 invented 0.01 each, 3 killed
    (-5 log-odds each), 2 abstained. Calibrated weights (no dynamics
    term, log-likelihood None) reproduce the fixture exactly."""
    t = HypothesisTracker()
    t.propose_null(log_prior=math.log(0.5))
    for i in range(1, 6):
        t.propose(f'inv{i}', [(1e-5, 10.0, 0.0)], log_prior=math.log(0.01))
    for i in (1, 2, 3):
        t.add_verdict(f'inv{i}', 'killed')
    for i in (4, 5):
        t.add_verdict(f'inv{i}', 'abstained')
    return t


def cd_shares_before(t):
    return t.bucket_posteriors()['uncapped']


# ---------------- T-C1 ----------------
def tc1():
    t = make_cd_tracker()
    before = cd_shares_before(t)
    check('T-C1 pre-deferral null', close(before['null'], 0.9611648301),
          str(before))
    # Defer the two abstained via the bucket path.
    assert t.defer_to_bucket('inv4', 'cd-case')
    assert t.defer_to_bucket('inv5', 'cd-case')
    rep = t.bucket_posteriors()
    u = rep['uncapped']
    check('T-C1 post-deferral null unchanged',
          close(u['null'], 0.9611648301), str(u))
    check('T-C1 bucket share', close(rep['bucket_share'], 0.0384465932),
          str(rep))
    killed = sum(u[f'inv{i}'] for i in (1, 2, 3))
    check('T-C1 killed share', close(killed, 0.0003885767), str(u))
    check('T-C1 cap not bound', rep['cap_applied'] is False, str(rep))
    check('T-C1 sum 1.0', close(sum(u.values()), 1.0), str(sum(u.values())))
    # Old path: active-only renormalization (pre-cap) on the same
    # fixture gives the inflated null — proving the test distinguishes
    # the fix from the bug. (Legacy capped posteriors() would report
    # 0.99 here, a different, also-wrong number; §1.3's old-path
    # number is the pre-cap renormalization.)
    t2 = make_cd_tracker()
    t2.hypotheses = [h for h in t2.hypotheses if h.name not in ('inv4', 'inv5')]
    old = t2.bucket_uncapped_posteriors()
    check('T-C1 old path inflated null',
          close(old['null'], 0.9995958866), str(old))


# ---------------- T-C2 ----------------
def tc2():
    t = make_cd_tracker()
    before = cd_shares_before(t)
    t.defer_to_bucket('inv4', 'c2-case')
    t.defer_to_bucket('inv5', 'c2-case')
    after = t.bucket_posteriors()['uncapped']
    ok = all(close(after[n], before[n]) for n in before)
    check('T-C2 every share conserved across deferral', ok,
          f"before={before} after={after}")
    check('T-C2 bucket increase equals transferred share',
          close(t.bucket_posteriors()['bucket_share'],
                before['inv4'] + before['inv5']), '')
    check('T-C2 active+bucket=1.0',
          close(sum(after.values()), 1.0), '')


# ---------------- T-C3 ----------------
def tc3():
    t = make_cd_tracker()
    before = cd_shares_before(t)
    t.defer_to_bucket('inv4', 'c3-case')
    assert t.reenter_from_bucket('inv4', trigger='redesigned case names inv4',
                                 case_id='c3-case')
    after = t.bucket_posteriors()['uncapped']
    ok = all(close(after[n], before[n]) for n in before)
    check('T-C3 re-entry restores distribution', ok, f"{before} vs {after}")
    check('T-C3 contribution exactly once',
          t.bucket_posteriors()['deferred_names'] == ['inv5'] or
          'inv4' not in t.bucket_posteriors()['deferred_names'],
          str(t.bucket_posteriors()['deferred_names']))
    names = [h.name for h in t.hypotheses]
    check('T-C3 inv4 active exactly once', names.count('inv4') == 1, str(names))


# ---------------- T-C4 ----------------
def tc4():
    t = make_cd_tracker()
    t.defer_to_bucket('inv4', 'c4-case')
    state_before = t.scientific_state()
    ledger_before = copy.deepcopy(t.bucket_ledger)
    result = t.defer_to_bucket('inv4', 'c4-case')
    check('T-C4 repeated deferral is a no-op return', result is False, str(result))
    check('T-C4 scientific state unchanged',
          t.scientific_state() == state_before, '')
    check('T-C4 persisted ledger unchanged',
          t.bucket_ledger == ledger_before, str(t.bucket_ledger))
    # Attempt log (if any) is diagnostic only: it must not appear in
    # the persisted bucket state dict.
    state_dict = t.bucket_state_dict()
    check('T-C4 attempt log absent from persisted state',
          'attempt_log' not in state_dict, str(list(state_dict.keys())))


# ---------------- T-C5 ----------------
def tc5():
    t = make_cd_tracker()
    t.defer_to_bucket('inv4', 'c5-case', event_identity={'dataset_id': 'D1'})
    state_before = t.scientific_state()
    # Replay the SAME movement (same name, case, identity).
    result = t.defer_to_bucket('inv4', 'c5-case',
                               event_identity={'dataset_id': 'D1'})
    check('T-C5 replay deferral is a no-op', result is False, str(result))
    check('T-C5 state tuple EXACTLY equal',
          t.scientific_state() == state_before, '')
    # A replayed re-entry of a non-deferred hypothesis is a rejection,
    # also leaving state unchanged.
    state_before2 = t.scientific_state()
    try:
        t.reenter_from_bucket('inv1', trigger='x', case_id='c5-case')
        rejected = False
    except ValueError:
        rejected = True
    check('T-C5 replay re-entry of active rejected', rejected, '')
    check('T-C5 state unchanged after rejected replay',
          t.scientific_state() == state_before2, '')


# ---------------- T-C6 ----------------
def tc6(tmp):
    # (a) ROM save/load round-trip: finite exact, -inf sentinel, underflow.
    path = os.path.join(tmp, 'rom_c6.json')
    parent = ParentROM(path=path)
    parent.extra['deferred'] = [
        {'name': 'a', 'log_weight': -2.5, 'case': 'c6'},
        {'name': 'zero', 'log_weight': float('-inf'), 'case': 'c6'},
        {'name': 'under', 'log_weight': -1000.0, 'case': 'c6'},
    ]
    parent.save()
    loaded = ParentROM(path=path)
    recs = {r['name']: r['log_weight'] for r in loaded.extra['deferred']}
    check('T-C6 finite log-weight exact', recs['a'] == -2.5, str(recs))
    check('T-C6 -inf sentinel preserved', recs['zero'] == float('-inf'), str(recs))
    check('T-C6 underflow finite weight exact', recs['under'] == -1000.0, str(recs))
    # (b) +inf rejected at save, file unchanged.
    before_md5 = md5(path)
    parent.extra['deferred'].append({'name': 'bad', 'log_weight': float('inf')})
    try:
        parent.save()
        rejected_save = False
    except ValueError:
        rejected_save = True
    check('T-C6 +inf rejected at save', rejected_save, '')
    check('T-C6 file unchanged after rejected save', md5(path) == before_md5, '')
    parent.extra['deferred'] = parent.extra['deferred'][:-1]
    # NaN rejected at save as well.
    parent.extra['deferred'].append({'name': 'bad2', 'log_weight': float('nan')})
    try:
        parent.save()
        rejected_nan = False
    except ValueError:
        rejected_nan = True
    check('T-C6 NaN rejected at save', rejected_nan, '')
    # (c) +inf/NaN rejected at load (crafted file).
    bad_path = os.path.join(tmp, 'rom_c6_bad.json')
    with open(bad_path, 'w') as f:
        json.dump({'bins': {}, 'extra_deferred': float('inf'),
                   'deferred': [{'name': 'x', 'log_weight': float('inf')}]}, f)
    try:
        ParentROM(path=bad_path)
        rejected_load = False
    except ValueError:
        rejected_load = True
    check('T-C6 +inf rejected at load', rejected_load, '')
    # (d) All -inf rejected (tracker bucket validation).
    t = HypothesisTracker()
    t.propose_null(log_prior=float('-inf'))
    try:
        t.bucket_uncapped_posteriors()
        rejected_all = False
    except ValueError:
        rejected_all = True
    check('T-C6 all -inf rejected', rejected_all, '')
    # (e) Tracker JSON round-trip exact for finite + underflow weights.
    t2 = HypothesisTracker()
    t2.propose_null(log_prior=0.0)
    t2.propose('tiny', [(1e-5, 10.0, 0.0)], log_prior=-1000.0)
    sd = t2.bucket_state_dict()
    rt = json.loads(json.dumps(sd))
    check('T-C6 tracker JSON finite exact',
          rt['active']['tiny'] == -1000.0, str(rt['active']))


# ---------------- T-C7 ----------------
def tc7():
    t = make_cd_tracker()
    t.defer_to_bucket('inv4', 'c7-case', event_identity={'dataset_id': 'D1'})
    # (a) same name, different params (re-entry identity mismatch)
    state = t.scientific_state()
    try:
        t.reenter_from_bucket('inv4', trigger='t', case_id='c7-case',
                              expected_bodies=[(9.9, 99.0, 0.0)])
        ok_a = False
    except ValueError:
        ok_a = True
    check('T-C7 same-name different-params rejected', ok_a, '')
    check('T-C7 state unchanged after (a)', t.scientific_state() == state, '')
    # (b) same event, different dataset
    try:
        t.reenter_from_bucket('inv4', trigger='t', case_id='c7-case',
                              event_identity={'dataset_id': 'D2'})
        ok_b = False
    except ValueError:
        ok_b = True
    check('T-C7 same-event different-dataset rejected', ok_b, '')
    check('T-C7 state unchanged after (b)', t.scientific_state() == state, '')
    # (c) movement without identity
    t2 = make_cd_tracker()
    try:
        t2.defer_to_bucket('inv4', None)
        ok_c = False
    except ValueError:
        ok_c = True
    check('T-C7 movement without identity rejected', ok_c, '')
    # (d) re-entry without trigger
    try:
        t.reenter_from_bucket('inv4', trigger=None, case_id='c7-case')
        ok_d = False
    except ValueError:
        ok_d = True
    check('T-C7 re-entry without trigger rejected', ok_d, '')
    check('T-C7 state unchanged after (d)', t.scientific_state() == state, '')
    # (e) rom_closure deferral without case_id (existing Phase 2b rule)
    try:
        rom_closure._defer_abstained(make_cd_tracker(), ParentROM(), case_id=None)
        ok_e = False
    except ValueError:
        ok_e = True
    check('T-C7 rom_closure deferral without case_id rejected', ok_e, '')


# ---------------- T-C8 ----------------
def tc8():
    t = HypothesisTracker()
    t.propose_null(log_prior=math.log(0.5))
    t.propose('act', [(1e-5, 10.0, 0.0)], log_prior=math.log(0.01))
    t.propose('def', [(2e-5, 20.0, 0.0)], log_prior=math.log(0.01))
    t.defer_to_bucket('def', 'c8-case')
    w_before = t.deferred_log_weights()['def']
    t.add_verdict('act', 'promoted', holdout_ratio=10.0)
    w_after = t.deferred_log_weights()['def']
    check('T-C8 deferred weight bit-unchanged', w_after == w_before,
          f"{w_before} vs {w_after}")
    # Bucket share recomputed from the new total.
    weights = t.bucket_log_weights()
    m = max(weights.values())
    exp_shares = {n: math.exp(w - m) / sum(math.exp(x - m) for x in weights.values())
                  for n, w in weights.items()}
    rep = t.bucket_posteriors()
    check('T-C8 bucket share recomputed from new total',
          close(rep['bucket_share'], exp_shares['def']), str(rep))


# ---------------- T-C9 ----------------
def tc9():
    t = HypothesisTracker()
    t.propose_null(log_prior=math.log(0.5))
    t.propose('def', [(2e-5, 20.0, 0.0)], log_prior=math.log(0.01))
    t.defer_to_bucket('def', 'c9-case')
    w_before = t.deferred_log_weights()['def']
    t.propose('new', [(3e-5, 30.0, 0.0)], log_prior=math.log(0.02))
    check('T-C9 deferred weight unchanged on insertion',
          t.deferred_log_weights()['def'] == w_before, '')
    weights = t.bucket_log_weights()
    m = max(weights.values())
    tot = sum(math.exp(w - m) for w in weights.values())
    exp_shares = {n: math.exp(w - m) / tot for n, w in weights.items()}
    got = t.bucket_posteriors()['uncapped']
    check('T-C9 shares renormalized correctly',
          all(close(got[n], exp_shares[n]) for n in exp_shares), f"{got} vs {exp_shares}")


# ---------------- T-C10 ----------------
def tc10():
    # Without cap: CD fixture, cap not bound, uncapped is the account.
    t = make_cd_tracker()
    t.defer_to_bucket('inv4', 'c10-case')
    rep = t.bucket_posteriors()
    check('T-C10 uncapped without cap, cap not applied',
          rep['cap_applied'] is False and close(sum(rep['uncapped'].values()), 1.0),
          str(rep))
    # With cap: null uncapped > 0.99, pre-cap values preserved alongside.
    t2 = HypothesisTracker()
    t2.propose_null(log_prior=0.0)
    t2.propose('weak', [(1e-5, 10.0, 0.0)], log_prior=-10.0)
    t2.propose('def', [(2e-5, 20.0, 0.0)], log_prior=-12.0)
    t2.defer_to_bucket('def', 'c10-case')
    rep2 = t2.bucket_posteriors()
    unc = rep2['uncapped']
    check('T-C10 cap binds on null', rep2['cap_applied'] is True, str(rep2))
    check('T-C10 cap_excess = uncapped - 0.99',
          close(rep2['cap_excess'], unc['null'] - 0.99), str(rep2))
    check('T-C10 null_display 0.99, display_only',
          rep2['null_display'] == 0.99 and rep2['display_only'] is True, str(rep2))
    check('T-C10 uncapped preserved alongside cap',
          close(sum(unc.values()), 1.0) and unc['null'] > 0.99, str(unc))
    check('T-C10 no redistribution (other shares = uncapped)',
          rep2['uncapped']['weak'] == unc['weak'], '')


# ---------------- T-C11 ----------------
def tc11(tmp):
    # Scratch two-class representation (§9): 10 belt-style deferred +
    # 4 synthetic-novel consolidations + 2 decided consolidations.
    path = os.path.join(tmp, 'rom_c11.json')
    parent = ParentROM(path=path)
    deferred = [{'name': f'belt_{i}', 'bodies': [[1e-5, 10.0, 0.0]],
                 'body_type': 'planet',
                 'reason': 'abstained in all closure rounds',
                 'case': 'belt-closure', 'posterior': 0.008 + i * 0.0001}
                for i in range(10)]
    consolidations = [{'name': f'novel_{i}', 'value': 1.0 + i,
                       'provenance': 'synthetic-novel'} for i in range(4)]
    consolidations += [{'name': f'decided_{i}', 'value': 2.0 + i,
                        'provenance': 'decided'} for i in range(2)]
    parent.extra['deferred'] = copy.deepcopy(deferred)
    parent.extra['consolidations'] = copy.deepcopy(consolidations)
    parent.save()
    parent2 = ParentROM(path=path)
    cls = parent2.classify_legacy_entries()
    check('T-C11 10 legacy-deferred', len(cls['legacy_deferred']) == 10,
          str(len(cls['legacy_deferred'])))
    check('T-C11 L-D no bucket weight',
          all(r['bucket_weight'] is None for r in cls['legacy_deferred']), '')
    check('T-C11 L-D posterior preserved as annotation',
          all(r['posterior_annotation'] == r['posterior']
              for r in cls['legacy_deferred']), '')
    check('T-C11 L-D flagged',
          all(r['legacy_class'] == 'legacy-deferred' for r in cls['legacy_deferred']), '')
    check('T-C11 4 legacy synthetic consolidations',
          len(cls['legacy_consolidations']) == 4, str(len(cls['legacy_consolidations'])))
    check('T-C11 L-C values untouched',
          all(cls['legacy_consolidations'][i]['value'] == 1.0 + i for i in range(4)), '')
    check('T-C11 L-C flagged synthetic provenance',
          all(r['synthetic_provenance'] is True for r in cls['legacy_consolidations']), '')
    check('T-C11 L-C not in deferred list',
          not any(n.startswith('novel_') for n in cls['deferred_names']), '')
    check('T-C11 L-D bucket weight total 0.0',
          parent2.legacy_deferred_bucket_weight() == 0.0, '')
    check('T-C11 stored entries not mutated by classification',
          parent2.extra['deferred'] == deferred
          and parent2.extra['consolidations'] == consolidations, '')
    # New deferral in the same tracker/parent disturbs neither class.
    t = HypothesisTracker()
    t.propose_null(log_prior=math.log(0.5))
    t.propose('newhyp', [(1e-5, 10.0, 0.0)], log_prior=math.log(0.01))
    t.add_verdict('newhyp', 'abstained')
    legacy_before = copy.deepcopy(parent2.extra['deferred'])
    cons_before = copy.deepcopy(parent2.extra['consolidations'])
    names = rom_closure._defer_abstained(t, parent2, case_id='test-new-case',
                                         event_identity={'dataset_id': 'DN'})
    check('T-C11 new deferral recorded', names == ['newhyp'], str(names))
    rec = parent2.extra['deferred'][-1]
    check('T-C11 new record carries log_weight + identity',
          'log_weight' in rec and rec.get('event_identity', {}).get('dataset_id') == 'DN',
          str(rec))
    check('T-C11 legacy deferred undisturbed',
          parent2.extra['deferred'][:10] == legacy_before, '')
    check('T-C11 consolidations undisturbed',
          parent2.extra['consolidations'] == cons_before, '')
    check('T-C11 new hyp in tracker bucket',
          'newhyp' in t.bucket_posteriors()['deferred_names'], '')
    # Live ROM, read-only, on a COPY.
    copy_path = os.path.join(tmp, 'parent_rom_copy.json')
    shutil.copyfile(LIVE_ROM, copy_path)
    live_copy = ParentROM(path=copy_path)
    cls_live = live_copy.classify_legacy_entries()
    check('T-C11 live copy: 10 belt-closure legacy-deferred',
          len(cls_live['legacy_deferred']) == 10
          and all(r.get('case') == 'belt-closure' for r in cls_live['legacy_deferred']),
          str(len(cls_live['legacy_deferred'])))
    check('T-C11 live copy: L-D no bucket weight',
          all(r['bucket_weight'] is None for r in cls_live['legacy_deferred']), '')
    check('T-C11 live copy file unchanged', md5(copy_path) == EXPECTED_LIVE_MD5, '')


# ---------------- T-C12 ----------------
def tc12():
    t = make_cd_tracker()
    before = cd_shares_before(t)
    t.defer_to_bucket('inv4', 'c12-case')
    t.defer_to_bucket('inv5', 'c12-case')
    after = t.bucket_posteriors()['uncapped']
    check('T-C12 original fixture passes post-fix (null not inflated)',
          close(after['null'], before['null']) and after['null'] < 0.99,
          str(after))
    check('T-C12 conservation on same fixture',
          all(close(after[n], before[n]) for n in before)
          and close(sum(after.values()), 1.0), '')


# ---------------- T-C13 ----------------
def tc13():
    def shares_for(shift):
        t = HypothesisTracker()
        t.propose_null(log_prior=0.0 + shift)
        t.propose('act', [(1e-5, 10.0, 0.0)], log_prior=-1.0 + shift)
        t.propose('def', [(2e-5, 20.0, 0.0)], log_prior=-2.0 + shift)
        t.defer_to_bucket('def', 'c13-case')
        return t.bucket_posteriors()['uncapped']
    base = shares_for(0.0)
    for c in (100.0, -100.0, 1000.0):
        got = shares_for(c)
        check(f'T-C13 common-offset invariance c={c:+.0f}',
              all(close(got[n], base[n]) for n in base), f"{base} vs {got}")


# ---------------- T-C14 ----------------
def tc14():
    t = HypothesisTracker()
    t.propose_null(log_prior=0.0)
    t.propose('far', [(1e-5, 10.0, 0.0)], log_prior=-800.0)
    t.propose('under', [(2e-5, 20.0, 0.0)], log_prior=-1000.0)
    t.defer_to_bucket('under', 'c14-case')
    u = t.bucket_posteriors()['uncapped']
    check('T-C14 extreme spread computes, no NaN/inf',
          all(math.isfinite(v) for v in u.values()), str(u))
    check('T-C14 shares sum 1.0', close(sum(u.values()), 1.0), str(u))
    check('T-C14 smallest share 0.0 (underflow)',
          u['under'] == 0.0 and u['far'] == 0.0, str(u))
    sd = t.bucket_state_dict()
    rt = json.loads(json.dumps(sd))
    check('T-C14 smallest finite weight preserved exactly',
          rt['deferred']['under'] == -1000.0, str(rt['deferred']))


# ---------------- T-C15 ----------------
def tc15():
    t = HypothesisTracker()
    t.propose_null(log_prior=0.0)
    t.propose('weak', [(1e-5, 10.0, 0.0)], log_prior=-10.0)
    t.propose('def', [(2e-5, 20.0, 0.0)], log_prior=-12.0)
    t.defer_to_bucket('def', 'c15-case')
    rep = t.bucket_posteriors()
    unc = rep['uncapped']
    check('T-C15 uncapped sums to 1.0', close(sum(unc.values()), 1.0), str(unc))
    check('T-C15 null_display 0.99 display_only',
          rep['null_display'] == 0.99 and rep['display_only'] is True, str(rep))
    check('T-C15 cap_excess exact',
          close(rep['cap_excess'], unc['null'] - 0.99), str(rep))
    check('T-C15 no other share changed by cap',
          rep['uncapped']['weak'] == unc['weak']
          and rep['uncapped']['def'] == unc['def'], '')
    sd = t.bucket_state_dict()
    check('T-C15 no capped value persisted as posterior',
          sd['uncapped']['null'] > 0.99 and 'capped_posteriors' not in sd
          and sd['cap_applied'] is True, str(sd))
    # MUST-NOT-COMBINE: capped null + uncapped others do NOT sum to 1.
    capped_sum = rep['null_display'] + sum(v for k, v in unc.items() if k != 'null')
    check('T-C15 MUST-NOT-COMBINE (capped sum != 1.0)',
          abs(capped_sum - 1.0) > 1e-6, str(capped_sum))
    check('T-C15 no capped distribution in report',
          'capped_posteriors' not in rep and 'capped' not in rep, str(list(rep.keys())))
    # Crafted capped-as-posterior state is rejected on validation.
    bad = copy.deepcopy(sd)
    bad['posteriors'] = dict(sd['uncapped'])
    bad['posteriors']['null'] = 0.99
    try:
        HypothesisTracker.validate_bucket_state_dict(bad)
        rejected = False
    except ValueError:
        rejected = True
    check('T-C15 capped-as-posterior validation rejected', rejected, '')


def main():
    live_before = md5(LIVE_ROM)
    check('LIVE ROM md5 before suite', live_before == EXPECTED_LIVE_MD5, live_before)
    tmp = tempfile.mkdtemp(prefix='bucket_tests_')
    try:
        tc1(); tc2(); tc3(); tc4(); tc5(); tc6(tmp); tc7(); tc8(); tc9()
        tc10(); tc11(tmp); tc12(); tc13(); tc14(); tc15()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    live_after = md5(LIVE_ROM)
    check('LIVE ROM md5 after suite (unchanged)', live_after == EXPECTED_LIVE_MD5,
          live_after)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", FAIL)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
