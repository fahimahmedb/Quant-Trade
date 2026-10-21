import unittest

from quant.factory.outcome_firewall import OutcomeFirewallError, assert_pre_outcome_payload


class FirewallHardeningTests(unittest.TestCase):
    def test_contains_outcome_marker_fails_closed(self):
        with self.assertRaisesRegex(OutcomeFirewallError, "OUTCOME_MARKER_FORBIDDEN"):
            assert_pre_outcome_payload({"route_id":"formation", "contains_outcome":True})

    def test_dataset_and_field_roles_fail_closed(self):
        for payload in ({"dataset_role":"OUTCOME"}, {"field_role":"OUTCOME"}, {"column_role":"OUTCOME"}):
            with self.assertRaises(OutcomeFirewallError):
                assert_pre_outcome_payload(payload)

    def test_alias_and_lineage_to_outcome_fail_closed(self):
        for payload in (
            {"role":"METADATA", "alias_of":"future_return"},
            {"role":"DERIVED", "sources":["issuer_id", "future_return"]},
            {"field_role":"DERIVED", "lineage":{"input":"realized_pnl"}},
        ):
            with self.assertRaisesRegex(OutcomeFirewallError, "OUTCOME_LINEAGE_FORBIDDEN"):
                assert_pre_outcome_payload(payload)

    def test_unknown_derived_lineage_fails_closed(self):
        with self.assertRaisesRegex(OutcomeFirewallError, "UNKNOWN_DERIVED_LINEAGE"):
            assert_pre_outcome_payload({"role":"DERIVED", "name":"opaque"})

    def test_safe_geometry_lineage_is_allowed(self):
        assert_pre_outcome_payload({"role":"DERIVED", "name":"hhi", "sources":["issuer_id"]})

    def test_preregistered_outcome_definition_is_still_allowed(self):
        assert_pre_outcome_payload({"outcome_definition":"next eligible return", "outcome_accessed":False,
                                    "result":"NOT_OBSERVED"})


if __name__ == "__main__":
    unittest.main()
