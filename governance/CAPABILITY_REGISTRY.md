# Canonical capability registry

This is the live routing registry. Detailed history remains in `governance/forensic-20261031/` and Git history.

| Capability | Owner | Status | Current proof / limit |
|---|---|---|---|
| Wave2 integrated research/evidence/factory/economic backbone | `code/canonical` | REUSE | base `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` |
| CP099 V2 pre-outcome hardening | `code/canonical` | CONNECTED_SELECTIVELY | carried forward; current run `41265514716`: `22/22 PASS` |
| Post-Wave2 GIGA-Q hardening | `code/canonical` | CONNECTED_SELECTIVELY_AND_QUALIFIED | source `4efadddf694eff0c0df00925b5b4b89194f32f8e`; current run: `110/110 PASS + 44 subtests` |
| PR46 bounded GPT-OSS/Codex orchestration | `code/canonical` | CONNECTED_AND_QUALIFIED | source `afedfd57986aa042e9e97aa53b9db53b4619764f`; current PR46+host tests `21/21 PASS`; launcher isolation PASS |
| Existing V1 timer → GPT-OSS/Codex host wake seam | `code/canonical` | CONNECTED_AND_ENGINEERING_QUALIFIED | `host_wake.py` + existing systemd timer; exact head `13c9ff03f0898e9af28abaa3dab78a520c70c887`; run `41265514716` SUCCESS |
| Canonical combined-code qualification | `code/canonical` | ENGINEERING_QUALIFIED | head `13c9ff03f0898e9af28abaa3dab78a520c70c887`; Wave2 sample `48/48 PASS`; authority closed; clean checkout |
| Scientific / negative memory | project + immutable code ledgers | REUSE | rejected/superseded knowledge preserved; no scientific semantics changed by host-wake seam |
| Authority state | `project/canonical` | ACTIVE_CLOSED | real capital/live trading/unblinding/production/cleanup remain false |
| Forensic reconstruction | `project/canonical` | HISTORICAL_REFERENCE | complete for convergence; no restart |
| Actual VM deployment of `13c9ff03…` | external runtime | NOT_PROVEN / BLOCK_EXTERNAL_HOST_ACCESS | current host state unknown; no authenticated OCI/SSH/host-command channel demonstrated |
| Real VM multi-wake GPT-OSS → Codex → GPT-OSS | external runtime + `code/canonical` | NOT_PROVEN / BLOCK_EXTERNAL_HOST_ACCESS | needs ≥2 automatic wakes and causal Codex result consumed by following GPT-OSS decision |
| Global post-terminal project mission selection | future control layer | PARK | current launcher is task-bounded; do not build before real VM bridge proof |
| Real-capital/live-trading | none | CLOSED | authority false |
| Legacy branches / restaurant-stock / review surfaces | none | PARK / RETIRE_FROM_ACTIVE_SCOPE | retain evidence; destructive deletion not authorized |

## Current exact-head proof

`code/canonical=13c9ff03f0898e9af28abaa3dab78a520c70c887`

Run `41265514716`:
- exact-head identity PASS;
- compile PASS;
- CP099 `22/22 PASS`;
- PR46 + host-wake `21/21 PASS`;
- `GPT_OSS_LAUNCHER_ISOLATION=PASS`;
- Wave2 sample `48/48 PASS`;
- GIGA-Q `110/110 PASS + 44 subtests PASS`;
- `CANONICAL_AUTHORITY_CLOSED=PASS`;
- clean checkout PASS.

Preceding challenge is retained:
- `a0115d8a0b3f83e32d321d73d2dfb560f221a406`, run `41265426984` FAILURE;
- failure isolated to two tests where mocked `os.execve` returned into an unreachable-production exception;
- one-file correction produced `13c9ff03…`; full qualification then passed.

## Routing law

`REUSE > CONNECT > REPAIR > BUILD`.

Current critical path: `VM_MULTI_WAKE_PROOF` only.
If authenticated host access is absent: `BLOCK_EXTERNAL_HOST_ACCESS`.
Do not reopen global audit, build another scheduler, manually simulate autonomous routing, or start global mission-selection work before the bridge is runtime-proven.
