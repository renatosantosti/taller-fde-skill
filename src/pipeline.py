"""CLI entry: runs the MAF intake workflow. Not a second orchestrator."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dotenv import load_dotenv

from src.assemble import assemble_dossier
from src.errors import ConfigError, NeedsHumanError, PipelineError
from src.inbox import find_lead, list_pending, validate_pending
from src.paths import INBOX_ROOT, REPO_ROOT


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Taller project-intake worker (pending folders only)."
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help="Validate and print the dossier. No LLM, no MAF.",
    )
    parser.add_argument("--list", action="store_true", help="List pending lead ids.")
    parser.add_argument("lead_id", nargs="?", help="Lead folder name under inbox/pending/.")
    return parser


def _resume_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m src.pipeline resume")
    parser.add_argument("lead_id")
    parser.add_argument("--decision", required=True, choices=["bid", "decline", "request_call"])
    parser.add_argument("--notes", default="")
    return parser


def assemble_only(lead_id: str) -> None:
    folder = find_lead(lead_id)
    validate_pending(folder)
    print(assemble_dossier(folder))


async def _async_main(args: argparse.Namespace) -> int:
    from src.workflow import run_lead

    if not args.lead_id:
        print("Provide a lead_id, --list, or resume.", file=sys.stderr)
        return 2
    try:
        result = await run_lead(args.lead_id)
    except ConfigError as exc:
        print(f"config: {exc}", file=sys.stderr)
        return 2
    except NeedsHumanError as exc:
        print(f"needs_human: {exc.reason}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv(REPO_ROOT / ".env")
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "resume":
        resume_args = _resume_parser().parse_args(argv[1:])

        async def _resume() -> int:
            from src.workflow import resume_lead

            result = await resume_lead(
                resume_args.lead_id, resume_args.decision, resume_args.notes
            )
            print(json.dumps(result, indent=2))
            return 0

        return asyncio.run(_resume())
    args = _parser().parse_args(argv)
    if args.list:
        print("\n".join(list_pending()) or "(none)")
        return 0
    if args.assemble_only:
        if not args.lead_id:
            print("assemble-only requires a lead_id", file=sys.stderr)
            return 2
        try:
            assemble_only(args.lead_id)
        except PipelineError as exc:
            print(f"needs_human: {exc}", file=sys.stderr)
            return 1
        return 0
    INBOX_ROOT.mkdir(parents=True, exist_ok=True)
    return asyncio.run(_async_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
