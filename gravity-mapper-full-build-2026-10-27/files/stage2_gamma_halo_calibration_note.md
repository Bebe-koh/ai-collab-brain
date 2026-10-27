# Stage 2 gamma-halo calibration note — literature numbers for `compute_pbh_gamma_halo_flux()`

Status: LITERATURE CALIBRATION — replaces the parametric spike in classifier v7/v8
(ambient-density boundary match, which underpredicted the flux by ~40 orders of
magnitude) with the published formation-epoch treatment. Numbers below are
reproduced independently (see Derivation) and agree with the paper to O(1).

Source: Scholtz & Unwin, "What if Planet 9 is a Primordial Black Hole?",
arXiv:1909.11090 (2019). Spike profile from Eroshenko, arXiv:1607.00612.

## 1. The spike normalization (replaces the broken boundary match)

A primordial spike does NOT form in today's thin DM breeze. It forms at
matter–radiation equality, when the universe was ~10⁹× denser, via secondary
infall onto the PBH. The profile (valid where DM kinetic energy is negligible
— true for M_PBH > 10⁻⁶ M☉, Adamek et al. 2019 — so it holds for 1–5 M⊕):

    ρ(r) = (ρ_eq / 2) · (r_eq / r)^{9/4}

    ρ_eq  = 2.1×10⁻¹⁹ g/cm³   (total density of the universe at equality)
    r_eq  = 220 AU × (M_BH / 5M⊕)^{1/3}   (radius of influence at equality)

At Jase's test point (1 M⊕): r_eq ≈ 129 AU.

The halo is truncated by the Sun's tides once captured:

    r_t,⊙ ≈ 8 AU × (r_p / 400 AU) × (M_BH / 5M⊕)^{1/3}

