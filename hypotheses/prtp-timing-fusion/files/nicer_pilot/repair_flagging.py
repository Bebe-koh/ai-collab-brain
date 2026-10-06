"""PRTP NICER pilot REPAIR, part 2: dwell flagging beyond the H-test.

Pilot finding (N2): H-test alone catches 35% of toy jitter corruption at 5%
FP, and cannot see J0030's per-ObsID coherent offsets at all (single-dwell
detection significance != timing accuracy, and != block systematics).

Flagger v2 adds two things:
  F1. Per-dwell TIMING-ACCURACY features at the photon level:
      split-half phase disagreement (even/odd photons, ML phase each half
      vs the frozen template), template gain, and formal sigma, alongside
      the H-test. Validated by corrupting REAL photon phases (flare: add
      uniform-phase photons; jitter: smear phases) and recomputing every
      feature through the same pipeline -- strictly stronger than the
      pilot's analytic toy.
  F2. Per-ObsID OFFSET significance for J0030-type block systematics:
      |weighted ObsID mean| / se under the empirical white model. These
      are modeled (not merely dropped) by the repaired filter's bias
      states; the flag marks them as systematics-dominated.

Run with the PINT venv: ~/workspace/venv_pint/bin/python repair_flagging.py
Saves repair_flagging.json.
"""
import sys, os, json, csv, warnings
warnings.filterwarnings('ignore')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot_toa as pt
from pilot_analysis import dwell_phases

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
N_PHOTON_DWELLS = 15
RNG = np.random.default_rng(20260925)


def load_template(psr):
    z = np.load(PILOT + f'/templates/{psr}_template.npz')
    return {'a': z['a'], 'b': z['b'], 'n_harm': int(z['n_harm'])}, \
        tuple(int(x) for x in z['band'])


def dwell_features(ph, tmpl):
    """All flagging features from one dwell's photon phases."""
    h = pt.h_test(ph)
    dphi, sig, gain, _ = pt.ml_phase(ph, tmpl)
    ph1, ph2 = ph[0::2], ph[1::2]
    d1, s1, _, _ = pt.ml_phase(ph1, tmpl)
    d2, s2, _, _ = pt.ml_phase(ph2, tmpl)
    dd = (d1 - d2 + 0.5) % 1.0 - 0.5  # circular diff, cycles
    sh = abs(dd) / np.sqrt(s1 ** 2 + s2 ** 2)
    return dict(htest=float(h), gain=float(gain), sigma=float(sig),
                split_half=float(sh), dphi=float(dphi))


def corrupt(ph, kind):
    ph = np.asarray(ph)
    if kind == 'flare':
        n_add = int(0.30 * len(ph))
        return np.concatenate([ph, RNG.uniform(0, 1, n_add)])
    if kind == 'jitter':
        return (ph + RNG.normal(0, 0.10, len(ph))) % 1.0
    raise ValueError(kind)


