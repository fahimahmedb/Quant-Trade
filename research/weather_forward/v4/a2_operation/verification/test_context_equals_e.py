"""Q23 / Astra J-1 : tests statiques d'egalite entre le contexte D2 final et E.

Aucun lancement du script d'operation, aucun appel au harnais, aucune evaluation. Verifie seulement
que le contexte et les epingles publies sont exactement ce que E (6e0320f1...) decrit.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from research.weather_forward.v4.a2_operation.identity import identity_stdlib as independent
from research.weather_forward.v4.a2_operation.operation import a2_doc_integration_operation as op

ROOT = Path(__file__).resolve().parents[1]
E_SHA = "6e0320f15d48a924cef9507af5641e47de9fe938"
C_SHA = "37e3b25f17a7c5d3b3bc8d37df730aa988585b6c"
E_TABLE_A = {  # E section A : (fichier, blob, identite)
    "input_manifest": ("input_manifest_d2_v1.json", "f85205f33a232de6fabd83c17c52a25d4634e374",
                       "sha256:5c55b855b91a5c2b0bde86f3c0888905b500c086309a761ff454644d0cfbbd00"),
    "output_manifest": ("output_manifest_d2_v1.json", "7651de7e718a276b596f2256aff0877e771e5d6d",
                        "sha256:b8157e4e15b4e03813b0ff43d52a2319ea589fc9aab9429f1c2894bcce990976"),
    "policy": ("harness_policy_d2_v1.json", "6a1fa30fac327c0183b2931550bd4c730195529c",
               "sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60"),
}
CANDIDATE_TRUSTED_ROOT_BLOB = "9704a844bae0ef54637c76dded5bb82d9f4c334f"


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def diff_paths(a, b, prefix=""):
    if type(a) is not type(b):
        return [prefix]
    if isinstance(a, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{prefix}/{key}")
            else:
                out += diff_paths(a[key], b[key], f"{prefix}/{key}")
        return out
    return [] if a == b else [prefix]


class ContextEqualsE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "frozen" / "operation_context_d2_pre_effect_v1.json").read_text(encoding="utf-8")
        cls.context = op.decode_context(cls.text)
        cls.pins = json.loads((ROOT / "frozen" / "final_pins_d2_v1.json").read_text(encoding="utf-8"))

    def test_context_is_structurally_valid_d2(self):
        op.validate_context(self.context)
        self.assertEqual(self.context["branch"], "D2")
        self.assertIsNone(self.context["release"])
        self.assertIsNone(self.context["log"]["output_record_id"])
        self.assertIsNone(self.context["log"]["incident_identifier"])

    def test_frozen_files_blobs_and_identities_equal_e_table_a(self):
        for key, (name, expected_blob, expected_identity) in E_TABLE_A.items():
            path = ROOT / "frozen" / name
            self.assertEqual(blob(path), expected_blob, name)
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(self.context[key], document, key)
            self.assertEqual(independent.identity(document), expected_identity, key)

    def test_authority_shas_equal_e_and_c(self):
        self.assertEqual(self.context["execution_authority_sha"], E_SHA)
        self.assertEqual(self.context["read_authorization"]["authority_sha"], E_SHA)
        self.assertEqual(self.context["authority_binding"]["owner_authority_sha"], C_SHA)
        self.assertEqual(self.context["authority_binding"]["harness_version_or_commit_identity"],
                         "weather-v4-a2-doc-integration-v1")
        self.assertEqual(self.context["authority_binding"]["manifest_version_identity"],
                         "A2-DOC-INTEGRATION-MANIFEST-V1")

    def test_e_b3_b4_values_exact(self):
        c = self.context
        self.assertEqual(c["read_authorization"]["authorization_id"], "a2-doc-v1-read-input-blue")
        self.assertEqual((c["read_authorization"]["action"], c["read_authorization"]["declared_role"]),
                         ("READ_INPUT", "EXECUTOR"))
        self.assertEqual(c["executor"], {"actor_id": "blue.weather-v4.a2.doc-integration.v1", "role": "EXECUTOR"})
        self.assertEqual(c["recipient"], {"actor_id": "project-owner.weather-v4.a2.doc-integration.v1",
                                          "role": "RESEARCH_VIEWER"})
        self.assertEqual(c["approver"], {"actor_id": "astra.weather-v4.a2.doc-integration.v1",
                                         "role": "RELEASE_APPROVER"})
        self.assertEqual(c["log"]["input_record_id"], "a2-doc-v1-d2-log-input-read-001")
        self.assertEqual((c["output_directory"], c["result_file_name"]),
                         ("/srv/a2out", "a2-doc-v1-d2-input-result-001.json"))
        self.assertEqual(c["accepted_detail_codes"], ["INPUT_READ_ELIGIBLE_LOGGED_AND_COMPLETED"])

    def test_pre_effect_state_is_not_authorized_and_activation_differs_only_there(self):
        self.assertEqual(self.context["read_authorization"]["state"], "UNRESOLVED")
        activation = deepcopy(self.context)
        activation["read_authorization"]["state"] = "AUTHORIZED"
        op.validate_context(activation)
        self.assertEqual(diff_paths(self.context, activation), ["/read_authorization/state"])

    def test_harness_blobs_are_the_candidate_and_match_pins(self):
        blobs = self.context["harness_source_blobs"]
        self.assertEqual(blobs["trusted_root.py"], CANDIDATE_TRUSTED_ROOT_BLOB)
        base = "research/weather_forward/v4/a2_harness/"
        for name, value in blobs.items():
            self.assertEqual(self.pins["sources"][base + name], value, name)
        self.assertEqual(self.pins["candidate_commit"], "73280c3e9d8604b2f2d8e6d2d174aa940389a760")
        self.assertEqual(self.pins["execution_authority_sha"], E_SHA)

    def test_final_pins_list_exactly_e_5f_objects_and_match_disk(self):
        sources = self.pins["sources"]
        self.assertEqual(len(sources), 13)  # 4 harnais + 7 sources d'operation + contexte + profil d'unite
        base = "research/weather_forward/v4/a2_operation/"
        on_disk = {k: v for k, v in sources.items() if k.startswith(base)}
        self.assertEqual(len(on_disk), 9)
        for key, value in on_disk.items():
            self.assertEqual(blob(ROOT / key[len(base):]), value, key)
        for parts in op.OPERATION_SOURCE_FILES:
            self.assertIn("/".join(parts), sources)
        self.assertIn(base + "common/a2_unit_profile.sh", sources)
        self.assertIn(base + "frozen/operation_context_d2_pre_effect_v1.json", sources)

    def test_adversarial_mutations_are_detected(self):
        for path, value in (("/execution_authority_sha", "0" * 40),
                            ("/authority_binding/owner_authority_sha", E_SHA)):
            mutated = deepcopy(self.context)
            node = mutated
            keys = path.strip("/").split("/")
            for key in keys[:-1]:
                node = node[key]
            node[keys[-1]] = value
            self.assertEqual(diff_paths(self.context, mutated), [path])
        mutated = deepcopy(self.context)
        mutated["release"] = {"authorization": None, "approval_artifact": None, "ledger": None}
        with self.assertRaises(op.ContextError):
            op.validate_context(mutated)  # D2 interdit toute section release
        mutated = deepcopy(self.context)
        mutated["log"]["output_record_id"] = "a2-doc-v1-d2-log-output-001"
        with self.assertRaises(op.ContextError):
            op.validate_context(mutated)  # D2 interdit un identifiant de sortie

    def test_text_is_canonical_and_duplicate_keys_rejected(self):
        self.assertEqual(self.text, json.dumps(self.context, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
        with self.assertRaises(op.ContextError):
            op.decode_context('{"a": 1, "a": 2}')


if __name__ == "__main__":
    unittest.main()
