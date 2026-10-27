# Belt Inventory Note — Gravity Mapper Real-Data Pipeline
**Date:** 2026-10-13/14 | **Author:** Atlas (subagent) | **Status:** research note, not a detection claim

## 1. What was added

### 1.1 Big-three asteroids as perturbers (on rails)
Ceres, Vesta, Pallas promoted from tracers to perturbing bodies. Ephemerides
pulled from JPL Horizons at 2-day cadence (2010–2025 and 2000–2040), Sun-center
(`500@10`), TDB epochs. Masses from JPL SBDB (verified 2026-10-13):

| Body   | GM (km³/s²) | Mass (M⊕) | Source |
|--------|-------------|-----------|--------|
| Ceres  | 62.6284     | 1.571e-4  | Dawn (Nature 537, 2016) |
| Vesta  | 17.2882844  | 4.336e-5  | Park et al. 2025, Nat Astron |
| Pallas | 13.63       | 3.419e-5  | Vernazza et al. 2021, A&A 654 |

Direct + indirect terms, exactly like the planets. In the TNO hunt the
indirect term is always kept; in the inner hunt Ceres/Vesta tracers skip their
own direct term via SELF_SKIP.

**Pull bug caught and fixed:** the first pull used Horizons IDs '1','2','4',
which resolve to Mercury/Venus/Mars (planet numbers), not the asteroids.
Re-pulled with names ('Ceres','Vesta','Pallas'); radii verified
(Ceres 2.78 AU, Vesta 2.37 AU, Pallas 2.85 AU mean).

### 1.2 Asteroid ring (remaining belt)
Total belt mass 2.39e21 kg (Pitjeva 2013) minus big-three (1.40e21 kg from
their GMs) = **9.88e20 kg** in a flat circular ring at R0=2.8 AU, σ=0.3 AU.

### 1.3 Ring formulation (validated)
Thin-ring analytic formula (elliptic integrals K, E) + Gauss-Legendre radial
quadrature (200-pt; GL200 vs GL400 agree to 1e-10) + Plummer softening
ε=1.0 AU (≈ belt scale height). Validated:
- vs brute-force θ-summation: 1e-12 agreement
- Sun force exactly 0 by symmetry; far-field → point mass
- Rejected: discretized point-mass rings (TNOs pass within 4e-5 AU of 43 AU —
  a point ring would spike), 2D Gauss-Hermite (does not converge on log cusp)

The softening means embedded tracers (Ceres at 2.77 AU in the 2.8 AU ring)
see a smooth field — no exclusions needed.

### 1.4 Kuiper ring (fitted mass)
Ring at R0=43 AU, σ_r=4 AU, ε=1.0 AU. Mass fitted by gridding the TNO null
(see §2).

## 2. Kuiper-ring mass fit

Grid over M_kb = 0.001–0.24 M⊕ (log-spaced, 8 pts) + M=0, TNO null each.
Belt (asteroids + asteroid ring) ON in all cases.

| M (M⊕) | train MSE | holdout MSE | dBIC vs M=0 |
|--------|-----------|-------------|-------------|
| 0      | 4.920e-16 | 2.612e-15   | —           |
| 0.001  | 4.938e-16 | 2.605e-15   | −24         |
| 0.0022 | 4.996e-16 | 2.639e-15   | +137        |
| 0.005  | 5.293e-16 | 2.904e-15   | —           |
| ≥0.011 | …         | …           | strongly disfavored |

**Result: the 43 AU ring is NOT detected.** Grid minimum at M=0. The M=0.001
holdout "improvement" (0.3%, dBIC −24) is not credible: train MSE worsens,
and M=0.0022 is strongly disfavored (dBIC +137). Parabola in log10(M)
(excluding M=0) gives 0.0063 M⊕ but is an artifact of fitting monotonic data.

**Upper limit:** M_kb(43 AU ring) < ~0.002 M⊕ (where it starts degrading the null).

**vs literature (0.01–0.1 M⊕):** our non-detection does not contradict
literature masses. Likely reasons: (a) the Horizons TNO vectors derive from
JPL ephemerides that do not include a diffuse KB component, so there is no KB
signature to detect; (b) a narrow 43 AU ring may be the wrong profile.

**Geometric note:** a 43 AU ring pulls TNOs at 40 AU OUTWARD (+1.9e-9 AU/yr²),
while the hunter's 31.2 AU point mass pulls INWARD (−3.6e-9 AU/yr²). A 43 AU
ring is geometrically incapable of mimicking the 31.2 AU signal. The y_drift
note's "Kuiper belt" hypothesis for that signal is disfavored in this form.

