"""Bounded offline governance tests; no research fixtures or economic evidence.

All objects below are deterministic TEST_ONLY structural values. The injected
root exists only under unittest.mock.patch in this test process and is never
production execution authority. Private finalizer calls test the audited
internal invariant, not a supported public API bypass.
"""
from __future__ import annotations

from dataclasses import fields, replace
import unittest
from unittest.mock import patch

from research.weather_forward.v4 import a2_harness as api
from research.weather_forward.v4.a2_harness import contract as c
from research.weather_forward.v4.a2_harness import harness as h
from research.weather_forward.v4.a2_harness import trusted_root as production_root


class TestContext:
    """Metadata-only TEST_ONLY objects; contains no payload, seed or real input."""

    def __init__(self):
        self.binding = api.AuthorityBinding(
            "1" * 40, "TEST_ONLY_HARNESS", "TEST_ONLY_VERSION", "TEST_ONLY_MANIFEST_V1"
        )
        self.reader = api.RoleDeclaration("TEST_ONLY_READER", api.Role.EXECUTOR)
        self.recipient = api.RoleDeclaration("TEST_ONLY_RECIPIENT", api.Role.RESEARCH_VIEWER)
        self.approver = api.RoleDeclaration("TEST_ONLY_APPROVER", api.Role.RELEASE_APPROVER)
        self.input = api.InputManifest(
            input_id="TEST_ONLY_INPUT",
            manifest_version_identity=self.binding.manifest_version_identity,
            input_classification=api.InputClassification.DOCUMENTATION_ONLY,
            source_provenance_class="TEST_ONLY_STATIC_SCHEMA",
            exact_permitted_fields=("TEST_ONLY_FIELD_A", "TEST_ONLY_FIELD_B"),
            exact_prohibited_fields=("TEST_ONLY_PROHIBITED_PAYLOAD",),
            permitted_reader_roles=(api.Role.EXECUTOR,),
            raw_values_visible=api.VisibilityState.HIDDEN,
            timestamps_visible=api.VisibilityState.HIDDEN,
            frequency_or_count_information_visible=api.VisibilityState.HIDDEN,
            longitudinal_observation_allowed=api.PermissionState.DENIED,
            aggregation_allowed=api.PermissionState.DENIED,
            cross_source_comparison_allowed=api.PermissionState.DENIED,
            efficacy_leakage_assessment=api.LeakageAssessment.CLEAR,
            access_logging_requirement=api.RequirementState.REQUIRED,
            quarantine_on_ambiguity=api.RequirementState.REQUIRED,
            owner_approval_required=api.RequirementState.REQUIRED,
        )
        self.output = api.OutputManifest(
            output_id="TEST_ONLY_OUTPUT",
            manifest_version_identity=self.binding.manifest_version_identity,
            output_type="TEST_ONLY_DOCUMENTARY_STATUS",
            exact_metric_or_artifact="TEST_ONLY_STRUCTURAL_STATUS",
            granularity="TEST_ONLY_SINGLE_STATUS",
            permitted_recipients=(api.Role.RESEARCH_VIEWER, api.Role.EXECUTOR),
            exportability=api.PermissionState.ALLOWED,
            quarantine_status=api.QuarantineState.CLEAR,
            cumulative_disclosure_risk=api.CumulativeDisclosureState.CLEAR,
            efficacy_leakage_assessment=api.LeakageAssessment.CLEAR,
            release_approval_requirement=api.RequirementState.REQUIRED,
            retention_rule="TEST_ONLY_NO_OPERATIONAL_RETENTION",
            incident_if_unexpected_information_revealed="TEST_ONLY_STOP",
        )
        self.provenance = api.FixtureProvenance(
            fixture_id="TEST_ONLY_METADATA_NOT_A_FIXTURE",
            construction_input_classes=(
                api.InputClassification.DOCUMENTATION_ONLY,
                api.InputClassification.NON_ECONOMIC_SYNTHETIC,
            ),
            generator_identity="TEST_ONLY_ABSTRACT_GENERATOR",
            generator_version="TEST_ONLY_GENERATOR_VERSION",
            lineage_references=("TEST_ONLY_DOCUMENT_A", "TEST_ONLY_DOCUMENT_B"),
            reproducibility_metadata=(
                ("test_spec_revision", "TEST_ONLY_V1"),
                ("construction_kind", "TEST_ONLY_STRUCTURAL"),
            ),
            contamination_state=api.ContaminationState.CLEAR,
            admissibility_state=api.AdmissibilityState.ADMISSIBLE,
        )
        self.provenance_contract = api.FixtureProvenanceContract(
            expected_fixture_id=self.provenance.fixture_id,
            expected_generator_identity=self.provenance.generator_identity,
            expected_generator_version=self.provenance.generator_version,
            expected_construction_input_classes=self.provenance.construction_input_classes,
            expected_lineage_references=self.provenance.lineage_references,
            required_reproducibility_keys=("test_spec_revision", "construction_kind"),
            allowed_reproducibility_keys=("test_spec_revision", "construction_kind"),
            expected_fixture_provenance_identity=api.fixture_provenance_identity(self.provenance),
        )
        self.policy = api.HarnessPolicy(
            expected_owner_authority_sha=self.binding.owner_authority_sha,
            expected_harness_identity=self.binding.harness_identity,
            expected_harness_version_or_commit_identity=self.binding.harness_version_or_commit_identity,
            expected_manifest_version_identity=self.binding.manifest_version_identity,
            expected_input_manifest_id=self.input.input_id,
            expected_input_manifest_identity=api.input_manifest_identity(self.input),
            expected_output_manifest_id=self.output.output_id,
            expected_output_manifest_identity=api.output_manifest_identity(self.output),
            allowed_input_classifications=(
                api.InputClassification.DOCUMENTATION_ONLY,
                api.InputClassification.NON_ECONOMIC_SYNTHETIC,
            ),
            prohibited_input_classifications=(
                api.InputClassification.UNKNOWN,
                api.InputClassification.PROHIBITED,
                api.InputClassification.REAL_TECHNICAL_METADATA,
            ),
            fixture_provenance_contract=self.provenance_contract,
            permitted_recipient_actor_roles=((self.recipient.actor_id, self.recipient.declared_role),),
        )
        self.root = self.root_for(self.policy)
        self.read_auth = self.authorization(self.reader, api.Action.READ_INPUT)
        self.admit_auth = self.authorization(self.reader, api.Action.ADMIT_FIXTURE_METADATA)
        self.release_auth = self.authorization(self.approver, api.Action.RELEASE_OUTPUT)
        self.ledger = api.CumulativeDisclosureLedger((
            api.DisclosureRecord(
                "TEST_ONLY_DISCLOSURE", self.output.output_id,
                self.recipient.actor_id, self.recipient.declared_role,
                api.CumulativeDisclosureState.CLEAR,
            ),
        ))

    def root_for(self, policy):
        return api.TrustedExecutionPolicyRoot(
            "2" * 40, self.binding.owner_authority_sha,
            self.binding.harness_identity, self.binding.harness_version_or_commit_identity,
            api.harness_policy_identity(policy),
        )

    def authorization(self, actor, action):
        return api.ActionAuthorization(
            "TEST_ONLY_AUTH_" + action.value, "2" * 40,
            actor.actor_id, actor.declared_role, action, api.AuthorizationState.AUTHORIZED,
        )

    def harness(self, policy=None, binding=None):
        return api.A2Harness(binding or self.binding, policy or self.policy)

    def read(self, *, policy=None, binding=None, manifest=None, actor=None,
             authorization=None, log=None, log_id="TEST_ONLY_LOG_READ"):
        return self.harness(policy, binding).evaluate_input_read(
            log if log is not None else api.StructuredAuditLog(()), log_id,
            manifest if manifest is not None else self.input,
            actor if actor is not None else self.reader,
            authorization if authorization is not None else self.read_auth,
        )

    def admit(self, *, provenance=None, policy=None):
        return self.harness(policy).evaluate_fixture_metadata_admission(
            api.StructuredAuditLog(()), "TEST_ONLY_LOG_METADATA",
            provenance if provenance is not None else self.provenance,
            self.reader, self.admit_auth,
        )

    def release(self, *, recipient=None, actor=None, authorization=None, ledger=None,
                manifest=None, policy=None, log=None, log_id="TEST_ONLY_LOG_RELEASE"):
        return self.harness(policy).evaluate_output_release(
            log if log is not None else api.StructuredAuditLog(()), log_id,
            manifest if manifest is not None else self.output,
            recipient if recipient is not None else self.recipient,
            actor if actor is not None else self.approver,
            authorization if authorization is not None else self.release_auth,
            ledger if ledger is not None else self.ledger,
        )


