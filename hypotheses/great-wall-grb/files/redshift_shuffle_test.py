#!/usr/bin/env python3
"""Redshift-shuffle (permutation) null test for the HCB Great Wall claim.

STATUS: pipeline only — the matching 9,180-row catalog is still missing
(see ~/workspace/grb/PROVENANCE.md). Do NOT run this on a non-matching
catalog and call the result a validation of the recorded p~0.0125.

Test design (matches the recorded claim, not a rectangular RA/Dec box):
  PRIMARY: fixed 50-degree spherical cap centered at (RA 215.94 deg,
  Dec +49.51 deg); count GRBs with z in [1.6, 2.1]. Permute redshifts
  among the redshift-bearing subset only (bursts without a measured z
  are excluded from the shuffle pool). Empirical p = fraction of
  permutations with count >= observed count.
  LOOK-ELSEWHERE variant: the cap center was chosen post-hoc, so also
  scan cap centers over a coarse sky grid, record the max count per
  permutation, and compare the observed max to the permuted-max
  distribution. This is the honest p for a post-hoc geometry.

Corrections vs the pasted Gemini scaffold:
  - 50-deg cap geometry (the recorded statistic) instead of a rectangular
    RA/Dec box (a different statistic with different power).
  - Shuffle pool restricted to redshift-bearing rows.
  - Post-hoc-geometry correction included.

Usage:
  python3 redshift_shuffle_test.py catalog.csv [--n-perm 10000] [--seed 42]
  python3 redshift_shuffle_test.py --self-test   # mechanics sanity check
"""

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

# Recorded claim geometry (from the portfolio record, not re-derived here)
CAP_RA = 215.94
CAP_DEC = 49.51
CAP_RADIUS_DEG = 50.0
Z_MIN, Z_MAX = 1.6, 2.1


def angsep_deg(ra1, dec1, ra2, dec2):
    """Great-circle separation in degrees (haversine)."""
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    s = (math.sin((d2 - d1) / 2.0) ** 2
         + math.cos(d1) * math.cos(d2) * math.sin((r2 - r1) / 2.0) ** 2)
    return math.degrees(2.0 * math.asin(min(1.0, math.sqrt(s))))


def load_catalog(path):
    df = pd.read_csv(path)
    for col in ("ra", "dec", "z"):
        if col not in df.columns:
            raise ValueError(f"catalog missing required column '{col}'")
    df = df.copy()
    df["ra"] = pd.to_numeric(df["ra"], errors="coerce")
    df["dec"] = pd.to_numeric(df["dec"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    df = df.dropna(subset=["ra", "dec"])
    zsub = df.dropna(subset=["z"]).reset_index(drop=True)
    return zsub


def sep_to_cap(ra, dec):
    ra = np.asarray(ra, dtype=float)
    dec = np.asarray(dec, dtype=float)
    r1 = np.radians(ra); d1 = np.radians(dec)
    r2 = math.radians(CAP_RA); d2 = math.radians(CAP_DEC)
    s = (np.sin((d2 - d1) / 2.0) ** 2
         + np.cos(d1) * np.cos(d2) * np.sin((r2 - r1) / 2.0) ** 2)
    return np.degrees(2.0 * np.arcsin(np.clip(np.sqrt(s), 0.0, 1.0)))


def run_primary(df, n_perm=10000, seed=42):
    rng = np.random.default_rng(seed)
    ra = df["ra"].to_numpy(); dec = df["dec"].to_numpy()
    z = df["z"].to_numpy()
    in_cap = sep_to_cap(ra, dec) <= CAP_RADIUS_DEG
    in_z = (z >= Z_MIN) & (z <= Z_MAX)
    n_obs = int(np.sum(in_cap & in_z))
    n_cap = int(np.sum(in_cap))
    sim = np.empty(n_perm, dtype=int)
    for k in range(n_perm):
        zs = rng.permutation(z)
        sim[k] = np.sum(in_cap & (zs >= Z_MIN) & (zs <= Z_MAX))
    p = float(np.mean(sim >= n_obs))
    return {
        "test": "primary_fixed_cap",
        "n_redshift_rows": len(df),
        "n_in_cap": n_cap,
        "n_obs_in_cap_zslice": n_obs,
        "n_perm": n_perm,
        "null_mean": float(np.mean(sim)),
        "null_std": float(np.std(sim)),
        "p_value": p,
    }


def run_lookelsewhere(df, n_perm=2000, seed=1234, grid_step=10.0):
    """Scan cap centers on a coarse grid; max count per permutation."""
    rng = np.random.default_rng(seed)
    ra = df["ra"].to_numpy(); dec = df["dec"].to_numpy()
    z = df["z"].to_numpy()
    # coarse grid of cap centers over the northern sky region of interest
    centers = [(r, d) for r in np.arange(120, 300, grid_step)
               for d in np.arange(10, 80, grid_step)]
    r1 = np.radians(ra)[:, None]; d1 = np.radians(dec)[:, None]
    cr = np.radians(np.array([c[0] for c in centers]))[None, :]
    cd = np.radians(np.array([c[1] for c in centers]))[None, :]
    s = (np.sin((cd - d1) / 2.0) ** 2
         + np.cos(d1) * np.cos(cd) * np.sin((cr - r1) / 2.0) ** 2)
    sep = np.degrees(2.0 * np.arcsin(np.clip(np.sqrt(s), 0, 1)))
    in_any_cap = sep <= CAP_RADIUS_DEG  # (n_bursts, n_centers)

    def max_count(zz):
        in_z = ((zz >= Z_MIN) & (zz <= Z_MAX))[:, None]
        counts = np.sum(in_any_cap & in_z, axis=0)
        return int(np.max(counts))

    obs_max = max_count(z)
    sim_max = np.empty(n_perm, dtype=int)
    for k in range(n_perm):
        sim_max[k] = max_count(rng.permutation(z))
    p = float(np.mean(sim_max >= obs_max))
    return {
        "test": "lookelsewhere_max_over_caps",
        "n_cap_centers": len(centers),
        "observed_max_count": obs_max,
        "n_perm": n_perm,
        "null_max_mean": float(np.mean(sim_max)),
        "p_value": p,
    }


def self_test():
    """Mechanics sanity check: uniform sky + uniform z -> p should be ~large."""
    rng = np.random.default_rng(0)
    n = 3000
    ra = rng.uniform(0, 360, n)
    dec = np.degrees(np.arcsin(rng.uniform(-1, 1, n)))
    z = rng.uniform(0.1, 8.0, n)
    df = pd.DataFrame({"ra": ra, "dec": dec, "z": z})
    r = run_primary(df, n_perm=2000, seed=7)
    print(json.dumps(r, indent=2))
    assert r["p_value"] > 0.05, "sanity check failed: uniform data gave small p"
    print("SELF-TEST OK: uniform data correctly yields a large p-value.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalog", nargs="?", default=None)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--look-elsewhere", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if not args.catalog:
        ap.error("provide a catalog CSV or --self-test")
    df = load_catalog(args.catalog)
    print(f"loaded {len(df)} redshift-bearing rows", file=sys.stderr)
    result = run_primary(df, n_perm=args.n_perm, seed=args.seed)
    if args.look_elsewhere:
        result["lookelsewhere"] = run_lookelsewhere(df)
    print(json.dumps(result, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
