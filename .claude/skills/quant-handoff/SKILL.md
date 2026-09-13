---
name: quant-handoff
description: Produce a compact, audit-ready handoff after a Quant milestone without repeating the whole project story.
disable-model-invocation: true
context: fork
effort: medium
---

Produce an audit-ready handoff from repository truth.

Return only these sections:

- HEAD SHA / branch / PR
- fixes or capabilities completed
- tests and demonstrations actually run
- recomputed research or paper/shadow results, if any
- remaining known limitations and external blockers
- files that contain the authoritative evidence

Keep it concise. Do not restate the North Star, narrate the work session, or claim capabilities that are only represented by enums, docs, stubs, fixtures or unexercised code paths.
