from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .core import audit_events, check_research_dates, pnl_report
from .manifest import create_manifest, verify_manifest


def read_csv(path: str, required: set[str]) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not required.issubset(fields):
            raise ValueError("CSV requires unique headers including: " + ", ".join(sorted(required)))
        rows = list(reader)
        if any(None in row or any(row[k] is None for k in required) for row in rows):
            raise ValueError("CSV has malformed rows")
        return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit supplied backtest evidence. No broker or network access.")
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report", help="Net daily PnL, missingness and drawdown")
    report.add_argument("pnl_csv")
    report.add_argument("--capital", type=float, required=True)
    report.add_argument("--sessions", help="CSV with one expected session per date row")
    report.add_argument("--periods-per-year", type=int, default=252)
    report.add_argument("--date-column", default="date", help="Observation date column in the PnL CSV")
    report.add_argument("--pnl-column", default="pnl", help="Exactly one net daily PnL column; no automatic aggregation")
    events = commands.add_parser("events", help="Audit declared timestamp causality")
    events.add_argument("events_csv")
    boundary = commands.add_parser("research-window", help="Audit observation dates against an OOS boundary")
    boundary.add_argument("dates_csv")
    boundary.add_argument("--oos-start", required=True)
    manifest = commands.add_parser("manifest", help="Hash explicit relative files; writes JSON to stdout")
    manifest.add_argument("--root", type=Path, default=Path("."))
    manifest.add_argument("files", nargs="+")
    verify = commands.add_parser("verify", help="Compare files with a retained manifest")
    verify.add_argument("manifest_json", type=Path)
    verify.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        if args.command == "report":
            if args.date_column == args.pnl_column:
                raise ValueError("date and PnL columns must be different")
            source_rows = read_csv(args.pnl_csv, {args.date_column, args.pnl_column})
            rows = [{"date": row[args.date_column], "pnl": row[args.pnl_column]} for row in source_rows]
            sessions = [r["date"] for r in read_csv(args.sessions, {"date"})] if args.sessions else None
            result = pnl_report(rows, args.capital, sessions, args.periods_per_year)
        elif args.command == "events":
            result = audit_events(read_csv(args.events_csv, {"available_at", "decision_at", "executed_at"}))
        elif args.command == "research-window":
            result = check_research_dates([r["date"] for r in read_csv(args.dates_csv, {"date"})], args.oos_start)
        elif args.command == "manifest":
            result = create_manifest(args.root, args.files)
        else:
            result = verify_manifest(args.root, json.loads(args.manifest_json.read_text(encoding="utf-8")))
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0 if result.get("status", "ok") == "ok" else 2
    except (ValueError, TypeError, KeyError, OSError, OverflowError, AttributeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
