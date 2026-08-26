# taller-fde-skill

Submission for **The AI Forward-Deployed Engineer (FDE)** training: a workflow map, an AI deployment strategy, and integration code that shows where AI belongs — and where it does not.

Public repository: [github.com/renatosantosti/taller-fde-skill](https://github.com/renatosantosti/taller-fde-skill)

## Purpose / company context

**TODO.** Choose a real or fictional company and one operational process. Until that exists, this README stays a scaffold: structure and grading sections are in place; business content is not invented.

- **Company:** TODO
- **Process:** TODO
- **Why AI might help:** TODO
- **What we refuse to automate:** TODO

## Workflow map

Criterion **#1** (weight x3). Full map: [docs/workflow.md](docs/workflow.md).

Every step is labeled as exactly one of **deterministic**, **LLM judgment**, or **human-in-the-loop**.

| ID | Step | Type | Notes |
|---|---|---|---|
| S1 | TODO | TODO | See `docs/workflow.md` |
| S2 | TODO | TODO | See `docs/workflow.md` |
| S3 | TODO | TODO | See `docs/workflow.md` |

## Deployment strategy

Criterion **#2** (weight x3). Full strategy: [docs/deployment.md](docs/deployment.md).

| Integration | Existing system | AI? | Rationale |
|---|---|---|---|
| I1 | TODO | TODO | TODO |

## Core loop

How this work follows **audit → evals → deployment**: [docs/core-loop.md](docs/core-loop.md).

1. **Audit** — map the process and classify steps before proposing a model.
2. **Evals** — measure LLM judgment with cases in [`evals/`](evals/).
3. **Deployment** — integrate only what audit and evals support, with fail-closed error handling in [`src/`](src/).

## How to run

Python 3.11+. No third-party package is required for the scaffold.

```bash
python -m src.pipeline
```

Expected today: the pipeline raises `NotImplementedError` until the workflow is chosen and the LLM adapter is implemented. Copy `evals/cases.example.json` to `evals/cases.json` when real cases exist (that file is gitignored if you later add secrets or production data).

## Design decisions

- **Single source of truth for agents:** `AGENTS.md`. Cursor, Claude Code, and Copilot native files are pointers, not copies.
- **Deterministic work stays code.** LLMs are reserved for non-deterministic judgment; humans keep risk, policy, and low-confidence cases.
- **Fail closed.** Timeout, invalid schema, policy refusal, or low confidence escalate to HITL — they do not trigger side effects.
- **English only.** All code, comments, docs, skills, and assistant pointers are English.

## Repository layout

```
AGENTS.md                 # agent-agnostic instructions
README.md                 # this submission README
docs/brief.md             # training brief + rubric
docs/workflow.md          # criterion #1
docs/deployment.md        # criterion #2
docs/core-loop.md         # audit → evals → deployment
src/                      # criteria #4 and #5
evals/                    # eval case format
skills/fde-assignment/    # canonical agent skill
```
