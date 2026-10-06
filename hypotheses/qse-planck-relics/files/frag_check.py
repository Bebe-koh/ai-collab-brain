"""Reproducibility script for fragmentation_vs_trapping_note.md (QSE Round 4).
Verifies: Jeans/Schwarzschild coincidence, collapse factor to trapping,
sub-mode unlock condition, relic shortfall arithmetic. Python3, numpy only."""
import numpy as np

G = 6.67430e-11
c = 299792458.0
hbar = 1.054571817e-34
m_Pl = np.sqrt(hbar*c/G)
rho_Pl = c**5/(hbar*G**2)

print(f"m_Pl = {m_Pl:.3e} kg, rho_Pl = {rho_Pl:.3e} kg/m^3")

# 1. Coincidence: R_s(M_J)/lambda_J = (pi^2/3)(c_s/c)^2 ; radiation: pi^2/9
print(f"\n[1] R_s(M_J)/lambda_J = {(np.pi**2/3)*(1/3):.4f}  (exact pi^2/9)")

# 2. Jeans mass at Planck density: correct prefactor pi^5/2/6, c_s = c/sqrt(3)
M_J_Pl = (np.pi**2.5/6)*(1/np.sqrt(3))**3
print(f"[2] M_J(rho_Pl)/m_Pl = {M_J_Pl:.3f}  (fork note had 0.524: dropped pi^1.5, used c_s=c)")

# 3. Trapping mass scale coefficient and ratio (density-independent)
m_trap_coeff = np.sqrt(3/(32*np.pi))
print(f"[3] m_trap = {m_trap_coeff:.4f} m_Pl sqrt(rho_Pl/rho); M_J/m_trap = {M_J_Pl/m_trap_coeff:.3f}")

# 4. Collapse factor horizon-entry -> trapping = 1/gamma_eff^2 (mass-independent)
for M, t_f in [(1e9, 5.0e-26), (6e22, 3.0e-12)]:
    H = 1/(2*t_f)
    rho_form = 3*H**2/(8*np.pi*G)
    rho_trap = 3*c**6/(32*np.pi*G**3*M**2)
    gamma_eff = M/(c**3*t_f/G)
    print(f"\n[4] M={M:.0e} kg: gamma_eff={gamma_eff:.3f}, "
          f"rho_trap/rho_form = {rho_trap/rho_form:.1f} (= 1/gamma_eff^2)")

# 5. Unlock: mode k unlocks after density amplification (k/k_J,i)^6.
#    Demanding < 400 -> k/k_J,i < 400^(1/6); sub-volumes < (k/k_J)^3
kmax = 400**(1/6)
print(f"\n[5] max k/k_J,i unlocking before trapping = {kmax:.2f} -> at most ~{kmax**3:.0f} sub-volumes")

# 6. Amplification needed to unlock m_Pl fragments: (M_J,i/m_Pl)^2, M_J,i ~ M/gamma_eff
for M in [1e9, 6e22]:
    M_Ji = M/0.05
    print(f"[6] M={M:.0e}: unlock m_Pl needs amplification {(M_Ji/m_Pl)**2:.1e}; parent traps at 400x")

# 7. Relic shortfall
for M, N_need in [(1e9, 4.6e16), (6e22, 2.8e30)]:
    for N in [1, 5, 20]:
        print(f"[7] M={M:.0e}: {N} trapped pieces -> short by {N_need/N:.1e}x")
