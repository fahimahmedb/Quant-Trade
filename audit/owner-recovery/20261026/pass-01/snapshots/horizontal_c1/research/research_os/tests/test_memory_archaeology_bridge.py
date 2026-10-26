from __future__ import annotations
import json
import unittest
from pathlib import Path

from research.research_os.archaeology import ArchaeologyCatalog
from research.research_os.memory_archaeology_bridge import bind_qualified_provenance, supersession_proof_refs
from research.research_os.scientific_memory import normalize_legacy_record

CATALOG = Path(__file__).parents[1] / "legacy" / "archaeology_source_catalog.json"


def f2_memory():
    legacy={
        "RESEARCH_FAMILY_ID":"f2-family","HYPOTHESIS_ID":"F2-KALSHI-FLB-OOS","LEGACY_ID_IF_ANY":"UNKNOWN",
        "GENERATION_ID":"G1-BLOCKED","MECHANISM":"behavioral favorite-longshot mispricing","RESULT_OBSERVED_AT":"2026-10-09",
        "UNIVERSE":"Kalshi binary markets","HORIZON":"pre-look","RESULT":"BLOCKED_DATA_PERMISSION",
        "RESULT_ARTIFACT":"research/kalshi_flb_f2/TERMS_DECISION_2026-10-09.md","RESULT_COMMIT":"abcdef1234567890abcdef1234567890abcdef12",
        "ECONOMIC_EVIDENCE":"NONE_NEW","STATISTICAL_EVIDENCE":"NONE_NEW","FALSIFICATION_SCOPE":"NONE","RESEARCH_DECISION":"PARK",
        "KNOWN_ATTEMPTS":0,"OPEN_BLOCKERS":["documented rights"],"PROVENANCE":["historical:f2"],
    }
    manifest={"source_commit":"183ad65ff260b903a16548ce37948f54d47a9ec8","ledger_blob_sha":"ba9b165aaf96956776672df51233bb9bf1e6cbc9"}
    return normalize_legacy_record(legacy,manifest)


class MemoryArchaeologyBridgeTests(unittest.TestCase):
    def setUp(self):
        self.catalog=ArchaeologyCatalog.load(CATALOG)

    def test_matching_binding_only_adds_provenance(self):
        memory=f2_memory(); finding=self.catalog.query(subject_id="F2-KALSHI-FLB-OOS")[0]
        protected={k:json.loads(json.dumps(memory[k])) for k in ("scientific_disposition","epistemic_status","claim_ceiling","evidence","identity")}
        bound=bind_qualified_provenance(memory,finding)
        self.assertGreater(len(bound["provenance"]),len(memory["provenance"]))
        self.assertTrue(any(x["kind"]=="ARCHAEOLOGY_IMMUTABLE_SOURCE" for x in bound["provenance"]))
        for key,value in protected.items(): self.assertEqual(bound[key],value)

    def test_wrong_subject_binding_fails_closed(self):
        weather=self.catalog.query(subject_id="WEATHER-FORWARD-V2-PROTOCOL")[0]
        with self.assertRaisesRegex(ValueError,"does not match"):
            bind_qualified_provenance(f2_memory(),weather)

    def test_supersession_refs_require_explicit_disposition(self):
        f2=self.catalog.query(subject_id="F2-KALSHI-FLB-OOS")[0]
        with self.assertRaises(ValueError): supersession_proof_refs(f2)
        synthetic=dict(f2); synthetic["archaeology_id"]="arch-f2-superseded"; synthetic["history_disposition"]="SUPERSEDED_WITH_PROOF"; synthetic["supersedes_subject_ids"]=["F2-OLD"]
        refs=supersession_proof_refs(synthetic)
        self.assertTrue(refs); self.assertTrue(all(x.startswith(("blob:","commit:")) for x in refs))


if __name__=="__main__": unittest.main()
