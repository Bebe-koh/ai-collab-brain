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
- **One task per kick.** Do ONLY the single task named in your kick, then
  stop and report. Do not take the next task from the queue on your own —
  workers cannot claim tasks, so uncoordinated continuation causes
  duplicate work (Grok duplicated Q-002 on 2026-10-06; harmless once,
  wasteful as a habit).
- **Buffer rule: at least 2 tasks stay QUEUED ahead of anything assigned.**
  The watcher alerts if the buffer drops below 2, so workers never idle
  waiting for Atlas to write the next task. Depth target is 4-6 real
  tasks; never pad with busywork — verification bandwidth, not queue
  depth, is the binding constraint.
- A task's instructions are complete and self-contained: exact file paths,
  no repo navigation, no downloads, no local execution (Perplexity-robust).
- Queue empty + nothing assigned = everybody rests. Tasks end; the queue
  never runs away.

## Task list

| ID    | Ver | Issue | Status | Task                                                      |
|-------|-----|-------|--------|-----------------------------------------------------------|
| Q-001 | v1  | #7    | DONE   | Investigate the X4227 sub-threshold veto-passing candidate |
| Q-002 | v1  | #8    | DONE   | Prior-art survey: achromaticity vetoes in (sub)mm pol.    |
| Q-003 | v1  | #9    | QUEUED | Independent reimplementation cross-check of v2 null99     |
| Q-004 | v1  | #10   | QUEUED | ALMA Band 6 EVPA systematics budget, 10-120 min scales    |
| Q-005 | v1  | #11   | QUEUED | EHT 2018/2021 calibrator-scan scoping for R(t)             |

## How the loop runs

1. Jase kicks a worker with the kick format above (one task per kick).
2. The worker reads its issue, does the task, posts results to the issue
   (or returns them in chat if posting fails), then stops.
3. Atlas's watcher (every ~3 min, approval-free anonymous polling) checks
   assigned tasks for new results, verifies them against primary evidence,
   and drafts the next kick.
4. Results pasted in chat are reconciled in chat; GitHub-posted results
   are picked up by the watcher. Either path works.