At 500 AU, 1 M⊕: r_t,⊙ ≈ 5.9 AU, containing ~0.2 M⊕ of DM (~20% of the
hole's mass — verified by direct integration below).

## 2. Annihilation rate — the number that replaces the J-factor integral

For cross-sections below the plateau threshold there is no annihilation core
(r_max < r_BH) and the 9/4 profile holds all the way down. The rate is
MASS-INDEPENDENT — no parametric J-factor needed:

    Γ = 10²⁰ s⁻¹ × (⟨σv⟩ / ⟨σv⟩_ch) × (100 GeV / m_χ)²

    ⟨σv⟩_ch = 1.3×10⁻⁵⁶ cm³/s   (freeze-in characteristic cross-section)

Fluxes at Earth:

    Φ_γ = κ₁ Γ / (4π r₉²)        [photons/cm²/s],  κ₁ ≈ 10
    Φ_E = κ₂ Γ m_χ / (4π r₉²)    [W/m²],           κ₂ ≈ 1,  m_χ in joules

Note: the ar5iv HTML rendering of their eq. (11) drops a c³ in the analytic
form (dimensional check: as printed it gives L⁻³T², not s⁻¹). The numerical
value 10²⁰ s⁻¹ is correct — my independent integration of eq. (10) gives
2.7×10¹⁹ s⁻¹, O(1) agreement. Cite the number, not the typeset form.

## 3. Predictions at Jase's test point (1 M⊕, 500 AU, freeze-in, m_χ = 100 GeV)

    Γ           ≈ 1×10²⁰ s⁻¹
    Φ_γ         ≈ 1.4×10⁻¹² photons/cm²/s
    Φ_E         ≈ 2.3×10⁻¹⁷ W/m²

Fermi-LAT 8-yr catalog faintest sources (100 MeV–100 GeV):
    8.8×10⁻¹² photons/cm²/s  and  5.96×10⁻¹³ erg/cm²/s (= 5.96×10⁻¹⁶ W/m²)

So the freeze-in PBH prediction sits ~6× below the faintest catalog photon
source and ~26× below in energy flux: NOT detectable by Fermi, consistent
with non-detection.

Fermi non-detection at 500 AU ⇒ ⟨σv⟩ < 8×10⁻⁵⁶ (m_χ/100 GeV)² cm³/s.

## 4. What a gamma non-detection actually constrains (read this twice)

The PBH hypothesis MUST be split by DM model — the gamma channel is
violently model-dependent:

- **PBH + thermal WIMP** (⟨σv⟩ = 3×10⁻²⁶ cm³/s): predicted flux is ~30 orders
  of magnitude over the Fermi limit. Already dead — diffuse gamma-ray emission
  from the whole PBH population excludes it independently (Boucenna et al.
  2017; Adamek et al. 2019). A Fermi non-detection kills it at ≫5σ.
- **PBH + freeze-in** (⟨σv⟩ ~ 10⁻⁵⁶ cm³/s): prediction is BELOW Fermi's
  reach. A non-detection is fully consistent — it constrains ⟨σv⟩ but does
  not touch the hypothesis.

Honest classifier consequence: gamma is a VETO channel, not a detection
channel, for the surviving PBH scenario. The only consistent "dark" verdict
is: not a planet (optical/thermal say no) + not a WIMP-spike PBH (gamma says
no) ⇒ ambiguous_dark_body with PBH+freeze-in as the surviving model.
A bare PBH with no annihilating halo is invisible to every channel — the
classifier must be allowed to report exactly that.

## 5. Drop-in replacement for compute_pbh_gamma_halo_flux()

```python
def compute_pbh_gamma_halo_flux(self, sigmav_cm3_s=1.3e-56, m_chi_gev=100.0):
    # Scholtz & Unwin 2019, arXiv:1909.11090, eqs (5)/(10)/(11).
    # Spike anchored at matter-radiation equality, NOT today's ambient density.
    # Thermal-WIMP cross-sections (~3e-26) are excluded by diffuse gamma
    # emission; pass sigmav explicitly so the DM model stays a parameter.
    sigmav_ch = 1.3e-56  # cm^3/s, freeze-in characteristic
    Gamma = 1e20 * (sigmav_cm3_s / sigmav_ch) * (100.0 / m_chi_gev) ** 2  # s^-1
    kappa1, kappa2 = 10.0, 1.0
    d_cm = self.distance_m * 100.0
    photon_flux = kappa1 * Gamma / (4.0 * np.pi * d_cm ** 2)          # ph/cm^2/s
    m_J = m_chi_gev * 1.602176634e-10                                 # GeV -> J
    energy_flux = kappa2 * Gamma * m_J / (4.0 * np.pi * self.distance_m ** 2)  # W/m^2
    return {"flux_w_m2": energy_flux,
            "photon_flux_cm2_s": photon_flux,
            "annihilation_rate_s": Gamma}
```

And fix the gamma noise floor — 1e-24 was ~10⁸× too deep:

```python
"gamma": 1.0e-15,   # Fermi-LAT point-source energy-flux limit, W/m^2
```

Caveat: no dedicated MOVING-source Fermi search exists (the paper notes the
source drifts several degrees over 8 yr, defeating catalog matching). Catalog
limits are therefore conservative for a moving PBH — note it, don't silently
tighten.

## 6. Prior update: OGLE 2024–2026 (affects P(PBH), not the channels)

- 2022–2024 OGLE Magellanic Clouds survey (arXiv:2410.06251): 35M stars, zero
  short-timescale events ⇒ planetary-mass PBHs (1.4×10⁻⁸–0.013 M☉, covering
  1–5 M⊕) are ≤ 1% of dark matter. Rules out the PBH origin of the bulge
  short-timescale excess.
- June 2026: the "Phoebe" lunar-mass PBH candidate reclassified as an
  ordinary variable star (Udalski & Mróz reanalysis).

Classifier prior: use f_PBH ≤ 0.01 for the PBH-vs-planet prior, not the
paper's 2019 benchmark f_PBH ~ 0.05. (Capture-rate ratio Γ_BH/Γ_FFP scales
linearly with f_PBH.)

## 8. Appendix: grounding the other three noise floors (added same day)

The v8 floors were optimistic in every channel. Corrected values for
`noise_sigmas` (all in W/m², integrated flux):

