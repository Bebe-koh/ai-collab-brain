"""Null search + surrogates with the DIFFERENCED pipeline (white-ish noise).
Same circular-shift surrogate scheme (common roll for hi/lo of a day)."""
import numpy as np, os, sys, json, time
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

def prep_day(fhi, flo):
    bands = []
    for fn in (fhi, flo):
        raw = raw_triangle_series(load_uvfits(os.path.join(DATADIR, fn)))
        t, d = stack_from_raw(raw, t0_jd=None, combine="diff")
        te, e, keep = difference_series(t, d)
        bands.append({"t": t, "e": e, "keep": keep})
    g0 = max(b["t"].min() for b in bands) + 3*TAU_SLIP/86400.0
    g1 = min(b["t"].max() for b in bands) - 3*TAU_SLIP/86400.0
    grid = np.arange(g0, g1, GRID_STEP_S/86400.0)
    for b in bands:
        t = b["t"]; ts = (t-t[0])*86400.0; gr = (grid-t[0])*86400.0
        m = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
        b["bank"] = DiffBank(ts, gr[m], b["keep"]); b["mask"] = m
    return {"grid": grid, "bands": bands}

def day_z(day, rolls=None):
    out = np.zeros(len(day["grid"]))
    for bi, b in enumerate(day["bands"]):
        e = b["e"]
        if rolls is not None:
            e = np.roll(e, rolls[bi])
        zb, _ = b["bank"].zgrid(e)
        o = np.zeros(len(day["grid"])); o[b["mask"]] = zb
        out += o/2.0
    return out

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    days = {k: prep_day(*v) for k, v in DAYS.items()}
    for k, day in days.items():
        print(k, "grid pts:", len(day["grid"]), "e n:", [len(b["e"]) for b in day["bands"]], flush=True)
    obs = {k: day_z(day) for k, day in days.items()}
    obs_max = {k: float(v.max()) for k, v in obs.items()}
    obs_arg = {k: float(days[k]["grid"][v.argmax()]) for k, v in obs.items()}
    print("OBSERVED max Z:", obs_max, flush=True)
    print("  at JD:", obs_arg, flush=True)
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    t_start = time.time()
    null_max = {k: [] for k in days}
    for it in range(N):
        for k, day in days.items():
            kroll = int(rng.integers(0, len(day["bands"][0]["e"])))
            z = day_z(day, rolls=(kroll, kroll))
            null_max[k].append(z.max())
        if (it+1) % 500 == 0: print(f"  {it+1}/{N}, {time.time()-t_start:.0f}s", flush=True)
    null_max = {k: np.array(v) for k, v in null_max.items()}
    for k in days:
        nm = null_max[k]
        p = float(np.mean(nm >= obs_max[k]))
        print(f"{k}: obs={obs_max[k]:.2f} null_mean={nm.mean():.2f} std={nm.std():.2f} "
              f"p95={np.percentile(nm,95):.2f} p(>=obs)={p:.4f}", flush=True)
    json.dump({"obs_max": obs_max, "obs_arg_jd": obs_arg,
               "null_max": {k: v.tolist() for k, v in null_max.items()}, "N": N},
              open(os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/eht_analysis/null2_surrogates.json"), "w"))
