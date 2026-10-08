"""L2-I new tests for the L2-H root candidate (read-only verification, no activation).

Real-root cases use the real frozen manifests/policy and the real root, but NEVER an
ActionAuthorization in state AUTHORIZED: every call is routed through ``real_eval`` which
refuses such an authorization and asserts DENY. Positive paths use only TEST_ONLY
synthetic objects under a patched root with synthetic identifiers and no E authority.
"""
from __future__ import annotations

import ast
import re
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from research.weather_forward.v4 import a2_harness as api
from research.weather_forward.v4.a2_harness import harness as h
from research.weather_forward.v4.a2_harness import trusted_root as tr
from research.weather_forward.v4.a2_harness.test_bounded_runtime import TestContext
from research.weather_forward.v4.a2_operation.identity import identity_via_harness as via_h
from research.weather_forward.v4.a2_operation.operation import a2_doc_integration_operation as op

ROOT = Path(__file__).resolve().parents[5]
V4 = ROOT / "research/weather_forward/v4"
E_SHA = "6e0320f15d48a924cef9507af5641e47de9fe938"
C_SHA = "37e3b25f17a7c5d3b3bc8d37df730aa988585b6c"
CANDIDATE_COMMIT = "73280c3e9d8604b2f2d8e6d2d174aa940389a760"
HARNESS_ID = "research/weather_forward/v4/a2_harness"
VERSION = "weather-v4-a2-doc-integration-v1"
POLICY_ID = "sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60"
INPUT_ID = "sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00"
OUTPUT_ID = "sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976"
EXPECTED_BLOBS = {"__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
                  "contract.py": "f6f94a4a472e3f6652a1502f6afb5825721364d0",
                  "harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
                  "trusted_root.py": "9704a844bae0ef54637c76dded5bb82d9f4c334f"}

COUNTERS = {"real_tuple_evaluations": 0, "real_tuple_permits": 0, "authorized_real_refused_by_guard": 0}


def load(name):
    document = via_h.load_document((V4 / "a2_operation/frozen" / name).read_text(encoding="utf-8"))
    return via_h.build_object(api, document)


class Real:
    input = load("input_manifest_d2_v1.json")
    output = load("output_manifest_d2_v1.json")
    policy = load("harness_policy_d2_v1.json")
    binding = api.AuthorityBinding(C_SHA, HARNESS_ID, VERSION, policy.expected_manifest_version_identity)
    executor = api.RoleDeclaration("blue.weather-v4.a2.doc-integration.v1", api.Role.EXECUTOR)

    @classmethod
    def auth(cls, **kw):
        base = dict(authorization_id="a2-doc-v1-read-input-blue", authority_sha=E_SHA,
                    actor_id=cls.executor.actor_id, declared_role=api.Role.EXECUTOR,
                    action=api.Action.READ_INPUT, state=api.AuthorizationState.DENIED)
        base.update(kw)
        return api.ActionAuthorization(**base)


def real_eval(authorization, *, manifest=None, policy=None, binding=None, actor=None):
    """Only entry point for evaluate_* on the real tuple: never AUTHORIZED, always DENY."""
    if authorization.state is api.AuthorizationState.AUTHORIZED:
        COUNTERS["authorized_real_refused_by_guard"] += 1
        raise AssertionError("TRIPWIRE: AUTHORIZED authorization on real tuple is forbidden in L2-I")
    COUNTERS["real_tuple_evaluations"] += 1
    result = api.A2Harness(binding or Real.binding, policy or Real.policy).evaluate_input_read(
        api.StructuredAuditLog(()), "TEST_ONLY_L2I_REAL_DENY", manifest or Real.input,
        actor or Real.executor, authorization)
    if result.decision.permit_or_deny_state is api.PermitState.PERMIT:
        COUNTERS["real_tuple_permits"] += 1
    return result


class DenyMixin:
    def assertDenied(self, result, reason=None, detail=None):
        d = result.decision
        self.assertIs(d.permit_or_deny_state, api.PermitState.DENY)
        self.assertIs(d.release_state, api.ReleaseState.BLOCKED)
        self.assertIsNot(d.validation_state, api.ValidationState.VALID)
        if reason is not None:
            self.assertIs(d.stop_reason, reason)
        if detail is not None:
            self.assertEqual(d.detail_code, detail)


