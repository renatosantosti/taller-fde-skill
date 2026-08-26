# Deployment strategy

Grading criterion **#2 Deployment Strategy** (weight x3).

Decisions: [docs/adrs/](adrs/README.md).

## Existing systems

| System | Role today | Data it owns | Integration style | Notes |
|---|---|---|---|---|
| Channel adapters | Ingest email / form / WhatsApp | Raw lead files | Write to object store | Out of scope in this repo |
| Object store (`inbox/`) | Lead folders by stage | Files per `lead_id` | Filesystem here; S3/blob in production | See adr002 |
| Document intelligence | Normalize raw files to `.md`/`.txt` | Extracted text, tables, image captions | Move `input/` → `pending/` | Tesseract or Azure Document Intelligence — not implemented |
| CRM | Account / deal stage | Customer record | Stub only | Illustrative; no live HubSpot |
| HITL work item | Human-readable review packet | `intake.json`, `hitl.md` | `inbox/needs_human/` | Pull queue for reviewers |
| HITL bus | Control plane for pause/resume | `IntakeNeedsReview`, `IntakeDecision` | Port + **file bus** here; **Azure Service Bus** in production | See adr005 |
| MAF workflow + checkpoints | Graph, HITL pause, resume | Executor state | `FileCheckpointStorage` here; Cosmos possible in prod | See adr003 |
| LLM provider | Synthesize intake JSON | None persisted here | LiteLLM | See adr004 |

## Integration points

| ID | Workflow step | System | Integration | AI involved? | Rationale |
|---|---|---|---|---|---|
| I1 | S1–S2 | Channel adapters + `inbox/input/` | Adapters write folders | no | Do not couple the model to SMTP or WhatsApp. |
| I2 | S3 | Document intelligence | Service writes `.md`/`.txt` into `pending/` | no | OCR is a dedicated deterministic (or vendor) service. |
| I3 | S4–S7, S9–S10, S13 | Object store + worker | Pathlib moves and reads | no | Rules and file IO. |
| I4 | S8 | LiteLLM | `completion` with JSON schema | yes | Only unstructured → structured judgment. |
| I5 | S11–S12 | Bus port + `needs_human/` | Publish review; human publishes decision | no | HITL is a person, not a model. File bus stands in for Service Bus. |
| I6 | S12–S13 | MAF checkpoint | `request_info` / resume with responses | no | State, not generation. |

## Runtime shape

- **Trigger:** CLI over a pending `lead_id` (stand-in for a queue consumer on `pending/`).
- **Orchestrator:** Microsoft Agent Framework workflow. Deterministic executors call inbox/assemble/fit. The synthesize executor calls LiteLLM. HITL uses `ctx.request_info()` and `FileCheckpointStorage`.
- **Model boundary:** assembled dossier text in; JSON intake out; no side effects toward the lead.
- **HITL queue:** `IntakeNeedsReview` on the bus plus `inbox/needs_human/{lead_id}/`. Resume: `python -m src.pipeline resume <lead_id> --decision bid|decline|request_call`.
- **Observability:** stdout, eval cases in `evals/`, checkpoint files under `checkpoints/` (gitignored).

## Core loop in this deployment

See [core-loop.md](core-loop.md).

- **Audit:** this map; steps classified; extraction and channels named but not built.
- **Evals:** `evals/cases.example.json` plus unit tests (mocked LiteLLM, file bus pause/resume).
- **Deployment:** worker + file bus locally; swap `FileBus` for Azure Service Bus and `FileCheckpointStorage` for Cosmos without changing step types.

## Risks and non-goals

- Do not automate: email/WhatsApp to the lead, pricing, bid submission, OCR, live Service Bus, live CRM.
- Fail closed (human), not open (auto-send): timeout, schema, policy, low confidence, thin dossier, leftover binary, over-cap — see adr007.
