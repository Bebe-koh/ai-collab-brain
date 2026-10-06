#!/usr/bin/env python3
"""Apply the CASA 5->6 Step-6 applycal try/except patch to all 8 converted QA2 scripts."""
import os, re, glob, py_compile

BASE = os.path.expanduser("~/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data/script_py3")

for path in sorted(glob.glob(os.path.join(BASE, "uid___A002_Xbec3cb_*.ms.scriptForCalibration_py3.py"))):
    name = os.path.basename(path)
    with open(path) as f:
        lines = f.readlines()
    if any("WARNING: applycal failed for" in l for l in lines):
        print(f"SKIP (already patched): {name}")
        continue

    # Find the print line for APP applycal
    idx = None
    for i, l in enumerate(lines):
        if "print('Applying calibration to %s (APP Obs.)'%field)" in l:
            idx = i
            break
    if idx is None:
        print(f"WARN: print pattern not found in {name}")
        continue
    # Next non-empty line should be the applycal( call
    j = idx + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if "applycal(vis" not in lines[j]:
        print(f"WARN: applycal not after print in {name} (line {j}: {lines[j][:60]})")
        continue

    # Replace: insert '    try:\n' before applycal, indent applycal block by 4, add except after closing
    new_lines = lines[:j]
    new_lines.append("    try:\n")
    k = j
    closed = False
    while k < len(lines):
        l = lines[k]
        if re.match(r"^      flagbackup = F\)\s*$", l):
            new_lines.append("    " + l)  # indented closing
            new_lines.append("    except RuntimeError as e:\n")
            new_lines.append("        print('WARNING: applycal failed for %s (harmless per QA2 script note): %s' % (field, e))\n")
            closed = True
            k += 1
            break
        # indent every line of the applycal call by 4 spaces (skip pure blanks)
        if l.strip() == "":
            new_lines.append(l)
        else:
            new_lines.append("    " + l)
        k += 1
    if not closed:
        print(f"WARN: applycal block end not found in {name}")
        continue
    new_lines.extend(lines[k:])
    with open(path, "w") as f:
        f.writelines(new_lines)
    try:
        py_compile.compile(path, doraise=True)
        print(f"PATCHED: {name}")
    except Exception as e:
        print(f"SYNTAX FAIL {name}: {e}")
