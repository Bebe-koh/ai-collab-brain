#!/usr/bin/env python3
"""Convert ALMA QA2 VLBI scriptForCalibration.py (CASA 5.1.1 / Python 2) to Python 3.

Faithful port: the ONLY changes are
  1. `print X`      -> `print(X)`
  2. `import casadef` + the CASA-version gate -> removed (we run CASA 6 via pip;
     the gate would NameError on the undefined CASAVER anyway)
  3. `from recipes.almahelpers import fixsyscaltimes` -> documented no-op.
     fixsyscaltimes only corrects SYSCAL-subtable timestamps used by Tsys
     calibration; these QA2 scripts apply NO Tsys calibration (verified: no
     'tsys' string in any of the 8 scripts), so skipping it is a no-op for the
     products. Logged loudly at run time.
  4. `T = True / F = False` are already defined in the scripts; kept as-is.

All CASA task calls, scan/antenna/spw selections, cal-table names and order of
operations are byte-identical to the archive QA2 scripts.
"""
import re
import sys

REMOVE_BLOCK_START = "# CHECK CASA VERSION"


def convert(text: str) -> str:
    out = []
    skip_version_block = False
    for line in text.splitlines():
        # 1. drop `import casadef`
        if re.match(r"^\s*import casadef\s*$", line):
            out.append("# [py3-port] removed: import casadef (CASA5-only module)")
            continue
        # 2. drop the version-gate block
        if REMOVE_BLOCK_START in line:
            skip_version_block = True
            out.append("# [py3-port] removed CASA 5.1.1 version gate (running CASA 6)")
            continue
        if skip_version_block:
            if "sys.exit" in line:
                skip_version_block = False
            continue
        # 3. replace fixsyscaltimes import with documented no-op (keep indent)
        m2 = re.match(r"^(\s*)from recipes\.almahelpers import fixsyscaltimes\s*$", line)
        if m2:
            ind = m2.group(1)
            out.append(f"{ind}def fixsyscaltimes(vis):")
            out.append(f"{ind}    print('[py3-port] fixsyscaltimes SKIPPED (no Tsys cal in "
                       "this script; SYSCAL times unused)')")
            continue
        # 4. print statement -> print()
        m = re.match(r"^(\s*)print(\s+)(.+)$", line)
        if m and "print(" not in line:
            out.append(f"{m.group(1)}print({m.group(3)})")
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as f:
        text = f.read()
    new = convert(text)
    # sanity: no py2 print statements remain
    for i, line in enumerate(new.splitlines(), 1):
        if re.match(r"^\s*print\s+[^(]", line):
            raise SystemExit(f"unconverted print at line {i}: {line}")
    if re.search(r"^\s*import casadef", new, re.M) or "from recipes.almahelpers import" in new:
        raise SystemExit("conversion incomplete")
    with open(dst, "w") as f:
        f.write(new)
    print(f"converted {src} -> {dst}")


if __name__ == "__main__":
    main()
