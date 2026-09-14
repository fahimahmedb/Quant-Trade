import unittest
from dataclasses import replace

from quant.factory.experiments import DatasetRef, ExperimentRegistry, ExperimentStatus, PreregistrationContract
from quant.factory.outcome_firewall import ColumnRole, ColumnSpec, DataAccessRequest, OutcomeFirewall, OutcomeFirewallError


def frozen_experiment():
    registry = ExperimentRegistry()
    protocol = PreregistrationContract("synthetic signal", "next eligible event", 20, "SPY", (), "synthetic-only preregistered test")
    record = registry.propose("firewall-proof", "synthetic", protocol)
    record = registry.advance(record.experiment_id, record.version, ExperimentStatus.PREREGISTERED)
    record = registry.attach_datasets(record.experiment_id, record.version, [DatasetRef("formation", "v1", "f" * 64)])
    record = registry.advance(record.experiment_id, record.version, ExperimentStatus.DATA_READY)
    return registry, record


class OutcomeFirewallAdversarialTests(unittest.TestCase):
    def test_direct_outcome_blocked_before_freeze(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("outcomes", "v1", "o" * 64, role="outcome"), "/x", (ColumnSpec("future_return", ColumnRole.OUTCOME),))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_lying_role_still_blocked_by_name(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("mixed", "v1", "m" * 64), "/x", (ColumnSpec("future_return", ColumnRole.FORMATION),))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_alias_and_derived_lineage_blocked(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("mixed", "v1", "m" * 64), "/x", (
            ColumnSpec("future_return", ColumnRole.OUTCOME),
            ColumnSpec("x", ColumnRole.METADATA, alias_of="future_return"),
            ColumnSpec("opaque", ColumnRole.DERIVED, sources=("x",)),
        ), operation="derive")
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_opaque_undeclared_formation_alias_fails_closed(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("mixed", "v1", "m" * 64), "/renamed/events", (
            ColumnSpec("x17", ColumnRole.FORMATION),
        ))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_safe_named_alias_still_fails_closed_before_freeze(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("mixed", "v1", "m" * 64), "/renamed/events", (
            ColumnSpec("issuer_id", ColumnRole.IDENTIFIER),
            ColumnSpec("event_id", ColumnRole.IDENTIFIER, alias_of="issuer_id"),
        ))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_alternative_path_blocked_by_fingerprint(self):
        _, record = frozen_experiment()
        fingerprint = "9" * 64
        request = DataAccessRequest(DatasetRef("renamed", "copy", fingerprint), "/other/harmless.bin", (ColumnSpec("event_id", ColumnRole.IDENTIFIER),))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall({fingerprint}).authorize(request, record)

    def test_unknown_derivation_fails_closed(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("events", "v1", "e" * 64), "/events", (ColumnSpec("mystery", ColumnRole.DERIVED),), operation="derive")
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_empty_manifest_fails_closed(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("events", "v1", "e" * 64), "/events", ())
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, record)

    def test_safe_geometry_derivation_from_generic_event_field_is_allowed(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("events", "v1", "e" * 64), "/events", (
            ColumnSpec("issuer_id", ColumnRole.IDENTIFIER),
            ColumnSpec("hhi", ColumnRole.DERIVED, sources=("issuer_id",)),
        ), operation="derive")
        OutcomeFirewall().authorize(request, record)

    def test_exact_gate_allows_outcome_and_rejects_dataset_substitution(self):
        registry, record = frozen_experiment()
        record, gate = registry.blue_freeze(record.experiment_id, record.version)
        request = DataAccessRequest(DatasetRef("outcomes", "v1", "o" * 64, role="outcome"), "/outcomes", (ColumnSpec("response", ColumnRole.OUTCOME),))
        OutcomeFirewall().authorize(request, record, gate)
        substituted = replace(record, dataset_refs=(DatasetRef("other", "v2", "2" * 64),))
        with self.assertRaises(OutcomeFirewallError):
            OutcomeFirewall().authorize(request, substituted, gate)

    def test_formation_manifest_allowed_without_gate(self):
        _, record = frozen_experiment()
        request = DataAccessRequest(DatasetRef("events", "v1", "e" * 64), "/events", (
            ColumnSpec("event_id", ColumnRole.IDENTIFIER),
            ColumnSpec("issuer_id", ColumnRole.IDENTIFIER),
            ColumnSpec("event_time", ColumnRole.FORMATION),
            ColumnSpec("formation_date", ColumnRole.FORMATION),
            ColumnSpec("provenance", ColumnRole.METADATA),
            ColumnSpec("status", ColumnRole.METADATA),
        ))
        OutcomeFirewall().authorize(request, record)


if __name__ == "__main__":
    unittest.main()
