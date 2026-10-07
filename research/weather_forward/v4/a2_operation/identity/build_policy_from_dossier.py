"""Build the HarnessPolicy frozen-content document (L2-F) from dossier D section 14.2C.

Ten values come from the dossier table (blob pinned in transcribe_frozen_from_dossier).
The two ``DERIVE_...`` cells are replaced by the identities passed on the command
line, which must be the identities of the frozen manifests agreed by both
derivation ways. ``fixture_provenance_contract`` must be ``None`` in the dossier.
No digest is computed here.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from research.weather_forward.v4.a2_operation.identity import transcribe_frozen_from_dossier as t

POLICY_FIELDS = (
    "expected_owner_authority_sha", "expected_harness_identity",
    "expected_harness_version_or_commit_identity", "expected_manifest_version_identity",
    "expected_input_manifest_id", "expected_input_manifest_identity",
    "expected_output_manifest_id", "expected_output_manifest_identity",
    "allowed_input_classifications", "prohibited_input_classifications",
    "fixture_provenance_contract", "permitted_recipient_actor_roles",
)
DERIVE_LABELS = {
    "expected_input_manifest_identity": "DERIVE_FROM_FROZEN_INPUT_MANIFEST_ONLY_WHEN_AUTHORIZED",
    "expected_output_manifest_identity": "DERIVE_FROM_FROZEN_OUTPUT_MANIFEST_ONLY_WHEN_AUTHORIZED",
}
_IDENTITY = re.compile(r"^sha256:[0-9a-f]{64}$")
_PAIR = re.compile(r"\(([^,()]+), Role\.([A-Z_]+)\)")


def build(lines, input_identity, output_identity):
    rows = t.table_rows(lines, "#### 14.2C", "#### 14.2D")
    if tuple(name for name, _ in rows) != POLICY_FIELDS:
        raise t.TranscriptionError("POLICY_FIELDS_OR_ORDER_DIFFER")
    supplied = {"expected_input_manifest_identity": input_identity,
                "expected_output_manifest_identity": output_identity}
    fields = {}
    for name, cell in rows:
        if name in DERIVE_LABELS:
            if cell != DERIVE_LABELS[name] or not _IDENTITY.match(supplied[name]):
                raise t.TranscriptionError("DERIVE_CELL_OR_IDENTITY_INVALID")
            fields[name] = supplied[name]
        elif name == "fixture_provenance_contract":
            if cell != "None":
                raise t.TranscriptionError("ONLY_NONE_FIXTURE_CONTRACT_SUPPORTED")
            fields[name] = None
        elif name == "permitted_recipient_actor_roles":
            pairs = _PAIR.findall(cell)
            if not pairs or cell != "(" + ", ".join(f"({a}, Role.{r})" for a, r in pairs) + ",)":
                raise t.TranscriptionError("RECIPIENT_PAIR_SHAPE_UNEXPECTED")
            fields[name] = [[a, r] for a, r in pairs]
        elif name in ("allowed_input_classifications", "prohibited_input_classifications"):
            fields[name] = [t.enum_value(item) for item in t.parse_tuple_cell(cell)]
        else:
            fields[name] = cell
    return {"schema": t.SCHEMA, "kind": "HarnessPolicy", "fields": fields}


def main(argv) -> int:
    if len(argv) != 4:
        raise SystemExit("usage: build_policy_from_dossier.py <dossier_D.md> <input_identity> <output_identity> <out.json>")
    document = build(t.read_dossier(Path(argv[0])), argv[1], argv[2])
    target = Path(argv[3])
    if target.exists():
        raise SystemExit("REFUSING_TO_OVERWRITE:" + argv[3])
    target.write_bytes(t.encode(document))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
