"""Experiment 2 — radiometer-grounded realistic configs.
1-hr integrations, single steerable dish cycling 4 pulsars.
sigma values from radiometer calc (T_sys=80K, B=200MHz, J0437-class):
  10-m dish -> ~2 us/hr ; 5-m -> ~7 us/hr ; 3-m -> ~20 us/hr
"""
import numpy as np
import time
from cislunar_xnav_sim import gen_truth, run_case, run_baseline

if __name__ == "__main__":
    t0 = time.time()
    ts, xs = gen_truth(srp=0.0)
    configs = [
        ("R1_10m", 2e-6, 3600.0, [1, 3300]),
        ("R2_5m", 7e-6, 3600.0, [1, 3300]),
        ("R3_3m", 20e-6, 3600.0, [1]),
    ]
    seeds = [0, 1, 2]
    out = []
    for name, sig, dtm, Ms in configs:
        for M in Ms:
            for seed in seeds:
                rms, ps, nm = run_case(ts, xs, sig, M, seed=seed,
                                      dt_meas=dtm)
                out.append((name, M, seed, rms, ps, nm))
                print(f"{name} M={M:5d} seed={seed}: rms={rms*1000:9.1f} m "
                      f"(pred {ps*1000:.1f} m) n={nm}", flush=True)
    arr = np.array(out, dtype=[("cfg", "U8"), ("M", float), ("seed", int),
                              ("rms", float), ("pred", float), ("nmeas", int)])
    np.savez("grid2_results.npz", arr=arr)
    print(f"TOTAL {time.time()-t0:.0f}s — saved grid2_results.npz")
