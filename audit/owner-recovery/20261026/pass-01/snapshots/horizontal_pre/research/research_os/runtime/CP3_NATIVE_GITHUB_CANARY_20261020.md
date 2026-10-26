# CP3.1–CP3.4 — native Oracle service-user qualification

Live qualification completed 2026-10-19T23:50:07.796958Z (October 20 Paris).
Operational code remains pinned to `f138c980c94eea313fd77532c20857da5c02d3fe`;
GitHub durable state advances independently of that deployment identity.

The Owner successfully ran the hash-verified root preparation. Actual OCI probe
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaanwiy2mgzq62jppbljldvayit74xgz5uifusan4msve3a`
confirmed `quant-local-model.service` enabled/running and loopback health OK,
both fixed no-argument recovery wrappers present, and no research timer installed.
The native private deploy key stays on the VM under the unprivileged service user.

Actual command
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaaq5zg7gpokgsyjtgjyczlufcm25rcotjn4672xyqbdvza`
ran the canonical canary as `quant-research`, exited zero, and published its full
report in GitHub at
`research/research_os/artifacts/AAA-ORACLE-H24-CANARY-f138c980c94eea31/qualification-fa6ecb5ec2109f56.json`.
Publication commit: `8fda1d154458074459f721bbeb6d6f208c97a8be`.
Report Git blob: `c5c86ea780330c6eea8c360dbe15fab816b33b2b`;
19,500 bytes, SHA256 `721f82cad9804fc0b2bbfb5d0b25d93d621b87b3d35423f2dfd6d2474361fd0b`.

Result: **PASS_PRE_ACTIVATION, all 13 gates true**. Exact-release Oracle CI
39338286363 and general CI 39338286411 were independently rechecked SUCCESS.
Live local structured inference took 20.238 seconds; the production critique
took 68.100 seconds. Both used only the loopback GPT-OSS implementation.

The canary deliberately terminated a real child process immediately after its
generation-1 claim had reached GitHub. After the 90-second lease expired, fresh
worker instances completed `recover_or_qualify` and `provenance_check` as generations
2 and 3. The task is COMPLETE with exactly two immutable stage artifacts and
two receipts, three start generations, and no duplicate lineage or freeze.
Fresh dry-run and no-op also passed without writes or model calls.

Scientific preflight loaded the real blob-verified 20-record Legacy ledger and
all 13 normalized frozen hypotheses. The historical Legacy census remains
partial with explicit gaps; no missing records were invented. All four authority
flags are false; hosted model calls are zero. This Legacy-only canary created
no hypothesis, experiment outcome, allocation, sizing or order.

Post-canary actual model probe
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaawbxtxht7izureascdwz5djl4rios5wpw7bn55rz2mavq`
confirmed the same enabled/running model PID and health OK. The cgroup peak was
2,654,416,896 bytes during this bounded service run (different metric from the
earlier qualification process's RSS). No swap was used.

Remaining at this checkpoint: gated timer activation, two automatic scheduled
wakes, actual VM reboot recovery, and the final V1 operational receipt. The
process-crash canary does not substitute for a VM reboot. No H24 RUNNING verdict
is asserted here. Live Lab native ingress/UI integration remains unfinished.
