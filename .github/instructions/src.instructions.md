---
applyTo: "src/**"
---

When editing `src/`, follow `AGENTS.md` and the code-clarity + error-handling rule.

- Rubric criteria #4 and #5: linear logic, comments for why, error handling on every LLM integration.
- Use the types in `src/errors.py`. Orchestration in `src/pipeline.py` (or a successor).
- Failures (timeout, schema, policy, low confidence) close to HITL — no silent side effects.
- Python 3.11+, stdlib first. No secrets in code.
