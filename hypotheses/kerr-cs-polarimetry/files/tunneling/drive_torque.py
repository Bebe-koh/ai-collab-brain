"""
Drive-torque plausibility for classical 2π phase slips on Sgr A*.

Question: can the magnetospheric E·B, via the thread's (γ/2)θFF̃ coupling,
supply enough torque to drive homogeneous-mode slips at 2π per 46.9 s?

Setup (thread action + explicit f normalization):
  S ⊃ ∫ √(-g) [ (f²/2)(∇θ)² + (γ/2) θ F_{μν}F̃^{μν} ],  θ dimensionless phase.
  θ EOM: f²□θ = (γ/2) F F̃  →  homogeneous: d/dt[Mθ θ̇] = (γ/2)∫FF̃√(-g)d³x
  Mθ = f² Ī M³,  Ī = 7452 (a*=0.9, r_c=10M).
  |FF̃| = 4|E·B|.

Required torque (change θ̇ by 2π/τ over time τ):
  τ_req = Mθ · 2π/τ².
Available torque:
  τ_av = 2γ ∫|E·B| √(-g)d³x  ≈ 2γ · (0.1 B²) · η_fill · V_shell,
  B ~ 10-50 G (EHT pol.), E~0.1B (reconnection), η_fill ~ 1e-3..1e-1,
  V_shell ~ (10M)³.

Solve τ_av = τ_req for f → upper bound on f.
Lower bound on f: CAST/HB via g_aγ = 2γ/f  (g = 2γ from derivation note §3).
"""
import numpy as np
from scipy import constants

eV_s = constants.hbar / constants.electron_volt
M_sun_eV = 1.98847e30 * constants.c**2 / constants.electron_volt
M_sgra = 4.3e6 * M_sun_eV                       # eV^-1 as length
tau = 46.9 / eV_s                               # eV^-1
Ibar = 7452.0
gamma = 0.15

G_to_eV2 = 1.95e-2                              # 1 G = 1.95e-2 eV^2

def torque_required(f_eV):
    Mtheta = f_eV**2 * Ibar * M_sgra**3         # eV^-1
    return Mtheta * 2*np.pi / tau**2            # eV^2

def torque_available(B_G=30.0, EoverB=0.1, eta=1e-2, shell_R_M=10.0):
    B = B_G * G_to_eV2                          # eV^2
    EB = EoverB * B**2                          # eV^4
    V = eta * (shell_R_M*M_sgra)**3             # eV^-3
    return 2*gamma * EB * V                      # eV^2

if __name__ == "__main__":
    print("=== torque available vs required (Sgr A*) ===")
    for B_G, eta in [(10, 1e-3), (30, 1e-2), (50, 1e-1)]:
        ta = torque_available(B_G=B_G, eta=eta)
        # f_max: torque_required(f) = ta
        fmax = np.sqrt(ta / (Ibar * M_sgra**3 * 2*np.pi / tau**2))
        print(f"B={B_G} G, eta={eta:g}: τ_av={ta:.2e} eV² → f ≲ {fmax:.2e} eV")
    print()
    print("=== lower bound from lab/stellar bounds (g_aγ = 2γ/f) ===")
    for name, gmax_GeV in [("CAST", 6.6e-11), ("HB stars", 1e-10)]:
        gmax_eV = gmax_GeV * 1e9
        fmin = 2*gamma / gmax_eV
        print(f"{name}: g < {gmax_GeV:.1e} GeV⁻¹ → f ≳ {fmin:.2e} eV  (at γ=0.15)")
    print()
    print("Note: bounds assume m_θ ≲ 0.02 eV (CAST) / 10 keV (HB).")
    print("Heavy-θ escape (m_θ>10keV) needs μ≲f → m_θ≲f → f>10keV anyway: lower bound robust.")
