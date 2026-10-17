# Contributing

Start with a GitHub issue describing the expected behavior, actual behavior, Python
version, command and a minimal **synthetic** example. Do not upload account statements,
credentials, proprietary trading logic or market data you cannot redistribute.

Run `python3 -m unittest discover -s tests -v` before proposing a change. Keep fixes
small and add a regression test for the observed bug. Accounting changes should
include a hand-calculated example and a methodology update. CI runs the tests and
positive examples on Python 3.10, 3.12 and 3.13.

Preserve explicit missingness and units. Do not silently sort, fill gaps, reinterpret
timestamps, or replace undefined ratios with zero. Changes to the JSON schema or
exit-code semantics must be documented. Do not add a runtime dependency merely for
convenience. External contributions are welcome; no response-time guarantee is made.

Contributions are submitted under the project's MIT license.
