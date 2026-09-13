# Quant-Trade — Autonomous Alpha Discovery System

Quant-Trade is being rebuilt as an autonomous quantitative research and trading system whose terminal objective is simple:

> **Find, validate, select and eventually monetize real market edge so that capital grows over time.**

This repository is not organized around one permanent strategy, one market, or one forecasting model.

The target is a continuously learning system that can:

`SCAN -> REASON -> TEST -> VALIDATE -> VET -> SIZE -> RISK -> FILL -> BOOK -> LEARN -> REPEAT`

## Core idea

The durable asset is not one winning strategy. It is a factory that discovers new strategies faster than old alpha decays.

Quant-Trade therefore separates three different problems:

1. **Alpha discovery** — where is the edge?
2. **Capital decision** — does this opportunity deserve money now, and how much?
3. **Execution / book** — what actually happened to the capital?

A signal is not an order. `NO_TRADE` is a valid decision.

## Architecture

See `SYSTEM.md` for the full design.

High-level flow:

```text
MARKETS / DATA
    ↓
SCAN LAYER
    ↓
CANDIDATES
    ↓
HYPOTHESIS / BACKTEST / VALIDATION
    ↓
LIVE SIGNAL
    ↓
VET → SIZE → RISK → FILLS → BOOK
    ↓
REALIZED ECONOMICS
    ↓
MEMORY / ALPHA-DECAY LEARNING
    ↺
```

The scan layer should be broad and cheap. Deep reasoning should be spent only on filtered candidates.

## Initial research families

The source material motivating this rebuild proposes four initial families of mispricing:

- statistical arbitrage / relative value;
- volatility-surface mispricings;
- factor-decomposition anomalies;
- insider / filing-driven signals.

These are starting lanes, not permanent limits.

## Important economic rule

Profit caused mainly by passive long exposure to a secularly rising market is not automatically evidence of discovered alpha.

Where relevant, Quant-Trade must separate broad beta / factor exposure from the residual contribution of the strategy.

## Stateful capital

The system is stateful. Capital carries over from one decision to the next.

There is no conceptual reset after every trade or session:

`State_t = cash + positions + exposures + open risk + history + current market state`

The next decision depends on the current state.

The **Book** is the accounting source of truth for cash, positions, realized P&L, unrealized P&L, fees, financing and NAV.

## Autonomy

The human defines the terminal objective and hard external boundaries.

The system should choose the research path itself: markets, hypotheses, tests, rejections, sizing logic, and next research action.

Failed ideas should normally be absorbed internally rather than handed back to the human one by one.

## Existing NASDAQ research

The existing `src/`, `scripts/`, `data/` and `results/` directories contain the historical NASDAQ volatility research that predates this rebuild.

It is retained as prior research and reusable code where useful. It does **not** define the future research universe.

## Start Codex

The single launch instruction is:

`CODEX.md`

Codex should read `CODEX.md`, `MISSION.md`, `SYSTEM.md`, `AGENTS.md`, `SOURCE_BASIS.md`, and the schemas before beginning work.
