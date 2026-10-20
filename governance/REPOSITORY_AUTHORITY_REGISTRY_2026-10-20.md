# REPOSITORY AUTHORITY REGISTRY — 2026-10-20

Authority: CP12 deep organizational audit.

This registry supersedes the 2026-09 branch authority registry for CURRENT navigation/classification only. Historical registries remain evidence of the state and decisions that existed at their dates.

Current observed branch count: `229`.

This registry does NOT authorize physical branch deletion. Current V2 policy keeps `destructive_git_operations_authorized = false`.

## Classification vocabulary

- `LIVE_RUNTIME_V1`
- `LIVE_V2_BUILD`
- `LIVE_PARALLEL_PRODUCT`
- `SOURCE_IMPORT_REQUIRED`
- `SCIENTIFIC_MEMORY_REQUIRED`
- `OWNER_GOVERNANCE_REQUIRED`
- `HISTORICAL_GOVERNANCE_EVIDENCE`
- `HISTORICAL_IMPLEMENTATION_EVIDENCE`
- `ABSORBED_REF_DELETE_READY` — informational; Owner deletion still required
- `ARCHIVE_AFTER_IMPORT`
- `SUPERSEDED_ROUTING`
- `OWNER_RETENTION_OVERRIDE`
- `UNKNOWN_REVIEW_REQUIRED`

---

# 1. Live/current refs

| Ref | Classification | Current role |
|---|---|---|
| `builder/oracle-economic-loop-recovery-20261019` | `LIVE_RUNTIME_V1` | qualified autonomous Oracle H24 V1 |
| `builder/oracle-v2-core-20261020` | `LIVE_V2_BUILD` | current V2 scientific architecture/build rail |
| `builder/live-lab-oracle-canonical-20261020` | `LIVE_PARALLEL_PRODUCT` | current Live Lab canonical candidate rail |
| `builder/live-lab-oracle-integration-20261020` | `LIVE_PARALLEL_PRODUCT` | current Oracle/Live Lab integration rail; diverged from canonical |
| `audit/forensic-checkpoint-20261019` | `HISTORICAL_GOVERNANCE_EVIDENCE` + current audit | CP10–CP12 forensic/organizational baseline |
| `blue/master-v2-2026-09-20` | `SUPERSEDED_ROUTING` / temporary default portal | repository default; not V1/V2 implementation authority |

No other branch should be treated as current project authority merely because it is newer-looking.

---

# 2. V2 capability sources — mandatory review/import before retirement

| Ref | Class | Why it survives |
|---|---|---|
| `builder/research-factory-core-v2` | `SOURCE_IMPORT_REQUIRED` | experiment registry, Outcome Firewall, power/geometry; 15 unique commits observed |
| `builder/evidence-store-identity-v2` | `SOURCE_IMPORT_REQUIRED` | Evidence/PIT/source/corporate-action identity; 22 unique commits observed |
| `builder/sec-form4-census-v2a` | `SOURCE_IMPORT_REQUIRED` | SEC/Form-4 census/schema/calendar/tests; 67 unique commits observed |
| `builder/research-os-aggressive-architecture-20261015` | `SOURCE_IMPORT_REQUIRED` | architectural depth; 84 unique commits observed |
| `research/design-v1` | `SOURCE_IMPORT_REQUIRED` | Alpha Factory / market-selection / abstention / launch doctrine; 20 unique commits observed |
| `research/edge-lab-continuous` | `SOURCE_IMPORT_REQUIRED` + `SCIENTIFIC_MEMORY_REQUIRED` | 170 unique commits; discovery/experiments/probes/memory |
| `research/legacy-economic-reconciliation-20261015` | `SOURCE_IMPORT_REQUIRED` + `SCIENTIFIC_MEMORY_REQUIRED` | 102 unique commits; Legacy reconciliation still partial |

These refs are NOT `archive-and-delete` merely because V2 Core exists.

---

# 3. Scientific-memory refs

| Ref | Class | Durable state |
|---|---|---|
| `codex/test` | `SCIENTIFIC_MEMORY_REQUIRED` | historical KILL/REJECT experiment; one unique commit remains material |
| `builder/f1-persistent-stage-a-2026-10-08` | `SCIENTIFIC_MEMORY_REQUIRED` | F1 acquisition line / PR #24 |
| `builder/f1-stage-a-execution-2026-10-09` | `SCIENTIFIC_MEMORY_REQUIRED` | F1 discovery A / PR #25 |
| `builder/f1-sealed-stage-b-capture-2026-10-09` | `SCIENTIFIC_MEMORY_REQUIRED` | F1 final B `REJECT` / PR #26 |
| `research/f2-primary-terms-decision-2026-10-09` | `SCIENTIFIC_MEMORY_REQUIRED` | F2 permission block / PR #27 |
| `research/technical-signals-literature-2026-10-10` | `SCIENTIFIC_MEMORY_REQUIRED` | EURUSD frozen/unexecuted research / PR #28 |

Intermediate branches in the same research chains may later become absorbed/delete-ready only after the scientific memory index binds their unique result/exposure state.

---

# 4. Live Lab family

## Preserve pending reconciliation

- `builder/live-lab-oracle-canonical-20261020`
- `builder/live-lab-oracle-integration-20261020`
- `builder/live-lab-3d-full-build-20261015`

Class:

`LIVE_PARALLEL_PRODUCT / PRODUCT_CAPABILITY_RECONCILIATION_REQUIRED`

The first two diverge; the old 3D branch has four unique commits and dedicated passing CI. Do not choose a survivor by branch name/date alone.

## Other Live Lab refs

