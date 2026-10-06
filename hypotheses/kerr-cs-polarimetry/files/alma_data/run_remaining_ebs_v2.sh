#!/bin/bash
# Sequential per-EB pipeline v2: download -> verify -> restore -> extract IQUV ->
# verify npz -> delete raw+MSs -> next EB.
# Order per task: X3fe6 first (fresh re-download, resume forbidden), then
# X3d77, X468b, X4bca, X4de4.
# Failure policy: retry each stage ONCE; on second failure log precisely and
# move to the next EB (never loop forever).
# Usage: run_remaining_ebs_v2.sh   (run from alma_data/)
set -uo pipefail

BASE="$HOME/workspace/goals/kerr-cs-polarimetry-exploration/hidden_files/alma_data"
VENV="$HOME/workspace/alma_venv/bin/python"
LOG="$BASE/REDUCTION_LOG.md"
PORTAL="https://almascience.eso.org/dataPortal"
FAILLOG="$BASE/EB_FAILURES.md"

# SFX:expected_bytes  (task order)
EBS="X3fe6:13223675904 X3d77:17565952000 X468b:15457030144 X4bca:11977251840 X4de4:13163095040"

cd "$BASE"

record_failure() {
  # $1=SFX $2=stage $3=detail
  echo "[pipeline] FAILURE: EB $1 stage '$2' failed twice. $3" | tee -a "$FAILLOG"
  cat >> "$LOG" <<EOF

### $1 (uid://A002/Xbec3cb/$1) — FAILED at stage '$2' (2 attempts)
- $3
- Moved on to next EB per failure policy.
EOF
}

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

  # ---- stage 1: download (fresh single stream, NO resume) ----
  rm -f "$TAR"   # never resume; integrity lesson 2026-10-06
  ok=0
  for attempt in 1 2; do
    echo "[pipeline] downloading ${SFX} (attempt $attempt) ..."
    rm -f "$TAR"
    if curl -sS --fail -o "$TAR" "$URL" 2> "raw/dl_${SFX}.log"; then
      SIZE=$(stat -c%s "$TAR")
      if [ "$SIZE" = "$EXPECT" ]; then ok=1; break; fi
      echo "[pipeline] size mismatch attempt $attempt: got $SIZE want $EXPECT"
    else
      echo "[pipeline] curl failed attempt $attempt:"; tail -3 "raw/dl_${SFX}.log"
    fi
    sleep 30
  done
  if [ "$ok" != "1" ]; then
    record_failure "$SFX" "download" "size/curl failure after 2 attempts (see raw/dl_${SFX}.log)"
    continue
  fi
  echo "[pipeline] download OK: $(stat -c%s "$TAR") bytes"

  # ---- stage 2: tar integrity ----
  ok=0
  for attempt in 1 2; do
    if tar -tf "$TAR" > /dev/null 2> "raw/tartest_${SFX}.log"; then ok=1; break; fi
    echo "[pipeline] tar corrupt attempt $attempt; re-downloading fresh"
    tail -3 "raw/tartest_${SFX}.log"
    rm -f "$TAR"
    curl -sS --fail -o "$TAR" "$URL" 2>> "raw/dl_${SFX}.log" || true
    SIZE=$(stat -c%s "$TAR" 2>/dev/null || echo 0)
    [ "$SIZE" = "$EXPECT" ] || echo "[pipeline] re-download size mismatch: $SIZE"
  done
  if [ "$ok" != "1" ]; then
    record_failure "$SFX" "tar-integrity" "tar -tf failed after fresh re-download (see raw/tartest_${SFX}.log)"
    rm -f "$TAR"
    continue
  fi
  echo "[pipeline] tar integrity OK"

  # ---- stage 3: restore ----
  ok=0
  for attempt in 1 2; do
    echo "[pipeline] restore_eb.py ${SFX} (attempt $attempt) ..."
    if "$VENV" restore_eb.py "$SFX" > "restore_${SFX}.log" 2>&1 && [ -d "$MS" ]; then
      ok=1; break
    fi
    echo "[pipeline] restore failed attempt $attempt; see restore_${SFX}.log"
    sleep 30
  done
  if [ "$ok" != "1" ]; then
    record_failure "$SFX" "restore" "restore_eb.py failed twice (see restore_${SFX}.log)"
    rm -f "$TAR"
    continue
  fi
  echo "[pipeline] restore OK: $MS"

  # ---- stage 4: extract IQUV ----
  ok=0
  for attempt in 1 2; do
    echo "[pipeline] extract_iquv.py ${SFX} (attempt $attempt) ..."
    if "$VENV" extract_iquv.py "$SFX" > "iquv_${SFX}.log" 2>&1; then ok=1; break; fi
    echo "[pipeline] extract failed attempt $attempt; see iquv_${SFX}.log"
    sleep 30
  done
  if [ "$ok" != "1" ]; then
    record_failure "$SFX" "extract" "extract_iquv.py failed twice (see iquv_${SFX}.log)"
    rm -f "$TAR"
    rm -rf "restore/raw/${ASDM}.asdm.sdm" "restore/calibrated/${ASDM}.calibration" \
           "restore/calibrated/${ASDM}.ms.split.cal" "$MS"
    continue
  fi

  # ---- stage 5: verify npz ----
  echo "[pipeline] verifying $NPZ ..."
  if ! "$VENV" - "$NPZ" <<'EOF' 2>&1 | tee -a "iquv_${SFX}.log"; then
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
    record_failure "$SFX" "npz-verify" "product failed sanity checks (see iquv_${SFX}.log)"
    rm -f "$TAR"
    rm -rf "restore/raw/${ASDM}.asdm.sdm" "restore/calibrated/${ASDM}.calibration" \
           "restore/calibrated/${ASDM}.ms.split.cal" "$MS"
    continue
  fi

  # ---- stage 6: cleanup raw + MSs for this EB ----
  echo "[pipeline] cleaning raw+MS for ${SFX} ..."
  rm -f "$TAR"
  rm -rf "restore/raw/${ASDM}.asdm.sdm"
  rm -rf "restore/calibrated/${ASDM}.calibration"
  rm -rf "restore/calibrated/${ASDM}.ms.split.cal"
  rm -rf "$MS"
  df -h /home/hatch | tail -1

  # ---- stage 7: log + status table checkpoint (immediately, before next EB) ----
  sed -i "/uid:\/\/A002\/Xbec3cb\/${SFX} /s/|[^|]*| *$/| **DONE — IQUV extracted, raw+MS deleted** |/" "$LOG"
  MJD_LINE=$(grep -E "MJD range" "iquv_${SFX}.log" | tail -1 || true)
  cat >> "$LOG" <<EOF

### ${SFX} (uid://A002/Xbec3cb/${SFX}) — COMPLETE
- Downloaded ${EXPECT} bytes (ESO dataPortal, fresh single stream, size-verified), tar integrity OK.
- \`restore_eb.py ${SFX}\`: importasdm + 12 QA2 steps -> polcalibrated APP MS (see restore_${SFX}.log).
- \`extract_iquv.py ${SFX}\` -> \`sgra_work/SGRA2017_${SFX}_IQUV.npz\` (${MJD_LINE}).
- Post-product cleanup: raw tar + all ${SFX} MSs deleted.
EOF
  echo "[pipeline] EB ${SFX} DONE $(date -u)"
done

echo "[pipeline] ALL EBS COMPLETE $(date -u)"
df -h /home/hatch | tail -1
