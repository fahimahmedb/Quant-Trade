#!/usr/bin/env python3
"""Construit, sans l'executer, le contexte d'operation D2 (avant prise d'effet de E) et les epingles finales.

Entrees : les trois documents geles, les constantes de E (B.1 a B.4) et les blobs du candidat root.
Sorties : frozen/operation_context_d2_pre_effect_v1.json, frozen/final_pins_d2_v1.json, frozen/final_pins_d2_v1.tsv (meme contenu, pour les scripts d'hote ; le contexte est ecrit d'abord, ses blobs entrent dans les epingles).
Aucun appel au harnais, aucune ecriture hors des deux sorties, aucun lancement du script d'operation.
Regle d'activation (E B.3) : le contexte d'activation (lot 4) ne differe du present que par
read_authorization.state, de "UNRESOLVED" a "AUTHORIZED"; toute autre difference est un defaut.
Usage : python3 -I build_context_d2.py <racine_a2_operation> (ecrit dans <racine>/frozen/)
"""
import hashlib
import json
import os
import sys

E_SHA = "6e0320f15d48a924cef9507af5641e47de9fe938"
C_SHA = "37e3b25f17a7c5d3b3bc8d37df730aa988585b6c"
HARNESS_BLOBS = {  # candidat 73280c3e9d8604b2f2d8e6d2d174aa940389a760
    "__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
    "contract.py": "f6f94a4a472e3f6652a1502f6afb5825721364d0",
    "harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
    "trusted_root.py": "9704a844bae0ef54637c76dded5bb82d9f4c334f",
}
EXECUTOR = {"actor_id": "blue.weather-v4.a2.doc-integration.v1", "role": "EXECUTOR"}
RECIPIENT = {"actor_id": "project-owner.weather-v4.a2.doc-integration.v1", "role": "RESEARCH_VIEWER"}
APPROVER = {"actor_id": "astra.weather-v4.a2.doc-integration.v1", "role": "RELEASE_APPROVER"}


def load(root, name):
    return json.load(open(os.path.join(root, "frozen", name), encoding="utf-8"))


def build(root):
    return {
        "schema": "A2_DOC_INTEGRATION_OPERATION_CONTEXT_V1",
        "branch": "D2",
        "output_directory": "/srv/a2out",
        "result_file_name": "a2-doc-v1-d2-input-result-001.json",
        "harness_source_blobs": dict(HARNESS_BLOBS),
        "authority_binding": {
            "owner_authority_sha": C_SHA,
            "harness_identity": "research/weather_forward/v4/a2_harness",
            "harness_version_or_commit_identity": "weather-v4-a2-doc-integration-v1",
            "manifest_version_identity": "A2-DOC-INTEGRATION-MANIFEST-V1",
        },
        "input_manifest": load(root, "input_manifest_d2_v1.json"),
        "output_manifest": load(root, "output_manifest_d2_v1.json"),
        "policy": load(root, "harness_policy_d2_v1.json"),
        "execution_authority_sha": E_SHA,
        "executor": dict(EXECUTOR),
        "recipient": dict(RECIPIENT),
        "approver": dict(APPROVER),
        "read_authorization": {
            "authorization_id": "a2-doc-v1-read-input-blue",
            "authority_sha": E_SHA,
            "actor_id": EXECUTOR["actor_id"],
            "declared_role": "EXECUTOR",
            "action": "READ_INPUT",
            "state": "UNRESOLVED",  # AUTHORIZED seulement a la prise d'effet d'E (lot 4)
        },
        "release": None,
        "log": {"input_record_id": "a2-doc-v1-d2-log-input-read-001",
                "output_record_id": None, "incident_identifier": None},
        "accepted_detail_codes": ["INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED"],
    }


OPERATION_SOURCES = (
    "__init__.py", "common/__init__.py", "common/bounded_output.py", "identity/__init__.py",
    "identity/identity_via_harness.py", "operation/__init__.py",
    "operation/a2_doc_integration_operation.py",
)


def git_blob(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def build_pins(root):
    """Epingles finales (E B.5(f)) : 4 fichiers du harnais (candidat), 7 sources d'operation, contexte, profil d'unite."""
    base = "research/weather_forward/v4/"
    sources = {base + "a2_harness/" + name: blob for name, blob in HARNESS_BLOBS.items()}
    for rel in OPERATION_SOURCES:
        sources[base + "a2_operation/" + rel] = git_blob(os.path.join(root, rel))
    sources[base + "a2_operation/common/a2_unit_profile.sh"] = git_blob(
        os.path.join(root, "common", "a2_unit_profile.sh"))
    sources[base + "a2_operation/frozen/operation_context_d2_pre_effect_v1.json"] = git_blob(
        os.path.join(root, "frozen", "operation_context_d2_pre_effect_v1.json"))
    return {"mode": "L2_J_FINAL_D2_PRE_EFFECT", "schema": "A2_FINAL_SOURCE_PINS_V1",
            "candidate_commit": "73280c3e9d8604b2f2d8e6d2d174aa940389a760",
            "execution_authority_sha": E_SHA, "sources": sources}


def dump(obj):
    return json.dumps(obj, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    path = os.path.join(root, "frozen", "operation_context_d2_pre_effect_v1.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(dump(build(root)))
    print("ecrit", path)
    pins = os.path.join(root, "frozen", "final_pins_d2_v1.json")
    with open(pins, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(dump(build_pins(root)))
    print("ecrit", pins)
    tsv = os.path.join(root, "frozen", "final_pins_d2_v1.tsv")
    with open(tsv, "w", encoding="utf-8", newline="\n") as handle:
        for path, blob in sorted(build_pins(root)["sources"].items()):
            handle.write(f"{blob}\t{path}\n")
    print("ecrit", tsv)


if __name__ == "__main__":
    main()
