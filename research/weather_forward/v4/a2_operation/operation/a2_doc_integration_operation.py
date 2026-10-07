"""Future bounded A2 documentary-integration operation (lot 4) -- NOT RUN IN LOT 2.

Authority: Owner lot-2 decision (commit 276fd995fe494e1734bba13827e6103864ce68da,
L2-B item 5) ratified at ccd4747e4bb9e2a4d93c552ba10e081f254af1e7. Running this
script against the real configuration requires execution authority E, the lot-3
independent review and an explicit lot-4 activation/operation decision. In lot 2
its logic is exercised only on synthetic TEST_ONLY objects.

Sequence (dossier D section 14.9D as rectified by section 14.14.5):
1. exactly one ``evaluate_input_read``;
2. the exact input proceed predicate;
3. at most one ``evaluate_output_release``, only on branch D1 when the release
   section (attributable Astra approval reference, RELEASE_OUTPUT authorization
   and ledger) is present, passing ``first_result.log`` and a distinct record id;
4. no retry.

Visible channel: the process exit code only. Nothing is written to stdout or
stderr. The structural result (exactly the fifteen elements of dossier D
section 14.2B) is written, at most 65,536 bytes, through the bounded writer, and
only on a normal end (0) or an authorized release (10).

Exit codes: 0 normal end without release; 10 release AUTHORIZED and linked;
30 STOP (context, predicate, linkage or unexpected code; no result written);
40 exception (no result written); 50 result above 64 KiB (nothing written).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys

EXIT_NORMAL_NO_RELEASE = 0
EXIT_RELEASE_AUTHORIZED = 10
EXIT_STOP = 30
EXIT_EXCEPTION = 40
EXIT_OUTPUT_LIMIT = 50

CONTEXT_SCHEMA = "A2_DOC_INTEGRATION_OPERATION_CONTEXT_V1"
HARNESS_PACKAGE_PATH = ("research", "weather_forward", "v4", "a2_harness")
HARNESS_PRODUCTION_FILES = ("__init__.py", "contract.py", "harness.py", "trusted_root.py")
OPERATION_SOURCE_FILES = (
    ("research", "weather_forward", "v4", "a2_operation", "__init__.py"),
    ("research", "weather_forward", "v4", "a2_operation", "common", "__init__.py"),
    ("research", "weather_forward", "v4", "a2_operation", "common", "bounded_output.py"),
    ("research", "weather_forward", "v4", "a2_operation", "identity", "__init__.py"),
    ("research", "weather_forward", "v4", "a2_operation", "identity", "identity_via_harness.py"),
    ("research", "weather_forward", "v4", "a2_operation", "operation", "__init__.py"),
    ("research", "weather_forward", "v4", "a2_operation", "operation",
     "a2_doc_integration_operation.py"),
)

INPUT_SUCCESS_CODE = "INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED"
OUTPUT_SUCCESS_CODE = "OUTPUT_RELEASE_ELIGIBLE_LOGGED_AND_COMPLETED"

RESULT_ELEMENTS = (
    "validation_state", "permit_or_deny_state", "quarantine_state", "release_state",
    "completion_state", "stop_reason", "detail_code", "input_manifest_reference",
    "output_manifest_reference", "policy_reference", "construction_authority_reference",
    "execution_authority_reference", "actor_role_bindings",
    "acknowledged_log_record_references", "structural_linkage_status",
)

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_RECORD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

CONTEXT_KEYS = frozenset({
    "schema", "branch", "output_directory", "result_file_name", "harness_source_blobs",
    "authority_binding", "input_manifest", "output_manifest", "policy",
    "execution_authority_sha", "executor", "recipient", "approver", "read_authorization",
    "release", "log", "accepted_detail_codes",
})


class ContextError(ValueError):
    """The operation context does not match its exact schema."""


class StopOperation(Exception):
    """A predicate, linkage or code check failed; stop without writing a result."""


# --------------------------------------------------------------------------- context

def _require_keys(value, keys, name):
    if type(value) is not dict or set(value) != set(keys):
        raise ContextError(f"{name}:EXACT_KEYS_REQUIRED")
    return value


def _require_text(value, name):
    if type(value) is not str or not value:
        raise ContextError(f"{name}:NON_EMPTY_STRING_REQUIRED")
    return value


def _require_sha40(value, name):
    if type(value) is not str or not _SHA40.match(value):
        raise ContextError(f"{name}:LOWERCASE_40_HEX_REQUIRED")
    return value


def _require_record_id(value, name):
    if type(value) is not str or not _RECORD_ID.match(value):
        raise ContextError(f"{name}:RECORD_ID_FORMAT")
    return value


def validate_context(context) -> dict:
    """Strict structural validation; raises ContextError before any harness call."""
    _require_keys(context, CONTEXT_KEYS, "context")
    if context["schema"] != CONTEXT_SCHEMA:
        raise ContextError("context:UNSUPPORTED_SCHEMA")
    if context["branch"] not in ("D1", "D2"):
        raise ContextError("branch:D1_OR_D2_REQUIRED")
    _require_text(context["output_directory"], "output_directory")
    _require_text(context["result_file_name"], "result_file_name")
    blobs = _require_keys(context["harness_source_blobs"], HARNESS_PRODUCTION_FILES,
                          "harness_source_blobs")
    for name in HARNESS_PRODUCTION_FILES:
        _require_sha40(blobs[name], f"harness_source_blobs.{name}")
    binding = _require_keys(context["authority_binding"], (
        "owner_authority_sha", "harness_identity", "harness_version_or_commit_identity",
        "manifest_version_identity"), "authority_binding")
    _require_sha40(binding["owner_authority_sha"], "authority_binding.owner_authority_sha")
    for key in ("harness_identity", "harness_version_or_commit_identity",
                "manifest_version_identity"):
        _require_text(binding[key], f"authority_binding.{key}")
    for key, kind in (("input_manifest", "InputManifest"), ("output_manifest", "OutputManifest"),
                      ("policy", "HarnessPolicy")):
        document = context[key]
        if type(document) is not dict or document.get("kind") != kind:
            raise ContextError(f"{key}:FROZEN_DOCUMENT_OF_KIND_{kind}_REQUIRED")
    _require_sha40(context["execution_authority_sha"], "execution_authority_sha")
    for key in ("executor", "recipient", "approver"):
        actor = _require_keys(context[key], ("actor_id", "role"), key)
        _require_text(actor["actor_id"], f"{key}.actor_id")
        _require_text(actor["role"], f"{key}.role")
    _validate_authorization(context["read_authorization"], "read_authorization")
    log = _require_keys(context["log"], ("input_record_id", "output_record_id",
                                         "incident_identifier"), "log")
    _require_record_id(log["input_record_id"], "log.input_record_id")
    if log["incident_identifier"] is not None:
        _require_text(log["incident_identifier"], "log.incident_identifier")
    release = context["release"]
    if context["branch"] == "D2":
        if release is not None or log["output_record_id"] is not None:
            raise ContextError("D2:NO_RELEASE_SECTION_OR_OUTPUT_RECORD_ALLOWED")
    if release is not None:
        _require_keys(release, ("authorization", "approval_artifact", "ledger"), "release")
        _validate_authorization(release["authorization"], "release.authorization")
        artifact = _require_keys(release["approval_artifact"],
                                 ("repository", "path", "commit", "blob"),
                                 "release.approval_artifact")
        _require_text(artifact["repository"], "release.approval_artifact.repository")
        _require_text(artifact["path"], "release.approval_artifact.path")
        _require_sha40(artifact["commit"], "release.approval_artifact.commit")
        _require_sha40(artifact["blob"], "release.approval_artifact.blob")
        if type(release["ledger"]) is not list or not release["ledger"]:
            raise ContextError("release.ledger:NON_EMPTY_ARRAY_REQUIRED")
        for index, record in enumerate(release["ledger"]):
            _require_keys(record, ("disclosure_id", "output_id", "recipient_actor_id",
                                   "recipient_role", "cumulative_safety"),
                          f"release.ledger[{index}]")
            for key in record:
                _require_text(record[key], f"release.ledger[{index}].{key}")
        _require_record_id(log["output_record_id"], "log.output_record_id")
        if log["output_record_id"] == log["input_record_id"]:
            raise ContextError("log:OUTPUT_RECORD_ID_MUST_DIFFER")
    codes = context["accepted_detail_codes"]
    if type(codes) is not list or not codes or any(type(c) is not str or not c for c in codes):
        raise ContextError("accepted_detail_codes:NON_EMPTY_STRING_ARRAY_REQUIRED")
    if len(set(codes)) != len(codes):
        raise ContextError("accepted_detail_codes:DUPLICATES")
    return context


def _validate_authorization(value, name):
    auth = _require_keys(value, ("authorization_id", "authority_sha", "actor_id",
                                 "declared_role", "action", "state"), name)
    _require_text(auth["authorization_id"], f"{name}.authorization_id")
    _require_sha40(auth["authority_sha"], f"{name}.authority_sha")
    for key in ("actor_id", "declared_role", "action", "state"):
        _require_text(auth[key], f"{name}.{key}")


# --------------------------------------------------------------------- source pins

def git_blob_id(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def verify_harness_blobs(read_bytes, expected: dict) -> dict:
    """Return the observed blob ids; raise StopOperation on any difference."""
    observed = {name: git_blob_id(read_bytes(name)) for name in HARNESS_PRODUCTION_FILES}
    if observed != expected:
        raise StopOperation("HARNESS_SOURCE_BLOB_MISMATCH")
    return observed


# ----------------------------------------------------------------------- objects

class Objects:
    """Exact harness objects built from the validated context."""

    __slots__ = ("binding", "input", "output", "policy", "executor", "recipient",
                 "approver", "read_authorization", "release_authorization", "ledger",
                 "execution_authority_sha", "input_record_id", "output_record_id",
                 "incident_identifier", "accepted_codes", "branch")


def _authorization(api, value):
    return api.ActionAuthorization(
        value["authorization_id"], value["authority_sha"], value["actor_id"],
        api.Role(value["declared_role"]), api.Action(value["action"]),
        api.AuthorizationState(value["state"]),
    )


def build_objects(api, build_object, context) -> Objects:
    """Build harness dataclasses; ``build_object`` is the frozen-content converter."""
    objects = Objects()
    binding = context["authority_binding"]
    objects.binding = api.AuthorityBinding(
        binding["owner_authority_sha"], binding["harness_identity"],
        binding["harness_version_or_commit_identity"], binding["manifest_version_identity"],
    )
    objects.input = build_object(api, context["input_manifest"])
    objects.output = build_object(api, context["output_manifest"])
    objects.policy = build_object(api, context["policy"])
    objects.executor = api.RoleDeclaration(context["executor"]["actor_id"],
                                           api.Role(context["executor"]["role"]))
    objects.recipient = api.RoleDeclaration(context["recipient"]["actor_id"],
                                            api.Role(context["recipient"]["role"]))
    objects.approver = api.RoleDeclaration(context["approver"]["actor_id"],
                                           api.Role(context["approver"]["role"]))
    objects.read_authorization = _authorization(api, context["read_authorization"])
    if objects.read_authorization.action is not api.Action.READ_INPUT:
        raise ContextError("read_authorization:READ_INPUT_REQUIRED")
    objects.execution_authority_sha = context["execution_authority_sha"]
    log = context["log"]
    objects.input_record_id = log["input_record_id"]
    objects.output_record_id = log["output_record_id"]
    objects.incident_identifier = log["incident_identifier"]
    objects.accepted_codes = frozenset(context["accepted_detail_codes"])
    objects.branch = context["branch"]
    release = context["release"]
    if release is None:
        objects.release_authorization = None
        objects.ledger = None
    else:
        objects.release_authorization = _authorization(api, release["authorization"])
        if objects.release_authorization.action is not api.Action.RELEASE_OUTPUT:
            raise ContextError("release.authorization:RELEASE_OUTPUT_REQUIRED")
        objects.ledger = api.CumulativeDisclosureLedger(tuple(
            api.DisclosureRecord(r["disclosure_id"], r["output_id"], r["recipient_actor_id"],
                                 api.Role(r["recipient_role"]),
                                 api.CumulativeDisclosureState(r["cumulative_safety"]))
            for r in release["ledger"]
        ))
    return objects


# -------------------------------------------------------------------- predicates

def _expected_record(api, objects, *, action, target_kind, target_id, manifest_identity,
                     actor, authorization, release_state, cumulative_state, recipient,
                     record_id):
    return api.LogRecord(
        record_id=record_id,
        construction_authority_identity=objects.binding.owner_authority_sha,
        execution_policy_authority_identity=objects.execution_authority_sha,
        authorization_authority_identity=authorization.authority_sha,
        manifest_identity=manifest_identity,
        actor_id=actor.actor_id,
        actor_role=actor.declared_role,
        authorization_id=authorization.authorization_id,
        attempted_action=action,
        target_kind=target_kind,
        target_id=target_id,
        permit_or_deny_state=api.PermitState.PERMIT,
        quarantine_state=api.QuarantineState.CLEAR,
        release_state=release_state,
        incident_identifier=objects.incident_identifier,
        cumulative_disclosure_state=cumulative_state,
        recipient_actor_id=recipient.actor_id if recipient is not None else None,
        recipient_role=recipient.declared_role if recipient is not None else None,
    )


def _check_decision(api, result, *, release_state, detail_code):
    if type(result) is not api.LoggedActionResult or type(result.decision) is not api.HarnessDecision:
        raise StopOperation("UNEXPECTED_RESULT_TYPE")
    decision = result.decision
    checks = (
        decision.validation_state is api.ValidationState.VALID,
        decision.permit_or_deny_state is api.PermitState.PERMIT,
        decision.quarantine_state is api.QuarantineState.CLEAR,
        decision.release_state is release_state,
        decision.completion_state is api.CompletionState.COMPLETED,
        decision.stop_reason is None,
        decision.detail_code == detail_code,
        result.log_acknowledged is True,
        type(result.log) is api.StructuredAuditLog,
    )
    if not all(checks):
        raise StopOperation("DECISION_PREDICATE_FAILED")


def _check_linkage(api, result, expected_record, preceding_records):
    records = result.log.records
    if records[:len(preceding_records)] != preceding_records:
        raise StopOperation("PRECEDING_RECORDS_NOT_PRESERVED")
    if len(records) != len(preceding_records) + 1:
        raise StopOperation("UNEXPECTED_RECORD_COUNT")
    matching = tuple(r for r in records if r.record_id == expected_record.record_id)
    if matching != (expected_record,) or result.log_record != expected_record:
        raise StopOperation("RECORD_CONTENT_OR_CONTEXT_MISMATCH")
    record = result.log_record
    decision = result.decision
    if (record.permit_or_deny_state is not decision.permit_or_deny_state
            or record.quarantine_state is not decision.quarantine_state
            or record.release_state is not decision.release_state):
        raise StopOperation("SHARED_STATE_MISMATCH")


def release_prerequisites_present(api, objects) -> bool:
    """External conditions for the second call that this script can check itself.

    The authenticity of the approval artifact, E's conditions and the lot-4
    decision are verified outside the process before launch; here only their
    presence and exact binding to the context are checked.
    """
    if objects.branch != "D1" or objects.release_authorization is None:
        return False
    auth = objects.release_authorization
    return (auth.state is api.AuthorizationState.AUTHORIZED
            and auth.actor_id == objects.approver.actor_id
            and auth.declared_role is api.Role.RELEASE_APPROVER
            and auth.authority_sha == objects.execution_authority_sha
            and objects.ledger is not None and len(objects.ledger.records) > 0
            and objects.output_record_id is not None)


# --------------------------------------------------------------------- execution

def execute(api, objects):
    """Run the bounded sequence; return (exit_code, evaluations, linkage)."""
    harness = api.A2Harness(objects.binding, objects.policy)
    first = harness.evaluate_input_read(
        api.StructuredAuditLog(()), objects.input_record_id, objects.input,
        objects.executor, objects.read_authorization, objects.incident_identifier,
    )
    _check_decision(api, first, release_state=api.ReleaseState.BLOCKED,
                    detail_code=INPUT_SUCCESS_CODE)
    first_expected = _expected_record(
        api, objects, action=api.Action.READ_INPUT, target_kind=api.TargetKind.INPUT_MANIFEST,
        target_id=objects.input.input_id,
        manifest_identity=api.input_manifest_identity(objects.input),
        actor=objects.executor, authorization=objects.read_authorization,
        release_state=api.ReleaseState.BLOCKED, cumulative_state=None, recipient=None,
        record_id=objects.input_record_id,
    )
    _check_linkage(api, first, first_expected, ())
    evaluations = [first]
    if not release_prerequisites_present(api, objects):
        return EXIT_NORMAL_NO_RELEASE, evaluations, "INPUT_LINKED_RELEASE_NOT_ATTEMPTED"
    second = harness.evaluate_output_release(
        first.log, objects.output_record_id, objects.output, objects.recipient,
        objects.approver, objects.release_authorization, objects.ledger,
        objects.incident_identifier,
    )
    _check_decision(api, second, release_state=api.ReleaseState.AUTHORIZED,
                    detail_code=OUTPUT_SUCCESS_CODE)
    second_expected = _expected_record(
        api, objects, action=api.Action.RELEASE_OUTPUT,
        target_kind=api.TargetKind.OUTPUT_MANIFEST, target_id=objects.output.output_id,
        manifest_identity=api.output_manifest_identity(objects.output),
        actor=objects.approver, authorization=objects.release_authorization,
        release_state=api.ReleaseState.AUTHORIZED,
        cumulative_state=api.CumulativeDisclosureState.CLEAR, recipient=objects.recipient,
        record_id=objects.output_record_id,
    )
    _check_linkage(api, second, second_expected, first.log.records)
    evaluations.append(second)
    return EXIT_RELEASE_AUTHORIZED, evaluations, "INPUT_AND_RELEASE_LINKED"


def build_result(api, objects, evaluations, linkage) -> dict:
    """Exactly the fifteen structural elements; codes outside the accepted scope stop."""
    decisions = [item.decision for item in evaluations]
    for decision in decisions:
        if decision.detail_code not in objects.accepted_codes:
            raise StopOperation("DETAIL_CODE_OUTSIDE_ACCEPTED_SCOPE")
    bindings = [[objects.executor.actor_id, objects.executor.declared_role.value]]
    if len(evaluations) == 2:
        bindings.append([objects.approver.actor_id, objects.approver.declared_role.value])
        bindings.append([objects.recipient.actor_id, objects.recipient.declared_role.value])
    result = {
        "validation_state": [d.validation_state.value for d in decisions],
        "permit_or_deny_state": [d.permit_or_deny_state.value for d in decisions],
        "quarantine_state": [d.quarantine_state.value for d in decisions],
        "release_state": [d.release_state.value for d in decisions],
        "completion_state": [d.completion_state.value for d in decisions],
        "stop_reason": [None if d.stop_reason is None else d.stop_reason.value for d in decisions],
        "detail_code": [d.detail_code for d in decisions],
        "input_manifest_reference": api.input_manifest_identity(objects.input),
        "output_manifest_reference": api.output_manifest_identity(objects.output),
        "policy_reference": api.harness_policy_identity(objects.policy),
        "construction_authority_reference": objects.binding.owner_authority_sha,
        "execution_authority_reference": objects.execution_authority_sha,
        "actor_role_bindings": bindings,
        "acknowledged_log_record_references": [item.log_record.record_id for item in evaluations],
        "structural_linkage_status": linkage,
    }
    if tuple(sorted(result)) != tuple(sorted(RESULT_ELEMENTS)):
        raise StopOperation("RESULT_ELEMENT_SET_MISMATCH")
    return result


# ------------------------------------------------------------------- audit hook

def audit_decision(event, args, *, allowed_reads, blocked_caches, write_partial,
                   final_path, stdlib_root) -> str:
    """Return ALLOW or a DENY_* reason for one audit event (pure, testable)."""
    if event.startswith(("socket.", "http.client.", "urllib.", "ftplib.", "smtplib.",
                         "imaplib.", "poplib.", "nntplib.", "telnetlib.", "webbrowser.")):
        return "DENY_NETWORK"
    if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
                 "os.exec", "os.fork", "os.forkpty", "os.spawn", "os.startfile", "pty.spawn"):
        return "DENY_SUBPROCESS"
    if event == "os.link":
        src, dst = str(args[0]), str(args[1])
        return "ALLOW" if (src, dst) == (write_partial, final_path) else "DENY_LINK"
    if event in ("os.remove", "os.unlink"):
        return "ALLOW" if str(args[0]) == write_partial else "DENY_REMOVE"
    if event in ("os.rename", "os.replace", "os.rmdir", "os.mkdir", "os.chmod", "os.chown",
                 "os.symlink", "os.truncate", "shutil.rmtree"):
        return "DENY_MUTATION"
    if event != "open":
        return "ALLOW"
    path, mode, flags = args
    if not isinstance(path, (str, bytes)):
        return "DENY_FD_OPEN"
    text = path.decode() if isinstance(path, bytes) else path
    write_flags = 1 | 2 | 64 | 512 | 1024
    writing = (flags is not None and flags & write_flags) or (mode and any(x in mode for x in "wax+"))
    if writing:
        return "ALLOW" if text == write_partial else "DENY_WRITE"
    if text in blocked_caches:
        return "DENY_CACHE"
    if text in allowed_reads:
        return "ALLOW"
    if text.startswith(stdlib_root + "/") and "site-packages" not in text \
            and text.endswith((".py", ".pyc", ".so")):
        return "ALLOW"
    return "DENY_READ"


def _install_audit_hook(repo_root: Path, output_directory: str, result_name: str):
    import importlib.util
    import sysconfig
    from research.weather_forward.v4.a2_operation.common.bounded_output import partial_name
    harness_dir = repo_root.joinpath(*HARNESS_PACKAGE_PATH)
    sources = [harness_dir / name for name in HARNESS_PRODUCTION_FILES]
    sources += [repo_root.joinpath(*parts) for parts in OPERATION_SOURCE_FILES]
    allowed = frozenset(str(path.resolve()) for path in sources)
    caches = frozenset(str(Path(importlib.util.cache_from_source(p)).resolve()) for p in allowed)
    stdlib_root = str(Path(sysconfig.get_path("stdlib")).resolve())
    out_dir = Path(output_directory).resolve()
    write_partial = str(out_dir / partial_name(result_name))
    final_path = str(out_dir / result_name)

    def normalized(value):
        if isinstance(value, bytes):
            value = value.decode()
        return os.path.realpath(value) if isinstance(value, str) else value

    def hook(event, args):
        if event == "open":
            args = (normalized(args[0]), args[1], args[2])
        elif event in ("os.link", "os.remove", "os.unlink") and args:
            args = tuple(normalized(item) if index < 2 else item
                         for index, item in enumerate(args))
        verdict = audit_decision(event, args, allowed_reads=allowed, blocked_caches=caches,
                                 write_partial=write_partial, final_path=final_path,
                                 stdlib_root=stdlib_root)
        if verdict != "ALLOW":
            raise PermissionError(verdict)

    sys.addaudithook(hook)


# ------------------------------------------------------------------------ main

def run(argv) -> int:
    if len(argv) != 4 or argv[0] != "--repo-root" or argv[2] != "--context":
        return EXIT_STOP
    repo_root = Path(argv[1]).resolve()
    try:
        context = validate_context(json.loads(Path(argv[3]).read_text(encoding="ascii")))
        harness_dir = repo_root.joinpath(*HARNESS_PACKAGE_PATH)
        verify_harness_blobs(lambda name: (harness_dir / name).read_bytes(),
                             context["harness_source_blobs"])
    except (ContextError, StopOperation, ValueError, UnicodeDecodeError):
        return EXIT_STOP
    sys.path.insert(0, str(repo_root))
    _install_audit_hook(repo_root, context["output_directory"], context["result_file_name"])
    from research.weather_forward.v4 import a2_harness as api
    from research.weather_forward.v4.a2_operation.common import bounded_output
    from research.weather_forward.v4.a2_operation.identity.identity_via_harness import build_object
    try:
        objects = build_objects(api, build_object, context)
        code, evaluations, linkage = execute(api, objects)
        payload = bounded_output.encode_result(build_result(api, objects, evaluations, linkage))
    except (ContextError, StopOperation, ValueError):
        return EXIT_STOP
    try:
        bounded_output.write_bounded(context["output_directory"], context["result_file_name"],
                                     payload)
    except bounded_output.OutputLimitExceeded:
        return EXIT_OUTPUT_LIMIT
    return code


def guarded(function, *args) -> int:
    """Map any escaping exception to EXIT_EXCEPTION without printing anything."""
    try:
        code = function(*args)
    except BaseException:  # noqa: BLE001 - no traceback may reach stdout/stderr
        return EXIT_EXCEPTION
    if code not in (EXIT_NORMAL_NO_RELEASE, EXIT_RELEASE_AUTHORIZED, EXIT_STOP,
                    EXIT_EXCEPTION, EXIT_OUTPUT_LIMIT):
        return EXIT_EXCEPTION
    return code


if __name__ == "__main__":
    sys.exit(guarded(run, sys.argv[1:]))