class RootCandidateConstants(unittest.TestCase):
    def test_exact_root_tuple_matches_l2h_and_E(self):
        root = tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
        self.assertIs(type(root), api.TrustedExecutionPolicyRoot)
        self.assertEqual(tr.CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY, E_SHA)
        self.assertEqual(tuple(getattr(root, f.name) for f in fields(root)),
                         (E_SHA, C_SHA, HARNESS_ID, VERSION, POLICY_ID))

    def test_resolver_returns_the_constant_and_harness_uses_it(self):
        self.assertIs(tr.get_trusted_execution_policy_root(), tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)
        self.assertIs(h.get_trusted_execution_policy_root, tr.get_trusted_execution_policy_root)

    def test_real_frozen_identities_equal_E_table_and_root_policy_identity(self):
        self.assertEqual(api.input_manifest_identity(Real.input), INPUT_ID)
        self.assertEqual(api.output_manifest_identity(Real.output), OUTPUT_ID)
        self.assertEqual(api.harness_policy_identity(Real.policy), POLICY_ID)
        self.assertEqual(Real.policy.expected_input_manifest_identity, INPUT_ID)
        self.assertEqual(Real.policy.expected_output_manifest_identity, OUTPUT_ID)

    def test_no_setter_override_or_environment_path_in_source(self):
        source = (V4 / "a2_harness/trusted_root.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and hasattr(n, "name")]
        self.assertEqual(functions, ["get_trusted_execution_policy_root"])
        code = ast.unparse(ast.Module(body=[n for n in tree.body if not (
            isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))], type_ignores=[]))
        for forbidden in (r"\benviron\b", r"\bgetenv\b", r"\bsetattr\b", r"\bglobal\b", r"\bopen\(",
                          r"\bimport os\b", r"\bimport sys\b", r"\bimportlib\b", r"\bexec\(", r"\beval\("):
            self.assertIsNone(re.search(forbidden, code), forbidden)
        imports = [ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.assertEqual(imports, ["from __future__ import annotations", "from typing import Final",
                                   "from .contract import TrustedExecutionPolicyRoot"])
        self.assertEqual(source.count(E_SHA), 3)  # docstring + authority constant + root field
        self.assertNotIn(CANDIDATE_COMMIT, source)  # E never names a candidate commit

    def test_root_is_immutable(self):
        root = tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
        with self.assertRaises(Exception):
            root.execution_policy_authority_sha = "f" * 40
        self.assertTrue(is_dataclass(root))


class RealRootBindingMismatches(unittest.TestCase, DenyMixin):
    """validate_binding is a binding validation, not an evaluate_*: no log, no authorization."""

    def vb(self, binding=None, policy=None):
        return api.A2Harness(binding or Real.binding, policy or Real.policy).validate_binding()

    def test_baseline_real_binding_resolves_only_with_announced_tuple(self):
        r = self.vb()
        self.assertIs(r.state, api.ValidationState.VALID)
        self.assertEqual(r.detail_code, "AUTHORITY_AND_TRUSTED_ROOT_VALID")

    def test_single_deviation_each_refused_at_its_own_barrier(self):
        cases = [
            ("construction", replace(Real.binding, owner_authority_sha="3" * 40), Real.policy,
             "TRUSTED_ROOT_CONSTRUCTION_AUTHORITY_MISMATCH"),
            ("component", replace(Real.binding, harness_identity="other/a2_harness"), Real.policy,
             "TRUSTED_ROOT_HARNESS_IDENTITY_MISMATCH"),
            ("version", replace(Real.binding, harness_version_or_commit_identity="weather-v4-a2-doc-integration-v2"),
             Real.policy, "TRUSTED_ROOT_HARNESS_VERSION_MISMATCH"),
            ("policy", Real.binding, replace(Real.policy, expected_input_manifest_id="substituted-input"),
             "TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH"),
        ]
        for name, binding, policy, detail in cases:
            with self.subTest(name):
                r = self.vb(binding, policy)
                self.assertIs(r.stop_reason, api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)
                self.assertEqual(r.detail_code, detail)
                self.assertIsNot(r.state, api.ValidationState.VALID)

    def test_manifest_version_mismatch_passes_root_but_fails_authority(self):
        r = self.vb(replace(Real.binding, manifest_version_identity="OTHER-MANIFEST-V1"))
        self.assertIs(r.stop_reason, api.StopReason.AUTHORITY_MISMATCH)
        self.assertEqual(r.detail_code, "MANIFEST_VERSION_IDENTITY_MISMATCH")

    def test_coordinated_identity_and_policy_substitution_cannot_move_the_root(self):
        binding = replace(Real.binding, owner_authority_sha="3" * 40, harness_identity="SUBSTITUTED_HARNESS")
        policy = replace(Real.policy, expected_owner_authority_sha="3" * 40,
                         expected_harness_identity="SUBSTITUTED_HARNESS")
        r = self.vb(binding, policy)
        self.assertIs(r.stop_reason, api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)
        self.assertEqual(r.detail_code, "TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH")


class RealRootActionRefusals(unittest.TestCase, DenyMixin):
    """Each case keeps authorization non-AUTHORIZED; the barrier reached is asserted."""

    def test_denied_authorization_citing_E_is_refused_at_state_barrier(self):
        for state in (api.AuthorizationState.DENIED, api.AuthorizationState.UNRESOLVED):
            with self.subTest(state=state):
                self.assertDenied(real_eval(Real.auth(state=state)),
                                  api.StopReason.UNAUTHORIZED_READER, "ACTION_AUTHORIZATION_NOT_AUTHORIZED")

    def test_wrong_E_sha_and_candidate_commit_as_E_refused(self):
        for sha in ("0" * 40, CANDIDATE_COMMIT, "6e0320f15d48a924cef9507af5641e47de9fe938".upper(),
                    E_SHA[:39] + "f"):
            with self.subTest(sha=sha):
                self.assertDenied(real_eval(Real.auth(authority_sha=sha)), api.StopReason.AUTHORITY_MISMATCH,
                                  "ACTION_AUTHORIZATION_EXECUTION_POLICY_AUTHORITY_MISMATCH")

    def test_actor_role_action_discordance_refused_before_authority(self):
        cases = {
            "actor": (Real.auth(actor_id="blue.other"), "ACTION_AUTHORIZATION_ACTOR_MISMATCH"),
            "role": (Real.auth(declared_role=api.Role.RELEASE_APPROVER), "ACTION_AUTHORIZATION_ROLE_MISMATCH"),
            "action": (Real.auth(action=api.Action.RELEASE_OUTPUT), "ACTION_AUTHORIZATION_ACTION_MISMATCH"),
        }
        for name, (auth, detail) in cases.items():
            with self.subTest(name):
                self.assertDenied(real_eval(auth), api.StopReason.UNAUTHORIZED_READER, detail)

    def test_out_of_domain_status_on_real_tuple_is_never_permit(self):
        with self.assertRaises(ValueError):
            api.AuthorizationState("APPROVED")
        for bad in ("APPROVED", None, 1):
            with self.subTest(bad=bad):
                try:
                    result = real_eval(Real.auth(state=bad))
                except Exception:
                    continue
                self.assertDenied(result)

    def test_manifest_and_policy_substitution_on_real_tuple(self):
        swapped = replace(Real.input, input_id="substituted-input")
        self.assertDenied(real_eval(Real.auth(), manifest=swapped))
        policy = replace(Real.policy, expected_output_manifest_id="substituted-output")
        self.assertDenied(real_eval(Real.auth(), policy=policy), api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH,
                          "TRUSTED_ROOT_POLICY_IDENTITY_MISMATCH")

    def test_E_substituted_in_root_denies_when_authorization_cites_real_E(self):
        root = replace(tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT, execution_policy_authority_sha="a" * 40)
        with patch.object(h, "get_trusted_execution_policy_root", return_value=root):
            self.assertDenied(real_eval(Real.auth()), api.StopReason.AUTHORITY_MISMATCH,
                              "ACTION_AUTHORIZATION_EXECUTION_POLICY_AUTHORITY_MISMATCH")

    def test_fail_closed_when_root_unavailable_or_malformed(self):
        bad_roots = {
            "none": None,
            "empty_fields": api.TrustedExecutionPolicyRoot("", "", "", "", ""),
            "short_sha": replace(tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT, execution_policy_authority_sha="6e0320f"),
            "bad_policy_identity": replace(tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT, expected_policy_identity="sha256:xyz"),
        }
        for name, root in bad_roots.items():
            with self.subTest(name), patch.object(h, "get_trusted_execution_policy_root", return_value=root):
                self.assertDenied(real_eval(Real.auth()))
        for name, value in {"object": object(), "namespace": SimpleNamespace()}.items():
            with self.subTest(name), patch.object(h, "get_trusted_execution_policy_root", return_value=value):
                try:
                    result = real_eval(Real.auth())
                except Exception:
                    continue
                self.assertDenied(result)
        with patch.object(h, "get_trusted_execution_policy_root", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                real_eval(Real.auth())

    def test_tripwire_refuses_authorized_on_real_tuple(self):
        before = COUNTERS["real_tuple_evaluations"]
        with self.assertRaises(AssertionError):
            real_eval(Real.auth(state=api.AuthorizationState.AUTHORIZED))
        self.assertEqual(COUNTERS["real_tuple_evaluations"], before)


class SyntheticOnlyPositiveAndLateBarriers(unittest.TestCase, DenyMixin):
    """TEST_ONLY objects, synthetic root (patched), synthetic ids, no E authority."""

    def setUp(self):
        self.ctx = TestContext()

    def patched(self, root=None):
        return patch.object(h, "get_trusted_execution_policy_root", return_value=root or self.ctx.root)

    def test_synthetic_context_does_not_use_E_or_real_identities(self):
        self.assertNotEqual(self.ctx.root.execution_policy_authority_sha, E_SHA)
        self.assertNotEqual(api.harness_policy_identity(self.ctx.policy), POLICY_ID)

    def test_synthetic_positive_sequence_and_real_root_restored(self):
        with self.patched():
            r = self.ctx.read()
            self.assertIs(r.decision.permit_or_deny_state, api.PermitState.PERMIT)
            self.assertIs(r.decision.release_state, api.ReleaseState.BLOCKED)
            self.assertTrue(r.log_acknowledged)
            rel = self.ctx.release()
            self.assertIs(rel.decision.release_state, api.ReleaseState.AUTHORIZED)
        self.assertIs(h.get_trusted_execution_policy_root(), tr.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT)

    def test_synthetic_substitution_denied_by_synthetic_root(self):
        binding = replace(self.ctx.binding, owner_authority_sha="3" * 40)
        policy = replace(self.ctx.policy, expected_owner_authority_sha="3" * 40)
        with self.patched():
            self.assertDenied(self.ctx.read(binding=binding, policy=policy),
                              api.StopReason.EXECUTION_POLICY_ROOT_MISMATCH)

    def test_synthetic_out_of_domain_and_wrong_authority_status(self):
        with self.patched():
            self.assertDenied(self.ctx.read(authorization=replace(self.ctx.read_auth, authority_sha=E_SHA)),
                              api.StopReason.AUTHORITY_MISMATCH)
            for bad in ("AUTHORIZED", "APPROVED", None):
                with self.subTest(bad=bad):
                    try:
                        result = self.ctx.read(authorization=replace(self.ctx.read_auth, state=bad))
                    except Exception:
                        continue
                    self.assertDenied(result)

    def test_synthetic_quarantine_barrier(self):
        for state in (api.QuarantineState.QUARANTINED, api.QuarantineState.BLOCKED_PENDING_OWNER_REVIEW):
            with self.subTest(state=state):
                output = replace(self.ctx.output, quarantine_status=state)
                policy = replace(self.ctx.policy, expected_output_manifest_identity=api.output_manifest_identity(output))
                with self.patched(self.ctx.root_for(policy)):
                    result = self.ctx.release(manifest=output, policy=policy)
                self.assertDenied(result)
                self.assertEqual(result.decision.detail_code, "OUTPUT_QUARANTINE_STATE_BLOCKS_RELEASE")

    def test_synthetic_ledger_and_log_barriers(self):
        with self.patched():
            self.assertDenied(self.ctx.release(ledger=api.CumulativeDisclosureLedger(())))
            blocked = replace(self.ctx.ledger.records[0], disclosure_id="TEST_ONLY_B",
                              cumulative_safety=api.CumulativeDisclosureState.BLOCKED)
            self.assertDenied(self.ctx.release(ledger=api.CumulativeDisclosureLedger((self.ctx.ledger.records[0], blocked))))
            first = self.ctx.read()
            second = self.ctx.read(log=first.log, log_id="TEST_ONLY_LOG_READ")  # duplicate record id
            self.assertDenied(second)
            self.assertFalse(second.log_acknowledged)

    def test_synthetic_leakage_barrier(self):
        output = replace(self.ctx.output, efficacy_leakage_assessment=api.LeakageAssessment.UNRESOLVED)
        policy = replace(self.ctx.policy, expected_output_manifest_identity=api.output_manifest_identity(output))
        with self.patched(self.ctx.root_for(policy)):
            self.assertDenied(self.ctx.release(manifest=output, policy=policy))


class BlobAndCommitMismatch(unittest.TestCase):
    def read(self, mutate=None):
        def reader(name):
            data = (V4 / "a2_harness" / name).read_bytes()
            return mutate(name, data) if mutate else data
        return reader

    def test_real_blobs_verify_and_candidate_blob_is_pinned(self):
        self.assertEqual(op.verify_harness_blobs(self.read(), EXPECTED_BLOBS), EXPECTED_BLOBS)

    def test_tampered_root_blob_or_E_sha_is_refused(self):
        wrong_e = lambda n, d: d.replace(E_SHA.encode(), b"0" * 40) if n == "trusted_root.py" else d
        extra = lambda n, d: d + b"\n" if n == "trusted_root.py" else d
        old_root = lambda n, d: d.replace(b"6e0320f1", b"6e0320f2", 1) if n == "trusted_root.py" else d
        for name, mutate in {"wrong_E": wrong_e, "appended": extra, "one_char": old_root}.items():
            with self.subTest(name), self.assertRaises(op.StopOperation):
                op.verify_harness_blobs(self.read(mutate), EXPECTED_BLOBS)

    def test_deny_all_h_blob_does_not_verify_as_candidate(self):
        h_blob = dict(EXPECTED_BLOBS, **{"trusted_root.py": "9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94"})
        with self.assertRaises(op.StopOperation):
            op.verify_harness_blobs(self.read(), h_blob)


if __name__ == "__main__":
    unittest.main()
