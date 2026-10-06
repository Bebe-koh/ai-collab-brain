"""
Independent verification of PRTP estimator claims — FRESH implementation.

Reimplements ONLY from ~/workspace/prtp/PRTP_verified_estimator_spec.md.
Does NOT import estimators.py / simulate.py / xray.py.
Pulsar coordinates copied (read-only) from simulate.py's PULSARS catalog;
documented below as the geometry source.

Tests:
  1. HD curve shape (mu(0)=1, zero crossing, quadrupolar character, PSD)
  2. GLS weight optimality (sums to 1, beats unweighted + random weights)
  3. Headline Monte Carlo: GLS vs unweighted mean on synthetic residuals
     from C = white + dipolar ephemeris + quadrupolar GWB.

Deterministic: all RNG seeded. Incremental JSON results.
Labels: verification-simulation, simulation-only. Never "validated".
"""

import json
import math
import os
import time

import numpy as np

# --------------------------------------------------------------------------
# constants & provenance
# --------------------------------------------------------------------------
SEED = 20260922
C_LIGHT = 299792458.0  # m/s

# Geometry source: simulate.py PULSARS list (approximate J2000 values;
# white-noise levels representative of published PTA precision, recorded
# in that file as SIMULATION-ONLY assumed parameters, not measured claims).
ANCHORS = [
    {"name": "J0437-4715", "ra": 69.3168,  "dec": -47.2525, "sigma_w": 120e-9},
    {"name": "J1909-3744", "ra": 287.4477, "dec": -37.7373, "sigma_w": 150e-9},
    {"name": "B1937+21",   "ra": 294.9107, "dec": 21.5831,  "sigma_w": 250e-9},
    {"name": "B1855+09",   "ra": 284.4016, "dec": 9.7214,   "sigma_w": 700e-9},
]
EXTRA = [  # Round-3 additions from the same catalog (for the N=10 check)
    {"name": "J1713+0747", "ra": 258.4639, "dec": 7.7903,   "sigma_w": 100e-9},
    {"name": "J1744-1134", "ra": 266.1195, "dec": -11.5732, "sigma_w": 150e-9},
    {"name": "J1600-3053", "ra": 240.2162, "dec": -30.8864, "sigma_w": 300e-9},
    {"name": "J0613-0200", "ra": 93.4329,  "dec": -2.0053,  "sigma_w": 400e-9},
    {"name": "J1012+5307", "ra": 153.1395, "dec": 53.1203,  "sigma_w": 500e-9},
    {"name": "J2145-0750", "ra": 326.4604, "dec": -7.8354,  "sigma_w": 600e-9},
]

# Noise-level choices (documented; "ballpark of report nominal conditions"):
#  - white: catalog sigma_w above (EFAC=1, EQUAD=0 in the spec's EFAC/EQUAD form)
#  - ephemeris: simulate.py EPH_RMS_M = 50.0 m per-component isotropic error.
#    Delay covariance = (sig_r/c)^2 * cos(gamma_pq)  (dipolar, as in spec).
#  - GWB: parameterized directly as per-epoch RMS A_gwb_s (seconds); swept
#    over {50,100,200} ns. simulate.py's GWB_A=2e-15 strain is the spectral
#    amplitude; mapping strain -> per-epoch RMS needs the full red-noise
#    treatment, so we parameterize the RMS directly and document the sweep.
EPH_RMS_M = 50.0
GWB_SWEEP_NS = [50.0, 100.0, 200.0]

OUTDIR = os.path.expanduser("~/workspace/prtp/hidden_files")
RESULTS_JSON = os.path.join(OUTDIR, "prtp_verify_results.json")
os.makedirs(OUTDIR, exist_ok=True)

results = {
    "label": "verification-simulation, simulation-only; independent "
             "reimplementation from PRTP_verified_estimator_spec.md; "
             "does NOT import estimators.py/simulate.py/xray.py",
    "seed": SEED,
    "geometry_source": "simulate.py PULSARS catalog (approx J2000; sim-only)",
    "noise_levels": {
        "white_sigma_w_ns": [p["sigma_w"] * 1e9 for p in ANCHORS],
        "ephemeris_rms_m": EPH_RMS_M,
        "ephemeris_rms_ns": EPH_RMS_M / C_LIGHT * 1e9,
        "gwb_per_epoch_rms_ns_sweep": GWB_SWEEP_NS,
        "note": "white from catalog; ephemeris from EPH_RMS_M/c; GWB RMS "
                "parameterized directly and swept (see module docstring)",
    },
    "tests": {},
    "partial": True,
}


def save():
    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------
# spec eq 2: angular separation
# --------------------------------------------------------------------------
def unit_vec(ra_deg, dec_deg):
    ra, dec = np.deg2rad(ra_deg), np.deg2rad(dec_deg)
    return np.array([np.cos(dec) * np.cos(ra),
                     np.cos(dec) * np.sin(ra),
                     np.sin(dec)])


