import unittest

from research.research_os.runtime.workflow_simulator import simulate


class WorkflowLaneSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = simulate(3)

    def test_simulation_passes(self):
        self.assertEqual(self.result["status"], "PASS")

    def test_one_lineage_per_wake(self):
        self.assertTrue(self.result["one_lineage_per_wake"])

    def test_no_self_validation(self):
        self.assertFalse(self.result["self_validation_detected"])

    def test_no_deadlock(self):
        self.assertFalse(self.result["deadlock_detected"])

    def test_authority_stays_closed(self):
        self.assertTrue(self.result["authority_safe"])

    def test_pipeline_advances_lineages(self):
        self.assertGreaterEqual(len(self.result["integrated_lineages"]), 1)
        self.assertGreater(self.result["productive_wakes"], 0)


if __name__ == "__main__":
    unittest.main()
