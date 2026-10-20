# CHECKPOINT 016 — Dual-Stream V2 Convergence + Builder Handoff Protocol

Recorded 2026-10-20 (Europe/Paris).

## Status

`CP16_DUAL_STREAM_V2_CONVERGENCE = CURRENT`

This checkpoint updates the execution model after CP14 and reinterprets CP15.

It does NOT erase CP12–CP15 historical truth. It changes how their conclusions are coordinated.

Observed audit branch HEAD before CP16:

`aa69b85687584c10e5573edf42406f29ccddd099`

Observed active V2 HEAD before CP16:

`38cd0690198e0ece412199e58814ce24bfc718bb`

Observed V2 message:

`Research OS document_or_fundamental_research FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-009-g2-1f0dfeb69ba1 [skip ci]`

All four hard authorities remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

---

## 1. Correction of execution model

CP14 correctly identified four blocking closure classes:

1. Real Oracle V2 -> existing Live Lab E2E
2. V2 post-reboot automatic recovery
3. CP12 historical capability / scientific-memory reconciliation
4. Canonical V2 trunk + repository/workflow consolidation

However, CP14 recorded an older sequencing assumption in which Closures 1+2 were handled separately, CP12 handled Closure 3, then Closure 4 occurred afterward.

The Owner and assistant subsequently concluded that this split wastes context and increases the risk of inconsistent architectural decisions.

The updated execution model is:

`FINAL INTEGRATOR / CLOSURE SUPERVISOR`

may coordinate Closures 1, 2 and 3 in parallel where dependencies permit, and may enter Closure 4 only after the required convergence gate is satisfied.

External actions may remain Owner-only where secrets, VM reboot, administrative control or destructive operations are required.

This supersedes only CP14's sequencing assumption, not CP14's factual closure findings.

---

## 2. Second correction: Closure work and V2 improvement are not strictly serial

A second stream now exists:

`V2 BUILD / IMPROVEMENT STREAM`

This stream examines the current V2, prior Builder design intent, historical capabilities, CP15 design hypotheses and the North-Star target, then improves only real residual gaps.

It must NOT wait passively for all Closure work to finish if safe independent progress is possible.

Likewise, Closure 4 must NOT canonicalise an architecture that is known to be mid-improvement.

The authoritative work graph is now:

```text
                    CURRENT V2
                        |
          +-------------+-------------+
          |                           |
          v                           v
 CLOSURE / FORENSIC STREAM      V2 BUILD / IMPROVEMENT
          |                           |
   Closure 1 / 2 / 3          analyse existing vs planned
          |                           |
   reconcile history            identify true gaps
          |                           |
          |                     build / test / prove
          |                           |
          +-------------+-------------+
                        |
                        v
                 CONVERGENCE GATE
                        |
                        v
                    CLOSURE 4
                        |
                        v
                  CANONICAL V2
```

`CLOSURE_4 = FINAL_CONVERGENCE`

not simple Git cleanup.

---

## 3. CP15 authority is reclassified

CP15 remains valuable, but its twelve specifications are NOT mandatory build tasks.

They are now classified as:

`V2_EDGE_DISCOVERY_DESIGN_HYPOTHESES`

A capable Builder must challenge each CP15 proposal against:

- current implementation;
- prior Builder design intent;
- CP12 historical capabilities;
- current V2 runtime state;
- North-Star system objective.

For any CP15 item the Builder may conclude:

- already solved;
- solved differently and more strongly;
- historical capability exists and should be imported;
- partially missing;
- genuinely missing;
- wrong abstraction / should not be built.

CP15 MUST NOT be implemented mechanically.

---

## 4. Prior Codex Builder missions are design intent, not executable dogma

Previously drafted Builder 2–5 missions remain useful evidence of intended capabilities:

- frozen experiment protocol / deterministic future runner;
- independent Validator / Red Team;
- economic identity / portfolio interpretation;
- producer evidence depth.

Before implementing them, a Builder must determine what current V2 already contains and what residual capability is actually missing.

The question is not:

`Did we execute the old prompt?`

The question is:

`Does current Quant possess the property that prompt was designed to guarantee?`

---

## 5. Required Builder reasoning model

The V2 improvement Builder must work at system level:

```text
UNDERSTAND CURRENT TRUTH
        -> RECONSTRUCT PRIOR INTENT
        -> RECONSTRUCT NORTH-STAR TARGET
        -> COMPARE
        -> IDENTIFY RESIDUAL GAPS
        -> SEARCH HISTORY FOR EXISTING CAPABILITY
        -> DESIGN MINIMAL COHERENT DELTA
        -> IMPLEMENT
        -> TEST / FALSIFY
        -> HANDOFF
```

Do not reduce this mission to a checklist of preselected fields or files.

---

## 6. Continuity requirement: simple AI first, Codex later

The Owner may begin V2-forward work with a simpler AI before Codex becomes available.

Therefore every meaningful Builder task MUST end with a durable Builder Checkpoint.

The checkpoint is part of the work product, not optional documentation.

Its purpose is to make capability and intent transferable across model changes.

A later Codex session must be able to resume from the latest Builder CP without reconstructing the previous model's hidden reasoning.

---

## 7. Mandatory Builder Checkpoint contract

After EACH coherent task or substantial subtask, push a durable Builder CP.

Use the repository's existing handoff/checkpoint conventions where appropriate; do not create unnecessary top-level architecture solely for checkpoint storage.

Each Builder CP must contain at least:

