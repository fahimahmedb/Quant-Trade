# CP060 — Bootstrap edge audit and remaining historical capability disposition

CP059 source 650af1c07a7604020e7702b302618558c94e6409: configured root 764,
core V2 273, broader Research OS 268, shared Python 2/JS 57 pass locally.
Exact-source workflow passes every run step; read-only GitHub entrypoint writes
and pushes zero. Hosted qualification is pending and not inferred from local CI.

## Highest-value executable depth finding

CP057 lets prepare() verify a literal qualified Builder source while preserving
Oracle as the sole scientific state branch. But standalone oracle_v2_host_prepare
still hardcodes Oracle for CI and invokes prepare without the source parameter.
The available entrypoint cannot express the newly qualified provenance.

Additionally, host_prepare verifies CI, calls the pinned V1 bootstrap function
(which installs/publishes the release archive), and only then invokes prepare(),
whose late active-V2 guard refuses re-preparation. Archive publication can thus
precede this refusal. This is not evidence of a V1 timer restart or current-release
switch: bootstrap() here calls install_release(), not the V1 prepare() routine.

History search found the original bootstrap plus staging-import repair 65847ab;
no existing early active-V2 admission or explicit source forwarding exists.
Integrate the CP057 source selection through the standalone CLI and fresh isolated
interpreter. Preserve legacy three-argument helper behavior. Reject unknown source
choices before requests. Check root and actual systemd load/active state before
bootstrap publication; unknown observations fail closed, and running/transitioning
V2 requires explicit repair. Keep the late native guard, all exact CI checks,
pinned V1 bootstrap digest, isolated imports and closed authorities.
This remains initial preparation, not an active V2 upgrade. No deployment authorized
by tests and no removal of the native observer's a67ffec core pin.

## Historical no-build decisions under current premises

Factory ca8ffe439953b063fb9d049773ce0b6245958c7d preserves unique experiments,
OutcomeFirewall, geometry and power. V2 sealed export guards are NOT proof of
supersession of the dataset-column/hash/lineage firewall. The old BlueTeamGate
cannot become V2 Owner permission. A connected import needs a governed dataset
loader/isolated Evaluation capability and explicit V2 authority mapping, currently
absent. Keep SOURCE_IMPORT_REQUIRED, no automatic activation or second registry.
Geometry/power needs event cohort, calendar/horizon and declared effect/ICC/power
premises. Current documentary snippets are not independent events or an admissible
sample size. Do not invent inputs or import disconnected classes for file count.

SEC census 08dcfc39b4b22e0b25e54edde7b6accbb2bc4502 preserves unique official-table
census, primary-key collision handling, acceptance identity and XNYS calendar.
The 1000-line sec_form4 module also contains network acquisition and Yahoo price
availability probing. Current src/quant/dataplane/sec is a pre-t0 raw-capture lane
with executable content/count visibility restrictions, not a replacement census.
No supersession claim: preserve SOURCE_IMPORT_REQUIRED. No blanket import into
that blinded lane, no Form-4 content exposure, no Yahoo probe. A later connected
import needs explicit source/data policy and visibility boundaries; economic
execution and prospective observation remain unauthorized.

Evidence Store was connected in CP055 with exact historical blob provenance.
P0-E1 source recovery was connected in CP059 with scoped review, not universal KILL.
None of these bounded integrations means the Edge 170-commit scientific-memory
corpus, owner/governance history or all source capabilities are reconciled.
No branch retirement or destructive cleanup. All four authority flags FALSE.
