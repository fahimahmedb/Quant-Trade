"""An unestablished availability clock cannot qualify a future-test package."""
from copy import deepcopy
import unittest

from research.research_os.expansion.source_qualification import qualify_source_route
from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness, READY
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.tests.test_producer_economic_readiness import _source_route


INVALID_CLOCKS = (None, "", " ", False, 0, [], {}, "not-a-clock", "2026-10-15", "2026-10-15T09:00:00")


class SourcePITClockTests(unittest.TestCase):
    def test_invalid_availability_or_freeze_never_qualifies_pit(self):
        for field in ("availability_start", "freeze_time"):
            for value in INVALID_CLOCKS:
                with self.subTest(field=field, value=value):
                    route = _source_route()
                    freeze = "2026-10-16T00:00:00Z"
                    if field == "availability_start":
                        route[field] = value
                    else:
                        freeze = value
                    before = deepcopy(route)
                    result = qualify_source_route(route, freeze_time=freeze)
                    self.assertEqual(result["status"], "BLOCK")
                    self.assertIn("AVAILABILITY_CLOCK_INVALID", result["blockers"])
                    self.assertFalse(result["point_in_time_qualified"])
                    self.assertEqual(route, before)

    def test_missing_availability_has_both_missing_and_pit_blockers(self):
        route = _source_route()
        del route["availability_start"]
        result = qualify_source_route(route, freeze_time="2026-10-16T00:00:00Z")
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("MISSING_AVAILABILITY_START", result["blockers"])
        self.assertIn("AVAILABILITY_CLOCK_INVALID", result["blockers"])
        self.assertFalse(result["point_in_time_qualified"])

    def test_explicit_offsets_compare_as_instants_without_rewriting_route(self):
        route = _source_route()
        route["availability_start"] = "2026-10-15T10:00:00+01:00"
        before = deepcopy(route)
        equal = qualify_source_route(route, freeze_time="2026-10-15T09:00:00Z")
        self.assertEqual(equal["status"], "PASS")
        self.assertTrue(equal["point_in_time_qualified"])
        self.assertEqual(equal["canonical_route"]["availability_start"], route["availability_start"])
        self.assertEqual(route, before)
        too_early = qualify_source_route(route, freeze_time="2026-10-15T08:59:59.999999Z")
        self.assertEqual(too_early["status"], "BLOCK")
        self.assertIn("ROUTE_NOT_AVAILABLE_AT_FREEZE", too_early["blockers"])
        self.assertFalse(too_early["point_in_time_qualified"])

    def test_readiness_cannot_promote_missing_or_naive_source_availability(self):
        for value in (None, "", "2026-10-15T09:00:00"):
            with self.subTest(value=value):
                package = fixture()
                package["sources"][0]["route"]["availability_start"] = value
                package["runner_meta"]["dataset_manifest_hash"] = sha256_json(package["sources"])
                before = deepcopy(package)
                result = economic_test_readiness(package, legacy=legacy())
                self.assertEqual(result["status"], "BLOCK")
                self.assertIn("AVAILABILITY_CLOCK_INVALID", result["block_reasons"])
                self.assertFalse(result["source_qualifications"][0]["point_in_time_qualified"])
                self.assertEqual(package, before)
                self.assertTrue(all(v is False for v in result["authority"].values()))
        self.assertEqual(economic_test_readiness(fixture(), legacy=legacy())["status"], READY)


if __name__ == "__main__":
    unittest.main()
