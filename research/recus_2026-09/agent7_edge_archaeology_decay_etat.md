# AGENT 7 — EDGE ARCHAEOLOGY / DECAY — state file

Date: 2026-09-29 (UTC). External research + public-API measurement only.
REAL_CAPITAL_AUTHORIZED = FALSE. LIVE_TRADING_AUTHORIZED = FALSE.

STATUS: IN_PROGRESS
PHASE: CHECKPOINT_1 (source map + first measured cases)
BRANCH: claude/exciting-planck-uq6rir (harness-assigned; used instead of `research/agent7-edge-archaeology-decay-2026-09-29`)
CURRENT_HEAD: see `git log -1` on the branch

## Inputs read
- `QUANT_NORTH_STAR.md`; reorientation checkpoint `research/economic-reorientation-checkpoint-2026-09-29@0f8f2d1`.
- Agents 1–6 final deliverables + state files at the exact heads named in the mission.
- Weather V1 spec (`claude/intelligent-gates-msidml@726070a`), Astra feasibility (`claude/dreamy-franklin-1vki4t@e1cf4ca`), Fable V2 challenge memo (`claude/zen-einstein-9moyry@5760ffa`) — read only for latency facts.
- Fast rail: `governance/TWO_SPEED_RESEARCH_PROPOSAL.md`, `FAST_RAIL_STATE.md`, `research/fast_rail/registry.jsonl` on `claude/new-session-0ydmkg` — read for latency facts.

## Measurements done so far (lead)
- HLP 2023-05 → 2026-09 return series (Hyperliquid `vaultDetails`).
- Polymarket maker-rebate pool decomposed by recipient for 13 dates (Polygon logs) — single-recipient discontinuity found.
- Box-office winning-bracket prices at release anchors, 152 events 2023-11 → 2026-09.
- Numerai round-level payout rules 2021 → 2026 (public GraphQL).
- Tweet-count family monthly volume 2024-04 → 2026-09 (gamma).
- Weather NYC/London anchors (running), settlement-liquidity 8 samples 2025-01 → 2026-09 (running).

## NEXT_ACTION
Finish weather + settlement measurements, integrate workstreams A/B, write all case cards, synthesis, self-audit, push.
