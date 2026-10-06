# Independent verification: Vela January 2000 glitch fast-rise claim
**Date:** 2026-10-03 · **Verifier:** independent subagent (fresh read, no trust in prior characterization)
**Paper:** Dodson, McCulloch & Lewis 2002, ApJL 564, L85 — read verbatim from arXiv:astro-ph/0111404
(preprint of the refereed paper; abstract text identical to the published version per IOP listing).

## Verbatim extracts (the load-bearing sentences)

**Rise-time constraint** (§3, Timing fits):
> "The observations are consistent with an instantaneous change in period;
> modelling has shown that a spin-up timescale of forty seconds would produce
> a three sigma signal."

(§4, Future development): "The parallel single pulse system designed to
observe this has a three σ detection limit of less than 40 seconds."

**Four timescales** (Abstract):
> "Four relaxation timescales are found, which are believed to be due to the
> variable coupling between the crust and the interior fluid. One is very
> short, about 60 s; the others have been previously reported and are 0.56,
> 3.33, and 19.1 days in length."

(§3): "The fast decay timescale, not previously observed (or observable) is
shown separated from the other effects in figure 1."

**Table 1 fit** (τ_n, Δν_n in 10⁻⁶ Hz; errors are 1σ):
> "1.2 ± 0.2 mins   0.020(5) / 0.53(3) days   0.31(2) / 3.29(3) days
> 0.193(2) / 19.07(2) days   0.2362(2)"

**Cadence that made it resolvable** (§2):
> "The de-dispersed bandpass is sampled at 2 kHz and recorded directly onto
> disk for later retrieval, while an 'on the fly' monitoring system folds on
> a ten second basis for which the RMS is 85µs. These arrival times are
> monitored and if a glitch is detected a warning is issued and the single
> pulse data are retained."
> Observations at 635, 990, 1390 MHz; 14-m antenna, Mt Pleasant Observatory.
> Glitch auto-detected; IAU telegram within 12 h. Δν/ν = 3.1×10⁻⁶,
> "the largest recorded for this pulsar."

**Crab contrast** (§4):
> "This is in contrast to the observations made on the Crab (Wong, Backer,
> & Lyne 2001) where the spin-up timescale has been observed to take about
> ∼ 0.5 of a day."

**How the fast term was isolated** (§3):
> "We have subtracted the terms found by TEMPO in the 2 minute data from the
> single pulse data folded for 10 seconds... We see a positive excursion,
> indicating that the true glitch epoch was later, and is followed by a rapid
> decay. We have fitted a linear rise (ΔνΔt) followed by a forth decay term
> to this."

## Comparison table

| # | Our note's claim | Paper verbatim | Verdict |
|---|---|---|---|
| 1 | Rise ≤ 40 s (3σ detection limit) | "a spin-up timescale of forty seconds would produce a three sigma signal"; "three σ detection limit of less than 40 seconds" | **CONFIRMED** |
| 2 | Four relaxation timescales incl. fast ~60 s, "not previously observed" | Abstract: "about 60 s"; §3: "not previously observed (or observable)"; longer three 0.56/3.33/19.1 d | **CONFIRMED** (see correction A) |
| 3 | Fast term previously unrecognized | Paper explicitly reports it as new | **CONFIRMED as new-to-our-census, not new-to-science** — the paper itself claims the discovery; what was "unrecognized" was only our own Q2 note's failure to fold it in |
| 4 | Naive B_eff ≈ 2.37×10⁻⁴ from τ≈60 s | Paper computes no B (our derivation) | **Arithmetic CONFIRMED** given B=1/(2πντ), ν=11.19 Hz, τ=60 s → 2.37×10⁻⁴; see correction B |
| 5 | Rise bound → B ≳ 3.6×10⁻⁴ (naive) | Our derivation from the 40 s limit | **Arithmetic CONFIRMED**: 1/(2π×11.19×40) = 3.55×10⁻⁴ |
| 6 | Hobart 14-m, single-pulse, 10-s folds, 3 freqs | §2 verbatim above | **CONFIRMED** |
| 7 | Paper contrasts <40 s with Crab ~0.5 d | §4 verbatim above | **CONFIRMED** |

## Corrections (minor — conclusions unchanged)

**A. The fast term is 1.2±0.2 min (72±12 s), not 60 s.** Our note wrote
"(The ASP-proceedings version tabulates the fast term as 1.2±0.2 min; the
refereed ApJL version says 'about 60 seconds' — cited here is the ApJL
value.)" That framing is wrong: the "about 60 seconds" (abstract) and the
"1.2±0.2 min" (Table 1) are in the *same* paper — the abstract rounds the
fit. There is no version discrepancy. The precise fitted value is 72±12 s;
60 s is the abstract's rounding (exactly 1σ below the fit central value).

**B. B_eff with the fitted value is ≈2.0×10⁻⁴, not 2.37×10⁻⁴.**
1/(2π×11.1946×72) = 1.98×10⁻⁴. Our note used the rounded 60 s. Both are
within ~2× of the microphysical ~4×10⁻⁴, so the "same friction number as
2016" conclusion is unaffected — but the honest number from the fit is
~2.0×10⁻⁴ (2000) vs ~2.6×10⁻⁴ (2016, τ=54 s), still mutually consistent
within the fit errors.

## Caveats the paper raises that our note omitted

1. **Large fractional errors on the fast term:** Δν_n = 0.020(5)×10⁻⁶ Hz
   (25%) and τ = 1.2±0.2 min (17%). Our note quotes "~60 s" with no
   uncertainties; the fast-term amplitude is the least well-determined of
   the four.
2. **The fast term comes from a dedicated sub-fit**, not the main TEMPO
   solution: a linear rise plus fourth decay fitted to 10-s single-pulse
   residuals after subtracting the TEMPO terms. This is methodologically
   sound but means the fast term's errors are not independent of the
   subtraction.
3. **The 40 s is a non-detection limit from modeling**, not a measured rise —
   our note does call it a "detection limit" in the census table, so this is
   correctly handled, but worth restating: the paper is consistent with an
   *instantaneous* spin-up.
4. The longer three terms match Alpar et al. 1993 / Flanagan 1990 in
   approximately equal ratios (5.9, 5.7) — the paper's own framing ties them
   to vortex-creep models, consistent with our slow-branch assignment.

## Verdict

**CONFIRMED.** Every load-bearing number in our note's Vela-2000 entry traces
to verbatim statements in Dodson, McCulloch & Lewis 2002: the 40 s 3σ rise
limit, four timescales with a previously-unobserved fast term, the
instrumental setup, and the Crab contrast. Two minor precision corrections:
quote the fitted 1.2±0.2 min (72±12 s) rather than the abstract's "about 60
s," and the corresponding naive B_eff ≈ 2.0×10⁻⁴ rather than 2.37×10⁻⁴.
Neither changes the conclusion — two independent Vela glitches, 16 years
apart, show a ~1-minute fast relaxation giving the same friction number
within ~2× of theory. The "new catch" framing should read "new to our
census": the paper itself announced the fast term in 2002.
