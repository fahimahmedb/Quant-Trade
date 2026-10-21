# CP092 — Epoch model policy -> qualification, before code

CP091/de54073 qualifies source d620b01 with both exact-source workflows SUCCESS.
Whole-Quant scope, Owner North Star a328b4e, four closed authorities and the
Owner-skipped network/production task remain unchanged. Latest Oracle source
reacquisition 2b4b9a9 differs from integrated d2e58a7 only by wake receipts.

Actual pure entrypoint reproductions use the existing attributed synthetic fixture:
1. Replace trial.model_identity with outside-the-epoch-model-set: READY is returned.
2. Replace validator.validator_model with the same unapproved name: READY is returned.
3. Set allowed_model_set=[true] and both declared model values=true: READY is returned.
Candidate/proposal/Validator binding remains coherent; no model is invoked and no
outcomes or external model resource is accessed. These are qualification/admission
errors, not proof of an actual unauthorized native model dispatch.

History/reuse: assert_model_allowed already rejects a model outside a built epoch
in the core's direct unit test, but run_pre_outcome_pipeline never invokes it.
build_epoch_manifest validates a nonempty model list, not attributable entries.
Reuse the existing helper and identifier predicate rather than create a router.

Require attributable literal model names in epoch policy and model admission;
after the existing completed-Validator/PASS checks, enforce both trial and Validator
model membership before pure export. Do not add models, normalize unapproved aliases,
upgrade backend versions, download weights or silently choose a fallback.

Native model dispatch/resource qualification is separate. Its deterministic engine
label and composite R0 Validator/critic description are not interchangeable with
raw model IDs; no string splitting or inferred native semantic permission is justified.
Preserve deterministic/local allowed names and current native source behavior.
Independent Validator execution remains distinct from cognitive diversity and
model PIT. An allowed model is not automatically independent or provably PIT.

Test both actual entrypoint actor declarations, malformed allowed-model entries,
literal direct admission, valid declared in-set models, deterministic replay and
unchanged valid fixture golden. Preserve existing blockers and immutable input
objects. Qualify the resulting stable source; do not infer hosted success from
unit counts or alter canonical Oracle policy/scientific state.
