"""Hypothesis history: the tracker's memory.

The tracker is currently amnesiac — every run starts from scratch.
The history gives it a way to learn:

1. REMEMBER: Every hypothesis ever tried, with its score.
   Don't re-invent what already failed.

2. LEARN PRIORS: If (mass, radius) regions consistently score well,
   the prior for new hypotheses in those regions goes up.
   If they consistently fail, the prior goes down.

3. INCREMENTAL: When new data arrives, don't re-score from scratch.
   Store the per-observation contributions, update only what's new.

4. TRANSFER: What worked in one system informs the prior for the next.
   (e.g., "planets at 5 AU are common" becomes a prior.)

This is the lab notebook: what was tried, what worked, what didn't.
"""
import math
import json
import os
import numpy as np
from collections import defaultdict


class HypothesisHistory:
    def __init__(self, path=None):
        """
        path: where to persist the history (JSON). If None, in-memory only.
        """
        self.path = path
        # Every hypothesis ever scored: name -> dict
        self.records = {}
        # Parameter-space learning: binned (log_mass, log_radius) -> stats
        # Each bin tracks: n_tried, n_good (posterior > 0.1), total_loglike
        self.bins = defaultdict(lambda: {'n_tried': 0, 'n_good': 0,
                                         'sum_loglike': 0.0})
        self.bin_width = 0.5  # in log10 units
        if path and os.path.exists(path):
            self.load()

    def _bin_key(self, mass, radius):
        lm = math.log10(max(mass, 1e-15))
        lr = math.log10(max(radius, 1e-3))
        return (round(lm / self.bin_width), round(lr / self.bin_width))

    def record(self, hypothesis, posterior, log_likelihood):
        """Log a hypothesis and its outcome."""
        self.records[hypothesis.name] = {
            'bodies': hypothesis.bodies,
            'body_type': hypothesis.body_type,
            'posterior': posterior,
            'log_likelihood': log_likelihood,
            'n_bodies': hypothesis.n_bodies,
        }
        # Update bins
        for m, r, _ in hypothesis.bodies:
            key = self._bin_key(m, r)
            b = self.bins[key]
            b['n_tried'] += 1
            b['sum_loglike'] += log_likelihood
            if posterior > 0.1:
                b['n_good'] += 1
        if self.path:
            self.save()

    def learned_prior(self, mass, radius, base_log_prior=math.log(0.01)):
        """Adjust prior based on history.

        If this (mass, radius) region has been good before, boost the prior.
        If it's been tried and failed, lower it.
        If never tried, use the base prior.
        """
        key = self._bin_key(mass, radius)
        b = self.bins.get(key)
        if b is None or b['n_tried'] == 0:
            return base_log_prior
        # Empirical success rate
        success_rate = b['n_good'] / b['n_tried']
        # Boost prior by success rate (in log space)
        # success_rate=1.0 -> +2.3 (10x boost)
        # success_rate=0.0 -> -2.3 (10x penalty)
        # success_rate=0.5 -> 0 (no change)
        adjustment = math.log(10) * (2 * success_rate - 1)
        # Don't over-adjust with few samples
        confidence = min(b['n_tried'] / 10.0, 1.0)
        return base_log_prior + confidence * adjustment

    def was_tried(self, mass, radius, tolerance=0.3):
        """Check if a similar hypothesis was already tried and failed."""
        for rec in self.records.values():
            for m, r, _ in rec['bodies']:
                dm = abs(math.log10(m) - math.log10(max(mass, 1e-15)))
                dr = abs(math.log10(r) - math.log10(max(radius, 1e-3)))
                if dm < tolerance and dr < tolerance:
                    return rec['posterior'] < 0.01  # True if tried and failed
        return False

    def promising_regions(self, top_k=5):
        """Return the (mass, radius) bins with highest success rates."""
        scored = []
        for key, b in self.bins.items():
            if b['n_tried'] >= 3:  # need minimum samples
                rate = b['n_good'] / b['n_tried']
                avg_ll = b['sum_loglike'] / b['n_tried']
                scored.append((rate, avg_ll, key))
        scored.sort(reverse=True)
        regions = []
        for rate, avg_ll, key in scored[:top_k]:
            lm = key[0] * self.bin_width
            lr = key[1] * self.bin_width
            regions.append({
                'mass': 10 ** lm, 'radius': 10 ** lr,
                'success_rate': rate, 'avg_loglike': avg_ll,
            })
        return regions

    def save(self):
        if not self.path:
            return
        data = {
            'records': self.records,
            # Convert tuple keys to strings for JSON
            'bins': {f"{k[0]},{k[1]}": v for k, v in self.bins.items()},
        }
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=1, default=str)

    def load(self):
        with open(self.path) as f:
            data = json.load(f)
        self.records = data.get('records', {})
        self.bins = defaultdict(lambda: {'n_tried': 0, 'n_good': 0,
                                         'sum_loglike': 0.0})
        for k_str, v in data.get('bins', {}).items():
            k = tuple(map(int, k_str.split(',')))
            self.bins[k] = v

    def summary(self):
        lines = [f"History: {len(self.records)} hypotheses recorded."]
        regions = self.promising_regions(top_k=3)
        if regions:
            lines.append("Promising regions (learned):")
            for r in regions:
                lines.append(f"  m={r['mass']:.1e} r={r['radius']:.1f} "
                             f"(success {r['success_rate']:.0%})")
        else:
            lines.append("No promising regions yet (need more data).")
        return "\n".join(lines)
