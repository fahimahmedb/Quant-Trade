# Quant-Trade — forensic history closure

Date: 2026-11-01

Status: `HISTORY_RECONSTRUCTION_COMPLETE_FOR_DECISION_RELEVANT_SCOPE`

This is the live-project pointer to the completed forensic reconstruction on `audit/forensic-checkpoint-20261019`.

Authoritative deep closure:
`governance/forensic-20261031/deep/CHECKPOINT_DECISION_HISTORY_FINAL_20261101.md`

Forensic resume commit after closure:
`73878dda9f1452e1dbb89e832c792510d0185807`.

## What is complete

- initial surface: `6393 / 6393` commit traces;
- `71` active days through 2026-10-31;
- CP055→CP099 deep supplement;
- decision-changing PR/issue/review history through the end of October;
- Owner authority changes, scientific freezes/results, independent challenges, repair/supersession chains and terminal unknowns.

`969` occurrences remain intentionally `UNKNOWN_BY_DATE`; this does not reopen the audit unless a specific SHA/date contradiction can change a current decision.

## Material historical correction

The older surface capability map simplified WP2 synthetic single-lineage causality as a bounded engineering proof. Deep history requires a stricter classification:

`WP2_SYNTHETIC_SINGLE_LINEAGE=CONTESTED_ENGINEERING_EVIDENCE`

Facts that coexist and must not be collapsed:

- PR39 contains an earlier independent bounded PASS on implementation `d40053bd112164826273a866199e2941259919b0` after a real receipt-alias defect was repaired;
- hosted run `41069767444` on later head `8f8df47d184f0f1594280bec7e9e7941962cf1c5` succeeded;
- later PR41 independently reviewed the same implementation lineage and left two unresolved findings: the synthetic adapter did not demonstrate the actual execute/result/evaluator arrow, and fixture identity was not durably pinned/recomputed across claim/recovery;
- Issue42 later verified hosted run identity but its fresh-context semantic verdict remained `UNKNOWN` for the relevant WP2 semantics.

Therefore WP2 remains useful synthetic historical evidence, but it is **not** a clean independent closure proof and it is not a global autonomy proof.

This correction does not invalidate PR46 or current `code/canonical` qualification, which use their own code/test/review lineage.

## Other final historical claim ceilings

- WP1: `BLOCK_EVIDENCE_ABSENT_OR_UNRECOVERED`; no historical outcome inference.
- F1 Crypto Carry Stage B: `REJECT`; no retune/rerun.
- Weather A2: frozen/deferred safety rail, not economic validation.
- Issue45 Astra gate: request existed; issue closed `not_planned` with no review result.
- PR46 source `afedfd57986aa042e9e97aa53b9db53b4619764f`: built + hosted-qualified; historical source itself did not prove VM deployment or real multi-wake autonomy.
- PR47: convergence diagnostic only; direct CP099→Wave2 merge rejected, selective port strategy retained.

## Routing rule after closure

Do not restart global archaeology.

Use `project/canonical` for current state and `code/canonical` for current engineering authority. Reopen historical evidence only for one concrete, falsifiable contradiction whose answer can change a current decision.

`GLOBAL_FORENSIC_RESTART_AUTHORIZED=FALSE`
`DESTRUCTIVE_CLEANUP_AUTHORIZED=FALSE`

The active project critical path remains whatever `governance/CURRENT_PROJECT_STATE.md` records; history completion does not override newer runtime/engineering evidence.
