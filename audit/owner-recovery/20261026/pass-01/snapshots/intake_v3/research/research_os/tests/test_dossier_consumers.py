"""Dossier support must survive canonical, validator and portfolio consumers."""
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from research.research_os.expansion.final_shape import economic_identity_v1, red_team
from research.research_os.expansion.validation_v2 import validator_diagnostics_v2
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.simulations.primary_documentary_build import documentary_case, run_primary_documentary_build, PRIMARY_SOURCES
from research.research_os.tests import test_primary_flow_and_challenge as challenge_fixtures
from research.research_os.scientific_store import sha256_json

BASE = Path(__file__).resolve().parents[1]


class DossierConsumerTests(unittest.TestCase):
    def test_canonical_consumers_share_reconstructed_dossier_and_preserve_blockers(self):
        with TemporaryDirectory() as directory:
            report = run_primary_documentary_build(BASE, Path(directory))
        for row in report['candidates']:
            dossier, validation, red = row['dossier'], row['validation_diagnostics'], row['red_team_diagnostics']
            self.assertEqual(dossier['factual_binding_status'], 'PASS')
            self.assertEqual(row['candidate_hash'], dossier['candidate_hash'])
            self.assertEqual(validation['dossier_hash'], dossier['dossier_hash'])
            self.assertEqual(red['dossier_hash'], dossier['dossier_hash'])
            self.assertIn('documentary_dossier_sufficient', validation['critical_failures'])
            self.assertEqual(validation['checks']['documentary_dossier_bound']['status'], 'PASS')
            self.assertIn('BLOCK_DOSSIER_SUFFICIENCY', red['negative_rights'])
            self.assertIn('BLOCK_COST_MODEL', red['negative_rights'])
            self.assertIn('BLOCK_CAPACITY', red['negative_rights'])
            self.assertEqual(row['forward_readiness'], 'NOT_READY')
        pair = next(p for p in report['portfolio']['pairwise'] if p['dimensions']['asset'] == 1.0)
        self.assertTrue(all(pair['dossier_hashes']))
        self.assertIn('payer', pair['unknown_dimensions'])
        self.assertIn('horizon', pair['unknown_dimensions'])

    def test_validator_rejects_promoted_or_missing_dossier_even_with_optimistic_metadata(self):
        for key in PRIMARY_SOURCES:
            with self.subTest(engine=key), TemporaryDirectory() as directory:
                args = challenge_fixtures.ActualDocumentaryChallengeTests().args(key, directory)
                for mutate in (lambda d:d.update(status='PASS',blockers=[]),
                               lambda d:d.update(candidate_hash='forged'),
                               lambda d:d['dossier'].update(disconfirmation_checks='filled prose')):
                    changed = deepcopy(args)
                    mutate(changed['envelope']['dry_run_execution']['dossier'])
                    diagnostics = validator_diagnostics_v2(**changed)
                    self.assertIn('documentary_dossier_bound', diagnostics['critical_failures'])
                    self.assertIn('documentary_dossier_sufficient', diagnostics['critical_failures'])
                del args['envelope']['dry_run_execution']['dossier']
                self.assertIn('documentary_dossier_bound', validator_diagnostics_v2(**args)['critical_failures'])

    def test_identity_ignores_unverified_payer_exposures_and_has_field_level_support(self):
        for key in PRIMARY_SOURCES:
            _, output, _, _ = documentary_case(BASE, key)
            before = deepcopy(output)
            identity = economic_identity_v1(output, dict(asset='FAKE', payer='investors', beta=0.8,
                horizon='1d', capacity='large', liquidity='high', tail_exposure='none'))
            self.assertEqual(identity, economic_identity_v1(output, {}))
            self.assertEqual(output, before)
            for field in ('payer','horizon','beta','capacity','liquidity','tail_exposure'):
                self.assertEqual(identity[field], 'UNKNOWN')
                self.assertIsNone(identity['identity_provenance']['field_support'][field]['support'])
            self.assertEqual(identity['asset'], 'UNKNOWN' if key=='institutional_flow' else 'AAPL')
            self.assertEqual(identity['identity_provenance']['candidate_hash'], sha256_json(output['candidate']))
            self.assertEqual(portfolio_diagnostics_v2([identity])['candidate_count'], 1)
            for mutate in (lambda i:i.update(payer='forced buyer'),
                           lambda i:i.update(beta=0.5),
                           lambda i:i['identity_provenance'].update(dossier_hash='forged'),
                           lambda i:i['documentary_basis']['candidate'].update(generation_id='G2')):
                forged = deepcopy(identity)
                mutate(forged)
                with self.assertRaises(ValueError):
                    portfolio_diagnostics_v2([forged])

    def test_red_team_independently_blocks_dossier_and_missing_disconfirmation(self):
        _, output, _, _ = documentary_case(BASE, 'event_document')
        meta = dict(pit_controls_declared=True, leakage_controls_declared=True, multiplicity_accounting_declared=True)
        impl = dict(cost_model_feasible=True, capacity_observable=True)
        assessment = red_team(output, impl, {'status':'PASS'}, meta)
        self.assertIn('BLOCK_DOSSIER_SUFFICIENCY', assessment['negative_rights'])
        output['candidate']['falsification_scope'] = ''
        before = deepcopy(output)
        assessment = red_team(output, impl, {'status':'PASS'}, meta)
        self.assertIn('BLOCK_DISCONFIRMATION', assessment['negative_rights'])
        self.assertIn('BLOCK_DOSSIER_SOURCE', assessment['negative_rights'])
        self.assertEqual(output, before)


if __name__ == '__main__':
    unittest.main()
