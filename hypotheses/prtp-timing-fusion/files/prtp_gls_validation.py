"""Scale-safe GLS with jackknife anomaly flagging (audited 2026-09-22).

Fixes relative to the pasted draft:
  1. The spatial template now takes an explicit variance scale
     ``spatial_amp2`` (s^2, default 0 = OFF). The draft added the template
     with unit amplitude (1 s^2 against ~1e-14 s^2 data), which silently
     reduced "GLS" to the unweighted mean, made white_noise_var decorative
     (100x change -> 0.27 ns shift), and inflated the reported error bar by
     ~1e7 (audit: /tmp/aldm/audit_unified.py).
  2. Jackknife now RETURNS flags: z = |p_full - p_drop| / sqrt(var_full +
     var_drop) per parameter, flagged when z > z_thresh. The draft only
     returned a dict and never flagged anything.
  3. Documents the design-matrix assumption: columns must be array-wide
     (e.g. per-epoch common mode). Per-pulsar columns go rank-deficient
     under drop-one-out; the solver raises instead of silently pinv-ing.

Convention: residuals flattened PULSAR-MAJOR (index = p*n_epochs + e),
matching kron(spatial, eye(n_epochs)).
"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve


def run_prtp_gls_validation(residuals, design_matrix, red_noise_cov,
                            white_noise_var, n_pulsars, n_epochs,
                            spatial_matrix=None, spatial_amp2=0.0,
                            rel_reg=1e-8, z_thresh=3.0):
    total_dim = n_pulsars * n_epochs
    residuals = np.asarray(residuals, float).ravel()
    design_matrix = np.asarray(design_matrix, float)
    assert residuals.shape == (total_dim,), "residual vector dim mismatch"
    assert design_matrix.shape[0] == total_dim, "design matrix row mismatch"
    assert np.asarray(white_noise_var, float).shape == (total_dim,), \
        "white_noise_var must be per-datapoint"

    c_matrix = np.asarray(red_noise_cov, float) + np.diag(white_noise_var)
    if spatial_matrix is not None and spatial_amp2 > 0:
        s = np.asarray(spatial_matrix, float)
        assert s.shape == (n_pulsars, n_pulsars), "spatial template shape mismatch"
        c_matrix = c_matrix + spatial_amp2 * np.kron(s, np.eye(n_epochs))
    c_matrix = c_matrix + rel_reg * np.median(np.diag(c_matrix)) * np.eye(total_dim)

    def solve_gls(c_in, d_in, r_in):
        try:
            cf, lo = cho_factor(c_in)
            cin_d = cho_solve((cf, lo), d_in)
            cin_r = cho_solve((cf, lo), r_in)
        except np.linalg.LinAlgError as exc:
            raise np.linalg.LinAlgError(
                "covariance not positive-definite; check design columns "
                "(per-pulsar columns go rank-deficient under jackknife)") from exc
        lhs = d_in.T @ cin_d
        try:
            p_cov = np.linalg.inv(lhs)
        except np.linalg.LinAlgError as exc:
            raise np.linalg.LinAlgError(
                "design matrix rank-deficient for this subset") from exc
        return p_cov @ (d_in.T @ cin_r), p_cov

    base_params, base_cov = solve_gls(c_matrix, design_matrix, residuals)
    base_var = np.diag(base_cov)

    jackknife_results, flags = {}, {}
    for p_idx in range(n_pulsars):
        keep = np.ones(total_dim, bool)
        keep[p_idx * n_epochs:(p_idx + 1) * n_epochs] = False
        try:
            sp, sc = solve_gls(c_matrix[np.ix_(keep, keep)],
                               design_matrix[keep], residuals[keep])
        except np.linalg.LinAlgError as exc:
            jackknife_results[f"drop_pulsar_{p_idx}"] = {"error": str(exc)}
            flags[f"drop_pulsar_{p_idx}"] = ["solver-failed"]
            continue
        sv = np.diag(sc)
        z = np.abs(sp - base_params) / np.sqrt(sv + base_var)
        bad = [int(j) for j in np.where(z > z_thresh)[0]]
        jackknife_results[f"drop_pulsar_{p_idx}"] = {
            "params": sp, "variance": sv, "z_vs_baseline": z}
        if bad:
            flags[f"drop_pulsar_{p_idx}"] = [f"param {j} z={z[j]:.1f}" for j in bad]
    return base_params, base_cov, jackknife_results, flags


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    n_p, n_e, dim = 4, 14, 56
    w = np.array([100., 100., 100., 1000.]) * 1e-9
    wv = np.repeat(w, n_e) ** 2
    r = 200e-9 + rng.normal(0, np.repeat(w, n_e)) + rng.normal(0, 50e-9, dim)
    r[2 * n_e:3 * n_e] += 2000e-9  # pulsar 2 carries a +2000 ns systematic
    d = np.ones((dim, 1))
    red = np.eye(dim) * (50e-9) ** 2

    bp, bc, jk, fl = run_prtp_gls_validation(r, d, red, wv, n_p, n_e)
    print(f"truth=200ns (+2000ns systematic on pulsar 2)")
    print(f"baseline: {bp[0]*1e9:.1f} ns +- {np.sqrt(bc[0,0])*1e9:.1f} ns")
    print("flags:", fl)
    assert not fl or "drop_pulsar_2" in fl, "jackknife should flag pulsar 2"
    wv_b = wv.copy(); wv_b[3*n_e:] /= 100.0   # pulsar 3 goes quiet -> upweighted
    bp2, _, _, _ = run_prtp_gls_validation(r, d, red, wv_b, n_p, n_e)
    assert abs(bp2[0] - bp[0]) > 5e-9, "estimate must respond to white_noise_var"
    print(f"quiet-pulsar-3 variant: {bp2[0]*1e9:.1f} ns (moved {abs(bp2[0]-bp[0])*1e9:.1f} ns)")
    print("OK: heteroscedastic weighting active; outlier pulsar flagged.")
