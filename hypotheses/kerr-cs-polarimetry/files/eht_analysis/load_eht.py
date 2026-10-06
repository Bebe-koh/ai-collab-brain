"""Loader for EHT 2017 public polarimetric UVFITS (Sgr A* pol release, Mar 2024).
Pol order from STOKES axis (CRVAL3=-1, CDELT3=-1): 0=RR, 1=LL, 2=RL, 3=LR.
"""
import numpy as np
from astropy.io import fits

POLS = ["RR", "LL", "RL", "LR"]

def load_uvfits(fn):
    h = fits.open(fn)
    d = h[0].data
    t = d["DATE"].astype(np.float64) + d["_DATE"].astype(np.float64)  # JD
    bl = d["BASELINE"]
    a1 = (bl // 256).astype(int); a2 = (bl % 256).astype(int)
    vis = d["DATA"]  # (n,1,1,1,1,4,3)
    out = {}
    for p, name in enumerate(POLS):
        v = vis[..., p, 0] + 1j * vis[..., p, 1]
        w = vis[..., p, 2]
        out[name] = (v.ravel(), w.ravel())
    an = h["AIPS AN"].data["ANNAME"]
    stations = {i + 1: s.strip() for i, s in enumerate(an)}
    h.close()
    return {"t": t, "a1": a1, "a2": a2, "inttim": d["INTTIM"],
            "vis": out, "stations": stations}

def build_closures(rec):
    """Per (time, triangle) closure phases for each pol product.
    Returns dict pol -> list of (t_mid, tri_idx, psi, sigma2) with per-point
    variance from visibility weights (high-SNR approx)."""
    t = rec["t"]; a1 = rec["a1"]; a2 = rec["a2"]
    ut = np.unique(np.round(t, 9))
    # index: (time_idx, (i,j)) -> (vis_idx)
    # store per-pol complex vis arrays
    V = {p: rec["vis"][p][0] for p in POLS}
    W = {p: rec["vis"][p][1] for p in POLS}
    tris = {}   # tri_id -> list of rows
    for ti, tt in enumerate(ut):
        m = np.abs(t - tt) < 1e-9
        idx = np.where(m)[0]
        # baseline lookup both orientations: V_ji = conj(V_ij)
        blmap = {}
        for k in idx:
            i, j = int(a1[k]), int(a2[k])
            blmap[(i, j)] = k
        ants = sorted(set(a1[idx].tolist()) | set(a2[idx].tolist()))
        for x in range(len(ants)):
            for y in range(x + 1, len(ants)):
                for z in range(y + 1, len(ants)):
                    i, j, k = ants[x], ants[y], ants[z]
                    legs = []
                    ok = True
                    for (a, b) in [(i, j), (j, k), (k, i)]:
                        if (a, b) in blmap: legs.append((blmap[(a, b)], 1))
                        elif (b, a) in blmap: legs.append((blmap[(b, a)], -1))
                        else: ok = False; break
                    if not ok: continue
                    tri = (i, j, k)
                    for p in POLS:
                        v1 = V[p][legs[0][0]]; v2 = V[p][legs[1][0]]; v3 = V[p][legs[2][0]]
                        if legs[0][1] < 0: v1 = np.conj(v1)
                        if legs[1][1] < 0: v2 = np.conj(v2)
                        if legs[2][1] < 0: v3 = np.conj(v3)
                        w1 = W[p][legs[0][0]]; w2 = W[p][legs[1][0]]; w3 = W[p][legs[2][0]]
                        if w1 <= 0 or w2 <= 0 or w3 <= 0: continue
                        psi = np.angle(v1 * v2 * v3)
                        snr2 = (abs(v1)**2 * w1 + abs(v2)**2 * w2 + abs(v3)**2 * w3)
                        # var(psi) ~ sum 1/(2*SNR_b^2)
                        var = 0.5 * (1.0 / max(abs(v1)**2 * w1, 1e-30)
                                     + 1.0 / max(abs(v2)**2 * w2, 1e-30)
                                     + 1.0 / max(abs(v3)**2 * w3, 1e-30))
                        tris.setdefault((tri, p), []).append((tt, psi, var))
    return tris, ut

if __name__ == "__main__":
    import sys
    rec = load_uvfits(sys.argv[1])
    tris, ut = build_closures(rec)
    print("times:", len(ut), "span hrs:", (ut.max() - ut.min()) * 24)
    npols = {}
    for (tri, p), rows in tris.items():
        npols[p] = npols.get(p, 0) + 1
    print("triangle-pol entries:", npols)
    ntri = len(set(tri for tri, p in tris))
    print("unique triangles:", ntri)
    # RL SNR check
    v, w = rec["vis"]["RL"]
    snr = np.abs(v[w > 0]) * np.sqrt(w[w > 0])
    print("RL per-vis SNR: med=%.2f frac>3=%.2f" % (np.median(snr), np.mean(snr > 3)))
    v, w = rec["vis"]["RR"]
    snr = np.abs(v[w > 0]) * np.sqrt(w[w > 0])
    print("RR per-vis SNR: med=%.2f frac>3=%.2f" % (np.median(snr), np.mean(snr > 3)))
