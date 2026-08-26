# File bus

JSON messages for HITL control plane. This folder stands in for Azure Service Bus.

- `intake-needs-review/{lead_id}.json` — worker → reviewer
- `intake-decisions/{lead_id}.json` — reviewer → worker

Runtime files are gitignored. See `docs/adrs/adr005.md`.
