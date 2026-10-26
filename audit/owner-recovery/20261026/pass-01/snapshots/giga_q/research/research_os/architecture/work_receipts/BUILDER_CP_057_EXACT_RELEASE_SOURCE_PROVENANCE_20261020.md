# CP057 — exact release-source provenance, canonical state stays separate

STATUS=IMPLEMENTED_FOCUSED_AND_BROADER_PASS_FULL_QUALIFICATION_PENDING
BASE=4cffea5
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

DONE: V2 CI verification optionally accepts qualification_source_branch from
exactly the Owner-authorized Oracle/Builder rails, defaulting to the historical
Oracle branch when absent. Both named successful runs must match that same
source and exact release SHA. Evidence records server-observed head_branch.
Unknown/null/ambiguous/lookalike sources fail before network access. Canonical
scientific repository, state branch, cache and lane validation remain unchanged.

PREPARATION: optional keyword-only source selection in the existing Python
prepare API is explicit and enters the config hash/qualification chain. Legacy
three-argument callers and fixed no-argument root controls retain their defaults.
Active V2 still raises V2_RUNNING_RELEASE_REQUIRES_EXPLICIT_REPAIR_HANDOFF before
config/unit writes; root, VM, model, exact receipt, canary and four authority gates
remain in force. No hot-upgrade path, observer core-pin bypass or deployment added.

EVIDENCE: five new adversarial tests plus existing deployment/host tests PASS
(12 focused). Cover both authorized/default sources, rejection before requests,
wrong/mixed SHA/branch/workflow/status/conclusion, inability to redirect scientific
state, and active-runtime preparation refusal with all authority flags False and
zero configuration writes. HTTP/host facts here are explicit unit fixtures.
Broader Research OS 268/268 PASS; pyflakes/whitespace PASS. Official configured
inventory targets 759; core V2 tests 268 plus shared metadata/57 JS checks.

ACTUAL ACCESS PROBE: benign root-page GET to the existing Site, without reading
its body or scientific data, fails at the proxy tunnel with 403 Forbidden.
No Site admin tool, VM remote-execution capability or TCP/VPN grant is exposed.
This is an observed environment boundary, not a request to weaken authentication.
Production Site/D1/SSE/Oracle/reboot proof is therefore not inferred from local CI.

NEXT: exact composed qualification and scoped CP12 historical provenance gaps.
Retain a concrete upgrade handoff for the current candidate; actual repair requires
fresh host release/config/lease/observer/root facts. Do not reinterpret source-CI
acceptance as operational qualification or authority to open economic membranes.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
DEPLOYMENT_PERFORMED=FALSE
