"""Clock-file cross-check: do the NANOGrav clock corrections show jumps/gaps
at the 14 common epochs that could explain the ~350 ns common monopole?

Files (~/workspace/prtp/hidden_files/nanograv15yr/extracted/clock/):
  ao2gps.clk          UTC(AO)-UTC(GPS), seconds, daily
  gbt2gps.clk         UTC(GBT)-UTC(GPS), seconds, daily
  tai2tt_bipm2019.clk TAI->TT(BIPM2019), seconds, 10-day

Logic: corrections are APPLIED to TOAs, so residuals carry *errors* in
these files, not the corrections. Signatures of file error: jumps in the
series (maser drifts are ~ns/day smooth), gaps in coverage (interpolation
across missing days), flagged/bad sections, extrapolated regions.
A GBT-clock error hits J0437+J1909(+part B1937); AO-clock hits B1855(+part
B1937); TT(BIPM) error hits all four (true monopole).

Archival-data analysis; not a detection claim.
"""
import numpy as np
import json
import os

CLK = os.path.expanduser("~/workspace/prtp/hidden_files/nanograv15yr/extracted/clock")
HID = os.path.expanduser("~/workspace/prtp/hidden_files")

def load_clk(path):
    mjds, vals, notes = [], [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            try:
                mjds.append(float(parts[0])); vals.append(float(parts[1]))
                notes.append(" ".join(parts[2:]))
            except ValueError:
                notes.append("UNPARSEABLE: " + line)
    return np.array(mjds), np.array(vals) * 1e9, notes  # ns

files = {}
for name in ["ao2gps.clk", "gbt2gps.clk", "tai2tt_bipm2019.clk"]:
    m, v, n = load_clk(os.path.join(CLK, name))
    files[name] = (m, v, n)
    print(f"{name}: {len(m)} pts, MJD {m[0]:.1f}-{m[-1]:.1f}, "
          f"range [{v.min():.1f}, {v.max():.1f}] ns")

epochs = np.array([57212., 57242., 57272., 57782., 57812., 57842., 57902.,
                   58622., 58652., 58742., 58772., 58802., 58892., 58952.])
common = np.array([274.8, 334.1, 352.4, -138.4, -159.7, -227.6, -201.9,
                   -97.3, 69.1, 49.9, -82.6, -28.0, -33.5, 40.0])  # ns

out = {"epochs": epochs.tolist(), "common_mode_ns": common.tolist(),
       "files": {}}

for name, (m, v, n) in files.items():
    lo, hi = 57050, 59100
    sel = (m >= lo) & (m <= hi)
    me, ve = m[sel], v[sel]
    # gaps
    dm = np.diff(me)
    gaps = [(float(me[i]), float(me[i + 1]), float(dm[i]))
            for i in np.where(dm > 3.0)[0]]
    # jumps: day-to-day (or sample-to-sample) differences
    dv = np.diff(ve)
    med = float(np.median(np.abs(dv)))
    jumps = [(float(me[i + 1]), float(dv[i])) for i in
             np.where(np.abs(dv) > max(50.0, 10 * med))[0]]
    # value at each epoch (nearest sample) + local slope
    at_ep = []
    for e in epochs:
        j = int(np.argmin(np.abs(me - e)))
        at_ep.append({"mjd": e, "nearest_mjd": float(me[j]),
                      "corr_ns": float(ve[j]),
                      "dt_days": float(e - me[j])})
    # flagged notes
    flagged = [nn for nn in n if nn and not nn.startswith("post")]
    out["files"][name] = {
        "n_pts_window": int(sel.sum()),
        "median_abs_step_ns": med,
        "gaps_gt3d": gaps[:20],
        "jumps_gt_thresh_ns": jumps[:20],
        "at_epochs": at_ep,
        "n_flagged_notes": len(flagged),
        "flagged_sample": flagged[:5],
    }
    print(f"\n{name}: median|step|={med:.2f} ns, gaps>3d: {len(gaps)}, "
          f"jumps: {len(jumps)}")
    for g in gaps[:10]:
        print(f"   gap {g[0]:.1f} -> {g[1]:.1f} ({g[2]:.0f} d)")
    for j in jumps[:10]:
        print(f"   jump at MJD {j[0]:.1f}: {j[1]:+.1f} ns")

# --- targeted: does any clock file jump where the common mode jumps?
# common-mode epoch-to-epoch changes (ns)
dcm = np.diff(common)
print("\ncommon-mode epoch steps (ns):", np.round(dcm, 0))
big = np.where(np.abs(dcm) > 150)[0]
print("big steps at epoch transitions:", [(int(i), int(i + 1)) for i in big])

with open(os.path.join(HID, "clock_crosscheck_results.json"), "w") as f:
    json.dump(out, f, indent=1)
print("\nwrote clock_crosscheck_results.json")
