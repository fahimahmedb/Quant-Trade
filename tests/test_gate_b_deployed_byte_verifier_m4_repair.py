from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


verifier = load_module(
    "verify_gate_b_deployed_bytes_m4_repair",
    ROOT / "scripts" / "verify_gate_b_deployed_bytes.py",
)
CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
TREE = "4d15ef6f471213ee6ab56337b555d2906ef9bf16"


class SyntheticVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "release"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "GateB M4 Test")
        self.git("config", "user.email", "gateb-m4@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "scripts").mkdir()
        (self.repo / "deploy").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "src" / "main.py").write_text("print('frozen')\n")
        (self.repo / "scripts" / "tool.sh").write_text("#!/bin/sh\necho ok\n")
        (self.repo / "scripts" / "tool.sh").chmod(0o755)
        (self.repo / "deploy" / "unit.service").write_text("[Service]\nExecStart=/bin/true\n")
        (self.repo / "docs" / "target.txt").write_text("target\n")
        os.symlink("target.txt", self.repo / "docs" / "link")
        (self.repo / "README.md").write_text("frozen\n")
        self.git("add", ".")
        self.git("commit", "-qm", "frozen")
        self.sha = self.git("rev-parse", "HEAD").strip()
        self.tree = self.git("rev-parse", "HEAD^{tree}").strip()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, cwd=None, check=True, env=None):
        proc = subprocess.run(
            ["git", "-C", str(cwd or self.repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
            env=env,
        )
        return proc.stdout

    def verify(self, repo=None, **kwargs):
        return verifier.verify(
            repo or self.repo,
            expected_sha=kwargs.pop("expected_sha", self.sha),
            expected_tree=kwargs.pop("expected_tree", self.tree),
            **kwargs,
        )

    def test_synthetic_green_reports_hardening_and_no_git_writes(self):
        index = self.repo / ".git" / "index"
        before = (index.stat().st_mtime_ns, index.read_bytes())
        report, digest = self.verify()
        after = (index.stat().st_mtime_ns, index.read_bytes())
        self.assertEqual(report["status"], "GREEN")
        self.assertTrue(digest.startswith("sha256:"))
        self.assertTrue(report["replacement_object_semantics_disabled"])
        self.assertTrue(report["replace_refs_absent"])
        self.assertTrue(report["legacy_grafts_absent"])
        self.assertTrue(report["git_metadata_unchanged"])
        self.assertEqual(before, after)
        self.assertEqual(report["git_metadata_before"]["lock_paths"], report["git_metadata_after"]["lock_paths"])
        self.assertIn("TARGET_HOST_ONLY", report["residual_immutability_boundary"])

    def test_tracked_byte_mutation_red(self):
        (self.repo / "src" / "main.py").write_text("print('mutated')\n")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("tracked_byte_or_mode_mismatch", report["reasons"])

    def test_executable_bit_mutation_red(self):
        (self.repo / "scripts" / "tool.sh").chmod(0o644)
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertTrue(any(x["kind"] == "mode" for x in report["tracked_mismatches"]))

    def test_tracked_regular_to_symlink_red(self):
        path = self.repo / "src" / "main.py"
        path.unlink()
        os.symlink("../README.md", path)
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertTrue(any(x["path"] == "src/main.py" and x["kind"] == "type" for x in report["tracked_mismatches"]))

    def test_expected_symlink_to_regular_red(self):
        path = self.repo / "docs" / "link"
        path.unlink()
        path.write_text("target.txt")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertTrue(any(x["path"] == "docs/link" and x["kind"] == "type" for x in report["tracked_mismatches"]))

    def test_missing_tracked_file_red(self):
        (self.repo / "deploy" / "unit.service").unlink()
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("deploy/unit.service", report["missing_tracked_paths"])

    def test_critical_untracked_red(self):
        (self.repo / "src" / "shadow.py").write_text("pass\n")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("src/shadow.py", report["untracked_execution_critical_paths"])

    def test_noncritical_untracked_red(self):
        (self.repo / "notes.txt").write_text("unexpected\n")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("notes.txt", report["untracked_other_paths"])

    def test_explicit_allowed_extra_prefix_green(self):
        (self.repo / "var").mkdir()
        (self.repo / "var" / "runtime.db").write_text("runtime")
        report, _ = self.verify(allowed_extra_prefixes=("var",))
        self.assertEqual(report["status"], "GREEN")

    def test_invalid_allowed_extra_prefix_red(self):
        for value in (
            "../src",
            "/tmp",
            "src/../deploy",
            "src/./nested",
            "src//nested",
            "src/",
            "src",
            "src/runtime",
            "deploy/extra",
            "scripts/generated",
        ):
            with self.subTest(value=value), self.assertRaises(verifier.VerifyError):
                self.verify(allowed_extra_prefixes=(value,))

    def test_allowed_prefix_cannot_hide_critical_untracked_bytes(self):
        (self.repo / "src" / "shadow.py").write_text("pass\n")
        with self.assertRaisesRegex(verifier.VerifyError, "overlaps execution-critical"):
            self.verify(allowed_extra_prefixes=("src",))

    def test_linked_worktree_red(self):
        worktree = self.root / "linked"
        self.git("worktree", "add", "--detach", str(worktree), self.sha)
        with self.assertRaisesRegex(verifier.VerifyError, "linked worktree"):
            verifier.verify(worktree, expected_sha=self.sha, expected_tree=self.tree)

    def test_dotgit_symlink_red(self):
        foreign = self.root / "foreign-git"
        (self.repo / ".git").rename(foreign)
        os.symlink(foreign, self.repo / ".git")
        with self.assertRaisesRegex(verifier.VerifyError, r"\.git must not be a symlink"):
            self.verify()

    def test_dotgit_text_pointer_red(self):
        foreign = self.root / "foreign-git"
        (self.repo / ".git").rename(foreign)
        (self.repo / ".git").write_text(f"gitdir: {foreign}\n")
        with self.assertRaisesRegex(verifier.VerifyError, "linked worktree"):
            self.verify()

    def test_objects_symlink_to_foreign_store_red(self):
        foreign = self.root / "foreign-objects"
        objects = self.repo / ".git" / "objects"
        shutil.copytree(objects, foreign, copy_function=shutil.copy2)
        shutil.rmtree(objects)
        os.symlink(foreign, objects)
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.sha)
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}").strip(), self.tree)
        with self.assertRaisesRegex(verifier.VerifyError, "objects"):
            self.verify()

    def test_alternates_file_red_even_empty(self):
        alt = self.repo / ".git" / "objects" / "info" / "alternates"
        alt.parent.mkdir(parents=True, exist_ok=True)
        alt.write_text("")
        with self.assertRaisesRegex(verifier.VerifyError, "alternates"):
            self.verify()

    def test_object_store_environment_overrides_red(self):
        for key, value in (
            ("GIT_OBJECT_DIRECTORY", str(self.root / "foreign")),
            ("GIT_ALTERNATE_OBJECT_DIRECTORIES", str(self.root / "foreign")),
            ("GIT_REPLACE_REF_BASE", "refs/evil/"),
            ("GIT_GRAFT_FILE", str(self.root / "foreign-grafts")),
            ("GIT_NAMESPACE", "evil"),
            ("GIT_QUARANTINE_PATH", str(self.root / "quarantine")),
        ):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: value}, clear=False):
                with self.assertRaisesRegex(verifier.VerifyError, "override environment"):
                    self.verify()

    def test_foreign_common_dir_indirection_red(self):
        foreign = self.root / "common"
        shutil.copytree(self.repo / ".git", foreign, copy_function=shutil.copy2)
        (self.repo / ".git" / "commondir").write_text(str(foreign) + "\n")
        with self.assertRaisesRegex(verifier.VerifyError, "common-dir indirection"):
            self.verify()

    def test_nested_object_directory_symlink_red(self):
        objects = self.repo / ".git" / "objects"
        shard = next(p for p in objects.iterdir() if p.is_dir() and len(p.name) == 2)
        foreign = self.root / "foreign-shard"
        shutil.copytree(shard, foreign, copy_function=shutil.copy2)
        shutil.rmtree(shard)
        os.symlink(foreign, shard)
        with self.assertRaisesRegex(verifier.VerifyError, "symlink indirection"):
            self.verify()

    def test_replace_ref_poisoning_is_rejected_before_authoritative_tree_read(self):
        expected_tree = self.tree
        (self.repo / "src" / "main.py").write_text("print('malicious')\n")
        self.git("add", "src/main.py")
        malicious_tree = self.git("write-tree").strip()
        malicious_listing = self.git("ls-tree", "-r", malicious_tree)
        self.git("reset", "--hard", "-q", self.sha)
        (self.repo / "src" / "main.py").write_text("print('malicious')\n")
        self.git("replace", expected_tree, malicious_tree)
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}").strip(), expected_tree)
        poisoned_listing = self.git("ls-tree", "-r", expected_tree)
        self.assertEqual(poisoned_listing, malicious_listing)
        with self.assertRaisesRegex(verifier.VerifyError, "replace refs"):
            self.verify()

    def test_legacy_grafts_metadata_red(self):
        grafts = self.repo / ".git" / "info" / "grafts"
        grafts.parent.mkdir(parents=True, exist_ok=True)
        grafts.write_text(self.sha + "\n")
        with self.assertRaisesRegex(verifier.VerifyError, "graft"):
            self.verify()

    def test_path_substitution_between_enumeration_and_read_fails_closed(self):
        original_walk = verifier.walk_filesystem
        target = self.repo / "src" / "main.py"

        def walk_then_substitute(*args, **kwargs):
            observed = original_walk(*args, **kwargs)
            target.unlink()
            os.symlink("../README.md", target)
            return observed

        with mock.patch.object(verifier, "walk_filesystem", side_effect=walk_then_substitute):
            report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertTrue(any(x["path"] == "src/main.py" for x in report["tracked_mismatches"]))

    def test_concurrent_content_mutation_during_read_fails_closed(self):
        target = self.repo / "src" / "main.py"
        original_read = verifier.os.read
        started = threading.Event()
        mutated = threading.Event()
        first = {"done": False}

        def mutate():
            self.assertTrue(started.wait(2))
            target.write_text("print('raced')\n")
            mutated.set()

        def slow_read(fd, size):
            try:
                opened_path = os.readlink(f"/proc/self/fd/{fd}")
            except OSError:
                opened_path = ""
            if not first["done"] and opened_path == str(target):
                first["done"] = True
                started.set()
                self.assertTrue(mutated.wait(2))
            return original_read(fd, size)

        thread = threading.Thread(target=mutate)
        thread.start()
        try:
            with mock.patch.object(verifier.os, "read", side_effect=slow_read):
                with self.assertRaisesRegex(verifier.VerifyError, "changed during inspection|identity raced"):
                    self.verify()
        finally:
            thread.join(timeout=2)
        self.assertFalse(thread.is_alive())


