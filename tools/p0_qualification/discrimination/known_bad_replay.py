"""Replay one exact P0 discriminant against a known-bad launcher blob.

Both launchers are read from exact Git objects and materialized only in a
temporary directory. Required result: KNOWN_BAD -> RED and FROZEN_V4 -> GREEN.
This module neither checks out nor modifies the historical branch.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.evidence import EvidenceRecord, Report, verified_input_tree_digest  # noqa: E402
from common import launcher_loader  # noqa: E402

KNOWN_BAD_SHA = "2da079d8ad75c69eb3fc2990c512735cb4bdc02b"
FROZEN_V4_SHA = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
LAUNCHER_PATH = "deploy/quant_sec_supervisor.py"
UNIT_PATH = "deploy/quant-sec-capture.service"
ARTIFACT = (
    REPO_ROOT / "tools" / "p0_qualification" / "evidence"
    / "discrimination" / "known_bad_replay.json"
)
REPRODUCE_COMMAND = (
    "PYTHONPATH=. python3 -m "
    "tools.p0_qualification.discrimination.known_bad_replay"
)

EXEC_START_BEFORE = (
    "{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I "
    "/opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying ; "
    "ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; "
    "code=(null) ; status=0/0 }"
)
EXEC_START_AFTER = (
    "{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I "
    "/opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying ; "
    "ignore_errors=no ; start_time=[Sun 2026-09-20 18:42:33 UTC] ; "
    "stop_time=[Sun 2026-09-20 19:58:25 UTC] ; pid=48213 ; code=exited ; "
    "status=0/SUCCESS }"
)


@dataclass(frozen=True)
class ReplayResult:
    commit: str
    launcher_blob_sha256: str
    unit_blob_sha256: str
    before_accepted: bool
    after_accepted: bool
    stable_across_transient_observations: bool
    semantic_drift_detected: bool
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "commit": self.commit,
            "launcher_blob_sha256": self.launcher_blob_sha256,
            "unit_blob_sha256": self.unit_blob_sha256,
            "before_accepted": self.before_accepted,
            "after_accepted": self.after_accepted,
            "stable_across_transient_observations":
                self.stable_across_transient_observations,
            "semantic_drift_detected": self.semantic_drift_detected,
            "error": self.error,
        }


def _git_blob(commit: str, path: str) -> bytes:
    """Read one exact Git blob without checking out its branch."""
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        error = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"GIT_BLOB_UNAVAILABLE:{commit}:{path}:{error}")
    return completed.stdout


def _shown(fragment: Path, exec_start: str) -> SimpleNamespace:
    fields = {
        "FragmentPath": str(fragment),
        "DropInPaths": "",
        "ExecStart": exec_start,
        "WorkingDirectory": "/opt/quant",
        "Restart": "on-failure",
        "RestartUSec": "15s",
        "StartLimitIntervalUSec": "10min",
        "StartLimitBurst": "5",
        "KillMode": "control-group",
        "KillSignal": "15",
        "TimeoutStopUSec": "30s",
        "EnvironmentFiles": "/etc/quant/sec-capture.env (ignore_errors=no)",
    }
    stdout = "\n".join(f"{key}={value}" for key, value in fields.items()) + "\n"
    return SimpleNamespace(returncode=0, stdout=stdout, stderr="")


def _digest(launcher, root: Path, fragment: Path, exec_start: str) -> str:
    with mock.patch.object(
        launcher.subprocess, "run", return_value=_shown(fragment, exec_start)
    ):
        return launcher._effective_systemd_definition(root)


def _replay_commit(commit: str, label: str) -> ReplayResult:
    launcher_blob = _git_blob(commit, LAUNCHER_PATH)
    unit_blob = _git_blob(commit, UNIT_PATH)
    launcher_hash = "sha256:" + hashlib.sha256(launcher_blob).hexdigest()
    unit_hash = "sha256:" + hashlib.sha256(unit_blob).hexdigest()

    with tempfile.TemporaryDirectory(prefix=f"quant-p0-{label}-") as directory:
        root = Path(directory) / "root"
        source = Path(directory) / "blobs" / "quant_sec_supervisor.py"
        fragment = root / UNIT_PATH
        source.parent.mkdir(parents=True)
        fragment.parent.mkdir(parents=True)
        source.write_bytes(launcher_blob)
        fragment.write_bytes(unit_blob)
        with mock.patch.object(launcher_loader, "LAUNCHER_SOURCE", source):
            launcher = launcher_loader.load_launcher(
                f"p0_known_bad_replay_{label}")
        try:
            before = _digest(launcher, root, fragment, EXEC_START_BEFORE)
            after = _digest(launcher, root, fragment, EXEC_START_AFTER)
            drifted_exec = EXEC_START_AFTER.replace(
                "path=/usr/bin/python3 ;", "path=/usr/bin/python3.11 ;"
            )
            try:
                drifted = _digest(launcher, root, fragment, drifted_exec)
            except RuntimeError:
                semantic_drift_detected = True
            else:
                semantic_drift_detected = drifted != after
            return ReplayResult(
                commit, launcher_hash, unit_hash, True, True,
                before == after, semantic_drift_detected,
            )
        except Exception as exc:
            return ReplayResult(
                commit, launcher_hash, unit_hash, False, False, False, False,
                f"{type(exc).__name__}:{exc}",
            )


def run() -> tuple[dict[str, object], bool]:
    known_bad = _replay_commit(KNOWN_BAD_SHA, "known-bad")
    frozen_v4 = _replay_commit(FROZEN_V4_SHA, "frozen-v4")

    known_bad_red = (
        known_bad.before_accepted
        and known_bad.after_accepted
        and not known_bad.stable_across_transient_observations
    )
    frozen_v4_green = (
        frozen_v4.before_accepted
        and frozen_v4.after_accepted
        and frozen_v4.stable_across_transient_observations
        and frozen_v4.semantic_drift_detected
    )
    discriminating = known_bad_red and frozen_v4_green

    report = Report(
        gate="HISTORICAL_KNOWN_BAD_REPLAY",
        exact_sha=FROZEN_V4_SHA,
        generated_at_utc="2026-09-21T00:00:00+00:00",
    )
    report.add(EvidenceRecord(
        property_name="known_bad_replay:transient_execstart_digest_defect",
        classification="FACT" if known_bad_red else "UNKNOWN",
        defect_class="REAL_DEFECT" if known_bad_red else "TEST_DEFECT",
        domain="REPOSITORY",
        detail=(
            "Exact pre-fix launcher reproduced transient-observation digest movement."
            if known_bad_red else "Required historical RED was not reproduced."
        ),
        exact_sha=KNOWN_BAD_SHA,
        reproduce_command=REPRODUCE_COMMAND,
        residual=(
            "None; sensitivity evidence against a known historical defect."
            if known_bad_red else "REPOSITORY: discriminant sensitivity unproven."
        ),
    ))
    report.add(EvidenceRecord(
        property_name="known_bad_replay:frozen_v4_transient_digest_stability",
        classification="FACT" if frozen_v4_green else "UNKNOWN",
        defect_class="NON_ISSUE" if frozen_v4_green else "REAL_DEFECT",
        domain="REPOSITORY",
        detail=(
            "Frozen V4 stayed stable and detected semantic executable-path drift."
            if frozen_v4_green
            else "Frozen V4 failed the discriminant or positive control."
        ),
        exact_sha=FROZEN_V4_SHA,
        reproduce_command=REPRODUCE_COMMAND,
        residual=(
            "TARGET_HOST: repository replay does not replace physical host evidence."
            if frozen_v4_green
            else "REPOSITORY: preserve RED evidence; do not repair production here."
        ),
    ))
    report.add(EvidenceRecord(
        property_name="known_bad_replay:discrimination_power",
        classification="FACT" if discriminating else "UNKNOWN",
        defect_class="NON_ISSUE" if discriminating else "MISSING_PROOF",
        domain="REPOSITORY",
        detail=(
            "KNOWN_BAD -> RED and FROZEN_V4 -> GREEN."
            if discriminating
            else "Exact historical and V4 blobs were not distinguished."
        ),
        exact_sha=FROZEN_V4_SHA,
        reproduce_command=REPRODUCE_COMMAND,
        residual=(
            "None for this repository discriminant."
            if discriminating
            else "REPOSITORY: historical discrimination remains unproven."
        ),
    ))

    input_paths = (
        "tools/p0_qualification/common/evidence.py",
        "tools/p0_qualification/common/launcher_loader.py",
        "tools/p0_qualification/discrimination/__init__.py",
        "tools/p0_qualification/discrimination/known_bad_replay.py",
        "tests/test_astra_pre_t0.py",
    )
    report.body.update({
        "known_bad_sha": KNOWN_BAD_SHA,
        "frozen_v4_sha": FROZEN_V4_SHA,
        "historical_branch_modified": False,
        "fixture_source": (
            "tests.test_astra_pre_t0."
            "Phase8EffectiveUnitDigestStabilityCampaign"
        ),
        "historical_real_defects_reproduced": 1 if known_bad_red else 0,
        "frozen_v4_real_defects": 0 if frozen_v4_green else 1,
        "known_bad_result": "RED" if known_bad_red else "NOT_RED",
        "frozen_v4_result": "GREEN" if frozen_v4_green else "NOT_GREEN",
        "discriminating": discriminating,
        "known_bad": known_bad.to_dict(),
        "frozen_v4": frozen_v4.to_dict(),
        "verified_input_tree_digest": verified_input_tree_digest(input_paths),
        "verified_input_paths": list(input_paths),
        "claims": {
            "gate_a_v4_pass": "NOT_CLAIMED_BY_BUILDER",
            "target_host_ready": "NOT_CLAIMED_BY_BUILDER",
            "p14d_amendment": "NOT_CLAIMED_BY_BUILDER",
            "t0": "NOT_DECLARED",
            "real_capital_authorized": False,
        },
    })
    payload = report.write(ARTIFACT)
    return payload, discriminating


def main() -> int:
    payload, passed = run()
    print(json.dumps({
        "artifact": str(ARTIFACT.relative_to(REPO_ROOT)),
        "known_bad_sha": KNOWN_BAD_SHA,
        "known_bad_result": payload["body"]["known_bad_result"],
        "frozen_v4_sha": FROZEN_V4_SHA,
        "frozen_v4_result": payload["body"]["frozen_v4_result"],
        "discriminating": passed,
        "report_digest": payload["report_digest"],
    }, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
