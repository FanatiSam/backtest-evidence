# A ten-minute trial

We are looking for usability feedback from people who already work with daily PnL
or backtest exports. No API key, market-data subscription or private data upload is needed.

## Run the examples

The 0.1.1 changes are on the review branch until maintainer review is complete:

```bash
git clone --branch trial-and-case-studies https://github.com/FanatiSam/backtest-evidence.git
cd backtest-evidence
python3 -m unittest discover -s tests -v
python3 -m examples.case_studies
python3 -m backtest_evidence report examples/wide_pnl.csv \
  --capital 1000 --date-column session --pnl-column example_a \
  --sessions examples/sessions.csv
```

Expected: tests pass; the two counterexamples reproduce; the selected synthetic
series reports total PnL 100 and maximum drawdown 50.

Now select `--pnl-column example_b`. It deliberately returns exit code 2,
`status: incomplete`, and `metrics: null`. This is the expected result, not a crash.

## Optional: use your own compact CSV locally

Use only data you are authorized to inspect. Do not open an untouched holdout just
to test this software. Supply net daily mark-to-market PnL in one currency, with no
cash deposits or withdrawals. Keep the original file and missing cells unchanged.

```bash
python3 -m backtest_evidence report /path/to/development.csv \
  --capital 10000 --date-column date --pnl-column net_pnl
```

The capital above is only an example: use the actual starting equity appropriate
to your selected series. Without an independent expected-session calendar, full
coverage remains unknown. See [METHODOLOGY.md](METHODOLOGY.md).

## Tell us what happened

Open a GitHub issue with:

1. Python version and operating system.
2. The command, with private paths removed.
3. Whether setup worked without assistance.
4. The first confusing instruction or result.
5. A small synthetic reproduction if something failed.
6. Whether you tried only the examples or your own development data, and whether
   the result was useful. Either answer is valuable.

Do not attach credentials, private strategy details, account statements, proprietary
data, or untouched holdout observations. A star is not required. Feedback is the goal.

## Optional invitation text for the maintainer

> I have released a small Python tool that checks daily backtest evidence: missing
> PnL, starting-capital drawdown, timestamp ordering and input fingerprints. Would
> you be willing to spend about ten minutes trying the synthetic examples and
> telling me where the instructions or output are unclear? No account, API key
> or private data upload is needed. It is an early project; honest criticism is
> more useful than a star. Instructions: https://github.com/FanatiSam/backtest-evidence/blob/trial-and-case-studies/docs/TRY_IT.md

This is a draft invitation, not a record that anyone has been contacted.
