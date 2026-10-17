# Maintainer plan

Maintainer: Sam Chen ([@FanatiSam](https://github.com/FanatiSam)).

## Current state

Version 0.1.0 is a new public extraction of research-workflow lessons, implemented
as an independent standard-library package. There are no claimed external users,
downloads, commercial adopters, or independent audits. The first release focuses
on five bounded checks and synthetic examples rather than exposing a private system.

## How Codex supports maintenance

Codex assisted the initial implementation, documentation and regression tests, with
the maintainer directing the scope. Planned uses include reproducing issues using
synthetic fixtures, proposing small fixes, reviewing accounting edge cases, improving
documentation, and adding regression tests. Changes require review and passing tests.
No automated external AI API integration or paid PR bot is currently installed.

## Near-term priorities

1. Gather reproducible issues and feedback from independent users.
2. Add adapters for additional daily PnL schemas only when backed by concrete examples.
3. Improve precision and property-based accounting tests as counterexamples arise.
4. Consider matched-reference comparisons with explicit shared seed, dates and
   missing-data semantics after the core interface stabilizes.

The priority is useful, maintainable evidence checks. New broker connections,
strategy optimization, production orchestration and live execution are outside scope.

## Support use

Maintainer coding access would support issue triage, tests, code review and docs.
API credits would be useful only for a separately designed and budgeted maintainer
workflow. No fixed API budget or existing community scale is claimed.