def main():
    tmpl, band = load_template('J0437-4715')
    # clean J0437 dwells for the photon sample: spread over ObsIDs
    rows = [r for r in csv.DictReader(
        open(PILOT + '/dwells_J0437-4715.csv'))
        if int(r['n_phot']) >= 50 and float(r['exp_s']) >= 300
        and float(r['htest']) >= 20 and r['dphi'] not in ('', 'nan')]
    by_ob = {}
    for r in rows:
        by_ob.setdefault(r['obsid'], []).append(r)
    sample = []
    obs = sorted(by_ob)
    k = 0
    while len(sample) < N_PHOTON_DWELLS:
        o = obs[k % len(obs)]
        cand = by_ob[o][(k // len(obs)) % len(by_ob[o])]
        if cand not in sample:
            sample.append(cand)
        k += 1
        if k > 500:
            break
    print('photon sample: %d dwells over %d obsids'
          % (len(sample), len(set(r['obsid'] for r in sample))), flush=True)

    clean, flared, jittered = [], [], []
    ckpt_path = PILOT + '/repair_flagging_ckpt.json'
    ckpt = {}
    if os.path.exists(ckpt_path):
        ckpt = json.load(open(ckpt_path))
        print('resumed checkpoint: %d dwells' % len(ckpt), flush=True)
    for idx, r in enumerate(sample):
        key = '%s_%.6f' % (r['obsid'], float(r['mjd_mid']))
        if key in ckpt:
            c = ckpt[key]
            clean.append(c['clean'])
            flared.append(c['flare'])
            jittered.append(c['jitter'])
            print('  dwell %d/%d cached' % (idx + 1, len(sample)), flush=True)
            continue
        try:
            ph = dwell_phases('J0437-4715', str(int(float(r['obsid']))), band,
                              float(r['mjd_mid']), float(r['exp_s']))
        except Exception as e:
            print('  dwell %d/%d ERROR: %s' % (idx + 1, len(sample), str(e)[:120]),
                  flush=True)
            continue
        if ph is None or len(ph) < 200:
            print('  skip obsid %s (no phases)' % r['obsid'], flush=True)
            continue
        c0 = dwell_features(ph, tmpl)
        c1 = dwell_features(corrupt(ph, 'flare'), tmpl)
        c2 = dwell_features(corrupt(ph, 'jitter'), tmpl)
        ckpt[key] = {'clean': c0, 'flare': c1, 'jitter': c2}
        with open(ckpt_path, 'w') as f:
            json.dump(ckpt, f)
        clean.append(c0)
        flared.append(c1)
        jittered.append(c2)
        print('  dwell %d/%d done (n=%d)' % (idx + 1, len(sample), len(ph)),
              flush=True)
    clean = np.array([(c['htest'], c['gain'], c['split_half'])
                      for c in clean])
    flared = np.array([(c['htest'], c['gain'], c['split_half'])
                       for c in flared])
    jittered = np.array([(c['htest'], c['gain'], c['split_half'])
                         for c in jittered])

    # ---- tune thresholds for 5% FP on clean ----
    # htest/gain: 5th/95th pct of the full clean CSV sample (n=57 J0437)
    h_all = np.array([float(r['htest']) for r in rows])
    g_all = np.array([float(r['gain']) for r in rows])
    H_T = float(np.percentile(h_all, 5))
    G_T = float(np.percentile(g_all, 5))
    # split-half: |N(0,1)| theory -> 2.58 ~= 1% per-dwell; check clean sample
    S_T = 2.58
    fp_clean = ((clean[:, 0] < H_T) | (clean[:, 1] < G_T)
                | (clean[:, 2] > S_T)).mean()

    def catch(arr):
        h = arr[:, 0] < H_T
        g = arr[:, 1] < G_T
        s = arr[:, 2] > S_T
        return dict(h_only=float(h.mean()), gain_only=float(g.mean()),
                    split_only=float(s.mean()),
                    combined=float((h | g | s).mean()))

    res = dict(
        n_photon_dwells=int(len(clean)),
        thresholds=dict(H_T=H_T, G_T=G_T, S_T=S_T),
        FP_clean=float(fp_clean),
        clean_split_half_median=float(np.median(clean[:, 2])),
        catch_flare=catch(flared),
        catch_jitter=catch(jittered),
        # pilot baseline for comparison
        pilot_H_only_catch_jitter=0.35,
    )
    print(json.dumps({k: v for k, v in res.items()
                      if k != 'thresholds'}, indent=1), flush=True)

    # ---- F2: J0030 per-ObsID offset flag (CSV only, white model v2) ----
    j3 = [r for r in csv.DictReader(open(PILOT + '/dwells_J0030+0451.csv'))
          if int(r['n_phot']) >= 50 and float(r['exp_s']) >= 300
          and float(r['htest']) >= 20 and r['dphi'] not in ('', 'nan')]
    P0 = 0.005757  # J0030 spin period s (from dwells file P0_s column)
    P0 = float(j3[0]['P0_s'])
    white_var = (850e-6) ** 2  # v2 empirical white (s^2)
    obs = {}
    for r in j3:
        ph = float(r['dphi'])
        obs.setdefault(r['obsid'], []).append(ph)
    # unwrap per obsid then mean in seconds
    flagged_obs, flagged_dw = 0, 0
    for ob, phs in obs.items():
        phs = np.unwrap(np.array(phs) * 2 * np.pi) / (2 * np.pi)
        mean_s = phs.mean() * P0
        se = np.sqrt(white_var / len(phs))
        if abs(mean_s) / se > 4.0:
            flagged_obs += 1
            flagged_dw += len(phs)
    res['J0030_obsid_flag'] = dict(n_obsids=len(obs), n_dwells=len(j3),
                                  flagged_obsids=int(flagged_obs),
                                  flagged_dwells=int(flagged_dw),
                                  frac_dwells=float(flagged_dw / len(j3)))
    print('J0030 ObsID-offset flag: %d/%d obsids, %d/%d dwells (%.0f%%)'
          % (flagged_obs, len(obs), flagged_dw, len(j3),
             100 * flagged_dw / len(j3)), flush=True)

    with open(PILOT + '/repair_flagging.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('saved repair_flagging.json', flush=True)


if __name__ == '__main__':
    main()
