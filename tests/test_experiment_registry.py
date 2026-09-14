import unittest

from quant.factory.experiments import DatasetRef, EventRecord, ExperimentError, ExperimentRegistry, ExperimentStatus, PreregistrationContract


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

    def test_same_experiment_key_is_independent_across_lanes(self):
        registry = ExperimentRegistry()
        form4 = registry.propose("cluster-primary", "sec-form4", protocol())
        crypto = registry.propose("cluster-primary", "crypto", protocol())
        self.assertNotEqual(form4.experiment_id, crypto.experiment_id)
        self.assertEqual((form4.version, crypto.version), (1, 1))

    def test_state_machine_and_data_freeze(self):
        registry = ExperimentRegistry()
        record = registry.propose("lane-a", "synthetic", protocol())
        with self.assertRaises(ExperimentError):
            registry.advance(record.experiment_id, record.version, ExperimentStatus.DATA_READY)
        with self.assertRaises(ExperimentError):
            registry.attach_datasets(record.experiment_id, record.version, [DatasetRef("events", "v1", "a" * 64)])
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
        record = registry.advance(record.experiment_id, record.version, ExperimentStatus.PREREGISTERED)
        with self.assertRaises(ExperimentError):
            registry.attach_datasets(record.experiment_id, record.version, [DatasetRef("future", "v1", "b" * 64, role="outcome")])

    def test_immutable_fields_cannot_be_weakened(self):
        with self.assertRaises(ExperimentError):
            PreregistrationContract("x", "y", 20, "SPY", (), "z", immutable_fields=("signal_definition",))

    def test_generic_event_contract_rejects_invalid_calendar_and_naive_time(self):
        with self.assertRaises(ExperimentError):
            EventRecord("e1", "i1", "2025-02-28T20:00:00Z", "2025-02-30", "SYNTHETIC", "CERTIFIED")
        with self.assertRaises(ExperimentError):
            EventRecord("e1", "i1", "2025-02-28T20:00:00", "2025-02-28", "SYNTHETIC", "CERTIFIED")


if __name__ == "__main__":
    unittest.main()
