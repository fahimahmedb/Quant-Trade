"""Transcribe D2 manifest declarations from the Blue dossier tables (L2-C / L2-D).

Reads only the dossier file given on the command line, after checking that its
git blob id is exactly the pinned dossier D blob. Converts the actual-field
tables of section 14.2A (InputManifest, 17 fields) and 14.2B (OutputManifest,
13 fields) into ``A2_FROZEN_CONTENT_V1`` documents.

The only permitted state transition is the input
``efficacy_leakage_assessment``: ``LeakageAssessment.UNRESOLVED`` becomes
``CLEAR`` (Astra lot-1 finding INPUT_LEAKAGE_FINDING = CLEAR_SUPPORTED, adopted
by Owner). The output manifest is transcribed unchanged (route D2).

No digest is computed. The name ``frozen`` in the output path is not a freeze:
a freeze is the Owner ratification of the exact published file.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

DOSSIER_D_BLOB = "c3271812aa7ad67747916afa0c64344aec36590d"
SCHEMA = "A2_FROZEN_CONTENT_V1"
INPUT_TRANSITION_FIELD = "efficacy_leakage_assessment"

INPUT_FIELDS = (
    "input_id", "manifest_version_identity", "input_classification", "source_provenance_class",
    "exact_permitted_fields", "exact_prohibited_fields", "permitted_reader_roles",
    "raw_values_visible", "timestamps_visible", "frequency_or_count_information_visible",
    "longitudinal_observation_allowed", "aggregation_allowed", "cross_source_comparison_allowed",
    "efficacy_leakage_assessment", "access_logging_requirement", "quarantine_on_ambiguity",
    "owner_approval_required",
)
OUTPUT_FIELDS = (
    "output_id", "manifest_version_identity", "output_type", "exact_metric_or_artifact",
    "granularity", "permitted_recipients", "exportability", "quarantine_status",
    "cumulative_disclosure_risk", "efficacy_leakage_assessment", "release_approval_requirement",
    "retention_rule", "incident_if_unexpected_information_revealed",
)

# Fields that hold a tuple of strings / enum members / a single enum member.
TEXT_TUPLES = {"exact_permitted_fields", "exact_prohibited_fields"}
ENUM_TUPLES = {"permitted_reader_roles", "permitted_recipients"}
PLAIN_TEXT = {
    "input_id", "manifest_version_identity", "source_provenance_class", "output_id",
    "output_type", "exact_metric_or_artifact", "granularity", "retention_rule",
    "incident_if_unexpected_information_revealed",
}

_ROW = re.compile(r"^\| `([a-z_]+)` \| `(.*)` \|$")
_ENUM = re.compile(r"^([A-Za-z]+)\.([A-Z_]+)$")


class TranscriptionError(ValueError):
    """The dossier text does not have the expected exact structure."""


def git_blob_id(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def read_dossier(path: Path) -> list[str]:
    raw = path.read_bytes()
    if git_blob_id(raw) != DOSSIER_D_BLOB:
        raise TranscriptionError("DOSSIER_BLOB_IS_NOT_THE_PINNED_D_BLOB")
    return raw.decode("utf-8").splitlines()


def table_rows(lines: list[str], start_prefix: str, end_prefix: str) -> list[tuple[str, str]]:
    start = next(i for i, line in enumerate(lines) if line.startswith(start_prefix))
    end = next(i for i, line in enumerate(lines) if line.startswith(end_prefix) and i > start)
    rows = []
    for line in lines[start:end]:
        if not line.startswith("| `"):
            continue
        match = _ROW.match(line)
        if match is None:
            raise TranscriptionError("ROW_DOES_NOT_MATCH_EXPECTED_SHAPE")
        rows.append((match.group(1), match.group(2)))
    return rows


def enum_value(cell: str) -> str:
    match = _ENUM.match(cell)
    if match is None:
        raise TranscriptionError("ENUM_CELL_EXPECTED")
    return match.group(2)


def parse_tuple_cell(cell: str) -> list[str]:
    if not (cell.startswith("(") and cell.endswith(")")):
        raise TranscriptionError("TUPLE_CELL_EXPECTED")
    inner = cell[1:-1]
    if inner.endswith(","):
        inner = inner[:-1]
    return [part for part in inner.split(", ")]


def convert(name: str, cell: str):
    if name in PLAIN_TEXT:
        return cell
    if name in TEXT_TUPLES:
        return parse_tuple_cell(cell)
    if name in ENUM_TUPLES:
        return [enum_value(item) for item in parse_tuple_cell(cell)]
    return enum_value(cell)


def build_document(kind: str, expected_fields, rows, *, input_transition: bool) -> dict:
    if tuple(name for name, _ in rows) != expected_fields:
        raise TranscriptionError("FIELD_NAMES_OR_ORDER_DIFFER_FROM_HARNESS_DATACLASS")
    fields = {name: convert(name, cell) for name, cell in rows}
    if input_transition:
        if fields[INPUT_TRANSITION_FIELD] != "UNRESOLVED":
            raise TranscriptionError("TRANSITION_SOURCE_VALUE_IS_NOT_UNRESOLVED")
        fields[INPUT_TRANSITION_FIELD] = "CLEAR"
    return {"schema": SCHEMA, "kind": kind, "fields": fields}


def build_documents(lines: list[str]) -> tuple[dict, dict]:
    input_rows = table_rows(lines, "#### 14.2A", "#### 14.2B")
    output_rows = table_rows(lines, "#### 14.2B", "#### 14.2C")
    return (
        build_document("InputManifest", INPUT_FIELDS, input_rows, input_transition=True),
        build_document("OutputManifest", OUTPUT_FIELDS, output_rows, input_transition=False),
    )


def encode(document: dict) -> bytes:
    return (json.dumps(document, ensure_ascii=True, indent=2) + "\n").encode("ascii")


def main(argv) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: transcribe_frozen_from_dossier.py <dossier_D.md> <input.json> <output.json>")
    input_document, output_document = build_documents(read_dossier(Path(argv[0])))
    for path, document in ((argv[1], input_document), (argv[2], output_document)):
        target = Path(path)
        if target.exists():
            raise SystemExit("REFUSING_TO_OVERWRITE:" + path)
        target.write_bytes(encode(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
