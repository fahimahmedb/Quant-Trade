"""Real dossier support cannot be supplied by filled prose or caller booleans."""
import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.engine_dossiers_v1 import build_engine_dossier, documentary_dossier_detail
from research.research_os.scientific_store import sha256_json

BASE = Path(__file__).resolve().parents[1]


def fundamental_output():
    source = json.loads((BASE / 'sources/apple_fy2025_statement_cells.json').read_text())
    return ENGINE_REGISTRY['fundamental'].run(source, EngineContext('DOSSIER', synthetic_only=False))


class FundamentalDossierDepthTests(unittest.TestCase):
    def test_captured_facts_are_bound_and_unavailable_economic_premises_stay_blocked(self):
        output = fundamental_output()
        before = deepcopy(output)
        dossier = build_engine_dossier(output)
        self.assertEqual(dossier, build_engine_dossier(output))
        self.assertEqual(output, before)
        self.assertEqual(dossier['factual_binding_status'], 'PASS')
        self.assertEqual(dossier['status'], 'BLOCK')
        self.assertEqual(dossier['claim_ceiling'], 'DOCUMENTED_FACTS_ONLY')
        self.assertEqual(dossier['dossier']['cash_flow_quality']['values']['free_cash_flow'], '98767')
        self.assertEqual(dossier['dossier']['cash_flow_quality']['values']['margin_unit'], 'ratio')
        for field in ('valuation_frame','balance_sheet_quality','estimate_revisions','competitive_position','catalysts'):
            self.assertEqual(dossier['field_statuses'][field], 'UNKNOWN')
            self.assertIn('UNQUALIFIED_'+field.upper(), dossier['blockers'])
        support = dossier['dossier']['financial_statements']['support']
        packet = output['candidate']['documentary_evidence']['packet']
        self.assertEqual(support['packet_hash'], packet['content_hash'])
        self.assertEqual(support['available_at'], packet['available_at'])
        self.assertEqual(dossier['candidate_hash'], sha256_json(output['candidate']))

    def test_prose_placeholders_or_promoted_status_do_not_replace_documentary_support(self):
        output = fundamental_output()
        detail = documentary_dossier_detail(output)
        mutations = [lambda d:d.update(valuation_frame='cheap'),
                     lambda d:d['valuation_frame'].update(status='SUPPORTED',values={'fair_value':'999'}),
                     lambda d:d['financial_statements']['support'].update(period='FY2024'),
                     lambda d:d['financial_statements']['values'].update(revenue='1'),
                     lambda d:d.update(outcome_accessed=True),
                     lambda d:d.update(candidate_hash='forged')]
        for mutate in mutations:
            changed = deepcopy(detail)
            mutate(changed)
            dossier = build_engine_dossier(output, changed)
            self.assertEqual(dossier['factual_binding_status'], 'BLOCK')
            self.assertIn('DOCUMENTARY_DOSSIER_DETAIL_NOT_BOUND', dossier['blockers'])

    def test_candidate_claim_inflation_is_rejected_without_mutating_candidate(self):
        output = fundamental_output()
        output['candidate']['claim'] = 'Profitable alpha established'
        before = deepcopy(output)
        dossier = build_engine_dossier(output)
        self.assertEqual(dossier['factual_binding_status'], 'BLOCK')
        self.assertIn('DOCUMENTARY_DOSSIER_SOURCE_NOT_BOUND', dossier['blockers'])
        self.assertEqual(output, before)

    def test_nonpositive_accounting_premise_is_reported_as_disconfirmed(self):
        source = json.loads((BASE / 'sources/apple_fy2025_statement_cells.json').read_text())
        # Counterfactual capture exercises arithmetic, never saved as real evidence.
        packet = source['documentary_packet']
        packet['facts']['operating_income'] = '-1'
        capture = packet['capture']
        rows = []
        for key, value in packet['facts'].items():
            value = '-'+value if key=='capital_expenditure' else value
            rows.append(f'{key}={value}\n')
        capture['text'] = ''.join(rows)
        import hashlib
        capture['text_sha256'] = hashlib.sha256(capture['text'].encode()).hexdigest()
        for key, span in capture['fact_spans'].items():
            start = capture['text'].index(key+'=')+len(key)+1
            span.update(start=start,end=capture['text'].index('\n',start))
        packet['content_hash'] = sha256_json({k:v for k,v in packet.items() if k!='content_hash'})
        output = ENGINE_REGISTRY['fundamental'].run(source,EngineContext('NEGATIVE',synthetic_only=False))
        dossier = build_engine_dossier(output)
        self.assertIn('FUNDAMENTAL_PREMISE_DISCONFIRMED', dossier['blockers'])
        self.assertEqual(dossier['dossier']['cash_flow_quality']['values']['positive_cash_profitability_premise'],'DISCONFIRMED')


if __name__ == '__main__':
    unittest.main()
