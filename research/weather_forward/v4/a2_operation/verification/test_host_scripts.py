"""Q22 : tests synthetiques des scripts d'hote (deploy_operation_files.sh, attest_loaded_code.sh).

Contenus synthetiques seulement (aucun fichier du candidat), repertoires temporaires, jamais /opt/a2.
Le script de deploiement est copie avec quatre substitutions de test (uid, cible, controle root, proprietaire)
et ces substitutions sont verifiees une a une : le texte de securite du script n'est pas modifie.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
QUAL = ROOT / "qualification"
BASE = "research/weather_forward/v4"
PATHS = (
    [f"{BASE}/a2_harness/{n}" for n in ("__init__.py", "contract.py", "harness.py", "trusted_root.py")]
    + [f"{BASE}/a2_operation/{n}" for n in (
        "__init__.py", "common/__init__.py", "common/bounded_output.py", "identity/__init__.py",
        "identity/identity_via_harness.py", "operation/__init__.py",
        "operation/a2_doc_integration_operation.py", "common/a2_unit_profile.sh",
        "frozen/operation_context_d2_pre_effect_v1.json")]
)


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def run(args, **kw):
    return subprocess.run(["bash", *map(str, args)], capture_output=True, text=True, **kw)


class HostScripts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="a2host-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.stage, self.target = self.tmp / "stage", self.tmp / "opt-a2"
        self.target.mkdir()
        rows = []
        for rel in PATHS:
            data = f"SYNTHETIC {rel}\n".encode()
            f = self.stage / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
            rows.append(f"{blob(data)}\t{rel}\n")
        self.tsv = self.stage / BASE / "a2_operation/frozen/final_pins_d2_v1.tsv"
        self.tsv.parent.mkdir(parents=True, exist_ok=True)
        self.tsv.write_text("".join(rows), encoding="utf-8")
        self.tsv_blob = blob(self.tsv.read_bytes())
        self.deploy = self.make_deploy()
        self.attest = QUAL / "attest_loaded_code.sh"

    def make_deploy(self):
        src = (QUAL / "deploy_operation_files.sh").read_text(encoding="utf-8")
        for old, new in (
            ('[ "$(id -u)" -eq 0 ] || stop "lancer avec sudo"', "true"),
            ("TARGET=/opt/a2", f"TARGET={self.target}"),
            ('[ "$(stat -c \'%u:%g:%a\' "$TARGET")" = 0:0:755 ] || stop "propriete ou permissions de $TARGET discordantes"', "true"),
        ):
            self.assertEqual(src.count(old), 1, old)
            src = src.replace(old, new)
        self.assertEqual(src.count(" -o root -g root"), 4)
        src = src.replace(" -o root -g root", "")
        path = self.tmp / "deploy_test.sh"
        path.write_text(src, encoding="utf-8")
        return path

    def do_deploy(self, blob_arg=None):
        return run([self.deploy, self.stage, blob_arg or self.tsv_blob])

    def do_attest(self, blob_arg=None):
        return run([self.attest, self.target, blob_arg or self.tsv_blob])

    def test_deploy_then_attest_ok_and_idempotent(self):
        r = self.do_deploy()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("OPERATION_FILES_DEPLOYED_OR_IDENTICAL=13", r.stdout)
        self.assertIn("OPERATION_SCRIPT_EXECUTED=0", r.stdout)
        a = self.do_attest()
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertIn("LOADED_CODE_MATCHES_APPROVED=13/13", a.stdout)
        self.assertEqual(self.do_deploy().returncode, 0)  # identique : accepte

    def test_deploy_refuses_tampered_or_symlinked_source_and_installs_nothing(self):
        victim = self.stage / PATHS[3]
        victim.write_bytes(b"TAMPERED\n")
        r = self.do_deploy()
        self.assertEqual(r.returncode, 2)
        self.assertIn("source discordante", r.stderr)
        self.assertEqual(list(self.target.rglob("*")), [])
        victim.unlink()
        victim.symlink_to(self.stage / PATHS[0])
        r = self.do_deploy()
        self.assertEqual(r.returncode, 2)
        self.assertEqual(list(self.target.rglob("*")), [])

    def test_deploy_refuses_wrong_pins_blob_and_foreign_path(self):
        self.assertEqual(self.do_deploy("0" * 40).returncode, 2)
        self.assertEqual(self.do_deploy("not-a-blob").returncode, 2)
        rows = self.tsv.read_text(encoding="utf-8").splitlines()
        rows[0] = rows[0].split("\t")[0] + "\tetc/passwd"
        self.tsv.write_text("\n".join(rows) + "\n", encoding="utf-8")
        r = self.do_deploy(blob(self.tsv.read_bytes()))
        self.assertEqual(r.returncode, 2)
        self.assertIn("hors perimetre", r.stderr)

    def test_deploy_never_replaces_a_different_existing_file(self):
        existing = self.target / PATHS[2]
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"DIFFERENT\n")
        r = self.do_deploy()
        self.assertEqual(r.returncode, 2)
        self.assertIn("aucun remplacement", r.stderr)
        self.assertEqual(existing.read_bytes(), b"DIFFERENT\n")
        self.assertFalse((self.target / PATHS[0]).exists())  # rien d'installe avant l'echec

    def test_attest_detects_modification_missing_extra_and_wrong_pins(self):
        self.assertEqual(self.do_deploy().returncode, 0)
        target_file = self.target / PATHS[1]
        os.chmod(target_file, 0o644)
        target_file.write_bytes(b"CHANGED\n")
        r = self.do_attest()
        self.assertEqual(r.returncode, 2)
        self.assertIn("discordance de blob", r.stderr)
        shutil.rmtree(self.target)
        self.target.mkdir()
        self.assertEqual(self.do_deploy().returncode, 0)
        (self.target / PATHS[5]).unlink()
        self.assertIn("absent", self.do_attest().stderr)
        shutil.rmtree(self.target)
        self.target.mkdir()
        self.assertEqual(self.do_deploy().returncode, 0)
        sneaky = self.target / BASE / "a2_harness" / "sitecustomize.py"
        sneaky.write_text("print('x')\n", encoding="utf-8")
        r = self.do_attest()
        self.assertEqual(r.returncode, 2)
        self.assertIn("UNEXPECTED_FILE=", r.stderr)
        sneaky.unlink()
        self.assertEqual(self.do_attest().returncode, 0)
        self.assertEqual(self.do_attest("0" * 40).returncode, 2)

    def test_attest_ignores_qualification_package_files(self):
        self.assertEqual(self.do_deploy().returncode, 0)
        q = self.target / BASE / "a2_operation" / "qualification" / "run_qualification.sh"
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text("#!/bin/sh\n", encoding="utf-8")
        self.assertEqual(self.do_attest().returncode, 0)


if __name__ == "__main__":
    unittest.main()
