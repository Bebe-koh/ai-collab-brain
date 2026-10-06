#!/usr/bin/env python3
"""Restore one ALMA QA2 VLBI execution block with CASA 6 (pip) + converted QA2 script.

Replicates ALMA's scriptForPI.py flow for a single ASDM:
  restore/
    raw/          extracted uid___.asdm.sdm  (+ the .tar kept alongside)
    script/       converted py3 scriptForCalibration for this ASDM
    calibration/  TRACK_C.calibration.tgz (from the QA2 auxiliary package)
    calibrated/   <asdm>.calibration/ workdir ; final products land here:
                    <asdm>.ms.split.cal  and  <asdm>.polcalibrated.APP.ms

Usage:  restore_eb.py X4947
(the full ASDM id is uid___A002_Xbec3cb_X4947)
"""
import glob
import os
import shutil
import subprocess
import sys

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/"
                          "hidden_files/alma_data")
QA2_SCRIPT_DIR = os.path.join(BASE, "qa2_aux/2016.1.01404.V/science_goal.uid___A001_X11b3_X2f/"
                              "group.uid___A001_X11b3_X30/member.uid___A001_X11b3_X35/script")
CAL_TGZ = os.path.join(BASE, "qa2_aux/2016.1.01404.V/science_goal.uid___A001_X11b3_X2f/"
                       "group.uid___A001_X11b3_X30/member.uid___A001_X11b3_X35/"
                       "calibration/TRACK_C.calibration.tgz")

ASDM_TEMPLATE = "uid___A002_Xbec3cb_{sfx}"


def log(msg):
    print(f"[restore] {msg}", flush=True)


def run_one(sfx):
    asdm = ASDM_TEMPLATE.format(sfx=sfx)
    rdir = os.path.join(BASE, "restore")
    rawdir = os.path.join(rdir, "raw")
    scriptdir = os.path.join(rdir, "script")
    caldir = os.path.join(rdir, "calibration")
    calddir = os.path.join(rdir, "calibrated")
    for d in (rawdir, scriptdir, caldir, calddir):
        os.makedirs(d, exist_ok=True)

    # 1. raw ASDM: extract the tar if the .asdm.sdm dir is not there yet
    tar = os.path.join(BASE, "raw",
                       f"2016.1.01404.V_{asdm}.asdm.sdm.tar")
    asdm_dir = os.path.join(rawdir, asdm + ".asdm.sdm")
    if not os.path.isdir(asdm_dir):
        if not os.path.isfile(tar):
            raise SystemExit(f"raw tar not found: {tar}")
        log(f"extracting {tar} ...")
        subprocess.run(["tar", "-xf", tar, "-C", rawdir, "--no-same-owner"],
                       check=True)
    if not os.path.isdir(asdm_dir):
        # ESO tars nest the ASDM deep (2016.1.01404.V/science_goal.../member.../raw/uid___.asdm.sdm);
        # find it and move it up to rawdir
        want = asdm + ".asdm.sdm"
        found = None
        for root, dirs, _ in os.walk(rawdir):
            if want in dirs:
                found = os.path.join(root, want)
                break
        if found:
            log(f"moving nested ASDM {found} -> {asdm_dir}")
            shutil.move(found, asdm_dir)
            # clean the now-empty deep tree
            top = os.path.join(rawdir, "2016.1.01404.V")
            if os.path.isdir(top):
                shutil.rmtree(top, ignore_errors=True)
    if not os.path.isdir(asdm_dir):
        raise SystemExit(f"extraction did not produce {asdm_dir}")
    log(f"raw ASDM ready: {asdm_dir}")

    # 2. converted script
    conv = os.path.join(BASE, "script_py3", asdm + ".ms.scriptForCalibration_py3.py")
    if not os.path.isfile(conv):
        raise SystemExit(f"converted script not found: {conv}")
    shutil.copy(conv, os.path.join(scriptdir, os.path.basename(conv)))

    # 3. calibration tgz
    dest_tgz = os.path.join(caldir, "TRACK_C.calibration.tgz")
    if not os.path.isfile(dest_tgz):
        shutil.copy(CAL_TGZ, dest_tgz)

    # 4. per-EB working dir (mimics scriptForPI.py)
    workdir = os.path.join(calddir, asdm + ".calibration")
    if os.path.isdir(workdir):
        log(f"removing previous workdir {workdir}")
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    os.chdir(workdir)
    os.symlink(os.path.join("../../raw", asdm + ".asdm.sdm"), asdm)
    log("extracting calibration tables ...")
    subprocess.run("tar -xzf ../../calibration/*.tgz --no-same-owner",
                   shell=True, check=True)

    # 5. run the converted QA2 script with CASA 6 tasks in the namespace
    log("importing casatasks (CASA 6) ...")
    import casatasks
    from casatasks import casalog
    ns = {
        "importasdm": casatasks.importasdm,
        "listobs": casatasks.listobs,
        "flagdata": casatasks.flagdata,
        "flagcmd": casatasks.flagcmd,
        "flagmanager": casatasks.flagmanager,
        "split": casatasks.split,
        "applycal": casatasks.applycal,
        "casalog": casalog,
        "os": os,
        "sys": sys,
        "glob": glob,
    }
    log(f"executing {os.path.basename(conv)} (all 12 QA2 steps) ...")
    with open(os.path.join(scriptdir, os.path.basename(conv))) as f:
        code = f.read()
    exec(compile(code, os.path.basename(conv), "exec"), ns)

    # 6. collect products (mimics scriptForPI.py)
    os.chdir(calddir)
    for prod in (asdm + ".ms.split.cal", asdm + ".polcalibrated.APP.ms"):
        p = os.path.join(workdir, prod)
        if os.path.isdir(p):
            dest = os.path.join(calddir, prod)
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            shutil.move(p, dest)
            log(f"product ready: {dest}")
        else:
            log(f"WARNING: expected product missing: {p}")
    log("done.")


if __name__ == "__main__":
    run_one(sys.argv[1])
