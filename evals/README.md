# evals

Cases for **audit → evals → deployment**. Live provider calls are optional.

| Path | Role |
|---|---|
| `cases.example.json` | Expected outcomes per fixture / failure mode |
| `tests/unit/` | Module tests; LiteLLM `completion` mocked |
| `tests/integration/` | MAF workflow in-process; `call_llm` mocked |

CI must not use a real model, Azure Service Bus, or Document Intelligence (adr009). Keep production data out of git.
