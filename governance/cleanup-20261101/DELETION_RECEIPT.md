# Dependency-First Branch Deletion Receipt

- Snapshot: `2026-11-01T13:39:34.460914+00:00`
- Start branches: **279**
- Deleted so far: **0**
- Default branch preserved: `blue/master-v2-2026-09-20`
- Active auditor preserved: `audit/forensic-checkpoint-20261019` @ `463e90970f5de02176f8a4696b94dce8f757c58a`

## Deleted refs

| Branch | Audited/current tip at deletion |
|---|---|
| — | — |

## Safety rule

Each deletion used a server-side force-with-lease against the exact re-read remote SHA. A changed ref, live dependency, open PR/issue dependency, active auditor/agent ref, default branch, or tip not reachable from a retained ref was not deleted.
