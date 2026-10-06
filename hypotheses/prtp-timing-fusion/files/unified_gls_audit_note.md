# Audit: pasted `run_prtp_gls_validation` (2026-09-22)

Status: **checked by execution, not by reading.** Three bugs found; fixed
version saved as `prtp_gls_validation.py` (self-testing, all asserts pass).

## Bug 1 (serious): the unit-amplitude spatial template

`c_matrix = red + diag(white) + kron(spatial, I)` adds the template with
**amplitude 1 s^2** against data variances ~1e-14 s^2 -- the exact scale
trap diagnosed twice earlier in this session. Measured consequences
(audit script: /tmp/aldm/audit_unified.py; 4 pulsars x 14 epochs,
heteroscedastic white 100/100/100/1000 ns, truth 200 ns):

- `white_noise_var` is decorative: scaling it 100x moves the estimate
  0.27 ns. GLS weighting -- the entire point -- is destroyed.
- The estimate collapses to the plain unweighted mean (identical to
  2 decimals). "Scale-safe" relative regularization does not help: it
  only pads the diagonal, while the template enters unscaled.
- The reported error bar is garbage: +-267,261,243 ns (0.27 s) on a
  200 ns quantity -- inflated ~1e7 by the template-dominated covariance.

The mock `__main__` test passed only because it asserts nothing; with
no injected signal the degenerate mean looks plausible.

## Bug 2: jackknife never flags anything

The docstring promises automatic anomaly flagging; the code returns a
bare dict with no criterion. Fixed version computes
z = |p_full - p_drop| / sqrt(var_full + var_drop) and flags z > 3.

## Bug 3 (latent): per-pulsar design columns

`design_matrix[keep_mask]` drops rows but not parameter columns. With
per-pulsar columns the subset goes rank-deficient and the unconditional
`pinv` silently returns *something*. Fixed version documents the
array-wide-columns assumption and raises instead of silently pinv-ing.

## Fixed version (`prtp_gls_validation.py`)

- `spatial_amp2` (s^2, default 0 = OFF): template scale is explicit.
- Cholesky-based solve; real jackknife flags; convention documented.
- Self-test: 200 ns truth + 2000 ns systematic on pulsar 2 ->
  baseline 827.7 +- 17.2 ns (sane weighting), pulsar 2 flagged at
  z=24.7 (highest; pulsars 0/1 also trip at z~12 because the baseline
  itself contains the systematic -- flags rank suspects, they don't
  convict), heteroscedastic response verified (127 ns move when a
  pulsar's noise level changes).

## Lesson for the corpus

Any GLS helper that accepts a spatial template must take its amplitude
as a separate physical parameter (or fit it). A template added with
implicit unit amplitude is never "plug-and-play" -- it is a scale bug
wearing a docstring.

## Addendum: v2 (`run_prtp_gls_rigorous`) audit (2026-09-22)

**Verified fixed:** heteroscedastic weighting now responds (36.9 ns move
on the probe that caught v1) -- the scale bug is genuinely dead via the
explicit `spatial_variance` parameter. Jackknife fires on the injected
outlier (z=33.6).

**Claim that fails:** "rank deficiencies raise explicit errors rather
than returning silent artifacts." Test with per-pulsar design columns
under drop-one-out completes *silently* -- the `pinv` fallback still
masks rank deficiency exactly as in v1, returning minimum-norm
pseudo-solutions with no warning. The Cholesky branch only guards the
covariance inversion, not the parameter solve.

**Overclaim:** forming `inv(chol.T) @ inv(chol)` explicitly is
numerically *worse* than `cho_solve`, not safer -- explicit inverses
square the condition-number exposure. "Safe Cholesky" is the wrong
adjective for the less stable formulation.

**Minor:**
- z-score normalizes by baseline std only (subset uncertainty ignored)
  and screens only `params[0]` -- multi-parameter designs are
  partially screened.
- Their self-test flags 4/4 pulsars (outlier at z=33.6, clean ones at
  z~11): flagging is sensitive, not specific, when the baseline itself
  contains the systematic. Rank order carries the information.
- Self-test still asserts nothing and uses homoscedastic white noise,
  so it cannot catch a regression of the heteroscedastic-weighting bug
  it was written to fix. A self-test that cannot fail is a demo, not a test.
- Default `spatial_variance=1e-22` silently applies (10 ns)^2 whenever a
  template is passed; default-off (0.0) would force an explicit choice.

Workspace version `prtp_gls_validation.py` already handles all of the
above (raises on rank deficiency, combined-std z-scores, asserting
self-test with heteroscedastic probe).
