"""Lifecycle provenance supplied from outside the collector.

``BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md §5.2``: "A collector
process cannot authoritatively classify its own origin." The retrospective audit
needs to know whether a restart was scheduled, automatic, a deployment, or a human
intervention - and the last of those invalidates the observation window, so the
process with an interest in the answer must not supply it.

Blue's second finding was that the first version was still not authoritative
enough, in three ways, all fixed here.

**Absence of provenance is never SCHEDULED_START.** The earlier design derived
``MANUAL_START`` from an ``--manual`` flag, so a human who simply did not pass it
was recorded as a normal scheduled start. The default direction is now inverted: a
launch that cannot show service-manager provenance is ``MANUAL_START`` and is not
qualifying. Omission cannot buy a clean record; only a real service manager can.

**The supervisor's own restart is observable.** The supervisor records that it is
running, together with the invocation identity the service manager gave it. A new
supervisor that finds a previous one still marked running under a different
invocation knows the previous one died, and reports
``AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE`` rather than inheriting a clean
``SCHEDULED_START``.

**A service manager launch is not yet a reason.** ``INVOCATION_ID`` proves systemd
started the service; it says nothing about why. An operator typing
``systemctl restart quant-sec-capture`` therefore looked identical to a scheduled
start. The classification no longer accepts "systemd did it" as evidence of an
automatic action: it requires a positive reason, and falls to ``MANUAL_START``
otherwise. The two positive reasons a healthy service can be started for are a
host boot - visible because the kernel's boot id changed - and the very first
start of a deployment. Anything else on a cleanly stopped service is an operator,
and an automatic restart after a failure is only automatic while it is still
inside the restart window the unit declares; after that systemd has given up and
a new start is again an operator.

**Effective service timing is bound.** Wake cadence, termination controls and
restart pacing change the expected acquisition timeline without touching any
source file, so they are exported by the launcher and folded into the fingerprint
manifest. In qualifying mode they may not be overridden at all.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any


#: The frozen cause vocabulary, which §5 gives as a *minimum*. The supervisor
#: failure cause refines AUTOMATIC_RESTART_AFTER_FAILURE rather than replacing
#: it: both are automatic and neither is an operator intervention.
SCHEDULED_START = "SCHEDULED_START"
AUTOMATIC_RESTART_AFTER_FAILURE = "AUTOMATIC_RESTART_AFTER_FAILURE"
AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE = "AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE"
DEPLOYMENT_RESTART = "DEPLOYMENT_RESTART"
MANUAL_START = "MANUAL_START"
LIFECYCLE_CAUSES = (SCHEDULED_START, AUTOMATIC_RESTART_AFTER_FAILURE,
                    AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE, DEPLOYMENT_RESTART,
                    MANUAL_START)

#: Automatic causes, which do not invalidate an observation window on their own.
AUTOMATIC_CAUSES = frozenset({AUTOMATIC_RESTART_AFTER_FAILURE,
                              AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE,
                              DEPLOYMENT_RESTART, SCHEDULED_START})

#: Not a cause. The absence of one.
UNATTESTED = "LIFECYCLE_CAUSE_UNATTESTED"

#: Causes that invalidate an active observation window (§5.2 intervention rule).
INVALIDATING_CAUSES = frozenset({MANUAL_START, SCHEDULED_START, AUTOMATIC_RESTART_AFTER_SUPERVISOR_FAILURE})

BOOT_ID_ENV = "QUANT_SEC_BOOT_ID"
CAUSE_ENV = "QUANT_SEC_LIFECYCLE_CAUSE"
BOOT_AT_ENV = "QUANT_SEC_BOOT_AT_UTC"
SUPERVISOR_ENV = "QUANT_SEC_SUPERVISOR_ID"

#: Declared by the unit file, not by a shell. Present only when a service manager
#: launched the supervisor.
SERVICE_MANAGER_ENV = "QUANT_SEC_SERVICE_MANAGER"
#: systemd sets this per unit invocation; a hand-typed command does not have it.
INVOCATION_ID_ENV = "INVOCATION_ID"
#: Whether the launcher asserts this run is the qualifying observation service.
QUALIFYING_ENV = "QUANT_SEC_QUALIFYING_MODE"

#: Effective service configuration the launcher exports for the fingerprint.
#: Kernel-supplied identity of the current host boot. It changes on every boot
#: and an operator cannot omit it, which is what lets a boot-time start be told
#: apart from an operator restart.
HOST_BOOT_ID_PATH = "/proc/sys/kernel/random/boot_id"

SERVICE_POLL_SECONDS_ENV = "QUANT_SEC_SERVICE_POLL_SECONDS"
SERVICE_MAX_WAITS_ENV = "QUANT_SEC_SERVICE_MAX_WAITS"
SERVICE_RESTART_DELAY_ENV = "QUANT_SEC_SERVICE_RESTART_DELAY_SECONDS"
SERVICE_RESTART_BURST_ENV = "QUANT_SEC_SERVICE_RESTART_BURST_LIMIT"
EFFECTIVE_UNIT_DIGEST_ENV = "QUANT_SEC_EFFECTIVE_UNIT_DIGEST"

#: Service managers whose invocation identity is accepted as provenance.
RECOGNISED_SERVICE_MANAGERS = frozenset({"systemd"})

#: Service definition and launcher, digested into the acquisition fingerprint.
SERVICE_DEFINITION_FILES: tuple[str, ...] = (
    "deploy/quant-sec-capture.service",
    "deploy/quant_sec_supervisor.py",
)


def host_boot_id(path: str = HOST_BOOT_ID_PATH) -> str | None:
    """The kernel's identity for this host boot, or None where unavailable."""
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def service_manager_provenance(environ: dict[str, str] | None = None) -> dict[str, Any]:
    """Markers showing a service manager launched this process, not a shell.

    A human can of course export these deliberately - that is forgery, and no
    environment check prevents it. What this removes is the *omission* path, where
    simply not passing a flag produced a clean scheduled-start record.
    """
    source = os.environ if environ is None else environ
    declared = (source.get(SERVICE_MANAGER_ENV) or "").strip().lower()
    invocation_id = (source.get(INVOCATION_ID_ENV) or "").strip()
    recognised = declared in RECOGNISED_SERVICE_MANAGERS
    return {"service_manager": declared or None,
            "service_manager_recognised": recognised,
            "invocation_id": invocation_id or None,
            # Both halves are required: the unit declares which manager it is,
            # and the manager itself supplies a per-invocation identity.
            "service_managed": bool(recognised and invocation_id)}


