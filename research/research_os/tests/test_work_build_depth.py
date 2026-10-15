"""Adversarial coverage of real offline execution; all input evidence is synthetic."""
import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError
from research.research_os.expansion.archaeology import EdgeArchaeologyEngine
from research.research_os.scientific_store import sha256_json

BASE = Path(__file__).resolve().parents[1]


def sources():
    return json.loads((BASE / 'simulations/documentary_inputs_fixture.json').read_text())['sources']


def repin(source):
    packet = source['documentary_packet']
    packet['content_hash'] = sha256_json({k: v for k, v in packet.items() if k != 'content_hash'})


class DocumentaryEngineTests(unittest.TestCase):
    def run_engine(self, family, source=None):
        engine = EdgeArchaeologyEngine() if family == 'archaeology' else ENGINE_REGISTRY[family]
        return engine.run(source or sources()[family], EngineContext('WORK-DEPTH'))

    def test_statement_numbers_determine_candidate_and_free_cash_flow(self):
        source = sources()['fundamental']
        before = self.run_engine('fundamental', source)
        source['documentary_packet']['facts']['capital_expenditure'] = '25'
        repin(source)
        after = self.run_engine('fundamental', source)
        self.assertEqual(before['candidate']['documentary_evidence']['measurements']['free_cash_flow'], '12')
        self.assertEqual(after['candidate']['documentary_evidence']['measurements']['free_cash_flow'], '-7')
        self.assertNotEqual(before['candidate']['claim'], after['candidate']['claim'])

    def test_event_revision_direction_changes_from_inputs(self):
        source = sources()['event_document']
        positive = self.run_engine('event_document', source)
        source['documentary_packet']['facts'].update(current_low='60', current_high='80')
        repin(source)
        negative = self.run_engine('event_document', source)
        self.assertEqual(positive['candidate']['documentary_evidence']['measurements']['guidance_change'], '20')
        self.assertEqual(negative['candidate']['documentary_evidence']['measurements']['guidance_change'], '-30')

    def test_constraint_engines_compute_coverage_without_outcomes(self):
        for key in ('quant', 'institutional_flow', 'archaeology'):
            output = self.run_engine(key)
            self.assertEqual(output['candidate']['documentary_evidence']['measurements']['constrained_share'], '0.1')
            self.assertTrue(output['synthetic_only'])
            self.assertEqual(output['candidate']['observation_authorization'], 'NOT_AUTHORIZED')

    def test_tamper_unknown_outcome_fields_and_nonfinite_values_are_rejected(self):
        mutations = [
            lambda p: p['facts'].update(revenue='999'),  # no repin: tamper
            lambda p: p.update(realized_return=0.5),
            lambda p: p['facts'].update(revenue='NaN'),
            lambda p: p.update(period=''),
            lambda p: p.update(revision_status='UNKNOWN'),
            lambda p: p.update(available_at='2026-10-16T10:00:00Z'),
            lambda p: p.update(published_at='2026-10-14T10:00:00'),
            lambda p: p.update(evidence_class='CAPTURED_DOCUMENT'),
        ]
        for i, mutation in enumerate(mutations):
            with self.subTest(mutation=i):
                source = sources()['fundamental']
                mutation(source['documentary_packet'])
                if i:
                    repin(source)
                with self.assertRaises(EngineContractError):
                    self.run_engine('fundamental', source)

    def test_conflicting_guidance_and_ineligible_population_are_rejected(self):
        for key, facts in [('event_document', {'current_low':'150', 'current_high':'100'}),
                           ('institutional_flow', {'constrained_quantity':'1001'})]:
            source = sources()[key]
            source['documentary_packet']['facts'].update(facts)
            repin(source)
            with self.assertRaises(EngineContractError):
                self.run_engine(key, source)


if __name__ == '__main__':
    unittest.main()
