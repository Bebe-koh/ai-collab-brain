"""
WKB instanton rate for homogeneous-mode 2π phase slips of a pseudoscalar
on Kerr, and calibration against the asserted Sgr A* slip cadence.

Model (stated):
  phi_c = f*theta, canonical. S = ∫dt [ (1/2) M_phi phidot^2 - mubar^4 (1-cos(phi/f)) ]
  M_phi   = Ibar * M^3            (Ibar from geo_integrals.py, M in eV^-1)
  mubar^4 = mu^4 * V_patch        (mu = cosine-potential scale in eV)
  V_patch = (4π/3) r_c^3 M^3      (coherent patch, r_c in units of M)

Kink (Euclidean): B = 8 f mubar^2 sqrt(M_phi)      [dimensionless]
  omega_0 = mubar^2/(f sqrt(M_phi))                [small-osc freq, eV]
  Gamma   = omega_0 sqrt(B/2π) e^{-B}              [per eV^-1]

Calibrate: Gamma^-1 = 46.9 s (Sgr A* asserted slip cadence) -> solve f*mu^2.
Then: sanity of (f, mu); M87* scaling (B ∝ M^3); backreaction bound on f.
"""
import numpy as np
from scipy import constants, optimize
import json

# ---------- physical constants ----------
eV_s = constants.hbar / constants.electron_volt      # 6.582e-16 s·eV
M_sun_kg = 1.98847e30
M_sun_eV = M_sun_kg * constants.c**2 / constants.electron_volt  # ~1.12e66 eV
M_sgra = 4.3e6 * M_sun_eV                            # eV (= eV^-1 as length)
M_m87 = 6.5e9 * M_sun_eV
tau_slip_sgra = 46.9                                 # s, asserted
tau_slip_sgra_eV = tau_slip_sgra / eV_s               # eV^-1

Ibar = 7452.0        # a_*=0.9, r_c=10M (geo_integrals.py)
r_c = 10.0
Vpatch_over_M3 = (4.0*np.pi/3.0) * r_c**3            # 4189

def rate_params(f_eV, mu_eV, M_eV):
    """Returns (B, omega0_eV, Gamma_eV)."""
    Mphi = Ibar * M_eV**3                            # eV^-3
    Vpatch = Vpatch_over_M3 * M_eV**3                # eV^-3
    mubar2 = mu_eV**2 * np.sqrt(Vpatch)              # eV^{1/2}
    B = 8.0 * f_eV * mubar2 * np.sqrt(Mphi)          # dimensionless
    omega0 = mubar2 / (f_eV * np.sqrt(Mphi))         # eV
    Gamma = omega0 * np.sqrt(B/(2*np.pi)) * np.exp(-B)
    return B, omega0, Gamma

def Gamma_of(f_eV, mu_eV, M_eV):
    B, o0, G = rate_params(f_eV, mu_eV, M_eV)
    return B, o0, G

if __name__ == "__main__":
    print("=== 1. sane parameters: how suppressed is tunneling? ===")
    for f_eV, mu_eV in [(1e19, 1e-10), (1e12*1e9, 1e-20), (2.4e27, 1e-33)]:
        B, o0, G = Gamma_of(f_eV, mu_eV, M_sgra)
        print(f"f={f_eV:.1e} eV, mu={mu_eV:.1e} eV: B={B:.2e}, Gamma^-1={1/G*eV_s:.2e} s")

    print("\n=== 2. unconstrained optimum over mu at fixed f ===")
    print("dlnΓ/d(mu^2)=0 -> B*=1, Gamma_max(f) = 0.0184/(f^2 M_phi)")
    Mphi = Ibar * M_sgra**3
    Vp = Vpatch_over_M3 * M_sgra**3
    log_sqrtVpMphi = 0.5*(np.log(Vp) + np.log(Mphi))  # log-domain: Vp*Mphi overflows float64
    for f_eV in [1e19, 1e3, 2.4e27]:
        Gmax = 0.0184/(f_eV**2 * Mphi)
        # mu at optimum: B* = 8 f mu^2 sqrt(Vp Mphi) = 1
        mu_star = np.exp(-0.5*(np.log(8*f_eV) + log_sqrtVpMphi))
        print(f"f={f_eV:.1e}: Gamma_max^-1={1/Gmax*eV_s:.2e} s, mu*={mu_star:.2e} eV, mu*/f={mu_star/f_eV:.1e}")
    # f needed for Gamma_max^-1 = 46.9 s:
    f_need = np.sqrt(0.0184 * tau_slip_sgra_eV / Mphi)
    mu_need = np.exp(-0.5*(np.log(8*f_need) + log_sqrtVpMphi))
    print(f"f for 46.9 s: {f_need:.2e} eV, mu*={mu_need:.2e} eV (mu*/f={mu_need/f_need:.1e} >> 1: EFT violated)")

    print("\n=== 3. EFT-consistent optimum (mu<=f): maximize over f with mu=f ===")
    # Gamma(f,f) = 0.75 f e^{-4.94e222 f^3} ; maximize
    K3 = 8*np.sqrt(Ibar*Vpatch_over_M3)*M_sgra**3   # B = K3 f^3 at mu=f
    f_opt = (1/(3*K3))**(1/3)
    B_opt = K3*f_opt**3
    G_opt = 0.75*f_opt*np.exp(-B_opt)*np.sqrt(B_opt/(2*np.pi))
    print(f"K3={K3:.2e}; f_opt={f_opt:.2e} eV, B={B_opt:.2f}, Gamma^-1={1/G_opt*eV_s:.2e} s (~{1/G_opt*eV_s/3.15e7:.1e} yr)")

    print("\n=== 4. M87* scaling (B propto M^3) ===")
    print(f"B_M87/B_SgrA = {(M_m87/M_sgra)**3:.2e}; tunneling doubly dead for M87*")

    print("\n=== 5. backreaction bound (test-field consistency) ===")
    for kt in [1.0, 265.0]:
        print(f"kappa_tilde={kt}: f << {1.0/np.sqrt(kt):.3g} eV")

    print("\n=== 6. localized phase-slip channel (LAMH-like, B~f^2 M^2) ===")
    f_loc = np.sqrt(40)/M_sgra
    print(f"B~40 needs f~{f_loc:.2e} eV; xi=M needs mu^2~f/M -> mu~{np.sqrt(f_loc/M_sgra):.1e} eV. Absurd too.")
