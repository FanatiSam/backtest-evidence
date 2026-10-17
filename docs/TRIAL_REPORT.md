# Maintainer-led compatibility trial — 2026-10-17

This is an internal integration trial, not external adoption, an independent audit,
or a new evaluation of trading strategies. Private inputs remain private. This
document discloses only aggregate test counts and software behavior.

## Scope and handling

- Two existing, compact historical PnL exports from an already inspected research workflow.
- Five selected series, restricted to the previously used 2009–2023 period; the last
  evaluated observation was 2023-12-29. No present holdout outcomes were evaluated.
- Source code was inspected to establish that these were daily mark-to-market outputs
  with transaction costs, rather than realized-only trade totals. The trial did not
  independently verify the correctness of the upstream pricing or cost model.
- Inputs were read-only. Before/after file hashes matched. Private extracts and detailed
  receipts were retained outside this public repository. No private returns, positions,
  symbols, parameter values, paths, source fingerprints or strategy code are published here.
- A nominal capital rebase was used for diagnostic arithmetic. It is not a claim about
  actual source-account equity at the beginning of the cropped window.

## Results

| Check | Result |
|---|---|
| Four wide-table series | 3,784 rows each; 10 blank PnL cells each; all returned `incomplete` with metrics withheld |
| One narrow-table series | 3,774 rows, no blank PnL cells; returned `ok` |
| Wide-table blank dates | Exactly the 10 dates present only in the wide calendar union |
| Independent arithmetic implementation | Complete series matched Decimal-based total PnL, ending equity and both drawdown calculations |
| CLI versus Python API | Same results for all five selected series |
| Source preservation | Both source-file hashes unchanged |

The arithmetic cross-check used a separate Decimal loop, with relative tolerance
1e-10 and absolute tolerance 1e-7 against floating-point outputs. It did not use an
independent human reviewer and did not validate Sharpe against a separate real-data implementation.

## What changed because of this trial

Version 0.1.1 adds `--date-column` and `--pnl-column`. Users can select one PnL
series in a wide CSV without renaming columns or performing an implicit aggregation.
Blank cells remain blank, and unknown or ambiguous columns fail explicitly. A
synthetic wide table, regression tests, and reproducible case studies accompany it.

## What remains unverified

- There was no independent exchange calendar. Full market-session coverage is unknown.
  The program's `coverage_checked` remained false. Union-alignment gaps are not proof
  of lost observations, and the trial did not fill them or silently shrink the sample.
- The real exports lack timezone-aware availability and execution timestamps. Real-data
  event causality was **not tested**; only synthetic timestamp fixtures were tested.
- No strategy was rerun, optimized, promoted, or connected to a broker. No frozen
  validation system, original research result, or production service was modified.
- There are no claimed external testers, downloads, or community adoption metrics.

The public counterexamples are independently reproducible. The private-data trial
is a maintainer report, not publicly reproducible evidence about investment performance.
