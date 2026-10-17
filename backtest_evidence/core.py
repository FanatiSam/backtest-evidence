"""Explicit dates, explicit missingness, and an initial-capital drawdown baseline."""
from __future__ import annotations

import math
import statistics
from datetime import date, datetime
from typing import Iterable, Mapping


def day(value: str) -> date:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("dates must be YYYY-MM-DD")
    return parsed


def finite(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    return number


def ordered_days(values: Iterable[str]) -> list[date]:
    dates = [day(v) for v in values]
    if not dates or any(a >= b for a, b in zip(dates, dates[1:])):
        raise ValueError("dates must be nonempty, unique, and strictly increasing")
    return dates


def pnl_report(rows: Iterable[Mapping[str, object]], initial_capital: float,
               expected_sessions: Iterable[str] | None = None,
               periods_per_year: int = 252) -> dict:
    """One net mark-to-market PnL observation per expected trading session."""
    capital = finite(initial_capital, "initial_capital")
    if capital <= 0:
        raise ValueError("initial_capital must be positive")
    if isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    rows = list(rows)
    dates = ordered_days(str(row["date"]) for row in rows)
    values = []
    for row in rows:
        raw = row["pnl"]
        missing = raw is None or (isinstance(raw, str) and raw.strip() in ("", "NA", "N/A"))
        values.append(None if missing else finite(raw, "pnl"))
    expected = ordered_days(expected_sessions) if expected_sessions is not None else dates
    unexpected = sorted(set(dates) - set(expected))
    if unexpected:
        raise ValueError("observed dates outside expected sessions")
    absent = sorted(set(expected) - set(dates))
    unknown = [d for d, v in zip(dates, values) if v is None]
    report = {
        "schema_version": 1,
        "status": "incomplete" if absent or unknown else "ok",
        "initial_capital": capital,
        "periods_per_year": periods_per_year,
        "observed_sessions": len(dates),
        "expected_sessions": len(expected) if expected_sessions is not None else None,
        "coverage_checked": expected_sessions is not None,
        "absent_sessions": [d.isoformat() for d in absent],
        "unknown_pnl_sessions": [d.isoformat() for d in unknown],
        "zero_pnl_sessions": sum(v == 0 for v in values),
        "metrics": None,
        "warnings": [] if expected_sessions is not None else ["Omitted sessions cannot be detected without an expected-session calendar."],
    }
    if absent or unknown:
        report["warnings"].append("Metrics withheld: missing PnL is not a zero or a no-trade observation.")
        return report
    equity = peak = capital
    max_dd = max_dd_pct = 0.0
    returns = []
    insolvent = False
    for pnl in values:
        prior = equity
        equity += pnl
        if not math.isfinite(equity):
            raise ValueError("equity calculation overflow")
        if prior > 0:
            returns.append(pnl / prior)
        if equity <= 0:
            insolvent = True
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        max_dd_pct = max(max_dd_pct, (peak - equity) / peak)
    sd = statistics.stdev(returns) if len(returns) > 1 and not insolvent else 0.0
    sharpe = statistics.mean(returns) / sd * math.sqrt(periods_per_year) if sd > 0 else None
    total = math.fsum(values)
    report["metrics"] = {
        "total_pnl": total,
        "ending_equity": equity,
        "total_return": total / capital,
        "max_drawdown_amount": max_dd,
        "max_drawdown_fraction": max_dd_pct,
        "pnl_over_max_drawdown": total / max_dd if max_dd else None,
        "sharpe_zero_rf": sharpe,
    }
    if insolvent:
        report["status"] = "invalid"
        report["warnings"].append("Equity reached zero or below; Sharpe withheld. Capital/execution feasibility requires separate review.")
    return report


def aware_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamps require an explicit UTC offset")
    return parsed


def audit_events(rows: Iterable[Mapping[str, str]]) -> dict:
    """Check declared available <= decision <= execution times; no market-data inference."""
    findings = []
    count = 0
    for count, row in enumerate(rows, 1):
        try:
            available, decision, executed = [aware_timestamp(row[k]) for k in
                                              ("available_at", "decision_at", "executed_at")]
        except (ValueError, TypeError, KeyError, AttributeError):
            findings.append({"row": count, "code": "INVALID_TIMESTAMP"})
            continue
        if available > decision:
            findings.append({"row": count, "code": "DATA_AFTER_DECISION"})
        if decision > executed:
            findings.append({"row": count, "code": "EXECUTION_BEFORE_DECISION"})
    if not count:
        findings.append({"row": None, "code": "EMPTY_EVENTS"})
    return {"status": "invalid" if findings else "ok", "rows": count, "findings": findings}


def check_research_dates(values: Iterable[str], oos_start: str) -> dict:
    """Audit supplied observation dates. This is not a filesystem access firewall."""
    boundary = day(oos_start)
    dates = ordered_days(values)
    violations = [d.isoformat() for d in dates if d >= boundary]
    return {"status": "invalid" if violations else "ok", "oos_start": boundary.isoformat(),
            "violating_dates": violations}
