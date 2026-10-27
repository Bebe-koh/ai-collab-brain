# Planet Nine / outer-solar-system target brief (2026-10-08)

Grounded details behind last night's video batch, for the Gravity Mapper benchmark ladder.

## 1. Phan et al. (2025) — the IRAS/AKARI Planet Nine candidate

- **Paper:** "A search for Planet Nine with IRAS and AKARI data", *Publ. Astron. Soc. Australia*, doi:10.1017/pasa.2025.10024. Pre-print on arXiv (unrefereed at the time of the IFLScience write-up).
- **Method:** 23-year baseline between IRAS (1983) and AKARI (2006) far-IR all-sky surveys. A >300 AU object looks stationary within each survey but shifts between them. Searched heliocentric distance 500–700 AU, mass 7–17 M⊕. 13 automated candidate pairs → 1 surviving manual verification.
- **The one candidate pair** (Table 2 of the paper):
  - IRAS F02211-4844: RA 35.74075°, Dec −48.5125°
  - AKARI-MUSL J0220440-491247: RA 35.18379°, Dec −49.2135°
  - Angular separation: 47.4586′ (~47.5′, ~1.5 full-Moon widths)
  - Fluxes: S60 = 0.24 Jy, S65 = 0.09 Jy, S90 = 0.27 Jy, S100 = 0.52 Jy
  - AKARI component was detected 5× (3 on 26 June 2006, 2 on 26 Dec 2006), satisfying the slow-mover confirmation pattern.
- **Honest caveat (from the paper itself):** the data is *not enough to predict an orbit* of the object. Follow-up observations are needed. So the mapper cannot fit an orbit from this candidate today — it can only be used as a constraint check (does a given mass/distance produce ~47.5′ of displacement over 23 years consistent with a 500–700 AU object?).

## 2. Ammonite (2023 KQ14) — ready-made benchmark object for the mapper ladder

- **What:** fourth known sednoid, discovered by Subaru/FOSSIL (announced by MPC 2025-04-14; discovery paper *Nature Astronomy* 2025-07-14).
- **Elements:** perihelion q ≈ 66 AU, semi-major axis a ≈ 252 AU, inclination ≈ 11°, diameter 220–380 km. 19+ years of arc (precoveries back to 2005/2014/2021) — well-measured.
- **Why it matters for us:** its orbital apsides are *anti-aligned* with the other sednoids, which challenges the Planet Nine orbital-clustering argument. It is also a genuine outer-solar-system body with published elements — an ideal **known-body recovery benchmark** for the mapper's gated ladder: simulate its trajectory, hand the mapper the ephemeris blind, and see whether it recovers q/a to the sub-percent accuracy the one-body blind test already demonstrated (mass 0.069%, radius 0.0037%). This is a real-world step between the toy solar-system tests and live data.
- **Further:** the FOSSIL team's simulations suggest Ammonite fills a previously unexplained "q-gap" in distant-object distributions and that a hypothetical super-Earth perturber would need an orbit around ~500 AU rather than closer — a concrete parameter region the mapper's population-level tests could target.

## Suggested next steps (for Jase's call)

1. Ammonite blind-recovery test: forward-integrate 2023 KQ14's published orbit, generate a synthetic observation set with realistic astrometric noise, run the Stage-1 grid + Nelder-Mead recovery blind. Success criterion: recover q and a within the blind-test's demonstrated precision.
2. Phan-candidate constraint check: for a grid of (mass, distance) pairs in the paper's 7–17 M⊕ / 500–700 AU box, compute the 23-year apparent displacement; mark the region consistent with 47.46′. This is a *consistency map*, not an orbit fit — label it as such.

Sources: Phan et al. 2025 via Cambridge Core PDF (doi:10.1017/pasa.2025.10024); Wikipedia "2023 KQ14"; BBC Sky at Night write-ups; IFLScience; ASJ 2025b abstract P320b (Patrick et al.).
