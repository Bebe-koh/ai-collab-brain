#!/usr/bin/env python3
"""Run calminispiral steps 3-4 only (unbuffered)"""
import os, sys, traceback

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data")
WORK = os.path.join(BASE, "sgra_work")
os.chdir(WORK)
os.environ["MPLBACKEND"] = "Agg"

print("[s34] importing...", flush=True)
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
# Only run steps 3 and 4
src = src.replace("mysteps = [0,1,2,3,4]", "mysteps = [3,4]")

print("[s34] executing steps 3-4...", flush=True)
try:
    exec(compile(src, "MINISPIRAL_CALIBRATION_DO_ALL_py3.py", "exec"), ns)
    print("[s34] SUCCESS", flush=True)
except Exception as e:
    print(f"[s34] FAILED: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
