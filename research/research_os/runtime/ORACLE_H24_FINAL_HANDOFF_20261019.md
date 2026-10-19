# Oracle H24 recovery — exact handoff

Verdict: **BLOCKED_BY_SPECIFIC_EXTERNAL_DEPENDENCY**.
`ORACLE_H24_RESEARCH_LAB = NOT_PROVEN`.

Do not restart the architecture. Continue on
`builder/oracle-economic-loop-recovery-20261019` from its fresh remote HEAD.
The Owner authorization remains valid; no renewed approval is required.

Verified production implementation:
`5e6c740329939b24ac2b20cfc830bcde5dcc5719`.
Oracle Recovery CI `39272109295`: **135 tests PASS** (16 Oracle, 28
worker/backend/scheduler, 91 scientific pre-outcome). Global SEC P0 CI
`39270935429` on predecessor `04a14e47dbdcb74fd7e24bbb82c210da3a12b6b1`
also passed: 555 unit tests, 267 SEC-lane tests and 35 end-to-end checks.
The CI artifact `oracle-h24-ci-receipt-<SHA>` binds the containing final commit
to its own executed test counts and explicitly records **CI-only** evidence.

Actual GitHub dry-run and read-only wake on the verified implementation both
returned zero writes and zero hosted model calls. They verified the exact real
Legacy blob, loaded 20 records (the manifest census is 33), normalized all 13
current hypotheses and retained the ASML overlap blocker. They ran in the
**build environment**, not on Oracle.

The implementation now includes the local pluggable backend, canonical lane
adapters, fresh-state Git transport, fenced claims, atomic persistence,
crash/restart regressions, deterministic queue refill, systemd units, read-only
OCI inventory operation, live pre-activation canaries and a gated installer.
Normal runtime data commits skip hosted CI; code releases still require CI.
Frozen generation/content, independent challenge and Red Team restrictions
remain fail-closed. No economic/live authority was opened.

The remaining dependency is **authenticated access to the actual Oracle VM**.
The execution environment declares no OCI identity, OCI configuration, SSH
directory/key/agent or TCP destination grant. OCI CLI is absent. GitHub Actions
secret metadata returns HTTP 403, so its unobservable contents are not assumed.
No Browser control tool is exposed. These observations were rechecked before
the final receipt. Installing a CLI alone would not supply the missing identity.

No claim is made about the VM's pre-existing GPT-OSS variant, quantization,
weights path, service, port, RAM/CPU use or timer state. Nothing was installed
or replaced on that VM by this mission.

Next: use authenticated OCI Run Command or SSH to run the versioned inventory
first, then follow [`deploy/ORACLE_H24_RUNBOOK.md`](../../../deploy/ORACLE_H24_RUNBOOK.md).
Reuse the existing model when healthy. Deploy the exact final CI-qualified SHA,
run the live canaries as the intended service user, activate the timer only on
matching live evidence, observe automatic wakes and persist the final live
RUNNING receipt. The script proves real **process** death only when actually
run; VM reboot evidence must be separately executed and labeled.

Machine-readable evidence and the complete checkpoint SHA map:
[`ORACLE_H24_FINAL_RECEIPT_20261019.json`](ORACLE_H24_FINAL_RECEIPT_20261019.json).
