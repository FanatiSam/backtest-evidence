# Methodology and limits

## Accounting conventions

For initial capital C and per-session net PnL p[t]:

- E[0] = C; E[t] = E[t-1] + p[t]. No compounding is imposed on dollar PnL.
- H[t] = max(C, E[1], ..., E[t]). The initial capital is included in the peak.
- Maximum drawdown amount = max(H[t] - E[t]), a nonnegative number.
- Maximum drawdown fraction = max((H[t] - E[t]) / H[t]). This may occur on a different
  date from the maximum currency drawdown. Fractions are not percentages.
- PnL / maximum drawdown = sum(p[t]) / maximum drawdown amount.
  It is null if drawdown is zero, not an invented zero or infinity.
- Session return r[t] = p[t] / E[t-1]. Zero-RF Sharpe is mean(r) divided by the
  sample standard deviation (ddof=1), multiplied by sqrt(periods_per_year).
  The annualization factor defaults to 252 and is configurable; it is an assumption,
  not an inferred exchange calendar. This is not a fixed-notional return series.
- Sharpe is null for fewer than two observations, zero volatility, or any nonpositive
  equity. Nonpositive equity also marks the report invalid while retaining dollar
  PnL and drawdown for diagnosis. Serial dependence and small samples can make the
  annualized Sharpe misleading.

Use a single currency and daily mark-to-market PnL after commissions, slippage,
financing and all other costs. Realized-only trade PnL cannot reconstruct the equity
path while positions are open. Deposits/withdrawals must be handled upstream; the
tool does not classify cashflows. No cost or execution-realism audit is performed.

Unknown PnL or missing expected sessions causes all aggregate metrics to be withheld.
Do not silently intersect or fill date ranges to obtain a passing report. Calendars
are caller supplied; only the given list is checked. Without that list, `status: ok`
does not mean coverage is complete. CSV inputs are loaded into memory; this release
is for compact daily evidence, not tick archives.

## Timestamp evidence

`available_at` must mean when information was actually accessible to the strategy,
including publication/ingestion delay, rather than merely its market observation
date. An internally consistent fabricated timestamp will still pass. The check does
not infer holidays, DST zones, quote staleness, bar-close semantics, minimum latency,
or executable prices. A timezone offset identifies the instant; correctness of the
offset is the caller's responsibility.

## OOS dates

`research-window` expects the observation/session date, not an earlier lagged feature
date. The OOS start is excluded from development. These checks run after the supplied
CSV has been opened. They do not enforce access control, track prior selection,
implement an embargo, or authorize opening a holdout. WFA or parameter selection on
a period means it has been used; a passing date check cannot reverse that history.

## Fingerprints

SHA-256 verification only compares the files explicitly named in the manifest.
Unlisted files and configuration outside those files are not covered. Missing files
and unsafe paths are errors. Content mismatch is an invalid result. The root itself
must be trusted. Symlink rejection and change detection are ordinary local-workflow
protections, not an adversarial filesystem sandbox or race-free security boundary.
There is no signature, trusted timestamp, full environment capture or proof of freeze.
Retain a trusted manifest and record the relevant source revision separately.

## Provenance

The initial design was informed by recurring issues in the maintainer's private
research workflow: implicit zero-filling, starting-equity drawdown baselines,
observation-time versus availability-time confusion, and input reproducibility.
The public package was implemented separately with synthetic fixtures; it contains
no private strategy implementation or historical performance evidence. Passing tests
establish bounded software behavior, not investment validity.
