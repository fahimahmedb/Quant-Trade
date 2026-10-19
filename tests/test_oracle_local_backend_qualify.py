"""Qualification cannot turn plausible wrong answers into PASS or leak a server."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from deploy import oracle_local_backend_qualify as qualification


class BackendQualificationTests(unittest.TestCase):
    def test_schema_valid_but_scientifically_wrong_answers_fail(self):
        class WrongBackend:
            def generate_structured(self, prompt, schema):
                choices = schema['properties']['decision']['enum']
                return {'decision': choices[-1]}
        results = qualification.scientific_cases(WrongBackend())
        self.assertEqual(len(results), 4)
        self.assertTrue(all(not item['passed'] for item in results))

    def test_backend_failure_stops_actual_temporary_process_and_persists_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processes = []
            real_popen = subprocess.Popen
            def spawn(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                processes.append(process)
                return process
            with patch.object(qualification.os, 'geteuid', return_value=999), \
                 patch.object(qualification, 'stage', return_value={'model': {'local_alias': 'gpt-oss-test'}}), \
                 patch.object(qualification, 'server_command', return_value=[sys.executable, '-c', 'import time; time.sleep(60)']), \
                 patch.object(qualification.subprocess, 'Popen', side_effect=spawn), \
                 patch.object(qualification.GPTOSSBackend, 'healthcheck', return_value={'status': 'PASS'}), \
                 patch.object(qualification, 'scientific_cases', side_effect=RuntimeError('ACTUAL_INFERENCE_FAILED')):
                report = qualification.qualify(root, root / 'result.json')
            self.assertEqual(report['status'], 'BLOCKED')
            self.assertIn('ACTUAL_INFERENCE_FAILED', report['blocker'])
            self.assertTrue(report['temporary_server_stopped'])
            self.assertIsNotNone(processes[0].poll())
            self.assertEqual(json.loads((root / 'result.json').read_text()), report)
            self.assertEqual(os.stat(root / 'result.json').st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
