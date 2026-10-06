#!/usr/bin/env python3
"""
QSE Round 2: end-to-end non-Gaussian formation calculation for Planck-relic DM.
Computes, for the briefing's beta targets, the required model parameters,
induced GW spectra, and LIGO O3 comparison for:
  (B) small-r curvaton (Pi & Sasaki 2112.12680, Eqs. 28/31/32)
  (C) USR exponential tail (Kitajima+ 2109.00791; Abe+ 2209.13891)
plus the Gaussian baseline for calibration.
All formulas sourced; systematics flagged inline.
"""
import numpy as np
from scipy.special import erfc, erfcinv
from scipy.integrate import quad
from scipy.optimize import brentq

# ---------- constants ----------
G_SI = 6.67430e-11       # m^3 kg^-1 s^-2
c_SI = 2.99792458e8      # m/s
m_Pl_kg = 2.176434e-8    # Planck mass, kg
T0_GeV = 2.348e-13       # CMB temperature today, GeV
Omega_r0 = 9.24e-5       # radiation density today (h=0.674)
gs_f = 106.75
gs0 = 3.91
gamma_pbh = 0.2          # collapse efficiency M_PBH = gamma * M_H
LIGO_O3 = 5.0e-9         # Omega_GW,0 stochastic bound, ~20-500 Hz band

# ---------- framework: M <-> t_f <-> T_f <-> f_* ----------
def t_of_M(M_kg):
    """Horizon-crossing time for PBH mass M (M = gamma*M_H)."""
    M_H = M_kg / gamma_pbh
    return M_H / 1.009e35  # M_H = 1.009e35 * t  (kg, s)

def T_of_t(t_s):
    """Formation temperature in GeV. T = 1.53e9 GeV (t/1e-25 s)^-1/2."""
    return 1.53e9 * (t_s / 1e-25) ** -0.5

def fstar_of_M(M_kg):
    """Peak frequency (Hz) of perturbations forming PBHs of mass M."""
    t = t_of_M(M_kg)
    T = T_of_t(t)
    return (1.0 / (4 * np.pi * t)) * (T0_GeV / T) * (gs0 / gs_f) ** (1.0 / 3.0)

def kstar_of_M(M_kg):
    """Peak wavenumber in Mpc^-1."""
    f = fstar_of_M(M_kg)
    # f = k c / (2 pi a0); k[Mpc^-1] = 2 pi f / c * (Mpc in m)
    return 2 * np.pi * f / c_SI * 3.085677581e22

# ---------- relic abundance sanity check ----------
def Omega_relic(beta, M_kg, kappa=1.0):
    """Relic density for collapse fraction beta at mass M (one relic of kappa*m_Pl per PBH)."""
    t = t_of_M(M_kg)
    T = T_of_t(t)                      # GeV
    T_MeV = T * 1e3
    # rho_f in GeV^4: (pi^2/30) g_* T^4
    rho_f = (np.pi ** 2 / 30) * gs_f * T ** 4
    # n_PBH(t_f) = beta * rho_f / M ; M in GeV: M_kg * 5.60958865e26 GeV/kg
    M_GeV = M_kg * 5.60958865e26
    n_f = beta * rho_f / M_GeV         # GeV^3
    a_ratio_cubed = (T0_GeV / T) ** 3 * (gs0 / gs_f)
    n_0 = n_f * a_ratio_cubed          # GeV^3
    m_relic_GeV = kappa * m_Pl_kg * 5.60958865e26
    rho_relic_0 = n_0 * m_relic_GeV    # GeV^4
    rho_crit = 8.098e-47              # GeV^4 (h=0.674)
    return rho_relic_0 / rho_crit

# ---------- Gaussian baseline ----------
def beta_gauss(sigma, zeta_c=1.0):
    return 0.5 * erfc(zeta_c / (np.sqrt(2) * sigma))

def sigma_for_beta(beta, zeta_c=1.0):
    x = erfcinv(2 * beta)
    return zeta_c / (np.sqrt(2) * x)

def Omega_GW_gauss(A, C_ind=0.822):
    """Present-day peak Omega_GW for monochromatic Gaussian source of amplitude A."""
    return C_ind * Omega_r0 * A ** 2

