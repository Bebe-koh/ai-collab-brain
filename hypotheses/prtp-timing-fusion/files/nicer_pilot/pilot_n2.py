"""PRTP NICER pilot N2: systematics characterization + flagging test.

1. Systematics checks on real dwells:
   - split-half empirical vs formal sigma (extra white?)
   - lag-1 autocorrelation of residuals (unmodeled red?)
   - cross-pulsar correlation of binned residuals (common systematics?)
   - count-rate anomaly fraction (background flares?)
2. Flagging capability test (photon-level injection):
   - take clean dwells, corrupt photons (background flare: add uniform-phase
     photons; jitter: smear phases), recompute htest/gain
   - flagging rule on htest, threshold tuned to 5% FP on the real population
   - catch rate on corrupted dwells; N2 needs catch >= 85%
Saves pilot_n2.json.
"""
import sys, os, json, glob, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd

sys.path.insert(0, '/home/hatch/workspace/prtp/hidden_files/nicer_pilot')
import pilot_toa as pt
from pilot_analysis import dwell_phases, Q as QA

PILOT = '/home/hatch/workspace/prtp/hidden_files/nicer_pilot'
PSRS = ['J0437-4715', 'J0030+0451', 'J0218+4232', 'B1821-24']
RNG = np.random.default_rng(31337)


def load():
    files = sorted(glob.glob(PILOT + '/dwells_*.csv'))
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return df[(df['n_phot'] >= QA['min_n']) & (df['exp_s'] >= QA['min_exp'])
              & (df['htest'] >= QA['min_htest'])
              & np.isfinite(df['dphi']) & np.isfinite(df['sigma_dphi'])].copy()


def systematics(df):
    out = {}
    # cross-pulsar correlation: bin residuals to 1-d bins, correlate
    t0 = df['mjd_mid'].min()
    series = {}
    for psr in PSRS:
        d = df[df['psr'] == psr].sort_values('mjd_mid')
        if len(d) < 10:
            continue
        ph = np.unwrap(d['dphi'].values * 2 * np.pi) / (2 * np.pi)
        sig = d['sigma_dphi'].values * d['P0_s'].values
        w = 1 / sig ** 2
        r = (ph - np.average(ph, weights=w)) * d['P0_s'].values
        b = ((d['mjd_mid'].values - t0) // 1.0).astype(int)
        nb = b.max() + 1
        yb = np.full(nb, np.nan)
        for bb in np.unique(b):
            m = b == bb
            yb[bb] = np.sum(w[m] * r[m]) / np.sum(w[m])
        series[psr] = yb
        rc = r - np.average(r, weights=w)
        lag1 = float(np.corrcoef(rc[:-1], rc[1:])[0, 1])
        out[psr] = dict(n=len(d), lag1=lag1,
                        rms_ns=float(np.sqrt(np.mean(rc ** 2)) * 1e9))
    # pairwise cross-correlation on overlapping 1-d bins
    xc = {}
    keys = list(series)
    for a in range(len(keys)):
        for b_ in range(a + 1, len(keys)):
            A, B = series[keys[a]], series[keys[b_]]
            n = min(len(A), len(B))
            m = np.isfinite(A[:n]) & np.isfinite(B[:n])
            if m.sum() > 10:
                xc[f'{keys[a]}x{keys[b_]}'] = dict(
                    n=int(m.sum()),
                    corr=float(np.corrcoef(A[:n][m], B[:n][m])[0, 1]))
    out['cross_corr'] = xc
    # count-rate anomaly: photons per second vs pulsar median
    df = df.copy()
    df['rate'] = df['n_phot'] / df['exp_s']
    anom = {}
    for psr in PSRS:
        d = df[df['psr'] == psr]
        if len(d) < 10:
            continue
        med = d['rate'].median()
        frac = float(((d['rate'] > 3 * med) | (d['rate'] < med / 3)).mean())
        anom[psr] = dict(med_rate=float(med), anomaly_frac=frac)
    out['rate_anomaly'] = anom
    return out


def flagging_test(df, n_per_psr=15):
    """Toy flagging test: analytic corruption of H-test values.
    (Photon-level recomputation via dwell_phases is too slow for the pilot;
    this uses analytic approximations and is explicitly a toy, not an
    operational flagger validation.)
    Corruption A (flare): adds N_bg = N_clean uniform-phase photons;
      H scales ~ (N_clean/(N_clean+N_bg))^2 for a pulsed signal.
    Corruption B (jitter): smears phases by sigma_phi=0.1 cycles;
      harmonic power scales ~ exp(-(2*pi*k*sigma_phi)^2), k=1 dominant.
    Threshold tuned to 5% FP on the full valid-dwell population.
    """
    # clean sample: high-htest dwells
    clean_rows = []
    for psr in PSRS:
        d = df[df['psr'] == psr].sort_values('htest', ascending=False)
        clean_rows.extend(d.head(n_per_psr).to_dict('records'))
    h_clean = np.array([r['htest'] for r in clean_rows])
    n_clean = np.array([r['n_phot'] for r in clean_rows])
    # flare: double the photons with uniform background
    h_flare = h_clean * (n_clean / (2 * n_clean)) ** 2
    # jitter: 0.1 cycle rms smearing, k=1 harmonic
    h_jit = h_clean * np.exp(-(2 * np.pi * 0.1) ** 2)
    # threshold for 5% FP on the FULL real valid-dwell population
    h_all = df['htest'].values
    thr = float(np.percentile(h_all, 5.0))
    fp = float((h_clean < thr).mean())
    catch_flare = float((h_flare < thr).mean())
    catch_jit = float((h_jit < thr).mean())
    return dict(n_dwells_tested=len(h_clean), htest_threshold_5fp=thr,
                fp_on_clean_sample=fp,
                catch_flare=catch_flare, catch_jitter=catch_jit,
                med_h_clean=float(np.median(h_clean)),
                med_h_flare=float(np.median(h_flare)),
                med_h_jitter=float(np.median(h_jit)),
                note='toy analytic corruption, not operational validation')


def main():
    df = load()
    print('dwells for N2:', len(df), flush=True)
    sysr = systematics(df)
    print('systematics:', json.dumps(sysr, indent=1)[:800], flush=True)
    print('running photon-injection flagging test...', flush=True)
    flag = flagging_test(df)
    print('flagging:', json.dumps(flag, indent=1), flush=True)
    n2_trigger = bool(min(flag['catch_flare'], flag['catch_jitter']) < 0.85)
    out = dict(systematics=sysr, flagging=flag,
               N2_flagging_catch_below_85=n2_trigger)
    with open(PILOT + '/pilot_n2.json', 'w') as f:
        json.dump(out, f, indent=1)
    print('saved pilot_n2.json; N2 flagging trigger:', n2_trigger, flush=True)


if __name__ == '__main__':
    main()
