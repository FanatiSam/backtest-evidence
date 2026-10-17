# Agent instructions

- Read README.md and docs/METHODOLOGY.md before changing accounting behavior.
- Run `python3 -m unittest discover -s tests -v` and the documented positive examples.
- Preserve missingness, starting-capital drawdown, timezone awareness, and fail-closed input validation.
- All committed fixtures must be synthetic and redistributable.
- Never introduce credentials, proprietary strategies, private datasets, or private repository history.
- Do not claim profitability, independent OOS validation, adoption, or an audit that did not occur.
- Keep changes bounded. No network calls or broker/order functionality belong in the core.
- AI-generated changes require human review before merging; tests are necessary but not sufficient.
