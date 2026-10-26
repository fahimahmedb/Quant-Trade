# BUILDER CP014 — Documentary control falsely classified as outcome demand

BRANCH: builder/v2-forward-20261020
BASE_SHA: 55a1f1d17afb3de5b596285ce5db761369d421c5
FRESH_ORACLE_HEAD: b2714598a3a5d2fb81869ded163a01a62f99b857
SAFE_TO_CONTINUE: TRUE

CP013 identified a conservative classification residual. Reproduced it using
the existing producer-readiness helper and existing EVENT_DOCUMENT fixtures:
readiness qualification PASS; four explicit requirements; no declared routes;
three unresolved intents and one BLOCK_FORBIDDEN_REQUIREMENT.

The blocked text is the exact existing source_qualification.py declaration:
`concurrent-news/confounder controls declared before outcome access`.
It describes a predeclared documentary control, not an outcome observation.
The generic substring check rejects it solely because it contains "outcome".
No route, source or permission failure explains that particular rejection.

## Minimal correction and adversarial contract

Recognize only this exact existing declaration as a documentary control before
the generic forbidden-demand text check. Do not infer meaning from arbitrary
negations, prefixes, suffixes, synonyms, case folding or prose. Preserve the
upstream specification/text/hash; do not reword producer requirements to evade
the firewall. Any altered or extended outcome-bearing requirement still blocks.

This recognition does not grant plan readiness: no exact route remains
UNRESOLVED_NO_DECLARED_ROUTE. A supplied exact route must still pass all existing
PIT/version, adapter and content-class checks and the existing acquisition
firewall. Forbidden outcome content must block even for the recognized control.

Required tests: real producer helper end-to-end with unchanged upstream artifact;
exact control with no route; explicit safe route gives plan-only; forbidden
content/active adapter/invalid PIT still block; injected outcome wording and
near-matches remain forbidden. No acquisition, provider invention, source
activation, task mutation or runtime/Site change.

## Workflow

Audit only at this checkpoint. Next implement the bounded recognition and
adversarial tests, refresh the official generated test inventory before the
code push, run full local regression and both exact-commit hosted gates, and
persist the qualification evidence. All four authorities remain FALSE;
OUTCOME_ACCESSED FALSE; ECONOMIC_RESULT NOT_OBSERVED.
