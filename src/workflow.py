"""Microsoft Agent Framework workflow for Taller intake (adr003, adr006)."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Never

from agent_framework import (
    Executor,
    FileCheckpointStorage,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    response_handler,
)

from src.assemble import assemble_dossier
from src.bus import (
    TOPIC_DECISION,
    TOPIC_REVIEW,
    FileBus,
    IntakeDecision,
    IntakeNeedsReview,
    decision_payload,
    review_payload,
)
from src.crm import record_intake
from src.errors import (
    ConfigError,
    LeftoverBinaryError,
    LlmProviderError,
    LlmTimeoutError,
    LowConfidenceError,
    NeedsHumanError,
    PolicyError,
    SchemaError,
    ThinDossierError,
)
from src.inbox import claim, lead_dir, move_lead, validate_pending
from src.llm import call_llm
from src.paths import CHECKPOINTS_ROOT, INBOX_ROOT, LEAD_INDEX_DIR
from src.schema import fit_requires_human, parse_intake

WORKFLOW_NAME = "taller-intake"


@dataclass
class PreparedLead:
    lead_id: str
    folder: str
    dossier: str
    error: str | None = None


@dataclass
class HitlRequest:
    lead_id: str
    reason: str
    intake: dict[str, Any] | None = None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _save_lead_index(lead_id: str, checkpoint_id: str, request_id: str) -> None:
    LEAD_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(
        LEAD_INDEX_DIR / f"{lead_id}.json",
        {"checkpoint_id": checkpoint_id, "request_id": request_id, "workflow_name": WORKFLOW_NAME},
    )


def load_lead_index(lead_id: str) -> dict[str, str]:
    path = LEAD_INDEX_DIR / f"{lead_id}.json"
    if not path.exists():
        raise NeedsHumanError(f"No HITL checkpoint index for {lead_id}. Run the pipeline first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_hitl_packet(lead_id: str, reason: str, intake: dict[str, Any] | None) -> None:
    folder = move_lead(lead_id, "needs_human")
    _write_json(folder / "intake.json", intake or {})
    (folder / "hitl.md").write_text(
        f"# HITL: {lead_id}\n\n**Reason:** {reason}\n\n"
        "Decide `bid`, `decline`, or `request_call`. "
        "Do not email the lead from this workflow.\n",
        encoding="utf-8",
    )


class PrepareExecutor(Executor):
    """S4–S7: list is CLI-side; validate, claim, assemble. Never reads inbox/input/."""

    @handler
    async def start(self, lead_id: str, ctx: WorkflowContext[PreparedLead]) -> None:
        analysis = claim(lead_id)
        error: str | None = None
        dossier = ""
        try:
            validate_pending(analysis)
            dossier = assemble_dossier(analysis)
        except (LeftoverBinaryError, ThinDossierError, NeedsHumanError) as exc:
            error = str(exc)
        await ctx.send_message(
            PreparedLead(lead_id=lead_id, folder=str(analysis), dossier=dossier, error=error)
        )


class SynthesizeExecutor(Executor):
    """S8–S13: LiteLLM synthesize, fit gate, bus HITL, resume."""

    def __init__(self, bus: FileBus | None = None, id: str | None = None) -> None:
        super().__init__(id=id or "synthesize")
        self._bus = bus or FileBus()

    @handler
    async def synthesize(
        self, prepared: PreparedLead, ctx: WorkflowContext[Never, dict]
    ) -> None:
        if prepared.error:
            await self._pause_for_human(prepared.lead_id, prepared.error, None, ctx)
            return
        try:
            raw = call_llm(prepared.dossier)
            intake = parse_intake(raw)
            fit_reason = fit_requires_human(intake)
            if fit_reason:
                raise LowConfidenceError(fit_reason)
        except (
            ConfigError,
            LlmTimeoutError,
            LlmProviderError,
            SchemaError,
            PolicyError,
            LowConfidenceError,
        ) as exc:
            await self._pause_for_human(prepared.lead_id, str(exc), None, ctx)
            return
        completed = move_lead(prepared.lead_id, "completed")
        _write_json(completed / "intake.json", intake)
        record_intake(prepared.lead_id, intake, decision=None)
        await ctx.yield_output(
            {"status": "ok", "lead_id": prepared.lead_id, "intake": intake}
        )

    async def _pause_for_human(
        self,
        lead_id: str,
        reason: str,
        intake: dict[str, Any] | None,
        ctx: WorkflowContext[Never, dict],
    ) -> None:
        review = IntakeNeedsReview(lead_id=lead_id, reason=reason, intake=intake)
        self._bus.publish(TOPIC_REVIEW, lead_id, review_payload(review))
        _write_hitl_packet(lead_id, reason, intake)
        record_intake(lead_id, intake, decision=None)
        await ctx.request_info(
            request_data=HitlRequest(lead_id=lead_id, reason=reason, intake=intake),
            response_type=IntakeDecision,
        )

    @response_handler
    async def on_decision(
        self,
        original_request: HitlRequest,
        response: IntakeDecision,
        ctx: WorkflowContext[Never, dict],
    ) -> None:
        allowed = {"bid", "decline", "request_call"}
        decision = response.decision.strip().lower()
        if decision not in allowed:
            decision = "request_call"
        completed = move_lead(original_request.lead_id, "completed")
        packet = {
            "intake": original_request.intake or {},
            "hitl_reason": original_request.reason,
            "decision": decision,
            "notes": response.notes,
        }
        _write_json(completed / "intake.json", packet)
        record_intake(original_request.lead_id, original_request.intake, decision)
        await ctx.yield_output(
            {
                "status": "completed_after_hitl",
                "lead_id": original_request.lead_id,
                "decision": decision,
            }
        )


def build_workflow(*, bus: FileBus | None = None) -> Any:
    storage = FileCheckpointStorage(
        CHECKPOINTS_ROOT,
        allowed_checkpoint_types=[
            "src.workflow:PreparedLead",
            "src.workflow:HitlRequest",
            "src.bus:IntakeDecision",
        ],
    )
    prepare = PrepareExecutor(id="prepare")
    synthesize = SynthesizeExecutor(bus=bus, id="synthesize")
    return (
        WorkflowBuilder(
            start_executor=prepare,
            checkpoint_storage=storage,
            name=WORKFLOW_NAME,
            output_from=[synthesize],
        )
        .add_edge(prepare, synthesize)
        .build()
    ), storage


async def run_lead(lead_id: str, *, bus: FileBus | None = None) -> dict[str, Any]:
    bus = bus or FileBus()
    workflow, storage = build_workflow(bus=bus)
    result = await workflow.run(lead_id)
    pending = _pending_requests(result)
    if pending:
        request_id, _payload = pending[0]
        latest = await storage.get_latest(workflow_name=WORKFLOW_NAME)
        if latest is None:
            raise NeedsHumanError("HITL requested but no checkpoint was saved.")
        _save_lead_index(lead_id, latest.checkpoint_id, request_id)
        return {
            "status": "needs_human",
            "lead_id": lead_id,
            "request_id": request_id,
            "checkpoint_id": latest.checkpoint_id,
        }
    outputs = result.get_outputs() if hasattr(result, "get_outputs") else []
    if outputs:
        return outputs[-1]
    return {"status": "ok", "lead_id": lead_id}


async def resume_lead(
    lead_id: str,
    decision: str,
    notes: str = "",
    *,
    bus: FileBus | None = None,
) -> dict[str, Any]:
    bus = bus or FileBus()
    payload = IntakeDecision(lead_id=lead_id, decision=decision, notes=notes)
    bus.publish(TOPIC_DECISION, lead_id, decision_payload(payload))
    index = load_lead_index(lead_id)
    workflow, _storage = build_workflow(bus=bus)
    result = await workflow.run(
        checkpoint_id=index["checkpoint_id"],
        responses={index["request_id"]: payload},
    )
    outputs = result.get_outputs() if hasattr(result, "get_outputs") else []
    if outputs:
        return outputs[-1]
    return {"status": "completed_after_hitl", "lead_id": lead_id, "decision": decision}


def _pending_requests(result: Any) -> list[tuple[str, Any]]:
    events = list(result) if result is not None else []
    if hasattr(result, "get_request_info_events"):
        info = result.get_request_info_events()
        return [(e.request_id, e.data) for e in info]
    pending: list[tuple[str, Any]] = []
    for event in events:
        if getattr(event, "type", None) == "request_info":
            pending.append((event.request_id, event.data))
    return pending
