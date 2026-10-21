from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import proposal_identity


class ProposalIdentityTests(unittest.TestCase):
    def test_policy_is_part_of_identity(self):
        kw={"context_snapshot_hash":"h","payload":{"m":1},"provenance":{"s":1}}
        a=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",**kw)
        b=proposal_identity(policy_kind="DIVERGENT_EXPLORATION",**kw)
        self.assertNotEqual(a["proposal_id"],b["proposal_id"])

    def test_provenance_is_part_of_identity(self):
        a=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",context_snapshot_hash="h",payload={"m":1},provenance={"s":1})
        b=proposal_identity(policy_kind="SYSTEMATIC_COVERAGE",context_snapshot_hash="h",payload={"m":1},provenance={"s":2})
        self.assertNotEqual(a["proposal_id"],b["proposal_id"])


if __name__ == "__main__": unittest.main()
