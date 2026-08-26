# src

Integration stubs for grading criteria **#4 Code clarity** and **#5 Error handling**.

There is no company workflow here yet. `pipeline.py` shows the orchestration and failure pattern; `errors.py` names the failure modes. Replace `NotImplementedError` after the process is chosen — do not invent a business case in this folder.

| File | Role |
|---|---|
| `errors.py` | Typed failures: timeout, schema, policy, low confidence, HITL |
| `pipeline.py` | One pass: validate → (optional) LLM → parse → route or escalate |

Run from the repo root:

```bash
python -m src.pipeline
```
