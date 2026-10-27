# Test qualification — non-pass closure

FACT: Local execution available (Python 3.12.14; pytest 9.1.1 installed as test dependency). Per-run command/environment/HEAD/start/end/result/failure/log metadata: evidence/TEST_RUNS.json. All archived original logs retained; top-level log refs resolve durably.

FACT: At freeze SHA: 61 focused integrity tests PASS; 455 Research OS tests PASS; 45 Mega B pytest tests plus 4 subtests PASS; selected Q18 PASS; H/V selected tests byte-identical to executed target tests; 17 historical replay tests PASS only on immutable CP06 code. E2 components25 PASS, E3 fixture8 PASS. Schema check PASS.

FACT: ordinary regression1125 has 4 failures and1 error. All five classified STALE_FIXTURE (published count, trial hash golden, and unattributed inline V2 fixture). Actual run remains FAIL, with no waivers or skips. Generated status check FAIL: STATE inventory1107 vs1125. One prior stale receipt golden was corrected before freeze with controlled same-builder proof; other stale fixtures remain for explicit follow-up.

FACT: current-C0 attack FAIL: structurally independent reconstruction with semantic review explicitly NOT_PROVEN still counts1 confirmation; expected0. This CURRENT_INVARIANT blocks qualification independently of stale tests. No protected economic outcomes consumed; no product repair after freeze.

FACT: L_ATTACK_SCOPE=NOT_USED because no exact immutable L SHA recovered. Selected immutable H/V/Q attack scope and classification: evidence/oneshot_regression_classification.json. Q is not globally claimed green.

FACT: Hosted exact-head execution NOT_AVAILABLE: CLI Actions API forbidden; connector lacks dispatch capability; existing branch-filtered workflows do not select the child branch. evidence/HOSTED_AVAILABILITY.json. No hosted PASS.

FACT: Two-stage finalization will push/fetch exact candidate, run local qualify_local.py with external logs, then create one evidence-only attestation, rerun local qualification on that exact SHA, push/fetch final ref and query external status. No commit follows the final run. Pending exact candidate/final metadata is explicitly not a qualification claim.
