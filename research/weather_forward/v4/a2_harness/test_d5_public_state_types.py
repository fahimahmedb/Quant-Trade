"""Deterministic D5 type regressions; structural metadata only, no fixtures."""
from dataclasses import replace
from types import SimpleNamespace
import unittest
from . import contract as c
from . import test_bounded_runtime as baseline

def denial_kwargs():
    return dict(validation_state=c.ValidationState.INVALID,
                permit_or_deny_state=c.PermitState.DENY,
                quarantine_state=c.QuarantineState.QUARANTINED,
                release_state=c.ReleaseState.BLOCKED,
                completion_state=c.CompletionState.NOT_COMPLETED,
                stop_reason=c.StopReason.INVALID_DECLARATION,
                detail_code="TEST_ONLY_D5_DENIAL")

STATE_TYPES = {
    "validation_state": c.ValidationState,
    "permit_or_deny_state": c.PermitState,
    "quarantine_state": c.QuarantineState,
    "release_state": c.ReleaseState,
    "completion_state": c.CompletionState,
    "stop_reason": c.StopReason,
}

class PublicStateTests(unittest.TestCase):
    def test_astra_exact_string_counterexample(self):
        kw = denial_kwargs()
        kw.update(permit_or_deny_state="PERMIT", release_state="AUTHORIZED")
        with self.assertRaises(TypeError):
            c.HarnessDecision(**kw)

    def test_valid_denial_and_error_semantics(self):
        for validation in c.ValidationState:
            for quarantine in c.QuarantineState:
                for completion in c.CompletionState:
                    kw = denial_kwargs()
                    kw.update(validation_state=validation, quarantine_state=quarantine,
                              completion_state=completion, stop_reason=None)
                    decision = c.HarnessDecision(**kw)
                    result = c.LoggedActionResult(decision, c.StructuredAuditLog(()), None, False)
                    self.assertIs(result.decision, decision)
                    self.assertIs(result.log_acknowledged, False)

    def test_duck_typed_decision(self):
        decision = SimpleNamespace(**denial_kwargs())
        with self.assertRaises(TypeError):
            c.LoggedActionResult(decision, c.StructuredAuditLog(()), None, False)

    def test_wrong_log_type(self):
        with self.assertRaises(TypeError):
            c.LoggedActionResult(c.HarnessDecision(**denial_kwargs()), None, None, False)

    def test_replace_valid_denial(self):
        decision = replace(c.HarnessDecision(**denial_kwargs()), detail_code="TEST_ONLY_REPLACED")
        result = c.LoggedActionResult(decision, c.StructuredAuditLog(()), None, False)
        self.assertIs(replace(result, log=c.StructuredAuditLog(())).log_acknowledged, False)

    def test_private_helper_valid_typed_denial(self):
        decision = c._new_guarded_harness_decision(**denial_kwargs())
        self.assertIs(decision.permit_or_deny_state, c.PermitState.DENY)

def install_state_tests():
    for field, enum in STATE_TYPES.items():
        valid = denial_kwargs()[field]
        invalids = [("value_string", valid.value), ("wrong_enum", c.Action.RELEASE_OUTPUT),
                    ("integer", 0), ("plain_object", object())]
        if field != "stop_reason":
            invalids.append(("none", None))
        for label, value in invalids:
            def direct(self, field=field, value=value):
                kw = denial_kwargs()
                kw[field] = value
                with self.assertRaises(TypeError):
                    c.HarnessDecision(**kw)
            def replacement(self, field=field, value=value):
                original = c.HarnessDecision(**denial_kwargs())
                with self.assertRaises(TypeError):
                    replace(original, **{field: value})
            def guarded(self, field=field, value=value):
                kw = denial_kwargs()
                kw[field] = value
                with self.assertRaises(TypeError):
                    c._new_guarded_harness_decision(**kw)
            for name, method in (("direct", direct), ("replace", replacement),
                                 ("helper", guarded)):
                setattr(PublicStateTests, f"test_{name}_{field}_{label}", method)
    for label, value in [("zero", 0), ("one", 1), ("none", None),
                         ("empty_string", ""), ("false_string", "False"), ("empty_list", [])]:
        def acknowledgement(self, value=value):
            with self.assertRaises((TypeError, ValueError)):
                c.LoggedActionResult(c.HarnessDecision(**denial_kwargs()),
                                     c.StructuredAuditLog(()), None, value)
        def replacement(self, value=value):
            original = c.LoggedActionResult(c.HarnessDecision(**denial_kwargs()),
                                            c.StructuredAuditLog(()), None, False)
            with self.assertRaises((TypeError, ValueError)):
                replace(original, log_acknowledged=value)
        setattr(PublicStateTests, "test_ack_type_" + label, acknowledgement)
        setattr(PublicStateTests, "test_replace_ack_type_" + label, replacement)

