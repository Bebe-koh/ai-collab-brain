# AI Collaboration Protocol

## 1. Always read state.md before writing anything.
## 2. Always update state.md after making changes.
## 3. Always append a new log entry in /logs/.
## 4. Never delete or overwrite logs.
## 5. Keep context.json valid JSON.
## 6. Use clear commit messages:
- READ: ...
- WRITE: ...
- UPDATE: ...
- FIX: ...

## 7. Multi-agent conventions (added 2026-10-06)
- **One voice per hypothesis file.** `hypotheses/<slug>/README.md` is the
  shared summary. Routine progress goes in the agent's own environment;
  only durable state changes (verdicts, kills, revivals, new results)
  are written here, with the date and the agent's name.
- **Sign your writes.** End substantive updates with
  `(agent name, YYYY-MM-DD)`.
- **Never overwrite another agent's in-progress work.** If a section is
  marked `IN PROGRESS: <agent>`, add a dated note instead of editing it.
- **Branches for contested changes.** If you disagree with a recorded
  verdict, open the discussion in `logs/` and mark the hypothesis
  `under review` — do not silently rewrite the verdict.
- **Claims discipline.** No `validated`, `detected`, `falsified`, or
  `production-ready` labels without reproducible calculations, stated
  assumptions, proper statistics, and independent validation. Downgrade
  overstated claims even when quoting another agent.
- **Primary evidence wins.** Summaries and other models' reports are
  hypotheses. Check against code, data, and derivations before building
  on them.
- **Public repo.** No personal data, credentials, private identifiers,
  or non-public material. Ever.
- **Human operator direction overrides agent inference.** When in doubt,
  log the question and stop.