class RuntimeCase(unittest.TestCase):
    def setUp(self):
        self.ctx = TestContext()

    def root_patch(self, root=None):
        return patch.object(h, "get_trusted_execution_policy_root", return_value=root or self.ctx.root)

    def assert_denied(self, result, reason=None):
        self.assertIs(result.decision.permit_or_deny_state, api.PermitState.DENY)
        self.assertIs(result.decision.release_state, api.ReleaseState.BLOCKED)
        self.assertIsNot(result.decision.validation_state, api.ValidationState.VALID)
        if reason is not None:
            self.assertIs(result.decision.stop_reason, reason)

    def assert_permitted(self, result, release=False):
        decision = result.decision
        self.assertIs(decision.permit_or_deny_state, api.PermitState.PERMIT)
        self.assertIs(decision.validation_state, api.ValidationState.VALID)
        self.assertIs(decision.completion_state, api.CompletionState.COMPLETED)
        self.assertIs(decision.release_state,
                      api.ReleaseState.AUTHORIZED if release else api.ReleaseState.BLOCKED)
        self.assertTrue(result.log_acknowledged)
        self.assertIsNotNone(result.log_record)
        linked = tuple(r for r in result.log.records if r.record_id == result.log_record.record_id)
        self.assertEqual(linked, (result.log_record,))
        self.assertIs(result.log_record.permit_or_deny_state, decision.permit_or_deny_state)
        self.assertIs(result.log_record.release_state, decision.release_state)


