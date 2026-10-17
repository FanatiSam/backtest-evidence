# Changelog

## 0.1.1 — review candidate

- Select a single series in a wide CSV with explicit `--date-column` and
  `--pnl-column`; preserve missingness and reject missing/ambiguous selections.
- Add two executable synthetic counterexamples: first-observation drawdown loss
  and uncertainty hidden by upstream zero-filling.
- Document a maintainer-led historical-data trial and its limitations.
- Add a ten-minute trial guide, invitation draft and issue feedback template.
- Expand the regression suite from 19 to 22 tests and add the new examples to CI.

## 0.1.0 — 2026-10-17

- Initial public release: daily PnL reports, timestamp checks, research-window
  checks and explicit-file fingerprints, with synthetic examples and 19 tests.
