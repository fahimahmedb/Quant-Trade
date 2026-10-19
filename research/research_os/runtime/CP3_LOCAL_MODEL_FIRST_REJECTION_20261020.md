# Actual local model first rejection and policy-context repair

Tested exact executable release: a4f2a822134370fdae5dc4723620dde32a4a07a5.
Actual OCI qualification command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaa2tppksxhg4ufeaczew7xdmjcmewiuhohnjcseukjdvea`.
Result: BLOCKED, LOCAL_MODEL_SCIENTIFIC_NEGATIVE_CASE_FAILED. Three cases passed
(closed authority, unavailable correlation, independent validation); unresolved
same-payer/mechanism overlap with unknown timing clock failed. This is an actual
model rejection, not a passing canary or a deployment success.

The original report is being retained as `local-backend-first-attempt.json` on
the VM, before any subsequent report may replace the current qualification file.
No competing model is downloaded. No model/worker service or timer is enabled.

The first test requested a Research OS-specific verdict without supplying its
explicit same-payer/mechanism/unknown-clock rule. Production reasoning also lacked
that explicit policy context. The repair supplies the same policy text in every
production critique and qualification prompt. It does not alter deterministic
screening, readiness, authorities, task/lease contracts or expected BLOCK.

Qualification is strengthened: option ordering no longer allows an always-first
answer to pass, and a positive proved-distinct **structural-only** screen must
clear, without granting validation or outcome permission. There are now five
scored cases, plus the actual production structured critique. Each result and
its measured resources are saved before proceeding. The host preparer requires
the exact production-policy hash and all five cases before model-service setup.

This is qualification of bounded unverified commentary with explicit policy,
not evidence that the experimental pruned model is an independent scientist or
reliable without context. If the stronger contextual evaluation still fails,
selection remains rejected. There is no silent hosted fallback or relaxed gate.

Build checks: targeted qualification/host/worker regressions and compilation.
Exact-head CI and actual policy-bound requalification are pending for the
containing commit. Baseline 0dba8d528393b46d28e94a7a3e3fcbb20d6ea087 Oracle CI
39336269429 passed 144 tests; its general CI is tracked separately.
All four authorities remain false and ORACLE_H24_RESEARCH_LAB remains NOT_PROVEN.
