# Deployment strategy

Grading criterion **#2 Deployment Strategy** (weight x3).

Name the existing systems, the integration points, and why each point is (or is not) a place for AI.

## Existing systems

| System | Role today | Data it owns | Integration style | Notes |
|---|---|---|---|---|
| TODO | TODO | TODO | API / queue / DB / file / UI | TODO |

## Integration points

| ID | Workflow step | System | Integration | AI involved? | Rationale |
|---|---|---|---|---|---|
| I1 | TODO (link to step ID in `docs/workflow.md`) | TODO | TODO | yes / no | TODO |

## Runtime shape

- **Trigger:** TODO — webhook, cron, user action, queue consumer.
- **Orchestrator:** TODO — who calls the model vs. who stays deterministic.
- **Model boundary:** TODO — prompt/schema in; structured result out; never a silent side effect.
- **HITL queue:** TODO — where humans review, approve, or take over.
- **Observability:** TODO — logs, traces, eval snapshots.

## Core loop in this deployment

How **audit → evals → deployment** shows up here: see `docs/core-loop.md`. Fill after the workflow exists.

- Audit: TODO
- Evals: TODO (`evals/`)
- Deployment: TODO

## Risks and non-goals

- TODO — what we will not automate
- TODO — failure modes that must fail closed (human), not open (auto-send)