class TrustedRootTests(RuntimeCase):
    def test_production_root_absent_denies_all_authority_bearing_paths(self):
        self.assertIsNone(production_root.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)
        self.assertIsNone(production_root.CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY)
        self.assertIsNone(production_root.get_trusted_execution_policy_root())
        self.assertIsNone(h.get_trusted_execution_policy_root())
        for result in (self.ctx.read(), self.ctx.admit(), self.ctx.release()):
            self.assert_denied(result, api.StopReason.MISSING_EXECUTION_POLICY_ROOT)
        self.assertIsNot(self.ctx.harness().validate_resource_boundary(
            api.ResourceBoundaryState.WITHIN_AUTHORITY).state, api.ValidationState.VALID)

    def test_coordinated_caller_substitution_cannot_create_production_root(self):
        binding = replace(self.ctx.binding, owner_authority_sha="3" * 40,
                          harness_identity="TEST_ONLY_SUBSTITUTED_HARNESS")
        policy = replace(self.ctx.policy, expected_owner_authority_sha=binding.owner_authority_sha,
                         expected_harness_identity=binding.harness_identity)
        self.assert_denied(self.ctx.read(binding=binding, policy=policy),
                           api.StopReason.MISSING_EXECUTION_POLICY_ROOT)

    def test_caller_substitution_cannot_replace_independent_root_patch(self):
        binding = replace(self.ctx.binding, owner_authority_sha="3" * 40)
        policy = replace(self.ctx.policy, expected_owner_authority_sha=binding.owner_authority_sha)
        with self.root_patch():
            self.assert_denied(self.ctx.read(binding=binding, policy=policy),
                               api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)

    def test_test_only_root_exercises_positive_paths_and_is_restored(self):
        with self.root_patch():
            self.assert_permitted(self.ctx.read())
            self.assert_permitted(self.ctx.admit())
            self.assert_permitted(self.ctx.release(), release=True)
        self.assertIsNone(h.get_trusted_execution_policy_root())
        self.assertIsNone(production_root.get_trusted_execution_policy_root())

    def test_wrong_execution_policy_authority_denies(self):
        with self.root_patch():
            self.assert_denied(self.ctx.read(
                authorization=replace(self.ctx.read_auth, authority_sha="3" * 40)),
                api.StopReason.AUTHORITY_MISMATCH)


class ProvenanceTests(RuntimeCase):
    def test_exact_valid_metadata_only_contract(self):
        with self.root_patch():
            result = self.ctx.admit()
            self.assert_permitted(result)
            self.assertEqual(result.log_record.manifest_identity,
                             api.fixture_provenance_identity(self.ctx.provenance))

    def test_no_provenance_contract_denies(self):
        policy = replace(self.ctx.policy, fixture_provenance_contract=None)
        with self.root_patch(self.ctx.root_for(policy)):
            self.assert_denied(self.ctx.admit(policy=policy),
                               api.StopReason.FIXTURE_PROVENANCE_MISMATCH)

    def test_wrong_expected_provenance_digest_denies(self):
        contract = replace(self.ctx.provenance_contract,
                           expected_fixture_provenance_identity="sha256:" + "0" * 64)
        policy = replace(self.ctx.policy, fixture_provenance_contract=contract)
        with self.root_patch(self.ctx.root_for(policy)):
            self.assert_denied(self.ctx.admit(policy=policy),
                               api.StopReason.FIXTURE_PROVENANCE_MISMATCH)


class RecipientTests(RuntimeCase):
    def test_exact_actor_and_role_succeeds_with_all_other_gates(self):
        with self.root_patch():
            self.assert_permitted(self.ctx.release(), release=True)

    def test_clear_cumulative_ledger_never_substitutes_for_recipient_permission(self):
        other = replace(self.ctx.recipient, actor_id="TEST_ONLY_OTHER_RECIPIENT")
        record = replace(self.ctx.ledger.records[0], recipient_actor_id=other.actor_id)
        ledger = api.CumulativeDisclosureLedger((record,))
        self.assertIs(ledger.evaluate_for(self.ctx.output.output_id,
                                         other.actor_id, other.declared_role),
                      api.CumulativeDisclosureState.CLEAR)
        with self.root_patch():
            self.assert_denied(self.ctx.release(recipient=other, ledger=ledger),
                               api.StopReason.UNAUTHORIZED_RECIPIENT)

    def test_wrong_mapped_role_is_denied_even_if_manifest_role_is_allowed(self):
        other = replace(self.ctx.recipient, declared_role=api.Role.EXECUTOR)
        self.assertIn(other.declared_role, self.ctx.output.permitted_recipients)
        with self.root_patch():
            self.assert_denied(self.ctx.release(recipient=other),
                               api.StopReason.UNAUTHORIZED_RECIPIENT)

    def test_same_valid_role_wrong_actor_denies(self):
        with self.root_patch():
            self.assert_denied(self.ctx.release(recipient=replace(
                self.ctx.recipient, actor_id="TEST_ONLY_OTHER_ACTOR")),
                api.StopReason.UNAUTHORIZED_RECIPIENT)


class ReleaseApprovalTests(RuntimeCase):
    def test_required_release_approver_is_independent(self):
        actor = replace(self.ctx.approver, actor_id=self.ctx.recipient.actor_id)
        authorization = replace(self.ctx.release_auth, actor_id=actor.actor_id)
        with self.root_patch():
            self.assert_denied(self.ctx.release(actor=actor, authorization=authorization),
                               api.StopReason.RELEASE_INDEPENDENCE_VIOLATION)

    def test_wrong_release_role_denies_even_with_matching_authorization(self):
        actor = replace(self.ctx.approver, declared_role=api.Role.EXECUTOR)
        authorization = replace(self.ctx.release_auth, declared_role=actor.declared_role)
        with self.root_patch():
            self.assert_denied(self.ctx.release(actor=actor, authorization=authorization),
                               api.StopReason.RELEASE_NOT_AUTHORIZED)


