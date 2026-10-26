# CP054 — recover a useful CP12 capability and connect raw evidence preservation

STATUS=AUDIT_BEFORE_IMPORT_AND_ADAPTATION
BASE=3f8555c
SOURCE=b8f7dffbe040753cb1e47b7f38f3ab4485e1e7ba
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

CP053 qualification: 734 configured / 243 core V2 / 268 broader Research OS PASS;
composed metadata/57 JS tests, policy/claim ceiling, exact-head qualification and
real read-only GitHub entrypoint PASS. Valid clean-epoch receipt hash unchanged.

CONCRETE GAP: existing offline capture_apple_dividend_announcements verifies the
provided local bytes/digests/excerpts and produces a documentary packet, but does
not itself preserve those verified bytes. If the caller discards/changes the
input file, a capture.raw_sha256 reference is not a recoverable raw object here.
Git source packets and scientific-store hashes do not manufacture original HTML.
This does not assert that all historical raw captures were lost.

HISTORY / REUSE: CP12 identified Evidence Store/Identity as SOURCE_IMPORT_REQUIRED.
Its evidence.py already implements content-addressed immutable objects, retrieval
receipts, replay-checked validation/derivation, torn-manifest recovery and restart
durability. It has no vendor/network dependency. identity.py and corporate_actions
provide evidence-bound PIT identities and ambiguity/knowledge-vs-effective clocks.
Sixteen existing adversarial tests cover these capabilities. They are absent from
current Data Plane, while its basic registry/SEC/price adapters already exist.

DISPOSITION=IMPORT_AND_CONNECT, not a new evidence-store design. Preserve three
exact historical implementation blobs plus their original tests. Adapt the
existing native offline two-document capture with an optional caller-owned raw
EvidenceStore: archive only after all digests/excerpts pass, use the exact bytes
already checked, preserve source URI/capture clock and the original output/hash.
No automatic raw archive root, new network acquisition, inferred identity mapping,
new experiment registry or second authoritative task/scientific backend.

CLAIM CEILING: content-addressed raw bytes are Data Plane evidence, not canonical
scientific conclusions. Imported PIT/corporate-action APIs require explicit
evidence assertions; the native AAPL label is not retroactively resolved to a
stable issuer/security identity. Historical raw bytes are not reconstructed from
excerpts. Tests use explicitly synthetic local capture fixtures, not new primary
market evidence or production source qualifications.

NEXT: prove native packet/hash equality with and without archival, idempotent
retrieval, reject-all-before-store on invalid input, corruption failure, and
resistance to caller file changes between validation and archive. Run original
crash/replay/identity tests and composed regressions; keep acquisition gates shut.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
NETWORK_CAPTURE_PERFORMED=FALSE
