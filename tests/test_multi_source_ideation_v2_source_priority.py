from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_bindings import canonical_source_identity


class SourceIdentityPriorityTests(unittest.TestCase):
    def test_content_identity_priority_is_stable(self):
        source={"packet_hash":"p","blob_sha":"b","record_hash":"r"}
        self.assertEqual(canonical_source_identity(source),"packet_hash:p")
        self.assertEqual(canonical_source_identity({"blob_sha":"b","record_hash":"r"}),"blob_sha:b")
        self.assertEqual(canonical_source_identity({"record_hash":"r"}),"record_hash:r")
        self.assertIsNone(canonical_source_identity({"path":"p"}))


if __name__ == "__main__": unittest.main()