class LoggingTests(RuntimeCase):
    def denial(self):
        return api.HarnessDecision(
            api.ValidationState.BLOCKED, api.PermitState.DENY,
            api.QuarantineState.BLOCKED_PENDING_OWNER_REVIEW, api.ReleaseState.BLOCKED,
            api.CompletionState.NOT_COMPLETED, api.StopReason.LOGGING_REQUIRED,
            "TEST_ONLY_DENIAL",
        )

    def test_direct_permit_decision_is_rejected(self):
        with self.assertRaises(ValueError):
            api.HarnessDecision(
                api.ValidationState.VALID, api.PermitState.PERMIT,
                api.QuarantineState.CLEAR, api.ReleaseState.BLOCKED,
                api.CompletionState.COMPLETED, None, "TEST_ONLY_DIRECT_PERMIT",
            )

    def test_direct_authorized_decision_is_rejected(self):
        with self.assertRaises(ValueError):
            api.HarnessDecision(
                api.ValidationState.VALID, api.PermitState.DENY,
                api.QuarantineState.CLEAR, api.ReleaseState.AUTHORIZED,
                api.CompletionState.COMPLETED, None, "TEST_ONLY_DIRECT_AUTHORIZED",
            )

    def test_direct_permissive_logged_result_is_rejected(self):
        with self.root_patch():
            decision = self.ctx.read().decision
        with self.assertRaises(ValueError):
            api.LoggedActionResult(decision, api.StructuredAuditLog(()), None, False)

    def test_fake_acknowledged_logged_result_is_rejected(self):
        with self.assertRaises(ValueError):
            api.LoggedActionResult(self.denial(), api.StructuredAuditLog(()), None, True)

    def test_direct_log_link_without_acknowledgement_is_rejected(self):
        with self.root_patch():
            record = self.ctx.read().log_record
        with self.assertRaises(ValueError):
            api.LoggedActionResult(self.denial(), api.StructuredAuditLog((record,)), record, False)

    def test_duplicate_log_id_fails_closed(self):
        with self.root_patch():
            first = self.ctx.read()
            result = self.ctx.read(log=first.log)
        self.assert_denied(result, api.StopReason.LOGGING_REQUIRED)
        self.assertIs(result.decision.completion_state, api.CompletionState.NOT_COMPLETED)
        self.assertFalse(result.log_acknowledged)
        self.assertEqual(result.log, first.log)

    def test_append_not_acknowledged_cannot_return_permissive_completed_state(self):
        def refuse(log, record):
            return api.LogAppendAcknowledgement(False, record.record_id, log)
        with self.root_patch(), patch.object(api.StructuredAuditLog, "append", refuse):
            result = self.ctx.read()
        self.assert_denied(result, api.StopReason.LOGGING_REQUIRED)
        self.assertIs(result.decision.completion_state, api.CompletionState.NOT_COMPLETED)
        self.assertFalse(result.log_acknowledged)

    def test_ack_wrong_record_id_fails_closed(self):
        def wrong(log, record):
            return api.LogAppendAcknowledgement(True, "TEST_ONLY_WRONG_LOG_ID",
                                               api.StructuredAuditLog((record,)))
        with self.root_patch(), patch.object(api.StructuredAuditLog, "append", wrong):
            self.assert_denied(self.ctx.read(), api.StopReason.LOGGING_REQUIRED)

    def test_ack_missing_stored_record_fails_closed(self):
        def wrong(log, record):
            return api.LogAppendAcknowledgement(True, record.record_id, log)
        with self.root_patch(), patch.object(api.StructuredAuditLog, "append", wrong):
            self.assert_denied(self.ctx.read(), api.StopReason.LOGGING_REQUIRED)

    def test_ack_duplicate_stored_record_fails_closed(self):
        def wrong(log, record):
            return api.LogAppendAcknowledgement(True, record.record_id,
                                               api.StructuredAuditLog((record, record)))
        with self.root_patch(), patch.object(api.StructuredAuditLog, "append", wrong):
            self.assert_denied(self.ctx.read(), api.StopReason.LOGGING_REQUIRED)

    def test_same_record_id_different_content_is_rejected_at_public_action(self):
        def wrong(log, record):
            changed = replace(record, target_id="TEST_ONLY_WRONG_TARGET")
            return api.LogAppendAcknowledgement(True, record.record_id,
                                               api.StructuredAuditLog((changed,)))
        with self.root_patch(), patch.object(api.StructuredAuditLog, "append", wrong):
            result = self.ctx.read()
        self.assert_denied(result, api.StopReason.LOGGING_REQUIRED)
        self.assertFalse(result.log_acknowledged)

    def test_exact_acknowledged_record_and_context_guarded_path(self):
        with self.root_patch():
            result = self.ctx.release()
        self.assert_permitted(result, release=True)
        record = result.log_record
        self.assertEqual(record.actor_id, self.ctx.approver.actor_id)
        self.assertEqual(record.actor_role, self.ctx.approver.declared_role)
        self.assertEqual(record.authorization_id, self.ctx.release_auth.authorization_id)
        self.assertEqual(record.authorization_authority_identity, self.ctx.release_auth.authority_sha)
        self.assertEqual(record.construction_authority_identity, self.ctx.binding.owner_authority_sha)
        self.assertEqual(record.execution_policy_authority_identity, self.ctx.root.execution_policy_authority_sha)
        self.assertEqual(record.target_id, self.ctx.output.output_id)
        self.assertEqual(record.manifest_identity, api.output_manifest_identity(self.ctx.output))
        self.assertEqual(record.recipient_actor_id, self.ctx.recipient.actor_id)
        self.assertIs(record.recipient_role, self.ctx.recipient.declared_role)

    def test_log_append_duplicate_content_is_not_acknowledged(self):
        with self.root_patch():
            result = self.ctx.read()
        for record in (result.log_record, replace(result.log_record,
                                                actor_id="TEST_ONLY_OTHER_LOG_ACTOR")):
            acknowledgement = result.log.append(record)
            self.assertFalse(acknowledgement.appended)
            self.assertEqual(acknowledgement.log, result.log)

    def finalizer_context(self):
        with self.root_patch():
            result = self.ctx.release()
        record = result.log_record
        return dict(
            acknowledgement=api.LogAppendAcknowledgement(True, record.record_id, result.log),
            log_record=record,
            validation_state=api.ValidationState.VALID,
            permit_or_deny_state=api.PermitState.PERMIT,
            quarantine_state=api.QuarantineState.CLEAR,
            release_state=api.ReleaseState.AUTHORIZED,
            completion_state=api.CompletionState.COMPLETED,
            stop_reason=None,
            detail_code="TEST_ONLY_GUARDED_FINALIZER",
            expected_construction_authority_identity=self.ctx.binding.owner_authority_sha,
            expected_execution_policy_authority_identity=self.ctx.root.execution_policy_authority_sha,
            expected_actor=self.ctx.approver,
            expected_authorization=self.ctx.release_auth,
            expected_action=api.Action.RELEASE_OUTPUT,
            expected_target_kind=api.TargetKind.OUTPUT_MANIFEST,
            expected_target_id=self.ctx.output.output_id,
            expected_manifest_identity=api.output_manifest_identity(self.ctx.output),
            expected_incident_identifier=None,
            expected_cumulative_disclosure_state=api.CumulativeDisclosureState.CLEAR,
            expected_recipient=self.ctx.recipient,
        )

    def test_internal_finalizer_exact_context_succeeds(self):
        self.assert_permitted(c._finalize_logged_action_result(**self.finalizer_context()), release=True)

    def test_authorized_requires_permit_even_if_log_states_match(self):
        context = self.finalizer_context()
        record = replace(context["log_record"], permit_or_deny_state=api.PermitState.DENY)
        context.update(
            log_record=record, permit_or_deny_state=api.PermitState.DENY,
            acknowledgement=api.LogAppendAcknowledgement(
                True, record.record_id, api.StructuredAuditLog((record,))),
        )
        self.assertIsNone(c._finalize_logged_action_result(**context))

    def test_permit_requires_completed(self):
        context = self.finalizer_context()
        context["completion_state"] = api.CompletionState.NOT_COMPLETED
        self.assertIsNone(c._finalize_logged_action_result(**context))

    def test_permit_requires_valid(self):
        context = self.finalizer_context()
        context["validation_state"] = api.ValidationState.BLOCKED
        self.assertIsNone(c._finalize_logged_action_result(**context))

    def test_guarded_helpers_are_not_package_exports(self):
        self.assertNotIn("_finalize_logged_action_result", api.__all__)
        self.assertNotIn("_new_guarded_harness_decision", api.__all__)


