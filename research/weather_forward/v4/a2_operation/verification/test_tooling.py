"""L2-B adversarial synthetic tests. No host probes, real contexts or file writes.

MemoryOS substitutes only the explicitly injectable writer filesystem. Patches
of results/harness calls target TEST_ONLY sequence checks, never proof that a
production barrier was reached. Late barriers use the unchanged H implementation
with a synthetic root and a freshly bound synthetic policy.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import fields, replace
from enum import Enum
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from research.weather_forward.v4 import a2_harness as api
from research.weather_forward.v4.a2_harness import harness as h
from research.weather_forward.v4.a2_harness.test_bounded_runtime import TestContext
from research.weather_forward.v4.a2_operation.common import bounded_output as writer
from research.weather_forward.v4.a2_operation.identity import identity_stdlib as independent
from research.weather_forward.v4.a2_operation.identity import identity_via_harness as via_h
from research.weather_forward.v4.a2_operation.operation import a2_doc_integration_operation as op
from research.weather_forward.v4.a2_operation.qualification import summarize_qualification as qual
from research.weather_forward.v4.a2_operation.verification.audit_boundary import decide


def transport(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [transport(x) for x in value]
    return value


def frozen(obj):
    return {"schema": "A2_FROZEN_CONTENT_V1", "kind": type(obj).__name__,
            "fields": {f.name: transport(getattr(obj, f.name)) for f in fields(obj)}}


def synthetic_context(branch="D1"):
    ctx = TestContext()
    policy = replace(ctx.policy, fixture_provenance_contract=None)
    def actor(obj):
        return {"actor_id": obj.actor_id, "role": obj.declared_role.value}
    def authorization(obj):
        return {f.name: transport(getattr(obj, f.name)) for f in fields(obj)}
    document = {
        "schema": op.CONTEXT_SCHEMA, "branch": branch,
        "output_directory": "/srv/a2out", "result_file_name": "TEST_ONLY-result.json",
        "harness_source_blobs": {name: "9" * 40 for name in op.HARNESS_PRODUCTION_FILES},
        "authority_binding": {f.name: getattr(ctx.binding, f.name) for f in fields(ctx.binding)},
        "input_manifest": frozen(ctx.input), "output_manifest": frozen(ctx.output),
        "policy": frozen(policy), "execution_authority_sha": "2" * 40,
        "executor": actor(ctx.reader), "recipient": actor(ctx.recipient), "approver": actor(ctx.approver),
        "read_authorization": authorization(ctx.read_auth),
        "release": None if branch == "D2" else {
            "authorization": authorization(ctx.release_auth),
            # Synthetic dependency placeholder only; never an attributable Astra approval.
            "approval_artifact": {"repository": "TEST_ONLY_NO_REPOSITORY",
                "path": "TEST_ONLY_APPROVAL_NOT_A_REAL_ARTIFACT", "commit": "3"*40, "blob": "4"*40},
            "ledger": [{f.name: transport(getattr(ctx.ledger.records[0], f.name))
                        for f in fields(ctx.ledger.records[0])}],
        },
        "log": {"input_record_id": "TEST_ONLY_INPUT_RECORD",
                "output_record_id": "TEST_ONLY_OUTPUT_RECORD" if branch == "D1" else None,
                "incident_identifier": None},
        "accepted_detail_codes": [op.INPUT_SUCCESS_CODE, op.OUTPUT_SUCCESS_CODE],
    }
    return ctx, policy, document


class MemoryOS:
    """Only the bounded writer's synthetic filesystem dependency."""
    path = os.path
    O_WRONLY, O_CREAT, O_EXCL, O_NOFOLLOW = os.O_WRONLY, os.O_CREAT, os.O_EXCL, os.O_NOFOLLOW
    def __init__(self, *, chunk=None, fail_after=None, zero_write=False):
        self.files = {}
        self.opened = []
        self.chunk, self.fail_after, self.zero_write = chunk, fail_after, zero_write
        self.path = SimpleNamespace(join=os.path.join, lexists=lambda p: p in self.files)
        self.closed = []
    def open(self, path, flags, mode):
        if path in self.files:
            raise FileExistsError(path)
        self.files[path] = bytearray()
        self.opened.append((path, flags, mode))
        return path
    def write(self, fd, payload):
        if self.fail_after is not None and len(self.files[fd]) >= self.fail_after:
            raise OSError("TEST_ONLY_INTERRUPTION")
        if self.zero_write:
            return 0
        n = len(payload) if self.chunk is None else min(self.chunk, len(payload))
        self.files[fd].extend(payload[:n])
        return n
    def fsync(self, fd):
        pass
    def close(self, fd):
        self.closed.append(fd)
    def unlink(self, path):
        del self.files[path]
    def link(self, src, dst):
        if dst in self.files:
            raise FileExistsError(dst)
        self.files[dst] = self.files[src]