Examples include owner UX rebuild checkpoints, platform probes, UX vision, full autonomy, publication, site-E2E and intake refs.

Default class:

`ARCHIVE_AFTER_IMPORT` or `ABSORBED_REF_DELETE_READY` only after exact ancestry/capability mapping to the reconciled Live Lab rail.

Exact duplicate checkpoint refs pointing to the same SHA are strong redundancy candidates but still await the final product reconciliation receipt.

---

# 5. Weather V4 family

Compact evidence corpus:

`builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08`

Class:

`OWNER_GOVERNANCE_REQUIRED + SCIENTIFIC_MEMORY_REQUIRED`

Important: this branch tip is candidate-only and explicitly not loaded/verified/reviewed/activated.

The wider Weather family spans:

- `owner/weather-v4-*`
- `blue/weather-v4-*`
- `builder/weather-v4-*`
- `astra/weather-v4-*`
- `team/weather-v4-*`

Family classification:

`CONSOLIDATION_REQUIRED`

Required semantic mapping:

- Owner branches → ratified/partial/conditional/draft decision registry;
- Blue branches → decision support/integration/governance evidence;
- Builder branches → implementation/test artifacts;
- Astra branches → independent audit/recheck evidence;
- Team coordination → historical coordination only.

After this mapping and import into canonical Weather memory, most Weather branch refs should be eligible for retirement even though the underlying commits remain evidence.

---

# 6. September Gate A / Gate B / P0 families

Families include numerous:

- `blue/gate-b-*`
- `astra/gate-b-*`
- `builder/gate-b-*`
- `blue/p0-*`
- `astra/p0-*`
- `builder/p0-*`
- related `parallel/*` branches.

Current class:

`HISTORICAL_GOVERNANCE_EVIDENCE`

They are not current V2 routing authority. However, old cleanup rules already distinguished canonical evidence from divergent falsifier/recovery branches. Do not bulk-delete these families until the 2026-09 evidence index plus any later unique work is bound to a compact historical authority record.

Goal:

retain a small number of canonical/final evidence refs or tags, then retire the intermediate branch namespace.

---

# 7. Historical OCI / VM rails

| Ref | Class |
|---|---|
| `ops/oci-one-shot-install-20261019` | `HISTORICAL_IMPLEMENTATION_EVIDENCE` |
| `builder/research-os-vm-autonomy-20261019` | `HISTORICAL_IMPLEMENTATION_EVIDENCE` |

Useful primitives/concepts were substantially ported into V1, but each small divergent tip must be checked/indexed before ref retirement.

---

# 8. Verified absorbed modern Research OS refs

These refs were previously verified as strict ancestors of the retained modern Oracle lineage:

- `builder/research-os-autonomous-loop-20261015`
- `builder/research-os-autonomous-econ-readiness-port-20261016`
- `builder/research-os-econ-readiness-activation-20261017`
- `builder/econ-test-flow-ust-auction-20261019`

Class:

`ABSORBED_REF_DELETE_READY`

This is an informational classification, NOT permission for an autonomous agent to delete them.

---

# 9. Historical special-preservation refs from prior audit

Until explicitly imported/rejected, preserve prior unique-evidence exceptions including:

- `blue/long-horizon-research-2026-09-20`
- `recovery/claude-sec-local-20260914`
- `parallel/codex-wave1-economic-system-2026-09-19`
- `blue/forward-finalization-2026-09-20`
- `builder/forward-market-recorder-v2`

Their old classification was based on unique proposal/recovery/implementation value. CP12 has not yet proven them semantically superseded.

---

# 10. Owner retention override

`claude/restaurant-stock-management-mvp-6oq43e`

Class:

`OWNER_RETENTION_OVERRIDE`

It is unrelated to current Quant architecture but was explicitly retained by Owner in the prior cleanup. Do not remove absent a later explicit Owner reversal.

---

# 11. Generic Claude / Sol / temporary research branches

The repository contains numerous opaque or agent-session-named refs such as `claude/*`, `sol/scout-*` and short-lived Builder/Research experiment branches.

Default class:

`UNKNOWN_REVIEW_REQUIRED`

They may become:

- `ABSORBED_REF_DELETE_READY` if strict ancestry/redundancy is proven;
- `SCIENTIFIC_MEMORY_REQUIRED` if they contain a result/exposure/source decision;
- `SOURCE_IMPORT_REQUIRED` if they contain unique reusable capability;
- `ARCHIVE_AFTER_IMPORT` after semantic import/rejection.

Opaque names are NOT evidence of disposability.

---

# 12. New branch lifecycle governance recommended for V2

Every active temporary branch should carry or eventually receive a disposition record containing:

- workstream ID;
- owner/role;
- base SHA;
- final tip SHA;
- unique capability/result/decision identity;
- current descendant/canonical replacement if any;
- disposition;
- deletion eligibility state.

Allowed terminal dispositions:

- `ACTIVE_CURRENT`
- `MERGED_OR_ABSORBED`
- `CAPABILITY_IMPORTED`
- `SCIENTIFIC_MEMORY_INDEXED`
- `OWNER_DECISION_INDEXED`
- `EXPLICITLY_REJECTED`

A completed workstream must not leave indefinite intermediate refs with no disposition.

---

# 13. Current deletion authority

`AUTONOMOUS_DESTRUCTIVE_GIT_AUTHORITY = FALSE`

Physical cleanup may be prepared and eventually executed by Owner, but the next deletion list must be generated from this semantic registry and CP12—not from CP11's preliminary keep-set.

Any branch not covered here remains `UNKNOWN_REVIEW_REQUIRED` rather than implicitly deletable.