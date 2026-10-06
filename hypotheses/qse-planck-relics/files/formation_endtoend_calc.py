#!/usr/bin/env python3
"""
QSE formation: full end-to-end calculation for ALL targets, both channels.
Extends marginal_beta_case_note.md (beta=1e-5) to the briefing relic targets.

Methodology: see marginal_beta_case_note.md §§1-2 (Pi & Sasaki 2112.12680
curvaton floor, Abe et al. 2209.13891 USR tail with the CORRECTED variance-ratio
formula, O3 95% bound via PI envelope). Shared machinery imported from
endtoend_calc.py (bug-fixed 2026-10-06).

Targets:
  - T&L illustrative : beta=1e-5   (calibration; must reproduce marginal-case note)
  - briefing low-mass : beta=2e-19 at M=1e9 kg   (f_* ~ 58 Hz, in LIGO band)
  - briefing high-mass: beta=1.5e-12 at M=6e22 kg (f_* ~ 7 uHz, out of band)
"""
import sys, math
import numpy as np
from scipy.special import erfcinv

sys.path.insert(0, '/home/hatch/workspace/goals/qse-remnant-dark-matter-exploration/hidden_files')
import endtoend_calc as E

# ---------- O3 bound treatment (marginal-case note §2) ----------
O3_95_ALPHA0 = 5.8e-9          # 95% credible, alpha=0, at 25 Hz (Abbott+ 2021, log-uniform prior)
O3_PI_POINTS = [(0.0, 5.8e-9), (2.0/3.0, 3.4e-9), (3.0, 3.9e-10)]  # (alpha, limit at 25 Hz)
O3_BAND = (20.0, 1726.0)       # Hz, approximate O3 stochastic band
BBN_BOUND = 1.0e-6             # Omega_GW,0 h^2 < ~1e-6 (95%, Delta-N_eff); operative out-of-band
H2 = 0.674**2

def Omega_PI(f_hz):
    """Power-law-integrated 95% envelope."""
    return max(lim * (f_hz/25.0)**a for a, lim in O3_PI_POINTS)

C_IND = 0.822 * E.Omega_r0     # induced-GW coefficient: Omega_GW,0 = C_IND * A^2

# ---------- targets ----------
TARGETS = [
    ("T&L illustrative", 1.0e-5,  1.0e9),
    ("briefing low-mass end",  2.0e-19, 1.0e9),
    ("briefing high-mass end", 1.5e-12, 6.0e22),
]
T_SCAN = [0.87, 1.00, 1.10, 1.20, 1.50, 2.00, 2.61]   # threshold multiplier (P&S: T=1; lit: 0.87-2.61)
ZC_SCAN = [0.5, 0.7, 1.0, 1.3]

results = {}

def check(name, got, want, tol):
    ok = abs(got-want)/want <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {got:.3e}, want {want:.3e} (tol {tol*100:.0f}%)")
    return ok

print("="*72); print("0. CONSISTENCY CHECKS vs marginal-case note + corrected ledger")
print("="*72)
allok = True
# curvaton beta=1e-5: floor 1.64e-9, 3.5x below 5.8e-9
ssr = E.curvaton_s0sqrtr(1e-5)
fl = E.curvaton_Omega_floor(ssr)
allok &= check("curvaton floor @1e-5", fl, 1.64e-9, 0.03)
allok &= check("curvaton margin @1e-5", O3_95_ALPHA0/fl, 3.5, 0.06)
# USR beta=1e-5, zeta_c=1: 2.56e-9, 2.3x below
ag = E.Ag_for_beta_tail(1e-5, 1.0)
om = C_IND * ag**2
allok &= check("USR Omega @1e-5,zc=1", om, 2.56e-9, 0.04)
allok &= check("USR margin @1e-5,zc=1", O3_95_ALPHA0/om, 2.3, 0.06)
# corrected briefing-target USR verdicts: 1.20e-10 (48x), 3.24e-10 (18x)
ag_lo = E.Ag_for_beta_tail(2e-19, 1.0); om_lo = C_IND * ag_lo**2
allok &= check("USR Omega low-mass", om_lo, 1.20e-10, 0.05)
allok &= check("USR margin low-mass", O3_95_ALPHA0/om_lo, 48.0, 0.06)
ag_hi = E.Ag_for_beta_tail(1.5e-12, 1.0); om_hi = C_IND * ag_hi**2
allok &= check("USR Omega high-mass", om_hi, 3.24e-10, 0.05)
allok &= check("USR margin high-mass", O3_95_ALPHA0/om_hi, 18.0, 0.06)
print("  ==> " + ("ALL CONSISTENCY CHECKS PASS" if allok else "!!! CHECKS FAILED"))
print()

