"""GitHub branch authority through ordinary fast-forward Git, never force push."""
import json
import hashlib
import subprocess
from pathlib import Path

from .seed import BRANCH
from .store import Refused, verify, digest, Store


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
        control_spec = sha + ":" + self.relative + "/CONTROL.json"
        if not 0 < int(self.git("cat-file", "-s", control_spec)) <= 2097152:
            raise Refused("Remote control metadata ceiling before body read")
        control = json.loads(self.git("show", control_spec))
        if control.get("paused") is True:
            return {"sha": sha, "branch": BRANCH, "state": None, "control": control, "runner_versions": {}}
        if (control.get("schema") != 1 or control.get("paused") is not False
                or control.get("real_capital_authorized") is not False
                or control.get("live_trading_authorized") is not False):
            raise Refused("Invalid remote controls before state read")
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
            for name in {protocol["runner"], *protocol.get("code_sha256", {})}:
                path = PurePosixPath(name)
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
        allowed = {self.relative + "/STATE.json", self.relative + "/STATUS.md"}
        # Retain exact output, including failed/partial bytes, on the same
        # authorized branch. Only the known receipt directory can be staged.
        for job in state["jobs"].values():
            look_id = job.get("metadata", {}).get("look_id")
            if not look_id or look_id not in state["looks"]:
                continue
            directory = self.directory / "receipts" / digest(look_id)
            if not directory.is_dir():
                continue
            if directory.is_symlink() or self.repo not in directory.resolve().parents:
                raise Refused("Linked receipt directory cannot be published")
            for name in ("stdout.bin", "stderr.bin", "receipt.json", "original-stdout.bin", "original-result.json"):
                path = directory / name
                if path.is_file():
                    if path.is_symlink() or path.resolve().parent != directory.resolve():
                        raise Refused("Receipt path escaped publication directory")
                    if path.stat().st_size > Store(self.directory).control()["limits"]["metadata_bytes_per_tick"]:
                        raise Refused("Receipt publication size ceiling")
                    allowed.add(path.relative_to(self.repo).as_posix())
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        if any(p not in allowed for p in staged):
            raise Refused("Unrelated staged changes; do not publish them with a reservation")
        write_json(self.directory / "STATE.json", state)
        from .dashboard import markdown_state
        (self.directory / "STATUS.md").write_text(markdown_state(state, Store(self.directory).control()))
        self.git("add", "--", *sorted(allowed))
        self.git("-c", "user.name=Quant Edge Lab", "-c", "user.email=edge-lab@users.noreply.github.com",
                 "commit", "-m", "edge-lab: durable single-use execution receipt [skip ci]")
        self.git("push", "origin", "HEAD:refs/heads/" + BRANCH)
        return self.git("rev-parse", "HEAD")
