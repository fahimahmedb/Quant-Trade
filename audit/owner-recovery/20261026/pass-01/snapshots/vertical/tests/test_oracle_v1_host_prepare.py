import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from deploy.oracle_local_backend_install import verify
from deploy.oracle_v1_host_prepare import copy_verified, wrapper


class HostPreparationTests(unittest.TestCase):
    def test_corrupt_copy_is_not_published_and_existing_asset_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / 'source', root / 'target'
            good = b'GGUFpinned-asset'
            spec = {'size': len(good), 'sha256': hashlib.sha256(good).hexdigest()}
            source.write_bytes(b'X' * len(good))
            with self.assertRaises(ValueError):
                copy_verified(source, target, spec, verify, magic=b'GGUF')
            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob('.asset-*')), [])
            target.write_bytes(b'old-installation')
            source.write_bytes(good)
            with self.assertRaises(ValueError):
                copy_verified(source, target, spec, verify, magic=b'GGUF')
            self.assertEqual(target.read_bytes(), b'old-installation')

    def test_no_argument_privileged_wrapper_rejects_caller_options_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / 'activate'
            script.write_bytes(wrapper(root, 'deploy.oracle_scheduler_install', ['--activate']))
            script.chmod(0o700)
            result = subprocess.run([str(script), '--release', '/tmp/attacker'], capture_output=True)
            self.assertEqual(result.returncode, 64)
            self.assertEqual(result.stdout, b'')
            self.assertEqual(result.stderr, b'')


if __name__ == '__main__':
    unittest.main()
