from __future__ import annotations

import inspect
import unittest

from research.research_os.multi_source_ideation_hardening import DurableProposalLedger


class LedgerNotQueueTests(unittest.TestCase):
    def test_ledger_has_no_queue_worker_methods(self):
        methods={n.lower() for n,_ in inspect.getmembers(DurableProposalLedger,inspect.isfunction)}
        for forbidden in ("lease","heartbeat","retry","dequeue","enqueue","claim_task","run"):
            self.assertNotIn(forbidden,methods)


if __name__ == "__main__": unittest.main()
