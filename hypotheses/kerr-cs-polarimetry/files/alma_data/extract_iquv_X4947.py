#!/usr/bin/env python3
"""Memory-efficient per-integration Stokes IQUV extraction from APP MS.

Reads the CORRECTED_DATA column in time chunks, averages over baselines
and channels per integration, computes Stokes IQUV for linear feeds:
  I = (XX + YY)/2, Q = (XX - YY)/2, U = (XY + YX)/2, V = -i(XY - YX)/2

Outputs NPZ with time (MJD), IQUV per SPW, and flags.
"""
import os, sys
import numpy as np

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data")
MS = os.path.join(BASE, "restore/calibrated/uid___A002_Xbec3cb_X4947.polcalibrated.APP.ms")
OUT = os.path.join(BASE, "sgra_work/SGRA2017_X4947_IQUV.npz")

print("[iquv] opening MS...", flush=True)
from casatools import table, ms as mstool

# Get SPW frequencies
tb = table()
tb.open(os.path.join(MS, 'SPECTRAL_WINDOW'))
chan_freq = tb.getcol('CHAN_FREQ')  # (nchan, nspw)
tb.close()
nspw = chan_freq.shape[1]
spw_freq = np.mean(chan_freq, axis=0)  # mean freq per SPW
print(f"[iquv] {nspw} SPWs, freqs GHz: {spw_freq/1e9}", flush=True)

# Get field ID for Sgr A*
tb.open(os.path.join(MS, 'FIELD'))
names = list(tb.getcol('NAME'))
sgra_fid = names.index('Sagittarius_A_star')
tb.close()
print(f"[iquv] Sgr A* field id: {sgra_fid}", flush=True)

# Get time range and scan info via ms tool (lightweight)
ms = mstool()
ms.open(MS)
scansum = ms.getscansummary()
ms.close()
# Collect Sgr A* scans
sgra_scans = [int(s) for s, info in scansum.items() if info['0']['FieldId'] == sgra_fid]
print(f"[iquv] {len(sgra_scans)} Sgr A* scans", flush=True)

# Process in chunks: iterate over scans, read one scan at a time
tb.open(MS)
# Get column keywords for units
times_list, I_list, Q_list, U_list, V_list = [], [], [], [], []
nint = 0

# Query by scan to keep memory bounded
for scan in sorted(sgra_scans):
    # Select this scan + Sgr A* field
    # Use taql via tb.query
    try:
        tbs = tb.query(f"SCAN_NUMBER=={scan} && FIELD_ID=={sgra_fid}")
    except Exception as e:
        print(f"[iquv] query failed for scan {scan}: {e}", flush=True)
        continue
    nrow = tbs.nrows()
    if nrow == 0:
        tbs.close()
        continue
    # Read columns for this scan (should fit in memory: one scan ~ few thousand rows)
    T = tbs.getcol('TIME')  # seconds (MJD*86400)
    DD = tbs.getcol('DATA_DESC_ID')
    CORR = tbs.getcol('DATA')  # (npol, nchan, nrow), complex; APP MS DATA is calibrated
    FLAG = tbs.getcol('FLAG')
    tbs.close()

    # Unique integrations in this scan
    utimes = np.unique(T)
    for ut in utimes:
        m = (T == ut)
        # Per SPW
        iquv_spw = []
        for spw in range(nspw):
            mspw = m & (DD == spw)
            if not np.any(mspw):
                iquv_spw.append([np.nan]*4)
                continue
            d = CORR[:, :, mspw]  # (4, nchan, nsel)
            f = FLAG[:, :, mspw]
            # Average over baselines and channels, ignoring flagged
            # d shape: (pol, chan, row); pol order: XX, XY, YX, YY (for linear)
            xx = np.ma.masked_array(d[0].ravel(), mask=f[0].ravel()).mean()
            xy = np.ma.masked_array(d[1].ravel(), mask=f[1].ravel()).mean()
            yx = np.ma.masked_array(d[2].ravel(), mask=f[2].ravel()).mean()
            yy = np.ma.masked_array(d[3].ravel(), mask=f[3].ravel()).mean()
            I = (xx + yy) / 2.0
            Q = (xx - yy) / 2.0
            U = (xy + yx) / 2.0
            V = -1j * (xy - yx) / 2.0
            iquv_spw.append([float(I.real), float(Q.real), float(U.real), float(V.imag)])
        times_list.append(float(ut) / 86400.0)  # MJD
        I_list.append([x[0] for x in iquv_spw])
        Q_list.append([x[1] for x in iquv_spw])
        U_list.append([x[2] for x in iquv_spw])
        V_list.append([x[3] for x in iquv_spw])
        nint += 1
    if nint % 500 == 0:
        print(f"[iquv] {nint} integrations...", flush=True)

tb.close()

times = np.array(times_list)
I = np.array(I_list); Q = np.array(Q_list); U = np.array(U_list); V = np.array(V_list)
print(f"[iquv] done: {nint} integrations, {nspw} SPWs", flush=True)
print(f"[iquv] MJD range: {times.min():.6f} - {times.max():.6f}", flush=True)

np.savez_compressed(OUT, mjd=times, I=I, Q=Q, U=U, V=V,
                     spw_freq_GHz=spw_freq/1e9,
                     eb='uid___A002_Xbec3cb_X4947',
                     field='Sagittarius_A_star',
                     units='Jy (visibility-averaged, APP MS DATA column)')
print(f"[iquv] wrote {OUT}", flush=True)
