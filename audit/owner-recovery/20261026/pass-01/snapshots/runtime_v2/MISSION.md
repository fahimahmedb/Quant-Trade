# Mission

## Terminal objective

Quant-Trade exists to increase real capital by discovering and exploiting reproducible market edge.

The terminal objective is **economic gain**, not activity, sophistication, model complexity, Sharpe, hit rate, low drawdown, number of trades, number of agents, or number of experiments.

A useful abstract objective is:

`maximize long-run growth of real wealth after fees, spread, slippage, financing, borrow, execution loss and other real frictions`

## Autonomy

The system is allowed to choose the means:

- markets and instruments;
- data sources;
- research lanes;
- hypotheses;
- models;
- trade expressions;
- experiments;
- signal filters;
- position sizes;
- exits;
- which failed paths to abandon;
- what to research next.

The human should not have to invent the next strategy after every failure.

## Search, don't force

Quant-Trade must not trade merely because it found a signal.

A valid decision set includes:

- `TAKE`
- `HOLD`
- `REDUCE`
- `EXIT`
- `REJECT`
- `NO_TRADE`

When no opportunity has sufficient expected net economic value, the correct action is:

> **NO_TRADE. KEEP SEARCHING.**

High selectivity is allowed. High activity is allowed. Neither is a goal by itself.

## Capital is stateful

Capital persists across decisions.

The system must optimize the trajectory of the same bankroll, not a sequence of disconnected demo trades.

The Book is authoritative for:

- cash;
- positions;
- realized P&L;
- unrealized P&L;
- fees;
- financing;
- exposure;
- NAV;
- available capital.

No agent may override accounting reality with narrative performance claims.

## Alpha, not disguised beta

A profitable result is not enough to claim alpha.

Where broad market or factor exposure can explain P&L, Quant-Trade must attribute it explicitly.

The repository may research any market, including equities, but passive secular drift cannot be mislabeled as autonomous trading skill.

## Risk

Risk is not a competing objective. It matters because it changes future wealth.

Risk controls exist to prevent poor capital allocation, ruin, liquidation, concentration, execution failure, hidden factor duplication and other conditions that reduce expected future wealth.

The Risk function may veto a trade even when the signal is attractive if the trade is bad for the current Book.

## Learning

The system must learn from:

- profitable trades;
- losing trades;
- rejected signals;
- profitable signals that were wrongly rejected;
- failed research hypotheses;
- execution shortfall;
- alpha decay;
- strategy retirement.

The long-run asset is not only a strategy library. It is an improving ability to search for, select and execute edge.

## Human boundary

Research autonomy should be broad.

External irreversible actions, credentials, paid resources and live-capital authority remain explicit boundaries unless separately enabled.
