"""CLI entry point for exploring MLB Stats API endpoints.

Usage::

    mlb-statsapi schedule date=07/01/2024
    mlb-statsapi game gamePk=745570 --output py
    mlb-statsapi --list-endpoints
    mlb-statsapi schedule --help-endpoint
"""

from __future__ import annotations

import argparse
import json
import sys
from pprint import pprint
from typing import Any

from pydantic import BaseModel

from mlb_statsapi import __version__
from mlb_statsapi.client.sync_client import MlbClient
from mlb_statsapi.endpoints.registry import ENDPOINTS
from mlb_statsapi.exceptions import MlbApiError, MlbValidationError

DEFAULTS: dict[str, dict[str, str]] = {
    "schedule": {"sportId": "1"},
    "teams": {"sportId": "1"},
    "standings": {"leagueId": "103,104"},
    "stats_leaders": {"sportId": "1", "leaderCategories": "homeRuns"},
}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mlb-statsapi",
        description="Query MLB Stats API endpoints and display results.",
    )
    parser.add_argument(
        "endpoint",
        nargs="?",
        help="endpoint name (e.g. schedule, game_boxscore)",
    )
    parser.add_argument(
        "params",
        nargs="*",
        metavar="KEY=VALUE",
        help="endpoint parameters as KEY=VALUE pairs",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "py"],
        default="json",
        help="output format (default: json)",
    )
    parser.add_argument(
        "-l",
        "--list-endpoints",
        action="store_true",
        help="list all available endpoints",
    )
    parser.add_argument(
        "-H",
        "--help-endpoint",
        action="store_true",
        help="show detailed info for the given endpoint",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def parse_params(raw: list[str]) -> dict[str, str]:
    """Parse KEY=VALUE pairs into a dict."""
    params: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid parameter '{item}'. Expected KEY=VALUE format.")
        key, value = item.split("=", 1)
        params[key] = value
    return params


def list_endpoints() -> None:
    """Print all endpoint names grouped by category."""
    groups: dict[str, list[str]] = {}
    for name in sorted(ENDPOINTS):
        prefix = name.split("_")[0] if "_" in name else name
        groups.setdefault(prefix, []).append(name)

    print(f"Available endpoints ({len(ENDPOINTS)} total):\n")
    for prefix, names in sorted(groups.items()):
        print(f"  {prefix + ':':20s} {', '.join(names)}")


def help_endpoint(name: str) -> None:
    """Print detailed info for a single endpoint."""
    name = name.replace("-", "_")
    ep = ENDPOINTS.get(name)
    if ep is None:
        print(f"Unknown endpoint: {name}", file=sys.stderr)
        print("Use --list-endpoints to see available endpoints.", file=sys.stderr)
        return

    print(f"Endpoint: {name}")
    print(f"  URL:             {ep.url_template}")
    print(f"  Version:         {ep.default_version}")

    if ep.path_params:
        path_str = ", ".join(
            f"{k}={v!r}" if v else k for k, v in ep.path_params.items()
        )
        print(f"  Path params:     {path_str}")

    if ep.query_params:
        print(f"  Query params:    {', '.join(ep.query_params)}")

    if ep.required_params and any(ep.required_params):
        groups = " OR ".join("(" + ", ".join(g) + ")" for g in ep.required_params if g)
        print(f"  Required:        {groups}")

    defaults = DEFAULTS.get(name)
    if defaults:
        default_str = ", ".join(f"{k}={v}" for k, v in defaults.items())
        print(f"  Defaults:        {default_str}")

    if ep.response_model:
        print(f"  Response model:  {ep.response_model.__name__}")

    if ep.note:
        print(f"  Note:            {ep.note}")


def format_output(result: BaseModel, mode: str) -> None:
    """Print result in the chosen format."""
    if mode == "json":
        print(result.model_dump_json(indent=2, by_alias=True))
    else:
        try:
            from rich.pretty import pprint as rich_pprint

            rich_pprint(result)
        except ImportError:
            pprint(result.model_dump())


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_endpoints:
        list_endpoints()
        return 0

    if not args.endpoint:
        parser.print_help()
        return 1

    endpoint = args.endpoint.replace("-", "_")

    if args.help_endpoint:
        help_endpoint(endpoint)
        return 0

    try:
        params = parse_params(args.params)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Apply sensible defaults (user params override)
    merged: dict[str, Any] = {**DEFAULTS.get(endpoint, {}), **params}

    try:
        with MlbClient() as client:
            result = client.get(endpoint, **merged)
    except MlbApiError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MlbValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        if e.raw_data:
            print(json.dumps(e.raw_data, indent=2))
        return 1

    format_output(result, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
