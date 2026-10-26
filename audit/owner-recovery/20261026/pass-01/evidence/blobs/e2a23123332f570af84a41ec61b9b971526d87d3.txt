# CP093 — Enforce declared epoch model admission before pure export

CP092 reproduced composed READY for unapproved generation and Validator model
names, and for boolean model policy/actor values. The existing core membership
helper was qualified directly but absent from the actual composed consumer.

Reuse assert_model_allowed in the pure pipeline for both trial.model_identity
and validator.validator_model after the existing completed-Validator/PASS check
and before export. Reuse _require_identifiers for each epoch allowed-model entry
and the selected model itself; malformed values cannot become permission by
membership/equality alone. No new model router, registry or dispatch function.

Allowed models, model-routing policy, current native epoch and backend configuration
are unchanged. The deterministic engine remains a valid literal identity. No
composite R0 description is split into an inferred allowed model; the native
critic/dispatch path is separate and not newly attested by pure metadata admission.
Allowed model, independent cognition and model PIT remain distinct claims.

Five new tests cover both actual entrypoint actors, malformed allowed-model entries,
direct literal admission, coherent declared in-set alternatives, no PIT/authority
upgrade, input immutability and deterministic replay. The valid fixture epoch and
entire qualification receipt retain their exact prior goldens. No fixture or
historical scientific object is migrated in this package. Focused 36, root 823 and
broader Research OS 268 PASS; suites overlap. Official inventory regenerated to 823.
Ruff F and whitespace PASS. Exact-source qualification follows this stable source.

North Star edge advanced: frozen epoch model policy -> declared generation and
Validator admission -> export qualification. This is source admission, not model
execution, download, resource availability, semantic independence, economic
validation or deployment. Four authorities stay FALSE. No active/sealed outcome,
prospective observation, experiment, Oracle state write, fallback model or paid
resource. Owner-skipped network/production stays excluded.