install_state_tests()

class FinalizerTypeTests(baseline.RuntimeCase):
    def context(self):
        # Reuse the original guarded setup, not its tests or assertions.
        return baseline.LoggingTests.finalizer_context(self)

    def test_exact_acknowledged_linkage(self):
        kw = self.context()
        result = c._finalize_logged_action_result(**kw)
        self.assert_permitted(result, release=c.ReleaseState.AUTHORIZED)

    def test_same_id_different_record_rejected(self):
        kw = self.context()
        kw["log_record"] = replace(kw["log_record"], manifest_identity="TEST_ONLY_MISMATCH")
        self.assertIsNone(c._finalize_logged_action_result(**kw))

    def test_replace_guarded_result_rejected(self):
        result = c._finalize_logged_action_result(**self.context())
        with self.assertRaises(ValueError):
            replace(result)

    def test_finalizer_duck_ack_rejected(self):
        kw = self.context()
        ack = kw["acknowledgement"]
        kw["acknowledgement"] = SimpleNamespace(appended=True, record_id=ack.record_id, log=ack.log)
        self.assertIsNone(c._finalize_logged_action_result(**kw))

def install_finalizer_tests():
    for field, enum in STATE_TYPES.items():
        for label, value in [("value_string", denial_kwargs()[field].value),
                             ("wrong_enum", c.Action.RELEASE_OUTPUT), ("integer", 0),
                             ("none", None)]:
            if field == "stop_reason" and value is None:
                continue
            def check(self, field=field, value=value):
                kw = self.context()
                # Correct acknowledged denial context so invalid validation/completion
                # cannot be rejected merely by the permissive VALID/COMPLETED gate.
                kw.update(permit_or_deny_state=c.PermitState.DENY,
                          release_state=c.ReleaseState.BLOCKED,
                          completion_state=c.CompletionState.NOT_COMPLETED,
                          validation_state=c.ValidationState.INVALID)
                record = replace(kw["log_record"], permit_or_deny_state=c.PermitState.DENY,
                                 release_state=c.ReleaseState.BLOCKED)
                kw[field] = value
                if field in ("permit_or_deny_state", "release_state", "quarantine_state"):
                    record = replace(record, **{field: value})
                kw["log_record"] = record
                kw["acknowledgement"] = c.LogAppendAcknowledgement(
                    True, record.record_id, c.StructuredAuditLog((record,)))
                self.assertIsNone(c._finalize_logged_action_result(**kw))
            setattr(FinalizerTypeTests, f"test_finalizer_{field}_{label}", check)
    for label, value in [("one", 1), ("true_string", "True")]:
        def check(self, value=value):
            kw = self.context()
            kw["acknowledgement"] = replace(kw["acknowledgement"], appended=value)
            self.assertIsNone(c._finalize_logged_action_result(**kw))
        setattr(FinalizerTypeTests, "test_finalizer_ack_" + label, check)

install_finalizer_tests()