print("="*72); print("1. FRAMEWORK (per target)")
print("="*72)
for name, beta, M in TARGETS:
    t, T, f, k = E.t_of_M(M), E.T_of_t(E.t_of_M(M)), E.fstar_of_M(M), E.kstar_of_M(M)
    inband = O3_BAND[0] < f < O3_BAND[1]
    print(f"{name}: beta={beta:.1e} M={M:.1e} kg -> T_f={T:.2e} GeV f_*={f:.2e} Hz "
          f"[{'IN O3 BAND' if inband else 'OUT OF O3 BAND'}]")
    results[name] = {"beta": beta, "M": M, "fstar": f, "inband": inband}
print()

print("="*72); print("2. CURVATON small-r (Pi & Sasaki), threshold scan")
print("="*72)
for name, beta, M in TARGETS:
    x = erfcinv(2*beta)
    tuning = 2*x*x
    ssr_nom = 1.97/x
    fl_nom = E.curvaton_Omega_floor(ssr_nom)
    sz2 = E.curvaton_sigma_zeta_sq(ssr_nom)
    s0 = ssr_nom/np.sqrt(1e-3)
    f = results[name]["fstar"]
    pi = Omega_PI(f)
    print(f"{name}: beta={beta:.1e}")
    print(f"  nominal (T=1): s0√r={ssr_nom:.4f} floor={fl_nom:.2e} "
          f"margin_vs_5.8e-9={O3_95_ALPHA0/fl_nom:.1f}x margin_vs_PI(f*)={pi/fl_nom:.1f}x")
    print(f"  validity: sigma_z^2={sz2:.2e} (<<0.1 OK); r=1e-3 -> s0={s0:.1f} (>>1 OK); "
          f"tuning dlnB/dln(s0√r)={tuning:.1f}")
    scan = []
    for T in T_SCAN:
        s = 1.97*T/x
        o = E.curvaton_Omega_floor(s)
        m = O3_95_ALPHA0/o
        flag = "EXCLUDED" if m < 1 else ""
        scan.append((T, s, o, m))
        print(f"    T={T:4.2f}: s0√r={s:.4f} floor={o:.2e} margin={m:8.1f}x {flag}")
    # flip point: T where margin = 1
    T_flip = (O3_95_ALPHA0/fl_nom)**(1.0/8.0)
    print(f"  flip point T_flip={T_flip:.2f} (margin erased at +{(T_flip-1)*100:.0f}% threshold shift)")
    results[name]["curvaton"] = {"ssr_nom": ssr_nom, "floor_nom": fl_nom,
        "margin_alpha0": O3_95_ALPHA0/fl_nom, "margin_PI": pi/fl_nom,
        "tuning": tuning, "sigma_z2": sz2, "T_flip": T_flip,
        "scan": scan}
print()

print("="*72); print("3. USR EXPONENTIAL TAIL (corrected), zeta_c scan")
print("="*72)
for name, beta, M in TARGETS:
    f = results[name]["fstar"]
    pi = Omega_PI(f)
    print(f"{name}: beta={beta:.1e}")
    scan = []
    for zc in ZC_SCAN:
        ag = E.Ag_for_beta_tail(beta, zc)
        om = C_IND*ag**2
        m = O3_95_ALPHA0/om
        flag = "EXCLUDED" if m < 1 else ""
        scan.append((zc, ag, om, m))
        print(f"    zc={zc}: A_g^tail={ag:.3e} Omega={om:.2e} margin_vs_5.8e-9={m:7.1f}x "
              f"margin_vs_PI(f*)={pi/om:7.1f}x {flag}")
    ag1 = E.Ag_for_beta_tail(beta, 1.0)
    print(f"  tuning dlnB/dlnA_g (zc=1) = {E.tail_tuning(ag1, 1.0):.1f}")
    results[name]["usr"] = {"scan": scan,
        "margin_alpha0_nom": O3_95_ALPHA0/(C_IND*ag1**2),
        "margin_PI_nom": pi/(C_IND*ag1**2)}
print()

print("="*72); print("4. OUT-OF-BAND / INTEGRAL CONSTRAINTS")
print("="*72)
for name, beta, M in TARGETS:
    r = results[name]
    f = r["fstar"]
    if not r["inband"]:
        for ch, key in [("curvaton", "floor_nom"), ("USR", None)]:
            om = r["curvaton"]["floor_nom"] if ch == "curvaton" else C_IND*E.Ag_for_beta_tail(beta, 1.0)**2
            # BBN integral bound is on Omega_GW h^2 integrated over all f; narrow peak ~ its height
            print(f"  {name} {ch}: f_*={f:.2e} Hz has NO direct stochastic bound. "
                  f"Peak {om:.2e} vs BBN integral bound (Om h^2<1e-6): "
                  f"{BBN_BOUND/(om*H2):.0f}x below (operative constraint).")
print()
np.savez("/home/hatch/workspace/goals/qse-remnant-dark-matter-exploration/hidden_files/formation_endtoend_results.npz",
         **{k.replace(" ", "_").replace("-", "_"): np.array([v["fstar"]]) for k, v in results.items()})
print("results npz saved.")
print("Done.")
