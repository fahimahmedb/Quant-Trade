# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Current authority / restart surface

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md`.
3. Read `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md`.
4. Read `handoff/BLUE_MASTER_V2_STATE_2026-09-20.md`.
5. Read the exact branch-specific mission/handoff named by current Blue governance.
6. Read only the architecture, code and tests relevant to that exact mission.

`STATE.md` and `CHIEF_BRIEF.md` are runtime/research snapshots, not current project-routing authority.
`CLAUDE_CURRENT_MISSION.md` is now a router and must not contain a frozen historical mission.
The repository default branch is currently historical and is not authority.

Do not import the whole of `AGENTS.md` into every session; use the current governance files above as the compact routing surface.

## Builder role

Claude Code is the Builder / Quant Engineer. Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish.

Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the current mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Ultracode / multi-agent discipline

Project settings enable Ultracode with a small workflow size guideline. Use parallel agents when workstreams are genuinely independent, need isolated context or benefit from adversarial review.

Do not spawn agents for trivial reads, one-file edits, sequential debugging or work that requires one shared evolving state.

For substantive changes, separate implementation from independent economic/research-integrity and runtime/restart review, then synthesize once in the lead agent.

Avoid duplicated exploration. Give each agent one distinct question and require a concise result.

## Token discipline

Use targeted search and file slices before full-file reads. Do not repeatedly restate architecture or facts already established in the repository.

Do not revisit a settled implementation choice unless new evidence contradicts it or a test fails.

Keep progress updates short. Put durable truth in code, tests, `STATE.md` and generated artifacts rather than long chat summaries.

Use `/compact` or a fresh session when the task changes materially. Use `/quant-orient` after branch/context changes instead of rereading everything manually.

## Verification

Normal V1 verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/demo_quant_system.py
python3 scripts/generate_schemas.py --check
```

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired. Use `/quant-proof` before declaring a major milestone complete.

## Git behavior

Follow the exact branch ownership and mutation permissions in the current Blue mission/handoff. Do not infer a current PR or branch from historical files.

Do not merge, force-push, delete branches, move frozen refs or perform irreversible external actions unless the current mission explicitly authorizes that operation.

Commit coherent checkpoints and keep durable mission state in GitHub rather than chat.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an environment limitation that prevents further progress.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.
