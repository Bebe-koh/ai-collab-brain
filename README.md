# ai-collab-brain

AI-first collaboration repository for coordinated work between multiple AI systems and the human operator.

## Purpose

This repository is a shared cognition layer for AI-to-AI and human-to-AI collaboration.  
Its job is to preserve context, reduce drift, maintain continuity across sessions, and let multiple agents work against the same evolving state without losing intent.

## Primary Use

This repo is not a normal software product repo.  
It is a coordination repo.

It exists to:
- store shared context
- track evolving project state
- define collaboration rules for agents
- preserve decisions, assumptions, and pending tasks
- provide handoff continuity between sessions, tools, and models

## Intended Participants

- AI agents operating on the repository
- Human operator maintaining direction and approval
- External automation or connectors that read/write structured state

## Source of Truth

Agents must treat the following files as canonical:

- `AI_PROTOCOL.md` — collaboration rules, behavior constraints, and operating procedure
- `state.md` — current active state of the project
- `context.json` — machine-readable shared context
- `logs/` — append-only operational history

If a conflict exists between files:
1. `AI_PROTOCOL.md`
2. `state.md`
3. `context.json`
4. `logs/`

## Operating Model

Each agent should:
1. Read this `README.md`
2. Read `AI_PROTOCOL.md`
3. Read `state.md`
4. Read `context.json`
5. Review the latest relevant file(s) in `logs/`
6. Perform only scoped updates
7. Leave a clear handoff note for the next agent

## Collaboration Rules

- Do not invent repository state.
- Do not delete context unless explicitly instructed.
- Do not rewrite canonical files without preserving intent.
- Prefer additive updates over destructive edits.
- Keep changes minimal, traceable, and reversible.
- When uncertain, log uncertainty instead of fabricating confidence.
- Preserve machine-readable structure where present.
- Human operator direction overrides agent inference.

## Update Protocol

When making changes:
- read before write
- update only the necessary file(s)
- record what changed
- explain why the change was made
- leave next-step guidance for the next agent

## Handoff Format

Each meaningful session should leave:

- `Summary:` what was done
- `Changes:` files updated
- `Open Questions:` unresolved items
- `Next Actions:` recommended next steps
- `Confidence:` low / medium / high

## Repository Layout

```text
.
├── README.md
├── AI_PROTOCOL.md
├── state.md
├── context.json
└── logs/
