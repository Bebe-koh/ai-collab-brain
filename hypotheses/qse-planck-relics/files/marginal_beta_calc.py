#!/usr/bin/env python3
"""
QSE marginal-case calculation: beta = 1e-5 (T&L illustrative benchmark).

Extends endtoend_calc.py machinery (same formulas, same conventions) to the
beta=1e-5 case for (B) small-r curvaton and (C) USR exponential tail, with:
  - exact numbers (replacing [EST] ranges),
  - threshold systematics AT beta=1e-5 (where margins are thin),
  - proper O3 comparison via power-law-integrated (PI) envelope from the
    published O3 95% limits (alpha=0: 5.8e-9; 2/3: 3.4e-9; 3: 3.9e-10,
    all at f_ref=25 Hz, Abbott et al. 2021, arXiv:2101.12130),
  - validity-regime checks at the new parameters.
"""
import os, sys
import numpy as np
from scipy.special import erfcinv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from endtoend_calc import (
    curvaton_s0sqrtr, curvaton_Omega_floor, curvaton_sigma_zeta_sq,
    curvaton_tuning, Ag_for_beta_tail, sigma_for_beta, Omega_GW_gauss,
    fstar_of_M, LIGO_O3, tail_tuning,
)

BETA = 1e-5
# O3 95% limits, log-uniform prior, f_ref = 25 Hz (Abbott et al. 2021)
O3_ALPHA = np.array([0.0, 2.0 / 3.0, 3.0])
O3_LIM = np.array([5.8e-9, 3.4e-9, 3.9e-10])
FREF = 25.0

def PI_envelope(f):
    """Power-law-integrated 95% sensitivity envelope at frequency f (Hz)."""
    f = np.atleast_1d(np.asarray(f, dtype=float))
    return np.max(O3_LIM[None, :] * (f[:, None] / FREF) ** O3_ALPHA[None, :], axis=1)

print("=" * 72)
print("MARGINAL CASE: beta = 1e-5 (T&L illustrative benchmark)")
print("=" * 72)
x_star = erfcinv(2 * BETA)
print(f"erfcinv(2e-5) = {x_star:.4f}")
# Gaussian calibration
s_g = sigma_for_beta(BETA)
A_g = s_g ** 2
Om_g = Omega_GW_gauss(A_g)
print(f"\n[Gaussian calibration] P_R = {A_g:.3e}, Omega_GW,0 = {Om_g:.2e} "
      f"({Om_g / 5.8e-9:.1f}x ABOVE O3 5.8e-9 -> robustly excluded)")
print()

print("=" * 72)
print("MECHANISM B: CURVATON small-r at beta=1e-5")
print("=" * 72)
ssr = curvaton_s0sqrtr(BETA)
floor = curvaton_Omega_floor(ssr)
sz2 = curvaton_sigma_zeta_sq(ssr)
print(f"sigma0*sqrt(r) = {ssr:.4f}   (EST said ~0.66)")
print(f"Omega_GW floor = {floor:.3e}   (EST said ~1.7e-9)")
print(f"  vs flat O3 number 5.8e-9: {5.8e-9 / floor:.2f}x below  |  vs briefing 5e-9: {5e-9 / floor:.2f}x below")
r = 1e-3
s0 = ssr / np.sqrt(r)
print(f"validity: r=1e-3 -> sigma0={s0:.1f} (>>1 OK), F_NL={3/(4*r):.0f}, "
      f"sigma_zeta^2={sz2:.3f} (<0.1 OK, nearer boundary than briefing targets)")
print(f"tuning dlnB/dln(s0√r) = {curvaton_tuning(BETA):.1f}")
print()
print("Threshold systematics (threshold factor T multiplies the 1.97).")
print("Pi & Sasaki adopt D_cr=0.23; literature range 0.2-0.6 -> T in [0.87, 2.61].")
print("  T      sigma0√r    floor        vs 5.8e-9   vs PI(58Hz)")
for T in [0.7, 0.87, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 2.61]:
    ssr_T = 1.97 * T / x_star
    fl_T = curvaton_Omega_floor(ssr_T)
    tag = " <- lit. low" if abs(T - 0.87) < 1e-9 else (" <- lit. high" if abs(T - 2.61) < 1e-9 else "")
    print(f"  {T:.2f}   {ssr_T:.4f}      {fl_T:.3e}   {5.8e-9/fl_T:6.2f}x      {PI_envelope(58.0)[0]/fl_T:6.2f}x{tag}")
print("  -> verdict flips (floor exceeds bound) between T=1.1 and T=1.2;")
print("     across the literature threshold range the case goes from 11x SAFE to 600x EXCLUDED")
print()

print("=" * 72)
print("MECHANISM C: USR EXPONENTIAL TAIL at beta=1e-5")
print("=" * 72)
print("Abe et al.: Omega_USR = (A_g^T/A_g^G)^2 * Omega_Gauss(A_g^G) = C*(A_g^T)^2")
print("(variance ratio squared; vanilla diagram dominates)")
# Abe-method bracket: their absolute A_g^T at f_PBH=1 is 1.32e-3 vs our PS
# 1.716e-3 at beta=1e-14 -> scale factor 0.769 applied to our beta=1e-5 A_g^T
ABE_SCALE = 1.32e-3 / Ag_for_beta_tail(1e-14)
for zc in [0.5, 0.7, 1.0, 1.3]:
    Ag_t = Ag_for_beta_tail(BETA, zeta_c=zc)
    Om = Omega_GW_gauss(Ag_t)          # correct: C * (A_g^T)^2
    Ag_t_abe = Ag_t * ABE_SCALE
    Om_abe = Omega_GW_gauss(Ag_t_abe)
    print(f"zeta_c={zc}: A_g^T={Ag_t:.3e}  Omega_GW={Om:.3e} "
          f"({5.8e-9/Om:5.2f}x below 5.8e-9; PI(58Hz): {PI_envelope(58.0)[0]/Om:5.2f}x)  "
          f"[Abe-scaled: {Om_abe:.3e}, {5.8e-9/Om_abe:5.2f}x]")
print(f"A_g^T validity (<<1 for vanilla dominance): {Ag_for_beta_tail(BETA):.2e} OK")
print(f"tuning dlnB/dlnA_g at zeta_c=1: {tail_tuning(Ag_for_beta_tail(BETA)):.1f}")
print()

print("=" * 72)
print("O3 FREQUENCY DEPENDENCE (PI envelope vs peak frequency)")
print("=" * 72)
print(" f_* (Hz)   PI_95%(f)     curvaton margin   USR margin (zc=1)")
ssr_b = curvaton_s0sqrtr(BETA)
fl_b = curvaton_Omega_floor(ssr_b)
Om_u1 = Omega_GW_gauss(Ag_for_beta_tail(BETA, zeta_c=1.0))  # corrected USR formula
for f in [20, 30, 58, 100, 200, 500, 1000]:
    pi = PI_envelope(float(f))[0]
    print(f"  {f:4d}      {pi:.3e}      {pi/fl_b:6.2f}x          {pi/Om_u1:6.2f}x")
print()
print("Anchor: M=1e9 kg -> f_*=%.1f Hz (in-band)" % fstar_of_M(1e9))
print("Done.")