def ang_sep_cos(nvec):
    """cos(gamma_pq) matrix from unit vectors (spec eq 2 in matrix form)."""
    return np.clip(nvec @ nvec.T, -1.0, 1.0)


# --------------------------------------------------------------------------
# spec eq 3: Hellings-Downs normalized curve
# --------------------------------------------------------------------------
def hd_mu(gamma):
    """mu(gamma) for p != q; gamma in radians (scalar or array)."""
    gamma = np.asarray(gamma, dtype=float)
    x = (1.0 - np.cos(gamma)) / 2.0
    with np.errstate(divide="ignore", invalid="ignore"):
        mu = 1.0 + 3.0 * x * np.log(x) - 0.5 * x
    return np.where(x <= 0.0, 1.0, mu)


def hd_matrix(nvec):
    """Full correlation matrix: unit diagonal, hd_mu off-diagonal."""
    cosg = ang_sep_cos(nvec)
    x = (1.0 - cosg) / 2.0
    with np.errstate(divide="ignore", invalid="ignore"):
        mu = 1.0 + 3.0 * x * np.log(x) - 0.5 * x
    return np.where(x <= 0.0, 1.0, mu)


# --------------------------------------------------------------------------
# spec eq 1: GLS weights
# --------------------------------------------------------------------------
def gls_weights(C):
    ones = np.ones(C.shape[0])
    w = np.linalg.solve(C, ones)
    return w / (ones @ w)


# --------------------------------------------------------------------------
# spec eq 4: reduced covariance assembly
# --------------------------------------------------------------------------
def build_C(sig_w, nvec, eph_rms_m=EPH_RMS_M, gwb_rms_s=100e-9,
            components=("white", "eph", "gwb")):
    N = len(sig_w)
    C = np.zeros((N, N))
    if "white" in components:
        C = C + np.diag(np.asarray(sig_w) ** 2)
    cosg = ang_sep_cos(nvec)
    if "eph" in components:
        C = C + (eph_rms_m / C_LIGHT) ** 2 * cosg
    if "gwb" in components:
        C = C + gwb_rms_s ** 2 * hd_matrix(nvec)
    return C


# --------------------------------------------------------------------------
# TEST 1: HD curve shape
# --------------------------------------------------------------------------
def test_hd_curve():
    t = {}
    # mu(0) = 1 via limit
    t["mu_at_zero"] = float(hd_mu(1e-12))
    # zero crossing by bisection on (0, pi)
    lo, hi = 0.5, 1.5  # radians; mu(0.5)>0, mu(1.5)<0 checked below
    assert hd_mu(lo) > 0 and hd_mu(hi) < 0, "bracket broken"
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if hd_mu(mid) > 0:
            lo = mid
        else:
            hi = mid
    t["zero_crossing_deg"] = float(np.rad2deg(0.5 * (lo + hi)))
    # quadrupolar character: Legendre coefficients of mu(gamma) on the sphere.
    # a_l = (2l+1)/2 * ∫ mu(gamma) P_l(cos gamma) sin(gamma) dgamma.
    # Quadrupolar => a_0 (monopole) ~ 0, a_1 (dipole) ~ 0, a_2 dominant.
    g = np.linspace(0.0, np.pi, 200001)
    mu = hd_mu(g)
    c = np.cos(g)
    wgt = np.sin(g)
    P = [np.ones_like(c), c, 0.5 * (3 * c ** 2 - 1.0), 0.5 * (5 * c ** 3 - 3 * c)]
    coeffs = {}
    for l in range(4):
        coeffs[f"a{l}"] = float((2 * l + 1) / 2.0 * np.trapz(mu * P[l] * wgt, g))
    t["legendre_coeffs"] = coeffs
    t["spherical_mean"] = float(np.trapz(mu * wgt, g) / 2.0)
    # PSD + unit diagonal for random pulsar direction sets
    rng = np.random.default_rng(SEED + 1)
    worst_eig = 1.0
    max_diag_err = 0.0
    for _ in range(20):
        u = rng.normal(size=(6, 3))
        u = u / np.linalg.norm(u, axis=1, keepdims=True)
        H = hd_matrix(u)
        worst_eig = min(worst_eig, float(np.linalg.eigvalsh(H).min()))
        max_diag_err = max(max_diag_err, float(np.abs(np.diag(H) - 1.0).max()))
    t["psd_min_eigval_20sets"] = worst_eig
    t["max_diag_deviation"] = max_diag_err
    return t