# ---------- Curvaton (Pi & Sasaki) ----------
def curvaton_s0sqrtr(beta):
    """Eq.(28): beta = 1/2 erfc(1.97/(s0 sqrt(r))) -> s0 sqrt(r)."""
    x = erfcinv(2 * beta)
    return 1.97 / x

def curvaton_Omega_floor(s0sqrtr):
    """Eq.(32): Omega_GW floor (r->0) = 1e-6 * (4/81) * (s0 sqrt(r))^8."""
    return 1e-6 * (4.0 / 81.0) * s0sqrtr ** 8

def curvaton_sigma_zeta_sq(s0sqrtr):
    """sigma_zeta^2 ~ (2/9)(s0 sqrt(r))^4  [from Eq.(31), s0>>1 limit]."""
    return (2.0 / 9.0) * s0sqrtr ** 4

def curvaton_tuning(beta):
    """d ln beta / d ln(s0 sqrt(r)) = 2 x^2."""
    x = erfcinv(2 * beta)
    return 2 * x ** 2

# ---------- USR exponential tail ----------
def P_tail(zeta, sigma_g):
    """P(zeta) = e^{-3 zeta} N(zeta_g(zeta); 0, sigma_g^2), zeta_g = (1-e^{-3z})/3."""
    zg = (1.0 - np.exp(-3.0 * zeta)) / 3.0
    return np.exp(-3.0 * zeta) / np.sqrt(2 * np.pi * sigma_g ** 2) * np.exp(-zg ** 2 / (2 * sigma_g ** 2))

def beta_tail(sigma_g, zeta_c=1.0):
    val, _ = quad(P_tail, zeta_c, np.inf, args=(sigma_g,), limit=200)
    return val

def Ag_for_beta_tail(beta, zeta_c=1.0):
    f = lambda s: np.log10(beta_tail(s, zeta_c)) - np.log10(beta)
    # bracket: sigma_g in [1e-3, 1]
    return brentq(f, 1e-3, 1.0) ** 2

def tail_tuning(Ag, zeta_c=1.0, h=1e-3):
    """d ln beta / d ln A_g, numerical."""
    s = np.sqrt(Ag)
    lp = np.log(beta_tail(s * (1 + h), zeta_c))
    lm = np.log(beta_tail(s * (1 - h), zeta_c))
    return (lp - lm) / (2 * h) / 2.0  # d ln beta / d ln s / 2 = d ln beta / d ln A

