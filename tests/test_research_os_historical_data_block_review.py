"""Recovered data blocks require exact-ID review, never an economic KILL."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.worker_preflight import git_blob_sha, verify_materialized_legacy
from research.research_os.worker_stages import AUTHORITY, _screen

BASE = Path(__file__).resolve().parents[1] / 'research/research_os'


class HistoricalDataBlockReviewTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((BASE / 'legacy/source_manifest.json').read_text())
        self.blocked = [entry for entry in self.manifest['recovered_source_reviews']
                        if entry['classification'] == 'HISTORICAL_DATA_BLOCK_WITH_LIMITATIONS']
        self.assertEqual(len(self.blocked), 3)

    def test_exact_reported_ids_require_scoped_review_without_changing_ledger(self):
        ledger = {'records': [{'HYPOTHESIS_ID': 'ORIGINAL-FAMILY', 'RESEARCH_DECISION': 'PARK'}]}
        before = deepcopy([ledger, self.manifest])
        kb = LegacyKnowledgeBase(self.manifest, ledger)
        for entry in self.blocked:
            with self.subTest(historical_id=entry['historical_id']):
                result = kb.screen_candidate({'hypothesis_id': entry['historical_id'], 'mechanism': entry['mechanism']})
                self.assertEqual(result['status'], 'REVIEW_LEGACY_OVERLAP')
                match = result['recovered_source_matches'][0]
                self.assertEqual(match['researcher_decision'], 'PARK_DATA')
                self.assertEqual(match['judge_verdict'], 'NOT_REPORTED')
                self.assertEqual(match['scientific_equivalence'], 'NOT_ESTABLISHED')
                self.assertEqual(match['match_reason'], 'HISTORICAL_ID_REQUIRES_SCOPE_REVIEW')
                for key in ('failure_scope', 'limitations', 'revisit_conditions', 'source_refs'):
                    self.assertEqual(match[key], entry[key])
                match['limitations'].append('caller mutation')
        self.assertEqual(kb.summary()['loaded_record_count'], 1)
        self.assertEqual(kb.summary()['recovered_source_review_count'], 4)
        self.assertEqual(kb.summary()['global_effective_trials'], 'UNKNOWN')
        self.assertEqual(kb.summary()['reconciliation_status'], 'PARTIAL_WITH_EXPLICIT_GAPS')
        self.assertEqual([ledger, self.manifest], before)
        self.assertEqual(kb.source_reviews, before[1]['recovered_source_reviews'])
        self.assertEqual(kb.screen_candidate({'hypothesis_id': 'ORIGINAL-FAMILY'})['status'], 'BLOCK_EXACT_LEGACY_DUPLICATE')

    def test_similar_mechanism_does_not_inherit_another_protocols_data_block(self):
        kb = LegacyKnowledgeBase(dict(self.manifest, recovered_source_reviews=self.blocked))
        for entry in self.blocked:
            result = kb.screen_candidate({'hypothesis_id': 'DISTINCT-PROTOCOL', 'mechanism': entry['mechanism']})
            self.assertEqual(result['status'], 'NO_EXACT_LEGACY_CONFLICT')
            self.assertEqual(result['recovered_source_matches'], [])
        # Negative-result overlap retains its existing separate contract.
        negative = self.manifest['recovered_source_reviews'][0]
        result = LegacyKnowledgeBase(self.manifest).screen_candidate({'hypothesis_id': 'DISTINCT', 'mechanism': negative['mechanism']})
        self.assertEqual(result['status'], 'REVIEW_LEGACY_OVERLAP')
        self.assertEqual(result['recovered_source_matches'][0]['researcher_decision'], 'KILL')

    def test_mixed_dispositions_metrics_and_incomplete_scope_are_rejected(self):
        original = self.blocked[0]
        variants = [dict(original, researcher_decision='KILL'), dict(original, judge_verdict='REJECT'),
                    dict(original, researcher_decision='PASS'), dict(original, judge_verdict='PASS'),
                    dict(original, classification='HISTORICAL_NEGATIVE_WITH_LIMITATIONS'),
                    dict(original, raw_returns=[1]), dict(original, economic_experiment_authorized=True),
                    dict(original, revisit_conditions=[]), dict(original, limitations=[]),
                    dict(original, source_refs=[])]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaisesRegex(ValueError, 'LEGACY_SOURCE_REVIEW'):
                LegacyKnowledgeBase(dict(self.manifest, recovered_source_reviews=[variant]))

    def test_native_screen_preflight_and_restart_retain_the_same_recovered_evidence(self):
        ledger = {'schema_version': self.manifest['schema_version'], 'governance': self.manifest['governance'],
                  'records': [{'HYPOTHESIS_ID': 'UNRELATED'}]}
        data = json.dumps(ledger).encode()
        manifest = dict(self.manifest, ledger_blob_sha=git_blob_sha(data))
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'legacy').mkdir()
            (base / 'hypotheses').mkdir()
            (base / 'hypotheses/PEER.json').write_text(json.dumps({
                'hypothesis_id': 'PEER', 'generation_id': 'G1', 'issuer': 'PEER',
                'mechanism': 'semiconductor lithography backlog service capacity', 'authority': AUTHORITY}))
            (base / 'legacy/source_manifest.json').write_text(json.dumps(manifest))
            ledger_path = base / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json'
            ledger_path.write_bytes(data)
            for entry in self.blocked:
                candidate = {'hypothesis_id': entry['historical_id'], 'generation_id': 'G1',
                             'mechanism': entry['mechanism'], 'issuer': 'UNKNOWN', 'authority': AUTHORITY}
                first = _screen(SimpleNamespace(base=base), candidate)
                restarted = _screen(SimpleNamespace(base=Path(directory)), deepcopy(candidate))
                self.assertEqual(first, restarted)
                self.assertEqual(first['status'], 'BLOCK')
                self.assertEqual(first['block_reasons'], ['REVIEW_LEGACY_OVERLAP'])
                self.assertEqual(first['legacy']['recovered_source_matches'][0]['source_refs'], entry['source_refs'])
                proof = verify_materialized_legacy(base)
                self.assertEqual(proof['recovered_source_review_count'], 4)
                self.assertEqual(proof['recovered_source_reviews_hash'], first['legacy']['recovered_source_reviews_hash'])
            self.assertEqual(ledger_path.read_bytes(), data)
            self.assertEqual(candidate['authority'], AUTHORITY)

    def test_manifest_recovery_joins_existing_reported_metadata_and_blob_receipt(self):
        receipts = BASE / 'architecture/work_receipts'
        index = json.loads((receipts / 'BUILDER_CP_062_EDGE_REPORTED_STATUS_INDEX_20261021.json').read_text())
        proof = json.loads((receipts / 'BUILDER_CP_087_BLOCKED_HISTORY_SOURCE_BINDINGS_20261021.json').read_text())
        self.assertFalse(proof['result_payloads_read_this_checkpoint'])
        self.assertFalse(proof['numerical_economics_extracted'])
        self.assertFalse(proof['active_sealed_or_prospective_outcomes_accessed'])
        for entry in self.blocked:
            record = next(r for r in index['records'] if r['experiment_id_as_reported'] == entry['historical_id'])
            bound = next(r for r in proof['records'] if r['historical_id'] == entry['historical_id'])
            self.assertEqual(record['metadata']['typed_verdict'], 'PARK_DATA')
            self.assertEqual(entry['source_refs'], bound['source_refs'])
            self.assertEqual(entry['source_commit'], bound['source_commit'])
            self.assertEqual(bound['metadata'], record['metadata'])
            self.assertEqual(bound['original_execution_commit'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
