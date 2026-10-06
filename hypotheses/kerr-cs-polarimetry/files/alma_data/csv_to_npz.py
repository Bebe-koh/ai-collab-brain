#!/usr/bin/env python3
"""Rebuild the SGRA2017_*_IQUV.npz files from the repo's CSV exports.

The repo ships plain CSVs (binaries corrupt through some app connectors);
evpa_transient_search_v2.py reads NPZ. Run this once to regenerate the
NPZs locally, then run v2 with the NPZ paths as arguments:

    python3 csv_to_npz.py
    python3 evpa_transient_search_v2.py SGRA2017_X4947_IQUV.npz SGRA2017_X448f_IQUV.npz SGRA2017_X4227_IQUV.npz

The round-trip is value-identical to the originals (CSV was exported at
%.10f precision; spot-check a few rows against the repo CSV after running).
"""
import csv
import numpy as np

META = {
    "X4227": "uid___A002_Xbec3cb_X4227",
    "X448f": "uid___A002_Xbec3cb_X448f",
    "X4947": "uid___A002_Xbec3cb_X4947",
}
SPW_FREQ = np.array([213.1, 215.1, 227.1, 229.1])
FIELD = "Sagittarius_A_star"
UNITS = "Jy (visibility-averaged, APP MS DATA column)"


def convert(sfx):
    rows = list(csv.DictReader(open(f"SGRA2017_{sfx}_IQUV.csv")))
    n = len(rows)
    mjd = np.array([float(r["mjd"]) for r in rows])
    I = np.array([[float(r[f"I{i}"]) for i in range(4)] for r in rows])
    Q = np.array([[float(r[f"Q{i}"]) for i in range(4)] for r in rows])
    U = np.array([[float(r[f"U{i}"]) for i in range(4)] for r in rows])
    V = np.array([[float(r[f"V{i}"]) for i in range(4)] for r in rows])
    np.savez(f"SGRA2017_{sfx}_IQUV.npz", mjd=mjd, I=I, Q=Q, U=U, V=V,
             spw_freq_GHz=SPW_FREQ, eb=np.array(META[sfx]),
             field=np.array(FIELD), units=np.array(UNITS))
    print(f"SGRA2017_{sfx}_IQUV.npz: {n} integrations")


if __name__ == "__main__":
    for sfx in ["X4227", "X448f", "X4947"]:
        convert(sfx)