class WriterTests(unittest.TestCase):
    def test_exact_limit_short_writes_and_atomic_final_name(self):
        fs = MemoryOS(chunk=7)
        payload = b"x" * 65536
        self.assertEqual(writer.write_bounded("/TEST_ONLY", "result.json", payload, _os=fs), 65536)
        self.assertEqual(bytes(fs.files["/TEST_ONLY/result.json"]), payload)
        self.assertNotIn("/TEST_ONLY/.partial-result.json", fs.files)
        self.assertEqual(fs.opened[0][2], 0o600)
        self.assertTrue(fs.opened[0][1] & os.O_EXCL)
    def test_oversize_refused_before_filesystem(self):
        fs = MemoryOS()
        with self.assertRaises(writer.OutputLimitExceeded):
            writer.write_bounded("/TEST_ONLY", "result.json", b"x"*65537, _os=fs)
        self.assertEqual(fs.opened, [])
    def test_no_bound_override(self):
        for bound in (True, -1, 65537, 1.5):
            with self.subTest(bound=bound), self.assertRaises(ValueError):
                writer.write_bounded("/TEST_ONLY", "result.json", b"", max_bytes=bound, _os=MemoryOS())
    def test_invalid_names_never_touch_filesystem(self):
        for name in ("../x", "/x", "a/b", "", ".partial-x", "x\n", "x\r", "x"*129, "é", None):
            fs = MemoryOS()
            with self.subTest(name=name), self.assertRaises(writer.InvalidOutputName):
                writer.write_bounded("/TEST_ONLY", name, b"{}", _os=fs)
            self.assertEqual(fs.opened, [])
    def test_existing_final_not_overwritten(self):
        fs = MemoryOS()
        fs.files["/TEST_ONLY/result.json"] = b"original"
        with self.assertRaises(writer.OutputTargetExists):
            writer.write_bounded("/TEST_ONLY", "result.json", b"replacement", _os=fs)
        self.assertEqual(fs.files["/TEST_ONLY/result.json"], b"original")
    def test_interruption_removes_partial_without_final(self):
        fs = MemoryOS(chunk=3, fail_after=3)
        with self.assertRaises(OSError):
            writer.write_bounded("/TEST_ONLY", "result.json", b"123456", _os=fs)
        self.assertEqual(fs.files, {})
        self.assertEqual(len(fs.closed), 1)
    def test_zero_write_stops_and_cleans_up(self):
        fs = MemoryOS(zero_write=True)
        with self.assertRaisesRegex(OSError, "SHORT_WRITE"):
            writer.write_bounded("/TEST_ONLY", "result.json", b"123", _os=fs)
        self.assertEqual(fs.files, {})
    def test_final_race_never_replaces_existing_target(self):
        fs = MemoryOS()
        def racing_link(src, dst):
            fs.files[dst] = b"TEST_ONLY_CONCURRENT_TARGET"
            raise FileExistsError(dst)
        fs.link = racing_link
        with self.assertRaises(FileExistsError):
            writer.write_bounded("/TEST_ONLY", "result.json", b"123", _os=fs)
        self.assertEqual(fs.files, {"/TEST_ONLY/result.json": b"TEST_ONLY_CONCURRENT_TARGET"})
    def test_payload_type_and_deterministic_encoding(self):
        with self.assertRaises(TypeError):
            writer.write_bounded("/TEST_ONLY", "result.json", bytearray(b"x"), _os=MemoryOS())
        self.assertEqual(writer.encode_result({"z": "é", "a": 1}), b'{"a":1,"z":"\\u00e9"}\n')


