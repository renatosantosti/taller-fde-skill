# Core loop — audit, evals, deployment

The training requires the loop **audit → evals → deployment**. Use this order; do not start with the model.

## 1. Audit

Understand the process **before** proposing AI.

- Map steps, actors, systems, and data (`docs/workflow.md`).
- Classify each step: deterministic / LLM judgment / human-in-the-loop.
- List existing systems and integration contracts (`docs/deployment.md`).
- Separate what is already a rule (no LLM needed) from what is judgment.

Audit output: the map plus a list of what **not** to automate.

## 2. Evals

Measure model judgment **before** wiring it into the live flow.

- Cases in `evals/` (input, context, expected result, HITL notes).
- Cover the happy path, ambiguity, refusal, and invalid schema.
- An eval that never fails is not measuring anything.

Eval output: evidence that the LLM-judgment step is reliable enough, or that it should stay HITL.

## 3. Deployment

Integrate only what passed audit and evals.

- Explicit integration points with systems that already exist.
- Error handling on every model call (`src/errors.py`, `src/pipeline.py`).
- Human fallback on timeout, schema, policy, or low confidence.
- No silent side effect (email, ticket, payment) from unvalidated output.

## How an agent should work in this repo

1. Read `AGENTS.md` and `docs/brief.md`.
2. If the workflow is still TODO: stop and ask for the business case. Do not invent one.
3. If the workflow exists: change the map, strategy, and code together — the step type decides the code type (rule vs. LLM vs. HITL).
