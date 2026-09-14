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
            (RawObject, "evidence_raw_object.schema.json"),
            (ValidatedObject, "evidence_validated_object.schema.json"),
            (DerivedArtifact, "evidence_derived_artifact.schema.json"),
        )
        for cls, filename in cases:
            with self.subTest(filename=filename):
                schema = load_schema(filename)
                self.assertEqual(set(schema["properties"]), field_names(cls))
                self.assertEqual(set(schema["required"]), field_names(cls))
                self.assertFalse(schema["additionalProperties"])

    def test_identity_schema_definitions_match_pit_contracts(self) -> None:
        schema = load_schema("security_identity_contracts.schema.json")
        definitions = schema["definitions"]
        cases = (IssuerIdentity, IssuerNameInterval, SecurityIdentity, TickerInterval, ListingInterval)
        self.assertEqual({cls.__name__ for cls in cases}, set(definitions))
        for cls in cases:
            with self.subTest(contract=cls.__name__):
                definition = definitions[cls.__name__]
                self.assertEqual(set(definition["properties"]), field_names(cls))
                self.assertFalse(definition["additionalProperties"])

    def test_corporate_action_schema_covers_event_and_leg_fields(self) -> None:
        schema = load_schema("dataplane_corporate_actions.schema.json")
        self.assertEqual(set(schema["properties"]), field_names(CorporateActionEvent))
        leg = schema["properties"]["legs"]["items"]
        self.assertEqual(set(leg["properties"]), field_names(CorporateActionLeg))
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(leg["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
