"""Cislunar pulsar-navigation design study — fresh independent simulation.
Phase 0: trajectory sanity check (Earth-centered inertial + Moon point mass).
"""
import numpy as np

C_KMS = 299792.458
MU_E = 398600.4418
MU_M = 4902.8000
R_MOON = 384400.0
T_MOON = 27.321661 * 86400.0
W_MOON = 2 * np.pi / T_MOON
AU_KM = 149597870.7
W_EARTH = 2 * np.pi / (365.25 * 86400.0)

PULSARS = [
    ("J0437-4715", (4, 37, 15.9), (-47, 15, 9.0)),
    ("B1937+21", (19, 39, 38.6), (21, 34, 59.0)),
    ("J1909-3744", (19, 9, 47.4), (-37, 44, 14.0)),
    ("B1821-24", (18, 24, 32.0), (-24, 52, 11.0)),
]

def radec_to_vec(ra, dec):
    h, m, s = ra
    d, am, asec = dec
    ra_rad = np.deg2rad((h + m / 60.0 + s / 3600.0) * 15.0)
    sign = -1.0 if d < 0 else 1.0
    dec_rad = np.deg2rad(sign * (abs(d) + am / 60.0 + asec / 3600.0))
    return np.array([np.cos(dec_rad) * np.cos(ra_rad),
                     np.cos(dec_rad) * np.sin(ra_rad),
                     np.sin(dec_rad)])

NVEC = np.array([radec_to_vec(ra, dec) for _, ra, dec in PULSARS])

PHI_MOON = 0.0  # tuned below

def moon_pos(t):
    a = W_MOON * t + PHI_MOON
    return R_MOON * np.array([np.cos(a), np.sin(a), 0.0])

def sc_accel(r, t):
    rm = moon_pos(t)
    dr = r - rm
    return (-MU_E * r / np.dot(r, r) ** 1.5
            - MU_M * (dr / np.dot(dr, dr) ** 1.5 + rm / R_MOON ** 3))

def rk4(x, t, dt, deriv):
    k1 = deriv(x, t)
    k2 = deriv(x + 0.5 * dt * k1, t + 0.5 * dt)
    k3 = deriv(x + 0.5 * dt * k2, t + 0.5 * dt)
    k4 = deriv(x + dt * k3, t + dt)
    return x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

def deriv6(x, t):
    r, v = x[0:3], x[3:6]
    xd = np.zeros(6)
    xd[0:3] = v
    xd[3:6] = sc_accel(r, t)
    return xd

if __name__ == "__main__":
    print("pulsar unit vectors (check spread):")
    for (name, _, _), n in zip(PULSARS, NVEC):
        print(f"  {name:12s} {n}")
    # pairwise angles
    print("min pairwise angle (deg):",
          np.degrees(np.arccos(np.clip(
              min(np.dot(NVEC[i], NVEC[j])
                  for i in range(4) for j in range(i + 1, 4)), -1, 1))))
    for v0y in (10.85, 10.95, 11.05):
        r = np.array([6578.0, 0.0, 0.0])
        v = np.array([0.0, v0y, 0.0])
        x = np.concatenate([r, v])
        T = 5.0 * 86400.0
        dt = 60.0
        t = 0.0
        maxd, mind = 0.0, 1e18
        t_lunar, d_moon_min = None, 1e18
        while t < T:
            x = rk4(x, t, dt, deriv6)
            t += dt
            d = np.linalg.norm(x[0:3])
            maxd = max(maxd, d)
            mind = min(mind, d)
            dm = np.linalg.norm(x[0:3] - moon_pos(t))
            if dm < d_moon_min:
                d_moon_min = dm
            if t_lunar is None and d > 300000:
                t_lunar = t / 86400.0
        print(f"v0y={v0y}: apogee~{maxd:,.0f} km, t(>300k km)={t_lunar}, "
              f"min Moon dist={d_moon_min:,.0f} km")
