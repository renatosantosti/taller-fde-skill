# src

Criteria **#4 Code clarity** and **#5 Error handling**. Taller intake starts at `inbox/pending/`.

| File | Role |
|---|---|
| `pipeline.py` | CLI: run, `--assemble-only`, `resume` |
| `workflow.py` | MAF graph, checkpoint, HITL `request_info` |
| `llm.py` | LiteLLM only |
| `bus.py` | File bus port (`IntakeNeedsReview` / `IntakeDecision`) |
| `inbox.py` / `assemble.py` | Deterministic folder + dossier |
| `schema.py` | Intake JSON + illustrative fit rules |
| `errors.py` | Typed failures → HITL |
| `crm.py` | No-op CRM stub |

```bash
python -m src.pipeline --assemble-only lead-happy
python -m src.pipeline lead-happy
python -m src.pipeline resume lead-happy --decision bid --notes "..."
```
