#!/usr/bin/env bash
set -euo pipefail

cat >&2 <<'EOF'
STOP: this CP11 cleanup engine is superseded and intentionally disabled.

Do not classify branches only as KEEP / ABSORBED / ARCHIVE_THEN_DELETE using the old CP11 keep-set.
CP12 found material unabsorbed V2 capabilities, scientific memory, Owner governance evidence, Live Lab divergence and workflow debt.

Use the current deep-audit surfaces on:
  audit/forensic-checkpoint-20261019

Primary document:
  CHECKPOINT_012.md

Physical deletion must wait for a new semantic delete manifest and explicit Owner execution.
EOF

exit 78
