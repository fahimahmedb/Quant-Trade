"""Root-boundary contracts; no credentials or system changes."""
from pathlib import Path
import unittest
from deploy.oracle_live_host_prepare import CORE_SHA, environment, override, parse_secret


class LiveHostPrepareTests(unittest.TestCase):
    def test_sealed_secret_strict_format(self):
        self.assertEqual(parse_secret(b'a' * 64 + b'\n'), 'a' * 64)
        for raw in (b'', b'a' * 63, b'a' * 64 + b'\nINJECT=1', b'G' * 64):
            with self.assertRaises(ValueError): parse_secret(raw)

    def test_rotation_preserves_unrelated_settings_and_removes_old_oracle_values(self):
        result = environment('OTHER=preserved\nQT_ORACLE_INGRESS_KEY=obsolete\nQT_ORACLE_PRINCIPAL=old\n', 'a' * 64).decode()
        self.assertIn('OTHER=preserved', result)
        self.assertNotIn('obsolete', result)
        self.assertEqual(result.count('QT_ORACLE_INGRESS_KEY='), 1)
        self.assertIn('QT_ORACLE_PRINCIPAL=oracle-research-live', result)

    def test_exact_core_and_observer_lock_and_secret_file(self):
        result = override(Path('/opt/quant-research/live-projections') / ('b' * 40)).decode()
        self.assertIn('EnvironmentFile=/etc/quant-research/worker.env', result)
        self.assertIn('ExecStart=\nExecStart=/usr/bin/flock --nonblock', result)
        self.assertIn('--core-release /opt/quant-research/releases/' + CORE_SHA, result)
        self.assertIn('/usr/bin/python3.12 -I -B', result)
        self.assertNotIn('sudo', result)
        self.assertNotIn('QT_ORACLE_INGRESS_KEY=', result)


if __name__ == '__main__': unittest.main()
