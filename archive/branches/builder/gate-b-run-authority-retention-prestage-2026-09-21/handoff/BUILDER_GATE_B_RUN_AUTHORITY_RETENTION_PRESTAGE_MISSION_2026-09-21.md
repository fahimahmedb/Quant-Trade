# BUILDER — GATE B RUN AUTHORITY / RETENTION PRESTAGE — 2026-09-21

MISSION_TYPE = READ_ONLY_ANALYSIS + HANDOFF_ONLY

Expected starting HEAD:
2ee9e1d2d84b7c0ded400a56f64ad7d9e2a60651

Read first:
1. QUANT_NORTH_STAR.md
2. handoff/BLUE_GATE_B_PARALLEL_PREPARATION_CONVERGENCE_2026-09-21.md
3. governance/BLUE_GATE_B_PARALLEL_PREPARATION_DISPATCH_2026-09-21.md
4. governance/BLUE_GATE_B_ACTIVATION_TEMPLATE_2026-09-21.md
5. governance/TARGET_HOST_GATE_B_ENTRANCE_CONTRACT_2026-09-21.md
6. governance/TARGET_HOST_GATE_B_TO_GATE_C_RUNBOOK_2026-09-21.md
7. governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json
8. Astra preactivation review @ aff6b7a2ca6355f518578c0ddbcac72fb49a356c

SCOPE:
Address ONLY Astra F2, F3, F6 and F7 preparation gaps.

Do NOT work on:
- evidence-schema F1 repair;
- V3->V4 transition mechanics (Lane A owns F4);
- synthetic lifecycle/sanitization mechanism (separate lane owns F5);
- target-host mutation.

OBJECTIVE:
Prepare a concrete fail-closed operational authority design for ONE future Gate-B run.

Must specify:

F2 — run identity / anti-laundering
- globally unique GATE_B_RUN_ID allocation rule;
- attempt-number rule;
- immutable reservation/consumption record;
- terminal-failure state;
- retry/new-run semantics;
- prevention of cross-run artifact relabeling;
- prevention of reuse of FAILED_TERMINAL evidence;
- how Blue checks no concurrent mutating run exists.

F3 — activation sealing completeness
- exact immutable references/digests that MUST be sealed:
  hybrid amendment, contract, runbook, schema, materialization procedure,
  transition-plan digest, evidence-root binding, synthetic-reservoir binding,
  allowed mount source/destination matrix, candidate triple;
- explicit mutation-capability allowlist/default deny;
- activation expiry/invalidation/revocation checks;
- exact first command that may consume activation.

F6 — evidence retention
- restricted evidence-root requirements;
- persistence through reboot;
- journald retention/boot visibility requirements;
- disk/inode headroom review;
- canonical artifact naming/manifest rules;
- retrievability and permissions;
- public-vs-restricted projection;
- preflight snapshot repeatability requirements.

F7 — no-write preflight
- replace any "read-only by label" assumption with commands/options/procedures
  that do not refresh Git index or otherwise mutate metadata;
- prove deployed bytes independently of mutable Git index/cache state.

CLASSIFY each proposed closure as:
REPOSITORY_PRESTAGE / TARGET_HOST_ONLY / BLUE_DECISION_REQUIRED / MISSING_MECHANISM.

Do NOT claim these properties are proven merely because a plan exists.

OUTPUT:
handoff/BUILDER_GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE_2026-09-21.md

Final status:
GATE_B_RUN_AUTHORITY_RETENTION_PRESTAGE = READY_FOR_BLUE_REVIEW
or precise blocker.

Only mission/handoff docs may be committed.
Return control to Blue.