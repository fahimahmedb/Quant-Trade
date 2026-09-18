"""Lifecycle provenance supplied from outside the collector.

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2``: "A collector
process cannot authoritatively classify its own origin." The retrospective audit
needs to know whether a restart was scheduled, automatic after a failure, a
deployment, or a human intervention - and the last of those invalidates the
observation window, so the process with an interest in the answer is exactly the
process that must not supply it.

This module therefore only *reads* what the launcher put in the environment. If
the launcher supplied nothing, the cause is ``LIFECYCLE_CAUSE_UNATTESTED``,
which is an explicit provenance gap rather than a default of convenience. It is
not one of the four valid causes, and the pre-t0 readiness check treats it as
not ready.

It also digests the service definition and restart policy into the fingerprint,
because a launcher that restarts on a different schedule changes the expected
acquisition timeline just as surely as a changed poll interval.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any


#: The frozen cause vocabulary.
SCHEDULED_START = "SCHEDULED_START"
AUTOMATIC_RESTART_AFTER_FAILURE = "AUTOMATIC_RESTART_AFTER_FAILURE"
DEPLOYMENT_RESTART = "DEPLOYMENT_RESTART"
MANUAL_START = "MANUAL_START"
LIFECYCLE_CAUSES = (SCHEDULED_START, AUTOMATIC_RESTART_AFTER_FAILURE,
                    DEPLOYMENT_RESTART, MANUAL_START)

#: Not a cause. The absence of one.
UNATTESTED = "LIFECYCLE_CAUSE_UNATTESTED"

#: Causes that invalidate an active observation window (§5.2 intervention rule).
INVALIDATING_CAUSES = frozenset({MANUAL_START})

BOOT_ID_ENV = "QUANT_SEC_BOOT_ID"
CAUSE_ENV = "QUANT_SEC_LIFECYCLE_CAUSE"
BOOT_AT_ENV = "QUANT_SEC_BOOT_AT_UTC"
SUPERVISOR_ENV = "QUANT_SEC_SUPERVISOR_ID"

#: Service definition and launcher, digested into the acquisition fingerprint.
SERVICE_DEFINITION_FILES: tuple[str, ...] = (
    "deploy/quant-sec-capture.service",
    "deploy/quant_sec_supervisor.py",
)


def lifecycle_provenance(environ: dict[str, str] | None = None) -> dict[str, Any]:
    """What the launcher said about this process. Never what the process thinks."""
    source = os.environ if environ is None else environ
    declared = (source.get(CAUSE_ENV) or "").strip().upper()
    cause = declared if declared in LIFECYCLE_CAUSES else UNATTESTED
    return {
        "boot_id": (source.get(BOOT_ID_ENV) or "").strip() or None,
        "lifecycle_cause": cause,
        "lifecycle_cause_declared": declared or None,
        "boot_at_utc": (source.get(BOOT_AT_ENV) or "").strip() or None,
        "supervisor_id": (source.get(SUPERVISOR_ENV) or "").strip() or None,
        "externally_attested": cause != UNATTESTED,
        "invalidates_observation_window": cause in INVALIDATING_CAUSES,
    }


def supervisor_manifest(root: Path) -> dict[str, Any]:
    """Digest of the service definition plus its effective restart policy.

    A missing definition is recorded as missing rather than skipped: the
    fingerprint must differ between a deployment that has a supervisor and one
    that does not, because the expected acquisition timeline differs.
    """
    digests: dict[str, str] = {}
    for relative in sorted(SERVICE_DEFINITION_FILES):
        path = Path(root) / relative
        digests[relative] = ("sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                             if path.exists() else "ABSENT")
    return {"service_definition_digests": digests,
            "restart_policy": restart_policy(root)}


def restart_policy(root: Path) -> dict[str, Any]:
    """Parse the restart semantics out of the unit rather than restating them."""
    unit = Path(root) / "deploy" / "quant-sec-capture.service"
    if not unit.exists():
        return {"declared": False}
    wanted = ("Restart", "RestartSec", "StartLimitIntervalSec", "StartLimitBurst",
              "TimeoutStopSec")
    parsed: dict[str, str] = {}
    for line in unit.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() in wanted:
            parsed[key.strip()] = value.strip()
    return {"declared": True, **{key: parsed[key] for key in sorted(parsed)}}
