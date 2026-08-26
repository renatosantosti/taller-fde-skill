# Architecture decision records

Important technical choices for this FDE submission. One decision per file, numbered in order.

| ADR | Title |
|---|---|
| [adr001.md](adr001.md) | Start at pending; extraction is out of scope |
| [adr002.md](adr002.md) | Filesystem inbox as the object-store contract |
| [adr003.md](adr003.md) | Microsoft Agent Framework for workflow state and HITL |
| [adr004.md](adr004.md) | LiteLLM as the only model adapter |
| [adr005.md](adr005.md) | Bus port with a file bus; Azure Service Bus on the map only |
| [adr006.md](adr006.md) | Closed-loop HITL; never auto-message the lead |
| [adr007.md](adr007.md) | Fail closed to HITL |
| [adr008.md](adr008.md) | English-only repo artifacts |
| [adr009.md](adr009.md) | Tests mock LiteLLM; MAF runs in-process |

New important decisions continue as `adr010.md`.
