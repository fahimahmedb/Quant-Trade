# BRANCH AUTHORITY REGISTRY — 2026-09-21

Authority: Blue / Mission Control.

## 0. Current facts

`LIVE_BRANCHES = 45`

`DEFAULT_BRANCH = blue/master-v2-2026-09-20`

`OPEN_PRS = 0`

`OPEN_ISSUES = 0`

`PROTECTED_BRANCHES = 0`

`REPOSITORY_RULESETS = 0`

Previous repository-hygiene execution closed at 40 live branches after deleting
34 authorized refs. None of those 34 deleted refs has reappeared.

Exactly five branch names are new relative to the post-cleanup live inventory:

- `builder/p0-hybrid-qualification-harness-2026-09-20`;
- `builder/codex-p0-hybrid-fault-matrix-2026-09-21`;
- `builder/codex-p0-hybrid-known-bad-replay-2026-09-21`;
- `builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`;
- `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21`.

These five are explained by the current hybrid qualification campaign.

## 1. Current route

Current Blue authority:
`blue/master-v2-2026-09-20`.

Frozen production candidate:
`blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`.

Gate A v4 repository disposition:
`PASS`.

Current repository blocker:
`restart_burst_limit = TEST_DEFECT -> MISSING_PROOF`.

Independent blocking audit:
`astra/p0-hybrid-fault-matrix-independent-review-2026-09-21@c6be804e99e409ab36a455f09ea2fccbe3d88252`.

Active Builder repair:
`builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21`.

Prepared mission base:
`6f0ca1d858d6937dc8199cc1690dce049ddb79a6`.

Do not route current work through the known-bad replay branch.

## 2. Cleanup policy

No additional branch deletion is authorized by this registry.

Reason:
the current proof-repair / targeted recheck cycle is still open and several
apparently historical refs are direct evidence dependencies or preserved
falsifiers.

After the restart-burst repair + targeted independent recheck + Blue final
fault-matrix disposition, perform a separate retirement review.

The explicit owner retention override remains:

`claude/restaurant-stock-management-mvp-6oq43e@e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0`

and is not a cleanup candidate.

## 3. Full live inventory

