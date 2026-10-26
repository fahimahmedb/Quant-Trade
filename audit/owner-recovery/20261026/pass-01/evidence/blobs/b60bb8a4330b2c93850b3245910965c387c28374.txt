# Research Factory V2 experiment API

This API is outcome-blind infrastructure. It does not fetch prices, compute realized returns, or make capital decisions.

## Stable injection boundary

A future certified lane injects only `EventRecord(event_id, issuer_id, event_time, formation_date, provenance, status)` plus a trading-session ordinal map. `GeometryEngine` uses those inputs to compute sample geometry without price data. The event contract is lane-neutral and therefore can serve Form 4, crypto, futures, and future lanes without changing scientific logic.

## Preregistration and freeze

1. Construct `PreregistrationContract`. `NEXT_SESSION_OPEN`, a session horizon (including 20), and a primary benchmark such as `SPY` are representable strings/integers only; nothing is fetched.
2. `ExperimentRegistry.propose()` creates a deterministic experiment identity and monotonic version.
3. Advance `PROPOSED -> PREREGISTERED`, attach formation `DatasetRef`s, then advance to `DATA_READY`.
4. `blue_freeze()` freezes the exact protocol/dataset set and emits `BlueTeamGate` bound to the protocol hash.
5. Only then may the state advance to `TESTING` and outcome access be requested.

Scientific edits never mutate a preregistered version: call `propose()` again with the same experiment key to create the next version.

## Outcome firewall

`OutcomeFirewall.authorize()` fails closed. Before an exact Blue Team gate it rejects direct outcome columns, suspicious outcome names, aliases, derived lineage, known outcome content hashes, and requests without a manifest. The content-hash rule is path-independent, so copying an outcome file to another path does not bypass the gate.

## Geometry and synthetic power

`GeometryEngine` reports N, annual counts, events/issuer, HHI, effective issuers, overlapping 20-session windows, and issuer cluster geometry. `PowerSimulationEngine` accepts only a `GeometryReport` and synthetic standardized-effect assumptions; it has no API for observed prices or realized outcomes.