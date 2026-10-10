"""Read-only admission checks for one immutable legacy bundle; never import or launch it."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .engine import budget_check, timestamp
from .seed import BRANCH
from .store import Refused

FROZEN_COMMIT = "e42d4924a33efa78bab97939d654424cc1501fb8"
FREEZE_SHA256 = "c891771ddc74adeae95b5492f708ad1c3cc07eca92da78ffe5b5346570d71de2"
PREFIX = "research/edge_search/eurusd_range_grid/"
QUESTION = "build:eurusd-technical-grid:legacy-authority-bridge"


def _git(repository, args, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise Refused("Legacy preflight wall-time exhausted")
    try:
        return subprocess.run(["git", "--no-pager", "-C", str(repository), *args],
            capture_output=True, check=True, timeout=min(5, remaining)).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise Refused("Pinned Git metadata unavailable; no fetch or legacy launch attempted") from exc


def inspect_eurusd(lab, repository, claim_id):
    cpu_start, wall_start = time.process_time(), time.monotonic()
    with lab.store.lock():
        control = lab.store.control()
        if control["paused"]:
            raise Refused("PAUSED: no legacy metadata read")
        state = lab.store.read()
        budget_check(state, control)
    question = state["decisions"].get(QUESTION, {})
    if (question.get("status") != "RESEARCHING" or not claim_id
            or question.get("claim_id") != claim_id):
        raise Refused("Exact construction claim required before legacy metadata")
    if (datetime.now(timezone.utc) - timestamp(question["claimed_at"])).total_seconds() > question["lease_seconds"]:
        raise Refused("Expired claim: reconcile saved receipt; do not repeat preflight")
    deadline = wall_start + control["limits"]["job_wall_seconds"]
    ceiling, consumed = control["limits"]["metadata_bytes_per_tick"], 0

    def blob(ref, path):
        nonlocal consumed
        spec = ref + ":" + path
        size = int(_git(repository, ["cat-file", "-s", spec], deadline))
        if size < 0 or consumed + size > ceiling:
            raise Refused("Legacy metadata ceiling: stopped before body read")
        value = _git(repository, ["show", spec], deadline)
        if len(value) != size:
            raise Refused("Pinned Git blob size mismatch")
        consumed += size
        return value

    published = json.loads(blob("HEAD", "research/edge_lab/STATE.json"))
    published_control = json.loads(blob("HEAD", "research/edge_lab/CONTROL.json"))
    if published != state or published_control != control:
        raise Refused("Publish exact claim/control with CAS before preflight")
    frozen_bytes = blob(FROZEN_COMMIT, PREFIX + "freeze.json")
    if hashlib.sha256(frozen_bytes).hexdigest() != FREEZE_SHA256:
        raise Refused("Immutable legacy freeze mismatch")
    frozen = json.loads(frozen_bytes)
    for name, expected in frozen["files"].items():
        if Path(name).name != name:
            raise Refused("Legacy code path escaped pinned bundle")
        if hashlib.sha256(blob(FROZEN_COMMIT, PREFIX + name)).hexdigest() != expected:
            raise Refused("Immutable legacy file mismatch: " + name)
    manifest = json.loads(blob(FROZEN_COMMIT, PREFIX + "manifest.json"))
    runtime_ok = sys.version_info[:2] == (3, 12)
    timezone_ok = True
    for path, expected in frozen["runtime_data"].items():
        try:
            size = Path(path).stat().st_size
            if consumed + size > ceiling:
                raise Refused("Runtime metadata ceiling: stopped before body read")
            value = Path(path).read_bytes()
            if len(value) != size:
                raise Refused("Runtime metadata changed during preflight")
            consumed += size
            timezone_ok = timezone_ok and hashlib.sha256(value).hexdigest() == expected
        except OSError:
            timezone_ok = False
    permitted_ref = "refs/heads/" + BRANCH
    return {
        "schema": 1, "scope": "READ_ONLY_EXACT_LEGACY_PREFLIGHT",
        "claim_id": claim_id, "frozen_commit": FROZEN_COMMIT, "freeze_sha256": FREEZE_SHA256,
        "checks": {"bundle_identity_verified": True, "files_verified": len(frozen["files"]),
                   "python_minor_matches": runtime_ok, "timezone_matches": timezone_ok},
        "contract": {"reservation_ref": frozen["reservation_ref"],
                     "output": frozen["fixed_output"], "outcome_window": manifest["utc_outcome"],
                     "archive_jobs": len(manifest["archive_jobs"]),
                     "trial_accounting": manifest["trial_accounting"]},
        "permitted_publication_ref": permitted_ref,
        "original_ref_creation_within_scope": frozen["reservation_ref"] == permitted_ref,
        "launch_admitted": False, "outcome_access_authorized": False,
        "blockers": ["EXACT_LAUNCH_ADAPTER_NOT_ADMITTED", "FULL_WINDOW_RESOURCE_ENVELOPE_UNMEASURED",
                     "SOURCE_AND_PRIOR_OUTCOME_RECONCILIATION_REQUIRED",
                     "ORIGINAL_RESERVATION_REQUIRED; CREATION_OUTSIDE_LAB_BRANCH_SCOPE"],
        "limits": control["limits"],
        "observed_cost": {"metadata_body_bytes": consumed,
                          "cpu_seconds": time.process_time() - cpu_start,
                          "wall_seconds": time.monotonic() - wall_start,
                          "tokens": None, "network_bytes": 0, "paid_usd": 0},
        "limitations": "Local pinned metadata only; no fresh remote original-ref/outcome check, "
                        "capture read, historical cost authentication or execution. "
                        "Report cannot substitute for either original reservation or lab reserve/RUNNING CAS."}
