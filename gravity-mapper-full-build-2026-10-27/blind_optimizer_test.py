"""Blind optimizer test for Gravity Mapper catalog recovery.

Tests whether grid + local refinement (Nelder-Mead) can recover a hidden body
where brute-force grid search alone failed.

Protocol (sealed-truth):
  1. Load scenario inference manifest + observations (NO truth file access).
  2. Coarse grid search over (mass, radius, phase) on TRAIN MSE (reuses the
     original MASS_GRID / RADIUS_GRID / PHASE_STEPS).
  3. Take top-K coarse candidates; refine each with Nelder-Mead on train MSE.
  4. Best refined candidate validated on HOLDOUT (same 15% gate).
  5. ONLY THEN read sealed truth for scoring.

Run from the source_upload/ directory:
  python3 /path/to/blind_optimizer_test.py
"""
import sys
import math
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent / "source_upload"))

from gravity_mapper.catalog.catalog_recovery import (
    SCENARIO_ID,
    MASS_GRID,
    RADIUS_GRID,
    PHASE_STEPS,
    TRAIN_FRACTION,
    MINIMUM_HOLDOUT_IMPROVEMENT,
    Candidate,
    angle_error,
    load_solver_inputs,
    flatten_observations,
    split_rows,
    score_candidate,
    visible_bodies,
    scenario_paths,
    load_json,
    dominant_truth_object,
)

TOP_K = 12
# refinement bounds: (log10(mass), radius, phase)
BOUNDS = [(-6.0, -2.7), (0.3, 35.0), (0.0, 2.0 * math.pi)]


def candidate_to_x(cand: Candidate):
    return np.array([math.log10(cand.mass_solar), cand.radius_au, cand.phase_rad])


def x_to_candidate(x) -> Candidate:
    mass = 10.0 ** x[0]
    radius = float(x[1])
    phase = float(x[2] % (2.0 * math.pi))
    return Candidate(mass_solar=mass, radius_au=radius, phase_rad=phase)


def main() -> dict:
    inference_manifest, observation_bundle = load_solver_inputs(SCENARIO_ID)
    if observation_bundle["withheld_truth_available_to_solver"] is not False:
        raise RuntimeError("withheld truth exposed to solver")

    all_rows = flatten_observations(observation_bundle)
    train_rows, holdout_rows = split_rows(all_rows)
    bodies = visible_bodies(inference_manifest)

    def train_mse_of(x) -> float:
        return score_candidate(train_rows, inference_manifest, x_to_candidate(x))

    # Stage 1: coarse grid (same as original)
    coarse = []
    for mi, mass in enumerate(MASS_GRID):
        for radius in RADIUS_GRID:
            for pi in range(PHASE_STEPS):
                cand = Candidate(
                    mass_solar=mass,
                    radius_au=radius,
                    phase_rad=2.0 * math.pi * pi / PHASE_STEPS,
                )
                mse = score_candidate(train_rows, inference_manifest, cand)
                coarse.append((mse, cand))
    coarse.sort(key=lambda t: t[0])
    print(f"coarse grid done: {len(coarse)} candidates, "
          f"best train MSE = {coarse[0][0]:.3e}", flush=True)

    # Stage 2: Nelder-Mead refinement from top-K
    refined = []
    for rank, (mse0, cand0) in enumerate(coarse[:TOP_K]):
        res = minimize(
            train_mse_of,
            candidate_to_x(cand0),
            method="Nelder-Mead",
            bounds=BOUNDS,
            options={"maxiter": 400, "xatol": 1e-5, "fatol": 1e-14},
        )
        cand = x_to_candidate(res.x)
        refined.append((res.fun, cand, rank, res.nit, res.success))
        print(f"  refine #{rank}: train MSE {mse0:.3e} -> {res.fun:.3e} "
              f"({res.nit} iters, success={res.success})", flush=True)
    refined.sort(key=lambda t: t[0])
    best_mse, best_cand, best_rank, best_nit, best_ok = refined[0]

    # Stage 3: holdout validation (same gate as original)
    baseline_holdout = score_candidate(holdout_rows, inference_manifest, None)
    cand_holdout = score_candidate(holdout_rows, inference_manifest, best_cand)
    improvement = (baseline_holdout - cand_holdout) / max(baseline_holdout, 1e-30)
    accepted = (improvement >= MINIMUM_HOLDOUT_IMPROVEMENT
                and cand_holdout < baseline_holdout)

    # Stage 4: unseal truth ONLY for scoring
    _, truth_path, _ = scenario_paths(SCENARIO_ID)
    truth = dominant_truth_object(load_json(truth_path))
    mass_err = abs(best_cand.mass_solar - float(truth["mass_solar"])) / float(truth["mass_solar"])
    radius_err = abs(best_cand.radius_au - float(truth["orbital_radius_au"])) / float(truth["orbital_radius_au"])
    phase_err = angle_error(best_cand.phase_rad, float(truth["phase_rad"]))
    recovered = (accepted and mass_err <= 0.50
                 and radius_err <= 0.35 and phase_err <= 0.55)

    result = {
        "scenario_id": SCENARIO_ID,
        "method": "coarse_grid_top12_plus_nelder_mead",
        "coarse_best_train_mse": coarse[0][0],
        "refined_train_mse": best_mse,
        "refined_from_coarse_rank": best_rank,
        "refinement_iters": best_nit,
        "selected_mass_solar": best_cand.mass_solar,
        "selected_radius_au": best_cand.radius_au,
        "selected_phase_rad": best_cand.phase_rad,
        "holdout_improvement_fraction": improvement,
        "accepted": accepted,
        "truth_mass_solar": float(truth["mass_solar"]),
        "truth_radius_au": float(truth["orbital_radius_au"]),
        "truth_phase_rad": float(truth["phase_rad"]),
        "mass_relative_error": mass_err,
        "radius_relative_error": radius_err,
        "phase_absolute_error": phase_err,
        "recovered": recovered,
    }
    out = Path(__file__).resolve().parent / "blind_optimizer_result.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"saved -> {out}")
    print(f"RECOVERED = {recovered}")
    return result


if __name__ == "__main__":
    main()
