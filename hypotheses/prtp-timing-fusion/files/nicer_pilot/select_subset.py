"""Select a focused subset of complete ObsIDs for Pass 2.
Strategy: dense window (58314-58374) + sparse sampling across full span.
"""
import csv, glob, os

PILOT = "/home/hatch/workspace/prtp/hidden_files/nicer_pilot"
OUT = PILOT + "/data"

complete = []
with open(PILOT + "/obsids.csv") as f:
    for r in csv.DictReader(f):
        d = os.path.join(OUT, r['obsid'])
        ob = glob.glob(d + '/ni*.orb*')
        ev = glob.glob(d + '/ni*_0mpu7_cl.evt*')
        if ob and os.path.getsize(ob[0]) > 50000 and \
           ev and os.path.getsize(ev[0]) > 1000:
            complete.append(r)

# group by pulsar, sort by MJD
by_psr = {}
for r in complete:
    by_psr.setdefault(r['psr'], []).append(r)
for p in by_psr:
    by_psr[p].sort(key=lambda r: float(r['mjd']))

subset = []
for psr, lst in sorted(by_psr.items()):
    # dense window
    dense = [r for r in lst if 58314 <= float(r['mjd']) <= 58374]
    # sparse: outside dense, pick every kth to get ~25
    sparse = [r for r in lst if not (58314 <= float(r['mjd']) <= 58374)]
    n_sparse = 25 if psr in ('J0437-4715', 'J0030+0451') else len(sparse)
    if len(sparse) > n_sparse:
        step = len(sparse) / n_sparse
        sparse = [sparse[int(i * step)] for i in range(n_sparse)]
    sel = dense + sparse
    print(f"{psr}: dense={len(dense)} sparse={len(sparse)} total={len(sel)}")
    subset.extend(sel)

with open(PILOT + "/obsids_subset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["obsid", "psr", "mjd"])
    w.writeheader()
    for r in subset:
        w.writerow({"obsid": r["obsid"], "psr": r["psr"], "mjd": r["mjd"]})
print(f"wrote {len(subset)} to obsids_subset.csv")
