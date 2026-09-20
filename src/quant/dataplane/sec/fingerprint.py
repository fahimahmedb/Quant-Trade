"""ACQUISITION_CRITICAL_FINGERPRINT V1.

``governance/P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md`` freezes what this
module computes and why. The error being prevented is an acquisition-semantic
change crossing the fourteen-day observation window without resetting ``t0`` -
and the point the governance makes is that such a change need not touch
``discovery_poll_seconds``. Retry behaviour, timeouts, error classification,
pagination, continuity, backlog drain, restart behaviour or launcher policy can
all change the expected sequence of acquisition actions on their own.

So the fingerprint is not a configuration hash. It is

    ACQUISITION_CRITICAL_FINGERPRINT = sha256(canonical_json(manifest_v1))

over four things: the source of the modules that *produce* acquisition
behaviour, the effective runtime policy, the supervisor semantics that control
when the process runs at all, and this schema's own version.

**Complete by construction.** The second frozen blocker,
``INCOMPLETE_CRITICAL_POLICY_SERIALIZATION``, was that ``to_dict()`` - a
telemetry serializer with a different purpose - silently omitted effective
policy fields, so two different acquisition policies could share a fingerprint.
The repair is not a longer hand-maintained list. Every field of
``SecAccessPolicy`` must carry exactly one classification here, the three
classification sets must be disjoint, and their union must equal the dataclass's
field set. That is checked *at generation time*, not only in tests: adding a
field without classifying it raises ``UnclassifiedPolicyField`` and no
fingerprint is produced.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import platform
import ssl
from pathlib import Path
from typing import Any

from .policy import DISCOVERY_ENDPOINT_CLASS, FILING_ENDPOINT_CLASS, SecAccessPolicy
from .discovery import daily_index_path, discovery_path
from .transport import SEC_HOST


#: Bumping this is itself an acquisition-critical change: it alters the manifest.
FINGERPRINT_SCHEMA_VERSION = "acquisition_critical_fingerprint/v1"

#: Query-construction version. Change it whenever the shape of a request the
#: SEC actually receives changes, even if no policy value moves.
QUERY_CONSTRUCTION_VERSION = "edgar_getcurrent_atom+daily_master_index/v2"

#: Module roots frozen by the governance document, relative to the repo root.
#: ``clock.py`` is included in full: the governance's conservative V1 rule,
#: because the acquisition scheduling path still lives in that mixed-purpose
#: module. Narrowing this is permitted only before the first qualifying t0.
ACQUISITION_CRITICAL_MODULES: tuple[str, ...] = (
    "src/quant/dataplane/sec/policy.py",
    "src/quant/dataplane/sec/budget.py",
    "src/quant/dataplane/sec/calendar.py",
    "src/quant/dataplane/sec/transport.py",
    "src/quant/dataplane/sec/discovery.py",
    "src/quant/dataplane/sec/collector.py",
    "src/quant/dataplane/sec/store.py",
    "src/quant/dataplane/sec/visibility.py",
    "src/quant/dataplane/sec/timebase.py",
    "src/quant/dataplane/sec/scheduler.py",
    "src/quant/dataplane/sec/supervisor.py",
    "src/quant/dataplane/sec/fingerprint.py",
    # The retrospective audit is included deliberately. It cannot change what
    # the collector does, so a narrow reading would leave it out - but it
    # decides whether a window is accountable, and a weakened audit could mask
    # exactly the hole the window exists to detect. Membership may only be
    # narrowed before the first qualifying t0, so the conservative choice now
    # is the one that stays available later.
    "src/quant/dataplane/sec/audit.py",
    "src/quant/clock.py",
    # Shared runtime primitives reached on the acquisition path.  Their names do
    # not contain "sec", but changing their persistence/path/event behaviour can
    # change acquisition or the proof of acquisition.
    "src/quant/state.py",
    "src/quant/paths.py",
    "src/quant/events.py",
    "src/quant/dataplane/sec/version.py",
    # Published firewall projections and the scripts that generate/check them.
    # A weaker projection or verifier can manufacture a false pre-t0 proof.
    "src/quant/status/render.py",
    "src/quant/status/brief.py",
    "scripts/status_artifacts.py",
    "scripts/verify_p0.py",
    ".github/workflows/sec-p0-pre-t0-gate.yml",
    # The service entry point. `sec-serve` binds the clock's wake cadence into
    # system.serve(), so it decides how often a due poll is noticed - acquisition
    # timing, in a file no source digest covered until now. Membership may only be
    # narrowed before the first qualifying t0, so it is added while that is still
    # possible rather than left for an incident to find.
    "scripts/quant.py",
)

# --- policy field classification -------------------------------------------
# Exactly one of these three sets must contain each SecAccessPolicy field.

#: Serialized directly, in canonical form.
INCLUDE_CANONICAL: frozenset[str] = frozenset({
    "discovery_poll_seconds",
    "max_concurrency",
    "max_requests_per_second",
    "allow_burst",
    "connect_timeout_seconds",
    "read_timeout_seconds",
    "idle_reuse_seconds",
    "total_deadline_seconds",
    "backoff_schedule_seconds",
    "jitter_ratio",
    "rate_limit_cooldown_seconds",
    "forbidden_cooldown_seconds",
    "discovery_page_size",
    "max_discovery_pages_per_poll",
    "filings_per_drain",
    "accept_encoding",
    "max_response_bytes",
})

#: Serialized as a deterministic semantic transform rather than a raw value.
TRANSFORM_CANONICAL: frozenset[str] = frozenset({
    "user_agent",
})

#: Permitted only with a frozen rationale showing the field cannot alter request
#: timing, request shape, source identity, response acceptance, retry/failure
#: classification, backlog drain, discovery/coverage or firewall semantics.
EXPLICITLY_NONCRITICAL: dict[str, str] = {
    "sources": (
        "Documentation provenance only: the URLs and revision dates of the SEC "
        "fair-access pages consulted before t0. It is recorded in the manifest "
        "as a separate provenance member and is reproduced on telemetry, but it "
        "is never read at runtime - no request timing, request shape, response "
        "acceptance, retry classification, drain order, discovery/coverage rule "
        "or firewall decision consults it. Re-checking the SEC documentation "
        "and recording a newer revision date must not reset t0; changing an "
        "actual limit in response to that re-check moves a field in "
        "INCLUDE_CANONICAL and does reset it."
    ),
}


class UnclassifiedPolicyField(RuntimeError):
    """A SecAccessPolicy field carries no classification, so no fingerprint.

    This is the defence the governance asks for against a future policy field
    silently escaping the fingerprint. It fails generation, not just tests.
    """


class PolicyClassificationInvalid(RuntimeError):
    """The classification sets overlap or do not cover the dataclass."""


def policy_field_names() -> frozenset[str]:
    return frozenset(field.name for field in dataclasses.fields(SecAccessPolicy))


def verify_policy_classification() -> None:
    """POLICY_FIELD_SET == INCLUDE ∪ TRANSFORM ∪ NONCRITICAL, pairwise disjoint."""
    noncritical = frozenset(EXPLICITLY_NONCRITICAL)
    pairs = (("INCLUDE_CANONICAL", INCLUDE_CANONICAL, "TRANSFORM_CANONICAL", TRANSFORM_CANONICAL),
             ("INCLUDE_CANONICAL", INCLUDE_CANONICAL, "EXPLICITLY_NONCRITICAL", noncritical),
             ("TRANSFORM_CANONICAL", TRANSFORM_CANONICAL, "EXPLICITLY_NONCRITICAL", noncritical))
    for left_name, left, right_name, right in pairs:
        overlap = left & right
        if overlap:
            raise PolicyClassificationInvalid(
                f"{left_name} and {right_name} both claim: {sorted(overlap)}")
    classified = INCLUDE_CANONICAL | TRANSFORM_CANONICAL | noncritical
    actual = policy_field_names()
    unclassified = actual - classified
    if unclassified:
        raise UnclassifiedPolicyField(
            f"SecAccessPolicy fields without a fingerprint classification: "
            f"{sorted(unclassified)}. Add each to INCLUDE_CANONICAL, "
            f"TRANSFORM_CANONICAL, or EXPLICITLY_NONCRITICAL with a rationale.")
    stale = classified - actual
    if stale:
        raise PolicyClassificationInvalid(
            f"classified fields that no longer exist on SecAccessPolicy: {sorted(stale)}")


def requester_identity_binding(user_agent: str) -> str:
    """Stable non-plaintext binding of the declared SEC identity.

    The governance requires the identity to be bound rather than omitted, but
    the contact address must not be committed. A digest changes when the
    declared identity changes and reveals nothing about it.
    """
    return "sha256:" + hashlib.sha256(user_agent.strip().encode("utf-8")).hexdigest()


def canonical_policy(policy: SecAccessPolicy) -> dict[str, Any]:
    """The dedicated fingerprint serialization. Never ``to_dict()``."""
    verify_policy_classification()
    canonical: dict[str, Any] = {}
    for name in sorted(INCLUDE_CANONICAL):
        value = getattr(policy, name)
        canonical[name] = list(value) if isinstance(value, tuple) else value
    canonical["requester_identity_binding"] = requester_identity_binding(policy.user_agent)
    return canonical


def canonical_json(payload: Any) -> str:
    """One rendering, so two identical manifests cannot differ as text."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def module_digests(root: Path) -> dict[str, str]:
    """Hash the runtime import closure conservatively.

    The current service entry imports QuantSystem, whose module imports research,
    desk, registry and learning packages at module load.  A change there can
    prevent acquisition from starting even if it never calls a SEC function.
    Until that topology is narrowed, name-based SEC membership is insufficient.
    """
    root = Path(root)
    members = set(ACQUISITION_CRITICAL_MODULES)
    for package in ("src/quant", "src/autonomous_research"):
        base = root / package
        if base.exists():
            members.update(str(path.relative_to(root))
                           for path in base.rglob("*.py")
                           if "__pycache__" not in path.parts)
    digests: dict[str, str] = {}
    for relative in sorted(members):
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(
                f"acquisition-critical module missing from the fingerprint root: {relative}")
        digests[relative] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def build_manifest(policy: SecAccessPolicy, *, root: Path,
                   supervisor: dict[str, Any] | None = None,
                   environ: dict[str, str] | None = None) -> dict[str, Any]:
    """The deterministic manifest the fingerprint is taken over.

    Everything in here can change the expected sequence of acquisition actions.
    Nothing in here is a wall-clock value, a path, a hostname of this machine or
    anything else that would make two identical deployments differ.
    """
    from .supervisor import supervisor_manifest

    return {
        "schema": FINGERPRINT_SCHEMA_VERSION,
        "code": module_digests(root),
        "runtime": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "openssl": ssl.OPENSSL_VERSION,
        },
        "policy": canonical_policy(policy),
        "request_shape": {
            "host": SEC_HOST,
            "query_construction_version": QUERY_CONSTRUCTION_VERSION,
            "discovery_endpoint_class": DISCOVERY_ENDPOINT_CLASS,
            # EDGAR matches ``type`` by prefix, so the authoritative Form-4
            # selection is local. Frozen here because changing which side
            # decides changes what gets captured.
            "server_filter_semantics": "prefix_match_not_exact",
            "authoritative_form_selection": "local",
            "filing_endpoint_class": FILING_ENDPOINT_CLASS,
            # The literal request lines, so a change to query construction moves
            # the fingerprint even if no policy value and no module body did.
            "discovery_path_template": discovery_path(0, policy.discovery_page_size),
            "daily_index_path_template": daily_index_path(__import__("datetime").date(2026, 1, 2)),
        },
        "policy_classification": {
            "include_canonical": sorted(INCLUDE_CANONICAL),
            "transform_canonical": sorted(TRANSFORM_CANONICAL),
            "explicitly_noncritical": sorted(EXPLICITLY_NONCRITICAL),
        },
        "supervisor": supervisor or supervisor_manifest(root, environ),
    }


def compute_fingerprint(manifest: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(manifest).encode("utf-8")).hexdigest()


def acquisition_critical_fingerprint(policy: SecAccessPolicy, *, root: Path,
                                     supervisor: dict[str, Any] | None = None,
                                     environ: dict[str, str] | None = None) -> str:
    return compute_fingerprint(build_manifest(policy, root=root, supervisor=supervisor,
                                              environ=environ))
