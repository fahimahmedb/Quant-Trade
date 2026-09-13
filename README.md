# Quant — Persistent Autonomous Quantitative System

Quant exists to increase real capital by repeatedly discovering, selecting and exploiting genuine market edge.

Read **`QUANT_NORTH_STAR.md` first**. It is the highest-level product specification for this repository.

Quant is not a backtester, a scanner, an LLM wrapper or a collection of strategies. The target is a persistent system combining:

- Control Plane / Clock;
- Data Plane;
- Research Factory;
- the paper/shadow functional chain `SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK`;
- persistent Book/economic state;
- learning feedback;
- Build/Codex plane;
- status/control UI backed by real state.

## Architecture

```text
                     HUMAN / PROJECT CONTROL
                              |
                              v
                       ROOT / CLOCK
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       DATA PLANE       RESEARCH FACTORY       BUILD PLANE
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                  SCAN -> VET -> SIZE -> RISK
                              -> FILLS -> BOOK
                                     |
                                     v
                              LEARNING / MEMORY
                                     |
                                     +----> SEARCH AGAIN
```

Quant System V1 is developed in persistent paper/shadow mode while preserving the topology of the intended complete system.

## Source basis

The supplied source material contributes the principles of continuous strategy discovery, alpha replacement/decay, broad inexpensive monitoring before deeper reasoning and specialized functional roles.

The project screenshots contribute system-level ideas including persistent runtime, `RUN/IDLE` state, ticket/activity traceability, bankroll continuity and the visible `SCAN/VET/SIZE/RISK/FILLS/BOOK` chain.

Their financial results, vendor claims and performance numbers are **not treated as verified evidence**.

See `SOURCE_BASIS.md`.

## Core specification hierarchy

1. `QUANT_NORTH_STAR.md` — what Quant is and what wins when priorities conflict.
2. `SYSTEM_ARCHITECTURE.md` — whole-system planes and boundaries.
3. `OPERATING_MODEL.md` — how the system behaves over time.
4. `MISSION.md` — terminal economic objective and autonomy rules.
5. `SOURCE_BASIS.md` — source-derived ideas versus project adaptations.
6. `PIPELINE.md` — Research Factory sub-pipeline, not the whole product.
7. `STATE.md` — current implementation/research frontier.

Lower-level documents and code must not silently redefine the North Star.

## Running the system

The system has no third-party dependencies. Python 3.11+ and the standard library are enough.

```bash
python3 scripts/ingest_data.py          # Data Plane: refresh and fingerprint datasets
python3 scripts/quant.py boot           # resume persistent state, seed due work
python3 scripts/quant.py run            # run until IDLE
python3 scripts/quant.py status         # status surface, rendered from real state
python3 scripts/quant.py brief          # regenerate CHIEF_BRIEF.md
python3 scripts/quant.py health         # watchdog report
python3 scripts/quant.py tick           # advance exactly one unit of due work
python3 scripts/quant.py pause --reason "..." | resume
```

Verification:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 scripts/demo_quant_system.py    # boot, stop mid-campaign, restart, resume
python3 scripts/generate_schemas.py --check
```

`ingest_data.py` fetches from a free credential-free source when the network allows and
otherwise re-registers the fingerprinted snapshot committed under `data/datasets/`, so every
published result is reproducible offline. It never fabricates a bar.

### Where state lives

| Path | Contents | Committed |
| --- | --- | --- |
| `data/datasets/*.csv` | normalized price panels | yes |
| `data/datasets/*.meta.json` | provenance, caveats, validation, fingerprint | yes |
| `schemas/` | contracts for the persistent state objects, generated from the code | yes |
| `var/` | live operational state: control state, work queue, ledgers, tickets, events | no |

A different `--root` gives a fully isolated system, which is how the tests and the restart
demonstration avoid touching operational state.

## Current state

Quant System V1 is implemented end to end in persistent paper/shadow mode: Control Plane clock,
Data Plane with real ingestion, Research Factory with a versioned strategy lifecycle, the
`SCAN -> VET -> SIZE -> RISK -> FILLS -> BOOK` chain, a persistent Book, a learning loop that
scores the system's own rejections, and a status surface plus `CHIEF_BRIEF.md` rendered from
that state.

`STATE.md` carries the current evidence, including what the research actually concluded and
which North-Star gaps remain open.

## Historical NASDAQ work

The existing NASDAQ research predates the rebuild. It remains prior evidence and reusable code where useful, but it does not define Quant's future market universe or architecture.

## Build philosophy

The engineering agent is the Builder / Quant Engineer. Quant is the persistent system.

A build task may end. Quant's state, Book, research memory, pending work and next legitimate action must remain coherent.

Build large coherent North-Star milestones instead of accumulating unrelated micro-fixes.
