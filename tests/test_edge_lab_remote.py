"""Real fast-forward conflicts across two clones of a temporary Git repository."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from quant.edge_lab.engine import initialize
from quant.edge_lab.remote import GitAuthority
from quant.edge_lab.seed import BRANCH
from quant.edge_lab.store import Refused, event


class RemoteTest(unittest.TestCase):
    def git(self, directory, *args):
        response = subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.test", *args],
                                  cwd=directory, capture_output=True, text=True, check=True)
        return response.stdout.strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bare = self.root / "origin.git"
        self.git(self.root, "init", "--bare", str(self.bare))
        self.first = self.root / "first"
        self.first.mkdir()
        self.git(self.first, "init", "-b", BRANCH)
        self.directory = self.first / "research/edge_lab"
        initialize(self.directory)
        self.git(self.first, "add", "research/edge_lab/STATE.json", "research/edge_lab/CONTROL.json")
        self.git(self.first, "commit", "-m", "synthetic initial state")
        self.git(self.first, "remote", "add", "origin", str(self.bare))
        self.git(self.first, "push", "-u", "origin", BRANCH)
        self.second = self.root / "second"
        self.git(self.root, "clone", "-b", BRANCH, str(self.bare), str(self.second))
        self.a = GitAuthority(self.first, self.directory)
        self.b = GitAuthority(self.second, self.second / "research/edge_lab")

    def tearDown(self):
        self.temp.cleanup()

    def test_only_one_host_can_publish_against_one_parent(self):
        first, second = self.a.snapshot(), self.b.snapshot()
        self.assertEqual(first["sha"], second["sha"])
        from quant.edge_lab.store import Store
        states = []
        for root in (self.directory, self.second / "research/edge_lab"):
            store = Store(root)
            with store.lock():
                state = store.read()
                event(state, "SYNTHETIC_CLAIM", {"host": str(root)})
                store.save(state)
                states.append(state)
        winner = self.a.claim(states[0], first["sha"])
        with self.assertRaises(Refused):
            self.b.claim(states[1], second["sha"])
        self.assertEqual(self.a.snapshot()["sha"], winner)

    def test_owner_pause_commit_cannot_be_overwritten(self):
        from quant.edge_lab.store import Store
        first = self.a.snapshot()
        Store(self.second / "research/edge_lab").pause(True, "fixture Owner pause")
        self.git(self.second, "add", "research/edge_lab/CONTROL.json", "research/edge_lab/STATE.json")
        self.git(self.second, "commit", "-m", "pause")
        self.git(self.second, "push", "origin", BRANCH)
        state = first["state"]
        store = Store(self.directory)
        with store.lock():
            event(state, "SYNTHETIC_STALE_CLAIM", {})
            store.save(state)
        with self.assertRaises(Refused):
            self.a.claim(state, first["sha"])
        self.assertTrue(self.a.snapshot()["control"]["paused"])


if __name__ == "__main__":
    unittest.main()
