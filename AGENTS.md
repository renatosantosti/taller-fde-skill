# taller-fde-skill

Source of truth for any coding assistant (Cursor, Claude Code, GitHub Copilot, Codex, Gemini). Each tool's native files **only point here** — do not duplicate rules.

## Purpose

Submission repository for **The AI Forward-Deployed Engineer (FDE)** training. Demonstrate FDE judgment: map a workflow, classify each step, and decide where (and where not) to apply AI.

## Current state (scaffold)

- Structure, rubric, and integration patterns are in place.
- **Do not invent** a company, process, or business content. Fill `docs/workflow.md` and `docs/deployment.md` only after the owner chooses the case.
- **Do not commit, push, or `--amend` without explicit authorization.**

## Language

All code, comments, documentation, skills, and assistant pointer files are **English**. Do not add Portuguese (or any other language) to repo artifacts.

## Where each rubric criterion lives

| # | Criterion | Weight | File |
|---|---|---|---|
| 1 | Workflow mapping | x3 | `docs/workflow.md` |
| 2 | Deployment strategy | x3 | `docs/deployment.md` |
| 3 | README quality | x2 | `README.md` |
| 4 | Code clarity | x2 | `src/` |
| 5 | Error handling | x2 | `src/errors.py`, `src/pipeline.py` |

Rubric detail and disqualification: `docs/brief.md`. Methodology audit → evals → deployment: `docs/core-loop.md`. Assignment skill: `skills/fde-assignment/SKILL.md`.

## Required step classification

Every workflow step must be **exactly one** of:

- **deterministic** — rule, API, SQL, validation, routing on a known field.
- **LLM judgment** — interpretation, ambiguous classification, drafting, unstructured-text extraction.
- **human-in-the-loop** — risk, policy, exception, approval, fallback after a model failure.

Do not put an LLM on a deterministic step. Do not automate a HITL step without an escalation rule.

## Code conventions

- Python 3.11+, stdlib first; no heavy framework until the owner asks.
- Short functions, explicit names, comments only for *why* (integration, failure, HITL).
- Every LLM call has error handling: timeout, invalid schema, refusal, human fallback. Use the types in `src/errors.py`.
- No secrets in the repo. Credentials live in `.env` (gitignored).

## Native pointers

- Cursor: `.cursor/rules/`, `.cursor/skills/`
- Claude Code: `CLAUDE.md`, `.claude/skills/`
- GitHub Copilot: `.github/copilot-instructions.md`, `.github/instructions/`
