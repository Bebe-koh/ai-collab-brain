"""Minimal subset: 10 ObsIDs per pulsar with good time spread."""
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

by_psr = {}
for r in complete:
    by_psr.setdefault(r['psr'], []).append(r)

subset = []
for psr in sorted(by_psr):
    lst = sorted(by_psr[psr], key=lambda r: float(r['mjd']))
    # pick 10 spread across the span
    n = 10
    if len(lst) <= n:
        sel = lst
    else:
        idx = [int(i * (len(lst) - 1) / (n - 1)) for i in range(n)]
        sel = [lst[i] for i in idx]
    print(f"{psr}: {len(sel)} obsids, MJD {sel[0]['mjd']} to {sel[-1]['mjd']}")
    subset.extend(sel)

with open(PILOT + "/obsids_minimal.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["obsid", "psr", "mjd"])
    w.writeheader()
    for r in subset:
        w.writerow({"obsid": r["obsid"], "psr": r["psr"], "mjd": r["mjd"]})
print(f"wrote {len(subset)}")
