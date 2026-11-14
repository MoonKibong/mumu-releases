"""Terminal interface for the hosted mumu service."""

import argparse
import json
import sys
from pathlib import Path

from mumu.remote_client import RemoteClientError, call_remote_tool

DEFAULT_TOP_K = 3


def _load_context(path: Path | None) -> dict | None:
    if path is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _print_result(result: dict, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(_as_text(result))


def _as_text(result: dict) -> str:
    lines = []
    for key, value in result.items():
        if isinstance(value, (dict, list)):
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pattern recommendation engine CLI")
    parser.add_argument(
        "--server",
        required=True,
        help="Remote mumu server URL (e.g. https://mumu.example.com). Reads the API key "
        "from MUMU_API_KEY.",
    )
    subparsers = parser.add_subparsers(dest="command")

    rec = subparsers.add_parser("recommend", help="Recommend patterns")
    rec.add_argument("query", help="Issue description")
    rec.add_argument("--context", type=Path, help="Context JSON file")
    rec.add_argument("--lang", choices=["en", "ko"], default="en")
    rec.add_argument("--format", choices=["json", "text"], default="json")
    rec.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    rec.add_argument("--intake", type=Path, help="Intake JSON file (see intake-form)")

    form = subparsers.add_parser("intake-form", help="Print the structured intake form")
    form.add_argument("scope", choices=["ux", "software", "mixed"])
    form.add_argument("--lang", choices=["en", "ko"], default="en")
    form.add_argument("--format", choices=["json", "text"], default="json")

    show = subparsers.add_parser("show", help="Show pattern details")
    show.add_argument("pattern_id", help="Pattern ID or alias")
    show.add_argument("--lang", choices=["en", "ko"], default="en")
    show.add_argument("--format", choices=["json", "text"], default="json")

    related = subparsers.add_parser("related", help="Expand typed relations for a pattern")
    related.add_argument("pattern_id", help="Pattern ID or alias")
    related.add_argument("--context", type=Path, help="Context JSON file")
    related.add_argument("--max-depth", type=int, default=5)
    related.add_argument("--max-nodes", type=int, default=100)
    related.add_argument("--format", choices=["json", "text"], default="json")

    check = subparsers.add_parser("check", help="Check composition of selected patterns")
    check.add_argument("pattern_ids", nargs="+", help="Pattern IDs or aliases")
    check.add_argument("--couplings", type=Path, help="JSON file: list of [id, id] pairs")
    check.add_argument("--context", type=Path, help="Context JSON file")
    check.add_argument("--format", choices=["json", "text"], default="json")

    return parser


def main() -> int:
    """Main CLI entry point: every command calls the remote mumu server."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "recommend":
            context = _load_context(args.context)
            arguments = {"query": args.query, "lang": args.lang, "top_k": args.top_k}
            if context is not None:
                arguments["context"] = context
            intake = _load_context(args.intake)
            if intake is not None:
                arguments["intake"] = intake
            result = call_remote_tool(args.server, "recommend_patterns", arguments)
            _print_result(result, args.format)
            return 0

        if args.command == "intake-form":
            result = call_remote_tool(
                args.server, "get_intake_form", {"scope": args.scope, "lang": args.lang}
            )
            _print_result(result, args.format)
            return 0

        if args.command == "show":
            result = call_remote_tool(
                args.server, "get_pattern", {"pattern_id": args.pattern_id, "lang": args.lang}
            )
            _print_result(result, args.format)
            return 0

        if args.command == "related":
            context = _load_context(args.context)
            arguments = {
                "pattern_id": args.pattern_id,
                "max_depth": args.max_depth,
                "max_nodes": args.max_nodes,
            }
            if context is not None:
                arguments["context"] = context
            result = call_remote_tool(args.server, "get_related_patterns", arguments)
            _print_result(result, args.format)
            return 0

        if args.command == "check":
            context = _load_context(args.context)
            couplings = None
            if args.couplings:
                with open(args.couplings, "r", encoding="utf-8") as f:
                    couplings = json.load(f)
            arguments = {"ids": args.pattern_ids, "couplings": couplings}
            if context is not None:
                arguments["context"] = context
            result = call_remote_tool(args.server, "check_composition", arguments)
            _print_result(result, args.format)
            return 0
    except (OSError, json.JSONDecodeError):
        print("Input file failed. Correct the private JSON file and its permissions, then retry.", file=sys.stderr)
        return 1
    except RemoteClientError as e:
        print(str(e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