- **optical — Rubin/LSST single visit, r = 24.7 (5σ):** ≈ 6×10⁻¹⁹ W/m².
  (AB: 3631 Jy × 10^(−24.7/2.5) = 4.8×10⁻⁷ Jy; × r-band Δν ≈ 1.2×10¹⁴ Hz.)
  His floor of 1.5×10⁻¹⁷ was ~25× too shallow. At his test point the
  planet's reflected flux (~7×10⁻¹⁸ W/m²) is ~12× above single-visit
  depth — Rubin should see a 1 M⊕ planet at 500 AU, albedo 0.3, in one
  visit. The 10-yr stack (r = 27.5) reaches ~4×10⁻²⁰ W/m²: a deep
  non-detection there rules the planet out hard. Optical is the one
  channel with a real operating survey behind it.
  `"optical": 6.0e-19`

- **xray — strategy-dependent, pick honestly:**
  all-sky eRASS1 ~5×10⁻¹⁴ erg/cm²/s = 5×10⁻¹⁷ W/m²;
  deep Chandra pointing ~10⁻¹⁷–10⁻¹⁶ erg/cm²/s = 10⁻²⁰–10⁻¹⁹ W/m².
  His steady-Bondi prediction (9.5×10⁻¹⁹ W/m² = 9.5×10⁻¹⁶ erg/cm²/s)
  sits ~50× below the all-sky survey floor but ~10× above the deepest
  pointed limit — i.e. invisible to surveys, accessible only to a
  targeted deep pointing nobody has done. His floor of 1×10⁻²² was
  10³–10⁵× too deep. Also: steady Bondi–Hoyle with η = 0.01 from the
  ISM is the most uncertain number in the whole classifier — the
  literature alternative is discrete accretion flares from shredding
  Oort-cloud bodies (arXiv:2005.12280: LSST could catch a few/yr).
  Consider replacing the steady model with a flare-rate model.
  `"xray": 5.0e-17   # eRASS1 all-sky; use 1e-19 only for a targeted deep pointing`

- **thermal — no operating instrument.** A 11 K blackbody peaks at
  ~250 μm; JWST/MIRI cuts off at 28 μm, Herschel is dead, and no
  current far-IR survey reaches the needed depth. The thermal channel
  as formulated is future-only (far-IR surveyor concept, e.g. PRIMA).
  Options: (a) keep it as a forward model with a "no data" flag so it
  contributes nothing to the likelihood until a survey exists;
  (b) reframe to the Wien tail at 22 μm (WISE W4) with the exponential
  suppression made explicit. Do NOT keep 1×10⁻¹⁹ labeled "JWST" —
  JWST cannot see a 250 μm peak.

Net for the classifier: optical is the detection channel (planet),
gamma is the veto channel (WIMP-spike PBH), xray is survey-weak
(targeted-only), thermal is future-only. A classifier that knows which
channels can actually fire is more honest than one with four live
channels on paper.

## 7. Derivation (reproducibility)

Γ = 4π⟨σv⟩/m² ∫_{r_BH}^{r_t} r²ρ(r)²dr, ρ from §1.
∫ r^{-5/2}dr = (2/3)(r_BH^{-3/2} − r_t^{-3/2}) ≈ (2/3)r_BH^{-3/2}.
Using M_BH = (4π/3)ρ_eq r_eq³ and r_BH = 2GM/c², the M_BH dependence
cancels exactly:
Γ = (2π/3)(⟨σv⟩/m²)ρ_eq^{1/2}(3c²/8πG)^{3/2} ≈ 2.7×10¹⁹ s⁻¹
at ⟨σv⟩_ch, m_χ = 100 GeV. Paper quotes 10²⁰ — same order.

Halo mass check: M_halo = (8π/3)ρ_eq r_eq^{9/4} r_t^{3/4}
= 1.24×10²⁴ kg ≈ 0.21 M⊕ at the test point ⇒ O(15–20%) of M_BH. ✓

No-plateau check at 1 M⊕: ceiling ⟨σv⟩ < 1.4×10⁻⁵⁴(m/100)(1/5)^{3/2}
= 1.25×10⁻⁵⁵ cm³/s > ⟨σv⟩_ch = 1.3×10⁻⁵⁶ ✓ — 9/4 profile valid to horizon.
