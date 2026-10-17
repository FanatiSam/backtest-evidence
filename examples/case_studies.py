"""Two synthetic counterexamples. Run from the repo: python -m examples.case_studies."""
import json

from backtest_evidence.core import pnl_report


def reproduce() -> dict:
    # Incorrect implementation: the first recorded equity is treated as the peak.
    values = [-50, 20]
    equity = 1000
    recorded = []
    for value in values:
        equity += value
        recorded.append(equity)
    peak = recorded[0]
    naive_dd = 0
    for value in recorded:
        peak = max(peak, value)
        naive_dd = max(naive_dd, peak - value)
    rows = [{"date": "2024-01-02", "pnl": -50}, {"date": "2024-01-03", "pnl": 20}]
    correct = pnl_report(rows, 1000)
    assert naive_dd == 0
    assert correct["metrics"]["max_drawdown_amount"] == 50

    unknown = [{"date": "2024-01-02", "pnl": 10},
               {"date": "2024-01-03", "pnl": None},
               {"date": "2024-01-04", "pnl": 20}]
    dates = [r["date"] for r in unknown]
    filled = [{"date": r["date"], "pnl": 0 if r["pnl"] is None else r["pnl"]} for r in unknown]
    fabricated = pnl_report(filled, 1000, dates)
    honest = pnl_report(unknown, 1000, dates)
    assert fabricated["status"] == "ok"
    assert fabricated["metrics"]["total_pnl"] == 30
    assert honest["status"] == "incomplete"
    assert honest["metrics"] is None

    return {
        "initial_loss": {"synthetic": True, "initial_capital": 1000, "daily_pnl": values,
                         "naive_max_drawdown": naive_dd,
                         "correct_max_drawdown": correct["metrics"]["max_drawdown_amount"]},
        "missing_observation": {"synthetic": True,
                                "zero_filled_status": fabricated["status"],
                                "zero_filled_total_pnl": fabricated["metrics"]["total_pnl"],
                                "preserved_missing_status": honest["status"],
                                "preserved_missing_metrics": honest["metrics"],
                                "lesson": "A zero-filled input hides its original uncertainty; the tool cannot recover discarded missingness."},
    }


if __name__ == "__main__":
    print(json.dumps(reproduce(), indent=2))
