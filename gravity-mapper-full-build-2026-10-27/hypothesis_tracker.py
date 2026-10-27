"""Hypothesis tracker: give the mapper multiple competing explanations.

Instead of one answer, maintain a set of hypotheses, each with a
posterior probability. As new data arrives, update the probabilities.
The user sees how the "percent" for each hypothesis shifts with evidence.

This is Bayesian model comparison over a discrete hypothesis set:
    P(H_i | data) ∝ P(data | H_i) * P(H_i)

Each hypothesis is a specific claim: "N bodies with these parameters."
The tracker generates, scores, updates, and prunes them.

CALIBRATION (2026-10-26 fix — see rom_integration_note.md §1/§2):
The raw BIC-style log-likelihood (-0.5 * N * log(MSE)) is overconfident
by construction: with N in the thousands, a 20% MSE improvement yields
e^182 odds and a posterior of exactly 1.0. Posteriors are therefore
computed from CALIBRATED weights:
  1. Tempering: raw log-likelihoods are divided by T = N / N_EFF_CAP
     (default cap 50). Justification, stated openly: orbit-fit residuals
     are dominated by correlated systematics (shared ephemeris, same
     trajectory, numerical floors), so one fit never carries more than
     ~50 independent evidence units, whatever N says.
  2. Complexity penalty: 0.5 * k * log(N_eff), k = 3 free parameters per
     body (mass, radius, phase). Previously missing entirely.
  3. Posterior cap: no posterior may exceed 0.99; excess is redistributed
     proportionally and the capping is flagged (self.capped). A single
     dataset with known model misspecification never justifies certainty.
  4. Verdict path: pipeline verdicts (PROMOTED/KILLED/ABSTAINED/NULL) add
     bounded log-odds contributions (per-item cap 5.0 ≈ 148:1). Verdicts
     are coarse evidence (fit summaries, not raw data); no single verdict
     can produce certainty. Repeated INDEPENDENT confirmations accumulate
     legitimately.
All hypotheses in one tracker must be scored on the SAME data; mixing N
across hypotheses invalidates comparison.

Usage:
    tracker = HypothesisTracker()
    tracker.propose_null()                    # "nothing there"
    tracker.propose_from_pipeline(...)        # "pipeline's best fit"
    tracker.propose_alternatives(...)         # "what else could it be?"
    tracker.update(data)                      # new evidence arrives
    tracker.report()                          # sorted by posterior
    tracker.add_verdict(name, 'promoted', holdout_ratio=5400.0)
"""
import copy
import math
import numpy as np

# Calibration constants (see note §2 for justification and test evidence).
N_EFF_CAP = 50        # max independent evidence units credited per fit
POSTERIOR_CAP = 0.99  # no posterior may exceed this
VERDICT_CAP = 5.0     # max |log-odds| contributed by one verdict
NULL_EVIDENCE = -2.0  # log-odds contribution of a clean null to a region
PARAMS_PER_BODY = 3   # (mass, radius, phase)


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
        # Verdict-path fields (rom_loop driver fills these).
        self.verdict_loglik = 0.0
        self.last_verdict = None
        self.last_holdout_ratio = None
        self.last_coherent = None
        self.killed_by_inventory = False
        # Bucket state (spec v2): 'active' by default; deferred
        # hypotheses keep a snapshot log-weight (see tracker methods).
        self.status = 'active'
        self._bucket_log_weight = None

    @property
    def n_bodies(self):
        return len(self.bodies)

    def __repr__(self):
        b = ", ".join(f"({m:.1e},{r:.1f},{p:.2f})"
                      for m, r, p in self.bodies)
        return f"{self.name}: [{b}] ({self.body_type})"