class ManifestBindingTests(RuntimeCase):
    def test_exact_input_and_output_digest_bindings(self):
        self.assertEqual(api.input_manifest_identity(self.ctx.input),
                         self.ctx.policy.expected_input_manifest_identity)
        self.assertEqual(api.output_manifest_identity(self.ctx.output),
                         self.ctx.policy.expected_output_manifest_identity)
        with self.root_patch():
            self.assert_permitted(self.ctx.read())
            self.assert_permitted(self.ctx.release(), release=True)

    def test_wrong_policy_input_digest_denies_after_root_matches_policy(self):
        policy = replace(self.ctx.policy, expected_input_manifest_identity="sha256:" + "0" * 64)
        with self.root_patch(self.ctx.root_for(policy)):
            self.assert_denied(self.ctx.read(policy=policy), api.StopReason.INPUT_MANIFEST_MISMATCH)

    def test_wrong_policy_output_digest_denies_after_root_matches_policy(self):
        policy = replace(self.ctx.policy, expected_output_manifest_identity="sha256:" + "0" * 64)
        with self.root_patch(self.ctx.root_for(policy)):
            self.assert_denied(self.ctx.release(policy=policy), api.StopReason.OUTPUT_MANIFEST_MISMATCH)

    def test_canonical_order_does_not_change_set_like_input_binding(self):
        manifest = replace(self.ctx.input,
                           exact_permitted_fields=tuple(reversed(self.ctx.input.exact_permitted_fields)))
        self.assertEqual(api.input_manifest_identity(manifest),
                         api.input_manifest_identity(self.ctx.input))
        with self.root_patch():
            self.assert_permitted(self.ctx.read(manifest=manifest))

    def test_duplicate_input_field_is_not_silently_deduplicated(self):
        manifest = replace(self.ctx.input, exact_permitted_fields=self.ctx.input.exact_permitted_fields * 2)
        self.assertNotEqual(api.input_manifest_identity(manifest),
                            api.input_manifest_identity(self.ctx.input))
        with self.root_patch():
            self.assert_denied(self.ctx.read(manifest=manifest),
                               api.StopReason.INPUT_MANIFEST_MISMATCH)