| Branch | HEAD | Current classification | Delete now? |
| --- | --- | --- | --- |
| `astra/checkpoint-gate-a-v2-independent-audit-2026-09-20` | `357b0e58bcf29832ee72976f757bc12d481c5d45` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `astra/p0-deep-adversarial-2026-09-19` | `816b999832d3ebf8d5d535981f232147a2a257f9` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `astra/p0-deep-adversarial-pre-t0` | `643deacdf5bbbdb1d2410c762eb20f72aff16bbf` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `astra/p0-gate-a-v2-independent-audit-2026-09-20` | `64b105f5a2cc1d798d1cf1e41e715b967c845a85` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `astra/p0-gate-a-v3-independent-audit-2026-09-20` | `33995d03c8632e5c3a7b77a12b87366fb06b4d30` | HISTORICAL_REJECTED_TARGET_HOST_EVIDENCE | NO |
| `astra/p0-gate-a-v4-independent-audit-2026-09-20` | `afe25984b0ddd261fda143d858106c3c71e45149` | FINAL_V4_AUDIT_EVIDENCE | NO |
| `astra/p0-hybrid-fault-matrix-independent-review-2026-09-21` | `c6be804e99e409ab36a455f09ea2fccbe3d88252` | FINAL_BLOCKING_AUDIT_EVIDENCE | NO |
| `blue/checkpoint-gate-a-v2-audit-2026-09-20` | `4678c29eb8cd22aa7ef143075c6d4b68739026a3` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `blue/forward-finalization-2026-09-20` | `d209348159c44ba4eac9c0a1999e04f0e96e7108` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/integration-readiness-2026-09-20` | `37e9f95f3e24be78b1cb61ab35244b2880988b12` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/long-horizon-research-2026-09-20` | `7e0fae86834db7f46ecea5755faf0ac544245399` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/master-v2-2026-09-20` | `119c6c833d6a6fa3475443b775a0397ddc78d119` | CURRENT_BLUE_AUTHORITY | NO |
| `blue/p0-audit-authority-fix-2026-09-20` | `a98bc8aef3a397c054a3df495f14a781b1b939de` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `blue/p0-audit-authority-red-2026-09-20` | `ca0f6b00c3e88e2a6e6d541ad538a529bfb57aee` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `blue/p0-calendar-direct-reconcile-red-2026-09-20` | `c81fa1cdf93d5b08265c5f06ed0f4424bdda917f` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `blue/p0-calendar-dst-proof-2026-09-20` | `99a64981b7f3c5e8755782d68d52cb7c7408e764` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-continuity-qualification-2026-09-20` | `3dfc54a4219f1b31374ff4a007f1d9a2dfc0ec4c` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-gate-a-long-history-2026-09-20` | `d79387f06821e2c0c4d345d7d42d05200ac384d3` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-gate-a-v2-final-2026-09-20` | `db166fd04c681e67a2c6d4440828af14ef58c48c` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-gate-a-v2-staging-2026-09-20` | `fd2e0f3b546fa8ad8e67a8368eb6a9a2543c81dc` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-gate-a-v3-frozen-2026-09-20` | `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` | HISTORICAL_REJECTED_TARGET_HOST_EVIDENCE | NO |
| `blue/p0-gate-a-v4-frozen-2026-09-20` | `4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072` | FROZEN_PRODUCTION_CANDIDATE | NO |
| `blue/p0-manual-operator-provenance-fix-2026-09-20` | `927f496a58fe71ffbaa6cce4df5297fe9638d0bb` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-manual-probe-fix-2026-09-20` | `a6924958e88c8f3f4ad38caa2c45bf8db9309116` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `blue/p0-manual-probe-red-2026-09-20` | `efbf72484e5e6873aba2446d53a728798b3f453f` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |
| `builder/codex-p0-hybrid-fault-matrix-2026-09-21` | `e5c4c720e758cd8ab3f0e04faf541b26e204be16` | DIRECT_REPAIR_PREDECESSOR | NO |
| `builder/codex-p0-hybrid-known-bad-replay-2026-09-21` | `565e4eb4c1240bbd23c00f2dc2c4e1d7aca7840b` | USEFUL_OUT_OF_ORDER_EVIDENCE | NO_FOR_NOW |
| `builder/codex-p0-hybrid-restart-burst-proof-fix-2026-09-21` | `6f0ca1d858d6937dc8199cc1690dce049ddb79a6` | ACTIVE_BUILDER_REPAIR | NO |
| `builder/evidence-store-identity-v2` | `b8f7dffbe040753cb1e47b7f38f3ab4485e1e7ba` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/forward-market-recorder-v2` | `87bd049574ec41fe9d22b2ffcfdfc06ec7b7166a` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/p0-effective-unit-digest-stability-v4-2026-09-20` | `b10cde0dd193714346abdfe87afb841482e9b7c8` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/p0-gate-a-v3-2026-09-20` | `2da079d8ad75c69eb3fc2990c512735cb4bdc02b` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/p0-hybrid-qualification-harness-2026-09-20` | `d4d446c412258b2a9e4792cdcd9e2442ef24b615` | DIRECT_EVIDENCE_PREDECESSOR | NO |
| `builder/research-factory-core-v2` | `ca8ffe439953b063fb9d049773ce0b6245958c7d` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/sec-form4-census-v2a` | `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `builder/sec-form4-p0-raw-capture` | `348c4e42bf4efb29d6e4135cc39b2e5ae31bf5ef` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `claude/nasdaq-trading-model-design-h3mp4n` | `8fea558143d0c46bc6eeb9f2aa57527b4e6c1fce` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `claude/restaurant-stock-management-mvp-6oq43e` | `e083cc70e3f4c2ce31ea04f4fc43be35e9549ab0` | OWNER_RETENTION_OVERRIDE | NO |
| `codex/test` | `723a778e302b6bc96e72030ded91440f75769aba` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `parallel/claude-economic-v2-2026-09-20` | `35dff27b8fac53618da434ee6d31febbddcc0e69` | CANONICAL_PRODUCT_LEAF_PAUSED | NO |
| `parallel/claude-forward-data-2026-09-20` | `83521dbfdd90027c90d04adfb7d814593c2355c5` | CANONICAL_PRODUCT_LEAF_PAUSED | NO |
| `parallel/codex-wave1-economic-system-2026-09-19` | `738a5879ef8634d3e08c717a2d439632fe64e1ff` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `recovery/claude-sec-local-20260914` | `ac37339ed31b59f2c16caed6a5e914e647006671` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `research/design-v1` | `2da2d1b6786e9a7b1d34f94f5066dca79abf8e07` | RETAINED_HISTORICAL_OR_PRODUCT_REFERENCE | REVIEW_LATER |
| `reviewer/v1-final-red-team` | `37f298423ca4a100c1c633da2c3c6c2641d8dd8e` | HISTORICAL_AUDIT_OR_FALSIFIER_EVIDENCE | REVIEW_LATER |

## 4. Governance observation

All 45 live branches are currently unprotected and the repository has zero
rulesets.

Classification:
`GOVERNANCE_HARDENING_DEBT / NOT_CURRENT_P0_BLOCKER`.

Do not mix branch-protection changes into the active proof-repair mission.

## 5. Safety

Branch existence does not imply authority.
Green CI does not imply Gate PASS.
Deletion eligibility requires a separate exact-SHA retirement decision.

`P14D_PROMOTION_READY = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

