"""The legacy verifier must execute the interpreter whose dependencies were qualified."""
import sys

from scripts import verify_p0


def test_legacy_verification_keeps_the_qualifying_python_interpreter():
    result = verify_p0.run([
        "python3", "-c", f"import sys; assert sys.executable == {sys.executable!r}",
    ])
    assert result["result"] == "PASS", result
