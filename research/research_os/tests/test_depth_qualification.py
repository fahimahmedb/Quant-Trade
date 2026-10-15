"""Restart and provenance qualification of the strengthened existing pipeline."""
import json
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.expansion.persistent_state import read_immutable_json
from research.research_os.simulations.primary_documentary_build import documentary_case, run_primary_documentary_build, PRIMARY_SOURCES
from research.research_os.scientific_store import sha256_json

BASE = Path(__file__).resolve().parents[1]


class DepthQualificationTests(unittest.TestCase):
    def test_all_documentary_lineages_recover_after_dossier_validation_without_duplicate_terminal_receipts(self):
        for key in PRIMARY_SOURCES:
            _, output, fixture, task = documentary_case(BASE, key)
            before = deepcopy(output)
            with self.subTest(engine=key), TemporaryDirectory() as interrupted, TemporaryDirectory() as clean:
                directory = Path(interrupted)
                with patch('research.research_os.expansion.canonical_spine.economic_identity_v1', side_effect=RuntimeError('interruption after dossier validation')):
                    with self.assertRaises(RuntimeError):
                        run_canonical_spine(BASE, fixture, task, checkpoint_dir=directory)
                self.assertEqual(len(list(directory.glob('*.generation.json'))), 1)
                self.assertFalse(list(directory.glob('*.canonical.json')))
                self.assertFalse(list(directory.glob('*.completed.json')))
                recovered = run_canonical_spine(BASE, fixture, task, checkpoint_dir=directory)
                self.assertEqual(recovered, run_canonical_spine(BASE, fixture, task, checkpoint_dir=Path(clean)))
                self.assertEqual(recovered, run_canonical_spine(BASE, fixture, task, checkpoint_dir=directory))
                files = list(directory.glob('*.canonical.json'))
                self.assertEqual(len(files), 1)
                self.assertEqual(read_immutable_json(files[0]), recovered)
                receipts = recovered['worker_receipts']
                self.assertEqual(len({r['receipt_id'] for r in receipts}), len(receipts))
                self.assertEqual(recovered['candidate']['candidate'], before['candidate'])
                self.assertEqual(recovered['validation']['dossier_hash'], recovered['documentary_depth']['dossier']['dossier_hash'])
                self.assertTrue(recovered['scientific_ledger']['verified'])
                self.assertFalse(any(recovered['authority'].values()))

    def test_changed_freeze_in_same_generation_cannot_rewrite_completed_checkpoint(self):
        _, _, fixture, task = documentary_case(BASE, 'event_document')
        with TemporaryDirectory() as directory:
            checkpoint = Path(directory)
            original = run_canonical_spine(BASE, fixture, task, checkpoint_dir=checkpoint)
            hashes = {p.name:sha256_json(json.loads(p.read_text())) for p in checkpoint.glob('*.json')}
            changed = deepcopy(fixture)
            source = changed['sources']['event_document']
            source['freeze_time'] = (datetime.fromisoformat(source['freeze_time'])+timedelta(seconds=1)).isoformat()
            changed['base_time'] = source['freeze_time']
            with self.assertRaises(ValueError):
                run_canonical_spine(BASE, changed, task, checkpoint_dir=checkpoint)
            self.assertEqual(hashes, {p.name:sha256_json(json.loads(p.read_text())) for p in checkpoint.glob('*.json')})
            self.assertEqual(original, run_canonical_spine(BASE, fixture, task, checkpoint_dir=checkpoint))

    def test_pipeline_pins_dossiers_and_fact_receipts_survive_reload(self):
        with TemporaryDirectory() as directory:
            report = run_primary_documentary_build(BASE, Path(directory))
            reloaded = json.loads(json.dumps(report))
            self.assertEqual(reloaded, run_primary_documentary_build(BASE, Path(directory)))
            self.assertEqual(report['pipeline_code_hash'], sha256_json(report['pipeline_code_pins']))
            completed = list(Path(directory).rglob('*.completed.json'))
            self.assertEqual(len(completed), 1)
            self.assertEqual(len(list(Path(directory).rglob('*.canonical.json'))), 3)
            self.assertEqual(report['fact_transform_replay'], 'IDENTICAL')
            self.assertFalse(report['fact_transform_execution']['outcome_accessed'])
            self.assertEqual(report['fact_transform_execution']['economic_result'], 'NOT_OBSERVED')
            for row in report['candidates']:
                self.assertEqual(row['candidate_hash'], row['dossier']['candidate_hash'])
                self.assertEqual(row['dossier']['status'], 'BLOCK')
                self.assertEqual(row['forward_readiness'], 'NOT_READY')


if __name__ == '__main__':
    unittest.main()