class IdentityTests(unittest.TestCase):
    def setUp(self):
        ctx = TestContext()
        self.docs = [frozen(ctx.input), frozen(ctx.output), frozen(replace(ctx.policy, fixture_provenance_contract=None))]
    def agree(self, doc):
        self.assertEqual(via_h.identity(api, doc), independent.identity(doc))
    def reject_both(self, doc):
        with self.assertRaises((ValueError, TypeError)):
            via_h.identity(api, doc)
        with self.assertRaises((ValueError, TypeError)):
            independent.identity(doc)
    def test_calibration_matches_published_digest(self):
        path = Path(independent.__file__).with_name("calibration_test_only_output_manifest.json")
        vector = json.loads(path.read_text(encoding="ascii"))
        expected = "sha256:54bfcafcca4d87b9771b905efe9fb12023fdce061fbccda155bcecb3a62253bf"
        self.assertEqual(vector["calibration_vector"]["expected_identity"], expected)
        self.assertEqual(vector["document"], self.docs[1])
        self.assertEqual(via_h.identity(api, vector["document"]), expected)
        self.assertEqual(independent.identity(vector["document"]), expected)
    def test_all_three_kinds_and_every_text_field(self):
        for doc in self.docs:
            self.agree(doc)
            baseline = independent.identity(doc)
            for name, value in doc["fields"].items():
                if type(value) is str and name not in {n for n, r in independent.SPECS[doc["kind"]][1] if r[0] == "enum"}:
                    changed = deepcopy(doc)
                    changed["fields"][name] = value + " é e\u0301  "
                    with self.subTest(kind=doc["kind"], field=name):
                        self.agree(changed)
                        self.assertNotEqual(independent.identity(changed), baseline)
    def test_list_order_is_ignored_duplicates_are_preserved(self):
        for doc in self.docs:
            baseline = independent.identity(doc)
            for name, value in doc["fields"].items():
                if type(value) is list and value:
                    changed = deepcopy(doc)
                    changed["fields"][name].reverse()
                    with self.subTest(kind=doc["kind"], field=name):
                        self.agree(changed)
                        self.assertEqual(independent.identity(changed), baseline)
                        changed["fields"][name].append(deepcopy(value[0]))
                        self.agree(changed)
                        self.assertNotEqual(independent.identity(changed), baseline)
    def test_unicode_and_whitespace_not_normalized(self):
        first, second = deepcopy(self.docs[1]), deepcopy(self.docs[1])
        first["fields"]["output_type"] = "é"
        second["fields"]["output_type"] = "e\u0301"
        self.agree(first)
        self.agree(second)
        self.assertNotEqual(independent.identity(first), independent.identity(second))
    def test_every_field_required_and_no_extra_fields(self):
        for doc in self.docs:
            for name in doc["fields"]:
                changed = deepcopy(doc)
                del changed["fields"][name]
                with self.subTest(kind=doc["kind"], field=name):
                    self.reject_both(changed)
            changed = deepcopy(doc)
            changed["fields"]["unexpected"] = "TEST_ONLY"
            self.reject_both(changed)
    def test_enum_values_and_container_types_strict(self):
        for doc in self.docs:
            for name, rule in independent.SPECS[doc["kind"]][1]:
                bad = ("UNKNOWN_ENUM_NOT_A_VALUE" if rule[0] == "enum" else
                       ["UNKNOWN_ENUM_NOT_A_VALUE"] if rule[0] == "enum_list" else
                       "not-a-list" if rule[0] in {"text_list", "pairs"} else
                       {} if rule[0] == "null" else 123)
                changed = deepcopy(doc)
                changed["fields"][name] = bad
                with self.subTest(kind=doc["kind"], field=name):
                    self.reject_both(changed)
    def test_all_known_enum_alternatives_agree(self):
        for doc in self.docs:
            for name, rule in independent.SPECS[doc["kind"]][1]:
                if rule[0] in {"enum", "enum_list"}:
                    for value in independent.ENUM_VALUES[rule[1]]:
                        changed = deepcopy(doc)
                        changed["fields"][name] = value if rule[0] == "enum" else [value]
                        with self.subTest(kind=doc["kind"], field=name, value=value):
                            self.agree(changed)
    def test_recipient_pairs_sorted_by_actor_then_role(self):
        doc = deepcopy(self.docs[2])
        doc["fields"]["permitted_recipient_actor_roles"] = [
            ["TEST_ONLY_Z", "EXECUTOR"], ["TEST_ONLY_A", "RESEARCH_VIEWER"], ["TEST_ONLY_A", "EXECUTOR"]]
        self.agree(doc)
        self.assertEqual(independent.canonical_payload(doc)["permitted_recipient_actor_roles"],
            [["TEST_ONLY_A", "EXECUTOR"], ["TEST_ONLY_A", "RESEARCH_VIEWER"], ["TEST_ONLY_Z", "EXECUTOR"]])
    def test_kind_schema_and_top_level_extra_rejected(self):
        for key, value in (("kind", "Unknown"), ("schema", "OTHER"), ("extra", "TEST_ONLY")):
            doc = deepcopy(self.docs[1])
            doc[key] = value
            self.reject_both(doc)
    def test_duplicate_json_keys_and_non_json_numbers_rejected_by_both_routes(self):
        for text in ('{"kind":"InputManifest","kind":"OutputManifest"}', '{"fields":{"x":NaN}}'):
            for load in (via_h.load_document, independent.load_document):
                with self.assertRaises(ValueError):
                    load(text)
    def test_independent_route_has_no_harness_import_or_helpers(self):
        import ast
        tree = ast.parse(Path(independent.__file__).read_text(encoding="utf-8"))
        imported = [a.name for node in ast.walk(tree) if isinstance(node, ast.Import) for a in node.names]
        imported += [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any("harness" in name or "research" in name or "identity_via" in name for name in imported))


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.ctx, self.policy, self.doc = synthetic_context()
        self.objects = op.build_objects(api, via_h.build_object, op.validate_context(self.doc))
        self.root = self.ctx.root_for(self.policy)
    def run_sequence(self, obj=None):
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.root):
            return op.execute(api, obj or self.objects)
    def first_result(self):
        doc = deepcopy(self.doc)
        doc["release"] = None
        objects = op.build_objects(api, via_h.build_object, op.validate_context(doc))
        return self.run_sequence(objects)[1][0]
    def test_positive_two_calls_exact_linkage_and_first_record_preserved(self):
        with patch.object(api.A2Harness, "evaluate_input_read", autospec=True, side_effect=api.A2Harness.evaluate_input_read) as read, \
             patch.object(api.A2Harness, "evaluate_output_release", autospec=True, side_effect=api.A2Harness.evaluate_output_release) as release:
            code, evaluations, linkage = self.run_sequence()
        self.assertEqual((read.call_count, release.call_count), (1, 1))
        self.assertEqual(code, 10)
        self.assertEqual(linkage, "INPUT_AND_RELEASE_LINKED")
        first, second = evaluations
        self.assertIs(first.decision.release_state, api.ReleaseState.BLOCKED)
        self.assertIs(second.decision.release_state, api.ReleaseState.AUTHORIZED)
        self.assertIs(release.call_args.args[1], first.log)
        self.assertEqual(second.log.records[:-1], first.log.records)
        self.assertNotEqual(first.log_record.record_id, second.log_record.record_id)
    def test_d2_and_d1_without_release_omit_second_call(self):
        for branch in ("D1", "D2"):
            _, _, doc = synthetic_context(branch)
            doc["release"] = None
            objects = op.build_objects(api, via_h.build_object, op.validate_context(doc))
            with patch.object(api.A2Harness, "evaluate_output_release", side_effect=AssertionError("SECOND_CALL_FORBIDDEN")):
                code, evaluations, linkage = self.run_sequence(objects)
            self.assertEqual(code, 0)
            self.assertEqual(len(evaluations), 1)
            self.assertIs(evaluations[0].decision.release_state, api.ReleaseState.BLOCKED)
    def test_missing_proof_constructs_no_authorized_release_object(self):
        doc = deepcopy(self.doc)
        doc["release"]["approval_artifact"] = None
        objects = op.build_objects(api, via_h.build_object, op.validate_context(doc))
        self.assertIsNone(objects.release_authorization)
        with patch.object(api.A2Harness, "evaluate_output_release", side_effect=AssertionError("NO_PROOF")):
            self.assertEqual(self.run_sequence(objects)[0], 0)
    def test_missing_grant_ledger_or_output_id_preserves_valid_input(self):
        for key in ("authorization", "ledger", "output_record_id"):
            doc = deepcopy(self.doc)
            if key == "output_record_id":
                doc["log"][key] = None
            else:
                doc["release"][key] = None
            objects = op.build_objects(api, via_h.build_object, op.validate_context(doc))
            with self.subTest(key=key), patch.object(api.A2Harness, "evaluate_output_release", side_effect=AssertionError("MISSING_PRECONDITION")):
                self.assertEqual(self.run_sequence(objects)[0], 0)
    def test_denied_release_authority_is_not_an_input_failure(self):
        self.objects.release_authorization = replace(self.objects.release_authorization, state=api.AuthorizationState.DENIED)
        self.assertEqual(self.run_sequence()[0], 0)
    def test_wrong_release_actor_or_authority_omits_second_call(self):
        for change in ({"actor_id": "TEST_ONLY_OTHER"}, {"authority_sha": "5"*40},
                       {"declared_role": api.Role.EXECUTOR}, {"action": api.Action.READ_INPUT}):
            original = self.objects.release_authorization
            self.objects.release_authorization = replace(original, **change)
            with self.subTest(change=change):
                self.assertEqual(self.run_sequence()[0], 0)
            self.objects.release_authorization = original
    def test_duplicate_log_ids_and_d2_release_section_rejected_before_calls(self):
        doc = deepcopy(self.doc)
        doc["log"]["output_record_id"] = doc["log"]["input_record_id"]
        with self.assertRaises(op.ContextError):
            op.validate_context(doc)
        doc = deepcopy(self.doc)
        doc["branch"] = "D2"
        with self.assertRaises(op.ContextError):
            op.validate_context(doc)
    def test_output_directory_and_newline_identity_names_rejected(self):
        for key, value in (("output_directory", "/tmp"), ("result_file_name", "x\n"),
                           ("execution_authority_sha", "2"*40+"\n")):
            doc = deepcopy(self.doc)
            doc[key] = value
            with self.subTest(key=key), self.assertRaises(op.ContextError):
                op.validate_context(doc)
    def test_source_pin_mismatch_stops_before_import_or_evaluation(self):
        with self.assertRaisesRegex(op.StopOperation, "HARNESS_SOURCE_BLOB_MISMATCH"):
            op.verify_harness_blobs(lambda name: b"TEST_ONLY_SOURCE", self.doc["harness_source_blobs"])
    def test_result_contains_exact_fifteen_elements_and_no_diagnostics(self):
        code, results, linkage = self.run_sequence()
        result = op.build_result(api, self.objects, results, linkage)
        self.assertEqual(set(result), set(op.RESULT_ELEMENTS))
        self.assertEqual(len(result), 15)
        self.assertEqual(result["release_state"], ["BLOCKED", "AUTHORIZED"])
        self.assertEqual(len(result["acknowledged_log_record_references"]), 2)
        self.assertLess(len(writer.encode_result(result)), 65536)
    def test_unaccepted_input_code_stops_before_second_call(self):
        self.objects.accepted_codes = frozenset({op.OUTPUT_SUCCESS_CODE})
        with patch.object(api.A2Harness, "evaluate_output_release", side_effect=AssertionError("UNEXPECTED_SECOND_CALL")), \
             self.assertRaisesRegex(op.StopOperation, "DETAIL_CODE_OUTSIDE_ACCEPTED_SCOPE"):
            self.run_sequence()
    def test_each_input_decision_component_and_acknowledgement_is_checked(self):
        changes = (("validation_state", api.ValidationState.BLOCKED), ("permit_or_deny_state", api.PermitState.DENY),
            ("quarantine_state", api.QuarantineState.QUARANTINED), ("release_state", api.ReleaseState.AUTHORIZED),
            ("completion_state", api.CompletionState.NOT_COMPLETED), ("stop_reason", api.StopReason.MISSING_AUTHORITY),
            ("detail_code", "TEST_ONLY_UNEXPECTED_CODE"))
        for field, value in changes:
            result = self.first_result()
            # Corrupt a TEST_ONLY returned object to exercise the sequence detector.
            object.__setattr__(result.decision, field, value)
            with self.subTest(field=field), self.assertRaises(op.StopOperation):
                op._check_decision(api, result, release_state=api.ReleaseState.BLOCKED, detail_code=op.INPUT_SUCCESS_CODE)
        for value in (False, 1):
            result = self.first_result()
            object.__setattr__(result, "log_acknowledged", value)
            with self.assertRaises(op.StopOperation):
                op._check_decision(api, result, release_state=api.ReleaseState.BLOCKED, detail_code=op.INPUT_SUCCESS_CODE)
    def test_lost_preceding_record_duplicate_or_wrong_context_stops(self):
        _, results, _ = self.run_sequence()
        first, second = results
        expected = second.log_record
        for records in ((expected,), first.log.records + (expected, expected),
                        first.log.records + (replace(expected, actor_id="TEST_ONLY_OTHER"),)):
            object.__setattr__(second, "log", api.StructuredAuditLog(records))
            with self.assertRaises(op.StopOperation):
                op._check_linkage(api, second, expected, first.log.records)
    def test_finish_codes_output_limit_existing_target_exception_and_silence(self):
        def output_module(action):
            return SimpleNamespace(encode_result=writer.encode_result, write_bounded=action,
                OutputLimitExceeded=writer.OutputLimitExceeded, OutputTargetExists=writer.OutputTargetExists,
                InvalidOutputName=writer.InvalidOutputName)
        def fail(error):
            def action(*args):
                raise error
            return action
        fs = MemoryOS()
        actions = ((lambda d,n,p: writer.write_bounded(d,n,p,_os=fs), 10),
                   (fail(writer.OutputLimitExceeded()), 50), (fail(writer.OutputTargetExists()), 30),
                   (fail(OSError("TEST_ONLY")), 40))
        for action, expected in actions:
            stdout, stderr = io.StringIO(), io.StringIO()
            with self.subTest(expected=expected), patch("sys.stdout", stdout), patch("sys.stderr", stderr), \
                 patch.object(h, "get_trusted_execution_policy_root", return_value=self.root):
                code = op.guarded(op.finish, api, self.objects, output_module(action), "/TEST_ONLY", "result.json")
            self.assertEqual(code, expected)
            self.assertEqual((stdout.getvalue(), stderr.getvalue()), ("", ""))
    def test_stop_or_exception_never_calls_writer_and_never_retries(self):
        for effect, expected in ((op.StopOperation("TEST_ONLY"), 30), (RuntimeError("TEST_ONLY"), 40)):
            module = SimpleNamespace(encode_result=writer.encode_result, write_bounded=lambda *a: self.fail("WRITE_FORBIDDEN"),
                OutputLimitExceeded=writer.OutputLimitExceeded, OutputTargetExists=writer.OutputTargetExists,
                InvalidOutputName=writer.InvalidOutputName)
            with patch.object(op, "execute", side_effect=effect) as execute:
                self.assertEqual(op.guarded(op.finish, api, self.objects, module, "/TEST_ONLY", "result.json"), expected)
                self.assertEqual(execute.call_count, 1)
    def test_unexpected_or_boolean_exit_is_stop(self):
        for code in (99, True, False, "0", None):
            self.assertEqual(op.guarded(lambda: code), 30)
    def test_unexpected_sequence_code_is_stop_before_write(self):
        first = self.first_result()
        module = SimpleNamespace(encode_result=writer.encode_result, write_bounded=lambda *a: self.fail("WRITE_FORBIDDEN"),
            OutputLimitExceeded=writer.OutputLimitExceeded, OutputTargetExists=writer.OutputTargetExists,
            InvalidOutputName=writer.InvalidOutputName)
        with patch.object(op, "execute", return_value=(99, [first], "INPUT_LINKED_RELEASE_NOT_ATTEMPTED")):
            self.assertEqual(op.finish(api, self.objects, module, "/TEST_ONLY", "result.json"), 30)
    def test_duplicate_context_fields_rejected_before_calls(self):
        with self.assertRaises(op.ContextError):
            op.decode_context('{"branch":"D1","branch":"D2"}')


