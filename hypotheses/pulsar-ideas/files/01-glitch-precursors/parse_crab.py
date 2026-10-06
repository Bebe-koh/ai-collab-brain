#!/usr/bin/env python3
"""Parse Jodrell Bank Crab monthly ephemeris (crab2.txt) into a clean table.

Source: https://www.jb.man.ac.uk/pulsar/crab/crab2.txt
Columns (per header): Date MJD t_MIT t_JPL t_acc nu sigma_nu nudot sigma_nudot DM [DMDot] tau_408 [notes]
  sigma_nu in units of 1e-9 Hz; nudot/sigma_nudot in 1e-15 s^-2.
Layout changes partway (t_MIT dropped, DMDot added after Nov 2011).
Robust approach: locate MJD (integer ~47000-62000), nu (~29.5), nudot (~-3.7e5)
by VALUE, not column position.
"""
import re
import numpy as np

SRC = "/home/hatch/workspace/pulsar-ideas/01-glitch-precursors/crab2.txt"

rows = []
for line in open(SRC):
    line = line.rstrip("\n")
    toks = line.split()
    if not toks or not re.match(r"\d{2}$", toks[0]) and not re.match(r"\d{2}", toks[0]):
        continue
    # data rows start with day-of-month like '15' followed by MON and year
    if not (toks[0].isdigit() and len(toks) > 4):
        continue
    try:
        mjd = float(toks[3])  # '15 MAY 88 47296 ...' -> toks[3]
    except (ValueError, IndexError):
        continue
    if not (47000 < mjd < 62000):
        continue
    # find nu: token ~29-30 with decimals, followed by small-int sigma
    # find nudot: token ~ -3.6e5..-3.8e5 (written like -378616.35)
    nums = []
    for t in toks:
        tc = t.strip("()")
        try:
            nums.append((t, float(tc)))
        except ValueError:
            pass
    nu = nudot = s_nu = s_nd = None
    vals = [v for _, v in nums]
    for i, v in enumerate(vals):
        if 29.0 < v < 30.5 and nu is None:
            nu = v
            # sigma_nu: next small value (typically 1..100)
            if i + 1 < len(vals) and 0 < vals[i + 1] < 5000:
                s_nu = vals[i + 1]
        if -390000 < v < -360000 and nudot is None:
            nudot = v
            if i + 1 < len(vals) and 0 < vals[i + 1] < 5000:
                s_nd = vals[i + 1]
    if nu is None or nudot is None:
        continue
    rows.append(dict(mjd=mjd, nu=nu, s_nu=s_nu if s_nu else np.nan,
                     nudot=nudot, s_nd=s_nd if s_nd else np.nan))

rows.sort(key=lambda r: r["mjd"])
mjd = np.array([r["mjd"] for r in rows])
nu = np.array([r["nu"] for r in rows])
s_nu = np.array([r["s_nu"] for r in rows]) * 1e-9  # Hz
nudot = np.array([r["nudot"] for r in rows]) * 1e-15  # s^-2

print(f"rows: {len(rows)}, MJD {mjd[0]:.0f}..{mjd[-1]:.0f}")
print(f"nu[0]={nu[0]:.10f} s_nu[0]={s_nu[0]:.2e} Hz")
print(f"nu[-1]={nu[-1]:.10f}")
# duplicates?
print("duplicate MJDs:", len(mjd) - len(np.unique(np.round(mjd, 3))))
np.savez("crab_monthly.npz", mjd=mjd, nu=nu, s_nu=s_nu, nudot=nudot, s_nd=np.array([r["s_nd"] for r in rows]))
print("saved crab_monthly.npz")
