"""Experiment D2: can the joint method recover a SYNTHETIC Mercury?

If J1 fails on real data, this diagnoses whether the failure is the method
or the data. Simulate (fitted primary + known Mercury-like secondary) + noise,
then run the blind joint pipeline. If it recovers the synthetic, the method
is sound and real Mercury is just hard. If not, the method needs work.

Blind protocol: the synthetic secondary params are chosen WITHOUT opening
truth (Mercury-like = small mass, ~0.4 AU, arbitrary phase).
"""
import sys, os, math, json
os.chdir('/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/source_upload')
sys.path.insert(0, '.')
sys.path.insert(0, '/home/hatch/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files')
sys.path.insert(0, '/home/hatch/workspace/.jarvis/idea-executions/7edd9420-adb4-42ff-a131-2b931adf2814/scratch')
import numpy as np
from residual_statistic import load_rows
from j1_joint_refine import joint_refine, PRIMARY_0
from null_worker import simulate_null, SIGMA_AU
from gravity_mapper.catalog.catalog_two_body_recovery import (
    Candidate, score, build_system, step_verlet, DT)

# synthetic Mercury: Mercury-LIKE but not from truth (blind-safe)
# mass ~1.7e-7 Msun, radius 0.39 AU, phase arbitrary
SYNTH_MERCURY = Candidate(mass_solar=1.7e-7, radius_au=0.39, phase_rad=1.0)


def simulate_two_body(manifest, template_rows, seed):
    """Simulate (primary + synthetic Mercury) + noise at template times."""
    rng = np.random.default_rng(seed)
    system = build_system(manifest, (PRIMARY_0, SYNTH_MERCURY))
    by_time = {}
    for r in template_rows:
        by_time.setdefault(r['time_years'], []).append(r)
    max_time = max(by_time)
    steps = int(round(max_time / DT))
    sim = {}
    for step in range(steps + 1):
        t = round(step * DT, 10)
        if t in by_time:
            state = {b.object_id: b for b in system}
            for row in by_time[t]:
                b = state[row['object_id']]
                sim[(row['object_id'], row['time_years'])] = (
                    b.x + rng.normal(0, SIGMA_AU),
                    b.y + rng.normal(0, SIGMA_AU))
        if step < steps:
            step_verlet(system)
    return [dict(object_id=r['object_id'], time_years=r['time_years'],
                 x_au=sim[(r['object_id'], r['time_years'])][0],
                 y_au=sim[(r['object_id'], r['time_years'])][1])
            for r in template_rows]


def main():
    manifest, train_rows, holdout_rows = load_rows()
    print("Simulating synthetic two-body data...", flush=True)
    syn_rows = simulate_two_body(manifest, train_rows, seed=777)
    mse1 = score(syn_rows, manifest, (PRIMARY_0,))
    print(f"one-body MSE on synthetic: {mse1:.3e}", flush=True)

    # blind joint pipeline: sequential grid for seeds, then joint refine top
    from residual_statistic import SEC_MASSES, SEC_RADII, SEC_PHASES
    scored = []
    for m in SEC_MASSES:
        for r in SEC_RADII:
            for pi in range(SEC_PHASES):
                c2 = Candidate(m, r, 2 * math.pi * pi / SEC_PHASES)
                s = score(syn_rows, manifest, (PRIMARY_0, c2))
                scored.append((s, c2))
    scored.sort(key=lambda t: t[0])
    print(f"best sequential: {scored[0][0]:.3e}", flush=True)
    for i, (_, c2_init) in enumerate(scored[:6]):
        c1, c2, fun, nit = joint_refine(syn_rows, manifest, PRIMARY_0,
                                       c2_init, maxiter=400)
        # check recovery: is body2 near synthetic Mercury?
        dm = abs(c2.mass_solar - SYNTH_MERCURY.mass_solar) / SYNTH_MERCURY.mass_solar
        dr = abs(c2.radius_au - SYNTH_MERCURY.radius_au) / SYNTH_MERCURY.radius_au
        dp = abs((c2.phase_rad - SYNTH_MERCURY.phase_rad + math.pi) % (2*math.pi) - math.pi)
        # also check swapped (body1 might be the small one)
        dm1 = abs(c1.mass_solar - SYNTH_MERCURY.mass_solar) / SYNTH_MERCURY.mass_solar
        print(f"  [{i}] mse={fun:.3e} "
              f"b2: m_err={dm:.2f} r_err={dr:.2f} p_err={dp:.2f} | "
              f"b1_is_small: {dm1 < 0.5}", flush=True)
    print(f"\nSynthetic truth: m={SYNTH_MERCURY.mass_solar:.2e} "
          f"r={SYNTH_MERCURY.radius_au} p={SYNTH_MERCURY.phase_rad}", flush=True)


if __name__ == "__main__":
    main()