class DisclosureTests(RuntimeCase):
    def test_exact_disclosure_tuple_required(self):
        for key, value in (
            ("output_id", "TEST_ONLY_OTHER_OUTPUT"),
            ("recipient_actor_id", "TEST_ONLY_OTHER_RECIPIENT"),
            ("recipient_role", api.Role.EXECUTOR),
        ):
            record = replace(self.ctx.ledger.records[0], **{key: value})
            ledger = api.CumulativeDisclosureLedger((record,))
            self.assertIs(ledger.evaluate(), api.CumulativeDisclosureState.CLEAR)
            self.assertIs(ledger.evaluate_for(self.ctx.output.output_id,
                                             self.ctx.recipient.actor_id,
                                             self.ctx.recipient.declared_role),
                          api.CumulativeDisclosureState.UNRESOLVED)
            with self.root_patch():
                self.assert_denied(self.ctx.release(ledger=ledger),
                                   api.StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY)

    def test_empty_disclosure_ledger_is_unresolved_and_denies_release(self):
        ledger = api.CumulativeDisclosureLedger(())
        self.assertIs(ledger.evaluate(), api.CumulativeDisclosureState.UNRESOLVED)
        self.assertIs(ledger.evaluate_for(self.ctx.output.output_id, self.ctx.recipient.actor_id,
                                         self.ctx.recipient.declared_role),
                      api.CumulativeDisclosureState.UNRESOLVED)
        with self.root_patch():
            self.assert_denied(self.ctx.release(ledger=ledger),
                               api.StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY)

    def test_blocked_has_global_precedence_over_clear_and_unresolved(self):
        blocked = replace(self.ctx.ledger.records[0], disclosure_id="TEST_ONLY_BLOCKED",
                          output_id="TEST_ONLY_OTHER_OUTPUT",
                          cumulative_safety=api.CumulativeDisclosureState.BLOCKED)
        unresolved = replace(self.ctx.ledger.records[0], disclosure_id="TEST_ONLY_UNRESOLVED",
                             cumulative_safety=api.CumulativeDisclosureState.UNRESOLVED)
        ledger = api.CumulativeDisclosureLedger((self.ctx.ledger.records[0], unresolved, blocked))
        self.assertIs(ledger.evaluate(), api.CumulativeDisclosureState.BLOCKED)
        self.assertIs(ledger.evaluate_for(self.ctx.output.output_id, self.ctx.recipient.actor_id,
                                         self.ctx.recipient.declared_role),
                      api.CumulativeDisclosureState.BLOCKED)
        with self.root_patch():
            self.assert_denied(self.ctx.release(ledger=ledger),
                               api.StopReason.CUMULATIVE_DISCLOSURE_AMBIGUITY)

    def test_global_blocked_precedes_ambiguous_requested_recipient(self):
        record = replace(self.ctx.ledger.records[0],
                         cumulative_safety=api.CumulativeDisclosureState.BLOCKED)
        ledger = api.CumulativeDisclosureLedger((record,))
        self.assertIs(ledger.evaluate(), api.CumulativeDisclosureState.BLOCKED)
        self.assertIs(ledger.evaluate_for(self.ctx.output.output_id, "UNRESOLVED",
                                         self.ctx.recipient.declared_role),
                      api.CumulativeDisclosureState.BLOCKED)


class ResourceTests(RuntimeCase):
    def test_within_authority_exact_enum_value(self):
        self.assertEqual(api.ResourceBoundaryState.WITHIN_AUTHORITY.value, "WITHIN_AUTHORITY")
        with self.root_patch():
            self.assertIs(self.ctx.harness().validate_resource_boundary(
                api.ResourceBoundaryState.WITHIN_AUTHORITY).state, api.ValidationState.VALID)

    def test_unresolved_resource_fails_closed(self):
        with self.root_patch():
            result = self.ctx.harness().validate_resource_boundary(api.ResourceBoundaryState.UNRESOLVED)
        self.assertIsNot(result.state, api.ValidationState.VALID)
        self.assertIs(result.stop_reason, api.StopReason.RESOURCE_BOUNDARY_UNRESOLVED)

    def test_exceeded_resource_fails_closed(self):
        with self.root_patch():
            result = self.ctx.harness().validate_resource_boundary(api.ResourceBoundaryState.EXCEEDED)
        self.assertIsNot(result.state, api.ValidationState.VALID)
        self.assertIs(result.stop_reason, api.StopReason.RESOURCE_BOUNDARY_UNRESOLVED)


def add_case(cls, name, implementation):
    """Finite named cases are individually collected by standard unittest."""
    implementation.__name__ = "test_" + name
    setattr(cls, implementation.__name__, implementation)


ROOT_MUTATIONS = (
    ("policy_digest", "expected_policy_identity", "sha256:" + "0" * 64),
    ("construction_authority", "expected_construction_authority_sha", "3" * 40),
    ("harness_identity", "expected_harness_identity", "TEST_ONLY_OTHER_HARNESS"),
    ("harness_version", "expected_harness_version_or_commit_identity", "TEST_ONLY_OTHER_VERSION"),
    ("missing_authority", "execution_policy_authority_sha", "UNRESOLVED"),
    ("invalid_authority", "execution_policy_authority_sha", "TEST_ONLY_NOT_SHA"),
)
for name, field, value in ROOT_MUTATIONS:
    def run(self, field=field, value=value):
        with self.root_patch(replace(self.ctx.root, **{field: value})):
            self.assert_denied(self.ctx.read())
    add_case(TrustedRootTests, "root_mismatch_" + name, run)

