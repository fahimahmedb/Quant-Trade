#!/usr/bin/env bash
set -euo pipefail

cat >&2 <<'EOF'
STOP: this CP11 repository-cleanup bootstrap has been superseded by the CP12 deep organizational audit.

DO NOT run the old mass-deletion plan.

Reason:
- the repository has 229 branches and V2/Live Lab continued to evolve after CP11;
- CP12 proved that several historical/diverged refs still contain capabilities, Owner decisions, scientific memory, or parallel product work not yet absorbed by V2;
- current V2 governance keeps destructive Git operations unauthorized for autonomous agents.

Current audit authority:
  audit/forensic-checkpoint-20261019 / CHECKPOINT_012.md

Current supporting registries:
  governance/WORKSTREAM_INDEX_2026-10-20.md
  governance/OWNER_DECISIONS_2026-10-20.md
  governance/SCIENTIFIC_MEMORY_INDEX_2026-10-20.md
  governance/WORKFLOW_DISPOSITION_2026-10-20.md
  governance/REPOSITORY_AUTHORITY_REGISTRY_2026-10-20.md

A new Owner-executed one-command cleanup may only be generated after CP12 import/reconciliation work produces a semantic delete manifest.
EOF

exit 78
