import os
from pathlib import Path
import sys
import unittest
import tempfile
import json
from unittest.mock import patch

from research.research_os import host_wake
# Collect the F4/F5 seam challenge under the already-qualified exact-head suite.
from tests.test_f4_f5_terminal_continuation import TerminalBridgeTests


class HostWakeRouterTests(unittest.TestCase):
    def test_engineering_decider_reuses_local_backend_and_restricts_actions(self):
        from scripts.gpt_oss_orchestrator import local_backend_decision
        from unittest.mock import Mock
        backend = Mock()
        backend.generate_structured.return_value = {"action": "PARK", "reason": "rehearsal"}
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "worker.json"
            config.write_text(json.dumps({"model_backend": {"implementation": "gpt_oss"}}))
            with patch("research.research_os.oracle_worker.backend_from_config", return_value=backend) as factory:
                result = local_backend_decision(config, {"allowed_actions": ["PARK"]})
                self.assertEqual(result["action"], "PARK")
                self.assertEqual(backend.generate_structured.call_args.args[1]["properties"]["action"]["enum"], ["PARK"])
                factory.assert_called_once()
                with self.assertRaisesRegex(ValueError, "INVALID_ENGINEERING_ACTION_SET"):
                    local_backend_decision(config, {"allowed_actions": ["TRADE"]})

    @patch("research.research_os.host_wake.os.execve")
    def test_v2_default_stays_v2_and_codex_state_stays_in_v2_sandbox(self, execve):
        with patch.dict(os.environ, {"QUANT_CODEX_ORCHESTRATION_ENABLED": "0"}):
            host_wake.main(["--config", "/etc/quant-research-v2/worker.json", "--worker-version", "v2"])
        self.assertIn("research.research_os.oracle_worker_v2", execve.call_args.args[1])
        with patch.dict(os.environ, {"QUANT_CODEX_ORCHESTRATION_ENABLED": "1",
                "QUANT_CODEX_ORCHESTRATION_ROOT": "/var/lib/quant-research-v2/codex_control_plane"}):
            host_wake.main(["--config", "/etc/quant-research-v2/worker.json", "--worker-version", "v2"])
        self.assertIn("gpt_oss_orchestrator.py", execve.call_args.args[1][1])

    @patch("research.research_os.host_wake.os.execve")
    def test_default_path_preserves_existing_oracle_worker(self, execve):
        with patch.dict(os.environ, {"QUANT_CODEX_ORCHESTRATION_ENABLED": "0"}, clear=False):
            self.assertEqual(host_wake.main(["--config", "/etc/quant-research/worker.json"]), 0)
        execve.assert_called_once()
        executable, argv, env = execve.call_args.args
        self.assertEqual(executable, sys.executable)
        self.assertEqual(
            argv,
            [
                sys.executable,
                "-m",
                "research.research_os.oracle_worker",
                "--config",
                "/etc/quant-research/worker.json",
            ],
        )
        self.assertNotEqual(env.get("QUANT_CODEX_ORCHESTRATION_ENABLED"), "1")

    @patch("research.research_os.host_wake.os.execve")
    def test_feature_flag_routes_exactly_one_wake_to_codex_orchestrator(self, execve):
        root = "/var/lib/quant-research/codex_control_plane"
        with patch.dict(
            os.environ,
            {
                "QUANT_CODEX_ORCHESTRATION_ENABLED": "1",
                "QUANT_CODEX_ORCHESTRATION_ROOT": root,
                "PYTHONPATH": "existing-path",
            },
            clear=False,
        ):
            self.assertEqual(host_wake.main(["--config", "/etc/quant-research/worker.json"]), 0)
        execve.assert_called_once()
        executable, argv, env = execve.call_args.args
        release_root = Path(host_wake.__file__).resolve().parents[2]
        self.assertEqual(executable, sys.executable)
        self.assertEqual(argv, [sys.executable, str(release_root / "scripts" / "gpt_oss_orchestrator.py")])
        self.assertEqual(env["QUANT_CODEX_ORCHESTRATION_ROOT"], root)
        pythonpath = env["PYTHONPATH"].split(os.pathsep)
        self.assertEqual(pythonpath[:3], [str(release_root / "src"), str(release_root), "existing-path"])

    @patch("research.research_os.host_wake.os.execve")
    def test_codex_state_must_use_systemd_writable_state_subdirectory(self, execve):
        with patch.dict(
            os.environ,
            {
                "QUANT_CODEX_ORCHESTRATION_ENABLED": "1",
                "QUANT_CODEX_ORCHESTRATION_ROOT": "/opt/quant-research/current/runtime/codex_control_plane",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(SystemExit, "MUST_BE_STATE_SUBDIRECTORY"):
                host_wake.main(["--config", "/etc/quant-research/worker.json"])
        execve.assert_not_called()

    @patch("research.research_os.host_wake.os.execve")
    def test_invalid_feature_flag_fails_closed(self, execve):
        with patch.dict(os.environ, {"QUANT_CODEX_ORCHESTRATION_ENABLED": "yes"}, clear=False):
            with self.assertRaisesRegex(SystemExit, "INVALID_QUANT_CODEX_ORCHESTRATION_ENABLED"):
                host_wake.main(["--config", "/etc/quant-research/worker.json"])
        execve.assert_not_called()

    def test_v1_systemd_service_uses_router_not_direct_worker(self):
        repository_root = Path(__file__).resolve().parents[1]
        service = (repository_root / "deploy" / "systemd" / "quant-research-worker.service").read_text()
        exec_lines = [line for line in service.splitlines() if line.startswith("ExecStart=")]
        self.assertEqual(len(exec_lines), 1)
        self.assertIn("-m research.research_os.host_wake --config /etc/quant-research/worker.json", exec_lines[0])
        self.assertNotIn("-m research.research_os.oracle_worker --config", exec_lines[0])


if __name__ == "__main__":
    unittest.main()
