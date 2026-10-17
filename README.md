# Backtest Evidence

**Small, inspectable checks for the evidence behind a backtest.**

Backtest Evidence turns daily PnL, declared event timestamps and selected files into
machine-readable checks. It makes missing observations visible, includes starting
capital in drawdown calculations, and gives reviewers reproducible inputs.

Python 3.10+ · no runtime dependencies · no network calls · MIT licensed

> **Early project; v0.1.1 review candidate.** Developed from lessons in a private quantitative-research
> workflow. This is a new standalone implementation, not a public copy of that
> system. All included data is synthetic. External adoption and independent review
> have not yet been established. An `ok` result means only the documented checks
> passed; it is not evidence of profitability or a clean research history.

[繁體中文說明](README.zh-TW.md) · [Methodology](docs/METHODOLOGY.md) ·
[Contributing](CONTRIBUTING.md) · [Maintainer plan](docs/MAINTAINER_PLAN.md) ·
[Ten-minute trial](docs/TRY_IT.md) · [Executable case studies](docs/CASE_STUDIES.md) ·
[Internal trial report](docs/TRIAL_REPORT.md)

## Try it in one minute

```bash
git clone https://github.com/FanatiSam/backtest-evidence.git
cd backtest-evidence
python3 -m backtest_evidence report examples/daily_pnl.csv \
  --capital 1000 --sessions examples/sessions.csv
python3 -m unittest discover -s tests -v
```

For the 0.1.1 review candidate, check out `trial-and-case-studies` first. The main
branch remains the last published version until maintainer review is complete.

No installation or API key is needed to run from the repository. Optionally install
with `python3 -m pip install .` to use the `backtest-evidence` command elsewhere.
The package is not currently published on PyPI.

The synthetic five-session example produces:

| Measure | Value |
|---|---:|
| Net PnL | 100 |
| Ending equity | 1,100 |
| Maximum drawdown, amount | 50 |
| Maximum drawdown, fraction | 0.05 |
| PnL / maximum drawdown | 2.0 |
| Observed zero-PnL sessions | 1 |

These are arithmetic examples, not investment results. The example is far too
short for a meaningful estimate of risk-adjusted performance.

## What it checks

| Command | Input | Check |
|---|---|---|
| `report` | Daily net PnL CSV; optional expected-session CSV | Missingness, ordering, finite values, equity, drawdown, zero-RF Sharpe |
| `events` | Event CSV with timezone-aware timestamps | `available_at <= decision_at <= executed_at` |
| `research-window` | Observation-date CSV and OOS boundary | Every supplied date precedes the boundary |
| `manifest` | Explicit file allowlist | SHA-256 hashes and byte lengths, relative to a root |
| `verify` | Retained manifest and same files | Whether selected contents still match |

## Missing PnL stays missing

The `report` input has `date,pnl` columns, in strictly increasing `YYYY-MM-DD`
order. Supply **net daily mark-to-market PnL**, including all costs and open-position
valuation, with no deposits or withdrawals. One row means one observation; a zero
does not prove that no trading took place.

```bash
python3 -m backtest_evidence report examples/missing_pnl.csv \
  --capital 1000 --sessions examples/sessions.csv
```

This intentionally returns exit code **2**, `status: incomplete`, and
`metrics: null`. Blank, `NA` and `N/A` cells are unknown. NaN and infinity are
invalid, not missing. Omitted dates can only be detected when you provide an
authoritative expected-session calendar. The tool does not guess exchange holidays.

For a wide table or different header names, select exactly one series explicitly:

```bash
python3 -m backtest_evidence report examples/wide_pnl.csv --capital 1000 \
  --date-column session --pnl-column example_a --sessions examples/sessions.csv
```

No columns are summed automatically and no rows are dropped. Choosing `example_b`
returns `incomplete` because it contains a blank cell. The optional session calendar
still uses a `date` header. Missing or identical selected headers are input errors.

## Check declared causality

```bash
python3 -m backtest_evidence events examples/events.csv
python3 -m backtest_evidence events examples/future_event.csv
```

The second command deliberately fails with `DATA_AFTER_DECISION` and exit code 2.
All three timestamp columns must include a UTC offset. Comparisons use actual
instants, so different timezone offsets can be mixed safely. Equality is allowed
at the supplied resolution; the tool cannot prove ordering within the same timestamp.

```bash
python3 -m backtest_evidence research-window examples/sessions.csv \
  --oos-start 2024-01-09
```

This audits dates **already provided**. It neither blocks access to holdout data
nor proves that a researcher has never seen it. Apply real access controls separately.

## Retain an input fingerprint

```bash
mkdir -p reports
python3 -m backtest_evidence manifest --root . \
  examples/daily_pnl.csv examples/sessions.csv > reports/inputs.json
python3 -m backtest_evidence verify reports/inputs.json --root .
```

Files must be explicitly named, regular, non-symlink files inside the root.
There is no recursive directory collection. The output contains relative names,
hashes and sizes, not file contents. Review filenames before sharing a manifest.
Save its trusted copy in version control or an independent archive. Someone who
can replace both files and manifest can manufacture a match; a hash does not prove
when a strategy was frozen or that a holdout was unseen.

## Exit codes and integration

| Code | Meaning |
|---|---|
| `0` | Supplied checks passed, or manifest generated |
| `1` | Malformed input, I/O failure, or unsupported manifest |
| `2` | Completed check found incomplete/invalid evidence; also argparse usage errors |

Successful check execution prints JSON to stdout, including negative findings.
Input errors print an error object to stderr. Argument parsing errors use argparse's
standard text. Consumers should inspect both the exit code and the JSON status.

```python
from backtest_evidence.core import pnl_report

result = pnl_report(
    [{"date": "2024-01-02", "pnl": -50}, {"date": "2024-01-03", "pnl": 100}],
    initial_capital=1000,
    expected_sessions=["2024-01-02", "2024-01-03"],
)
assert result["metrics"]["max_drawdown_amount"] == 50
```

## Scope

This release does not implement trading strategies, execute orders, obtain market
data, model margin, validate fills, generate calendars, correct for multiple testing,
or certify an out-of-sample claim. It does not include the private research system,
production services, private strategy parameters, licensed data, or historical results.

Issues with a minimal synthetic example are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