class SyntheticBarrierTests(unittest.TestCase):
    """Actual H barriers, rebinding each single synthetic manifest change."""
    def setUp(self):
        self.ctx = TestContext()
        self.ctx.policy = replace(self.ctx.policy, fixture_provenance_contract=None)
    def test_output_quarantine_barrier_reached_after_valid_synthetic_authorization(self):
        manifest = replace(self.ctx.output, quarantine_status=api.QuarantineState.BLOCKED_PENDING_OWNER_REVIEW)
        policy = replace(self.ctx.policy, expected_output_manifest_identity=api.output_manifest_identity(manifest))
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(policy)):
            result = self.ctx.release(manifest=manifest, policy=policy)
        self.assertEqual(result.decision.detail_code, "OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE")
        self.assertIs(result.decision.release_state, api.ReleaseState.BLOCKED)
    def test_output_leakage_barrier_reached_with_quarantine_clear(self):
        manifest = replace(self.ctx.output, efficacy_leakage_assessment=api.LeakageAssessment.UNRESOLVED)
        policy = replace(self.ctx.policy, expected_output_manifest_identity=api.output_manifest_identity(manifest))
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(policy)):
            result = self.ctx.release(manifest=manifest, policy=policy)
        self.assertEqual(result.decision.detail_code, "OUTPUT_EFFICACY_LEAKAGE_NOT_CLEAR")
    def test_disclosure_manifest_barrier_reached_before_ledger(self):
        manifest = replace(self.ctx.output, cumulative_disclosure_risk=api.CumulativeDisclosureState.UNRESOLVED)
        policy = replace(self.ctx.policy, expected_output_manifest_identity=api.output_manifest_identity(manifest))
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(policy)):
            result = self.ctx.release(manifest=manifest, policy=policy)
        self.assertEqual(result.decision.detail_code, "OUTPUT_MANIFEST_CUMULATIVE_DISCLOSURE_NOT_CLEAR")
    def test_empty_ledger_barrier_reached_with_other_prerequisites_clear(self):
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(self.ctx.policy)):
            result = self.ctx.release(ledger=api.CumulativeDisclosureLedger(()))
        self.assertEqual(result.decision.detail_code, "DISCLOSURE_LEDGER_NOT_CLEAR_FOR_EXACT_OUTPUT_RECIPIENT_ACTOR_ROLE")
    def test_unacknowledged_append_is_not_permissive(self):
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(self.ctx.policy)), \
             patch.object(api.StructuredAuditLog, "append", return_value=api.LogAppendAcknowledgement(False, "TEST_ONLY_LOG_READ", api.StructuredAuditLog(()))):
            result = self.ctx.read()
        self.assertEqual(result.decision.detail_code, "REQUIRED_LOG_APPEND_NOT_ACKNOWLEDGED")
        self.assertIs(result.decision.permit_or_deny_state, api.PermitState.DENY)
    def test_mismatched_actor_denied_at_authorization_before_permission(self):
        with patch.object(h, "get_trusted_execution_policy_root", return_value=self.ctx.root_for(self.ctx.policy)):
            result = self.ctx.read(authorization=replace(self.ctx.read_auth, actor_id="TEST_ONLY_OTHER"))
        self.assertIs(result.decision.stop_reason, api.StopReason.UNAUTHORIZED_READER)
        self.assertIs(result.decision.permit_or_deny_state, api.PermitState.DENY)


