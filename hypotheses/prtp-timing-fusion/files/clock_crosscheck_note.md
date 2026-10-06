# Clock-file cross-check — tech note (2026-09-24)

## Question
The three-way fit ranked "clock-like epoch-uncorrelated common variance"
(BIC 188.4, sigma_c = 181 ns) as the best statistical description of the
~350 ns common monopole. Can the actual NANOGrav clock-correction chain
produce it? The correction files live in the workspace
(`nanograv15yr/extracted/clock/`), so this is directly testable.

## Method
Parsed the three correction files PINT applies to the TOAs:

| file | content | sampling | units |
|---|---|---|---|
| `ao2gps.clk` | UTC(Arecibo) − UTC(GPS) | daily | s |
| `gbt2gps.clk` | UTC(GBT) − UTC(GPS) | daily | s |
| `tai2tt_bipm2019.clk` | TAI → TT(BIPM2019) | 10-day | s |

Logic: corrections are *applied* to TOAs, so residuals carry *errors* in
these files, not the corrections themselves. A clock-file error would show
as (a) jumps/gaps/flags in the file near the 14 common epochs
(MJD 57212–58952), and (b) an **observatory-coherent** residual signature:
GBT-clock errors move J0437+J1909 together (B1937 partly), AO-clock errors
move B1855 (+B1937 partly), TT(BIPM) errors move all four (true monopole).
Checked per-pulsar epoch-to-epoch moves at every relevant transition
against that prediction.

Observatory mapping (from `*.nb.pars.txt` backend tags):
J0437-4715 GBT-only (YUPPI); J1909-3744 GBT-only (YUPPI);
B1937+21 mixed AO (ASP/PUPPI) + GBT (GASP/GUPPI); B1855+09 AO-only (ASP/PUPPI).

## Results

**1. Global time standard: exonerated.**
`tai2tt_bipm2019.clk` is perfectly smooth across the whole window: median
step 0.3 ns, zero jumps above threshold, no gaps beyond its regular 10-day
sampling. A ~350 ns global clock jump did not happen. The true-monopole-via-
time-standard variant is ruled out.

**2. Observatory clock files: events exist, none match.**
- `gbt2gps.clk`: −2807 ns jump at MJD 57931.5, a cluster (+186/+101/−95 ns)
  at 57942–57959, −691 ns at 58200.5, −101 ns at 58948.5, one 17-day gap.
  Median step 3 ns otherwise.
- `ao2gps.clk`: +99/+176 ns pair at 58483/58484, −362/+351 ns glitch pair at
  58953/58955, a 32-day gap at 58864–58896 (contains epoch 12 = 58892).
  Median step 1 ns otherwise. No bad-data flags in the epoch window
  (the 24 flagged notes are all 1999-era NIST-REF comments).

**3. The per-pulsar moves are not observatory-coherent — the sharp test.**
Common-mode big transitions and what each pulsar did (mean-subtracted, ns):

- ep 2→3 (57272→57782, common −491): J0437 **+215**, J1909 **−631**,
  B1937 +4410, B1855 +238. The two GBT pulsars move in *opposite*
  directions — impossible for a GBT clock error.
- ep 6→7 (57902→58622, across the 720-d gap holding the GBT −2807 ns
  event): J0437 +568, J1909 +117, B1937 +3639, B1855 +923. Same sign but
  5× apart within the GBT pair; the AO-only B1855 moves more than either
  GBT pulsar. No GBT-coherent step, and no µs-level trace of the −2807 ns
  file event — the file handled it (or the jump was real and correctly
  removed, as designed).
- ep 7→8 (58622→58652, common +166): J0437 −242, B1937 −275,
  B1855 −232 move together **across both observatories**, while J1909 —
  the pulsar carrying 89% of the common-mode weight — sits at +22.
- ep 12→13 (58892→58952, spanning the AO glitch pair): +53, +3, −283,
  +325 — no coherent AO injection; the −362/+351 ns pair nets out over
  the 30-day bin.

No clock-file event coincides in time *and* observatory pattern with any
common-mode jump.

## Interpretation
**The clock hypothesis is disfavored — a clean negative result.**
The leading candidate from the BIC ranking fails its most direct testable
form: the global time standard is smooth, and the observatory clock chains
show no fault capable of producing the jumps (their recorded jumps were
corrected for, and the residuals show no observatory-coherent signature).

"Clock-like" therefore remains a *statistical signature* (epoch-
uncorrelated common variance), not an identification. Remaining
possibilities, in rough order of plausibility:
(a) array-wide *processing/pipeline* systematics (version changes, RFI
environment — naturally epoch-uncorrelated and not observatory-respecting);
(b) red-noise-model mis-specification interacting with the two big data
gaps — note the three level groups (+300 / −200 / ~0 ns) break exactly at
the 510-d and 720-d gaps; jumps happen *across* gaps, never *within* a
well-sampled block;
(c) fitting artifact: with 89% of the common-mode weight on J1909 and only
4 pulsars, J1909's own epoch-uncorrelated variance is partly relabeled
"common";
(d) an unmodeled common physical process (no candidate on the table).

## Caveats
- Only 4 pulsars; J1909 dominates the common-mode weights (89%).
- Assumes *recorded* file jumps are approximately correct — a file that
  mis-records a jump is indistinguishable from a correct file in isolation,
  but it would leave an observatory-coherent residual step, which is not
  seen.
- One untestable corner: a *GPS-system-wide* error would corrupt both
  observatories' "X vs GPS" comparisons in common. GPS is monitored at the
  ~10 ns level; a 350 ns common GPS error is extraordinary and there is
  zero positive evidence for it. Noted, not live.
- Archival-data analysis. Not a clock-error, ULDM, ephemeris, or
  gravitational-wave detection.

## Files
- `~/workspace/prtp/hidden_files/clock_crosscheck.py` — parser + jump/gap scan
- `~/workspace/prtp/hidden_files/clock_crosscheck_results.json` — full results
- `~/workspace/prtp/hidden_files/clock_crosscheck_note.md` — this note
