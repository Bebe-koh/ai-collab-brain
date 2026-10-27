"""Hypothesis inventor: generate new hypotheses when the tracker is surprised.

The tracker maintains P(H_i | data). The inventor watches for surprise:
when the best hypothesis still fits poorly, it invents new ones.

Invention strategies:
1. PERTURB: Take the best hypothesis, perturb parameters (wider/narrower,
   heavier/lighter, closer/farther).
2. ADD_BODY: If 1 body doesn't explain it, try 2. If 2 don't, try 3.
3. SWAP_TYPE: If a planet doesn't fit, try a black hole (different mass
   prior, no optical emission constraint).
4. GRID_FILL: Sample the (mass, radius) grid where no hypothesis lives yet.

The inventor proposes; the tracker disposes (scores and prunes).
"""
import math
import numpy as np


class HypothesisInventor:
    def __init__(self, surprise_threshold=10.0):
        """
        surprise_threshold: if best log-likelihood is worse than
                            (null log-likelihood - threshold), we're surprised.
                            (Lower = more easily surprised = more inventive.)
        """
        self.surprise_threshold = surprise_threshold
        self.invention_count = 0

    def is_surprised(self, tracker):
        """Check if any hypothesis explains the data well."""
        from hypothesis_tracker import HypothesisTracker
        best_ll = max(h.log_likelihood for h in tracker.hypotheses
                      if h.log_likelihood is not None)
        # Find null hypothesis likelihood for comparison
        null_ll = None
        for h in tracker.hypotheses:
            if h.n_bodies == 0 and h.log_likelihood is not None:
                null_ll = h.log_likelihood
                break
        if null_ll is None:
            return False
        # Surprised if best is barely better than null
        # (meaning: we have structure we can't explain)
        # Actually: surprised if best is MUCH WORSE than expected
        # For now: surprised if (best - null) < threshold AND best is poor
        # in absolute terms. Simplified: if best_ll is very negative.
        return (best_ll - null_ll) < self.surprise_threshold

    def invent_from_best(self, tracker, n_new=5):
        """Strategy 1+2: perturb best, and try adding a body."""
        from hypothesis_tracker import Hypothesis
        if not tracker.hypotheses:
            return []
        posts = tracker.posteriors()
        best = max(tracker.hypotheses, key=lambda h: posts[h.name])
        new_hyps = []

        # If best is null (no bodies), can't perturb — propose from scratch
        if best.n_bodies == 0:
            return self.invent_grid_fill(tracker, n_new=n_new + 2)

        # Strategy 1: PERTURB the best
        for i in range(n_new):
            new_bodies = []
            for m, r, p in best.bodies:
                # Log-normal perturbation: factor of 2-5 in mass, 20-50% in radius
                m_new = m * 10 ** np.random.uniform(-0.7, 0.7)
                r_new = r * 10 ** np.random.uniform(-0.2, 0.2)
                r_new = max(0.1, min(r_new, 100.0))  # sane bounds
                # Phase: perturb by up to ±1 rad, wrap to [0, 2π)
                p_new = (p + np.random.uniform(-1.0, 1.0)) % (2 * math.pi)
                new_bodies.append((m_new, r_new, p_new))
            self.invention_count += 1
            new_hyps.append(Hypothesis(
                f"invented_perturb_{self.invention_count}",
                new_bodies,
                log_prior=math.log(0.01),  # low prior for invented
                body_type=best.body_type,
            ))

        # Strategy 2: ADD_BODY (if best has < 3 bodies)
        if best.n_bodies < 3:
            for i in range(2):
                new_bodies = list(best.bodies)
                # Add a body at a different scale
                existing_r = [r for _, r, _ in best.bodies]
                r_new = (max(existing_r) * 10 if existing_r
                         else 5.0)
                m_new = 1e-7  # start small
                p_new = np.random.uniform(0, 2 * math.pi)
                new_bodies.append((m_new, r_new, p_new))
                self.invention_count += 1
                new_hyps.append(Hypothesis(
                    f"invented_addbody_{self.invention_count}",
                    new_bodies,
                    log_prior=math.log(0.005),
                    body_type=best.body_type,
                ))

        # Strategy 3: SWAP_TYPE (planet -> PBH or vice versa)
        new_type = "pbh" if best.body_type == "planet" else "planet"
        self.invention_count += 1
        new_hyps.append(Hypothesis(
            f"invented_swap_{self.invention_count}",
            list(best.bodies),
            log_prior=math.log(0.01),
            body_type=new_type,
        ))

        return new_hyps

    def invent_grid_fill(self, tracker, mass_range=(1e-9, 1e-2),
                         radius_range=(0.3, 50.0), n_new=5):
        """Strategy 4: sample where no hypothesis lives yet."""
        from hypothesis_tracker import Hypothesis
        # Collect existing (log_mass, log_radius) points
        existing = []
        for h in tracker.hypotheses:
            for m, r, _ in h.bodies:
                existing.append((math.log10(m), math.log10(r)))
        existing = np.array(existing) if existing else np.empty((0, 2))

        new_hyps = []
        attempts = 0
        while len(new_hyps) < n_new and attempts < 50:
            attempts += 1
            lm = np.random.uniform(math.log10(mass_range[0]),
                                   math.log10(mass_range[1]))
            lr = np.random.uniform(math.log10(radius_range[0]),
                                   math.log10(radius_range[1]))
            # Check distance to nearest existing
            if len(existing) > 0:
                dists = np.sqrt(((existing - [lm, lr]) ** 2).sum(axis=1))
                if dists.min() < 0.5:  # too close to existing, skip
                    continue
            self.invention_count += 1
            p_new = np.random.uniform(0, 2 * math.pi)
            new_hyps.append(Hypothesis(
                f"invented_grid_{self.invention_count}",
                [(10 ** lm, 10 ** lr, p_new)],
                log_prior=math.log(0.01),
                body_type="planet",
            ))
        return new_hyps


def expand_and_contract(tracker, inventor, rows, manifest, build_system_fn,
                        max_rounds=3, prune_threshold=1e-4):
    """The full loop: score -> check surprise -> invent -> score -> prune.

    This is the "thought" process:
    1. Score current hypotheses.
    2. If surprised, invent new ones.
    3. Score the new ones.
    4. Prune the losers.
    5. Repeat until not surprised or max rounds.
    """
    for round_i in range(max_rounds):
        print(f"\n--- Round {round_i + 1} ---", flush=True)
        tracker.update(rows, manifest, build_system_fn)
        print(tracker.report(), flush=True)

        if not inventor.is_surprised(tracker):
            print("Not surprised. Hypotheses explain the data.", flush=True)
            break

        print("Surprised! Inventing new hypotheses...", flush=True)
        new_hyps = inventor.invent_from_best(tracker, n_new=3)
        new_hyps += inventor.invent_grid_fill(tracker, n_new=2)
        for h in new_hyps:
            tracker.add(h)
            print(f"  + {h}", flush=True)

        # Score the new ones
        tracker.update(rows, manifest, build_system_fn)

        # Prune losers
        before = len(tracker.hypotheses)
        tracker.prune(min_prob=prune_threshold)
        after = len(tracker.hypotheses)
        print(f"Pruned {before - after} hypotheses.", flush=True)

    print("\n=== FINAL ===", flush=True)
    print(tracker.report(), flush=True)
    return tracker
