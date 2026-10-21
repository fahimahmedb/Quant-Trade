"""Historical provenance reaches the existing screen without rewriting science."""
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


class HistoricalSourceRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((BASE / 'legacy/source_manifest.json').read_text())
        self.review = self.manifest['recovered_source_reviews'][0]

    def test_original_id_and_mechanism_route_to_scoped_review_not_scientific_kill(self):
        kb = LegacyKnowledgeBase(self.manifest)
        for candidate in ({'hypothesis_id': 'P0-E1'},
                          {'hypothesis_id': 'DIFFERENT', 'mechanism': self.review['mechanism']}):
            result = kb.screen_candidate(candidate)
            self.assertEqual(result['status'], 'REVIEW_LEGACY_OVERLAP')
            match = result['recovered_source_matches'][0]
            self.assertEqual(match['failure_scope'], self.review['failure_scope'])
            self.assertEqual(match['limitations'], self.review['limitations'])
            self.assertEqual(match['revisit_conditions'], self.review['revisit_conditions'])
            self.assertEqual(match['source_refs'], self.review['source_refs'])
            self.assertEqual(match['scientific_equivalence'], 'NOT_ESTABLISHED')
            match['source_refs'][0]['blob_sha'] = 'corrupted-return-value'
            self.assertEqual(kb.source_reviews[0], self.review)
        self.assertEqual(kb.screen_candidate({'mechanism': 'volatility'})['status'],
                         'NO_EXACT_LEGACY_CONFLICT')
        self.assertEqual(kb.screen_candidate({'hypothesis_id': 'NEW', 'mechanism':
                         'dividend announcement institutional settlement'})['status'],
                         'NO_EXACT_LEGACY_CONFLICT')

    def test_existing_ledger_identity_and_counts_are_unchanged(self):
        record = {'HYPOTHESIS_ID': 'TSR-NDX-001', 'RESEARCH_DECISION': 'KILL'}
        ledger = {'records': [record]}
        before = deepcopy(ledger)
        kb = LegacyKnowledgeBase(self.manifest, ledger)
        self.assertEqual(kb.screen_candidate({'hypothesis_id': 'TSR-NDX-001'})['status'],
                         'BLOCK_EXACT_LEGACY_DUPLICATE')
        summary = kb.summary()
        self.assertEqual(summary['loaded_record_count'], 1)
        self.assertEqual(summary['historical_research_items_found'], 33)
        self.assertEqual(summary['reconciliation_status'], 'PARTIAL_WITH_EXPLICIT_GAPS')
        self.assertEqual(summary['global_effective_trials'], 'UNKNOWN')
        self.assertEqual(summary['recovered_source_review_count'], len(self.manifest['recovered_source_reviews']))
        self.assertEqual(ledger, before)

    def test_incomplete_ambiguous_or_metric_bearing_recovery_fails_closed(self):
        variants = []
        for key in self.review:
            entry = deepcopy(self.review)
            entry.pop(key)
            variants.append([entry])
        for key, value in [('limitations', []), ('revisit_conditions', None),
                           ('source_refs', []), ('source_commit', 'UNKNOWN'),
                           ('judge_verdict', 'PASS'), ('classification', 'IDEA_FALSE_FOREVER'),
                           ('raw_returns', [1, 2])]:
            variants.append([dict(self.review, **{key: value})])
        variants.extend([None, {}, [self.review, self.review],
                         [dict(self.review, source_refs=[{'path': '../outcome', 'blob_sha': 'a'*40}])]])
        for entries in variants:
            with self.subTest(entries=entries), self.assertRaisesRegex(ValueError, 'LEGACY_SOURCE_REVIEW'):
                LegacyKnowledgeBase(dict(self.manifest, recovered_source_reviews=entries))

    def test_native_screen_and_preflight_bind_source_review_hash(self):
        ledger = {'schema_version': self.manifest['schema_version'],
                  'governance': self.manifest['governance'],
                  'records': [{'HYPOTHESIS_ID': 'UNRELATED'}]}
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'legacy').mkdir()
            data = json.dumps(ledger).encode()
            manifest = dict(self.manifest, ledger_blob_sha=git_blob_sha(data))
            (base / 'legacy/source_manifest.json').write_text(json.dumps(manifest))
            (base / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json').write_bytes(data)
            (base / 'hypotheses').mkdir()
            peer = {'hypothesis_id': 'PEER', 'generation_id': 'G1', 'mechanism':
                    'semiconductor lithography backlog service capacity', 'issuer': 'PEER',
                    'authority': AUTHORITY}
            (base / 'hypotheses/PEER.json').write_text(json.dumps(peer))
            candidate = dict(peer, hypothesis_id='P0-E1', issuer='NASDAQ',
                             mechanism=self.review['mechanism'])
            screen = _screen(SimpleNamespace(base=base), candidate)
            self.assertEqual(screen['status'], 'BLOCK')
            self.assertEqual(screen['block_reasons'], ['REVIEW_LEGACY_OVERLAP'])
            self.assertEqual(screen['legacy']['recovered_source_matches'][0]['source_commit'],
                             self.review['source_commit'])
            preflight = verify_materialized_legacy(base)
            self.assertEqual(preflight['loaded_record_count'], 1)
            self.assertEqual(preflight['recovered_source_review_count'], len(self.manifest['recovered_source_reviews']))
            self.assertEqual(preflight['recovered_source_reviews_hash'],
                             screen['legacy']['recovered_source_reviews_hash'])
            altered = deepcopy(manifest)
            altered['recovered_source_reviews'][0]['limitations'].append('New disclosed limitation')
            self.assertNotEqual(LegacyKnowledgeBase(altered).summary()['recovered_source_reviews_hash'],
                                preflight['recovered_source_reviews_hash'])

    def test_no_recovery_entries_preserves_old_manifests(self):
        self.manifest.pop('recovered_source_reviews')
        kb = LegacyKnowledgeBase(self.manifest)
        self.assertEqual(kb.summary()['recovered_source_review_count'], 0)
        self.assertEqual(kb.screen_candidate({'hypothesis_id': 'P0-E1'})['status'],
                         'NO_EXACT_LEGACY_CONFLICT')

