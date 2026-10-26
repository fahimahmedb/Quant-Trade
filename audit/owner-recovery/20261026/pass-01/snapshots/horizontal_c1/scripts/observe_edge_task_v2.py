#!/usr/bin/env python3
"""Observe one producer task from exact local Git objects; no fetch or writes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.research_os.github_state import PREFIX, SHA, StateUnavailable
from research.research_os.worker_preflight import git_blob_sha
from research.research_os.expansion.edge_observation_reader_v2 import (
    EdgeObservationReadError, observe_edge_task, task_observation_paths,
)


class LocalGitObservationSnapshot:
    """Read adapter for the existing snapshot protocol, not a state backend."""
    def __init__(self, repository, commit, task_id):
        paths = task_observation_paths(task_id)
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            raise EdgeObservationReadError("EXACT_LOCAL_COMMIT_REQUIRED")
        self.repository = Path(repository)
        self.head = self._git("rev-parse", "--verify", commit + "^{commit}").decode().strip()
        if self.head != commit:
            raise EdgeObservationReadError("LOCAL_COMMIT_MISMATCH")
        # Only tree metadata is indexed for sources and receipts. Source content
        # is never read, and the collector selects only its bound last receipt.
        self.blobs = {}
        entries = self._git("ls-tree", "-rz", commit, "--", *paths,
                            PREFIX + f"receipts/{task_id}/", PREFIX + "sources/")
        for entry in filter(None, entries.split(b"\0")):
            info, name = entry.split(b"\t", 1)
            mode, kind, blob = info.decode().split()
            if mode not in ("100644", "100755") or kind != "blob":
                raise EdgeObservationReadError("NON_REGULAR_OBSERVATION_FILE")
            self.blobs[name.decode()] = blob

    def _git(self, command, *arguments):
        result = subprocess.run(["git", "-c", "maintenance.auto=false", "-C", str(self.repository),
                                 command, *arguments], capture_output=True, timeout=30)
        if result.returncode:
            raise StateUnavailable("LOCAL_GIT_READ_FAILED:" + command)
        return result.stdout

    def read(self, path):
        if path not in self.blobs:
            raise StateUnavailable("LOCAL_OBSERVATION_PATH_NOT_PRESENT")
        raw = self._git("cat-file", "blob", self.blobs[path])
        if git_blob_sha(raw) != self.blobs[path]:
            raise StateUnavailable("LOCAL_OBSERVATION_BLOB_MISMATCH")
        return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--commit", required=True, help="Full 40-character local Git commit SHA")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--catalog", type=Path, help="Explicit local declared_routes/validated_adapters JSON")
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text()) if args.catalog else {}
        if not isinstance(catalog, dict) or set(catalog) - {"declared_routes", "validated_adapters"}:
            raise EdgeObservationReadError("EXPLICIT_ACQUISITION_CATALOG_REQUIRED")
        snapshot = LocalGitObservationSnapshot(args.repository, args.commit, args.task_id)
        result = observe_edge_task(snapshot, args.task_id, **catalog)
    except (ValueError, RuntimeError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, "OBSERVATION_FAILED:" + str(exc) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
