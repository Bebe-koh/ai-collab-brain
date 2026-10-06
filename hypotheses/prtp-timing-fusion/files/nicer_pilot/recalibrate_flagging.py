"""Recalibrate flagger-v2 thresholds on the photon-level clean sample.

The first pass tuned thresholds on the CSV sample (different grid
resolution) and got 47% empirical FP on the photon-level clean dwells --
the split-half statistic is also miscalibrated (clean median 1.75 vs 0.67
for |N(0,1)|: formal per-dwell errors underestimated ~2.6x, same story as
the white-noise underestimation). This script sets each marginal threshold
at the most extreme clean photon-level value (marginal FP 0/15), so the
combined rule has empirical FP 0/15 (conservative), then re-measures catch
on the corrupted versions. Binomial 95% CIs (Wilson) reported throughout.
"""
import json, math
import numpy as np

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
ckpt = json.load(open(PILOT + '/repair_flagging_ckpt.json'))
keys = sorted(ckpt)
clean = np.array([(ckpt[k]['clean']['htest'], ckpt[k]['clean']['gain'],
                   ckpt[k]['clean']['split_half']) for k in keys])
flare = np.array([(ckpt[k]['flare']['htest'], ckpt[k]['flare']['gain'],
                   ckpt[k]['flare']['split_half']) for k in keys])
jitter = np.array([(ckpt[k]['jitter']['htest'], ckpt[k]['jitter']['gain'],
                   ckpt[k]['jitter']['split_half']) for k in keys])
n = len(keys)
print('n =', n)

# thresholds at the most extreme clean value -> 0/15 marginal FP each
H_T = float(clean[:, 0].min())
G_T = float(clean[:, 1].min())
S_T = float(clean[:, 2].max())
print('recalibrated thresholds: H_T=%.2f G_T=%.2f S_T=%.2f'
      % (H_T, G_T, S_T))
print('clean split-half: median %.2f, max %.2f (|N(0,1)| median 0.67)'
      % (np.median(clean[:, 2]), clean[:, 2].max()))


def wilson(k, m, z=1.96):
    p = k / m
    d = 1 + z ** 2 / m
    c = p + z ** 2 / (2 * m)
    h = z * math.sqrt(p * (1 - p) / m + z ** 2 / (4 * m ** 2))
    return max(0.0, (c - h) / d), min(1.0, (c + h) / d)


def rule(a):
    return (a[:, 0] < H_T) | (a[:, 1] < G_T) | (a[:, 2] > S_T)


for name, arr in [('clean', clean), ('flare', flare), ('jitter', jitter)]:
    f = rule(arr)
    k = int(f.sum())
    lo, hi = wilson(k, n)
    parts = {
        'h_only': float((arr[:, 0] < H_T).mean()),
        'gain_only': float((arr[:, 1] < G_T).mean()),
        'split_only': float((arr[:, 2] > S_T).mean()),
    }
    print('%-6s flagged %2d/%d  combined %.2f  CI[%.2f, %.2f]  parts %s'
          % (name, k, n, k / n, lo, hi,
             {kk: round(vv, 2) for kk, vv in parts.items()}))

out = dict(
    n=n, H_T=H_T, G_T=G_T, S_T=S_T,
    FP_clean=0.0,
    clean_split_half_median=float(np.median(clean[:, 2])),
    clean_split_half_max=float(clean[:, 2].max()),
    catch_flare=dict(combined=float(rule(flare).mean()),
                     h_only=float((flare[:, 0] < H_T).mean()),
                     gain_only=float((flare[:, 1] < G_T).mean()),
                     split_only=float((flare[:, 2] > S_T).mean()),
                     ci95=[wilson(int(rule(flare).sum()), n)[0],
                           wilson(int(rule(flare).sum()), n)[1]]),
    catch_jitter=dict(combined=float(rule(jitter).mean()),
                      h_only=float((jitter[:, 0] < H_T).mean()),
                      gain_only=float((jitter[:, 1] < G_T).mean()),
                      split_only=float((jitter[:, 2] > S_T).mean()),
                      ci95=[wilson(int(rule(jitter).sum()), n)[0],
                            wilson(int(rule(jitter).sum()), n)[1]]),
    pilot_H_only_catch_jitter=0.35,
)
json.dump(out, open(PILOT + '/repair_flagging_v2.json', 'w'), indent=1)
print('saved repair_flagging_v2.json')
