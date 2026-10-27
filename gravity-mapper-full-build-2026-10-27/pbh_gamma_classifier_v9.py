"""
Stage-2 classifier v9 — planet vs primordial black hole via multi-channel flux.

REBUILT 2026-10-12 from the gamma-halo calibration note
(~/workspace/goals/gravity-mapper-hidden-body-inference/files/stage2_gamma_halo_calibration_note.md).
This is NOT the lost v8 source. It reimplements the calibrated physics
(Scholtz & Unwin 2019, arXiv:1909.11090; Eroshenko, arXiv:1607.00612)
with corrected survey noise floors. Do not cite as v8.

Classifier logic (from calibration note §4, §8):
  - optical is the DETECTION channel (planet reflects sunlight)
  - gamma is a VETO channel (thermal-WIMP spike already excluded by diffuse bounds)
  - freeze-in PBH gamma is below Fermi reach -> non-detection is uninformative
  - bare PBH (no annihilating halo) is invisible to every channel
  -> the classifier may return "ambiguous", and must.

WRAPPER REDESIGN 2026-10-13 (see ../v9_wrapper_fix_note.md):
  The old convenience wrapper classify(mass, distance) computed planet
  optical flux from mass for EVERY object and returned object-type labels
  ("planet"/"pbh"). For a black-hole truth (e.g. 5 Mearth PBH at 500 AU) it
  therefore returned a confident "planet" — a misclassification, because a
  black hole reflects no sunlight. The 90-case benchmark never caught it:
  it exercised decide() on ground-truth fluxes, never the wrapper.
  The redesigned wrapper takes the object hypothesis EXPLICITLY (kind) and
  returns per-hypothesis DETECTABILITY verdicts ("detectable"/"ambiguous"),
  never object classifications. Optical reflected flux is forced to zero for
  PBH kinds. The core flux functions and decision thresholds below are
  UNCHANGED; run_v9_benchmark.py is untouched and still passes.
"""

import math

import numpy as np

# ---- constants ----
AU_M = 1.495978707e11          # m
AU_CM = 1.495978707e13         # cm
SIGMAV_CH = 1.3e-56            # cm^3/s, freeze-in characteristic (Scholtz & Unwin)
SIGMAV_WIMP = 3.0e-26          # cm^3/s, thermal WIMP (excluded by diffuse gamma)
M_CHI_GEV = 100.0
GEV_TO_J = 1.602176634e-10

# ---- survey floors (corrected, calibration note §5, §8) ----
FERMI_PHOTON_LIMIT = 8.8e-12   # ph/cm^2/s, faintest 8-yr catalog source
FERMI_ENERGY_LIMIT = 1.0e-15   # W/m^2, point-source energy-flux limit
RUBIN_OPTICAL_LIMIT = 6.0e-19  # W/m^2, LSST single visit r=24.7

# planet optical flux anchored to calibration note §8:
# 1 Mearth, 500 AU, albedo 0.3 -> 7e-18 W/m^2
PLANET_OPT_ANCHOR = 7.0e-18    # W/m^2
PLANET_OPT_D0 = 500.0          # AU

# ---- wrapper interface (redesigned 2026-10-13) ----
VALID_KINDS = ("planet", "pbh_freezein", "pbh_wimp")
DOMAIN_D_MIN_AU = 150.0        # benchmark-validated distance domain (90-case
DOMAIN_D_MAX_AU = 1000.0       # benchmark: 150-1000 AU). Outside it, verdicts
                               # carry an explicit domain_warning (extrapolated,
                               # not silently trusted).
_SIGMAV_BY_KIND = {"pbh_freezein": SIGMAV_CH, "pbh_wimp": SIGMAV_WIMP}


def compute_pbh_gamma_halo_flux(distance_au, sigmav_cm3_s=SIGMAV_CH,
                                m_chi_gev=M_CHI_GEV):
    """PBH DM-spike annihilation flux at Earth.

    Scholtz & Unwin 2019 eqs (5)/(10)/(11). Spike anchored at
    matter-radiation equality. Rate is MASS-INDEPENDENT in the
    no-plateau regime (valid for freeze-in; see note §7).
    """
    Gamma = 1e20 * (sigmav_cm3_s / SIGMAV_CH) * (100.0 / m_chi_gev) ** 2  # s^-1
    kappa1, kappa2 = 10.0, 1.0
    d_m = distance_au * AU_M
    d_cm = distance_au * AU_CM
    photon_flux = kappa1 * Gamma / (4.0 * math.pi * d_cm ** 2)      # ph/cm^2/s
    m_j = m_chi_gev * GEV_TO_J
    energy_flux = kappa2 * Gamma * m_j / (4.0 * math.pi * d_m ** 2)  # W/m^2
    return {"photon_flux_cm2_s": photon_flux,
            "flux_w_m2": energy_flux,
            "annihilation_rate_s": Gamma}


def compute_planet_optical_flux(mass_earth, distance_au, albedo=0.3):
    """Reflected-sunlight flux at Earth for a distant planet.

    Anchored to 7e-18 W/m^2 at (1 Mearth, 500 AU, albedo 0.3).
    Radius from R ~ M^0.27 (rocky); flux ~ albedo * R^2 / d^4
    (d ~= geocentric distance for outer solar system).
    """
    r_ratio = mass_earth ** 0.27
    flux = (PLANET_OPT_ANCHOR * (albedo / 0.3) * r_ratio ** 2
            * (PLANET_OPT_D0 / distance_au) ** 4)
    return flux


