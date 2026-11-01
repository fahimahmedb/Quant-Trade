# Canonical capability registry

This is the live routing registry. Detailed historical proof remains in `governance/forensic-20261031/CAPABILITY_MAP.md`.

| Capability | Canonical owner | Status | Evidence / limit |
|---|---|---|---|
| Wave2 integrated research/evidence/factory/economic backbone | `code/canonical` | REUSE | base `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` |
| CP099 V2 pre-outcome hardening spine | `code/canonical` | CONNECTED_SELECTIVELY | source `ded4228de74ce3b6926d9ea3e3c2114ff1be8208`; conflicting source-line files were not wholesale merged |
| Post-Wave2 GIGA-Q hardenings | `code/canonical` | CONNECTED_SELECTIVELY_AND_QUALIFIED | source `4efadddf694eff0c0df00925b5b4b89194f32f8e`; non-overlapping blobs selectively recovered, then only proven `v2_core.py` identity/negative-memory semantics repaired |
| GPT-OSS/Codex bounded orchestration | `code/canonical` | CONNECTED_AND_QUALIFIED_IN_CI | PR46 source `afedfd57986aa042e9e97aa53b9db53b4619764f`; current exact-head tests pass; runtime deployment/use still separate |
| Canonical combined-code qualification | `code/canonical` | ENGINEERING_QUALIFIED | head `6039cfd7a8502e0a4727a6928a4ef4cb75a3bb6e`; workflow run `41264501411` SUCCESS |
| Scientific/negative memory | `project/canonical` + code-owned immutable ledgers | REUSE | rejected/superseded history is preserved; GIGA-Q fail-closed negative-memory shape/hash tests pass at current head |
| Authority state | `project/canonical` | ACTIVE_CLOSED | `governance/AUTHORITY_STATE.json`; destructive cleanup also PARK/false |
| Forensic/history | `project/canonical` | HISTORICAL_REFERENCE | global archaeology complete; no restart |
| Actual VM multi-wake GPT-OSS → Codex → GPT-OSS autonomy | external runtime + `code/canonical` | NOT_PROVEN | needs real host/runtime receipts over multiple wakes; CI is insufficient |
| Real-capital/live-trading | none | CLOSED | explicit false authority |
| Side project `restaurant-stock/` | none | RETIRE_FROM_ACTIVE_QUANT | out of Quant scope; no destructive deletion authorized |
| Legacy review/challenge/handoff branches | none | PARK / RETIRE_AFTER_PRESERVATION | evidence remains referenced by SHA/history; branch deletion not authorized |

## Current exact-head qualification proof

`code/canonical=6039cfd7a8502e0a4727a6928a4ef4cb75a3bb6e`

Run `41264501411` executed successfully on that exact head:
- CP099 carried-hardening regressions: `22/22 PASS`;
- PR46 autonomy regressions: `16/16 PASS` plus `GPT_OSS_LAUNCHER_ISOLATION=PASS`;
- Wave2 non-regression sample: `48/48 PASS`;
- post-Wave2 GIGA-Q focused challenge: `110/110 PASS` plus `44 subtests PASS`;
- `CANONICAL_AUTHORITY_CLOSED=PASS`;
- clean checkout: PASS.

This proves the current combined code candidate at the hosted CI level. It does **not** prove deployment, actual VM use, or multi-wake autonomy.

Rule: `REUSE > CONNECT > REPAIR > BUILD`. `PARK`, `BLOCK`, `UNKNOWN`, and `NO_CHANGE_REQUIRED` remain valid outcomes.
