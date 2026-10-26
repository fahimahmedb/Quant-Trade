# Quant - Claude Code operating context

This file is intentionally short because Claude Code loads it every session. Put standing project rules here and task procedures in `.claude/skills/`.

## North Star

Quant is a persistent quantitative research and paper/shadow decision system. Its terminal project objective is net economic value from genuine market edge after realistic frictions. `QUANT_NORTH_STAR.md` is the highest authority.

Do not redefine Quant around the subsystem currently being edited. Preserve the whole-system model: Control/Clock, Data, Research Factory, Capital Desk `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`, persistent Book, Learning, Build and Status.

No real-capital authority is granted by this file. Current engineering work remains paper/shadow unless the project owner explicitly changes that boundary.

## Read economically, not ceremonially

Before substantial work:
1. Read `QUANT_NORTH_STAR.md`.
2. Read `BUILDER_ROLE.md` and the current released mission when acting as Builder.
3. Read `STATE.md` and mission-relevant code/tests.
4. Read longer architecture docs when the decision depends on them.

Do not import `AGENTS.md` here. Avoiding that startup context cost is intentional.

## Builder role

Claude Code is one provider that may occupy the provider-independent Builder / Quant Engineer role. `BUILDER_ROLE.md` defines its authority, prohibitions, proof discipline and Red-Team handoff.

Choose local implementation details autonomously, but do not redefine the product around the easiest component to finish. Prefer coherent capability over local elegance. Avoid extra abstractions, files, agents and refactors unless they directly advance the released mission or repair a demonstrated invariant.

Ordinary coding failures, negative research results and blocked research lanes are not project stop conditions. Record them and continue with the highest-value executable work.

## Integrity invariants

Use one causal information timeline across research, paper/shadow decisions and the Book. Research evidence must describe the executable paper/shadow strategy rather than a more favorable backtest object.

Every persistent economic-state mutation must be restart-safe and idempotent. Crash plus replay must not duplicate simulated fills, cash movements, P&L, sessions or attribution.

Multiple strategies may reference the same instrument. Preserve strategy-level sleeves/attribution and aggregate them separately for portfolio state.

Risk approval must describe the final post-transform/post-scale portfolio that would actually be simulated.

A state enum is not a capability. Do not claim decay management, historical strategy versioning, liveness or other behavior unless evidence actually drives it.

Never fabricate market data. Preserve provenance, timestamps, point-in-time caveats, validation and fingerprints.

## Token and workflow discipline

Use parallel agents only for genuinely independent workstreams or independent review. Do not duplicate exploration. Use targeted search and file slices before full-file reads. Put durable truth in code, tests and generated artifacts rather than chat summaries.

## Verification

Run the proof gate defined by the current released mission. Existing V1 verification remains a required baseline unless that mission explicitly supersedes it.

Passing tests is necessary, not sufficient. Add adversarial tests for the specific failure mode being repaired or data semantic being asserted.

## Git behavior

Never infer current authority from an old PR, branch name or this provider-specific file. Verify the exact released `BASE_SHA` and branch from the current mission. Do not merge, force-push, delete branches or perform irreversible external actions unless explicitly authorized.

Commit coherent checkpoints and remove temporary scratch files from the final diff.

## Stop conditions

Stop only for a genuine external boundary: unavailable access, paid resources requiring approval, irreversible external action requiring authority, missing canonical content that cannot be recovered, or an objective ambiguity that changes the scientific contract.

Do not stop merely because one test, experiment, worker, lane or subsystem completed or failed.
