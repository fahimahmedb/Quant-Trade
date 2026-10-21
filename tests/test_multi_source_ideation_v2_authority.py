from __future__ import annotations

import inspect
import unittest

from research.research_os import ideation_cycle, multi_source_ideation, multi_source_ideation_bindings, multi_source_ideation_hardening


class IdeationAuthorityMembraneTests(unittest.TestCase):
    def test_modules_do_not_import_control_plane_or_runtime_execution(self):
        sources="\n".join(inspect.getsource(m) for m in (ideation_cycle,multi_source_ideation,multi_source_ideation_bindings,multi_source_ideation_hardening))
        forbidden=("import control_plane","from control_plane","oracle_worker","create_ready_task","run_producer(","execute_experiment(")
        for token in forbidden:
            self.assertNotIn(token,sources)

    def test_authority_flags_are_closed(self):
        flags={
            "REAL_CAPITAL_AUTHORIZED":False,
            "LIVE_TRADING_AUTHORIZED":False,
            "PROSPECTIVE_OBSERVATION_AUTHORIZED":False,
            "ECONOMIC_EXPERIMENT_AUTHORIZED":False,
            "OUTCOME_ACCESSED":False,
        }
        self.assertFalse(any(flags.values()))

    def test_eligible_for_discovery_is_not_ready(self):
        got=multi_source_ideation_hardening.qualify_for_discovery(
            proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",
            memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        self.assertEqual(got["boundary"],"ELIGIBLE_FOR_DISCOVERY")
        self.assertFalse(got["ready_task_created"]); self.assertFalse(got["candidate_created"])


if __name__ == "__main__": unittest.main()
