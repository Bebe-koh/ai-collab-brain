#!/usr/bin/env python3
"""Chain test for one EB: QA2 restore -> SgrA* split -> calminispiral steps 0-4.

Usage: chain_test.py X4947
Expects restore_eb.py to have produced:
  restore/calibrated/uid___A002_Xbec3cb_X4947.polcalibrated.APP.ms
Produces:
  sgra_work/SGRA2017_X4947.ms                      (Sgr A* only, calibrated)
  sgra_work/SGRA_FIT_SGRA2017_X4947.fit            (per-spw fit arrays)
  sgra_work/Light_Curve_SPW{i}_SGRA2017_X4947.dat   (per-spw light curves)
"""
import os
import sys

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/"
                          "hidden_files/alma_data")
WORK = os.path.join(BASE, "sgra_work")
os.makedirs(WORK, exist_ok=True)

SFX = sys.argv[1]
ASDM = f"uid___A002_Xbec3cb_{SFX}"
RESTORED = os.path.join(BASE, "restore/calibrated", ASDM + ".polcalibrated.APP.ms")
MSNAME = os.path.join(WORK, f"SGRA2017_{SFX}.ms")

assert os.path.isdir(RESTORED), f"restored MS not found: {RESTORED}"

import casatasks
from casatasks import casalog
from casatools import table, image

os.environ["MPLBACKEND"] = "Agg"  # headless: pl.show() becomes a no-op

# 1. split out Sgr A* only (calminispiral has no field selection)
if not os.path.isdir(MSNAME):
    print(f"[chain] splitting Sgr A* from {ASDM} ...", flush=True)
    casatasks.split(vis=RESTORED, outputvis=MSNAME,
                    field="Sagittarius_A_star", datacolumn="data")
else:
    print("[chain] Sgr A* MS already exists, skipping split", flush=True)

# 2. run calminispiral steps 0-4
os.chdir(WORK)
ns = {
    "tb": table(),
    "ia": image(),
    "casalog": casalog,
    "os": os,
    "sys": sys,
}
for _t in ["clearcal", "tclean", "split", "gaincal", "applycal"]:
    ns[_t] = getattr(casatasks, _t)

script = os.path.join(BASE, "calminispiral",
                      "MINISPIRAL_CALIBRATION_DO_ALL_py3.py")
src = open(script).read()
# configure for this single track
src = src.replace('DATNAM = \'\'', 'DATNAM = \'SGRA2017\'')
src = src.replace('TRACKS = [\'\']', f'TRACKS = [\'{SFX}\']')
open("_run_config.py", "w").write(
    f"# auto-config\nDATNAM='SGRA2017'\nTRACKS=['{SFX}']\n")
print(f"[chain] running calminispiral steps 0-4 on SGRA2017_{SFX} ...",
      flush=True)
exec(compile(src, "MINISPIRAL_CALIBRATION_DO_ALL_py3.py", "exec"), ns)
print("[chain] done.", flush=True)