def classify(kind, mass_earth=None, distance_au=None, albedo=0.3,
             optical_flux_w_m2=None, gamma_photon_flux=None,
             gamma_energy_flux=None, sigmav_pbh=None, m_chi_gev=M_CHI_GEV):
    """Per-hypothesis detectability verdict for a stage-1-recovered body.

    kind (REQUIRED): the object hypothesis under test —
        "planet" | "pbh_freezein" | "pbh_wimp".
        The wrapper NEVER infers object type from mass alone (2026-10-13 fix:
        the old wrapper did, and confidently mislabeled a black hole "planet").

    mass_earth, distance_au: recovered body parameters (mass in Earth masses,
        distance in AU). Mass is unused for PBH kinds (gamma rate is
        mass-independent in the no-plateau regime); accepted and ignored.

    Explicit fluxes (optical_flux_w_m2, gamma_photon_flux, gamma_energy_flux):
        real observational constraints at the recovered location, when
        available. Override the computed model fluxes; recorded in
        detail["flux_source"]. This is how a Rubin non-detection or a real
        Fermi limit enters the pipeline.

    Returns (verdict, detail dict). Verdicts are DETECTABILITY PREDICTIONS
    for the stated hypothesis, NOT object classifications:
      "detectable" — this hypothesis predicts a signal above the survey floor
      "ambiguous"  — below floor / non-discriminating: the hypothesis is
                     neither confirmed nor ruled out by these channels
    """
    if kind not in VALID_KINDS:
        raise ValueError(
            "kind must be one of %s; got %r. The wrapper never infers "
            "object type from mass alone." % (VALID_KINDS, kind))
    detail = {"kind": kind, "flux_source": {}, "notes": []}
    if (distance_au is not None
            and not (DOMAIN_D_MIN_AU <= distance_au <= DOMAIN_D_MAX_AU)):
        detail["domain_warning"] = (
            "distance %.3g AU outside benchmark-validated domain "
            "(%.0f-%.0f AU); verdict is extrapolated, not silently trusted"
            % (distance_au, DOMAIN_D_MIN_AU, DOMAIN_D_MAX_AU))

    if kind == "planet":
        if optical_flux_w_m2 is not None:
            f_opt, src = optical_flux_w_m2, "observed"
        else:
            if mass_earth is None or distance_au is None:
                raise ValueError(
                    "kind='planet' needs mass_earth and distance_au "
                    "(or explicit optical_flux_w_m2)")
            f_opt = compute_planet_optical_flux(mass_earth, distance_au,
                                                albedo)
            src = "computed"
        detail["flux_source"]["optical"] = src
        detail["optical_flux_w_m2"] = f_opt
        detail["optical_detected"] = bool(f_opt > RUBIN_OPTICAL_LIMIT)
        # A planet has no annihilating DM spike: gamma is not applicable.
        detail["gamma_photon_flux"] = 0.0
        detail["gamma_energy_flux"] = 0.0
        detail["gamma_detected"] = False
        detail["notes"].append(
            "planet hypothesis: no DM-spike gamma expected; gamma channel "
            "not applicable")
        if detail["optical_detected"]:
            verdict = "detectable"
        else:
            verdict = "ambiguous"
            detail["notes"].append(
                "below Rubin optical floor: planet hypothesis neither "
                "confirmed nor ruled out")
    else:
        # PBH kinds: optical reflected flux is identically ZERO — a black
        # hole reflects no sunlight. THIS is the 2026-10-13 fix: the old
        # wrapper computed mass->optical-flux here and labeled BHs "planet".
        if optical_flux_w_m2 is not None:
            detail["notes"].append(
                "explicit optical flux ignored for PBH kind "
                "(black hole reflects no sunlight)")
        detail["optical_flux_w_m2"] = 0.0
        detail["optical_detected"] = False
        detail["flux_source"]["optical"] = "forced-zero (black hole)"
        sv = sigmav_pbh if sigmav_pbh is not None else _SIGMAV_BY_KIND[kind]
        if gamma_photon_flux is not None and gamma_energy_flux is not None:
            g_ph, g_en, gsrc = gamma_photon_flux, gamma_energy_flux, "observed"
        else:
            if distance_au is None:
                raise ValueError(
                    "kind=%r needs distance_au (or explicit gamma fluxes)"
                    % (kind,))
            g = compute_pbh_gamma_halo_flux(distance_au, sv, m_chi_gev)
            g_ph, g_en = g["photon_flux_cm2_s"], g["flux_w_m2"]
            gsrc = "computed"
        detail["flux_source"]["gamma"] = gsrc
        detail["gamma_photon_flux"] = g_ph
        detail["gamma_energy_flux"] = g_en
        gam_det = bool(g_ph > FERMI_PHOTON_LIMIT or g_en > FERMI_ENERGY_LIMIT)
        detail["gamma_detected"] = gam_det
        if gam_det:
            verdict = "detectable"
            if kind == "pbh_wimp":
                detail["notes"].append(
                    "WIMP-level gamma; thermal-WIMP spike scenario already "
                    "excluded by diffuse gamma bounds")
        else:
            verdict = "ambiguous"
            detail["notes"].append(
                "gamma below Fermi reach: PBH hypothesis non-discriminating "
                "here (a freeze-in PBH is gamma-dark at this distance)")

    detail["verdict_semantics"] = (
        "detectability prediction for the stated hypothesis, NOT an object "
        "classification")
    return verdict, detail


def classify_all(mass_earth, distance_au, **kwargs):
    """Evaluate every object hypothesis for a recovered body.

    Pipeline-facing replacement for the old classify(mass, distance).
    Returns {kind: (verdict, detail)} with per-hypothesis detectability
    verdicts. Combining hypotheses with real observations (e.g. a Rubin
    non-detection at the recovered location ruling out the planet
    hypothesis) is the pipeline's job, not the classifier's.
    """
    return {k: classify(k, mass_earth=mass_earth, distance_au=distance_au,
                        **kwargs)
            for k in VALID_KINDS}
