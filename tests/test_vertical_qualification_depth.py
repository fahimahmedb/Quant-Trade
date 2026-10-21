"""Exact-source receipts must describe the executable that produced them."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / "checkout"
    subprocess.run(["git", "clone", "--quiet", "--local", "--no-hardlinks", str(ROOT), str(root)],
                   check=True, capture_output=True, timeout=30)
    # Exercise the actual proposed script, committed in an isolated source tree.
    shutil.copyfile(ROOT / "scripts/qualify_oracle_v2_core.py", root / "scripts/qualify_oracle_v2_core.py")
    git(root, "add", "scripts/qualify_oracle_v2_core.py")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
        "commit", "--allow-empty", "-m", "disposable exact-source fixture")
    return root


def qualify(root, sha):
    output = root / "proof.json"
    env = dict(os.environ, PYTHONPATH=str(root / "src") + os.pathsep + str(root))
    result = subprocess.run([sys.executable, str(root / "scripts/qualify_oracle_v2_core.py"),
                             "--fixture", str(root / "tests/fixtures/oracle_v2_core_fixture.json"),
                             "--sha", sha, "--output", str(output)],
                            cwd=root, env=env, capture_output=True, text=True, timeout=15)
    return result, output


@pytest.mark.parametrize("foreign", ["0" * 40, "base"])
def test_foreign_sha_cannot_label_a_successful_qualification(checkout, foreign):
    if foreign == "base":
        foreign = "01c2e520fa4116645870f96acf6770ea83f1881c"
    result, output = qualify(checkout, foreign)
    assert result.returncode != 0
    assert "CODE_HEAD_MISMATCH" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("path", ["research/research_os/expansion/v2_core.py",
                                 "scripts/qualify_oracle_v2_core.py"])
def test_dirty_executable_cannot_claim_the_committed_source_identity(checkout, path):
    source = checkout / path
    source.write_text(source.read_text() + "\n# disposable uncommitted change\n")
    result, output = qualify(checkout, git(checkout, "rev-parse", "HEAD"))
    assert result.returncode != 0
    assert "DIRTY_EXECUTABLE_TREE" in result.stderr
    assert not output.exists()


def test_clean_exact_source_can_produce_a_closed_receipt(checkout):
    head = git(checkout, "rev-parse", "HEAD")
    result, output = qualify(checkout, head)
    assert result.returncode == 0, result.stderr
    artifact = json.loads(output.read_text())
    assert artifact["verified_commit_sha"] == head
    assert artifact["receipt"]["outcome_accessed"] is False
    assert all(value is False for value in artifact["receipt"]["authority"].values())
