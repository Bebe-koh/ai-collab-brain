#!/usr/bin/env python3
"""Memory-efficient per-integration Stokes IQUV extraction from an APP MS.

Usage: extract_iquv.py X448f
Reads the APP MS DATA column (polarization-calibrated) in per-scan chunks,
averages XX/XY/YX/YY over baselines+channels per integration, computes:
  I=(XX+YY)/2, Q=(XX-YY)/2, U=(XY+YX)/2, V=-i(XY-YX)/2
Writes sgra_work/SGRA2017_<SFX>_IQUV.npz

Caveat: visibility-averaged flux (includes minispiral extended emission),
not the minispiral-model-subtracted point-source fit.
"""
import os, sys
import numpy as np

SFX = sys.argv[1]
ASDM = f"uid___A002_Xbec3cb_{SFX}"
BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data")
MS = os.path.join(BASE, "restore/calibrated", ASDM + ".polcalibrated.APP.ms")
OUT = os.path.join(BASE, f"sgra_work/SGRA2017_{SFX}_IQUV.npz")

assert os.path.isdir(MS), f"APP MS not found: {MS}"

print(f"[iquv] EB {SFX}: opening MS...", flush=True)
from casatools import table, ms as mstool

tb = table()
tb.open(os.path.join(MS, 'SPECTRAL_WINDOW'))
chan_freq = tb.getcol('CHAN_FREQ')
tb.close()
nspw = chan_freq.shape[1]
spw_freq = np.mean(chan_freq, axis=0)
print(f"[iquv] {nspw} SPWs, freqs GHz: {spw_freq/1e9}", flush=True)

tb.open(os.path.join(MS, 'FIELD'))
names = list(tb.getcol('NAME'))
sgra_fid = names.index('Sagittarius_A_star')
tb.close()

ms = mstool()
ms.open(MS)
scansum = ms.getscansummary()
ms.close()
sgra_scans = [int(s) for s, info in scansum.items() if info['0']['FieldId'] == sgra_fid]
print(f"[iquv] {len(sgra_scans)} Sgr A* scans", flush=True)

tb.open(MS)
times_list, I_list, Q_list, U_list, V_list = [], [], [], [], []
nint = 0
for scan in sorted(sgra_scans):
    try:
        tbs = tb.query(f"SCAN_NUMBER=={scan} && FIELD_ID=={sgra_fid}")
    except Exception as e:
        print(f"[iquv] query failed for scan {scan}: {e}", flush=True)
        continue
    nrow = tbs.nrows()
    if nrow == 0:
        tbs.close()
        continue
    T = tbs.getcol('TIME')
    DD = tbs.getcol('DATA_DESC_ID')
    DAT = tbs.getcol('DATA')
    FLAG = tbs.getcol('FLAG')
    tbs.close()
    for ut in np.unique(T):
        m = (T == ut)
        iquv_spw = []
        for spw in range(nspw):
            mspw = m & (DD == spw)
            if not np.any(mspw):
                iquv_spw.append([np.nan]*4)
                continue
            d = DAT[:, :, mspw]
            f = FLAG[:, :, mspw]
            xx = np.ma.masked_array(d[0].ravel(), mask=f[0].ravel()).mean()
            xy = np.ma.masked_array(d[1].ravel(), mask=f[1].ravel()).mean()
            yx = np.ma.masked_array(d[2].ravel(), mask=f[2].ravel()).mean()
            yy = np.ma.masked_array(d[3].ravel(), mask=f[3].ravel()).mean()
            I = (xx + yy) / 2.0
            Q = (xx - yy) / 2.0
            U = (xy + yx) / 2.0
            V = -1j * (xy - yx) / 2.0
            iquv_spw.append([float(I.real), float(Q.real), float(U.real), float(V.imag)])
        times_list.append(float(ut) / 86400.0)
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
                     spw_freq_GHz=spw_freq/1e9, eb=ASDM,
                     field='Sagittarius_A_star',
                     units='Jy (visibility-averaged, APP MS DATA column)')
print(f"[iquv] wrote {OUT}", flush=True)