class ExactFrozenCandidateControl(unittest.TestCase):
    def test_real_frozen_candidate_green_from_self_contained_local_clone(self):
        source = ROOT
        verifier_mod = load_module(
            "verify_gate_b_deployed_bytes_m4_exact",
            source / "scripts" / "verify_gate_b_deployed_bytes.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "frozen"
            subprocess.run(
                ["git", "clone", "--no-local", "--no-checkout", "-q", str(source), str(clone)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            have = subprocess.run(
                ["git", "-C", str(clone), "cat-file", "-e", f"{CANDIDATE}^{{commit}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if have.returncode != 0:
                subprocess.run(
                    ["git", "-C", str(clone), "fetch", "-q", "--no-tags", str(source), CANDIDATE],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            subprocess.run(
                ["git", "-C", str(clone), "checkout", "-q", "--detach", CANDIDATE],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            sha = subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD"], text=True).strip()
            tree = subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD^{tree}"], text=True).strip()
            self.assertEqual(sha, CANDIDATE)
            self.assertEqual(tree, TREE)
            alternates = clone / ".git" / "objects" / "info" / "alternates"
            self.assertFalse(alternates.exists())
            for path in (clone / ".git" / "objects").rglob("*"):
                if path.is_file() and not path.is_symlink():
                    self.assertLessEqual(path.stat().st_nlink, 1, f"hardlinked object: {path}")
            report, _ = verifier_mod.verify(clone, expected_sha=CANDIDATE, expected_tree=TREE)
            self.assertEqual(report["status"], "GREEN")
            self.assertEqual(report["observed_sha"], CANDIDATE)
            self.assertEqual(report["observed_head_tree"], TREE)


if __name__ == "__main__":
    unittest.main()
