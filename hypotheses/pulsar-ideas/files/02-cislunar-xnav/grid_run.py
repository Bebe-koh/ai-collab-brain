"""Full experiment grid for the cislunar XNAV design study."""
import numpy as np
import time
from cislunar_xnav_sim import gen_truth, run_case, run_baseline

if __name__ == "__main__":
    t0 = time.time()
    ts, xs = gen_truth(srp=0.0)  # matched dynamics; SRP sensitivity separate
    Ms = [1, 10, 100, 1000, 3300]
    sigmas = [0.3e-6, 1e-6, 3e-6, 10e-6]
    seeds = [0, 1, 2]
    res = []
    for M in Ms:
        for s in sigmas:
            for seed in seeds:
                rms, ps, nm = run_case(ts, xs, s, M, seed=seed)
                res.append((M, s, seed, rms, ps, nm))
                print(f"M={M:5d} sigma={s*1e6:4.1f}us seed={seed}: "
                      f"rms={rms*1000:8.1f} m (pred {ps*1000:.1f} m)", flush=True)
    # baselines (3 seeds)
    b = [run_baseline(ts, xs, seed=s) for s in seeds]
    print(f"baseline rms: {np.mean(b)/1000:.1f} km +/- {np.std(b)/1000:.1f}")
    arr = np.array(res, dtype=[("M", float), ("sigma", float), ("seed", int),
                              ("rms", float), ("pred", float), ("nmeas", int)])
    np.savez("grid_results.npz", arr=arr,
             baseline=np.array(b), Ms=np.array(Ms), sigmas=np.array(sigmas))
    print(f"TOTAL {time.time()-t0:.0f}s — saved grid_results.npz")
