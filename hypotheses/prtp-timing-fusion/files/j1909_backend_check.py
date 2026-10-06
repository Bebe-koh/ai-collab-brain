"""J1909-3744 8-yr excursion vs backend flags.

Question: is J1909's ~7.9-yr, ~300-ns quasi-periodic excursion (found in the
wide-array stage-3/phasetest work) an instrumental (backend) artifact or an
intrinsic red-noise feature?

Data: binned_J1909 (154 thirty-day bins, MJD centers) + per-TOA backend
flags (-be GASP/GUPPI/YUPPI) from the .tim file.

Tests:
  M0 null:            r = const
  M1 wave:            r = const + A*sin(2*pi*t/P + phi), P free near 7.9 yr
  M2 backends:        r = const + sum_b frac_b * off_b   (backend level jumps)
  M3 wave + backends
Also: sinusoid turning points vs backend transition MJDs;
      GUPPI-only-span check (GUPPI alone spans 10.07 yr > 7.9 yr period).

Archival-data analysis; not a detection claim.
"""
import numpy as np, json, os
from scipy.optimize import minimize

HID = os.path.expanduser("~/workspace/prtp/hidden_files")
z = np.load(os.path.join(HID, "nanograv_binned.npz"), allow_pickle=True)
centers = z["centers"]
b = z["binned_J1909"]
bi = b[:, 0].astype(int)
mjd = centers[bi]
res_ns = b[:, 1] * 1e3
err_ns = np.maximum(b[:, 2] * 1e3, 20.0)
t_yr = (mjd - mjd[0]) / 365.25
print(f"bins: {len(b)}, MJD {mjd.min():.0f}-{mjd.max():.0f} ({t_yr.max():.2f} yr)")

# per-bin backend fractions from the tim file
tm, tb = [], []
with open(os.path.join(HID, "nanograv15yr/extracted/narrowband/tim/J1909-3744_PINT_20220303.nb.tim")) as f:
    for line in f:
        p = line.split()
        if len(p) < 5 or p[0] in ("FORMAT", "C"):
            continue
        try:
            m = float(p[2])
        except ValueError:
            continue
        be = ""
        for i, t in enumerate(p):
            if t == "-be" and i + 1 < len(p):
                be = p[i + 1]
        tm.append(m); tb.append(be)
tm = np.array(tm); tb = np.array(tb)
backends = ["GASP", "GUPPI", "YUPPI"]
frac = np.zeros((len(mjd), 3))
for i, mc in enumerate(mjd):
    sel = (tm >= mc - 15) & (tm < mc + 15)
    n = sel.sum()
    if n:
        for j, be in enumerate(backends):
            frac[i, j] = (tb[sel] == be).mean()
print("backend eras (TOA MJD):")
for j, be in enumerate(backends):
    m = tm[tb == be]
    print(f"  {be}: {m.min():.0f}-{m.max():.0f}")

def lnlike(par, wave, be_off):
    # par: [const] + wave?[A,phi(,P)] + be_off?[o1,o2] (o3 = -o1-o2 constraint via mean)
    c = par[0]; k = 1
    pred = np.full_like(res_ns, c)
    if wave:
        A, ph = par[k], par[k + 1]; k += 2
        P = par[k] if len(par) > k + (2 if be_off else 0) else 7.906
        if wave == "freeP":
            P = par[k]; k += 1
        pred += A * np.sin(2 * np.pi * t_yr / P + ph)
    if be_off:
        o = par[k:k + 2]
        offs = np.array([o[0], o[1], -(o[0] + o[1])])
        pred += frac @ offs
    return -0.5 * np.sum(((res_ns - pred) / err_ns) ** 2)

def fit(wave, be_off, p0):
    r = minimize(lambda p: -lnlike(p, wave, be_off), p0, method="Nelder-Mead",
                 options=dict(maxiter=20000, xatol=1e-6, fatol=1e-6))
    return r.x, -r.fun

x0, L0 = fit(None, False, [0.0])
x1, L1 = fit(True, False, [0.0, 250.0, 0.0])          # fixed P=7.906
x1f, L1f = fit("freeP", False, [0.0, 250.0, 0.0, 7.9])
x2, L2 = fit(None, True, [0.0, 0.0, 0.0])
x3, L3 = fit(True, True, [0.0, 250.0, 0.0, 0.0, 0.0])
print("\nmodel comparison (lnL, dlnL vs null):")
for name, L, k in [("M0 null", L0, 1), ("M1 wave P=7.906", L1, 3),
                   ("M1f wave P free", L1f, 4), ("M2 backends", L2, 3),
                   ("M3 wave+backends", L3, 5)]:
    print(f"  {name:18s} lnL={L:9.1f} dlnL={L-L0:7.1f} k={k}")
print(f"\nM1f: A={x1f[1]:.0f} ns, P={x1f[3]:.2f} yr, phi={x1f[2]:.2f}")
print(f"M2 backend offsets (ns, GASP/GUPPI/YUPPI): "
      f"{x2[1]:+.0f} / {x2[2]:+.0f} / {-(x2[1]+x2[2]):+.0f}")
print(f"M3: A={x3[1]:.0f} ns, backend offs {x3[3]:+.0f}/{x3[4]:+.0f}/{-x3[3]-x3[4]:+.0f}, "
      f"wave dlnL over backends-only = {L3-L2:.1f}")

# turning points of M1f wave vs backend transitions
A, ph, P = x1f[1], x1f[2], x1f[3]
tmax = ((np.pi/2 - ph) / (2*np.pi) * P) % P
tmin = ((3*np.pi/2 - ph) / (2*np.pi) * P) % P
mjd0 = mjd[0]
print("\nwave extrema (MJD) vs backend transitions (GASP->GUPPI ~55275-55390, YUPPI start 57164):")
for k in range(-1, 3):
    print(f"  max: {mjd0 + (tmax+k*P)*365.25:.0f}   min: {mjd0 + (tmin+k*P)*365.25:.0f}")

out = {"M_dlnL": {"M1": L1-L0, "M1f": L1f-L0, "M2": L2-L0, "M3": L3-L0,
                  "wave_over_backends": L3-L2},
       "M1f": {"A_ns": float(x1f[1]), "P_yr": float(x1f[3]), "phi": float(x1f[2])},
       "backend_offsets_ns": [float(x2[1]), float(x2[2]), float(-x2[1]-x2[2])]}
json.dump(out, open(os.path.join(HID, "j1909_backend_check.json"), "w"), indent=1)
print("\nwrote j1909_backend_check.json")
