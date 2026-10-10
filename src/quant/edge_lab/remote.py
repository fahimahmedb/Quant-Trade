"""GitHub branch authority through ordinary fast-forward Git, never force push."""
import json
import hashlib
import subprocess
from pathlib import Path

from .seed import BRANCH
from .store import Refused, verify


class GitAuthority:
    def __init__(self, repository, directory):
        self.repo = Path(repository).resolve()
        self.directory = Path(directory).resolve()
        if self.repo not in self.directory.parents:
            raise Refused("Persistent state must be inside this checkout")
        self.relative = self.directory.relative_to(self.repo).as_posix()

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.repo, text=True, capture_output=True,
                                timeout=45)
        if result.returncode:
            # Never emit credentials, proxy settings or arbitrary git diagnostics.
            raise Refused("Git operation failed: " + args[0])
        return result.stdout.strip()

    def snapshot(self):
        self.git("fetch", "--no-tags", "origin", "refs/heads/" + BRANCH)
        sha = self.git("rev-parse", "FETCH_HEAD")
        control = json.loads(self.git("show", sha + ":" + self.relative + "/CONTROL.json"))
        if control.get("paused") is True:
            return {"sha": sha, "branch": BRANCH, "state": None, "control": control, "runner_versions": {}}
        remaining = control["limits"]["metadata_bytes_per_tick"]
        def blob(path):
            nonlocal remaining
            spec = sha + ":" + path
            size = int(self.git("cat-file", "-s", spec))
            if not 0 <= size <= remaining:
                raise Refused("Execution authority metadata ceiling before body read")
            response = subprocess.run(["git", "show", spec], cwd=self.repo, capture_output=True, timeout=45)
            if response.returncode or len(response.stdout) != size:
                raise Refused("Pinned metadata unavailable")
            remaining -= size
            return response.stdout
        state = json.loads(blob(self.relative + "/STATE.json"))
        verify(state)
        runners = {}
        from pathlib import PurePosixPath
        for protocol in state["protocols"].values():
            path = PurePosixPath(protocol["runner"])
            if path.is_absolute() or ".." in path.parts or path.suffix != ".py":
                raise Refused("Invalid frozen runner path")
            if str(path) not in runners:
                runners[str(path)] = hashlib.sha256(blob(str(path))).hexdigest()
        return {"sha": sha, "branch": BRANCH, "state": state, "control": control, "runner_versions": runners}

    def claim(self, state, expected_sha):
        """Local parent + server fast-forward rejection supplies the remote CAS."""
        if self.git("branch", "--show-current") != BRANCH:
            raise Refused("Wrong branch")
        if self.git("rev-parse", "HEAD") != expected_sha:
            raise Refused("Checkout is stale; no merge/rebase/rerun of a look")
        verify(state)
        from quant.state import write_json
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        if any(p not in (self.relative + "/STATE.json", self.relative + "/STATUS.md") for p in staged):
            raise Refused("Unrelated staged changes; do not publish them with a reservation")
        write_json(self.directory / "STATE.json", state)
        from .dashboard import markdown_state
        from .store import Store
        (self.directory / "STATUS.md").write_text(markdown_state(state, Store(self.directory).control()))
        self.git("add", "--", self.relative + "/STATE.json", self.relative + "/STATUS.md")
        self.git("-c", "user.name=Quant Edge Lab", "-c", "user.email=edge-lab@users.noreply.github.com",
                 "commit", "-m", "edge-lab: durable single-use execution receipt [skip ci]")
        self.git("push", "origin", "HEAD:refs/heads/" + BRANCH)
        return self.git("rev-parse", "HEAD")
