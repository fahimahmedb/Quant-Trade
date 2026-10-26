# Source Analysis — Continuous Strategy Discovery Article

## Purpose

This document extracts the reusable design ideas from the uploaded article about an AI-driven continuous strategy discovery system. It preserves the article's core structure while separating principles from implementation claims and marketing assertions.

## Core idea worth preserving

The article's central proposition is not one specific model, market, or strategy. It is the idea that the durable asset is a **continuous strategy discovery pipeline**:

`observe -> detect -> hypothesize -> test -> validate -> deploy -> monitor -> retire -> rediscover`

The system should therefore be judged by its ability to repeatedly discover and validate exploitable edges faster than old edges decay, not by the success of one static model.

## Functional architecture extracted from the article

The article describes specialized roles:

- scanning / monitoring;
- hypothesis generation;
- backtesting;
- validation;
- deployment;
- risk control;
- notification / operator interface.

For Quant-Trade these are treated as **functions**, not as a requirement to instantiate eight separate AI agents.

## Research lanes extracted from the article

The article proposes four initial families of opportunity:

1. statistical arbitrage / relative-value spreads;
2. volatility and options mispricing;
3. factor decomposition / cross-sectional anomalies;
4. insider / filing-driven signals.

These are useful as starting research lanes, not as a closed universe.

## What should NOT be copied blindly

The following are article-specific implementation or promotional claims and should not be treated as established project facts without independent verification:

- named model capabilities;
- model pricing and cost comparisons;
- claims of institutional equivalence;
- exact agent counts;
- exact monitoring scale;
- vendor-specific orchestration;
- exact quoted alpha values or thresholds unless validated from primary sources;
- claims that any specific architecture is sufficient for production trading.

## Adaptation rule

Preserve the article's **nature**:

- continuous discovery;
- multiple opportunity families;
- cheap scanning before expensive reasoning;
- explicit hypothesis generation;
- separate validation;
- monitoring of alpha decay;
- replacement of dead strategies.

Change the implementation whenever evidence or project constraints demand it.

## Quant-Trade-specific interpretation

Quant-Trade should evolve from a repository centered on one NASDAQ volatility research thread into an **alpha research operating system** capable of running multiple independent research lanes.

The existing NASDAQ work remains useful as historical research, but it must not define the future research universe.

## New project constraint: no secular-beta dependency

The project must not mistake long exposure to an asset with a persistent positive secular drift for discovered alpha.

A candidate whose economic performance is primarily explained by passive exposure to a broad risk asset fails the spirit of the project even if its backtest is profitable.

This constraint is formalized in `docs/MARKET_SELECTION_DOCTRINE.md`.
