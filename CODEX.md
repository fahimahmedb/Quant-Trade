# Codex Launch Mandate — Persistent Research Runtime

Work from this branch as the autonomous research-system engineer for Quant-Trade.

Before changing code, read:

1. `MISSION.md`
2. `SOURCE_BASIS.md`
3. `AGENTS.md`
4. `PIPELINE.md`
5. `RUNTIME.md`
6. `README.md`
7. `schemas/research_ticket.schema.json`
8. `schemas/campaign_state.schema.json`
9. the existing `src/autonomous_research/` package, tests, research memory, opportunity map and current `STATE.md`

## What already exists

The first Codex run already built and exercised one end-to-end research vertical slice:

`SCAN -> FILTER -> HYPOTHESIS -> TEST -> VALIDATE -> PAPER/SHADOW -> MEMORY`

Do not rebuild that demonstration from scratch.

Treat it as a worker that can perform one bounded research cycle.

## Mission for this run

Move autonomy out of the temporary Codex task and into the software itself.

Build the first persistent **Research Campaign Orchestrator** around the existing worker.

A Codex task ending, a PR being opened, one experiment finishing, or one candidate being rejected must no longer be interpreted as the end of the Quant research campaign.

## Required runtime capabilities

Implement the smallest restart-safe runtime that can:

1. persist campaign state across process restarts;
2. maintain a research queue;
3. dispatch due research work;
4. record heartbeat / idle state;
5. persist completed-ticket lessons;
6. use memory and the opportunity map to choose the next credible research action;
7. avoid repeating the same dead experiment without new evidence;
8. distinguish `IDLE` from `FINISHED`;
9. distinguish ordinary failed experiments from genuine resource/human boundaries;
10. stop or pause only for an explicit configured reason.

## Normal events that MUST NOT terminate the campaign

Do not treat any of these as a final stop condition:

- one cycle completed;
- one ticket rejected;
- one scanner returned no useful candidate;
- one lane failed;
- one vertical slice was successfully demonstrated;
- one pull request was created.

These are events inside the campaign.

## Genuine campaign boundaries

A campaign may pause or escalate when, for example:

- configured compute/time budget is exhausted;
- no credible next research task can be executed with currently available data;
- a required dataset is unavailable;
- paid or permissioned access is needed;
- credentials or an external account are needed;
- an explicit human boundary is reached.

When blocked, preserve the exact reason in campaign state.

## Queue behavior

The runtime should maintain persistent task state rather than a transient Python list.

At minimum each queued task should expose:

- task ID;
- research lane;
- source / parent ticket;
- priority;
- status;
- reason it exists;
- required data/resources;
- attempt count;
- blocked reason when applicable.

The orchestrator should be able to promote a next action from:

- a ticket's lesson / next-action hint;
- the opportunity map;
- research memory;
- newly available data.

## Heartbeat behavior

If the system has nothing useful to execute right now, remain `IDLE` rather than pretending the research mission is complete.

Heartbeat/state should make clear whether Quant is:

- actively processing a ticket;
- waiting for new data;
- waiting for a scheduled scan;
- blocked by missing resources;
- paused by budget;
- explicitly stopped.

## Reuse the first worker correctly

The existing PR #7 implementation is a bounded research worker and proof of integration.

Do not keep rerunning the same NDX experiment against the same unchanged dataset merely to create activity.

Use data fingerprints / completed-task identity / memory to prevent duplicate work.

If the next credible research direction requires a dataset that is not present, represent that as a blocked queued task and continue any other executable work before escalating.

## Testing requirements

Add tests for at least:

- campaign state persistence across restart;
- queue persistence and ordering;
- completed work not being immediately repeated;
- rejected ticket leading to another queued action when one is available;
- `IDLE` not being treated as `STOPPED`;
- explicit budget / resource boundary producing a recorded pause/block reason;
- heartbeat updates without corrupting research memory.

## Deliverables

Leave the branch with:

1. a campaign/orchestrator module;
2. persistent campaign-state storage matching `schemas/campaign_state.schema.json`;
3. a persistent research queue;
4. a scheduler/heartbeat entry point;
5. tests for lifecycle and restart behavior;
6. updated `STATE.md` explaining what can now keep running without a Codex task;
7. a short runbook describing how to start, inspect, pause and resume the research runtime.

## Definition of done

The task is not complete merely because one cycle can run.

It is complete when the repository contains a research runtime whose state survives the Codex task and which can decide whether to run, idle, queue follow-up work, or pause at a genuine boundary.

## Final instruction

Codex is the builder.

Quant is the thing that should keep going.
