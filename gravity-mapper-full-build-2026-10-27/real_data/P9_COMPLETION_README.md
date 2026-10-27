# P9 Population Model — Completion Instructions

Production is running autonomously via `launch_p9.py` (2 concurrent batch jobs,
checkpoint/resume every 250 Myr). If the driver dies (VM restart), relaunch:
```
cd ~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data
nohup ~/workspace/.venv-p9/bin/python launch_p9.py >> launch_p9.log 2>&1 &
```
It skips completed `.npz` files and resumes partial `.work.npz`+`.ckpt.bin`.

## When all 50 jobs are done

```bash
cd ~/workspace/goals/gravity-mapper-hidden-body-inference/hidden_files/real_data
~/workspace/.venv-p9/bin/python - <<'PYEOF'
import sys; sys.path.insert(0,'.')
from p9_population import merge_batches
for cfg in ['none','fiducial','close','far','lowmass']:
    merge_batches(f'p9_runs/merged_{cfg}.npz',
                  [f'p9_runs/{cfg}_b{b}.npz' for b in range(10)])
PYEOF
# Per-config Rayleigh analysis
for cfg in none fiducial close far lowmass; do
  ~/workspace/.venv-p9/bin/python analyze_runs.py p9_runs/merged_${cfg}.npz p9_runs/${cfg}.json
done
# Extended: attrition, 2D KS, observability cut, FPR (pairwise vs noP9)
for cfg in fiducial close far lowmass; do
  ~/workspace/.venv-p9/bin/python extend_analysis.py p9_runs/merged_none.npz p9_runs/merged_${cfg}.npz
done
```

## Key files
- `p9_population.py` — simulation (WHFast dt=8, REBOUNDx J2, 4 P9 configs, matched ICs, batching, checkpoint/resume)
- `analyze_runs.py` — Rayleigh/Kuiper per snapshot
- `extend_analysis.py` — attrition, Fasano-Franceschini 2D KS, q<40 observability cut, FPR
- `observed_clustering.py` / `observed_clustering.json` — observed benchmarks (full: Z=0.60, p=0.55)
- `../p9_population_note.md` — the note (fill in Results/Verdict when done)
- `conv_test.py`, `ias15_test.py` — integrator validation (both pass)

## If VM restarts
All state is in `p9_runs/`. Relaunch driver (above). Partial jobs resume bit-exactly.
The venv is at `~/workspace/.venv-p9` (persistent). `/tmp` is wiped on restart —
nothing needed lives there.
