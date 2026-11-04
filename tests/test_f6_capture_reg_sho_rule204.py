"""Adversarial offline F6 capture prequalification. No scientific admission."""
import hashlib
import unittest
from scripts.f6_capture_reg_sho_rule204 import URL, extract_section, receipt

class F6Rule204CaptureTests(unittest.TestCase):
    @staticmethod
    def original():
        header = "Code of Federal Regulations April 1, 2025 Edition "
        body = (
            "Sec. 242.204 Close-out requirement. "
            "(a) a participant of a registered clearing agency must deliver securities. "
            "(1) Long sales by the third consecutive settlement day. "
            "(2) a restricted sale by the thirty-fifth consecutive calendar day. "
            "(3) bona fide market making activities have separate deadlines. "
            "(b) a broker or dealer has separate restrictions. "
            "(c) participants must notify brokers. "
            "(d) allocated fails have separate rules. "
            "(e) bona fide buy-in exemption. "
            "(f) non-delivery arrangements prohibited. "
            "(g) settlement date definitions. "
            + "Bona fide clearing agency settlement exceptions. " * 65
            + "[74 FR 38292 as amended at 89 FR 26608] "
            + "Regulation ATS--Alternative Trading Systems"
        )
        return ("<html><body><pre>" + header + body + "</pre></body></html>").encode()

    def test_capture_pins_raw_and_extracted_identity_without_source_admission(self):
        raw = self.original()
        r = receipt(raw, captured_at="2026-11-04T03:00:00Z")
        self.assertEqual(r["raw_html_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(r["extracted_section_sha256"], hashlib.sha256(r["section_text"].encode()).hexdigest())
        self.assertEqual(r["status"], "CAPTURED_NOT_SCIENTIFICALLY_ADMITTED")
        self.assertEqual(r["source_url"], URL)
        self.assertNotIn("economic_result", r)

    def test_missing_clause_and_wrong_section_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "RULE204_REQUIRED_CLAUSE_MISSING"):
            extract_section(self.original().replace(b"89 FR 26608", b"89 FR 26609"))
        with self.assertRaisesRegex(ValueError, "RULE204_HEADING"):
            extract_section(self.original().replace(b"242.204", b"242.205"))
        with self.assertRaisesRegex(ValueError, "RULE204_REQUIRED_CLAUSE_MISSING"):
            extract_section(self.original().replace(b"(e) bona fide", b"(x) bona fide"))

    def test_bad_provenance_never_becomes_captured(self):
        with self.assertRaisesRegex(ValueError, "NOT_OFFICIAL"):
            receipt(self.original(), captured_at="2026-11-04T03:00:00Z", source_url="https://example.com/")
        with self.assertRaisesRegex(ValueError, "CAPTURE_CLOCK_INVALID"):
            receipt(self.original(), captured_at="2020-01-01T00:00:00Z")
        with self.assertRaisesRegex(ValueError, "RAW_HTML_INVALID"):
            extract_section(b"short")

if __name__ == "__main__":
    unittest.main()