## 3. Before/after null

TNO null, 74 TNOs, 15-yr, holdout MSE (pooled):

| Model | train MSE | holdout MSE | holdout RMS (med) |
|-------|-----------|-------------|-------------------|
| Pre-belt (Sun+8 planets) | 5.73e-16 | 3.206e-15 | ~6 km |
| + big-three + ast ring (KB=0) | 4.92e-16 | 2.612e-15 | 4.7 km |
| + KB ring (fitted, ≈0) | — | — | — (not used) |

**Belt improves the null by 18.5% in holdout MSE** (3.206e-15 → 2.612e-15).
The big asteroids are visible at the 6 km floor — Jase's "everything we know"
directive pays off.

## 4. Hunt verdict: the 31.2 AU signal — ABSORBED

**With the belt (big-three + asteroid ring, KB=0), the 31.2 AU candidate is
GONE.** Full re-run hunt (480-candidate grid + Nelder-Mead refinements):

**Before (pre-belt):** 2.38e-3 M⊕ @ 31.2 AU, 1.89× holdout, dBIC +7758.
**After (belt):** top refined candidate is 1.97e-6 M⊕ @ 250.8 AU, 1.007×
holdout, dBIC +54.5. No candidate near 31.2 AU.

The new top hit is 1000× less massive, 8× farther, with 0.7% absolute
improvement (vs 89% for the 31.2 AU signal). By the large-N dBIC lesson, the
+54.5 dBIC does not make it credible — the absolute ho_improvement is
negligible. The hunter returns to a clean null.

**Interpretation:** the 31.2 AU "planet" was the hunter's point-mass
approximant to the big asteroids' gravity (Ceres/Vesta/Pallas were missing
from the null). It was never a planet (would have been brighter than Pluto)
and it was not the Kuiper belt — the 43 AU ring fit (§2) rules that form out
geometrically (wrong sign) and statistically (M≈0). Jase's "everything we
know" directive works: modeling known inventory removes the phantom.

## 5. 40-yr barycenter replacement (task 5)

Applied the SPICE DE440 system-barycenter replacement (IDs 5,6,7,8) to
`planet_ephemerides_40yr.csv` outer planets, same method as the 15-yr file.
**Epoch lesson:** file epochs are TDB (Horizons interprets calendar dates as
TDB); using `utc2et` is 64 s off (≈900 km Jupiter error). Correct: ET =
t×31557600 − 43200. Verified: 15-yr Jupiter matches SPICE to 0.0001 km at the
TDB epoch.

Wobble removed (body-center → barycenter): Jupiter 219 km max, Saturn 312 km,
Uranus 2887 km, Neptune 692 km max. The Uranus/Neptune values conflate moon
wobble with DE440-vs-DE441 ephemeris differences growing to 2040; harmless for
TNOs (2887 km Uranus offset → 0.0005 km TNO effect).

## 6. Inner hunt wiring

`residual_hunt.py`: BODY_NAMES += Ceres/Vesta/Pallas (NB=11); asteroid masses
appended; SELF_SKIP updated (Ceres→8, Vesta→9); asteroid ring + KB ring in
accel(); variational T_var picks up asteroid tidal tensors automatically.
KB_MASS_EARTH global (0.0 from TNO fit). Wiring verified (accel computes);
full inner re-run pending (not required for the 31.2 AU verdict).

## 7. Explicit non-claims

- The absorbed 31.2 AU signal was never a planet. It was the hunter's
  point-mass approximant to unmodeled systematics (now: big asteroids modeled;
  43 AU KB ring ruled out as the explanation).
- The fitted KB mass (≈0, upper limit ~0.002 M⊕) is a pipeline measurement
  under stated profile assumptions (Gaussian torus R0=43±4 AU, ε=1.0 AU),
  not a published belt mass. It does not contradict literature 0.01–0.1 M⊕.
- No new outer-solar-system mass is claimed. The null is cleaner; the hunt
  verdict is in §4.

## Files
- `belt.py` — asteroid/ring physics (validated)
- `pull_asteroids_fine.py` — Horizons pull (fixed IDs)
- `ceres|vesta|pallas_fine[_40yr].csv` — 2-day ephemerides
- `tno_hunt.py` — belt wired; run_null()/run_hunt() refactored
- `fit_kb_ring.py`, `kb_ring_fit.json` — mass grid
- `residual_hunt.py` — belt wired (inner)
- `replace_barycenter_40yr.py` — task 5