# --------------------------------------------------------------------------
# TEST 2: GLS optimality on synthetic covariances
# --------------------------------------------------------------------------
def test_gls_optimality():
    rng = np.random.default_rng(SEED + 2)
    out = {"n_matrices": 0, "max_sum_deviation": 0.0,
           "min_margin_over_unweighted": 1e9,
           "min_margin_over_random_weights": 1e9,
           "gls_best_in_all": True}
    n_rand_w = 500
    for trial in range(60):
        N = 4 if trial % 2 == 0 else 8
        # random SPD matrix with log-uniform eigenvalues (wide condition range)
        Q, _ = np.linalg.qr(rng.normal(size=(N, N)))
        lam = 10.0 ** rng.uniform(-2, 3, size=N)
        C = (Q * lam) @ Q.T
        w = gls_weights(C)
        out["n_matrices"] += 1
        out["max_sum_deviation"] = max(out["max_sum_deviation"],
                                      float(abs(w.sum() - 1.0)))
        var_gls = float(w @ C @ w)
        var_unw = float(np.ones(N) @ C @ np.ones(N) / N ** 2)
        out["min_margin_over_unweighted"] = min(
            out["min_margin_over_unweighted"], var_unw - var_gls)
        # random weight vectors on the simplex
        W = rng.dirichlet(np.ones(N), size=n_rand_w)
        var_rand = np.einsum("ij,jk,ik->i", W, C, W)
        best_rand = float(var_rand.min())
        out["min_margin_over_random_weights"] = min(
            out["min_margin_over_random_weights"], best_rand - var_gls)
        if not (var_gls <= var_unw + 1e-9 and var_gls <= best_rand + 1e-9):
            out["gls_best_in_all"] = False
    return out


# --------------------------------------------------------------------------
# TEST 3: headline Monte Carlo — GLS vs unweighted mean of common mode
# --------------------------------------------------------------------------
def mc_config(pulsars, gwb_rms_ns, components, n_trials, seed):
    nvec = np.array([unit_vec(p["ra"], p["dec"]) for p in pulsars])
    sig_w = np.array([p["sigma_w"] for p in pulsars])
    C = build_C(sig_w, nvec, gwb_rms_s=gwb_rms_ns * 1e-9, components=components)
    L = np.linalg.cholesky(C)
    w = gls_weights(C)
    rng = np.random.default_rng(seed)
    N = len(pulsars)
    se_gls, se_unw = 0.0, 0.0
    for _ in range(n_trials):
        m = rng.normal(0.0, 1000e-9)          # common monopolar component
        y = m + L @ rng.standard_normal(N)    # synthetic residuals
        se_gls += (w @ y - m) ** 2
        se_unw += (y.mean() - m) ** 2
    rms_gls = math.sqrt(se_gls / n_trials)
    rms_unw = math.sqrt(se_unw / n_trials)
    return {"n_pulsars": N, "components": list(components),
            "gwb_rms_ns": gwb_rms_ns, "n_trials": n_trials,
            "rms_gls_ns": rms_gls * 1e9, "rms_unweighted_ns": rms_unw * 1e9,
            "ratio_unw_over_gls": rms_unw / rms_gls,
            "gls_weight_vector": [round(float(x), 4) for x in w]}


def test_headline_mc(n_trials_full=3000):
    cfgs = []
    # main: 4 anchors, full covariance, GWB sweep
    for g in GWB_SWEEP_NS:
        cfgs.append(("anchors4_full_gwb%g" % g, ANCHORS, g,
                     ("white", "eph", "gwb")))
    # ablations at mid GWB
    cfgs.append(("anchors4_white_only", ANCHORS, 100.0, ("white",)))
    cfgs.append(("anchors4_white_eph", ANCHORS, 100.0, ("white", "eph")))
    cfgs.append(("anchors4_white_gwb", ANCHORS, 100.0, ("white", "gwb")))
    # array-size scaling with 10 pulsars
    cfgs.append(("pulsars10_full", ANCHORS + EXTRA, 100.0,
                 ("white", "eph", "gwb")))
    out = {}
    for i, (tag, pulsars, g, comps) in enumerate(cfgs):
        r = mc_config(pulsars, g, comps, n_trials_full, SEED + 100 + i)
        out[tag] = r
        log(f"MC {tag}: rms_gls={r['rms_gls_ns']:.1f}ns "
            f"rms_unw={r['rms_unweighted_ns']:.1f}ns "
            f"ratio={r['ratio_unw_over_gls']:.2f}")
        results["tests"]["headline_mc"] = out
        save()
    return out


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    log(f"mode={mode}")
    if mode in ("smoke", "full"):
        log("TEST 1: HD curve")
        results["tests"]["hd_curve"] = test_hd_curve()
        save()
        log("TEST 1 done: " + json.dumps(results["tests"]["hd_curve"],
                                         default=float)[:300])
        log("TEST 2: GLS optimality")
        results["tests"]["gls_optimality"] = test_gls_optimality()
        save()
        log("TEST 2 done")
    if mode == "smoke":
        log("SMOKE: tiny MC (4 pulsars, 60 trials)")
        r = mc_config(ANCHORS, 100.0, ("white", "eph", "gwb"), 60, SEED + 999)
        assert all(math.isfinite(v) for v in
                   (r["rms_gls_ns"], r["rms_unweighted_ns"],
                    r["ratio_unw_over_gls"]))
        results["tests"]["smoke_mc"] = r
        save()
        log(f"SMOKE OK: ratio={r['ratio_unw_over_gls']:.2f}")
    elif mode == "full":
        log("TEST 3: headline Monte Carlo")
        test_headline_mc()
        results["partial"] = False
        save()
        log("ALL DONE")
