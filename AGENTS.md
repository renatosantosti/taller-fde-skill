# taller-fde-skill

Source of truth for any coding assistant (Cursor, Claude Code, GitHub Copilot, Codex, Gemini). Each tool's native files **only point here** — do not duplicate rules.

## Purpose

Submission repository for **The AI Forward-Deployed Engineer (FDE)** training: Taller **project / RFP intake**.

## Current state

- The business case is chosen. Do not invent a different company or process.
- The pipeline **starts at `inbox/pending/`**. Do not implement Tesseract, Azure Document Intelligence, email, or WhatsApp.
- Orchestration is **Microsoft Agent Framework** (`src/workflow.py`). The only model call is **LiteLLM** (`src/llm.py`). HITL uses a **bus port** with a file-bus implementation (`src/bus.py`).
- Record new important technical decisions as the next file in `docs/adrs/` (`adr009.md`, …).
- **Do not commit, push, or `--amend` without explicit authorization.**

## Language

All code, comments, documentation, skills, ADRs, and assistant pointer files are **English**.

## Where each rubric criterion lives

| # | Criterion | Weight | File |
|---|---|---|---|
| 1 | Workflow mapping | x3 | `docs/workflow.md` |
| 2 | Deployment strategy | x3 | `docs/deployment.md` |
| 3 | README quality | x2 | `README.md` |
| 4 | Code clarity | x2 | `src/` |
| 5 | Error handling | x2 | `src/errors.py`, `src/workflow.py`, `src/llm.py` |

Also: `docs/adrs/`, `docs/brief.md`, `docs/core-loop.md`, `skills/fde-assignment/SKILL.md`.

## Required step classification

Every workflow step must be **exactly one** of:

- **deterministic** — rule, API, SQL, validation, routing on a known field.
- **LLM judgment** — interpretation, ambiguous classification, drafting, unstructured-text extraction.
- **human-in-the-loop** — risk, policy, exception, approval, fallback after a model failure.

Do not put an LLM on a deterministic step. Do not automate a HITL step without an escalation rule. S8 is the only LLM step in this repo.

## Code conventions

- Python 3.11+. Allowed packages: `agent-framework`, `litellm`, `python-dotenv`, `pytest`, `pytest-asyncio`, `pytest-cov`. Do not add LangGraph, LangChain, OCR, or Azure Service Bus SDKs.
- Short functions, explicit names, comments only for *why* (integration, failure, HITL).
- Every LLM call has error handling: timeout, invalid schema, refusal, provider failure, human fallback. Types in `src/errors.py`.
- No secrets in the repo. Credentials live in `.env` (gitignored).

## Native pointers

- Cursor: `.cursor/rules/`, `.cursor/skills/`
- Claude Code: `CLAUDE.md`, `.claude/skills/`
- GitHub Copilot: `.github/copilot-instructions.md`, `.github/instructions/`
