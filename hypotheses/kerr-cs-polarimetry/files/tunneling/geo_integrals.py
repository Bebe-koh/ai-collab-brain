"""
Derive the homogeneous-mode effective action for a pseudoscalar phase theta
on a Kerr background, and the WKB instanton rate for 2π phase slips.

Conventions: geometric units G=c=1 for geometry; natural units hbar=c=1 for
field theory. Sgr A*: M = 4.3e6 M_sun, benchmark a_* = 0.9.

Field: Phi = (f/sqrt(2)) e^{i theta}, canonical phi_c = f*theta,
  S = ∫ d^4x sqrt(-g) [ (1/2)(d phi_c)^2 - mu^4 (1 - cos(phi_c/f)) ]
Homogeneous mode: phi_c = phi_c(t) coherent over patch r in [r_+ + delta, r_c].

Outputs: Ibar(a_*) = M_phi / M^3  (dimensionless inertia coefficient),
         winding-energy coefficient kappa (sign in ergosphere),
         calibration f*mu^2 required for Gamma^-1 = 46.9 s.
"""
import numpy as np
from scipy import integrate, constants
import json

# ---------- Kerr geometry (M = 1) ----------
def kerr_inertia(a_star, r_c=10.0, delta_r=1e-6, n_r=1500, n_th=300):
    """M_phi = ∫ sqrt(-g)(-g^tt) d^3x  (M=1 units)."""
    r_plus = 1.0 + np.sqrt(1.0 - a_star**2)
    # cluster radial points near horizon (log-like)
    s = np.linspace(0.0, 1.0, n_r)
    rs = r_plus + delta_r + (r_c - r_plus - delta_r) * s**2
    th = np.linspace(1e-8, np.pi - 1e-8, n_th)
    R, TH = np.meshgrid(rs, th, indexing='ij')
    a = a_star
    Delta = R**2 - 2.0*R + a**2
    # sqrt(-g)(-g^tt) = sinθ * ((r^2+a^2)^2 - a^2 Δ sin^2θ) / Δ
    f = np.sin(TH) * ((R**2 + a**2)**2 - a**2 * Delta * np.sin(TH)**2) / Delta
    I = 2.0 * np.pi * integrate.simpson(integrate.simpson(f, th, axis=1), rs)
    return I

def winding_coeff(a_star, r_c=10.0, delta_r=1e-6, n_r=1500, n_th=300):
    """
    kappa_tilde = E_k / ( (f^2/2) k^2 ) / M  -> dimensionless.
    Integrand: sqrt(-g) g^{φφ} = (Δ - a^2 sin^2θ)/(Δ sinθ).
    Split ergosphere (r < r_ergo(θ)) vs outside.
    """
    r_plus = 1.0 + np.sqrt(1.0 - a_star**2)
    s = np.linspace(0.0, 1.0, n_r)
    rs = r_plus + delta_r + (r_c - r_plus - delta_r) * s**2
    # polar exclusion: the kφ ansatz has a vortex-core (log) divergence on the
    # axis; exclude a polar cap and report the regular bulk contribution.
    th_cut = 0.05
    th = np.linspace(th_cut, np.pi - th_cut, n_th)
    R, TH = np.meshgrid(rs, th, indexing='ij')
    a = a_star
    Delta = R**2 - 2.0*R + a**2
    g = (Delta - a**2 * np.sin(TH)**2) / (Delta * np.sin(TH))
    r_ergo = 1.0 + np.sqrt(np.maximum(0.0, 1.0 - a**2 * np.cos(TH)**2))
    mask_ergo = R < r_ergo
    integ = lambda m: 2.0*np.pi*integrate.simpson(
        integrate.simpson(np.where(m, g, 0.0), th, axis=1), rs)
    return integ(mask_ergo), integ(~mask_ergo)

if __name__ == "__main__":
    out = {}
    print("=== M_phi / M^3 (Ibar), cutoff dependence ===")
    for a_star in [0.0, 0.5, 0.9, 0.998]:
        row = {}
        for dc in [10.0]:
            for dr in [1e-3, 1e-6, 1e-9]:
                I = kerr_inertia(a_star, r_c=dc, delta_r=dr)
                row[f"rc{dc}_dr{dr:g}"] = I
        # r_c scaling at fixed dr
        for dc in [5.0, 10.0, 20.0]:
            I = kerr_inertia(a_star, r_c=dc, delta_r=1e-6)
            row[f"rc{dc}"] = I
        out[f"Ibar_a{a_star}"] = row
        print(f"a_*={a_star}: " + ", ".join(f"{k}={v:.4g}" for k, v in row.items()))

    print("\n=== winding coefficient kappa_tilde (ergo | outside), a_*=0.9 ===")
    ke, ko = winding_coeff(0.9)
    out["kappa_ergo_a0.9"] = ke
    out["kappa_out_a0.9"] = ko
    print(f"ergo: {ke:.4g}, outside: {ko:.4g}, total: {ke+ko:.4g}")

    with open("/tmp/kerr_tunnel_geo.json", "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote /tmp/kerr_tunnel_geo.json")
