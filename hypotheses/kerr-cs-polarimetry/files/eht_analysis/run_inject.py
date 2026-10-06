"""Injection calibration: verified slip injected into REAL visibilities
(RL -> RL*exp(-2i*chi), LR -> LR*exp(+2i*chi) per baseline, chi = 2*pi*gamma*
0.5*(1+tanh((t-t0)/tau)), tau=46.9 s, k=1), then full pipeline.
Threshold per day = observed max Z (no injection). Reports efficiency(gamma)
and the 95%-recovery crossing = 95% CL upper bound on gamma."""
import numpy as np, os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits
from pipeline import raw_triangle_series, stack_from_raw, Bank, TAU_SLIP

DATADIR = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
DAYS = {
    "2017-04-06": ("ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
    "2017-04-07": ("ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
}
GRID_STEP_S = 20.0
# Fine gamma grid; the observable is periodic: signal amplitude propto
# |sin(12*pi*gamma)|, blind at gamma=k/12. We map efficiency vs gamma and
# quote the bound on |sin(12*pi*gamma)|, translated to gamma at small gamma.
GAMMAS = [round(x, 4) for x in np.linspace(0.03, 0.45, 15)]
N_INJ = int(sys.argv[1]) if len(sys.argv) > 1 else 25

null = json.load(open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null_surrogates.json")))
thr95 = {k: float(np.percentile(v, 95)) for k, v in null["null_max"].items()}
thr = null["obs_max"]
print("T95:", thr95, "Tobs:", thr, flush=True)

rng = np.random.default_rng(7)
results = {}
for day, (fhi, flo) in DAYS.items():
    raws, bands = [], []
    for fn in (fhi, flo):
        raw = raw_triangle_series(load_uvfits(os.path.join(DATADIR, fn)))
        raws.append(raw)
        t, d = stack_from_raw(raw, t0_jd=None, combine="diff")
        bands.append({"raw": raw, "t": t})
    g0 = max(b["t"].min() for b in bands) + 3*TAU_SLIP/86400.0
    g1 = min(b["t"].max() for b in bands) - 3*TAU_SLIP/86400.0
    grid = np.arange(g0, g1, GRID_STEP_S/86400.0)
    # precompute banks per band on the common grid
    for b in bands:
        t = b["t"]; ts = (t-t[0])*86400.0; gr = (grid-t[0])*86400.0
        m = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
        b["bank"] = Bank(ts, gr[m]); b["mask"] = m
    day_res = {"gamma": [], "eff": [], "eff95": [], "zrec": [], "amp": []}
    for g in GAMMAS:
        amp = abs(np.sin(12*np.pi*g))  # physical signal amplitude factor
        zrec = []
        for _ in range(N_INJ):
            t0 = float(rng.uniform(g0, g1))
            zday = np.zeros(len(grid))
            for b in bands:
                t, d = stack_from_raw(b["raw"], t0_jd=t0, gamma=g, combine="diff")
                zb, _ = b["bank"].zgrid(d)
                o = np.zeros(len(grid)); o[b["mask"]] = zb
                zday += o/2.0
            win = np.abs(grid - t0)*86400.0 < 3*TAU_SLIP
            zrec.append(float(zday[win].max()) if win.any() else 0.0)
        zrec = np.array(zrec)
        eff = float(np.mean(zrec > thr[day]))
        eff95 = float(np.mean(zrec > thr95[day]))
        day_res["gamma"].append(g); day_res["eff"].append(eff)
        day_res["eff95"].append(eff95); day_res["amp"].append(amp)
        day_res["zrec"].append(zrec.tolist())
        print(f"{day} gamma={g:.3f} amp={amp:.2f}: eff={eff:.2f} eff95={eff95:.2f} medZ={np.median(zrec):.2f}", flush=True)
    results[day] = day_res

json.dump(results, open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/inject_results.json"), "w"))
# Report efficiency tables; gamma_95 interpolated on eff95 (T95 threshold).
# Because the signal is periodic in gamma (amplitude |sin(12*pi*gamma)|), the
# quoted bound is on the amplitude; translated to gamma for small gamma.
for day, r in results.items():
    print(f"--- {day} ---")
    for g, a, e, e95 in zip(r["gamma"], r["amp"], r["eff"], r["eff95"]):
        print(f"  g={g:.3f} amp={a:.2f} eff={e:.2f} eff95={e95:.2f}")
