"""Schema drift checks for Builder C evidence and PIT identity contracts."""

from __future__ import annotations

import dataclasses
import json
import unittest
from pathlib import Path

from quant.dataplane.corporate_actions import CorporateActionEvent, CorporateActionLeg
from quant.dataplane.evidence import DerivedArtifact, RawObject, ValidatedObject
from quant.dataplane.identity import (
    IssuerIdentity,
    IssuerNameInterval,
    ListingInterval,
    SecurityIdentity,
    TickerInterval,
)


ROOT = Path(__file__).resolve().parents[1]


def load_schema(name: str) -> dict[str, object]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def field_names(cls: type) -> set[str]:
    return {field.name for field in dataclasses.fields(cls)}


class BuilderCSchemaTests(unittest.TestCase):
    def test_evidence_schema_properties_match_dataclasses(self) -> None:
        cases = (
            (RawObject, "raw_object.schema.json"),
            (ValidatedObject, "validated_object.schema.json"),
            (DerivedArtifact, "derived_artifact.schema.json"),
        )
        for cls, filename in cases:
            with self.subTest(filename=filename):
                schema = load_schema(filename)
                self.assertEqual(set(schema["properties"]), field_names(cls))
                self.assertEqual(set(schema["required"]), field_names(cls))
                self.assertFalse(schema["additionalProperties"])

    def test_identity_schema_properties_match_pit_dataclasses(self) -> None:
        cases = (
            (IssuerIdentity, "issuer_identity.schema.json"),
            (IssuerNameInterval, "issuer_name_interval.schema.json"),
            (SecurityIdentity, "security_identity.schema.json"),
            (TickerInterval, "ticker_interval.schema.json"),
            (ListingInterval, "listing_interval.schema.json"),
        )
        for cls, filename in cases:
            with self.subTest(filename=filename):
                schema = load_schema(filename)
                self.assertEqual(set(schema["properties"]), field_names(cls))
                self.assertFalse(schema["additionalProperties"])

    def test_corporate_action_schemas_cover_event_and_leg_fields(self) -> None:
        event_schema = load_schema("corporate_action_event.schema.json")
        leg_schema = load_schema("corporate_action_leg.schema.json")
        self.assertEqual(set(event_schema["properties"]), field_names(CorporateActionEvent))
        self.assertEqual(set(leg_schema["properties"]), field_names(CorporateActionLeg))
        embedded_leg = event_schema["properties"]["legs"]["items"]
        self.assertEqual(set(embedded_leg["properties"]), field_names(CorporateActionLeg))
        self.assertFalse(event_schema["additionalProperties"])
        self.assertFalse(leg_schema["additionalProperties"])
        self.assertFalse(embedded_leg["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
