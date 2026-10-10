"""GitHub branch authority through ordinary fast-forward Git, never force push."""
import json
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
        state = json.loads(self.git("show", sha + ":" + self.relative + "/STATE.json"))
        control = json.loads(self.git("show", sha + ":" + self.relative + "/CONTROL.json"))
        verify(state)
        return {"sha": sha, "branch": BRANCH, "state": state, "control": control}

    def claim(self, state, expected_sha):
        """Local parent + server fast-forward rejection supplies the remote CAS."""
        if self.git("branch", "--show-current") != BRANCH:
            raise Refused("Wrong branch")
        if self.git("rev-parse", "HEAD") != expected_sha:
            raise Refused("Checkout is stale; no merge/rebase/rerun of a look")
        verify(state)
        from quant.state import write_json
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        if any(p != self.relative + "/STATE.json" for p in staged):
            raise Refused("Unrelated staged changes; do not publish them with a reservation")
        write_json(self.directory / "STATE.json", state)
        self.git("add", "--", self.relative + "/STATE.json")
        self.git("-c", "user.name=Quant Edge Lab", "-c", "user.email=edge-lab@users.noreply.github.com",
                 "commit", "-m", "edge-lab: durable single-use execution receipt [skip ci]")
        self.git("push", "origin", "HEAD:refs/heads/" + BRANCH)
        return self.git("rev-parse", "HEAD")
