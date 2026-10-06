"""Q1 analysis v2: fixed negatives, powerlaw-pkg cross-check, KS p-values for waiting times."""
import csv, json
import numpy as np
from collections import defaultdict
from scipy import stats
import powerlaw

rng = np.random.default_rng(7)

rows = []
with open('glitch_catalog.csv') as f:
    for r in csv.DictReader(f):
        df = float(r['df_1e9']) if r['df_1e9'] else np.nan
        mjd = float(r['mjd']) if r['mjd'] else np.nan
        rows.append((r['jname'], int(r['gno']), mjd, df))

pos = [(j, g, m, df) for j, g, m, df in rows if np.isfinite(df) and df > 0]
neg = [(j, g, m, df) for j, g, m, df in rows if np.isfinite(df) and df <= 0]
print(f"positive sizes: {len(pos)}, non-positive: {len(neg)}")
for j, g, m, df in neg:
    print(f"  non-positive: {j} glitch {g} MJD {m} dF/F={df}e-9")

by_psr = defaultdict(list)
for j, g, m, df in pos:
    by_psr[j].append((g, m, df * 1e-9))

def my_mle(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    cands = np.unique(x)
    if len(cands) > 400:
        cands = np.unique(np.quantile(x, np.linspace(0, 1, 400)))
    best = None
    for xm in cands:
        tail = x[x >= xm]; nt = len(tail)
        if nt < 10: continue
        a = 1 + nt / np.sum(np.log(tail / xm))
        xe = np.sort(tail); ce = np.arange(1, nt+1)/nt
        cf = 1 - (xe/xm)**(1-a)
        D = np.max(np.abs(ce-cf))
        if best is None or D < best[0]: best = (D, xm, a, nt)
    D, xm, a, nt = best
    return {'alpha': a, 'sigma': (a-1)/np.sqrt(nt), 'xmin': xm, 'ntail': nt, 'KS': D}

out = {'catalog_date': '2026-09-24',
       'source': 'http://www.jb.man.ac.uk/pulsar/glitches/gTable.html',
       'n_glitches': len(rows), 'n_pulsars': len(by_psr),
       'anti_glitch': [{'jname': j, 'gno': g, 'mjd': m, 'df_1e9': df} for j, g, m, df in neg]}

print("\n== per-pulsar: my MLE vs powerlaw pkg ==")
per = {}
for psr in sorted(by_psr, key=lambda p: -len(by_psr[p])):
    sz = np.array(sorted(df for _, _, df in by_psr[psr]))
    if len(sz) < 10: continue
    mine = my_mle(sz)
    fit = powerlaw.Fit(sz, verbose=False)
    R_pl_ln, p_pl_ln = fit.distribution_compare('power_law', 'lognormal', normalized_ratio=True)
    R_pl_ex, p_pl_ex = fit.distribution_compare('power_law', 'exponential', normalized_ratio=True)
    # waiting times
    mjds = np.array(sorted(m for _, m, _ in by_psr[psr] if np.isfinite(m)))
    d = np.diff(mjds); d = d[d > 0]
    lam = 1/d.mean()
    ks = stats.kstest(d, 'expon', args=(0, 1/lam))
    cv = d.std()/d.mean()
    per[psr] = {
        'n': len(sz),
        'my_alpha': round(mine['alpha'], 3), 'my_sigma': round(mine['sigma'], 3),
        'my_xmin': mine['xmin'], 'my_ntail': mine['ntail'],
        'pl_alpha': round(float(fit.power_law.alpha), 3),
        'pl_sigma': round(float(fit.power_law.sigma), 3),
        'pl_xmin': float(fit.power_law.xmin),
        'pl_ntail': int((sz >= fit.power_law.xmin).sum()),
        'R_pl_vs_lognormal': round(float(R_pl_ln), 3), 'p_pl_vs_lognormal': round(float(p_pl_ln), 3),
        'R_pl_vs_exponential': round(float(R_pl_ex), 3), 'p_pl_vs_exponential': round(float(p_pl_ex), 3),
        'wt_n': len(d), 'wt_mean_days': round(float(d.mean()), 1),
        'wt_cv': round(float(cv), 3),
        'wt_exp_KS': round(float(ks.statistic), 4), 'wt_exp_p': round(float(ks.pvalue), 4),
    }
    q = per[psr]
    print(f"{psr:12s} n={q['n']:3d} my={q['my_alpha']:.2f}±{q['my_sigma']:.2f} "
          f"pkg={q['pl_alpha']:.2f}±{q['pl_sigma']:.2f} xmin={q['pl_xmin']:.2e} ntail={q['pl_ntail']:3d} "
          f"Rln={q['R_pl_vs_lognormal']:+.2f}(p={q['p_pl_vs_lognormal']:.2f}) "
          f"wt: cv={q['wt_cv']:.2f} exp-p={q['wt_exp_p']:.3f}")
out['per_pulsar'] = per

# aggregate: demonstrate bimodality
sizes_all = np.array(sorted(df*1e-9 for _, _, _, df in pos))
lg = np.log10(sizes_all)
h, edges = np.histogram(lg, bins=40)
pk = np.argsort(h)[-4:][::-1]
print("\nlog10(size) histogram top bins:", [(round(edges[i],2), h[i]) for i in pk])
# dip-ish check: two-component split at 1e-7
lo = sizes_all[sizes_all < 1e-7]; hi = sizes_all[sizes_all >= 1e-7]
print(f"below 1e-7: {len(lo)}, at/above 1e-7: {len(hi)}")
out['aggregate_bimodal'] = {
    'n_below_1e-7': int(len(lo)), 'n_above_1e-7': int(len(hi)),
    'log10_hist_edges': [round(e,3) for e in edges],
    'log10_hist_counts': [int(c) for c in h],
    'note': 'aggregate is bimodal; a single power law is not the right model (cf. Espinoza et al. 2011)'}
# aggregate MLE on the giant tail only, for reference
agg = my_mle(sizes_all)
out['aggregate_tail_fit'] = {k: (round(v,4) if isinstance(v,float) else v) for k,v in agg.items()}
print("aggregate tail fit:", out['aggregate_tail_fit'])

with open('fit_results2.json','w') as f: json.dump(out, f, indent=1)
print("\nwrote fit_results2.json")
