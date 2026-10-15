import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.simulations.primary_documentary_build import documentary_case, run_primary_documentary_build, PRIMARY_SOURCES

BASE = Path(__file__).resolve().parents[1]


class PrimaryDocumentaryIntegrationTests(unittest.TestCase):
    def test_actual_three_source_lineages_replay_and_preserve_unknown_portfolio_estimates(self):
        with TemporaryDirectory() as directory:
            report = run_primary_documentary_build(BASE, Path(directory))
            self.assertEqual(report, run_primary_documentary_build(BASE, Path(directory)))
            for candidate in report['candidates']:
                self.assertTrue(candidate['scientific_ledger_verified'])
                self.assertEqual(candidate['forward_readiness'], 'NOT_READY')
                self.assertEqual(candidate['canonical_economic_transform_executed'], 'NOT_EXECUTED')
                self.assertLess(candidate['stage_order'].index('LEGACY_SCREEN'),
                                candidate['stage_order'].index('IMPLEMENTABILITY_ASSESSMENT'))
            self.assertEqual(len(list(Path(directory).rglob('*.canonical.json'))), 3)
            # The separate executed batch performs facts only; no blocked
            # canonical economic envelope is ever run.
            self.assertEqual(len(list(Path(directory).rglob('*.completed.json'))), 1)
        portfolio = report['portfolio']
        self.assertEqual(portfolio['candidate_count'], 3)
        self.assertEqual(set(portfolio['structural_novelty'].values()), {'UNKNOWN'})
        shared = next(p for p in portfolio['pairwise'] if p['dimensions']['asset'] == 1.0)
        self.assertGreater(shared['dimensions']['economic_tags'], 0)
        self.assertIn('horizon', shared['unknown_dimensions'])
        self.assertIn('payer', shared['unknown_dimensions'])
        self.assertEqual(shared['classification'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(portfolio['statistical_correlation_matrix'], 'UNAVAILABLE_BY_DESIGN')
        self.assertFalse(portfolio['capital_allocation_authorized'])
        for row in report['economic_identities']:
            self.assertEqual(row['payer'], 'UNKNOWN')
            self.assertEqual(row['capacity'], 'UNKNOWN')
        for key, value in report['authority'].items():
            if key != 'scope':
                self.assertFalse(value)

    def test_actual_batch_recovers_from_interruption_without_false_completion(self):
        with TemporaryDirectory() as first:
            report = run_primary_documentary_build(BASE, Path(first))
        inputs = [{'engine_key':key, 'source':documentary_case(BASE, key)[0]} for key in PRIMARY_SOURCES]
        runner = DryRunExperimentRunner()
        with TemporaryDirectory() as directory:
            with patch.object(ENGINE_REGISTRY['institutional_flow'], 'run', side_effect=RuntimeError('interrupted')):
                with self.assertRaises(RuntimeError):
                    runner.execute(report['fact_transform_plan'], inputs, Path(directory))
            self.assertEqual(len(list(Path(directory).glob('*.prepared.json'))), 1)
            self.assertFalse(list(Path(directory).glob('*.completed.json')))
            recovered = runner.execute(report['fact_transform_plan'], inputs, Path(directory))
            self.assertEqual(recovered['execution_receipt_hash'], report['fact_transform_execution']['execution_receipt_hash'])
            self.assertFalse(recovered['outcome_accessed'])

    def test_actual_flow_legacy_duplicate_stops_before_generation_or_runner(self):
        _, _, configuration, task = documentary_case(BASE, 'institutional_flow')
        ledger = json.loads((BASE / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json').read_text())
        hid = next(r['HYPOTHESIS_ID'] for r in ledger['records'] if r.get('HYPOTHESIS_ID') not in (None, '', 'UNKNOWN'))
        with TemporaryDirectory() as directory, patch.object(DryRunExperimentRunner, 'execute', side_effect=AssertionError('downstream ran')):
            result = run_canonical_spine(BASE, configuration, task, checkpoint_dir=Path(directory),
                                         candidate_override_hypothesis_id=hid)
            self.assertFalse(list(Path(directory).glob('*.generation.json')))
            self.assertFalse(list(Path(directory).glob('*.completed.json')))
        self.assertFalse(result['downstream_executed'])
        self.assertEqual(result['status'], 'BLOCKED_EXACT_LEGACY_DUPLICATE')


if __name__ == '__main__':
    unittest.main()
