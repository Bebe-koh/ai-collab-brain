"""Cislunar pulsar-navigation design study — fresh independent simulation.

Estimates spacecraft state [r, v, clock bias, clock drift] in Earth-centered
inertial frame from pulsar TOA measurements, fused in an EKF. Compares
pulsar-aided navigation accuracy vs clock grade and vs a no-pulsar baseline.

NOT copied from PRTP code — re-derived independently.
"""
import numpy as np
from scipy.linalg import expm

# ---------------- constants ----------------
C_KMS = 299792.458
MU_E = 398600.4418
MU_M = 4902.8000
R_MOON = 384400.0
T_MOON = 27.321661 * 86400.0
W_MOON = 2 * np.pi / T_MOON
AU_KM = 149597870.7
W_EARTH = 2 * np.pi / (365.25 * 86400.0)
PHI_MOON = 0.0

# 4 MSPs (AIAA 2022-1589 set): name, RA(h,m,s), Dec(d,am,asec), ~S1400 (mJy)
PULSARS = [
    ("J0437-4715", (4, 37, 15.9), (-47, 15, 9.0)),
    ("B1937+21", (19, 39, 38.6), (21, 34, 59.0)),
    ("J0218+4232", (2, 18, 6.4), (42, 32, 17.0)),
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

# ---------------- dynamics ----------------
def moon_pos(t):
    a = W_MOON * t + PHI_MOON
    return R_MOON * np.array([np.cos(a), np.sin(a), 0.0])

def earth_ssb(t):
    a = W_EARTH * t
    return AU_KM * np.array([np.cos(a), np.sin(a), 0.0])

def sc_accel(r, t):
    rm = moon_pos(t)
    dr = r - rm
    return (-MU_E * r / np.dot(r, r) ** 1.5
            - MU_M * (dr / np.dot(dr, dr) ** 1.5 + rm / R_MOON ** 3))

def state_deriv8(x, t):
    """x = [r(3) km, v(3) km/s, clock bias (s), clock drift (1/s)]"""
    r, v = x[0:3], x[3:6]
    xd = np.zeros(8)
    xd[0:3] = v
    xd[3:6] = sc_accel(r, t)
    xd[6] = x[7]
    xd[7] = 0.0
    return xd

def rk4_step(x, t, dt):
    k1 = state_deriv8(x, t)
    k2 = state_deriv8(x + 0.5 * dt * k1, t + 0.5 * dt)
    k3 = state_deriv8(x + 0.5 * dt * k2, t + 0.5 * dt)
    k4 = state_deriv8(x + dt * k3, t + dt)
    return x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

def jac_numeric(x, t):
    n = len(x)
    F = np.zeros((n, n))
    f0 = state_deriv8(x, t)
    for j in range(n):
        h = 1e-7 * max(1.0, abs(x[j]))
        dx = np.zeros(n)
        dx[j] = h
        F[:, j] = (state_deriv8(x + dx, t) - f0) / h
    return F

def proc_noise(dt, q_acc, q_f):
    Q = np.zeros((8, 8))
    Q[0:3, 0:3] = np.eye(3) * q_acc * dt ** 3 / 3.0
    Q[0:3, 3:6] = np.eye(3) * q_acc * dt ** 2 / 2.0
    Q[3:6, 0:3] = np.eye(3) * q_acc * dt ** 2 / 2.0
    Q[3:6, 3:6] = np.eye(3) * q_acc * dt
    Q[6, 6] = q_f * dt ** 3 / 3.0
    Q[6, 7] = q_f * dt ** 2 / 2.0
    Q[7, 6] = q_f * dt ** 2 / 2.0
    Q[7, 7] = q_f * dt
    return Q

def qf_from_M(M):
    """RW-FM diffusion coeff calibrated so 2-yr holdover RMS = 1.4 us * M
    (PRTP measured anchor). sigma_x(T) = sqrt(q T^3/3)."""
    return 3.0 * (1.4e-6 * M) ** 2 / (2 * 365.25 * 86400.0) ** 3

# ---------------- truth trajectory ----------------
def gen_truth(T_days=4.5, dt=30.0, v0y=10.95, srp=1e-10):
    """Integrate TLI-like coast. srp = unmodelled sunward accel (truth only)."""
    n = int(T_days * 86400.0 / dt) + 1
    xs = np.zeros((n, 8))
    x = np.zeros(8)
    x[0:3] = [6578.0, 0.0, 0.0]
    x[3:6] = [0.0, v0y, 0.0]
    ts = np.arange(n) * dt
    sun_dir = np.array([1.0, 0.0, 0.0])  # fixed sunward unit vector (approx)
    for i, t in enumerate(ts):
        xs[i] = x
        # RK4 with extra SRP term on velocity
        def d(x_, t_):
            xd = state_deriv8(x_, t_)
            xd[3:6] += srp * sun_dir
            return xd
        k1 = d(x, t)
        k2 = d(x + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = d(x + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = d(x + dt * k3, t + dt)
        x = x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ts, xs

# ---------------- EKF run ----------------
def run_case(truth_ts, truth_xs, sigma_toa, M, seed=0,
             dt_meas=600.0, q_acc=(3e-10) ** 2):
    rng = np.random.default_rng(seed)
    q_f = qf_from_M(M)
    dt = truth_ts[1] - truth_ts[0]  # filter steps on the truth grid
    n_steps = len(truth_ts)
    meas_every = int(round(dt_meas / (truth_ts[1] - truth_ts[0])))
    # initial estimate: perturbed truth
    x = truth_xs[0].copy()
    perr = np.array([10.0, 10.0, 10.0, 0.01, 0.01, 0.01, 1e-3, 3e-10])
    x += rng.normal(0, perr)
    P = np.diag(perr ** 2)
    cb_true, cd_true = 0.0, 0.0
    pos_err, pred_std = [], []
    meas_count = 0
    for i in range(n_steps):
        t = truth_ts[i]
        xt = truth_xs[i]
        # --- measurement at current t (state and truth aligned) ---
        if i > 0 and i % meas_every == 0:
            k = meas_count % 4
            nhat = NVEC[k]
            r_ssb = earth_ssb(t) + xt[0:3]
            z_true = np.dot(nhat, r_ssb) / C_KMS + cb_true
            z = z_true + rng.normal(0, sigma_toa)
            r_ssb_pred = earth_ssb(t) + x[0:3]
            z_pred = np.dot(nhat, r_ssb_pred) / C_KMS + x[6]
            H = np.zeros(8)
            H[0:3] = nhat / C_KMS
            H[6] = 1.0
            y = z - z_pred
            S = H @ P @ H + sigma_toa ** 2
            K = P @ H / S
            x = x + K * y
            P = P - np.outer(K, H) @ P
            meas_count += 1
        if t > 0.5 * truth_ts[-1]:
            pos_err.append(np.linalg.norm(x[0:3] - xt[0:3]))
            pred_std.append(np.sqrt(np.trace(P[0:3, 0:3]) / 3.0))
        # --- propagate to next step ---
        if i < n_steps - 1:
            dt = truth_ts[i + 1] - truth_ts[i]
            cd_true += np.sqrt(q_f * dt) * rng.normal()
            cb_true += cd_true * dt
            F = jac_numeric(x, t)
            Phi = expm(F * dt)
            x = rk4_step(x, t, dt)
            P = Phi @ P @ Phi.T + proc_noise(dt, q_acc, q_f)
    return (np.sqrt(np.mean(np.square(pos_err))),
            np.mean(pred_std), meas_count)

def run_baseline(truth_ts, truth_xs, seed=0):
    """No-pulsar: propagate perturbed initial state with dynamics only."""
    rng = np.random.default_rng(seed)
    x = truth_xs[0].copy()
    perr = np.array([10.0, 10.0, 10.0, 0.01, 0.01, 0.01])
    x[0:6] += rng.normal(0, perr)
    dt = 30.0
    errs = []
    for i, t in enumerate(truth_ts):
        if t > 0.5 * truth_ts[-1]:
            errs.append(np.linalg.norm(x[0:3] - truth_xs[i, 0:3]))
        # propagate 6-state
        def d6(y_, t_):
            r_, v_ = y_[0:3], y_[3:6]
            yd = np.zeros(6)
            yd[0:3] = v_
            yd[3:6] = sc_accel(r_, t_)
            return yd
        k1 = d6(x[0:6], t)
        k2 = d6(x[0:6] + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = d6(x[0:6] + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = d6(x[0:6] + dt * k3, t + dt)
        x[0:6] = x[0:6] + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.sqrt(np.mean(np.square(errs)))

if __name__ == "__main__":
    import time
    t0 = time.time()
    print("generating truth...", flush=True)
    ts, xs = gen_truth()
    print(f"truth done ({time.time()-t0:.1f}s), {len(ts)} steps", flush=True)
    print("pulsar geometry: min pairwise angle = %.1f deg" % np.degrees(
        np.arccos(np.clip(max(np.dot(NVEC[i], NVEC[j])
            for i in range(4) for j in range(i+1, 4)), -1, 1))))
    # single-cell smoke test
    rms, ps, nm = run_case(ts, xs, 1e-6, 1.0, seed=0)
    print(f"smoke: sigma=1us M=1 -> rms pos {rms*1000:.1f} m, "
          f"pred {ps*1000:.1f} m, n_meas={nm}", flush=True)
    b = run_baseline(ts, xs, seed=0)
    print(f"baseline (no pulsar): rms pos {b:.1f} km", flush=True)