class AuditTests(unittest.TestCase):
    def check(self, event, args):
        return decide(event, args, allowed_reads=frozenset({"/TEST_ONLY/code.py"}),
            expected_caches=frozenset({"/TEST_ONLY/__pycache__/code.cpython-310.pyc"}), stdlib_root="/TEST_STDLIB")
    def test_network_and_child_attempts_refused_without_os_operations(self):
        for event in ("socket.__new__", "socket.connect", "http.client.connect", "urllib.Request"):
            self.assertEqual(self.check(event, ()), "NETWORK")
        for event in ("subprocess.Popen", "os.fork", "os.system", "os.posix_spawn", "os.exec"):
            self.assertEqual(self.check(event, ()), "SUBPROCESS")
    def test_all_filesystem_mutation_events_refused(self):
        for event in ("os.remove", "os.mkdir", "os.link", "os.rename", "os.symlink", "os.truncate"):
            self.assertEqual(self.check(event, ("/TEST_ONLY/code.py",)), "FILE_MUTATION")
    def test_allowlisted_source_only_caches_and_file_descriptors_refused(self):
        self.assertEqual(self.check("open", ("/TEST_ONLY/code.py", "r", os.O_RDONLY)), "ALLOW")
        self.assertEqual(self.check("open", ("/TEST_ONLY/__pycache__/code.cpython-310.pyc", "r", 0)), "EXPECTED_CACHE_REFUSAL")
        self.assertEqual(self.check("open", ("/TEST_STDLIB/__pycache__/json.pyc", "r", 0)), "EXPECTED_CACHE_REFUSAL")
        self.assertEqual(self.check("open", (42, "r", 0)), "FD_OPEN")
        self.assertEqual(self.check("open", ("/TEST_ONLY/code.py", "w", os.O_TRUNC)), "FILE_WRITE")
    def test_path_traversal_and_third_party_reads_not_stdlib(self):
        for path in ("/TEST_STDLIB/../SECRET/file.py", "/TEST_STDLIB/site-packages/x.py", "/TEST_STDLIB/dist-packages/x.py",
                     "/TEST_STDLIB2/x.py", "/TEST_STDLIB/data.txt"):
            self.assertEqual(self.check("open", (path, "r", 0)), "FILE_READ")
    def test_operation_hook_only_authorized_partial_and_link(self):
        args = dict(allowed_reads={"/TEST_ONLY/code.py"}, blocked_caches=set(),
                    write_partial="/srv/a2out/.partial-result.json", final_path="/srv/a2out/result.json", stdlib_root="/TEST_STDLIB")
        self.assertEqual(op.audit_decision("open", (args["write_partial"], None, os.O_WRONLY|os.O_CREAT), **args), "ALLOW")
        self.assertEqual(op.audit_decision("open", (args["final_path"], "w", os.O_WRONLY), **args), "DENY_WRITE")
        self.assertEqual(op.audit_decision("os.link", (args["write_partial"], args["final_path"]), **args), "ALLOW")
        self.assertEqual(op.audit_decision("os.link", (args["write_partial"], "/tmp/x"), **args), "DENY_LINK")
        self.assertEqual(op.audit_decision("open", ("/TEST_STDLIB/dist-packages/x.py", "r", 0), **args), "DENY_READ")
    def test_operation_hook_bootstrap_has_no_local_import_before_cache_guard(self):
        import ast
        text = Path(op.__file__).read_text(encoding="utf-8")
        tree = ast.parse(text)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_install_audit_hook")
        imports = [n.module for n in ast.walk(function) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(name and name.startswith("research") for name in imports))
        self.assertEqual(writer.PARTIAL_PREFIX, ".partial-")