if __name__ == "__main__":
    # ================= main =================
    targets = [
        ("low-mass end", 2.0e-19, 1.0e9),
        ("high-mass end", 1.5e-12, 6.0e22),
    ]
    # T&L benchmark for calibration
    TL_beta, TL_A, TL_M = 1.0e-5, 5.6e-2, 1.0e9

    print("=" * 72)
    print("FRAMEWORK")
    print("=" * 72)
    for name, M in [("1e9 kg", 1e9), ("6e22 kg", 6e22)]:
        t, T, f, k = t_of_M(M), T_of_t(t_of_M(M)), fstar_of_M(M), kstar_of_M(M)
        print(f"M={name}: t_f={t:.2e} s  T_f={T:.2e} GeV  f_*={f:.2e} Hz  k_*={k:.2e} Mpc^-1")
    print()
    print("Relic-abundance sanity check (Omega_relic for briefing beta targets):")
    for name, beta, M in targets:
        print(f"  {name}: beta={beta:.1e} at M={M:.1e} kg -> Omega_relic={Omega_relic(beta, M):.3f}")
    print("  (expect ~0.25 if targets are self-consistent relic-DM numbers)")
    print()

    print("=" * 72)
    print("GAUSSIAN BASELINE (calibration)")
    print("=" * 72)
    # T&L check
    s_TL = sigma_for_beta(TL_beta)
    print(f"T&L: beta={TL_beta:.0e} -> sigma={s_TL:.4f}, P_R={s_TL**2:.2e} (paper: 5.6e-2)")
    print(f"     Omega_GW,0 = {Omega_GW_gauss(TL_A):.2e}  (paper: 1e-7--1e-6)")
    print(f"     LIGO exclusion factor: {Omega_GW_gauss(TL_A)/LIGO_O3:.1f}x")
    for name, beta, M in targets:
        s = sigma_for_beta(beta)
        A = s ** 2
        Om = Omega_GW_gauss(A)
        f = fstar_of_M(M)
        inband = "IN LIGO BAND" if 20 < f < 1000 else "outside LIGO band"
        print(f"{name}: beta={beta:.1e} -> P_R={A:.2e}, Omega_GW={Om:.2e} "
              f"({Om/LIGO_O3:.2f}x LIGO), f_*={f:.1e} Hz [{inband}]")
        x = erfcinv(2 * beta)
        print(f"     tuning dlnB/dlnA = {2*x**2:.1f} (1% amplitude -> {2*x**2:.0f}% abundance shift)")
    print()

    print("=" * 72)
    print("MECHANISM B: CURVATON small-r (Pi & Sasaki Eqs. 28/31/32)")
    print("=" * 72)
    for name, beta, M in targets:
        ssr = curvaton_s0sqrtr(beta)
        Om = curvaton_Omega_floor(ssr)
        sz2 = curvaton_sigma_zeta_sq(ssr)
        f = fstar_of_M(M)
        inband = "IN LIGO BAND" if 20 < f < 1000 else "outside LIGO band"
        # validity: pick r=1e-3 -> s0 = ssr/sqrt(r)
        r = 1e-3
        s0 = ssr / np.sqrt(r)
        print(f"{name}: beta={beta:.1e}")
        print(f"  sigma0*sqrt(r) = {ssr:.4f}")
        print(f"  e.g. r={r:.0e} -> sigma0={s0:.2f} (>>1 OK), F_NL={3/(4*r):.1e}")
        print(f"  sigma_zeta^2 = {sz2:.2e} (<<0.1 required for quadr. approx: OK)")
        print(f"  Omega_GW floor = {Om:.2e}  ({LIGO_O3/Om:.1f}x BELOW LIGO), f_*={f:.1e} Hz [{inband}]")
        print(f"  tuning dlnB/dln(s0√r) = {curvaton_tuning(beta):.1f}")
    print()

    print("=" * 72)
    print("MECHANISM C: USR EXPONENTIAL TAIL")
    print("=" * 72)
    # calibration check vs Abe et al.: VARIANCE ratio A_g(tail)/A_g(Gauss) at
    # beta~1e-14 should be ~0.255 (their 1.32e-3/5.17e-3 at f_PBH=1).
    for beta_cal in [1e-14, 2e-19, 1.5e-12]:
        Ag_t = Ag_for_beta_tail(beta_cal)
        Ag_g = sigma_for_beta(beta_cal) ** 2
        print(f"  beta={beta_cal:.0e}: A_g(tail)={Ag_t:.3e}  A_g(Gauss)={Ag_g:.3e}  "
              f"variance ratio={Ag_t/Ag_g:.3f} (paper: 0.255 at f_PBH=1)")
    print()
    for name, beta, M in targets:
        Ag_t = Ag_for_beta_tail(beta)
        Ag_g = sigma_for_beta(beta) ** 2
        # Abe et al.: vanilla diagram dominates, so Omega_USR = (A_g^T/A_g^G)^2 *
        #   Omega_Gauss(A_g^G) with A_g the spectrum amplitudes (variances), i.e.
        #   Omega_USR = C * (A_g^T)^2 = Omega_GW_gauss(A_g^T).  (Corrected
        #   2026-10-06: the previous line used ratio=sqrt(Ag_t/Ag_g) then
        #   ratio^2*Omega_GW_gauss(Ag_g) = C*Ag_t*Ag_g, overestimating Omega by
        #   Ag_g/Ag_t ~ 10x. Abe's reduction is the VARIANCE ratio squared.)
        Om = (Ag_t / Ag_g) ** 2 * Omega_GW_gauss(Ag_g)
        f = fstar_of_M(M)
        inband = "IN LIGO BAND" if 20 < f < 1000 else "outside LIGO band"
        print(f"{name}: beta={beta:.1e}")
        print(f"  A_g(tail) = {Ag_t:.3e}  (Gaussian would need {Ag_g:.3e}; variance ratio {Ag_t/Ag_g:.3f})")
        print(f"  Omega_GW = {Om:.2e}  ({LIGO_O3/Om:.1f}x BELOW LIGO), f_*={f:.1e} Hz [{inband}]")
        print(f"  tuning dlnB/dlnA_g = {tail_tuning(Ag_t):.1f}")
    print()
    print("Done.")
