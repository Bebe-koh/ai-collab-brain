"""Injection calibration with the DIFFERENCED pipeline.
Thresholds: 95th percentile of surrogate null (primary, conservative) and
observed max (cross-check). Reports efficiency(gamma) and gamma_95."""
import numpy as np, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits
from pipeline import raw_triangle_series, stack_from_raw, difference_series, DiffBank, TAU_SLIP

DATADIR = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
DAYS = {
    "2017-04-06": ("ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
    "2017-04-07": ("ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
}
GRID_STEP_S = 20.0
GAMMAS = [0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.5]
N_INJ = int(sys.argv[1]) if len(sys.argv) > 1 else 30

null = json.load(open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null2_surrogates.json")))
T95 = {k: float(np.percentile(v, 95)) for k, v in null["null_max"].items()}
Tobs = null["obs_max"]
print("T95:", T95, "Tobs:", Tobs, flush=True)

rng = np.random.default_rng(11)
results = {}
for day, (fhi, flo) in DAYS.items():
    bands = []
    for fn in (fhi, flo):
        raw = raw_triangle_series(load_uvfits(os.path.join(DATADIR, fn)))
        bands.append({"raw": raw})
    # reference (uninjected) grids from one band for the t0 range
    t_ref, _ = stack_from_raw(bands[0]["raw"], t0_jd=None, combine="diff")
    g0 = t_ref.min() + 3*TAU_SLIP/86400.0; g1 = t_ref.max() - 3*TAU_SLIP/86400.0
    grid = np.arange(g0, g1, GRID_STEP_S/86400.0)
    for b in bands:
        t, d = stack_from_raw(b["raw"], t0_jd=None, combine="diff")
        te, e, keep = difference_series(t, d)
        b.update({"t": t, "e": e, "keep": keep})
        ts = (t-t[0])*86400.0; gr = (grid-t[0])*86400.0
        m = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
        b["bank"] = DiffBank(ts, gr[m], keep); b["mask"] = m
    day_res = {"gamma": [], "eff95": [], "effobs": [], "zrec": []}
    for g in GAMMAS:
        zrec = []
        for _ in range(N_INJ):
            t0 = float(rng.uniform(g0, g1))
            zday = np.zeros(len(grid))
            for b in bands:
                t, d = stack_from_raw(b["raw"], t0_jd=t0, gamma=g, combine="diff")
                te, e, keep = difference_series(t, d)
                # note: keep may differ slightly from bank's keep; rebuild bank cheap? No -
                # use the precomputed bank but e must match its keep. Recompute keep-matched e:
                # simplest: rebuild DiffBank per injection (fast: 3 small matmuls setup)
                ts = (t-t[0])*86400.0; gr = (grid-t[0])*86400.0
                mm = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
                bk = DiffBank(ts, gr[mm], keep)
                zb, _ = bk.zgrid(e)
                o = np.zeros(len(grid)); o[mm] = zb
                zday += o/2.0
            win = np.abs(grid - t0)*86400.0 < 3*TAU_SLIP
            zrec.append(float(zday[win].max()) if win.any() else 0.0)
        zrec = np.array(zrec)
        e95 = float(np.mean(zrec > T95[day])); eobs = float(np.mean(zrec > Tobs[day]))
        day_res["gamma"].append(g); day_res["eff95"].append(e95)
        day_res["effobs"].append(eobs); day_res["zrec"].append(zrec.tolist())
        print(f"{day} g={g:4.2f}: eff95={e95:.2f} effobs={eobs:.2f} medZ={np.median(zrec):.2f}", flush=True)
    results[day] = day_res

json.dump(results, open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/inject2_results.json"), "w"))
for day, r in results.items():
    gs = np.array(r["gamma"])
    for key, lab in (("eff95", "T95"), ("effobs", "Tobs")):
        es = np.array(r[key]); g95 = None
        for i in range(len(gs)-1):
            if es[i] < 0.95 <= es[i+1]:
                f = (0.95-es[i])/(es[i+1]-es[i]); g95 = gs[i]+f*(gs[i+1]-gs[i]); break
        print(f"{day} {lab}: gamma_95 ~ {g95}")
