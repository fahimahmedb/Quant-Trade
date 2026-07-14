#!/bin/bash
# .claude/hooks/pre-commit-lookahead-check.sh
# Pre-commit hook: blocks commits if lookahead bias is detected in overlay/volatility code
#
# Install: configure in settings.json under hooks.preCommit
# Usage: Automatically runs before git commit
#
# Inspired by: Bailey et al. (PBO), Harris (look-ahead bias detection),
# López de Prado (AFML ch. 2 - walk-forward validation)

set -e

# Check if src/overlay.py or src/volatility.py were modified
MODIFIED_FILES=$(git diff --cached --name-only)

if echo "$MODIFIED_FILES" | grep -qE "(src/overlay\.py|src/volatility\.py|src/prediction\.py|scripts/run_etape_d)"; then
    echo "[pre-commit] Lookahead-sensitive files modified: running validation tests..."
    echo ""

    # Run the no-lookahead test suite
    python3 tests/test_no_lookahead.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Pre-commit lookahead check PASSED. Commit allowed."
        exit 0
    else
        echo ""
        echo "❌ Pre-commit lookahead check FAILED. Commit BLOCKED."
        echo ""
        echo "   Changes to overlay/volatility detected lookahead bias."
        echo "   Do NOT commit until the tests pass."
        echo ""
        echo "   Debugging steps:"
        echo "   1. Review audit_code_overlay.md (7 critical issues)"
        echo "   2. Implement fixes in CODE_FIXES_REQUIRED.md"
        echo "   3. Re-run: python3 tests/test_no_lookahead.py"
        echo ""
        exit 1
    fi
else
    echo "[pre-commit] No lookahead-sensitive files modified. Skipping test."
    exit 0
fi
