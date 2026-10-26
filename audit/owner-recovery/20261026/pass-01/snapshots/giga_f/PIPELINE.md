# Research Factory Pipeline

This file defines the Research Factory sub-pipeline only.

It does **not** define the whole Quant system. Read `QUANT_NORTH_STAR.md`, `SYSTEM_ARCHITECTURE.md` and `OPERATING_MODEL.md` first.

Canonical research loop:

`OBSERVE -> SCAN -> FILTER -> HYPOTHESIZE -> TEST -> VALIDATE -> REGISTER -> LEARN -> CONTINUE`

## SCAN

Generate broad, inexpensive research candidates from point-in-time data.

## FILTER

Remove stale, duplicate, low-materiality or already-discredited candidates before expensive reasoning.

## HYPOTHESIZE

Define a falsifiable mechanism, required information, benchmark and failure condition.

## TEST

Run the smallest credible causal test with explicit timestamp semantics and machine-readable evidence.

## VALIDATE

Attempt to falsify the result using timing/leakage checks, out-of-sample behavior, beta/factor attribution, modeled costs, sensitivity, regime dependence and concentration checks as relevant.

Possible outcomes include `REJECT_RESEARCH`, `REVISE` and `VALIDATED`.

## REGISTER

A surviving result should become a versioned strategy definition with evidence and lifecycle state, rather than remain only a backtest artifact.

## LEARN

Persist what failed or survived and how that changes future research priority.

## CONTINUE

Choose the next highest-value executable research action automatically. Ordinary failed tests do not require the human to invent the next strategy.

## Boundary

Research is one subsystem of Quant. Whole-system behavior, persistent economic state, Control/Data/Build planes and the project status surface are defined by the higher-level architecture documents.
