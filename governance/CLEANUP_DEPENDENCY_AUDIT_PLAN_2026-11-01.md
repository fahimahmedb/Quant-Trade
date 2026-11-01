# Quant-Trade — cleanup dependency audit plan

DATE=`2026-11-01`
STATUS=`PLANNED_NOT_AUTHORIZED_FOR_DELETION`
AUTHORITY_PAIR=`project/canonical + code/canonical`

Purpose: prepare the fastest trustworthy path to repository cleanup without deleting useful code, evidence, history, workflows, data references, or currently required dependencies.

Operating law:
- current forensic auditor continues independently; do not restart or duplicate its chronology;
- use its outputs as indexes only, and reconcile fresh Git evidence before acting;
- evaluate cleanup candidates by dependency/value proof, not by branch age/name;
- no destructive deletion until every candidate passes a bounded dependency and unique-value gate;
- unknown or conflicting candidates are PARK/BLOCK, not deleted;
- prefer classify -> retire -> verify -> delete only after proof;
- preserve project/canonical and code/canonical as authority pair;
- cleanup must not displace current runtime critical path `VM_MULTI_WAKE_PROOF_ON_AUTHENTICATED_EXISTING_HOST`.

Required classification per branch/object:
`KEEP_ACTIVE | KEEP_EVIDENCE | SUBSUMED | RETIRE_SAFE | DELETE_CANDIDATE | PARK | BLOCK | UNKNOWN`

Required proof before deletion:
1. exact tip SHA and ancestry known;
2. no unique code semantics not already integrated or intentionally retired;
3. no unique scientific evidence, negative result, protocol, dataset receipt, or qualification artifact needed for reproducibility;
4. no live workflow/config/runtime/docs dependency;
5. no open PR/issue/review/reference requiring the ref;
6. no active agent/auditor working on the ref;
7. canonical replacement identified where applicable;
8. rollback/recovery evidence retained;
9. branch/object classified by fresh Git evidence;
10. independent final challenge finds no material counterexample.

Deletion authority remains separate from analysis. This file records cleanup intent only.