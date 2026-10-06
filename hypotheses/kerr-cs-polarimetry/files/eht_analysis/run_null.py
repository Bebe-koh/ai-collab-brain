"""Null search + circular-shift surrogate calibration (preserves red noise and
hi/lo simultaneity: same roll applied to both bands of a day)."""
import numpy as np, os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits
from pipeline import build_dataset, stack_series, Bank, TAU_SLIP

DATADIR = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_data")
DAYS = {
    "2017-04-06": ("ER6_SGRA_2017_096_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_096_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
    "2017-04-07": ("ER6_SGRA_2017_097_hi_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits",
                   "ER6_SGRA_2017_097_lo_hops_netcal_LMTcal_10s_ALMArot_dtermcal.uvfits"),
}
GRID_STEP_S = 20.0

def prep_day(fhi, flo):
    ds_hi = build_dataset(load_uvfits(os.path.join(DATADIR, fhi)))
    ds_lo = build_dataset(load_uvfits(os.path.join(DATADIR, flo)))
    t_hi, d_hi = stack_series(ds_hi, "diff")
    t_lo, d_lo = stack_series(ds_lo, "diff")
    # absolute grid spanning the overlap
    g0 = max(t_hi.min(), t_lo.min()) + 3*TAU_SLIP/86400.0
    g1 = min(t_hi.max(), t_lo.max()) - 3*TAU_SLIP/86400.0
    grid = np.arange(g0, g1, GRID_STEP_S/86400.0)
    bands = []
    for t, d in ((t_hi, d_hi), (t_lo, d_lo)):
        ts = (t - t[0])*86400.0
        gr = (grid - t[0])*86400.0
        m = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
        bands.append({"bank": Bank(ts, gr[m]), "d": d, "mask": m,
                      "t": t, "n": len(d)})
    return {"grid": grid, "bands": bands}

def day_z(day, rolls=None):
    """Combined (hi+lo)/2 Z on the absolute grid. rolls: per-band int or None."""
    out = np.zeros(len(day["grid"]))
    for bi, b in enumerate(day["bands"]):
        d = b["d"]
        if rolls is not None:
            d = np.roll(d, rolls[bi])
        zb, _ = b["bank"].zgrid(d)
        o = np.zeros(len(day["grid"])); o[b["mask"]] = zb
        out += o/2.0
    return out

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    days = {k: prep_day(*v) for k, v in DAYS.items()}
    for k, day in days.items():
        print(k, "grid pts:", len(day["grid"]), "bands n:", [b["n"] for b in day["bands"]])
    obs = {k: day_z(day) for k, day in days.items()}
    obs_max = {k: float(v.max()) for k, v in obs.items()}
    obs_arg = {k: float(days[k]["grid"][v.argmax()]) for k, v in obs.items()}
    print("OBSERVED max Z:", obs_max)
    print("  at JD:", obs_arg)
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    t_start = time.time()
    null_max = {k: [] for k in days}
    for it in range(N):
        r = {}
        for k, day in days.items():
            kroll = int(rng.integers(0, day["bands"][0]["n"]))
            z = day_z(day, rolls=(kroll, kroll))
            r[k] = z.max()
        for k in days: null_max[k].append(r[k])
        if (it+1) % 500 == 0: print(f"  {it+1}/{N} surrogates, {time.time()-t_start:.0f}s")
    null_max = {k: np.array(v) for k, v in null_max.items()}
    for k in days:
        nm = null_max[k]
        p = float(np.mean(nm >= obs_max[k]))
        print(f"{k}: obs_max={obs_max[k]:.2f} null_mean={nm.mean():.2f} null_std={nm.std():.2f} "
              f"null_max={nm.max():.2f} p(>=obs)={p:.4f}")
    json.dump({"obs_max": obs_max, "obs_arg_jd": obs_arg,
               "null_max": {k: v.tolist() for k, v in null_max.items()},
               "N": N},
              open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null_surrogates.json"), "w"))
    # save observed Z curves (downsampled) for the note
    curves = {}
    for k in days:
        g = days[k]["grid"]; z = obs[k]
        curves[k] = {"jd": g[::5].tolist(), "z": z[::5].tolist()}
    json.dump(curves, open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null_curves.json"), "w"))
