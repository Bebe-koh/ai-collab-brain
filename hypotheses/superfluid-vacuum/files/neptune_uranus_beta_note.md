# Neptune/Uranus superfluid-drag formula — quantitative test
**2026-10-03 · completed-toy · hypothesis registry item #1**

## 1. The claim

The hypothesis proposes a superfluid drag coefficient

$$\beta = \frac{Q_{\rm out} - Q_{\rm in}}{m\,v^2}$$

to account for the thermal asymmetry between Neptune (large internal heat flux)
and Uranus (low internal heat flux). Dimensional check: power/(mass·velocity²)
= (kg·m²/s³)/(kg·m²/s²) = s⁻¹, so β is a rate; interpreted as drag, the implied
force is F = β·m·v and the dissipated power F·v = β·m·v². Dimensionally coherent.

Note the formula does not specify *which* velocity v. We test the two natural
readings: heliocentric orbital velocity (a body moving through a vacuum medium)
and equatorial rotational velocity. The verdict is the same under both.

## 2. Input data (published values)

| quantity | Uranus | Neptune | Jupiter (check) |
|---|---|---|---|
| mass (kg) | 8.6810×10²⁵ | 1.02413×10²⁶ | 1.89813×10²⁷ |
| orbital v (km/s) | 6.81 | 5.43 | 13.07 |
| equatorial v (km/s) | 2.57 | 2.67 | — |
| emitted/absorbed E/A | 1.06±0.08 (PC91) → 1.15±0.06 (I25) | 2.61±0.28 (PC91) | 2.132±0.051 (Li+2018) |
| internal power Q_exc (W) | 0.34±0.38×10¹⁵ (PC91; consistent with zero) → 0.63×10¹⁵ (W25: 0.078 W/m²) | 3.30±0.35×10¹⁵ (PC91) | 4.60×10¹⁷ (Li+2018: 7.485 W/m²) |

Sources: Pearl & Conrath 1991 (PC91, Voyager IRIS); Pearl et al. 1990; Li et al.
2018 Nature Comm (Cassini, Jupiter); Wang et al. 2025 GRL + Irwin et al. 2025
(Uranus 2025 revision: E/A = 1.15±0.06, intrinsic flux 0.078±0.018 W/m² —
Uranus *does* have internal heat; the old "zero" premise is outdated, though
its flux remains ~5× below Neptune's ~0.43 W/m²).

## 3. Computed β (orbital velocity)

| planet | β (s⁻¹) |
|---|---|
| Uranus (PC91) | 8.4×10⁻²⁰ |
| Uranus (2025 rev.) | 1.6×10⁻¹⁹ |
| Neptune | 1.09×10⁻¹⁸ |
| Jupiter | 1.42×10⁻¹⁸ |

β_N/β_U ≈ **13** (PC91) or **7** (2025 revision). With rotational velocity the
ratio is 7.6. Not universal under either reading. (Curiosity, reported honestly:
Jupiter and Neptune agree within ~30%; Uranus is the outlier by an order of
magnitude. Two-point agreement is not a law.)

## 4. The load-bearing test: universal β predicts the WRONG direction

If β were a genuine property of the vacuum medium (the only way the formula
*explains* anything), it must be planet-independent, and the predicted excess
ratio is fixed by m·v² alone:

- predicted (Q_exc,N / Q_exc,U) = (m_N·v_N²)/(m_U·v_U²) = **0.75**
  — Neptune should radiate *less* excess heat than Uranus;
- observed: **9.7** (PC91) / **5.2** (2025 revision).

The formula with a universal coefficient gets the *sign of the asymmetry*
backwards, off by a factor of ~7–13. With per-planet β it fits by construction.
**Verdict on explanation: it restates the asymmetry, it does not explain it.**
Fitting β per planet is equivalent to writing down the measured excess twice.

## 5. Ephemeris / drag consistency

Implied drag acceleration a = β·v:
- Neptune: 5.9×10⁻¹⁵ m/s²; Jupiter: 1.9×10⁻¹⁴ m/s²; Uranus: ~10⁻¹⁵ m/s².
- INPOP08 bound (Fienga et al. 2009): no constant anomalous acceleration larger
  than ¼ Pioneer anomaly ≈ 2.2×10⁻¹⁰ m/s² affects solar-system planets; Uranus
  residuals constrain it tighter still.

The implied drag is ~10⁴–10⁵× below detectability: **no conflict with
ephemerides**, but only because the effect is far too small to see, not because
it is confirmed. Implied orbital-decay timescale for Neptune ≈ 1.5×10¹⁰ yr
(≈ age of the universe) — unobservable. The ephemeris test is passed
vacuously.

## 6. Physical objections (independent of the numbers)

1. **Category error.** The measured excess is deep internal heat flux
   (primordial cooling, differentiation, interior stratification — the standard
   account of the Uranus difference is a giant-impact-altered, stably
   stratified interior suppressing convection). Orbital drag would dissipate in
   the atmosphere/surface, with no proposed coupling to the deep interior.
2. **No mechanism for β's variation.** Even as a fit, nothing in the hypothesis
   says why the vacuum would drag Neptune 13× more efficiently per unit m·v²
   than Uranus.
3. **v is undefined** in the hypothesis; the verdict survives both natural
   choices, but an explanation should not depend on the reader's guess.
4. **Uranus's PC91 internal power (0.034±0.038×10¹⁶ W) is consistent with zero**
   — in the original data β_U is statistically indistinguishable from zero.

## 7. Verdict

**RESTATES, does not explain; no ephemeris conflict (effect far below
detectability).** The formula takes the observed heat excess as input and
returns it divided by m·v². As a universal law it is falsified by its own
structure: it predicts Neptune should have *less* excess heat than Uranus.
As a per-planet fit it has no predictive content. The 2025 Uranus revision
(flux ~5× below Neptune, not ~10×) softens the asymmetry the formula was built
to explain but does not save it — the direction is still wrong.

Research label: **completed-toy** (reproducible arithmetic on published
inputs). A Saturn test point (predicted vs measured excess at universal β)
was not computed for lack of a verified Cassini-era number at hand; it would
not change the verdict.

### Reproducibility
All numbers above recomputed in-session from the cited inputs; see §3–§5.
Key check anyone can redo: (m_N·v_N²)/(m_U·v_U²) = 0.75 < 1 while
Q_exc,N/Q_exc,U > 5 — the entire result follows from this inequality.
