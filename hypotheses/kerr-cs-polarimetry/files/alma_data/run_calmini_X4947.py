#!/usr/bin/env python3
"""Run calminispiral steps 0-4 on SGRA2017_X4947.ms"""
import os, sys, traceback

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data")
WORK = os.path.join(BASE, "sgra_work")
os.chdir(WORK)
os.environ["MPLBACKEND"] = "Agg"

print("[calmini] importing casatasks...", flush=True)
import casatasks
from casatasks import casalog
from casatools import table, image

ns = {
    "tb": table(),
    "ia": image(),
    "casalog": casalog,
    "os": os,
    "sys": sys,
}
for _t in ["clearcal", "tclean", "split", "gaincal", "applycal"]:
    ns[_t] = getattr(casatasks, _t)

script = os.path.join(BASE, "calminispiral", "MINISPIRAL_CALIBRATION_DO_ALL_py3.py")
src = open(script).read()
src = src.replace("DATNAM = ''", "DATNAM = 'SGRA2017'")
src = src.replace("TRACKS = ['']", "TRACKS = ['X4947']")

print("[calmini] executing calminispiral steps 0-4...", flush=True)
try:
    exec(compile(src, "MINISPIRAL_CALIBRATION_DO_ALL_py3.py", "exec"), ns)
    print("[calmini] SUCCESS", flush=True)
except Exception as e:
    print(f"[calmini] FAILED: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
