# V1 deployment continuation — evidence, not activation

Owner fixed the current Oracle H24 delivery as V1 on October 20 Europe/Paris.
Scope: ORACLE_LAB_V1_SCOPE_20261020.md. Exact implementation checkpoint:
`a4f2a822134370fdae5dc4723620dde32a4a07a5`.

## Build / CI

- Local backend/worker/scheduler/qualification/host-preparation suite: 37 PASS.
- Oracle Recovery CI 39335658300: completed SUCCESS on that exact SHA.
- General SEC P0 CI 39335116970 (preceding a5e8adf) and 39335658198 failed
  status-artifact freshness after new tests increased discovery. No scientific
  result was changed to repair this. `scripts/status_artifacts.py --write`
  regenerated the canonical checkpoint: 559 tests, versus 555 previously.
- The host-preparation `/meta` read bound was increased from 128 KiB to 2 MiB
  after a real GitHub metadata response was truncated. Oversized responses still
  fail closed; official SSH host keys are never replaced by an unverified scan.
- CI on the containing repair commit remains pending; none of this is H24 proof.

## Actual Oracle

Pinned ARM64 runtime now executes successfully after Owner's dependency repair:
`llama.cpp` build 11742, commit `4c3c5810f`, GNU 14.2.0, aarch64.
Actual command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaadvuuzw2motz3keo6ct7t2ywhdhol3qyktkf6sgoosmeq`.
Required context/thread/reasoning-budget flags are present; no service changed.

Actual isolated release qualification for a4f2a822 passed 98 tests, loaded the
20-record real Legacy ledger and confirmed every authority false:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaakudg2iddatp5yxochvgpz2p53sbhnzwehne2ci5bh4oa`.
Its scheduler_started value is false. Prior installation pointers were preserved.

The single chosen model download command finished with Oracle exit 0, but its
TEXT output was empty. This is not substituted for an asset hash/inference proof.
Actual qualification is queued/running separately; it re-verifies all asset bytes,
starts only a temporary loopback server, measures four scientific negative cases
and a representative worker critique, checks memory and always stops the server.

A repository-scoped SSH deploy identity was generated on the VM. Owner reports
adding its public half with write permission. The private key has not been
exported. Authenticated GitHub access and actual canonical writes still require
live verification. Root service preparation and timer activation are pending.

## Live Lab follow-up requested during V1 work

Read-only Sites access confirms the existing project
`appgprj_6aca43cb86bc81918e067097356a37de` is active, version 22, caller owner,
at https://quant-trade-lab.sassylime.chatgpt.site. No Site was edited/published.
An unauthenticated direct SSE probe returned HTTP 403 from this executor; it
does not establish that the authenticated Site stream is unhealthy.

The Oracle worker currently publishes canonical events to GitHub, without a
native Site-ingress transport. The native UI mapper accepts those event identity
fields but requires explicit activity for animation. GitHub persistence alone is
not native-ingress/SSE/render/verified-ACK integration. Preserve the existing
ingress protocol; do not revive GitHub polling as the primary live protocol or
invent activity. Future delivery must bind actual stage/lane activity, lifecycle,
lease expiry and idempotent acknowledgments; display remains observational and
must never become a second task/authority source. A temporarily unavailable UI
must not break Oracle's durable scientific control loop.

Economic Look native semantics remain separate from the four basic worker event
types. A true iPhone/Safari check remains required before claiming that physical
device validation. Neither item opens economic/prospective/capital/live authority.