def qualified_units():
    """Fabricated TEST_ONLY accounting; never evidence from a host."""
    props = {"Result": "exit-code", "ExecMainCode": "1", "ExecMainStatus": "20", "TasksMax": "1",
        "RuntimeMaxUSec": "1min", "LimitCPU": "5", "LimitCORE": "0", "MemoryMax": str(qual.MEMORY_MAX),
        "MemorySwapMax": "0", "MemorySwapPeak": "0", "MemoryPeak": "10000000", "CPUUsageNSec": "10000000",
        "ExecMainStartTimestampMonotonic": "1000000", "ExecMainExitTimestampMonotonic": "2000000",
        "StandardOutput": "null", "StandardError": "null", "PrivateNetwork": "yes"}
    units = {key: {"probe": probe, "show": deepcopy(props), "show_available": True,
        "observation": {}, "malformed_observation": False, "journal_available": True, "probe_entered": True,
        "stdio_marker_in_journal": False, "cgroup": {}} for key, probe, _ in qual.UNIT_KEYS}
    units["time"]["show"].update(Result="timeout", ExecMainCode="2", ExecMainStatus="15")
    units["cpu"]["show"].update(Result="signal", ExecMainCode="2", ExecMainStatus="24", CPUUsageNSec="5000000000")
    units["memory"]["show"].update(Result="oom-kill", ExecMainCode="2", ExecMainStatus="9")
    for key in ("time", "cpu", "memory"):
        units[key]["observation"] = None
    units["child"]["observation"] = {"fork": "EAGAIN", "thread": "RuntimeError"}
    for key in ("network", "network_pn"):
        units[key]["observation"] = {"interfaces": ["lo"], "namespace_isolated": True,
            "attempts": {key: "SOCKET_EAFNOSUPPORT" for key in qual.NETWORK_KEYS}}
    units["write"]["observation"] = {"fill": "ENOSPC", "fill_bytes_before_stop": qual.ONE_MIB,
        "outside_writable_directory": {key: "EROFS" for key in qual.ESCAPE_PATHS}}
    units["output"]["observation"] = {"bounded_writer": "REFUSED", "oversize_file_present": False}
    units["read"]["observation"] = {key: expected if expected is not None else "EMPTY"
                                    for key, expected in qual.READ_EXPECTATIONS.items()}
    units["positive"]["show"]["ExecMainStatus"] = "21"
    units["positive"]["observation"] = {"checksum_mod_97": sum(i*i for i in range(200000)) % 97}
    return units


