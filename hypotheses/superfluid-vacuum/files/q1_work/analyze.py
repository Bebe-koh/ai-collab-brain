"""Q1 glitch universality: power-law MLE fits (Clauset-Shalizi-Newman) to JBO glitch catalog.
Catalog snapshot: fetched 2026-09-24 from http://www.jb.man.ac.uk/pulsar/glitches/gTable.html
Columns: jname, bname, gno, mjd, df_1e9  (df_1e9 = Delta nu / nu in units of 1e-9)
"""
import csv, json
import numpy as np
from collections import defaultdict

rng = np.random.default_rng(42)

def load():
    rows = []
    with open('glitch_catalog.csv') as f:
        for r in csv.DictReader(f):
            df = float(r['df_1e9']) if r['df_1e9'] else np.nan
            mjd = float(r['mjd']) if r['mjd'] else np.nan
            rows.append((r['jname'], int(r['gno']), mjd, df))
    return rows

def clauset_fit(x, xmin_candidates=None, n_boot=250):
    """MLE power-law fit with xmin chosen by min KS distance. Returns dict."""
    x = np.sort(np.asarray(x, dtype=float))
    x = x[np.isfinite(x) & (x > 0)]
    n = len(x)
    if n < 10:
        return {'n': n, 'ok': False, 'reason': 'n<10'}
    cands = np.unique(x) if xmin_candidates is None else xmin_candidates
    # limit candidates for speed on large n
    if len(cands) > 400:
        cands = np.unique(np.quantile(x, np.linspace(0, 1, 400)))
    best = None
    for xm in cands:
        tail = x[x >= xm]
        nt = len(tail)
        if nt < 10:
            continue
        a = 1.0 + nt / np.sum(np.log(tail / xm))
        # KS distance between empirical CDF and fitted power law
        xe = np.sort(tail)
        cdf_emp = np.arange(1, nt + 1) / nt
        cdf_fit = 1.0 - (xe / xm) ** (1.0 - a)
        D = np.max(np.abs(cdf_emp - cdf_fit))
        if best is None or D < best[0]:
            best = (D, xm, a, nt)
    if best is None:
        return {'n': n, 'ok': False, 'reason': 'no valid xmin'}
    D, xm, a, nt = best
    sigma = (a - 1.0) / np.sqrt(nt)
    # bootstrap p-value (goodness of fit): fraction of synthetic KS >= observed
    tail = x[x >= xm]
    count = 0
    for _ in range(n_boot):
        # synthetic: power law above xm + resampled below
        u = rng.random(nt)
        synth_tail = xm * (1.0 - u) ** (1.0 / (1.0 - a))
        below = x[x < xm]
        nb = n - nt
        synth = np.concatenate([synth_tail, rng.choice(below, size=nb, replace=True)] if nb else [synth_tail])
        synth = np.sort(synth)
        # refit xmin on synthetic (use same xm for speed -> conservative)
        st = synth[synth >= xm]; m = len(st)
        if m < 10:
            continue
        ab = 1.0 + m / np.sum(np.log(st / xm))
        se = np.sort(st)
        ce = np.arange(1, m + 1) / m
        cf = 1.0 - (se / xm) ** (1.0 - ab)
        Db = np.max(np.abs(ce - cf))
        if Db >= D:
            count += 1
    p = count / n_boot
    return {'n': n, 'ntail': nt, 'ok': True, 'xmin': float(xm), 'alpha': float(a),
            'sigma': float(sigma), 'KS': float(D), 'p_boot': float(p)}

def lognormal_lr(x, xm):
    """Log-likelihood ratio: power law vs lognormal on tail x>=xm. Positive favors power law."""
    tail = np.sort(np.asarray(x))[np.asarray(x) >= xm]
    nt = len(tail)
    a = 1.0 + nt / np.sum(np.log(tail / xm))
    ll_pl = nt * np.log(a - 1) - nt * np.log(xm) - a * np.sum(np.log(tail / xm))
    mu = np.mean(np.log(tail)); sg = np.std(np.log(tail), ddof=0)
    # truncated lognormal (tail only), approximate normalization via survival of full dist
    from math import erf, sqrt, log, pi
    def Phi(z): return 0.5 * (1 + erf(z / sqrt(2)))
    norm = 1.0 - Phi((np.log(xm) - mu) / sg)
    ll_ln = (-np.sum(np.log(tail)) - nt * 0.5 * np.log(2 * pi) - nt * np.log(sg)
             - np.sum((np.log(tail) - mu) ** 2) / (2 * sg ** 2) - nt * np.log(norm))
    # Vuong-ish sigma
    d = (np.log(a - 1) - np.log(xm) - a * np.log(tail / xm)) - \
        (-np.log(tail) - 0.5 * np.log(2 * pi) - np.log(sg)
         - (np.log(tail) - mu) ** 2 / (2 * sg ** 2) - np.log(norm))
    R = ll_pl - ll_ln
    s2 = np.var(d, ddof=1)
    z = R / np.sqrt(nt * s2) if s2 > 0 else 0.0
    return R, z

