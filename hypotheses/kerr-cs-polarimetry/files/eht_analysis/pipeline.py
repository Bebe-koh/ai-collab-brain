"""CS phase-slip null/bound pipeline for EHT 2017 Sgr A* polarimetry.

Signal (verified conventions): RL closure triangles acquire -6*dchi(t),
LR acquire +6*dchi(t), dchi(t) = 2*pi*gamma*0.5*(1+tanh((t-t0)/tau)),
tau = 46.9 s (Sgr A*), k = 1.

Complex-domain matched filter (no angle wrapping):
  per (triangle, channel): z(t) = exp(i*psi(t)), derotated by circular mean
  stack -> S^RL(t), S^LR(t); D(t) = S^RL*conj(S^LR); d(t) = D/|D|
  slip -> D acquires phase -12*dchi(t); intrinsic Q/U moves RL,LR together
  template U(t;t0,g) = exp(-12i*dchi(t;t0,g)) - mean(...), complex-demeaned
  Z(t0,g) = |sum_t d(t)*conj(U)| / sqrt(sum|U|^2 / 2)
Vetoes: SUM = S^RL*S^LR (slip cancels, station R-L cancels); RR, LL
  (slip-invariant). Calibrator scans are absent from the public release, so
  the synchronized all-station R-L jump degeneracy is unbounded -> the final
  bound is conditional on excluding that morphology by other means.
"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_eht import load_uvfits, build_closures

TAU_SLIP = 46.9
BANK = (0.15, 0.3, 0.6)   # template gamma values

def dchi(t, t0, gamma, tau=TAU_SLIP):
    return 2*np.pi*gamma*0.5*(1.0+np.tanh((t-t0)/tau))

def build_dataset(rec):
    """-> dict with per-triangle stacked ingredients + absolute time grid."""
    tris, ut = build_closures(rec)
    series = {}
    for (tri, p), rows in tris.items():
        tt = np.array([r[0] for r in rows]); psi = np.array([r[1] for r in rows])
        var = np.array([r[2] for r in rows])
        w = 1.0/np.maximum(var, 1e-12)
        z = np.exp(1j*psi)
        m = np.sum(w*z)/np.sum(w)
        series.setdefault(tuple(sorted(tri)), {})[p] = (tt, z*np.conj(m)/abs(m), w)
    ds = {"tris": {}}
    for sname, dd in series.items():
        if "RL" not in dd or "LR" not in dd: continue
        ttr = dd["RL"][0]
        e = {"t": ttr}  # absolute JD
        for p in ("RL", "LR", "RR", "LL"):
            if p in dd: e[p] = (dd[p][1], dd[p][2])
        ds["tris"][sname] = e
    return ds

def raw_triangle_series(rec):
    """Per (triangle, pol): absolute-JD times, z0 = exp(i*psi) BEFORE derotation,
    weights. Injection z -> z*exp(-/+6i*chi(t)) on these is EXACT (slip rotates
    each visibility by -/+2i*chi at the same timestamp -> triple product by
    -/+6i*chi), avoiding closure rebuilds."""
    tris, ut = build_closures(rec)
    series = {}
    for (tri, p), rows in tris.items():
        tt = np.array([r[0] for r in rows]); psi = np.array([r[1] for r in rows])
        var = np.array([r[2] for r in rows])
        w = 1.0/np.maximum(var, 1e-12)
        series.setdefault(tuple(sorted(tri)), {})[p] = (tt, np.exp(1j*psi), w)
    out = {}
    for sname, dd in series.items():
        if "RL" not in dd or "LR" not in dd: continue
        out[sname] = dd
    return out

def stack_from_raw(raw, t0_jd=None, gamma=0.0, combine="diff", tau=TAU_SLIP):
    """Stack series from raw triangle data, optionally injecting the verified
    slip (RL -> RL*exp(-2i*chi) per visibility => z_RL -> z_RL*exp(-6i*chi(t)))."""
    tris = {}
    for sname, dd in raw.items():
        e = {"t": dd["RL"][0]}
        for p in ("RL", "LR", "RR", "LL"):
            if p not in dd: continue
            tt, z0, w = dd[p]
            z = z0
            if t0_jd is not None and p in ("RL", "LR"):
                tsec = (tt - t0_jd)*86400.0
                chi = 2*np.pi*gamma*0.5*(1.0+np.tanh(tsec/tau))
                z = z0*np.exp((-6j if p == "RL" else 6j)*chi)
            # derotate by circular mean (as in build_dataset)
            m = np.sum(w*z)/np.sum(w)
            e[p] = (z*np.conj(m)/abs(m), w)
        tris[sname] = e
    ds = {"tris": tris}
    return stack_series(ds, combine)

def stack_series(ds, combine):
    """combine in {"diff","sum","RL","LR","RR","LL"} -> (t_jd, d unit phasors)."""
    tris = ds["tris"]
    tall = np.concatenate([v["t"] for v in tris.values()])
    tu = np.unique(np.round(tall, 10))
    acc = {}
    for v in tris.values():
        idx = np.searchsorted(tu, np.round(v["t"], 10))
        for p in ("RL", "LR", "RR", "LL"):
            if p not in v: continue
            z, w = v[p]
            a = acc.setdefault(p, [np.zeros(len(tu), complex), np.zeros(len(tu))])
            np.add.at(a[0], idx, w*z); np.add.at(a[1], idx, w)
    S = {}
    den0 = None
    for p, (num, den) in acc.items():
        S[p] = num/np.maximum(den, 1e-30); S[p+"_den"] = den
    if combine == "diff":
        D = S["RL"]*np.conj(S["LR"]); good = (S["RL_den"]>0)&(S["LR_den"]>0)
    elif combine == "sum":
        D = S["RL"]*S["LR"]; good = (S["RL_den"]>0)&(S["LR_den"]>0)
    else:
        D = S[combine]; good = S[combine+"_den"]>0
    amp = np.abs(D)
    d = D/np.maximum(amp, 1e-30)
    good = good & (amp > 1e-12)
    return tu[good], d[good]

def difference_series(t_jd, d):
    """Phase-increment phasors e(t)=d(t+1)*conj(d(t)), masked at gaps (>15 s).
    Kills red drifts (they become a demeaned constant); the tanh step becomes
    a sech^2-like pulse of width ~tau. No unwrapping needed.
    Returns (t_kept, e_kept, keep_idx) with keep_idx into the N-1 differences."""
    dt = np.diff((t_jd-t_jd[0])*86400.0)
    e = d[1:]*np.conj(d[:-1])
    m = dt < 15.0
    return t_jd[:-1][m], e[m], np.where(m)[0]

class DiffBank:
    """Matched filter bank for the differenced series. Template is the phase
    increment of -12*chi(t): v(t) = exp(-12i*Dchi(t)) - mean, Dchi = diff(chi).
    t = ORIGINAL (undifferenced) time grid in seconds; keep = boolean/index mask
    over the N-1 differences (from difference_series)."""
    def __init__(self, t, t0_grid, keep, gammas=BANK, tau=TAU_SLIP):
        self.t0_grid = t0_grid; self.gammas = gammas
        self.V = {}; self.nrm = {}
        keep = np.asarray(keep)
        for g in gammas:
            chi = 2*np.pi*g*0.5*(1.0+np.tanh((t[None,:]-t0_grid[:,None])/tau))
            dchi = np.diff(chi, axis=1)[:, keep]
            Vr = np.exp(-12j*dchi)
            V = Vr - Vr.mean(axis=1, keepdims=True)
            self.V[g] = V
            self.nrm[g] = np.sqrt(np.sum(np.abs(V)**2, axis=1)/2.0)
    def zgrid(self, e):
        best = np.zeros(len(self.t0_grid)); gb = np.zeros(len(self.t0_grid))
        for g in self.gammas:
            s = np.abs(self.V[g].conj() @ e)
            z = s/self.nrm[g]
            m = z > best
            best[m] = z[m]; gb[m] = g
        return best, gb

class Bank:
    def __init__(self, t, t0_grid, gammas=BANK, tau=TAU_SLIP):
        self.t = t; self.t0_grid = t0_grid; self.gammas = gammas
        self.U = {}; self.nrm = {}
        for g in gammas:
            # U[i,t]: vectorized over grid
            dt = t[None, :] - t0_grid[:, None]
            chi = 2*np.pi*g*0.5*(1.0+np.tanh(dt/tau))
            Ur = np.exp(-12j*chi)
            U = Ur - Ur.mean(axis=1, keepdims=True)
            self.U[g] = U
            self.nrm[g] = np.sqrt(np.sum(np.abs(U)**2, axis=1)/2.0)

    def zgrid(self, d):
        """max over template bank of Z(t0); returns (Zbest(G,), gbest(G,))."""
        best = np.zeros(len(self.t0_grid)); gb = np.zeros(len(self.t0_grid))
        for g in self.gammas:
            s = np.abs(self.U[g].conj() @ d)
            z = s/self.nrm[g]
            m = z > best
            best[m] = z[m]; gb[m] = g
        return best, gb

    def z_at(self, d, t0, gamma):
        chi = dchi(self.t, t0, gamma)
        ur = np.exp(-12j*chi); u = ur - ur.mean()
        s = np.abs(np.sum(d*np.conj(u)))
        return float(s/np.sqrt(np.sum(np.abs(u)**2)/2.0))

def day_statistic(ds_hi, ds_lo, t0_abs_grid):
    """Combined hi+lo day statistic on absolute-JD grid."""
    t_hi, d_hi = stack_series(ds_hi, "diff")
    t_lo, d_lo = stack_series(ds_lo, "diff")
    # per-band banks on their own grids, evaluated at common absolute t0
    out = np.zeros(len(t0_abs_grid)); gb = np.zeros(len(t0_abs_grid))
    for (t, d) in ((t_hi, d_hi), (t_lo, d_lo)):
        ts = (t - t[0])*86400.0  # relative seconds; template uses relative t
        g = t0_abs_grid
        # map absolute grid to this band's relative grid
        gr = (g - t[0])*86400.0
        m = (gr > ts.min()+3*TAU_SLIP) & (gr < ts.max()-3*TAU_SLIP)
        b = Bank(ts, gr[m])
        zb, gbb = b.zgrid(d)
        # accumulate (average of the two bands)
        out[m] += zb/2.0
    return out
