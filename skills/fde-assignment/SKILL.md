---
name: fde-assignment
description: >-
  Guides work on The AI Forward-Deployed Engineer (FDE) assignment: classify
  steps (deterministic / LLM judgment / HITL), follow audit → evals →
  deployment, and fill in workflow, strategy, and code without inventing the
  business case. Use when editing README, docs/, src/, or evals/.
---

# FDE assignment

Canonical skill. Native pointers in `.cursor/skills/fde-assignment/` and `.claude/skills/fde-assignment/` point at this file.

## Before any edit

1. Read `AGENTS.md` and `docs/brief.md`.
2. If `docs/workflow.md` still has company/process TODOs, **do not invent** the case. Ask the owner.
3. Do not commit without explicit authorization.

## Rubric (the work must cover)

1. **Workflow mapping (x3)** — `docs/workflow.md`: each step has exactly one type.
2. **Deployment strategy (x3)** — `docs/deployment.md`: existing systems plus why each integration exists.
3. **README (x2)** — `README.md` in English, succinct, with useful Markdown.
4. **Code clarity (x2)** — `src/`, linear logic, comments for why.
5. **Error handling (x2)** — timeout, schema, refusal, HITL fallback; types in `src/errors.py`.

## FDE judgment

- Deterministic → code/rules, not an LLM.
- Judgment / unstructured text → LLM with a schema and evals.
- Risk, policy, exception, low confidence → human.
- Core loop: audit → evals → deployment (`docs/core-loop.md`). Never wire the model into the live flow without the first two.

## Integration

Every LLM call goes through `src/pipeline.py` (or a successor) and the errors in `src/errors.py`. Failure closes to a human, not to a side effect.