def main():
    rows = load()
    by_psr = defaultdict(list)
    for jname, gno, mjd, df in rows:
        by_psr[jname].append((gno, mjd, df))
    sizes_all = np.array([df * 1e-9 for _, _, _, df in rows if np.isfinite(df)])
    print(f"total glitches with size: {len(sizes_all)} / {len(rows)}")
    print(f"size range: {sizes_all.min():.3e} .. {sizes_all.max():.3e}")

    out = {}
    print("\n== aggregate size fit ==")
    agg = clauset_fit(sizes_all)
    out['aggregate'] = agg
    print(json.dumps(agg, indent=1))
    if agg['ok']:
        R, z = lognormal_lr(sizes_all, agg['xmin'])
        print(f"PL vs lognormal: R={R:.2f}, z={z:.2f} (positive favors power law)")
        out['aggregate']['LR_pl_lognorm'] = R
        out['aggregate']['LR_z'] = z

    print("\n== per-pulsar size fits (n>=10) ==")
    per = {}
    for psr in sorted(by_psr, key=lambda p: -len(by_psr[p])):
        sz = np.array([df * 1e-9 for _, _, df in by_psr[psr] if np.isfinite(df)])
        if len(sz) < 10:
            continue
        fit = clauset_fit(sz, n_boot=100)
        per[psr] = fit
        print(f"{psr:12s} n={len(sz):3d} alpha={fit.get('alpha', float('nan')):.2f}±{fit.get('sigma', float('nan')):.2f} "
              f"xmin={fit.get('xmin', float('nan')):.2e} ntail={fit.get('ntail',0)} p={fit.get('p_boot', float('nan')):.2f}")
    out['per_pulsar'] = per

    print("\n== waiting times (days), per pulsar n>=10 ==")
    wt = {}
    for psr in sorted(by_psr, key=lambda p: -len(by_psr[p])):
        mjds = np.array(sorted(m for _, m, _ in by_psr[psr] if np.isfinite(m)))
        if len(mjds) < 11:
            continue
        d = np.diff(mjds)
        d = d[d > 0]
        # exponential fit (Poisson): rate = 1/mean
        lam = 1.0 / d.mean()
        # KS test vs exponential
        de = np.sort(d)
        ce = np.arange(1, len(de) + 1) / len(de)
        cf = 1.0 - np.exp(-lam * de)
        D = np.max(np.abs(ce - cf))
        # power-law fit on waiting times
        pl = clauset_fit(d, n_boot=50)
        # CV of waiting times (1.0 = Poisson)
        cv = d.std() / d.mean()
        wt[psr] = {'n': len(d), 'mean_days': float(d.mean()), 'cv': float(cv),
                   'exp_KS': float(D), 'pl': pl}
        pa = pl.get('alpha', float('nan')); ps = pl.get('sigma', float('nan'))
        print(f"{psr:12s} nwt={len(d):3d} mean={d.mean():8.1f}d cv={cv:.2f} expKS={D:.3f} "
              f"pl_alpha={pa:.2f}±{ps:.2f} p={pl.get('p_boot', float('nan')):.2f}")
    out['waiting_times'] = wt

    # bimodality: histogram of log10 sizes
    h, edges = np.histogram(np.log10(sizes_all), bins=40)
    out['logsize_hist'] = {'edges': edges.tolist(), 'counts': h.tolist()}
    print("\nlog10(size) histogram peaks at:", edges[np.argsort(h)[-3:]][::-1])

    with open('fit_results.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("\nwrote fit_results.json")

main()
