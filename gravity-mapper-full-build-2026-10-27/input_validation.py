"""Input data validation for the gravity mapper pipeline.

Adapted from the secular pipeline's ingest_real_residuals.py concept:
validate schema, bounds, and data quality BEFORE fitting. Garbage in
means garbage out — the pipeline should refuse bad data loudly, not
produce confident wrong answers quietly.
"""
import math


# reasonable bounds for the mapper's scenario (inner solar system tracers)
BOUNDS = {
    'time_years': (0, 100),
    'x_au': (-50, 50),
    'y_au': (-50, 50),
}

REQUIRED_COLS = ['object_id', 'time_years', 'x_au', 'y_au']


def validate_rows(rows, label=""):
    """Validate a list of row dicts. Returns (clean_rows, report).

    Checks: required columns, finite values, reasonable bounds,
    sufficient time coverage per tracer.
    Raises ValueError on fatal problems; warns on suspicious ones.
    """
    report = {"total": len(rows), "dropped": 0, "warnings": []}
    if not rows:
        raise ValueError(f"[{label}] No rows provided")
    # schema
    for col in REQUIRED_COLS:
        if not all(col in r for r in rows):
            raise ValueError(f"[{label}] Missing required column: {col}")
    clean = []
    for r in rows:
        ok = True
        for col in ['time_years', 'x_au', 'y_au']:
            v = r[col]
            if not math.isfinite(v):
                ok = False
                break
            lo, hi = BOUNDS[col]
            if not (lo <= v <= hi):
                ok = False
                break
        if ok:
            clean.append(r)
        else:
            report["dropped"] += 1
    # coverage: each tracer needs >= 3 distinct times
    by_oid = {}
    for r in clean:
        by_oid.setdefault(r['object_id'], set()).add(r['time_years'])
    thin = [oid for oid, times in by_oid.items() if len(times) < 3]
    if thin:
        report["warnings"].append(
            f"Tracers with <3 time points (unconstrained): {thin}")
    # time span
    times = sorted(set(r['time_years'] for r in clean))
    span = max(times) - min(times) if len(times) > 1 else 0
    if span < 0.5:
        report["warnings"].append(
            f"Short time span ({span:.2f} yr) — weak constraints on periods")
    report["clean"] = len(clean)
    report["n_tracers"] = len(by_oid)
    report["time_span_yr"] = span
    print(f"[{label}] Validation: {report['clean']}/{report['total']} rows, "
          f"{report['n_tracers']} tracers, span {span:.1f} yr", flush=True)
    for w in report["warnings"]:
        print(f"[{label}] WARNING: {w}", flush=True)
    if report["clean"] == 0:
        raise ValueError(f"[{label}] No valid rows after validation")
    return clean, report
