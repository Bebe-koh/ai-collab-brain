# Task Queue — multi-model worker loop

Atlas is the always-awake orchestrator. Grok and Perplexity are episodic
workers: they act when kicked, then go quiet. This file is the shared
state between Atlas's monitoring and their work.

## Protocol — read before taking a task

- Every task has a stable ID (`Q-001`) and a version (`v1`, `v2`, ...).
- The task's GitHub issue always shows the CURRENT version in full.
- Updates bump the version and append to the issue's changelog — never
  silent edits. If you read v1 and the issue now says v2, v2 wins; the
  changelog tells you exactly what changed.
- Status lifecycle: `QUEUED` → `ASSIGNED` (worker + time) → `DONE`
  (result link). Status lives in the issue body header and the table below.
- Kick format (one tap): `Do task Q-001 v1 (issue #7). Post findings as a
  comment on that issue; if you cannot post, return them in chat.`
- **Buffer rule: at least 2 tasks stay QUEUED ahead of anything assigned.**
  The watcher alerts if the buffer drops below 2, so workers never idle
  waiting for Atlas to write the next task.
- A task's instructions are complete and self-contained: exact file paths,
  no repo navigation, no downloads, no local execution (Perplexity-robust).
- Queue empty + nothing assigned = everybody rests. Tasks end; the queue
  never runs away.

## Task list

| ID    | Ver | Issue | Status | Task                                                      |
|-------|-----|-------|--------|-----------------------------------------------------------|
| Q-001 | v1  | #7    | QUEUED | Investigate the X4227 sub-threshold veto-passing candidate |
| Q-002 | v1  | #8    | QUEUED | Prior-art survey: achromaticity vetoes in (sub)mm pol.    |

## How the loop runs

1. Jase kicks a worker with the kick format above.
2. The worker reads its issue, does the task, posts results to the issue
   (or returns them in chat if posting fails).
3. Atlas's watcher (every ~30 min) checks assigned tasks for new results,
   verifies them against primary evidence, and drafts the next kick.
4. Results pasted in chat are reconciled in chat; GitHub-posted results
   are picked up by the watcher. Either path works.
