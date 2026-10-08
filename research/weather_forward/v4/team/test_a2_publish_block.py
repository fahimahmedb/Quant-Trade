"""Tests du script de publication verifiee (commentaires synthetiques, aucun reseau)."""
import hashlib
import importlib.util
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("pb", pathlib.Path(__file__).with_name("a2_publish_block.py"))
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(body):
    pb.fetch = lambda repo, cid: body
    out = tempfile.mkdtemp(prefix="a2pb-")
    pb.sys.argv = ["a2_publish_block.py", "1", out]
    try:
        pb.main()
    except SystemExit as e:
        return e.code, sorted(p.name for p in pathlib.Path(out).iterdir())


class PublishBlock(unittest.TestCase):
    def test_declared_block_is_extracted(self):
        a = "# A\ncontenu\n"
        body = f"entete\n\n```markdown\n{a}```\n\nSHA-256 du bloc : `{sha(a)}`\n"
        self.assertEqual(run(body), (0, ["block_1.md"]))

    def test_undeclared_block_is_not_extracted_even_if_its_digest_is_cited_elsewhere(self):
        a = "# A\ncontenu\n"
        body = f"```markdown\n{a}```\n\nvoir `{sha(a)}` ailleurs\n"
        self.assertEqual(run(body), (0, []))

    def test_declared_sha_without_own_block_fails_even_if_cited_inside_another_block(self):
        b = "# B\nautre\n"
        a = f"# A\ncontenu qui cite le digest de B `{sha(b)}`\n"
        body = f"```markdown\n{a}```\n\nSHA-256 de A : `{sha(a)}`\nSHA-256 de B : `{sha(b)}`\n"
        code, files = run(body)
        self.assertEqual((code, files), (1, ["block_1.md"]))

    def test_digest_inside_block_text_is_content_not_a_declaration(self):
        b = "# B\nautre\n"
        a = f"# A\nSHA-256 de B (document cite) : `{sha(b)}`\n"
        body = f"```markdown\n{a}```\n\nSHA-256 du bloc : `{sha(a)}`\n"
        self.assertEqual(run(body), (0, ["block_1.md"]))

    def test_wrong_declared_sha_fails(self):
        body = "```markdown\nx\n```\n\nSHA-256 : `" + "0" * 64 + "`\n"
        self.assertEqual(run(body)[0], 1)


if __name__ == "__main__":
    unittest.main()
