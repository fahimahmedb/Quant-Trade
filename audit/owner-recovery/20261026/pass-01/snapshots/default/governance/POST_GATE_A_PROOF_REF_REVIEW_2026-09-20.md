# POST-GATE-A PROOF REF REVIEW — 2026-09-20

Authority: Blue / Mission Control.
Status: `REVIEW_COMPLETE / NON-DESTRUCTIVE_CLASSIFICATION`

Purpose: re-evaluate the former `KEEP_UNTIL_ASTRA` proof refs now that Gate A v3 repository proof is PASS and the final Astra audit is durable.

## 1. Move to delete-ready

The following refs are now safe to lose as branch names because their exact tip commits are strict ancestors of retained authorities. Their commits remain reachable and their exact historical SHAs are already durably recorded in Gate A evidence/handoffs.

| Branch | Tip | Retained descendant |
|---|---|---|
| `blue/p0-direct-reconcile-fix-2026-09-20` | `dc9769b2790e724aaa281af209d822449d0bedfb` | `blue/p0-gate-a-v3-frozen-2026-09-20` |
| `blue/p0-gate-a-final-2026-09-20` | `19b6069e485c2e619698e235d24a6110556b1865` | `blue/p0-gate-a-v3-frozen-2026-09-20` |
| `builder/p0-integrity-blockers-fingerprint-v1` | `8d5dbb41559c4716e94d5290b6ae979a8b96143c` | `astra/p0-deep-adversarial-pre-t0` |
| `builder/sec-form4-p0-raw-capture-v2` | `859ffafd2f31aa16e26c120def79aa8726517ed0` | `blue/p0-gate-a-v3-frozen-2026-09-20` |
| `codex/reprendre-mission-astra-p0-pre-t0` | `a321bfd9d77d42bb43a4fcd8b774a6eb38789179` | `astra/p0-deep-adversarial-pre-t0` |

All five were live-rechecked after Gate A PASS:
- branch exists;
- tip equals the SHA above;
- branch is unprotected;
- compare reports `behind_by = 0` from the branch tip to the retained descendant.

Classification:
`DELETE_READY_WHEN_DELETE_REF_AVAILABLE`

This is branch-ref cleanup only. It does not erase the historical commits or their evidentiary meaning.

## 2. Preserve explicit divergent falsifier/audit refs

The following remain deliberately preserved because they contain divergent unique history or direct historical falsifiers whose branch-level discoverability is still useful:

- `blue/p0-calendar-direct-reconcile-red-2026-09-20@c81fa1cdf93d5b08265c5f06ed0f4424bdda917f`
  - direct unredirected B1 falsifier lineage;
  - diverged from final v3 line.

- `blue/p0-manual-probe-red-2026-09-20@efbf72484e5e6873aba2446d53a728798b3f453f`
  - historical B3 line;
  - contains/retains the original direct `collector.poll()` discriminant lineage including parent `345e18d94963b4fcc7063d73d1c23aff5244ca28`;
  - diverged from final v3 line.

- `blue/p0-audit-authority-red-2026-09-20@ca0f6b00c3e88e2a6e6d541ad538a529bfb57aee`
  - historical B2 red evidence;
  - diverged by unique audit evidence.

- `blue/checkpoint-gate-a-v2-audit-2026-09-20@4678c29eb8cd22aa7ef143075c6d4b68739026a3`
  - Blue-side v2 audit trail;
  - diverged from canonical Astra v2 audit.

- `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20@357b0e58bcf29832ee72976f757bc12d481c5d45`
  - historical Astra checkpoint containing superseded intermediate conclusions;
  - useful evidence of audit evolution.

- `astra/p0-deep-adversarial-2026-09-19@816b999832d3ebf8d5d535981f232147a2a257f9`
  - earlier independent adversarial trail;
  - diverged substantially from the canonical pre-t0 authority.

- `builder/sec-form4-p0-raw-capture@348c4e42bf4efb29d6e4135cc39b2e5ae31bf5ef`
  - older raw-capture line with unique divergence;
  - preserve until semantic comparison/recovery relevance is explicitly exhausted.

Classification:
`PRESERVE_DIVERGENT_EVIDENCE`

## 3. Cleanup rule

Do not delete a divergent proof branch merely because the final candidate now passes.

A branch ref may be removed when:
1. its unique evidence has been copied/indexed into a retained hash-addressable authority; or
2. Blue explicitly records that the divergence has no remaining replay, recovery, scientific, audit or governance value.

## 4. Current net effect

Additional delete-ready refs after Gate A PASS: **5**.

Previously prepared:
- first safe batch: 18 refs;
- post-Gate strict-ancestor batch: 12 refs.

Current prepared delete-ready total, before de-duplication across batches:
`18 + 12 + 5 = 35 refs`

Physical deletions remain unexecuted because the current connector exposes no safe delete-ref mutation.
