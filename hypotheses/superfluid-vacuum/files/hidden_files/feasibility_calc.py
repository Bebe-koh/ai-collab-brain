#!/usr/bin/env python3
"""
Feasibility numbers for the BEC optical-lattice tabletop glitch experiment.
All SI unless noted. Produces the tables used in bec_feasibility_note.md.
"""
import numpy as np

# ---------- constants ----------
hbar = 1.0545718e-34
h = 6.62607015e-34
kB = 1.380649e-23
m_Rb = 87 * 1.66053906660e-27
a_s = 5.3e-9                      # 87Rb s-wave scattering length (m)
z3 = 1.2020569

# ---------- trap / cloud ----------
N = 2.0e5
w_perp = 2*np.pi*20.0              # rad/s
w_z = 2*np.pi*200.0
a_perp = np.sqrt(hbar/(m_Rb*w_perp))
a_z = np.sqrt(hbar/(m_Rb*w_z))
w_bar = (w_perp**2 * w_z)**(1/3)
a_bar = (a_perp**2 * a_z)**(1/3)
mu = 0.5*hbar*w_bar*(15*N*a_s/a_bar)**0.4      # Thomas-Fermi chem. potential (J)
R_perp0 = np.sqrt(2*mu/(m_Rb*w_perp**2))
R_z0 = np.sqrt(2*mu/(m_Rb*w_z**2))
n0 = mu*m_Rb/(4*np.pi*hbar**2*a_s)              # peak density (TF)
xi = 1.0/np.sqrt(8*np.pi*n0*a_s)               # healing length
Tc = (hbar*w_bar/kB)*(N/z3)**(1/3)
kappa = h/m_Rb                                  # circulation quantum

print("=== BEC scales ===")
print(f"a_perp = {a_perp*1e6:.2f} um, a_z = {a_z*1e6:.2f} um")
print(f"mu/h = {mu/h:.0f} Hz, mu/kB = {mu/kB*1e9:.1f} nK")
print(f"R_perp(0) = {R_perp0*1e6:.1f} um, R_z(0) = {R_z0*1e6:.2f} um")
print(f"n0 = {n0:.2e} m^-3, xi = {xi*1e9:.0f} nm")
print(f"Tc = {Tc*1e9:.0f} nK")
for d_um in (2.0, 2.5, 5.0):
    d = d_um*1e-6
    Er = h**2/(8*m_Rb*d**2)
    print(f"d_OL = {d_um} um: Er/h = {Er/h:.0f} Hz, xi/d = {xi/d:.3f}")

# ---------- vortex number vs Omega (centrifugal TF correction) ----------
print("\n=== vortex number (Feynman, centrifugal-corrected TF) ===")
for Om_frac in (0.3, 0.5, 0.8):
    Om = Om_frac*w_perp
    eff = 1 - Om_frac**2
    mu_p = mu*eff**0.4
    Rp = np.sqrt(2*mu_p/(m_Rb*(w_perp*np.sqrt(eff))**2))
    nv = 2*Om/kappa
    Nv = nv*np.pi*Rp**2
    av = np.sqrt(2/(np.sqrt(3)*nv))
    print(f"Om = {Om_frac}*w_perp: mu'/h = {mu_p/h:.0f} Hz, R' = {Rp*1e6:.1f} um, "
          f"Nv = {Nv:.0f}, a_v = {av*1e6:.1f} um")

# ---------- pinning barrier ----------
# u_p (J/m) = pinning energy per unit length ~ (pi xi^2 n0 / 2) * V0
# DeltaE_hop = u_p * Lz, Lz = 2*R_z0 ; tau_slow = tau0 * exp(DeltaE/kT)
Lz = 2*R_z0
rho = m_Rb*n0
ml = np.pi*rho*xi**2*np.log(R_perp0/xi)   # vortex line mass per unit length (kg/m)

def pinning(V0_Hz, d_um=2.5):
    V0 = h*V0_Hz
    d = d_um*1e-6
    up = np.pi*xi**2*n0*V0/2.0
    dE = up*Lz
    kp = up*(2*np.pi/d)**2
    w_pin = np.sqrt(kp/ml)
    tau0 = 1.0/w_pin
    return dict(up=up, dE=dE, w_pin=w_pin, tau0=tau0)

