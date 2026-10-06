#!/bin/bash
# Sequential per-EB pipeline: download -> verify -> restore -> extract IQUV ->
# verify npz -> delete raw+MSs -> next EB. STOPS on first failure.
# Usage: run_remaining_ebs.sh   (run from alma_data/)
set -euo pipefail

BASE="$HOME/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data"
VENV="$HOME/workspace/alma_venv/bin/python"
LOG="$BASE/REDUCTION_LOG.md"
PORTAL="https://almascience.eso.org/dataPortal"

# SFX:expected_bytes
EBS="X3d77:17565952000 X3fe6:13223675904 X468b:15457030144 X4bca:11977251840 X4de4:13163095040"

cd "$BASE"

for pair in $EBS; do
  SFX="${pair%%:*}"
  EXPECT="${pair##*:}"
  ASDM="uid___A002_Xbec3cb_${SFX}"
  TAR="raw/2016.1.01404.V_${ASDM}.asdm.sdm.tar"
  URL="${PORTAL}/2016.1.01404.V_${ASDM}.asdm.sdm.tar"
  MS="restore/calibrated/${ASDM}.polcalibrated.APP.ms"
  NPZ="sgra_work/SGRA2017_${SFX}_IQUV.npz"

  echo "================================================================"
  echo "[pipeline] EB ${SFX} starting $(date -u)"
  df -h /home/hatch | tail -1

  # 1. download (single stream, no resume)
  if [ ! -f "$TAR" ]; then
    echo "[pipeline] downloading ${URL}"
    curl -sS --fail -o "$TAR" "$URL" 2> "raw/dl_${SFX}.log" || {
      echo "[pipeline] DOWNLOAD FAILED for ${SFX}"; tail -5 "raw/dl_${SFX}.log"; exit 1; }
  fi
  SIZE=$(stat -c%s "$TAR")
  if [ "$SIZE" != "$EXPECT" ]; then
    echo "[pipeline] SIZE MISMATCH for ${SFX}: got $SIZE, want $EXPECT"
    exit 1
  fi
  echo "[pipeline] size OK: $SIZE bytes"

  # 2. tar integrity
  echo "[pipeline] tar -tf verify ${SFX} ..."
  if ! tar -tf "$TAR" > /dev/null 2> "raw/tartest_${SFX}.log"; then
    echo "[pipeline] TAR CORRUPT for ${SFX}; deleting and aborting"
    tail -3 "raw/tartest_${SFX}.log"
    rm -f "$TAR"
    exit 1
  fi
  echo "[pipeline] tar integrity OK"

  # 3. restore (all 12 QA2 steps)
  echo "[pipeline] restore_eb.py ${SFX} ..."
  "$VENV" restore_eb.py "$SFX" > "restore_${SFX}.log" 2>&1 || {
    echo "[pipeline] RESTORE FAILED for ${SFX}; see restore_${SFX}.log"; exit 1; }
  [ -d "$MS" ] || { echo "[pipeline] expected MS missing: $MS"; exit 1; }
  echo "[pipeline] restore OK: $MS"

  # 4. extract IQUV
  echo "[pipeline] extract_iquv.py ${SFX} ..."
  "$VENV" extract_iquv.py "$SFX" > "iquv_${SFX}.log" 2>&1 || {
    echo "[pipeline] EXTRACT FAILED for ${SFX}; see iquv_${SFX}.log"; exit 1; }

  # 5. verify npz
  echo "[pipeline] verifying $NPZ ..."
  "$VENV" - "$NPZ" <<'EOF' || { echo "[pipeline] NPZ VERIFY FAILED"; exit 1; }
import sys, numpy as np
d = np.load(sys.argv[1])
mjd, I, Q, U, V = d['mjd'], d['I'], d['Q'], d['U'], d['V']
n = len(mjd)
nanfrac = float(np.isnan(I).mean())
print(f"  n_int={n} spw={I.shape[1]} mjd={mjd.min():.6f}-{mjd.max():.6f} "
      f"meanI_Jy={np.nanmean(I):.3f} nanfrac={nanfrac:.4f}")
assert n > 100, "too few integrations"
assert nanfrac < 0.05, "too many NaNs"
assert 2.0 < np.nanmean(I) < 2.5, "mean I outside expected Sgr A* range"
print("  NPZ OK")
EOF

  # 6. cleanup raw + MSs for this EB
  echo "[pipeline] cleaning raw+MS for ${SFX} ..."
  rm -f "$TAR"
  rm -rf "restore/raw/${ASDM}.asdm.sdm"
  rm -rf "restore/calibrated/${ASDM}.calibration"
  rm -rf "restore/calibrated/${ASDM}.ms.split.cal"
  rm -rf "$MS"
  df -h /home/hatch | tail -1

  # 7. log
  MJD_LINE=$(grep -E "MJD range" "iquv_${SFX}.log" | tail -1 || true)
  cat >> "$LOG" <<EOF

### ${SFX} (uid://A002/Xbec3cb/${SFX}) — COMPLETE
- Downloaded ${EXPECT} bytes (ESO dataPortal, single stream, size-verified), tar integrity OK.
- \`restore_eb.py ${SFX}\`: importasdm + 12 QA2 steps -> polcalibrated APP MS (see restore_${SFX}.log).
- \`extract_iquv.py ${SFX}\` -> \`sgra_work/SGRA2017_${SFX}_IQUV.npz\` (${MJD_LINE}).
- Post-product cleanup: raw tar + all ${SFX} MSs deleted.
EOF
  echo "[pipeline] EB ${SFX} DONE $(date -u)"
done

echo "[pipeline] ALL EBS COMPLETE $(date -u)"
