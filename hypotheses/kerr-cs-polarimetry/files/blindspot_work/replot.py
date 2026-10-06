"""Regenerate corrected figures from synth_results.json (no re-simulation)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open("synth_results.json", "r"))
resA, resB, resC, resC2 = d["expA"], d["expB"], d["expC"], d["expC2"]
resD = d["expD"]
resE, resE2, resE3 = d["expE"], d["expE2"], d["expE3"]

# ---- Fig A: detection vs gamma -------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
g = [r["gamma"] for r in resA]
ax.plot(g, [r["new_det1"] for r in resA], "o-", label="new: R(t) matched filter")
ax.plot(g, [r["old_det1"] for r in resA], "s--", label="old: asymptotic step (oracle t0)")
ax.plot(g, [r["oldfree_det1"] for r in resA], "^:", label="old: free-t0 step search", alpha=0.7)
for kk in [1, 2, 3, 4]:
    ax.axvline(kk/12, color="k", ls=":", alpha=0.4)
ax.set_xlabel("injected γ"); ax.set_ylabel("detection fraction @ FPR=1%")
ax.set_title("A: detection vs γ — old blind at k/12, new is not")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
ax.plot(g, [r["new_margin"] for r in resA], "o-", label="new")
ax.plot(g, [r["old_margin"] for r in resA], "s--", label="old (oracle)")
for kk in [1, 2, 3, 4]:
    ax.axvline(kk/12, color="k", ls=":", alpha=0.4)
ax.set_xlabel("injected γ"); ax.set_ylabel("median Z / null 99th pct")
ax.set_title("A: detection margin vs γ")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("synth_figA.png", dpi=110)

# ---- Fig BC: jump confounder + sample-phase lottery ------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
dd = [r["delta"] for r in resB]
ax.plot(dd, [r["old_det1"] for r in resB], "s--", label="old (false alarm)")
ax.plot(dd, [r["new_det1"] for r in resB], "o-", label="new (silent)")
ax.set_xlabel("jump amplitude δ (rad)"); ax.set_ylabel("detection fraction @ FPR=1%")
ax.set_title("B: jump-only injection — old fires, new silent")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
off = [r["offset"] for r in resC2]
ax.bar([str(o) for o in off], [r["new_det1"] for r in resC2], color="steelblue")
ax.axhline(1.0, color="k", ls=":", alpha=0.3)
ax.set_xlabel("sample-grid offset (s) at Δt=200 s ≫ τ")
ax.set_ylabel("new-stat detection fraction @ FPR=1%, γ=1/12")
ax.set_title("C2: unresolved ramp — detection is a sample-phase lottery")
ax.set_ylim(0, 1.1)
fig.tight_layout(); fig.savefig("synth_figBC.png", dpi=110)

# ---- Fig D: calibrator interpolation residuals ------------------------------
fig, ax = plt.subplots(figsize=(8, 4.2))
cads = sorted(set(r["cal_cad"] for r in resD))
x = np.arange(len(cads)); w = 0.35
mid = [next(r for r in resD if r["cal_cad"] == c and r["tag"] == "mid-gap") for c in cads]
ins = [next(r for r in resD if r["cal_cad"] == c and r["tag"] == "in-scan") for c in cads]
ax.bar(x - w/2, [r["spurious_det1"] for r in mid], w, label="jump mid-gap")
ax.bar(x + w/2, [r["spurious_det1"] for r in ins], w, label="jump in-scan")
for i, c in enumerate(cads):
    ax.text(i - w/2, mid[i]["spurious_det1"] + 0.03, f'×{mid[i]["suppression"]:.0f}',
            ha="center", fontsize=8)
    ax.text(i + w/2, ins[i]["spurious_det1"] + 0.03, f'×{ins[i]["suppression"]:.0f}',
            ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([f"{c:.0f} s" for c in cads])
ax.set_xlabel("calibrator cadence"); ax.set_ylabel("spurious new-stat det. fraction @ FPR=1%")
ax.set_title("D: mid-gap jumps at realistic cadence are NOT cancelled (suppression ×N labelled)")
ax.legend(fontsize=8); ax.set_ylim(0, 1.25)
fig.tight_layout(); fig.savefig("synth_figD.png", dpi=110)

# ---- Fig E: alias / estimation ----------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
ss = [r["sig"] for r in resE]
ax.semilogx(ss, [r["frac_true"] for r in resE], "o-", label="LS picks γ=1/12 (true)")
ax.semilogx(ss, [r["frac_plus"] for r in resE], "s--", label="LS picks γ=1/6 (alias)")
ax.semilogx(ss, [r["frac_other"] for r in resE], "^-.", label="other")
ax.set_xlabel("per-sample fractional noise σ"); ax.set_ylabel("fraction of realizations")
ax.set_title("E: no alias-locking — amplitude-aware LS picks true γ")
ax.legend(fontsize=8); ax.set_ylim(-0.05, 1.05)
ax = axes[1]
ss2 = [r["sig"] for r in resE2]
ax.errorbar(ss2, [r["gamma_hat_mean"] for r in resE2],
            yerr=[r["gamma_hat_std"] for r in resE2], fmt="o-", capsize=3,
            label="cumsum unwrapping γ̂")
ax.axhline(1/12, color="k", ls=":", alpha=0.5, label="true γ=1/12")
ax.set_xscale("log")
ax.set_xlabel("per-sample fractional noise σ"); ax.set_ylabel("γ̂")
ax.set_title("E2: unwrapping recovers γ incl. the 2π winding")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("synth_figE.png", dpi=110)
print("figures rewritten")