print("\n=== pinning barrier (d = 2.5 um) ===")
print(" V0(Hz) | up(J/m)      | DeltaE/kB(nK) | w_pin(rad/s) | tau0(ms)")
for V0_Hz in (50, 100, 150, 200, 400, 1000):
    p = pinning(V0_Hz)
    print(f" {V0_Hz:6d} | {p['up']:.2e} | {p['dE']/kB*1e9:12.1f} | {p['w_pin']:11.1f} | {p['tau0']*1e3:7.1f}")

print("\n=== tau_slow = tau0*exp(DeltaE/kT), seconds ===")
Ts = [60, 70, 90, 100]
hdr = " V0(Hz) |" + "".join(f"  T={T:3d}nK  |" for T in Ts)
print(hdr)
for V0_Hz in (0, 50, 100, 150, 200, 400, 1000):
    row = f" {V0_Hz:6d} |"
    for T in Ts:
        if V0_Hz == 0:
            row += "    ---     |"
            continue
        p = pinning(V0_Hz)
        ratio = p['dE']/(kB*T*1e-9)
        ts = p['tau0']*np.exp(ratio)
        row += f" {ts:10.2g} |"
    print(row + "   (--- = no lattice)")

# ---------- depinning crossover ----------
# f_M = rho*kappa*r*dOm  (per unit length) ; f_p = 2*pi*up/d
# dOm_c = pi^2 xi^2 V0 / (d h r)
print("\n=== depinning crossover dOm_c (units of w_perp), r = 15 um ===")
for V0_Hz in (50, 100, 150, 200, 400, 1000):
    for d_um in (2.5, 5.0):
        d = d_um*1e-6
        r = 15e-6
        dOm_c = np.pi**2*xi**2*(h*V0_Hz)/(d*h*r)
        print(f" V0={V0_Hz:4d} Hz, d={d_um} um: dOm_c = {dOm_c/w_perp:.4f} w_perp ({dOm_c:.2f} rad/s)")

# ---------- tau_fast anchor ----------
print("\n=== tau_fast anchors ===")
print("Abo-Shaeer spin-down (Na, no lattice): tau ~ 0.4-2 s, rate x17 shorter for +60% T")
print("Adopted: tau_fast = 0.20 s at T=90 nK (T/Tc=0.79), scaling ~ (T/Tc)^-4 (ZNG-like)")
for T in (60, 70, 90, 100):
    tf = 0.20*( (90/114.0)/(T/114.0) )**4
    print(f" T={T} nK (T/Tc={T/114.0:.2f}): tau_fast ~ {tf:.2f} s")

# ---------- signal size ----------
print("\n=== signal per step ===")
Om = 0.8*w_perp
Rp = 29.9e-6
A = np.pi*Rp**2
for dom_frac in (0.005, 0.01, 0.02, 0.05):
    dom = dom_frac*w_perp
    dNv = (2*A/kappa)*dom
    print(f"dom = {dom_frac:.3f} w_perp ({dom:.2f} rad/s): Delta Nv = {dNv:+.1f}, "
          f"angle swept in 3 s = {dom*3:.1f} rad")

# ---------- imaging SNR ----------
print("\n=== stroboscopic readout SNR ===")
print("assumptions: 15 runs/point -> per-point sigma_Om = 0.05 rad/s")
print("(single-run vortex-pattern orientation noise ~0.2 rad/s / sqrt(15))")
for dom_frac in (0.005, 0.01, 0.02):
    dom = dom_frac*w_perp
    print(f" dom={dom_frac}: signal {dom:.2f} rad/s -> per-point SNR = {dom/0.05:.0f}")

# ---------- heating ----------
print("\n=== lattice heating (1064 nm, order of magnitude) ===")
print("Typical measured heating in 1064-nm OL at ~kHz depths: < 1 nK/s (spontaneous emission).")
print("Step itself is a phase jump (<1 ms): no intensity change -> negligible direct heating.")
print("Non-adiabatic excitation: step time 1 ms << trap period 50 ms -> sudden w.r.t. vortex dynamics,")
print("adiabatic w.r.t. band excitation (band gap ~ Er/h ~ 100 Hz -> 10 ms; MARGINAL - check).")
for d_um in (2.5, 5.0):
    Er = h**2/(8*m_Rb*(d_um*1e-6)**2)
    print(f" d={d_um} um: band gap ~ Er/h = {Er/h:.0f} Hz -> timescale {h/Er*1e3:.1f} ms vs step 1 ms")