- checkpoint id / task name;
- agent role/class if useful;
- exact working branch;
- exact base SHA when task began;
- exact branch HEAD at checkpoint;
- fresh observed active Oracle V2 HEAD;
- objective of the task;
- what repository evidence was inspected;
- prior design intent considered (old Builder prompts / CP15 / CP12 etc.);
- existing capability found;
- exact gap concluded;
- files / surfaces changed;
- commits produced;
- tests executed and results;
- adversarial / falsification checks where relevant;
- authority flags;
- scientific/outcome-access statement;
- unresolved risks;
- explicit remaining work;
- exact next resume action;
- whether the task is safe for another agent to continue immediately;
- integration / Final Integrator handoff implications.

No Builder CP may claim a runtime, Site, VM, economic or scientific property that was not actually evidenced.

---

## 8. Checkpoint cadence

The minimum cadence is one Builder CP after every coherent task.

Create an additional checkpoint before any transition where losing context would make recovery expensive, including:

- major architectural decision;
- historical capability import;
- high-risk refactor;
- externally blocked operation;
- branch handoff;
- large test/qualification milestone;
- switch from simple AI to Codex.

Commits alone are not sufficient because a commit says what changed, not why it changed or what remains.

---

## 9. Simple-AI operating policy

The initial simpler AI is allowed to make useful progress.

It should preferentially perform work that is:

- repository-grounded;
- reversible;
- testable;
- bounded;
- compatible with the North Star;
- unlikely to require hidden architectural assumptions.

It may investigate, reconcile, implement and test when evidence is clear.

It should avoid speculative broad rewrites merely to appear productive.

When uncertainty materially exceeds its confidence, it should leave a precise CP with evidence, options and blocker rather than inventing certainty.

This is not permission to stop after trivial work: continue independent useful tasks where safe.

---

## 10. Codex takeover policy

When Codex becomes available, it must NOT restart the project or blindly rerun old prompts.

Codex takeover sequence:

1. read `QUANT_NORTH_STAR.md`;
2. read fresh audit branch HEAD and CP12–CP16;
3. resolve fresh active V2 HEAD;
4. read current `CLAUDE.md` / V2 policy / active epoch;
5. locate and read the latest Builder Checkpoints from the simple-AI stream;
6. verify their claimed HEADs / commits / tests against repository evidence;
7. reconstruct completed capability and remaining delta;
8. continue from the latest valid resume point;
9. preserve or correct prior work with explicit evidence;
10. keep producing Builder CPs after every coherent task.

Codex may challenge and revise earlier Builder conclusions; it must preserve provenance rather than silently overwrite them.

---

## 11. Scope relationship with Final Integrator

The V2 Builder stream and Final Integrator stream have different primary responsibilities.

### Final Integrator / Closure Supervisor

Owns:

- Closure 1 real V2 -> Site proof;
- Closure 2 V2 reboot proof;
- Closure 3 CP12 global historical reconciliation;
- final cross-stream convergence;
- Closure 4 canonicalisation;
- repository/workflow authority clarity.

### V2 Builder stream

Owns:

- analyzing current V2 against prior intended properties and North Star;
- challenging CP15 economic-depth hypotheses;
- identifying true residual capability gaps;
- reusing historical capabilities where discovered;
- building and testing justified V2 improvements;
- preparing clean handoff into final convergence.

The streams may exchange evidence and capability handoffs.

Neither should duplicate the other's work unnecessarily.

---

## 12. Closure 4 convergence gate

Closure 4 may only canonicalise the final pre-outcome V2 when:

- operational closures are closed or explicitly dispositioned;
- CP12 material historical capability reconciliation is sufficiently complete;
- the active V2 Builder workstream has reached a stable handoff boundary;
- no known high-priority V2 improvement package is mid-flight and intended for the canonical target;
- active workflows and routing authority can be stated unambiguously.

Destructive branch deletion remains separate Owner authority unless explicitly granted.

---

## 13. Final pre-outcome target

The target before any economic authority decision remains one coherent Quant V2 with:

- qualified autonomous runtime;
- restart/reboot recovery evidence;
- factual Live Lab projection;
- Data/Evidence provenance and PIT discipline;
- Research Factory with strong producer/validation/disconfirmation capability;
- normalized scientific and negative memory;
- explicit economic identity / portfolio / readiness state;
- preserved Capital Desk and persistent Book;
- sealed Evaluation membrane;
- one canonical authority surface;
- reconstructable history;
- Builder continuity independent of model/session.

Only after this convergence may the Owner separately decide whether to authorize economic experimentation.

---

## 14. Binding markers

`CP14_FOUR_CLOSURE_CLASSES = RETAINED`

`CP14_OLD_SEQUENCING = SUPERSEDED_BY_CP16`

`FINAL_INTEGRATOR_MAY_COORDINATE_CLOSURES_1_2_3 = TRUE`

`CLOSURE_4_IS_FINAL_CONVERGENCE = TRUE`

`CP15_STATUS = DESIGN_HYPOTHESES_NOT_MANDATORY_BUILD_LIST`

`OLD_BUILDER_PROMPTS_STATUS = PRIOR_DESIGN_INTENT`

`SIMPLE_AI_MAY_START_V2_FORWARD_WORK = TRUE`

`BUILDER_CP_REQUIRED_AFTER_EACH_COHERENT_TASK = TRUE`

`CODEX_MUST_RESUME_FROM_LATEST_VALID_BUILDER_CP = TRUE`

`ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`LIVE_TRADING_AUTHORIZED = FALSE`

Resume marker:

`CP16_RESUME_POINT = DUAL_STREAM_WORK_ACTIVE_WITH_CHECKPOINTED_SIMPLE_AI_TO_CODEX_CONTINUITY`
