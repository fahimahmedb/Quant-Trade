"""Generate JSON Schemas for the core persistent state objects.

``SYSTEM_ARCHITECTURE.md`` requires explicit contracts for the system's state
objects. Writing them by hand guarantees they drift from the code, so they are
derived from the dataclasses themselves and a test fails if the committed
schemas stop matching.

    python3 scripts/generate_schemas.py [--check]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import types
import typing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.book.ledger import LedgerState, Position  # noqa: E402
from quant.clock import ControlState  # noqa: E402
from quant.dataplane.registry import DatasetRecord  # noqa: E402
from quant.dataplane.sec.collector import CollectorState  # noqa: E402
from quant.dataplane.sec.store import (SecAcquisitionEnvelope, SecAttemptRecord,  # noqa: E402
                                       SecRawObjectRecord, SecSourceVersionRecord)
from quant.desk.opportunity import OpportunityTicket  # noqa: E402
from quant.events import SystemEvent  # noqa: E402
from quant.factory.strategies import StrategyDefinition  # noqa: E402
from quant.learning.store import BuildTask  # noqa: E402
from quant.state import ComponentStatus  # noqa: E402

OBJECTS = {
    "book_state": (LedgerState, "Persistent economic state of one ledger."),
    "position": (Position, "One open position inside a ledger."),
    "opportunity_ticket": (OpportunityTicket,
                           "Lifecycle of one paper/shadow opportunity through "
                           "SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK."),
    "strategy_definition": (StrategyDefinition,
                            "Versioned strategy, its evidence and its lifecycle."),
    "dataset_record": (DatasetRecord, "Data lineage, validation and availability."),
    "system_event": (SystemEvent, "Append-only trace entry for status and audit."),
    "control_state": (ControlState, "Control Plane lifetime and cursors."),
    "component_status": (ComponentStatus, "RUN/IDLE/BLOCKED/FAULT/PAUSED per function."),
    "build_task": (BuildTask, "A capability gap the system raised for the Build Plane."),
    "sec_attempt_record": (SecAttemptRecord,
                           "One SEC request attempt. The Day-1 liveness record, "
                           "written whether or not bytes were received, carrying "
                           "an opaque locator digest rather than an identifying "
                           "locator."),
    "sec_raw_object_record": (SecRawObjectRecord,
                              "One immutable raw response body: content address, "
                              "byte length, receipt time, transport metadata and "
                              "the capture/visibility/admissibility states."),
    "sec_acquisition_envelope": (SecAcquisitionEnvelope,
                                 "Binds one source identity to one immutable raw "
                                 "object. The durable acknowledgement, and the "
                                 "record that keeps source publication time "
                                 "distinct from local receipt time."),
    "sec_source_version": (SecSourceVersionRecord,
                           "Every observation of a source identity's bytes, so "
                           "differing bytes become an explicit conflict version "
                           "instead of a silent replacement."),
    "sec_collector_state": (CollectorState,
                            "Durable capture-lane state: continuity cursor, "
                            "coverage verdict, open gaps, queued work and "
                            "reconciliation progress."),
}

PRIMITIVES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def json_type(annotation: typing.Any) -> dict[str, typing.Any]:
    origin = typing.get_origin(annotation)
    if origin in (typing.Union, types.UnionType):
        parts = [json_type(arg) for arg in typing.get_args(annotation)
                 if arg is not type(None)]
        nullable = any(arg is type(None) for arg in typing.get_args(annotation))
        base = parts[0] if parts else {"type": "string"}
        if nullable:
            kinds = base.get("type", "string")
            base = dict(base)
            base["type"] = [kinds, "null"] if isinstance(kinds, str) else list(kinds) + ["null"]
        return base
    if origin in (list, tuple):
        args = typing.get_args(annotation)
        return {"type": "array", "items": json_type(args[0]) if args else {}}
    if origin is dict:
        args = typing.get_args(annotation)
        return {"type": "object",
                "additionalProperties": json_type(args[1]) if len(args) > 1 else True}
    if annotation in PRIMITIVES:
        return {"type": PRIMITIVES[annotation]}
    return {}


def schema_for(name: str, cls: type, description: str) -> dict[str, typing.Any]:
    hints = typing.get_type_hints(cls)
    properties, required = {}, []
    for field in dataclasses.fields(cls):
        properties[field.name] = json_type(hints.get(field.name, typing.Any))
        if (field.default is dataclasses.MISSING
                and field.default_factory is dataclasses.MISSING):  # type: ignore[misc]
            required.append(field.name)
    return {"$schema": "http://json-schema.org/draft-07/schema#",
            "title": name, "description": description, "type": "object",
            "properties": properties, "required": required,
            "additionalProperties": False}


def generate() -> dict[str, dict[str, typing.Any]]:
    return {name: schema_for(name, cls, description)
            for name, (cls, description) in OBJECTS.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed schemas are stale")
    args = parser.parse_args()
    stale = []
    for name, schema in generate().items():
        path = ROOT / "schemas" / f"{name}.schema.json"
        rendered = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                stale.append(name)
        else:
            path.write_text(rendered, encoding="utf-8")
    if args.check and stale:
        print("stale schemas: " + ", ".join(stale))
        return 1
    print("schemas checked" if args.check else f"wrote {len(OBJECTS)} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
