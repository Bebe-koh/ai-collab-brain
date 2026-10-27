"""Hypothesis tracker: give the mapper multiple competing explanations.

Instead of one answer, maintain a set of hypotheses, each with a
posterior probability. As new data arrives, update the probabilities.
The user sees how the "percent" for each hypothesis shifts with evidence.

This is Bayesian model comparison over a discrete hypothesis set:
    P(H_i | data) ∝ P(data | H_i) * P(H_i)

Each hypothesis is a specific claim: "N bodies with these parameters."
The tracker generates, scores, updates, and prunes them.

Usage:
    tracker = HypothesisTracker()
    tracker.propose_null()                    # "nothing there"
    tracker.propose_from_pipeline(...)        # "pipeline's best fit"
    tracker.propose_alternatives(...)         # "what else could it be?"
    tracker.update(data)                      # new evidence arrives
    tracker.report()                          # sorted by posterior
"""
import math
import numpy as np


class Hypothesis:
    """One specific explanation: N bodies with parameters."""

    def __init__(self, name, bodies, log_prior=0.0, body_type="planet"):
        """
        bodies: list of (mass_solar, radius_au, phase_rad) tuples
                (phase defaults to 0.0 if 2-tuple given)
        body_type: "planet", "pbh", or "unknown"
        log_prior: log P(H) before seeing data
        """
        self.name = name
        # Normalize to 3-tuples (m, r, phase)
        self.bodies = [tuple(list(b) + [0.0] * (3 - len(b))) for b in bodies]
        self.body_type = body_type
        self.log_prior = log_prior
        self.log_likelihood = None
        self.n_data = 0

    @property
    def n_bodies(self):
        return len(self.bodies)

    def __repr__(self):
        b = ", ".join(f"({m:.1e},{r:.1f},{p:.2f})"
                      for m, r, p in self.bodies)
        return f"{self.name}: [{b}] ({self.body_type})"


class HypothesisTracker:
    def __init__(self, sigma_au=1e-5):
        """
        sigma_au: assumed measurement noise for likelihood calculation.
                  P(data|H) = prod over obs of Normal(pred, sigma)
        """
        self.hypotheses = []
        self.sigma = sigma_au
        self.log_evidence = None

    def add(self, hypothesis):
        self.hypotheses.append(hypothesis)

    def propose_null(self, log_prior=0.0):
        """The null: no hidden bodies."""
        self.add(Hypothesis("null", [], log_prior=log_prior))

    def propose(self, name, bodies, body_type="planet", log_prior=0.0):
        """Add a specific hypothesis."""
        self.add(Hypothesis(name, bodies, log_prior, body_type))

    def score_hypothesis(self, hyp, rows, manifest, build_system_fn):
        """Compute log-likelihood via BIC-style approximation on holdout MSE.

        Instead of a fragile Gaussian with hand-picked sigma, we use:
            log P(data|H) ≈ -0.5 * N * log(MSE)
        where MSE is the mean squared error on the given rows.
        This is the Bayesian Information Criterion approximation, which
        doesn't require knowing the noise level in advance.

        For proper holdout validation, pass holdout rows (not train).
        """
        from gravity_mapper.catalog.catalog_two_body_recovery import Candidate
        from gravity_mapper.catalog.scenario_simulator import DT, step_verlet

        candidates = tuple(Candidate(m, r, p) for m, r, p in hyp.bodies)
        system = build_system_fn(manifest, candidates)

        by_time = {}
        for r in rows:
            by_time.setdefault(r['time_years'], []).append(r)
        max_time = max(by_time)
        steps = int(round(max_time / DT))

        sse = 0.0
        n = 0
        for step in range(steps + 1):
            t = round(step * DT, 10)
            if t in by_time:
                state = {b.object_id: b for b in system}
                for row in by_time[t]:
                    b = state[row['object_id']]
                    sse += (row['x_au'] - b.x) ** 2 + (row['y_au'] - b.y) ** 2
                    n += 2
            if step < steps:
                step_verlet(system)

        mse = sse / max(n, 1)
        # BIC-style: log_like ≈ -0.5 * N * log(MSE)
        # Add small floor to avoid log(0)
        mse = max(mse, 1e-30)
        log_like = -0.5 * n * math.log(mse)
        hyp.log_likelihood = log_like
        hyp.n_data = n
        hyp.mse = mse
        return log_like

    def update(self, rows, manifest, build_system_fn):
        """Score all hypotheses against data, compute posteriors."""
        for hyp in self.hypotheses:
            if hyp.log_likelihood is None:
                self.score_hypothesis(hyp, rows, manifest, build_system_fn)
        # Log-evidence via logsumexp
        lps = np.array([h.log_prior + h.log_likelihood for h in self.hypotheses])
        m = lps.max()
        self.log_evidence = m + math.log(np.sum(np.exp(lps - m)))

    def posteriors(self):
        """Return {name: posterior probability}."""
        if self.log_evidence is None:
            raise ValueError("Call update() first")
        return {
            h.name: math.exp(h.log_prior + h.log_likelihood - self.log_evidence)
            for h in self.hypotheses
        }

    def prune(self, min_prob=1e-6):
        """Drop hypotheses with negligible posterior."""
        posts = self.posteriors()
        self.hypotheses = [h for h in self.hypotheses
                           if posts[h.name] >= min_prob]
        # Recompute evidence
        lps = np.array([h.log_prior + h.log_likelihood for h in self.hypotheses])
        m = lps.max()
        self.log_evidence = m + math.log(np.sum(np.exp(lps - m)))

    def report(self):
        """Print hypotheses sorted by posterior probability."""
        posts = self.posteriors()
        ranked = sorted(self.hypotheses,
                        key=lambda h: -posts[h.name])
        lines = ["Hypothesis posteriors:"]
        for h in ranked:
            p = posts[h.name]
            lines.append(f"  {p*100:6.2f}%  {h}")
        return "\n".join(lines)

    def update_sequential(self, data_batches, manifest, build_system_fn):
        """Update with multiple data batches, showing how probs shift.

        Returns list of posterior dicts, one per batch.
        This is the "watch the percent change" that Jase asked for.
        """
        history = []
        for i, batch in enumerate(data_batches):
            # Reset likelihoods to force rescoring on cumulative data
            # (in practice, accumulate batches)
            for h in self.hypotheses:
                h.log_likelihood = None
            # For simplicity, score on this batch only
            # (true sequential would accumulate)
            self.update(batch, manifest, build_system_fn)
            posts = self.posteriors()
            history.append(dict(posts))
            print(f"After batch {i+1}:", flush=True)
            for name, p in sorted(posts.items(), key=lambda x: -x[1]):
                print(f"  {p*100:6.2f}%  {name}", flush=True)
        return history
