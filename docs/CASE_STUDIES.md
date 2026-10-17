# Two small bugs that change the evidence

These examples are entirely synthetic and executable from the repository:

```bash
python3 -m examples.case_studies
```

## 1. A loss on day one disappears from drawdown

Start with 1,000. Lose 50 on the first day, then gain 20 on the second:

| Point | Equity | Peak including starting capital | Drawdown |
|---|---:|---:|---:|
| Start | 1,000 | 1,000 | 0 |
| Day 1 | 950 | 1,000 | 50 |
| Day 2 | 970 | 1,000 | 30 |

A calculation that takes a cumulative maximum only over `[950, 970]` reports
**zero** maximum drawdown. It has lost the starting-capital observation.
Including that observation produces the correct maximum drawdown of **50**.

This is a useful regression test even when a long series happens to reach a later
peak: the bug can be hidden by subsequent price movements.

## 2. An unknown observation becomes an invented zero

Consider three daily PnL observations: `10, unknown, 20`.

| Input treatment | What the report says |
|---|---|
| Replace the unknown with zero | Complete-looking series; total PnL 30 |
| Preserve the unknown | `incomplete`; aggregate metrics withheld |

We do not know the total PnL. The missing number could have either sign. The known
subtotal is not the full-period result. An expected-session calendar alone does
not catch the problem if the missing cell has already been overwritten with zero.

**The tool cannot recover uncertainty discarded upstream.** Preserve missingness
from ingestion onward and distinguish a recorded zero from a missing observation.

Blank cells may also arise when combining instruments with different calendars.
That is not automatically a lost market-data record. Identify the applicable
calendar, inspect the source, and document the classification. Do not replace all
blanks with zero or drop dates globally just to obtain a complete report.

## Why these examples exist

A maintainer-led compatibility trial found blank observations in a historical
wide-format table. Their dates exactly matched rows introduced by a calendar union.
The report withheld metrics as intended. That trial motivated the explicit-column
adapter and this explanation; it did not establish an upstream data-loss bug.

See [TRIAL_REPORT.md](TRIAL_REPORT.md) for the bounded evidence and limitations.
