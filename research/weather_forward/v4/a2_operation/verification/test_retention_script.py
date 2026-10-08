"""Q27 : tests synthetiques du script de verification suppression/retention (repertoires temporaires)."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "qualification" / "verify_retention_deletion.sh"


def run(*args):
    return subprocess.run(["bash", str(SCRIPT), *map(str, args)], capture_output=True, text=True)


class Retention(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="a2ret-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.out = self.tmp / "out"
        self.out.mkdir()

    def test_empty_directory_deletion_verified_and_never_claims_retention(self):
        r = run(self.out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("DELETION_CAPABILITY=VERIFIED", r.stdout)
        self.assertIn("RETENTION_30D_DEMONSTRATED=NO", r.stdout)
        self.assertIn("EXISTING_FILES_TOUCHED=0", r.stdout)
        self.assertIn("PERSISTENT_ACROSS_REBOOT=", r.stdout)
        self.assertEqual(list(self.out.iterdir()), [])  # aucune sonde residuelle

    def test_refuses_a_directory_that_already_holds_a_file_and_leaves_it_alone(self):
        keep = self.out / "a2-doc-v1-d2-input-result-001.json"
        keep.write_text("REAL-LOOKING RESULT\n", encoding="utf-8")
        before = keep.stat().st_mtime_ns
        r = run(self.out)
        self.assertEqual(r.returncode, 2)
        self.assertIn("non vide", r.stderr)
        self.assertEqual(keep.read_text(encoding="utf-8"), "REAL-LOOKING RESULT\n")
        self.assertEqual(keep.stat().st_mtime_ns, before)
        self.assertNotIn("DELETION_CAPABILITY", r.stdout)

    def test_refuses_symlink_missing_and_wrong_argument_count(self):
        link = self.tmp / "link"
        link.symlink_to(self.out)
        self.assertEqual(run(link).returncode, 2)
        self.assertEqual(run(self.tmp / "absent").returncode, 2)
        self.assertEqual(run().returncode, 2)
        self.assertEqual(run(self.out, "extra").returncode, 2)

    def test_non_tmpfs_is_reported_unverified_not_persistent(self):
        r = run(self.out)
        fstype = [l for l in r.stdout.splitlines() if l.startswith("OUTPUT_DIR_FSTYPE=")][0].split("=")[1]
        persistent = [l for l in r.stdout.splitlines() if l.startswith("PERSISTENT_ACROSS_REBOOT=")][0].split("=")[1]
        self.assertEqual(persistent, "NO" if fstype in ("tmpfs", "ramfs") else "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
