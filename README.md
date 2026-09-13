# Quant-Trade — Autonomous Alpha Discovery System

Quant-Trade is being rebuilt as an autonomous quantitative research system whose terminal objective is simple:

> **Find and validate real market edge so the system can improve the future growth of capital.**

This repository is not organized around one permanent strategy, one market, or one forecasting model.

The target is a continuously learning discovery engine that can:

`SCAN -> FILTER -> HYPOTHESIZE -> TEST -> VALIDATE -> PAPER/SHADOW SELECT -> LEARN -> REPEAT`

## Core idea

The durable asset is not one winning strategy. It is a factory that discovers new strategies faster than old alpha decays.

A candidate is not a conclusion. A signal is not automatically an action. `NO_TRADE` is a valid paper/shadow decision.

## Source-inspired architecture

The supplied source material contributes three central ideas:

1. **continuous strategy discovery** rather than one static strategy;
2. **wide/cheap scanning followed by narrow/deep reasoning**;
3. **specialized logical roles** for scanning, hypothesis generation, backtesting, validation and downstream selection.

The later screenshots add a fourth idea: strong autonomy may look inactive because most candidates can be rejected. Their displayed profit claims are not treated as verified evidence.

See `SOURCE_BASIS.md` for the exact distinction between source-derived concepts and project inference.

## Initial research families

The source material proposes four starting families:

- statistical arbitrage / relative value;
- volatility-surface mispricings;
- factor-decomposition anomalies;
- insider / filing-driven signals.

These are starting lanes, not permanent limits.

## Important economic rule

Profit caused mainly by passive exposure to a secularly rising market is not automatically evidence of discovered alpha.

Where relevant, Quant-Trade must separate broad beta / factor exposure from the residual contribution of the research hypothesis.

## Autonomy

The human defines the terminal objective and hard external boundaries.

The system should choose the research path itself: markets, hypotheses, tests, rejections and next research action.

Failed ideas should normally be absorbed internally rather than handed back to the human one by one.

## Existing NASDAQ research

The existing `src/`, `scripts/`, `data/` and `results/` directories contain historical NASDAQ volatility research that predates this rebuild.

It is retained as prior research and reusable code where useful. It does **not** define the future research universe.

## Core files

- `MISSION.md` — terminal objective and autonomy.
- `SOURCE_BASIS.md` — what came from the article/screenshots versus project inference.
- `AGENTS.md` — autonomous research contract.
- `PIPELINE.md` — minimum continuous discovery loop.
- `schemas/research_ticket.schema.json` — common research-ticket format.
- `CODEX.md` — single launch mandate for Codex.

## Reproduce the first discovery cycle

The initial vertical slice uses only the Python standard library. It ranks a
small pre-declared scan on a discovery subsample, performs a strictly lagged OOS
test with costs, attacks the result, writes a ticket, and appends research
memory:

```bash
python scripts/run_discovery_cycle.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

The committed ticket is the immutable evidence from the first run. Re-running
the command intentionally appends another record; use a separate memory path
from the Python API for exploratory runs.

## Start Codex

Launch Codex from this branch and give it only:

> Read `CODEX.md` in full, then execute it as your operating mandate. Read every referenced project file before acting. Continue autonomously through ordinary failed experiments rather than asking me to invent the next strategy.

Any future real-capital integration is a separate explicit stage. This rebuild focuses on the autonomous research and paper/shadow decision engine.
