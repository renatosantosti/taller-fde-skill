# Core loop — audit, evals, deployment

The training requires **audit → evals → deployment**. This intake workflow follows that order.

## 1. Audit

- Map: [workflow.md](workflow.md) (S1–S13 classified).
- Systems: [deployment.md](deployment.md). Extraction and channels named, not built.
- Only S8 is LLM judgment. Commercial action is HITL (S12).
- ADRs: [adrs/README.md](adrs/README.md).

## 2. Evals

- Cases: [evals/cases.example.json](../evals/cases.example.json).
- `pytest --cov=src` mocks LiteLLM: happy path completes; unknown engagement pauses; `resume --decision decline` does not call the model again. Unit tests live under `tests/unit/`; MAF HITL under `tests/integration/`.
- Cover schema/policy by mapping those errors to HITL (adr007).

## 3. Deployment

- Worker CLI + filesystem inbox + file bus locally.
- Production swaps: FileBus → Azure Service Bus; FileCheckpointStorage → Cosmos; pending writer → Document Intelligence.
- Fail closed. No email to the lead from model output.

## How an agent should work in this repo

1. Read `AGENTS.md` and `docs/brief.md`.
2. Do not implement OCR or live channels.
3. Keep step types, ADRs, and code aligned. New technical decisions get `docs/adrs/adr009.md` onward.