PROVENANCE_MUTATIONS = (
    ("fixture_id", dict(fixture_id="TEST_ONLY_WRONG_METADATA_ID")),
    ("generator_id", dict(generator_identity="TEST_ONLY_WRONG_GENERATOR")),
    ("generator_version", dict(generator_version="TEST_ONLY_WRONG_GENERATOR_VERSION")),
    ("missing_lineage", dict(lineage_references=())),
    ("duplicate_lineage", dict(lineage_references=("TEST_ONLY_DOCUMENT_A", "TEST_ONLY_DOCUMENT_A"))),
    ("wrong_lineage", dict(lineage_references=("TEST_ONLY_OTHER_DOCUMENT",))),
    ("ambiguous_lineage", dict(lineage_references=("UNKNOWN",))),
    ("missing_required_keys", dict(reproducibility_metadata=(("test_spec_revision", "TEST_ONLY_V1"),))),
    ("empty_metadata", dict(reproducibility_metadata=())),
    ("unexpected_keys", dict(reproducibility_metadata=(
        ("test_spec_revision", "TEST_ONLY_V1"), ("construction_kind", "TEST_ONLY_STRUCTURAL"),
        ("TEST_ONLY_UNEXPECTED_KEY", "TEST_ONLY_VALUE")))),
    ("duplicate_metadata_keys", dict(reproducibility_metadata=(
        ("test_spec_revision", "TEST_ONLY_V1"), ("test_spec_revision", "TEST_ONLY_V1"),
        ("construction_kind", "TEST_ONLY_STRUCTURAL")))),
    ("wrong_classes", dict(construction_input_classes=(api.InputClassification.DOCUMENTATION_ONLY,))),
    ("empty_classes", dict(construction_input_classes=())),
    ("duplicate_classes", dict(construction_input_classes=(
        api.InputClassification.DOCUMENTATION_ONLY, api.InputClassification.DOCUMENTATION_ONLY))),
    ("prohibited_class", dict(construction_input_classes=(api.InputClassification.PROHIBITED,))),
    ("unknown_class", dict(construction_input_classes=(api.InputClassification.UNKNOWN,))),
    ("unknown_contamination", dict(contamination_state=api.ContaminationState.UNKNOWN)),
    ("contaminated", dict(contamination_state=api.ContaminationState.CONTAMINATED)),
    ("unresolved_admissibility", dict(admissibility_state=api.AdmissibilityState.UNRESOLVED)),
    ("blocked_admissibility", dict(admissibility_state=api.AdmissibilityState.BLOCKED)),
    ("wrong_digest_by_changed_metadata_value", dict(reproducibility_metadata=(
        ("test_spec_revision", "TEST_ONLY_V2"), ("construction_kind", "TEST_ONLY_STRUCTURAL")))),
)
for name, changes in PROVENANCE_MUTATIONS:
    def run(self, changes=changes):
        provenance = replace(self.ctx.provenance, **changes)
        with self.root_patch():
            self.assert_denied(self.ctx.admit(provenance=provenance))
    add_case(ProvenanceTests, "reject_" + name, run)

for token in ("", " ", "UNKNOWN", "UNRESOLVED", "AMBIGUOUS", "NOT_ATTESTED", "NONE"):
    def run(self, token=token):
        with self.root_patch():
            self.assert_denied(self.ctx.release(recipient=replace(self.ctx.recipient, actor_id=token)),
                               api.StopReason.UNAUTHORIZED_RECIPIENT)
    add_case(RecipientTests, "ambiguous_actor_" + (token.strip() or "empty_" + str(len(token))), run)

AUTHORIZATION_MUTATIONS = (
    ("actor", dict(actor_id="TEST_ONLY_OTHER_AUTH_ACTOR")),
    ("role", dict(declared_role=api.Role.CUSTODY_ADMIN)),
    ("action", dict(action=api.Action.RECORD_LOG)),
    ("authority", dict(authority_sha="3" * 40)),
    ("denied_state", dict(state=api.AuthorizationState.DENIED)),
    ("unresolved_state", dict(state=api.AuthorizationState.UNRESOLVED)),
    ("ambiguous_id", dict(authorization_id="UNKNOWN")),
)
for name, changes in AUTHORIZATION_MUTATIONS:
    def read_run(self, changes=changes):
        with self.root_patch():
            self.assert_denied(self.ctx.read(authorization=replace(self.ctx.read_auth, **changes)))
    add_case(ManifestBindingTests, "reader_authorization_mismatch_" + name, read_run)
    def release_run(self, changes=changes):
        with self.root_patch():
            self.assert_denied(self.ctx.release(authorization=replace(self.ctx.release_auth, **changes)))
    add_case(ReleaseApprovalTests, "release_authorization_mismatch_" + name, release_run)

for name, actor in (
    ("actor_mismatch", api.RoleDeclaration("TEST_ONLY_OTHER_READER", api.Role.EXECUTOR)),
    ("role_mismatch", api.RoleDeclaration("TEST_ONLY_READER", api.Role.CUSTODY_ADMIN)),
):
    def run(self, actor=actor):
        with self.root_patch():
            self.assert_denied(self.ctx.read(actor=actor), api.StopReason.UNAUTHORIZED_READER)
    add_case(ManifestBindingTests, name, run)

for token in ("", " ", "UNKNOWN", "UNRESOLVED"):
    def run(self, token=token):
        with self.root_patch():
            result = self.ctx.read(log_id=token)
        self.assert_denied(result, api.StopReason.LOGGING_REQUIRED)
        self.assertIs(result.decision.completion_state, api.CompletionState.NOT_COMPLETED)
        self.assertFalse(result.log_acknowledged)
    add_case(LoggingTests, "missing_or_ambiguous_log_id_" + (token.strip() or str(len(token))), run)

