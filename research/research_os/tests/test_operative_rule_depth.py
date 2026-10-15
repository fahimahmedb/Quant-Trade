"""Official rule edition, conditional scope, and preserved Legacy hard-stop."""
import json
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError
from research.research_os.expansion.source_adapters_v1 import capture_sec_t1_rule, assess_t1_rule_scope
from research.research_os.expansion.engine_dossiers_v1 import build_engine_dossier
from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.simulations.primary_documentary_build import documentary_case, PRIMARY_SOURCES

BASE = Path(__file__).resolve().parents[1]


def rule_source():
    return json.loads((BASE / 'sources/sec_t1_operative_rule.json').read_text())


def rule_output(source=None):
    return ENGINE_REGISTRY['institutional_flow'].run(source or rule_source(), EngineContext('RULE', synthetic_only=False))


class OperativeRuleDepthTests(unittest.TestCase):
    def test_official_bytes_reproduce_rule_and_dossier_without_forced_flow(self):
        source = rule_source()
        self.assertEqual(source, capture_sec_t1_rule(BASE / 'sources/captures/sec_15c6_1_2025.xml',
                                                    retrieved_at=source['freeze_time']))
        output = rule_output(source)
        before = deepcopy(output)
        dossier = build_engine_dossier(output)
        self.assertEqual(output, before)
        self.assertEqual(dossier['factual_binding_status'], 'PASS')
        self.assertEqual(dossier['status'], 'BLOCK')
        self.assertEqual(dossier['field_statuses']['constraint_rule'], 'SUPPORTED')
        for field in ('expected_footprint', 'capacity_constraints'):
            self.assertEqual(dossier['field_statuses'][field], 'UNKNOWN')
        self.assertEqual(dossier['dossier']['forced_actor']['values']['forced_quantity'], 'UNKNOWN')
        self.assertEqual(dossier['dossier']['constraint_rule']['values']['current_legal_status'], 'UNKNOWN')
        self.assertIn('Prior closed research families remain closed', output['candidate']['falsification_scope'])

    def test_faq_remains_nonbinding_and_cannot_be_promoted_to_rule_text(self):
        source = json.loads((BASE / 'sources/sec_t1_staff_faq.json').read_text())
        dossier = build_engine_dossier(rule_output(source))
        self.assertEqual(dossier['field_statuses']['constraint_rule'], 'PARTIAL')
        source['documentary_packet']['rule_kind'] = 'STANDARD_SETTLEMENT_OPERATIVE_RULE'
        with self.assertRaises(EngineContractError):
            rule_output(source)

    def test_rule_tampering_missing_exceptions_and_bad_capture_clocks_are_rejected(self):
        from research.research_os.scientific_store import sha256_json
        for field, value in [('raw_sha256','0'*64), ('section_text','one business day'),
                             ('retrieved_at','2024-01-01T00:00:00Z'), ('edition_date','2026-01-01')]:
            source = rule_source()
            packet = source['documentary_packet']
            packet['capture'][field] = value
            packet['content_hash'] = sha256_json({k:v for k,v in packet.items() if k!='content_hash'})
            with self.subTest(field=field), self.assertRaises(EngineContractError):
                rule_output(source)

    def test_conditional_scope_rejects_exceptions_and_unknown_assumptions(self):
        # Declared engineering scenarios, never facts about real transactions.
        case = dict(broker_or_dealer=True, security_class='ORDINARY_COMMON_EQUITY',
                    agreed_alternate_date=False, commission_exemption=False, firm_commitment_offering=False)
        self.assertEqual(assess_t1_rule_scope(case)['status'], 'CONDITIONALLY_WITHIN_RULE_SCOPE')
        for field in ('agreed_alternate_date','commission_exemption','firm_commitment_offering'):
            self.assertEqual(assess_t1_rule_scope(dict(case, **{field:True}))['status'], 'OUTSIDE_BOUNDED_SCOPE')
            self.assertEqual(assess_t1_rule_scope(dict(case, **{field:None}))['status'], 'UNKNOWN')
        for security in ('GOVERNMENT_SECURITY','MUNICIPAL_SECURITY','EXEMPTED_SECURITY','COMMERCIAL_PAPER',
                         'BANKERS_ACCEPTANCE','COMMERCIAL_BILL','UNLISTED_LIMITED_PARTNERSHIP','SECURITY_BASED_SWAP'):
            self.assertEqual(assess_t1_rule_scope(dict(case,security_class=security))['status'], 'OUTSIDE_BOUNDED_SCOPE')
        self.assertEqual(assess_t1_rule_scope(dict(case,broker_or_dealer=False))['status'], 'OUTSIDE_BOUNDED_SCOPE')
        self.assertEqual(assess_t1_rule_scope(dict(case,broker_or_dealer='True'))['status'], 'UNKNOWN')
        self.assertEqual(assess_t1_rule_scope({})['status'], 'UNKNOWN')

    def test_official_rule_legacy_duplicate_stops_before_dossier_or_runner(self):
        with patch.dict(PRIMARY_SOURCES, institutional_flow='sec_t1_operative_rule.json'):
            _, _, fixture, task = documentary_case(BASE, 'institutional_flow')
        ledger = json.loads((BASE / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json').read_text())
        hid = next(r['HYPOTHESIS_ID'] for r in ledger['records'] if r.get('HYPOTHESIS_ID') not in (None,'','UNKNOWN'))
        with TemporaryDirectory() as directory, \
             patch('research.research_os.expansion.engine_dossiers_v1.build_engine_dossier', side_effect=AssertionError('dossier before Legacy')), \
             patch('research.research_os.expansion.experiment_runner.DryRunExperimentRunner.execute', side_effect=AssertionError('runner before Legacy')):
            result = run_canonical_spine(BASE, fixture, task, checkpoint_dir=Path(directory), candidate_override_hypothesis_id=hid)
            self.assertEqual(result['status'], 'BLOCKED_EXACT_LEGACY_DUPLICATE')
            self.assertFalse(result['downstream_executed'])
            self.assertFalse(list(Path(directory).glob('*.generation.json')))


if __name__ == '__main__':
    unittest.main()
