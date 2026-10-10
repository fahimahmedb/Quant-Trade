import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from quant.edge_lab.dashboard import markdown, server
from quant.edge_lab.engine import Lab, initialize


class PanelTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name) / "state"
        initialize(self.directory)
        self.instance = server(self.directory, 0)
        self.thread = threading.Thread(target=self.instance.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.instance.server_port}"

    def tearDown(self):
        self.instance.shutdown()
        self.instance.server_close()
        self.thread.join(2)
        self.temp.cleanup()

    def test_state_and_controls_persist_across_new_lab_instance(self):
        with urllib.request.urlopen(self.url + "/api/state") as response:
            self.assertFalse(json.load(response)["control"]["paused"])
        for action, paused in (("pause", True), ("resume", False)):
            request = urllib.request.Request(self.url + "/control/" + action, data=b"", headers={"Origin": self.url})
            with urllib.request.urlopen(request) as response:
                self.assertEqual(response.status, 200)
            self.assertEqual(Lab(self.directory).snapshot()[1]["paused"], paused)

    def test_cross_origin_and_rebound_host_cannot_change_pause(self):
        request = urllib.request.Request(self.url + "/control/pause", data=b"", headers={"Origin": "https://attacker.test"})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 403)
        request = urllib.request.Request(self.url + "/", headers={"Host": "attacker.test"})
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(request)
        self.assertFalse(Lab(self.directory).snapshot()[1]["paused"])

    def test_view_does_not_claim_edge_or_active_economic_worker(self):
        view = markdown(self.directory)
        self.assertIn("NON MESURÉ", view)
        self.assertIn("Aucun worker économique exécuté", view)
        self.assertIn("40 = B2 36 + B4 4", view)
        self.assertIn("CONTROL.json", view)


if __name__ == "__main__":
    unittest.main()
