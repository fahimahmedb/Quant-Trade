import unittest

from quant.factory.experiments import DatasetRef, ExperimentError, ExperimentRegistry, ExperimentStatus, PreregistrationContract


def protocol(horizon=20):
    return PreregistrationContract("generic event cluster", "admit preregistered candidates", horizon, "SPY", (), "two-sided issuer-aware test")


class ExperimentRegistryTests(unittest.TestCase):
    def test_identity_version_and_protocol_hash(self):
        registry = ExperimentRegistry()
        first = registry.propose("cluster-primary", "generic", protocol())
        second = registry.propose("cluster-primary", "generic", protocol(30))
        self.assertEqual(first.experiment_id, second.experiment_id)
        self.assertEqual((first.version, second.version), (1, 2))
        self.assertNotEqual(first.protocol_hash, second.protocol_hash)

    def test_state_machine_and_data_freeze(self):
        registry = ExperimentRegistry()
        record = registry.propose("lane-a", "synthetic", protocol())
        with self.assertRaises(ExperimentError):
            registry.advance(record.experiment_id, record.version, ExperimentStatus.DATA_READY)
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.PREREGISTERED)
        record = registry.attach_datasets(record.experiment_id, record.version, [DatasetRef("events", "v1", "a" * 64)])
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.DATA_READY)
        record, gate = registry.blue_freeze(record.experiment_id, record.version)
        self.assertEqual(gate.protocol_hash, record.protocol_hash)
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.TESTING)
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.INSUFFICIENT)
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.RETIRED)
        self.assertEqual(record.status, ExperimentStatus.RETIRED)

    def test_outcome_dataset_not_formation(self):
        registry = ExperimentRegistry()
        record = registry.propose("lane-b", "synthetic", protocol())
        with self.assertRaises(ExperimentError):
            registry.attach_datasets(record.experiment_id, record.version, [DatasetRef("future", "v1", "b" * 64, role="outcome")])

    def test_immutable_fields_cannot_be_weakened(self):
        with self.assertRaises(ExperimentError):
            PreregistrationContract("x", "y", 20, "SPY", (), "z", immutable_fields=("signal_definition",))


if __name__ == "__main__":
    unittest.main()