# evals

Eval cases for the **audit → evals → deployment** loop. Do not deploy an LLM step that has no cases covering the happy path, ambiguity, refusal, and invalid schema.

| File | Role |
|---|---|
| `cases.example.json` | Schema and empty placeholders — copy, do not invent business content |

When the workflow exists, add real cases (input, expected type of outcome, HITL notes). Keep production data and secrets out of git.
