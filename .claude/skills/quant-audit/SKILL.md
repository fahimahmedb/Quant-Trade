---
name: quant-audit
description: Independently audit a Quant change against the North Star using distinct review angles and one deduplicated verdict.
disable-model-invocation: true
effort: xhigh
---

Audit the current change independently from the implementation narrative. First resolve current Blue governance, the exact frozen candidate SHA and the branch-specific audit mission; do not infer authority from the working branch name or STATE.md.

Use a small parallel workflow only if the change is substantive. Give each reviewer a non-overlapping question:

1. causal timeline and persistent-state integrity;
2. restart/liveness/control-plane reliability;
3. research/data validity and evidence truthfulness.

Then synthesize once in the lead context. Deduplicate findings and rank them by impact on correctness and the North Star.

For each material finding report: severity, exact file/function, failure mechanism, evidence, and smallest regression test or correction needed.

Do not edit code during this skill. Do not praise architecture unless the behavior is actually exercised by tests or runtime evidence.
