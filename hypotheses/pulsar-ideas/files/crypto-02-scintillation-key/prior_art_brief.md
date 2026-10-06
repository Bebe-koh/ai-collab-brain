# Crypto idea #2 — prior-art brief (2026-10-06)
Idea: two receivers generate a *private* shared key from a pulsar signal — intrinsic single-pulse structure (public) plus location-dependent interstellar scintillation (the private channel).

## Prior art found (2026-10-06 web search)

**1. Dawson et al. 2022, arXiv:2201.05763 — "Physical Publicly Verifiable Randomness from Pulsars"**
Demonstrated publicly verifiable randomness (PVR) from pulsar flux densities, extracted identical bit sequences at Parkes (Australia) and FAST (China), sequences passed NIST tests. Also notes Cordes privately explored pulsar-derived mutually-verified randomness for 1970s arms-limitation verification (never published).
*Relevance: the two-receiver shared-extraction half of our idea is proven. But PVR is the opposite security goal — everyone with a dish gets the same bits. Their protocol streams de-dispersed flux openly.*

**2. arXiv:2502.18430 (2025) — "Random Number Generation from Pulsars"**
Timing-variation RNG with a formal extractor: Leftover Hash Lemma + SHAKE-256, empirical min-entropy table for 10 pulsars (NANOGrav + EPTA, 0.68–0.97 bits/bit).
*Relevance: the debiasing/extraction machinery a key-generation protocol would need already exists with measured numbers.*

**3. LOFAR multistation scintillation of PSR B0655+64, MNRAS (stag1534, published ~Oct 2026)**
Four LOFAR stations simultaneously measured the same scintillation pattern with baseline-dependent time delays; joint modeling recovered screen parameters.
*Relevance: direct proof that two separated receivers share the scintillation channel — the empirical basis for the private half of the idea. This paper is brand new.*

**4. Private shared key from location-dependent scintillation: no prior art found.**
Searches for pulsar-based private key generation / scintillation as a secret channel returned nothing. The novelty wedge is real.

## The feasibility structure (what the full workup must answer)

- **Intrinsic pulse structure contributes zero secrecy.** Every observer with a sensitive enough dish sees the same emission (after de-dispersion). The entire secret must come from the *scintillation modulation*, which is location-dependent.
- **The decisive number is the diffractive spatial coherence scale (b_iso).** Two legitimate receivers must sit well inside it (correlated pattern); the adversary must be outside it (decorrelated pattern). DISS scales range ~10^8–10^11 cm depending on pulsar/frequency/geometry — for many pulsars this is Earth-scale, which is *bad* for the adversary model. The workup's core calculation: find pulsars/frequencies where b_iso lands in the tens-to-hundreds-of-km window, making "parties in, adversary out" physically plausible.
- **Key rate is bounded by scintillation, not pulses.** Secret bits ≈ independent scintles ≈ (T/Δt_d)·(BW/Δν_d). Example: B1937+21 (FAST: Δt_d≈7.67 min, Δν_d≈0.56 MHz) → 1 hr × 100 MHz ≈ ~1,400 scintles → order of ~1 kbit/hr. Fine for key-refresh, not for bulk encryption.
- **The protocol pipeline is standard physical-layer key generation** (advantage distillation → information reconciliation → privacy amplification). Dawson's BER/reconciliation analysis for PVR transfers directly.
- **Adversary model honesty:** security is geographic-exclusion, not computational. A well-resourced adversary with their own dish *inside* the coherence footprint defeats it. The real moat is the cost of radio-telescope infrastructure, which is a weaker claim than "unbreakable" — the workup must not oversell it.

## Verdict on "is it worth it" (preliminary, pending Jase's go on the full workup)
Not dead on arrival. The shared-extraction half is published, the private-channel half (multistation scintillation) was just demonstrated in October 2026, and the private-key application appears novel. The kill risk concentrates in one checkable number: whether any good pulsar gives a spatial coherence scale that admits the legitimate geometry while excluding a plausible adversary. That single calculation is the right first step.
