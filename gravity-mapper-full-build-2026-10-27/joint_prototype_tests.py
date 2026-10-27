#!/usr/bin/env python3
"""Joint-interface prototype tests (D9 prototype, NEW FILE).

Order is load-bearing: the k=0 regression proof runs FIRST against
the pre-declared D11 bar in joint_prototype_plan_2026-10-26.md. If
it fails, this script writes proof-only results and exits non-zero
BEFORE any demo run. The demo runs only on a passed proof.
No live ROM contact, no existing-file edits, no rom_closure import.
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'real_data'))
from secular_elements import elements_to_cart, MU_SUN
from rails_brain import PlanetRails
from particle_brain import NBodyParticle
from optimizer_brain import fit_state
from joint_model_spec import JointSpec
from joint_driver import JointParticle, make_particle, fit_model
from joint_checker import check_model

TRACER = {'a': 40.0, 'e': 0.1, 'i': 0.087, 'Omega': 1.2, 'omega': 3.5,
          'M': 5.0}
TS = np.linspace(5.0, 20.0, 60)
T_REF = 5.0
SIGMA = 7.04e-5
NOISE_SEED = 12345
RAILS_CACHE = os.path.join(HERE, 'sealed_runs', 'planet_rails.npz')
# D11 (from the plan, set before runs): rel RMS <= 1e-4, rel a <= 1e-4,
# abs e <= 1e-4, success flags agree.
D11 = {'rel_rms_max': 1.0e-4, 'rel_a_max': 1.0e-4, 'abs_e_max': 1.0e-4}
# D10 (from the plan): scan offsets [0,-1,+1,-2,+2] decades, bounds
# inventor +/- 3 decades (implemented in JointSpec / joint_driver).


def tracer_x0():
    r, v = elements_to_cart(TRACER, mu=MU_SUN)
    return np.concatenate([r, v])


def noisy_obs(clean):
    rng = np.random.default_rng(NOISE_SEED)
    return clean + rng.normal(0.0, SIGMA, clean.shape)


def main():
    results = {'plan': 'joint_prototype_plan_2026-10-26.md',
               'd11': D11, 'd10_scan_offsets_decades': [0, -1, 1, -2, 2],
               'd10_bounds_decades': 3,
               'live_rom_contact': False,
               'existing_files_modified': [],
               'rom_closure_imported': 'rom_closure' in sys.modules,
               'hardware': 'Linux VM (this session)'}
    rails = PlanetRails.build(0.0, 27.0, dt_days=0.5,
                              cache_path=RAILS_CACHE)
    x0 = tracer_x0()

    # ---- k=0 regression proof (D11) ----
    ref = NBodyParticle(rails)
    clean0 = ref.predict(x0, TS, T_REF)
    assert clean0 is not None, "reference k=0 propagation failed"
    obs0 = noisy_obs(clean0)
    t0 = time.perf_counter()
    ref_fit = fit_state(TS, obs0, ref.predict, t_ref=T_REF,
                        n_starts=3, seed=0, early_stop_rms=2.0 * SIGMA)
    ref_wall = time.perf_counter() - t0
    spec0 = JointSpec([], rails, T_REF)
    joint0 = make_particle(spec0)
    t0 = time.perf_counter()
    joint_fit = fit_model(TS, obs0, spec0, joint0, n_starts=3, seed=0,
                          early_stop_rms=2.0 * SIGMA)
    joint_wall = time.perf_counter() - t0
    rel_rms = abs(joint_fit['rms_au'] - ref_fit['rms_au']) / ref_fit['rms_au']
    rel_a = abs(joint_fit['a'] - ref_fit['a']) / ref_fit['a']
    abs_e = abs(joint_fit['e'] - ref_fit['e'])
    state_diff = float(np.max(np.abs(
        np.array(joint_fit['r0_au'] + joint_fit['v0_au_yr'])
        - np.array(ref_fit['r0_au'] + ref_fit['v0_au_yr']))))
    proof_pass = bool(
        ref_fit.get('success') and joint_fit.get('success')
        and rel_rms <= D11['rel_rms_max']
        and rel_a <= D11['rel_a_max'] and abs_e <= D11['abs_e_max'])
    results['k0_proof'] = {
        'reference': {'success': bool(ref_fit.get('success')),
                      'rms_au': float(ref_fit['rms_au']),
                      'a': float(ref_fit['a']), 'e': float(ref_fit['e']),
                      'nfev': int(ref_fit.get('nfev', -1)),
                      'best_start': int(ref_fit.get('best_start', -1)),
                      'wall_s': float(ref_wall)},
        'joint': {'success': bool(joint_fit.get('success')),
                  'rms_au': float(joint_fit['rms_au']),
                  'a': float(joint_fit['a']), 'e': float(joint_fit['e']),
                  'nfev': int(joint_fit.get('nfev', -1)),
                  'best_start': int(joint_fit.get('best_start', -1)),
                  'wall_s': float(joint_wall)},
        'rel_rms_diff': float(rel_rms), 'rel_a_diff': float(rel_a),
        'abs_e_diff': float(abs_e),
        'state_max_abs_diff': state_diff,
        'state_diff_note': 'reported verbatim, not gated (see plan)',
        'pass': proof_pass}
    print(f"[k0 proof] ref rms={ref_fit['rms_au']:.6e} "
          f"joint rms={joint_fit['rms_au']:.6e} rel_rms={rel_rms:.3e} "
          f"rel_a={rel_a:.3e} abs_e={abs_e:.3e} "
          f"state_diff={state_diff:.3e} PASS={proof_pass}", flush=True)
    if not proof_pass:
        results['demo'] = None
        results['stop_reason'] = ('k=0 proof failed D11; demo NOT run '
                                  '(plan stop rule)')
        with open(os.path.join(HERE, 'joint_prototype_results_2026-10-26.json'),
                  'w') as f:
            json.dump(results, f, indent=2)
        print("K0 PROOF: FAIL -- stopping before demo (plan rule)",
              flush=True)
        sys.exit(1)

    # ---- k=1 synthetic demo (sealed truth, pre-declared in plan) ----
    truth_mass, truth_r, truth_phase = 1.0e-4, 8.0, 1.0
    inv_mass, inv_r, inv_phase = 1.0e-5, 8.0, 1.0
    truth_part = JointParticle(rails, [(truth_r, truth_phase)],
                               [(math.log10(truth_mass) - 3,
                                 math.log10(truth_mass) + 3)], T_REF)
    theta_truth = np.concatenate([x0, [math.log10(truth_mass)]])
    clean1 = truth_part.predict(theta_truth, TS, T_REF)
    assert clean1 is not None, "truth k=1 propagation failed"
    obs1 = noisy_obs(clean1)
    spec1 = JointSpec([(inv_r, inv_phase, inv_mass)], rails, T_REF)
    part1 = make_particle(spec1)
    t0 = time.perf_counter()
    fit1 = fit_model(TS, obs1, spec1, part1, n_starts=3, seed=0,
                     early_stop_rms=2.0 * SIGMA)
    fit1_wall = time.perf_counter() - t0
    t0 = time.perf_counter()
    chk1 = check_model(fit1, TS, obs1, spec1, SIGMA, holdout_frac=0.30,
                       seed=0, early_stop_rms=2.0 * SIGMA, n_starts=3)
    chk_wall = time.perf_counter() - t0
    fitted_mass = (fit1['masses_solar'][0]
                   if fit1.get('masses_solar') else float('nan'))
    # Removal test: null train refit inside check_model, same partition.
    # Contribution claim per plan: ratio >= 1.2 with converged null
    # refit; otherwise abstain (unconverged null refit -> abstain).
    ratio = chk1['holdout_mse_ratio']
    if chk1['null_refit_success'] and np.isfinite(ratio) and ratio >= 1.2:
        removal_claim = 'contribution_supported'
    else:
        removal_claim = 'abstain'
    results['k1_demo'] = {
        'truth': {'mass_solar': truth_mass, 'radius_au': truth_r,
                  'phase_rad': truth_phase},
        'inventor': {'mass_solar': inv_mass, 'radius_au': inv_r,
                     'phase_rad': inv_phase},
        'full_fit': {'success': bool(fit1.get('success')),
                     'rms_au': float(fit1['rms_au']),
                     'fitted_mass_solar': float(fitted_mass),
                     'fitted_logmass': (float(fit1['logmasses'][0])
                                        if fit1.get('logmasses') else None),
                     'mass_rel_error': (float(abs(fitted_mass - truth_mass)
                                              / truth_mass)
                                        if np.isfinite(fitted_mass) else None),
                     'logmass_error_decades': (float(fit1['logmasses'][0]
                                                     - math.log10(truth_mass))
                                               if fit1.get('logmasses') else None),
                     'nfev': int(fit1.get('nfev', -1)),
                     'best_start': int(fit1.get('best_start', -1)),
                     'wall_s': float(fit1_wall)},
        'checker': chk1,
        'checker_wall_s': float(chk_wall),
        'removal': {'method': 'refit (null model, same partition); '
                               'frozen removal prohibited',
                    'null_refit_success': bool(chk1['null_refit_success']),
                    'joint_refit_success': bool(chk1['joint_refit_success']),
                    'claim': removal_claim},
        'pragmatic_variant_run': False,
        'pragmatic_note': 'not run; strict refit is the acceptance path'}
    print(f"[k1 demo] fit success={fit1.get('success')} "
          f"rms={fit1['rms_au']:.6e} fitted_mass={fitted_mass:.6e} "
          f"truth_mass={truth_mass:.6e} "
          f"logmass_err={results['k1_demo']['full_fit']['logmass_error_decades']} "
          f"nfev={fit1.get('nfev')} wall={fit1_wall:.1f}s", flush=True)
    print(f"[k1 checker] verdict={chk1['verdict']} gates={chk1['gates']} "
          f"train_rms={chk1['train_rms_au']:.6e} "
          f"holdout_rms={chk1['holdout_rms_au']:.6e} "
          f"null_holdout_rms={chk1['null_holdout_rms_au']:.6e} "
          f"mse_ratio={ratio} start_rule={chk1['start_rule']} "
          f"removal_claim={removal_claim} checker_wall={chk_wall:.1f}s",
          flush=True)

    # ---- cost: predict time vs k (single predict each, same ts) ----
    radii = [8.0, 12.0, 16.0, 20.0]
    phases = [1.0, 2.0, 0.5, 1.5]
    predict_costs = []
    for k in range(4):
        geom = list(zip(radii[:k], phases[:k]))
        p = JointParticle(rails, geom, [(-8.0, -2.0)] * k, T_REF)
        theta = np.concatenate([x0, [-4.0] * k])
        t0 = time.perf_counter()
        out = p.predict(theta, TS, T_REF)
        dt = time.perf_counter() - t0
        assert out is not None, f"k={k} predict failed"
        predict_costs.append({'k': k, 'predict_wall_s': float(dt),
                              'n_predict_calls': p.n_predict_calls})
        print(f"[cost predict] k={k} wall={dt:.3f}s", flush=True)
    results['cost_table'] = {
        'k0_fit': results['k0_proof']['joint'],
        'k0_reference_fit_wall_s': float(ref_wall),
        'k1_full_fit_wall_s': float(fit1_wall),
        'k1_full_fit_nfev': int(fit1.get('nfev', -1)),
        'k1_checker_wall_s': float(chk_wall),
        'k1_joint_refit_wall_s': float(chk1['joint_refit_wall_s']),
        'k1_null_refit_wall_s': float(chk1['null_refit_wall_s']),
        'predict_vs_k': predict_costs,
        'predict_note': 'single predict per k (n=1); full k=2/3 fits '
                        'NOT run (out of demo scope), no extrapolation',
        'nfev_note': 'nfev is the winning start only, as in fit_state'}
    with open(os.path.join(HERE, 'joint_prototype_results_2026-10-26.json'),
              'w') as f:
        json.dump(results, f, indent=2)
    print("JOINT PROTOTYPE TESTS: DONE", flush=True)


if __name__ == '__main__':
    main()
