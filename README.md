# taller-fde-skill

Submission for **The AI Forward-Deployed Engineer (FDE)** training: a workflow map, an AI deployment strategy, and integration code that shows where AI belongs — and where it does not.

Public repository: [github.com/renatosantosti/taller-fde-skill](https://github.com/renatosantosti/taller-fde-skill)

## Purpose / company context

**Taller** is a software consultancy. This repo models **project / RFP intake**: a lead arrives with a message and attachments; Taller decides whether to bid, decline, or request a call.

- **Why AI might help:** Unstructured briefs need a structured intake (problem, constraints, urgency, open questions).
- **What we refuse to automate:** Emailing the lead, pricing, commercial commit, OCR, live CRM writes.

Channel adapters and document extraction (Tesseract or Azure Document Intelligence) are **on the map, not in this repo**. Work starts at `inbox/pending/` as `.md` / `.txt`. Production leads may be PT-BR; fixtures here are English.

Decisions: [docs/adrs/](docs/adrs/README.md).

## Workflow map

Criterion **#1** (weight x3). Full map: [docs/workflow.md](docs/workflow.md).

| ID | Step | Type |
|---|---|---|
| S1–S3 | Channels, raw drop, document intelligence | deterministic (out of scope) |
| S4–S7 | List, validate, claim, assemble dossier | deterministic |
| S8 | Synthesize intake (LiteLLM) | LLM judgment |
| S9–S11, S13 | Fit rules, fail-closed gate, publish, apply decision | deterministic |
| S12 | Human bid / decline / request call via bus | human-in-the-loop |

## Deployment strategy

Criterion **#2** (weight x3). Full strategy: [docs/deployment.md](docs/deployment.md).

| Integration | Existing system | AI? | Rationale |
|---|---|---|---|
| I1–I2 | Channel adapters + document intelligence | no | Do not couple the model to SMTP or OCR |
| I3 | Filesystem inbox (`inbox/`) | no | Object-store contract |
| I4 | LiteLLM | yes | Only unstructured → JSON |
| I5 | File bus (prod: Azure Service Bus) | no | HITL control plane |
| I6 | MAF checkpoints | no | Pause / resume state |

## Core loop

[docs/core-loop.md](docs/core-loop.md)

1. **Audit** — map and classify before proposing a model.
2. **Evals** — [`evals/`](evals/) plus `pytest` with mocked LiteLLM.
3. **Deployment** — worker + file bus locally; swap bus/checkpoint storage later without changing step types.

## How to run

Python 3.11+. Create a venv, then:

```bash
pip install -r requirements.txt
copy .env.example .env
```

Set `LLM_MODEL` and the matching provider key in `.env`. Never commit `.env`.

```bash
python -m src.pipeline --list
python -m src.pipeline --assemble-only lead-happy
python -m src.pipeline lead-happy
python -m src.pipeline resume lead-happy --decision bid --notes "Fits portal rebuild"
pytest
pytest --cov=src
```

`--assemble-only` needs no API key. A full run without `LLM_MODEL` fails closed with a config error. HITL pause writes `inbox/needs_human/{lead_id}/` and `bus/intake-needs-review/{lead_id}.json`. `resume` publishes `IntakeDecision` and continues the MAF checkpoint. Tests mock LiteLLM (see [adr009](docs/adrs/adr009.md)); they never call a live provider.

## Design decisions

- **Single source of truth for agents:** `AGENTS.md`.
- **MAF orchestrates; LiteLLM generates.** Not LangGraph. See adr003 and adr004.
- **Fail closed.** Timeout, schema, policy, thin dossier, leftover binary, over-cap → HITL. Never email the lead.
- **English only** in this repo. Record new technical choices as `docs/adrs/adr009.md` onward.

## Repository layout

```
docs/workflow.md          # criterion #1
docs/deployment.md        # criterion #2
docs/adrs/                # architecture decision records
inbox/input/              # raw drops (not read here)
inbox/pending/            # normalized .md/.txt fixtures
src/workflow.py           # MAF graph + HITL
src/llm.py                # LiteLLM adapter
src/bus.py                # file bus port
src/pipeline.py           # CLI
tests/unit/               # module tests; LiteLLM mocked
tests/integration/        # MAF in-process; call_llm mocked
```