## 4. LATEST AUTHORITY OVERRIDE — F11 FRONTIER

This section supersedes stale active-branch classifications above.

Current Blue authority:

`blue/master-v2-2026-09-20`

Latest compact restart surface:

`handoff/BLUE_CONTEXT_REACQUISITION_F11_2026-09-21.md`

Current audited integration object:

`blue/gate-b-run-authority-repair-integration-2026-09-21@644da76eb0227be275b8e3448118dac0cc7096ca`

Final Astra review branch:

`astra/gate-b-run-authority-mechanisms-recheck-2026-09-21@41c3f291f46b7b5849bdb702c09ccefbeecde691`

Classification:

`FINAL_ASTRA_RECHECK / BLOCKED_F11 / PRESERVE`

Antigravity Product-prestage branch:

`parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21@568eea1e028302e14f96a06eb2515bb89aa73ad4`

Classification:

`PRODUCT_PRESTAGE_COMPLETE / PRESERVE_FOR_FUTURE_INTEGRATION`

Historical R1 repair:

`builder/gate-b-run-authority-m1-m3-repair-2026-09-21@2d2ff4e32f239fb7ef41d9e44745005f5f5fb44a`

Classification:

`DELIVERED_REPAIR_EVIDENCE / PRESERVE_UNTIL_F11_CLOSURE`

Historical R2 repair:

`builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21@e19f45709b9e0c2a6d6d22c4d666b701a5bced86`

Classification:

`DELIVERED_REPAIR_EVIDENCE / PRESERVE_UNTIL_F11_CLOSURE`

Next expected branch:

`builder/gate-b-f11-lock-identity-repair-2026-09-21`

Status at this override:

`NOT_YET_CREATED`

Do not delete or repurpose any of the above refs until Blue records F11 closure and a subsequent branch-retirement decision.



## LIVE F11 BUILDER DISPATCH OVERRIDE — 2026-09-21

This section supersedes the earlier `NOT_YET_CREATED` classification for the F11 repair branch.

Active branch:

`builder/gate-b-f11-lock-identity-repair-2026-09-21@8a30bd385f6f6c04c085bb72cb0c853c5de3c3b8`

Exact audited implementation base:

`644da76eb0227be275b8e3448118dac0cc7096ca`

Blue F11 spec on Builder branch:

`113e60cb6ae9a56ffb4adb83c13a797e3563369e`

Classification:

`ACTIVE_BOUNDED_F11_BUILDER_REPAIR / PRESERVE`

Allowed mission scope is limited by:

`governance/BLUE_GATE_B_F11_LOCK_IDENTITY_REPAIR_SPEC_2026-09-21.md`

The Builder may return only `READY_FOR_INDEPENDENT_REVIEW` or an explicit blocker.

Do not create a parallel/overlapping F11 repair branch.
Do not delete or repurpose this branch until independent Astra closure and subsequent Blue retirement review.