class QualificationTests(unittest.TestCase):
    def verdict(self, units, key):
        return qual.summarize_units(units, "TEST_ONLY")["verdicts"][key]
    def test_synthetic_positive_complete_transcript(self):
        self.assertEqual(qual.summarize_units(qualified_units(), "TEST_ONLY")["overall"], qual.FULLY_QUALIFIED)
    def test_profile_bounds_match_ratified_values_and_stdio_is_discarded(self):
        path = Path(__file__).resolve().parents[1] / "common/a2_unit_profile.sh"
        text = path.read_text(encoding="ascii")
        properties = {line.strip()[3:] for line in text.splitlines() if line.strip().startswith("-p ")}
        expected = {"RuntimeMaxSec=60", "LimitCPU=5", "MemoryMax=128M", "MemorySwapMax=0",
            "TasksMax=1", "LimitCORE=0", "StandardInput=null", "StandardOutput=null",
            "StandardError=null", "PrivateNetwork=yes", "RestrictAddressFamilies=AF_UNIX",
            "ReadWritePaths=/srv/a2out", "User=a2runner", "Group=a2runner"}
        self.assertTrue(expected.issubset(properties))
        self.assertIn("/usr/bin/python3 -I -S -B -X pycache_prefix=/nonexistent", text)
    def test_missing_or_malformed_accounting_cannot_qualify(self):
        self.assertNotEqual(qual.summarize_units({}, "TEST_ONLY")["overall"], qual.FULLY_QUALIFIED)
        for key, _, _ in qual.UNIT_KEYS:
            for field in ("show_available", "malformed_observation"):
                units = qualified_units()
                units[key][field] = field == "malformed_observation"
                self.assertNotEqual(qual.summarize_units(units, "TEST_ONLY")["overall"], qual.FULLY_QUALIFIED)
    def test_numeric_overshoot_is_breach_even_with_expected_signal(self):
        for key, prop, value, label in (("time", "ExecMainExitTimestampMonotonic", "61000001", "ELAPSED_60S"),
            ("cpu", "CPUUsageNSec", "5000000001", "CPU_5S"),
            ("memory", "MemoryPeak", str(qual.MEMORY_MAX+1), "MEMORY_128MIB"),
            ("memory", "MemorySwapPeak", "1", "NO_SWAP")):
            units = qualified_units()
            units[key]["show"][prop] = value
            with self.subTest(key=key):
                self.assertEqual(self.verdict(units, label), qual.BREACH)
    def test_missing_peak_or_masked_cpu_probe_is_not_verified(self):
        units = qualified_units()
        units["memory"]["show"].pop("MemoryPeak")
        self.assertEqual(self.verdict(units, "MEMORY_128MIB"), qual.UNVERIFIED)
        units["cpu"]["show"]["Result"] = "oom-kill"
        self.assertEqual(self.verdict(units, "CPU_5S"), qual.UNVERIFIED)
    def test_probe_not_reached_or_early_unexplained_kill_is_not_verified(self):
        units = qualified_units()
        units["memory"]["probe_entered"] = False
        self.assertEqual(self.verdict(units, "MEMORY_128MIB"), qual.UNVERIFIED)
        units["cpu"]["show"].update(ExecMainStatus="9", CPUUsageNSec="100000")
        self.assertEqual(self.verdict(units, "CPU_5S"), qual.UNVERIFIED)
    def test_child_or_thread_created_is_breach_despite_exit_20(self):
        for component in ("fork", "thread"):
            units = qualified_units()
            units["child"]["observation"][component] = "CREATED"
            self.assertEqual(self.verdict(units, "ONE_PROCESS_NO_CHILD"), qual.BREACH)
    def test_network_timeout_does_not_prove_zero_communication(self):
        units = qualified_units()
        units["network_pn"]["observation"]["attempts"]["tcp:192.0.2.1"] = "TimeoutError"
        self.assertEqual(self.verdict(units, "NETWORK_ZERO_PRIVATE_NETWORK_ALONE"), qual.UNVERIFIED)
    def test_network_sent_namespace_unknown_or_incomplete_attempts(self):
        for change, expected in (("sent", qual.BREACH), ("namespace", qual.UNVERIFIED), ("missing", qual.UNVERIFIED)):
            units = qualified_units()
            obs = units["network"]["observation"]
            if change == "sent":
                obs["attempts"]["udp:192.0.2.1"] = "SENT"
            elif change == "namespace":
                obs["namespace_isolated"] = False
            else:
                del obs["attempts"]["udp:192.0.2.1"]
            self.assertEqual(self.verdict(units, "NETWORK_ZERO_FAMILY_RESTRICTION_AND_PRIVATE_NETWORK"), expected)
    def test_empty_observation_does_not_prove_refusal(self):
        for key, label in (("child", "ONE_PROCESS_NO_CHILD"), ("write", "WRITABLE_1MIB_AND_NO_ESCAPE"),
                          ("output", "OUTPUT_64KIB_BOUNDED_WRITER"), ("read", "READ_ISOLATION")):
            units = qualified_units()
            units[key]["observation"] = {}
            self.assertEqual(self.verdict(units, label), qual.UNVERIFIED)
    def test_escape_oversize_or_stdio_marker_is_breach(self):
        units = qualified_units()
        units["write"]["observation"]["outside_writable_directory"]["/tmp"] = "CREATED"
        units["output"]["observation"]["oversize_file_present"] = True
        units["output"]["stdio_marker_in_journal"] = True
        for label in ("WRITABLE_1MIB_AND_NO_ESCAPE", "OUTPUT_64KIB_BOUNDED_WRITER", "STDOUT_STDERR_DISCARDED"):
            self.assertEqual(self.verdict(units, label), qual.BREACH)
    def test_absent_journal_and_core_dump_are_not_success(self):
        units = qualified_units()
        units["output"]["journal_available"] = False
        self.assertEqual(self.verdict(units, "STDOUT_STDERR_DISCARDED"), qual.UNVERIFIED)
        units["cpu"]["show"]["ExecMainCode"] = "3"
        self.assertEqual(self.verdict(units, "NO_CORE_DUMP"), qual.BREACH)
    def test_show_duplicates_rejected_and_zero_not_treated_as_missing(self):
        self.assertEqual(qual.parse_show("Result=signal\nResult=success\n"), ({}, False))
        self.assertEqual(qual._integer("0"), 0)
        self.assertIsNone(qual._integer(True))
    def test_malformed_observation_is_safe_not_verified(self):
        with patch.object(qual, "_read", side_effect=lambda path: "{" if path.suffix == ".json" else "Result=signal\n"):
            unit = qual.load_unit(Path("/TEST_ONLY"), "memory", "full", "TEST_ONLY")
        self.assertTrue(unit["malformed_observation"])
        self.assertEqual(self.verdict({"memory": unit}, "MEMORY_128MIB"), qual.UNVERIFIED)
