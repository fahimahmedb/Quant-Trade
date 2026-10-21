"""Issuer facts and proposed thesis labels are not qualified economic structure."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.final_shape import economic_identity_v1
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2, structural_identity, structural_pair
from research.research_os.scientific_store import sha256_json
from research.research_os.tests import test_economic_identity_portfolio_readiness as generic


BASE = Path(__file__).resolve().parents[1] / 'research/research_os/sources'
SOURCES = {'fundamental': 'apple_fy2025_statement_cells.json',
           'event_document': 'apple_dividend_announcements.json',
           'institutional_flow': 'sec_t1_operative_rule.json'}


def identity(key):
    source = json.loads((BASE / SOURCES[key]).read_text())
    output = ENGINE_REGISTRY[key].run(source, EngineContext('DOCUMENTARY-PORTFOLIO-SCOPE', synthetic_only=False))
    return economic_identity_v1(output, {})


class DocumentaryPortfolioScopeTests(unittest.TestCase):
    def test_three_documentary_families_preserve_support_without_promoting_aliases(self):
        for key in SOURCES:
            with self.subTest(engine=key):
                original = identity(key)
                before = deepcopy(original)
                projected = structural_identity(original)
                fields = projected['fields']
                for name in ('instrument', 'horizon', 'economic_exposure'):
                    self.assertEqual(fields[name]['status'], 'UNKNOWN')
                    self.assertEqual(fields[name]['value'], 'UNKNOWN')
                    self.assertIn(name, projected['unknown_fields'])
                for name, support_name in (('instrument', 'asset'), ('horizon', 'horizon'),
                                            ('economic_exposure', 'economic_tags'), ('mechanism', 'mechanism')):
                    evidence = fields[name]['documentary_evidence']
                    self.assertEqual(evidence['declared_value'], original[support_name])
                    self.assertEqual(evidence['identity_field'], support_name)
                    self.assertEqual(evidence['status'], original['identity_provenance']['field_support'][support_name]['status'])
                    self.assertEqual(evidence['support'], original['identity_provenance']['field_support'][support_name]['support'])
                self.assertEqual(fields['mechanism']['value'], original['mechanism'])
                self.assertEqual(fields['mechanism']['documentary_evidence']['status'], 'CANDIDATE_THESIS_ONLY')
                self.assertEqual(fields['source_identity']['value'], original['identity_provenance']['source_hash'])
                self.assertEqual(fields['source_identity']['documentary_evidence']['status'], 'CONTENT_IDENTITY_ONLY')
                self.assertEqual(original, before)
                self.assertFalse(projected['empirical_return_data_consumed'])

    def test_same_issuer_pair_retains_issuer_diagnostic_without_known_instrument_or_exposure(self):
        left, right = identity('fundamental'), identity('event_document')
        originals = deepcopy([left, right])
        result = portfolio_diagnostics_v2([left, right])
        pair = result['pairwise'][0]
        self.assertEqual(left['asset'], 'AAPL')
        self.assertEqual(right['asset'], 'AAPL')
        self.assertEqual(pair['dimensions']['asset'], 1.0)  # existing issuer/asset diagnostic
        structure = pair['economic_structure']
        for name in ('instrument', 'horizon', 'economic_exposure'):
            self.assertIsNone(structure['dimensions'][name])
            self.assertIn(name, structure['unknown_dimensions'])
        self.assertEqual(structure['classification'], 'UNKNOWN')
        self.assertEqual(result['empirical_correlation'], 'UNAVAILABLE')
        self.assertEqual(result['marginal_portfolio_contribution'], 'NOT_ESTIMATED')
        self.assertFalse(result['return_series_consumed'])
        for name in ('capital_allocation_authorized', 'position_sizing_authorized', 'orders_authorized',
                     'real_capital_authorized', 'live_trading_authorized', 'portfolio_optimization_authorized'):
            self.assertIs(result[name], False)
        self.assertEqual([left, right], originals)

    def test_explicit_generic_structural_declarations_keep_the_existing_golden_contract(self):
        declared = generic.identity('H1')
        before = deepcopy(declared)
        result = structural_identity(declared)
        for name in ('instrument', 'horizon', 'economic_exposure'):
            self.assertEqual(result['fields'][name]['value'], declared[name])
            self.assertEqual(result['fields'][name]['status'], 'KNOWN')
            self.assertNotIn('documentary_evidence', result['fields'][name])
        self.assertEqual(sha256_json(structural_pair(generic.identity('H1'), generic.identity('H2'))),
                         '0c788583ae3c7f561ffd665227152b69733f8b46611496bc3e53f67f7c66deb4')
        self.assertEqual(declared, before)
