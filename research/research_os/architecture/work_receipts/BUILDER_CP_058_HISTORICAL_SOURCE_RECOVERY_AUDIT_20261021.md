# CP058 — Exact CP057 qualification and scoped historical recovery audit

Source release: fecd09e0839f1208d9f876c311331221bde3ab7d. Both hosted workflows
succeeded: Oracle V2 Core 39517451814 (16 job steps) and SEC P0 pre-t0
39517451804 (17 steps). Adjacent JSON archives observed job metadata and page
hashes; artifact payloads were not downloaded. Local root 759, core V2 268,
broader Research OS 268, shared metadata 2 and JavaScript 57 pass; suites overlap.
The real read-only GitHub worker reported zero writes/push. This is qualification
of source, not proof of production installation, Site ingress or reboot.

Reacquired Oracle efe05e51722d1641052c25b5073834e0479a612b: changes since the
merged d2e58a7 are bounded wake receipts only. North Star remains unchanged.

## Reuse/integrate decision before code

CP12 at forensic commit 67543ff explicitly requires preserving codex/test's
unique negative result before any retirement. Source commit
723a778e302b6bc96e72030ded91440f75769aba contains P0-E1: the completed ledger
entry reports researcher KILL, independent judge REJECT and consumed holdout.
Only historical verdict/protocol metadata was inspected; no raw return series,
result JSON, active sealed Evaluation data or prospective observations were read.

Exact source blobs:
- research/ledger.jsonl: effa8d35602c2967cd30b03c35bd64050cf2a5c9
- evaluation/phase0_e1_judgment.md: 85761cf47d15fb17eb01abddcff3dddcd7d8cba1
- research/EXPERIMENT_PROTOCOL.md: afeab9a43600b8da8db02e766a624f5210f75f5b

The pinned 20-record legacy ledger has no explicit P0-E1/723a778 provenance in
its identity/source fields. A NASDAQ reversal KILL with unknown result commit
is not sufficient to identify this volatility-exposure experiment. The 33-item
manifest count uses different units and is not evidence of 13 missing records.

Existing LegacyKnowledgeBase and native worker screening already route overlap
to review and preserve durable screen artifacts. Reuse those edges. Integrate
one source-review entry into the existing legacy manifest and reader, separate
from immutable imported ledger records. Match original identity or conservative
mechanism overlap; expose original verdict, protocol scope, caveats and revisit
conditions as REVIEW_LEGACY_OVERLAP, never automatic scientific KILL or broad
family rejection. Expose recovery counts/hashes through existing preflight.
Do not invent V2 trial membership, map TSR-NDX-001 to P0-E1, change the pinned
ledger/counts, import numerical outcomes or claim reconciliation complete.
No additional memory engine, scheduler or historical rerun is justified.

All four authority flags remain FALSE. No production mutation or branch cleanup.
Next: implement scoped source recovery, test its connection to actual screening,
then reassess remaining unique Factory/SEC and operational boundaries.