FINALIZER_MUTATIONS = (
    ("construction_authority", "expected_construction_authority_identity", "3" * 40),
    ("execution_authority", "expected_execution_policy_authority_identity", "3" * 40),
    ("actor_id", "expected_actor", api.RoleDeclaration("TEST_ONLY_OTHER_APPROVER", api.Role.RELEASE_APPROVER)),
    ("actor_role", "expected_actor", api.RoleDeclaration("TEST_ONLY_APPROVER", api.Role.EXECUTOR)),
    ("action", "expected_action", api.Action.READ_INPUT),
    ("target_kind", "expected_target_kind", api.TargetKind.INPUT_MANIFEST),
    ("target_id", "expected_target_id", "TEST_ONLY_OTHER_TARGET"),
    ("manifest_identity", "expected_manifest_identity", "sha256:" + "0" * 64),
    ("incident", "expected_incident_identifier", "TEST_ONLY_OTHER_INCIDENT"),
    ("cumulative_context", "expected_cumulative_disclosure_state", api.CumulativeDisclosureState.UNRESOLVED),
    ("recipient_id", "expected_recipient", api.RoleDeclaration("TEST_ONLY_OTHER_RECIPIENT", api.Role.RESEARCH_VIEWER)),
    ("recipient_role", "expected_recipient", api.RoleDeclaration("TEST_ONLY_RECIPIENT", api.Role.EXECUTOR)),
    ("permit_state", "permit_or_deny_state", api.PermitState.DENY),
    ("release_state", "release_state", api.ReleaseState.BLOCKED),
    ("quarantine_state", "quarantine_state", api.QuarantineState.QUARANTINED),
)
for name, field, value in FINALIZER_MUTATIONS:
    def run(self, field=field, value=value):
        context = self.finalizer_context()
        context[field] = value
        self.assertIsNone(c._finalize_logged_action_result(**context))
    add_case(LoggingTests, "finalizer_context_mismatch_" + name, run)

for name, changes in (
    ("id", dict(authorization_id="TEST_ONLY_OTHER_AUTH_ID")),
    ("authority", dict(authority_sha="3" * 40)),
):
    def run(self, changes=changes):
        context = self.finalizer_context()
        context["expected_authorization"] = replace(context["expected_authorization"], **changes)
        self.assertIsNone(c._finalize_logged_action_result(**context))
    add_case(LoggingTests, "finalizer_authorization_context_mismatch_" + name, run)

INPUT_MUTATIONS = (
    ("input_id", "TEST_ONLY_OTHER_INPUT"),
    ("manifest_version_identity", "TEST_ONLY_OTHER_MANIFEST"),
    ("input_classification", api.InputClassification.NON_ECONOMIC_SYNTHETIC),
    ("source_provenance_class", "TEST_ONLY_OTHER_DOCUMENTATION"),
    ("exact_permitted_fields", ("TEST_ONLY_OTHER_FIELD",)),
    ("exact_prohibited_fields", ("TEST_ONLY_OTHER_PROHIBITED_FIELD",)),
    ("permitted_reader_roles", (api.Role.CUSTODY_ADMIN,)),
    ("raw_values_visible", api.VisibilityState.VISIBLE),
    ("timestamps_visible", api.VisibilityState.VISIBLE),
    ("frequency_or_count_information_visible", api.VisibilityState.VISIBLE),
    ("longitudinal_observation_allowed", api.PermissionState.ALLOWED),
    ("aggregation_allowed", api.PermissionState.ALLOWED),
    ("cross_source_comparison_allowed", api.PermissionState.ALLOWED),
    ("efficacy_leakage_assessment", api.LeakageAssessment.UNRESOLVED),
    ("access_logging_requirement", api.RequirementState.NOT_REQUIRED),
    ("quarantine_on_ambiguity", api.RequirementState.NOT_REQUIRED),
    ("owner_approval_required", api.RequirementState.NOT_REQUIRED),
)
OUTPUT_MUTATIONS = (
    ("output_id", "TEST_ONLY_OTHER_OUTPUT"),
    ("manifest_version_identity", "TEST_ONLY_OTHER_MANIFEST"),
    ("output_type", "TEST_ONLY_OTHER_OUTPUT_TYPE"),
    ("exact_metric_or_artifact", "TEST_ONLY_OTHER_ARTIFACT"),
    ("granularity", "TEST_ONLY_OTHER_GRANULARITY"),
    ("permitted_recipients", (api.Role.EXECUTOR,)),
    ("exportability", api.PermissionState.DENIED),
    ("quarantine_status", api.QuarantineState.QUARANTINED),
    ("cumulative_disclosure_risk", api.CumulativeDisclosureState.UNRESOLVED),
    ("efficacy_leakage_assessment", api.LeakageAssessment.UNRESOLVED),
    ("release_approval_requirement", api.RequirementState.NOT_REQUIRED),
    ("retention_rule", "TEST_ONLY_OTHER_RETENTION"),
    ("incident_if_unexpected_information_revealed", "TEST_ONLY_OTHER_STOP"),
)
for kind, mutations in (("input", INPUT_MUTATIONS), ("output", OUTPUT_MUTATIONS)):
    for field, value in mutations:
        def run(self, kind=kind, field=field, value=value):
            base = self.ctx.input if kind == "input" else self.ctx.output
            manifest = replace(base, **{field: value})
            identity = api.input_manifest_identity if kind == "input" else api.output_manifest_identity
            self.assertNotEqual(identity(manifest), identity(base))
            with self.root_patch():
                result = self.ctx.read(manifest=manifest) if kind == "input" else self.ctx.release(manifest=manifest)
                self.assert_denied(result)
        add_case(ManifestBindingTests, kind + "_all_field_binding_" + field, run)

# Guard the completeness of the explicit tampering matrices without creating tests
# that merely repeat production validation: every material field gets an attack.
assert {name for name, _ in INPUT_MUTATIONS} == {field.name for field in fields(api.InputManifest)}
assert {name for name, _ in OUTPUT_MUTATIONS} == {field.name for field in fields(api.OutputManifest)}