class HypothesisTracker:
    def __init__(self, sigma_au=1e-5, n_eff_cap=N_EFF_CAP,
                 posterior_cap=POSTERIOR_CAP, verdict_cap=VERDICT_CAP):
        """
        sigma_au: assumed measurement noise for likelihood calculation.
                  (Kept for interface compatibility; the BIC scorer does
                  not use it. The verdict path does not need it.)
        n_eff_cap: tempering cap — see module docstring.
        posterior_cap: hard cap on any posterior (0.99 default).
        verdict_cap: max |log-odds| per verdict (5.0 default).
        """
        self.hypotheses = []
        self.sigma = sigma_au
        self.n_eff_cap = n_eff_cap
        self.posterior_cap = posterior_cap
        self.verdict_cap = verdict_cap
        self.log_evidence = None
        self.capped = False
        self.capped_names = []
        # Bucket-aware state (spec v2, SEPARATE from legacy path).
        # Deferred hypotheses live here, not in self.hypotheses, so
        # legacy posteriors()/prune()/update_from_verdicts() are
        # unaffected. Bucket ledger is in-memory only, never part
        # of the ROM persisted state; attempt_log is diagnostic only.
        self.deferred_hypotheses = []
        self.bucket_ledger = []
        self.attempt_log = []

    def add(self, hypothesis):
        # Phase 2 hygiene: posteriors are keyed by name and add_verdict
        # targets the FIRST match, so a silent name collision is a
        # correctness bug, not a style point. All live call sites use
        # unique names (counter-suffixed inventor names, one propose
        # per name per tracker in replays); a collision here means a
        # caller bug and must surface, not merge.
        if any(h.name == hypothesis.name for h in self.hypotheses):
            raise ValueError(
                f"duplicate hypothesis name: {hypothesis.name}")
        self.hypotheses.append(hypothesis)

    def propose_null(self, log_prior=0.0):
        """The null: no hidden bodies."""
        self.add(Hypothesis("null", [], log_prior=log_prior))

    def propose(self, name, bodies, body_type="planet", log_prior=0.0):
        """Add a specific hypothesis."""
        self.add(Hypothesis(name, bodies, log_prior, body_type))

    def score_hypothesis(self, hyp, rows, manifest, build_system_fn):
        """Compute log-likelihood via BIC-style approximation on holdout MSE.

        NOTE (2026-10-26 audit): the catalog import below requires
        `source_upload/` on sys.path; without it this raises
        ModuleNotFoundError. Callers that score through this method must
        ensure the path (Tracker3D and residual_hunt bypass it with their
        own scorers). The returned value is the RAW log-likelihood; the
        calibration (tempering, penalty, cap) is applied in
        calibrated_weight()/posteriors(), so all scorers benefit.

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

    def calibrated_weight(self, hyp):
        """Calibrated log-weight for one hypothesis (see module docstring).

        weight = log_prior + tempered dynamics log-like (if scored)
                 - complexity penalty + verdict log-odds.
        Unscored hypotheses contribute no dynamics term.
        """
        w = hyp.log_prior + hyp.verdict_loglik
        if hyp.log_likelihood is not None:
            n_eff = min(max(hyp.n_data, 1), self.n_eff_cap)
            temper = max(hyp.n_data, 1) / n_eff
            w += hyp.log_likelihood / temper
            k = PARAMS_PER_BODY * hyp.n_bodies
            w -= 0.5 * k * math.log(n_eff)
        return w

    def _compute_posteriors(self):
        """Softmax over calibrated weights, with the posterior cap applied.

        Returns (posteriors dict, capped_names list). Never returns
        exactly 0.0 or 1.0.
        """
        if not self.hypotheses:
            return {}, []
        ws = np.array([self.calibrated_weight(h) for h in self.hypotheses])
        m = ws.max()
        unnorm = np.exp(ws - m)
        posts = unnorm / unnorm.sum()
        capped_names = []
        # Cap loop (only meaningful with >= 2 hypotheses: a single
        # hypothesis exhausts the space, so its posterior is 1.0 by
        # construction and capping it would be incoherent).
        if len(posts) < 2:
            return {h.name: float(p) for h, p in
                    zip(self.hypotheses, posts)}, []
        # Cap loop: cap the top hypothesis, redistribute excess
        # proportionally, repeat if redistribution pushes another over.
        for _ in range(len(self.hypotheses)):
            over = [i for i, p in enumerate(posts)
                    if p > self.posterior_cap]
            if not over:
                break
            for i in over:
                capped_names.append(self.hypotheses[i].name)
                excess = posts[i] - self.posterior_cap
                posts[i] = self.posterior_cap
                rest = np.array([p if j not in over else 0.0
                                 for j, p in enumerate(posts)])
                tot = rest.sum()
                if tot > 0:
                    posts = posts + rest / tot * excess
                    # restore capped entries (they were zeroed in rest)
                    for j in over:
                        posts[j] = self.posterior_cap
                # renormalize defensively
                posts = posts / posts.sum()
        # Numerical floor: never exactly 0.0
        posts = np.maximum(posts, 1e-12)
        posts = posts / posts.sum()
        return {h.name: float(p) for h, p in
                zip(self.hypotheses, posts)}, capped_names


    # --- Bucket-aware posterior path (spec v2, separate path) ---
    # Legacy _compute_posteriors() above is UNCHANGED. This path is
    # used only when a deferred bucket exists (or in bucket tests).
    # It normalizes over active + deferred TOGETHER with a single
    # shared max-offset (§1.5), returns the UNCAPPED distribution as
    # the scientific distribution, and reports the cap as display-only
    # metadata (§1.4) — it never constructs a capped distribution and
    # never redistributes cap excess to anyone (MUST-NOT-COMBINE).
    @staticmethod
    def _norm_bodies(bodies):
        out = []
        for b in bodies:
            t = tuple(list(b) + [0.0] * (3 - len(b)))[:3]
            out.append((float(t[0]), float(t[1]), float(t[2])))
        return out

    def _bucket_weight(self, hyp):
        # Deferred weights are frozen at deferral (snapshot), so later
        # active-only evidence can never move them (spec §1.2).
        snap = getattr(hyp, '_bucket_log_weight', None)
        if getattr(hyp, 'status', 'active') == 'deferred' and snap is not None:
            return snap
        return self.calibrated_weight(hyp)

    @staticmethod
    def _validate_bucket_weights(weights):
        for name, w in weights.items():
            if isinstance(w, float) and (math.isnan(w) or w == float('inf')):
                raise ValueError(
                    f"bucket log-weight for {name!r} is +inf/NaN: rejected")
        if weights and all(w == float('-inf') for w in weights.values()):
            raise ValueError(
                "all bucket weights are -inf: distribution undefined")
        return weights

    def bucket_log_weights(self):
        """{name: log-weight} over active + deferred together."""
        weights = {}
        for h in self.hypotheses:
            weights[h.name] = self._bucket_weight(h)
        for h in self.deferred_hypotheses:
            weights[h.name] = self._bucket_weight(h)
        return self._validate_bucket_weights(weights)

    def deferred_log_weights(self):
        """{name: frozen log-weight} for deferred hypotheses only."""
        return {h.name: self._bucket_weight(h)
                for h in self.deferred_hypotheses}

    def bucket_uncapped_posteriors(self):
        """Uncapped softmax over active + deferred (§1.5), pre-floor.

        Single shared max-offset; underflow to 0.0 is documented, not
        an error; -inf sentinel gives share 0.0; all -inf rejected.
        This is the scientific distribution; it sums to 1.0.
        """
        weights = self.bucket_log_weights()
        if not weights:
            return {}
        m = max(weights.values())
        if not math.isfinite(m):
            raise ValueError(
                "all bucket weights are -inf: distribution undefined")
        unnorm = {}
        for name, w in weights.items():
            # w - m <= 0, so exp never overflows; very negative
            # differences underflow to 0.0 (documented, §1.5).
            unnorm[name] = math.exp(w - m) if w != float('-inf') else 0.0
        total = sum(unnorm.values())
        if total <= 0.0 or not math.isfinite(total):
            raise ValueError("bucket normalization failed")
        return {name: u / total for name, u in unnorm.items()}

    def bucket_posteriors(self):
        """Bucket report dict. No capped distribution is constructed.

        Keys: uncapped (= postering scientific distribution, alias
        'posteriors'), bucket_share, active_share, null_share,
        cap_applied, cap_excess, null_display, display_only,
        deferred_names, active_names. Cap rule (§1.4): only the null's
        uncapped share is capped, and only as display; a single active
        hypothesis plus a non-empty bucket is a TWO-component
        distribution, so the legacy single-hypothesis exemption does
        NOT apply here — cap_applied is decided purely on the null's
        uncapped share, regardless of hypothesis count.
        """
        uncapped = self.bucket_uncapped_posteriors()
        deferred_names = [h.name for h in self.deferred_hypotheses]
        bucket_share = sum(uncapped.get(n, 0.0) for n in deferred_names)
        null_share = uncapped.get('null', 0.0)
        cap_applied = 'null' in uncapped and null_share > self.posterior_cap
        cap_excess = (null_share - self.posterior_cap) if cap_applied else 0.0
        return {
            'uncapped': dict(uncapped),
            'posteriors': dict(uncapped),
            'bucket_share': bucket_share,
            'active_share': 1.0 - bucket_share if uncapped else 0.0,
            'null_share': null_share,
            'cap_applied': cap_applied,
            'cap_excess': cap_excess,
            'null_display': self.posterior_cap if cap_applied else null_share,
            'display_only': cap_applied,
            'deferred_names': list(deferred_names),
            'active_names': [h.name for h in self.hypotheses],
        }

    def scientific_state(self):
        """State tuple covered by equality tests (§2.1): (weights,
        statuses, bucket, persisted ledger). Attempt log is explicitly
        NOT part of this tuple and is never persisted via ROM save."""
        weights = self.bucket_log_weights()
        statuses = {}
        for h in self.hypotheses:
            statuses[h.name] = 'active'
        for h in self.deferred_hypotheses:
            statuses[h.name] = 'deferred'
        return (dict(weights), statuses,
                tuple(h.name for h in self.deferred_hypotheses),
                copy.deepcopy(self.bucket_ledger))

    def bucket_state_dict(self):
        """JSON-able bucket state for persistence tests (§4).

        Persisted form carries UNCAPPED shares + cap metadata only;
        capped values are never stored as posteriors. Finite
        log-weights round-trip exactly via JSON float repr; -inf is
        the sole permitted non-finite sentinel.
        """
        weights = self.bucket_log_weights()
        report = self.bucket_posteriors()
        return {
            'active': {h.name: weights[h.name] for h in self.hypotheses},
            'deferred': {h.name: weights[h.name]
                         for h in self.deferred_hypotheses},
            'statuses': {h.name: ('active' if h in self.hypotheses
                                  else 'deferred')
                         for h in self.hypotheses + self.deferred_hypotheses},
            'ledger': copy.deepcopy(self.bucket_ledger),
            'uncapped': report['uncapped'],
            'bucket_share': report['bucket_share'],
            'cap_applied': report['cap_applied'],
            'cap_excess': report['cap_excess'],
            'null_display': report['null_display'],
            'display_only': report['display_only'],
        }

    @staticmethod
    def validate_bucket_state_dict(d):
        """Validate a persisted bucket state dict (§4, §1.4 rule 4).

        Rejects +inf/NaN log-weights, all -inf weights, a capped
        distribution stored under 'posteriors', and a 'posteriors'
        field that differs from the uncapped distribution when the
        cap is applied. Returns True on acceptance.
        """
        if 'capped_posteriors' in d:
            raise ValueError("capped distribution must never be persisted")
        weights = {}
        for section in ('active', 'deferred'):
            weights.update(d.get(section, {}))
        for name, w in weights.items():
            if isinstance(w, float) and (math.isnan(w) or w == float('inf')):
                raise ValueError(
                    f"persisted bucket log-weight for {name!r} is +inf/NaN")
        if weights and all(w == float('-inf') for w in weights.values()):
            raise ValueError("persisted bucket state has all -inf weights")
        if d.get('cap_applied') and isinstance(d.get('posteriors'), dict):
            if d['posteriors'].get('null') != d.get('uncapped', {}).get('null'):
                raise ValueError(
                    "capped value stored as a posterior: rejected")
        return True

    def defer_to_bucket(self, name, case_id, event_identity=None,
                        expected_bodies=None):
        """Move an active hypothesis to the deferred bucket (§2).

        Validation runs BEFORE any mutation, so a rejection leaves
        the complete state unchanged. Deferring an already-deferred
        hypothesis is a NO-OP on scientific state and ledger (the
        attempt is logged only to the separate attempt_log, §2.1).
        Returns True on a new deferral, False on a no-op replay.
        """
        if case_id is None:
            raise ValueError(
                'defer_to_bucket requires an explicit case_id '
                '(no silent default on persisted paths)')
        target = None
        for h in self.hypotheses:
            if h.name == name:
                target = h
                break
        if target is None:
            if any(h.name == name for h in self.deferred_hypotheses):
                self.attempt_log.append({
                    'action': 'defer_replay', 'name': name,
                    'case_id': case_id, 'result': 'noop'})
                return False
            raise ValueError(f"unknown hypothesis: {name}")
        if target.name == 'null':
            raise ValueError("null is never deferred (it is the control)")
        if expected_bodies is not None:
            if self._norm_bodies(expected_bodies) != self._norm_bodies(target.bodies):
                raise ValueError(
                    f"identity mismatch for {name!r}: same name, "
                    f"different parameters — rejected, state unchanged")
        w = self.calibrated_weight(target)
        if isinstance(w, float) and (math.isnan(w) or w == float('inf')):
            raise ValueError(f"log-weight for {name!r} is +inf/NaN: rejected")
        target._bucket_log_weight = w
        target.status = 'deferred'
        self.hypotheses.remove(target)
        self.deferred_hypotheses.append(target)
        self.bucket_ledger.append({
            'action': 'defer', 'name': name,
            'bodies': self._norm_bodies(target.bodies),
            'body_type': target.body_type, 'case_id': case_id,
            'log_weight': w,
            'event_identity': (copy.deepcopy(event_identity)
                               if isinstance(event_identity, dict)
                               else event_identity),
            'trigger': None})
        return True

    def reenter_from_bucket(self, name, trigger, case_id=None,
                            event_identity=None, expected_bodies=None):
        """Transfer a deferred hypothesis back to active (§2).

        Requires an explicit case_id AND a recorded trigger; either
        missing is a rejection (state unchanged). Re-entry TRANSFERS
        the existing contribution — it never duplicates it. Returns
        True on success.
        """
        if case_id is None:
            raise ValueError(
                'reenter_from_bucket requires an explicit case_id')
        if not trigger:
            raise ValueError(
                'reenter_from_bucket requires a recorded trigger')
        target = None
        for h in self.deferred_hypotheses:
            if h.name == name:
                target = h
                break
        if target is None:
            raise ValueError(f"hypothesis {name!r} is not deferred")
        if expected_bodies is not None:
            if self._norm_bodies(expected_bodies) != self._norm_bodies(target.bodies):
                raise ValueError(
                    f"identity mismatch for {name!r}: same name, "
                    f"different parameters — rejected, state unchanged")
        if isinstance(event_identity, dict):
            for ev in self.bucket_ledger:
                if (ev.get('action') == 'defer' and ev.get('name') == name
                        and ev.get('case_id') == case_id):
                    orig = ev.get('event_identity')
                    if (isinstance(orig, dict)
                            and orig.get('dataset_id') is not None
                            and event_identity.get('dataset_id') is not None
                            and orig['dataset_id'] != event_identity['dataset_id']):
                        raise ValueError(
                            f"same event {case_id!r} under a different "
                            f"dataset — rejected, state unchanged")
        w_before = self._bucket_weight(target)
        self.deferred_hypotheses.remove(target)
        target.status = 'active'
        target._bucket_log_weight = None
        w_after = self.calibrated_weight(target)
        self.hypotheses.append(target)
        self.bucket_ledger.append({
            'action': 'reenter', 'name': name,
            'bodies': self._norm_bodies(target.bodies),
            'body_type': target.body_type, 'case_id': case_id,
            'log_weight_before': w_before, 'log_weight_after': w_after,
            'event_identity': (copy.deepcopy(event_identity)
                               if isinstance(event_identity, dict)
                               else event_identity),
            'trigger': trigger})
        return True

    def update(self, rows, manifest, build_system_fn, force_rescore=True):
        """Score all hypotheses against data, compute posteriors.

        force_rescore=True (default, fixed 2026-10-26): every hypothesis
        is re-scored on every update. The old code skipped already-scored
        hypotheses, so new data silently kept old scores. Callers that
        pre-set log_likelihood manually (e.g. residual_hunt's
        set_likelihoods) must pass force_rescore=False or not call
        update() at all.
        """
        for hyp in self.hypotheses:
            if force_rescore or hyp.log_likelihood is None:
                self.score_hypothesis(hyp, rows, manifest, build_system_fn)
        posts, capped = self._compute_posteriors()
        self.capped = bool(capped)
        self.capped_names = capped
        ws = np.array([self.calibrated_weight(h) for h in self.hypotheses])
        m = ws.max()
        self.log_evidence = m + math.log(np.sum(np.exp(ws - m)))

    def add_verdict(self, name, outcome, holdout_ratio=None, region=None,
                    coherent=None):
        """Add one pipeline verdict as bounded evidence (verdict path).

        outcome: 'promoted' | 'killed' | 'killed_by_inventory' |
                 'abstained' | 'null'
        holdout_ratio: holdout MSE without the body / with it (>1 = better).
        region: optional (log10_mass_center, log10_radius_center, dex_radius)
            for 'null' verdicts: applies NULL_EVIDENCE to hypotheses with a
            body in that region. If None, applies to all non-null hyps.
        coherent: whether the case showed coherent (split-half) structure.
            Recorded on the hypothesis for the surprise trigger.
        """
        target = None
        for h in self.hypotheses:
            if h.name == name:
                target = h
                break
        if outcome == 'null':
            # Region-scoped null evidence against matching hypotheses.
            for h in self.hypotheses:
                if h.n_bodies == 0:
                    continue
                if region is None or self._in_region(h, region):
                    h.verdict_loglik += NULL_EVIDENCE
                    h.last_verdict = 'null'
                    h.last_holdout_ratio = holdout_ratio
                    h.last_coherent = coherent
            return
        if target is None:
            raise ValueError(f"unknown hypothesis: {name}")
        if outcome == 'promoted':
            ratio = holdout_ratio if holdout_ratio else 1.0
            contrib = min(math.log(max(ratio, 1e-12)), self.verdict_cap)
            target.verdict_loglik += contrib
        elif outcome == 'killed':
            target.verdict_loglik -= self.verdict_cap
        elif outcome == 'killed_by_inventory':
            target.verdict_loglik -= self.verdict_cap
            target.killed_by_inventory = True
        elif outcome == 'abstained':
            pass  # no evidence either way
        else:
            raise ValueError(f"unknown verdict outcome: {outcome}")
        target.last_verdict = outcome
        target.last_holdout_ratio = holdout_ratio
        target.last_coherent = coherent

    def update_from_verdicts(self, verdicts):
        """Apply a batch of verdict dicts, then refresh posteriors/cap flags.

        Each verdict dict: {name, outcome, holdout_mse_ratio? (preferred,
        MSE domain, Phase 2 fix #2) or holdout_ratio? (legacy, also MSE
        domain per add_verdict's contract), region?, coherent?}.
        'null' verdicts need name=None (region-scoped).
        """
        for v in verdicts:
            ratio = v.get('holdout_mse_ratio')
            if ratio is None:
                ratio = v.get('holdout_ratio')
            self.add_verdict(v.get('name'), v['outcome'],
                             holdout_ratio=ratio,
                             region=v.get('region'),
                             coherent=v.get('coherent'))
        posts, capped = self._compute_posteriors()
        self.capped = bool(capped)
        self.capped_names = capped
        ws = np.array([self.calibrated_weight(h) for h in self.hypotheses])
        m = ws.max()
        self.log_evidence = m + math.log(np.sum(np.exp(ws - m)))

    @staticmethod
    def _in_region(hyp, region):
        lm_c, lr_c, dex = region
        for m, r, _ in hyp.bodies:
            if (abs(math.log10(max(m, 1e-15)) - lm_c) <= dex and
                    abs(math.log10(max(r, 1e-3)) - lr_c) <= dex):
                return True
        return False

    def posteriors(self):
        """Return {name: calibrated posterior probability}."""
        posts, capped = self._compute_posteriors()
        self.capped = bool(capped)
        self.capped_names = capped
        return posts

    def prune(self, min_prob=1e-6):
        """Drop hypotheses with negligible posterior.

        Safety rules (2026-10-26): the null hypothesis is NEVER pruned
        (it is the control and must always remain), and pruning never
        leaves fewer than 2 hypotheses. This prevents the irreversible
        collapse the old code allowed after one overconfident batch.
        """
        posts = self.posteriors()
        ranked = sorted(self.hypotheses, key=lambda h: -posts[h.name])
        keep = []
        for h in ranked:
            if h.name == 'null':
                keep.append(h)
            elif posts[h.name] >= min_prob:
                keep.append(h)
        if len(keep) < 2 and len(ranked) >= 2:
            for h in ranked:
                if h not in keep:
                    keep.append(h)
                if len(keep) >= 2:
                    break
        self.hypotheses = keep
        posts, capped = self._compute_posteriors()
        self.capped = bool(capped)
        self.capped_names = capped
        if self.hypotheses:
            ws = np.array([self.calibrated_weight(h)
                           for h in self.hypotheses])
            m = ws.max()
            self.log_evidence = m + math.log(np.sum(np.exp(ws - m)))

    def report(self):
        """Print hypotheses sorted by posterior probability."""
        posts = self.posteriors()
        ranked = sorted(self.hypotheses,
                        key=lambda h: -posts[h.name])
        lines = ["Hypothesis posteriors:"]
        for h in ranked:
            p = posts[h.name]
            flag = " (capped)" if h.name in self.capped_names else ""
            lines.append(f"  {p*100:6.2f}%  {h}{flag}")
        return "\n".join(lines)

    def update_batches(self, data_batches, manifest, build_system_fn):
        """Update with multiple data batches, showing how probs shift.

        Returns list of posterior dicts, one per batch.
        BATCH-ONLY comparison (renamed Phase 2 from update_sequential,
        whose docstring claimed cumulative rescoring while the body
        scored batch-only): each batch is scored independently after
        resetting likelihoods. This is NOT cumulative rescoring over
        accumulated data — true sequential accumulation is a separate
        feature, not this method.
        """
        history = []
        for i, batch in enumerate(data_batches):
            # Reset likelihoods to force rescoring on this batch.
            for h in self.hypotheses:
                h.log_likelihood = None
            # Score on this batch only (batch-only by design).
            self.update(batch, manifest, build_system_fn)
            posts = self.posteriors()
            history.append(dict(posts))
            print(f"After batch {i + 1}:", flush=True)
            for name, p in sorted(posts.items(), key=lambda x: -x[1]):
                print(f"  {p*100:6.2f}%  {name}", flush=True)
        return history