def effective_service_configuration(environ: dict[str, str] | None = None) -> dict[str, Any]:
    """The launcher's effective timing/termination settings, for the fingerprint.

    Hashing source files does not distinguish two services started from the same
    code with different arguments, which was Blue's point. These values are what
    actually decide wake cadence, service lifetime and restart pacing.
    """
    source = os.environ if environ is None else environ

    def number(name: str) -> float | None:
        raw = (source.get(name) or "").strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    return {"poll_seconds": number(SERVICE_POLL_SECONDS_ENV),
            "max_waits": number(SERVICE_MAX_WAITS_ENV),
            "restart_delay_seconds": number(SERVICE_RESTART_DELAY_ENV),
            "restart_burst_limit": number(SERVICE_RESTART_BURST_ENV),
            "qualifying_mode": (source.get(QUALIFYING_ENV) or "").strip().lower()
                               in ("1", "true", "yes")}


def lifecycle_provenance(environ: dict[str, str] | None = None) -> dict[str, Any]:
    """What the launcher said about this process. Never what the process thinks."""
    source = os.environ if environ is None else environ
    declared = (source.get(CAUSE_ENV) or "").strip().upper()
    cause = declared if declared in LIFECYCLE_CAUSES else UNATTESTED
    managed = service_manager_provenance(source)
    service = effective_service_configuration(source)
    # A qualifying claim is only honoured when a recognised service manager
    # actually launched this process and the cause is externally attested.
    qualifying = bool(service["qualifying_mode"] and managed["service_managed"]
                      and cause != UNATTESTED)
    return {
        "boot_id": (source.get(BOOT_ID_ENV) or "").strip() or None,
        "lifecycle_cause": cause,
        "lifecycle_cause_declared": declared or None,
        "boot_at_utc": (source.get(BOOT_AT_ENV) or "").strip() or None,
        "supervisor_id": (source.get(SUPERVISOR_ENV) or "").strip() or None,
        "externally_attested": cause != UNATTESTED,
        "invalidates_observation_window": cause in INVALIDATING_CAUSES,
        "service_manager": managed["service_manager"],
        "service_managed": managed["service_managed"],
        "service_invocation_id": managed["invocation_id"],
        "qualifying_service_mode": qualifying,
        "effective_service_configuration": service,
    }


def supervisor_manifest(root: Path,
                        environ: dict[str, str] | None = None) -> dict[str, Any]:
    """Service definition digest, restart policy and effective invocation.

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
            "restart_policy": restart_policy(root),
            # Bound so two services from identical code with different runtime
            # arguments cannot share a fingerprint.
            "effective_service_invocation": effective_service_configuration(environ)}


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
