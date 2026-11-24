# Quant-Trade — AI Working Method V1

STATUS=`ACTIVE_METHOD`
DATE=`2026-11-02`
PURPOSE=`Make every AI advance the same canonical project without restart, parallel rebuild, stale authority or false PASS.`

This remains the single working method for Builder, Reviewer, Research, Operator and coordinating AI. The 2026-11-02 change does not create a second methodology: it makes the existing mission-admission gate executable on real material missions.

## 1. Two-branch law

Only two branches may carry current authority:

- `project/canonical` — objective, current router, decisions, scientific memory, receipts, blockers and next action;
- `code/canonical` — executable product, tests, workflows and deployment/runtime helpers.

Historical information may remain in Git history or evidence, but it is not a third current authority. Branch names, the repository default branch, stale prompts and chat memory are not authority.

## 2. Single bootstrap for every AI

Before substantive action:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `QUANT_NORTH_STAR.md` and this method on `project/canonical`;
3. read `governance/CURRENT_PROJECT_STATE.md`;
4. resolve exact current project/code SHAs and current router identity;
5. inspect only evidence relevant to the current blocker/decision;
6. classify existing capability as `REUSE`, `CONNECT`, `REPAIR`, `BUILD_REQUIRED`, or `UNKNOWN`;
7. perform the real mission admission below before any material mutation or authoritative project decision.

If durable current state proves the requested work is already complete, return `NO_CHANGE_REQUIRED` and continue from the recorded next action.

## 3. Real mission admission gate

A material AI mission is executable only after creating or replacing the single machine-readable receipt:

`code/canonical:.quant/MISSION_ADMISSION.json`

The receipt is an input to enforcement, not documentation. It must contain fresh values for:

- mission identity/type/timestamp;
- `PROJECT_CANONICAL_SHA`;
- admitted `CODE_CANONICAL_SHA`;
- current router identity;
- exact current subject;
- current blocker or decision;
- target F0–F6 gate or recorded blocker;
- existing capability: `REUSE | CONNECT | REPAIR | BUILD_REQUIRED | UNKNOWN`;
- why the work can change the decision;
- minimal decisive test;
- one concrete counterexample;
- durable output required;
- next action after PASS/FAIL/BLOCK;
- Owner-authorization requirement/status;
- active seam and concurrency counts;
- requested action;
- `primary_evidence` for decision-changing exact claims, as defined in §13.5.

Before substantive work, validate the real receipt with the canonical validator on `code/canonical` against the fresh project SHA, admitted code SHA and router identity.

A copied receipt from another mission is invalid. A receipt becomes stale when the project head, code head or router identity it binds moves, unless exact equivalence is explicitly proven. Reconcile and regenerate it; never silently reuse it.

Pure automatic ingestion changes confined to `data/feeds/**` are exempt because they are not AI project missions or project decisions. The exemption does not extend to code, workflow, governance, research-decision or operational-authority mutations.

## 4. Admission → completion binding

Every material authoritative PASS/handoff must bind to the immutable identity `sha256(canonical-json(admission))` and the exact published/tested subject SHA.

A material result with no valid admission link, wrong tested SHA, local-only output or no next action is `NON_AUTHORITATIVE_RESULT`, not PASS.

The hosted `AI Working Method Gate` is post-push detection/qualification. It does not become server-side prevention merely because it is green. Server-side required-check enforcement must be separately demonstrated.

## 5. Progress order

Always prefer:

`REUSE > CONNECT > REPAIR > BUILD`

A new architecture, scheduler, control plane, memory system, framework or agent layer is forbidden unless a concrete current gate cannot be closed with the first three choices.

`UNKNOWN` blocks only the affected action. It does not authorize repository-wide archaeology.

Hosted reasoning is reserved for a demonstrated high-value engineering or validation gap that deterministic checks/local GPT-OSS cannot close. Routine inspection, prioritization, waiting, summaries and no-delta monitoring stay local. State an invocation budget before dispatch; do not silently renew it by renaming a failed task. The current F3 transport trial allows one builder and at most one review, with no paid automatic retry. Invocation limits are not a token or monetary ceiling; do not invent usage estimates.

## 5.1 Opportunity-rescue law — challenge the implementation before PARK

A documented implementation blocker is not, by itself, proof that its underlying
economic/scientific mechanism is false. Before proposing a terminal `PARK`,
`BLOCK` or `STOP` for a candidate, perform a **bounded decision-changing
solution search** within the existing mission and authority:

1. **Name the failure precisely.** Distinguish mechanism/inference, frozen
   experimental expression, instrument/right, point-in-time information, access
   or custody, broker/corporate-action transmission, cost/liquidity, execution
   clock, data licensing, and Owner/VM permission. State whether the failure is
   `FALSIFIED`, `NOT_IMPLEMENTABLE_ON_TESTED_ROUTE` or `UNKNOWN`.
2. **REUSE first.** Inspect existing source qualifications, negative memory,
   admissible alternatives, available connectors and previously tested routes.
   Do not replay closed trials or rebuild an exhausted research architecture.
3. **Challenge plausible solutions, not arbitrary variants.** For each
   materially distinct, feasible path capable of changing the next decision,
   examine the exact right/instrument, legally accessible intermediary or
   transfer agent, causal information timestamp, actual operational action,
   fees, delay, worst-case downside, and documentary proof. Prefer a small
   set of decisive alternatives over exhaustive broker scans or limitless
   creativity. Do not use unauthorized resources or circumvent access rules.
4. **Choose the least costly decisive discriminator.** When one missing
   document, entitlement, fee schedule, time-of-publication check or
   independent synthetic-safe test can resolve a path, pursue it within scope
   before a broad PARK. If primary evidence cannot be obtained within
   the authorized bound, mark that path `UNKNOWN` with exact reopen evidence.
5. **Preserve scientific identity.** Never alter a frozen T0, first-event
   selection, cost/size, source route, outcome membrane or trial accounting
   because a result or broker constraint is inconvenient. A different
   instrument, broker-execution rule, information clock or payoff expression
   that materially changes the inference is a **distinct, linked prospective
   hypothesis**, admitted and predeclared before any new outcome access;
   it does not reset multiplicity or transform contaminated history into OOS.
6. **Classify narrowly.** `PARK_IMPLEMENTATION` in prose may close a tested
   route while preserving the family as `CONDITIONAL_FEASIBILITY` or
   `UNKNOWN`. Use the existing machine `PARK/BLOCK/UNKNOWN` states; do
   not invent a new scheduler, router or authority enum. When a mechanism is
   economically falsified by a valid test, record that negative result instead
   of inventing rescue variants to evade it.
7. **Hand off one decision-changing next action.** Record paths actually
   checked, primary proof or contradiction, not-checked high-value path if
   any, conclusion by mechanism versus implementation, next exact witness,
   and stop/reopen condition in existing evidence/checkpoint surfaces.

**Machine receipt boundary.** For material `PARK/BLOCK` completions, the
existing admission/completion validator must require an explicit disposition
scope. An implementation-specific terminal result needs a bounded rescue
review, the decisive witness/reopen condition and an explicit non-falsification
of the underlying mechanism. A proven authority/safety stop can remain
immediate. The validator checks declared structure and binding, **not**
whether a model genuinely considered every economic alternative. That
requires independent behavioral challenge and eventual runtime witnesses.

**Real FINAL_HANDOFF binding.** The existing GitHub method gate uses an outer
completion `claim=PASS` to represent successful transmission of a
`FINAL_HANDOFF`, even when the **actual** admitted result is
`handoff_result=PARK` or `handoff_result=BLOCK`. Terminal behavioral
requirements apply to the admitted `handoff_result`, not merely the outer
CI claim. For such a terminal result, include `disposition_scope`,
`exact_reopen_condition` and, where implementation-specific,
`tested_implementation_route` and `solution_search` in the **same
mission admission**, causally bound to opened primary evidence. A
`CHECKPOINT` is not terminal; a proven Owner/safety prohibition can
be recorded as a direct scoped hard stop without speculative rescue.

**Stopping discipline.** Do not extend a solved decision, audit an audit,
or enumerate speculative routes. Stop when remaining alternatives cannot
materially change the decision, have no lawful/technically plausible path,
lack required Owner authority or verified budget/permission, entail
unacceptable risk, or would require a forbidden post-outcome protocol change.
A local blocker never stops unaffected authorized work. A valid PARK is
acceptable after this bounded challenge; numerical counts of options,
reports or synthetic tests are not success metrics.

**Scope.** This is a decision-quality rule, not an authorization to trade,
observe prospective/economic outcomes, invoke agents, access paid data, spend
capital, alter runtime or mutate another active seam. An agent's statement
that it searched is not behavioral proof; fresh-agent counterexamples and
real operating decisions must be checked separately.

## 5.2 Economic research behavior — fresh and long-context AI

This extends the **same** canonical method and existing §5.1 rescue rule. It does not create a new memory, router, gate, agent, or experimental authorization. Both `FRESH_CONTEXT` and `LONG_CONTEXT` AIs are subject to the same scientific and authority boundaries. Their **starting failure modes differ**:

- **`FRESH_CONTEXT` AI:** bootstrap from fresh `project/canonical` and `code/canonical` heads, `QUANT_NORTH_STAR.md`, the current router and this method. Retrieve only decision-changing Git objects and frozen result evidence. Never fill absent historical context with a guess, treat chat reconstruction as a prerequisite, or redo a proved finished/failed experiment without a new material contradiction. Form an independent hypothesis about how the decision could create value. Identify the payer when the mechanism depends on one. Use earlier rankings as locators.
- **`LONG_CONTEXT` AI:** its accumulated chat, remembered SHAs, previous answers and lengthy analytical narratives are **not** authority. Re-fetch heads/router and reconcile previous decisions with current exact primary evidence. Specifically challenge anchoring, prior rapid-reasoning assumptions, omitted negative results, stale permissions and concurrent work. Preserve continuity and proven closed work, but do not treat confidence, elapsed reflection time or context length as economic proof.

**Common economic decision order** (all roles, including Research and Reviewer):

1. **Reconcile, reuse and bound.** Identify current authorized decision; reuse existing positive/negative trials and prior scientific exposure; stop when no decision-changing evidence remains. Avoid auditing audits.
2. **Economic cause before software.** Explain how the decision could affect real net wealth. Where payment depends on a constraint or contractual right, identify the payer, constraint and exact entitlement. Assess available capital, risk and capacity. Separate a documented mechanism, a frozen testable expression, an actual implementation route and observed net result.
3. **Feasibility and capturability.** Screen for a plausible route at discovery. Before ranking a route as executable, verify its applicable conditions. These include point-in-time public information and its time relative to ownership/eligibility, settlement, custodian/broker access, tax withholding and cash immobilization, permitted orders, real bid/ask depth, borrow, financing, fixed and variable fees. Unknown broker or tax access means `UNKNOWN/BLOCK` **for that route**, not mechanism `FAIL`.
4. **Predeclare one discriminator.** Write the smallest decisive hypothesis, falsifier, timestamp, instrument, costs, executable trade size, negative case and expected proof **before any new outcome access**. Do not reselect first events, rewrite frozen T0, reset multiplicity or call post-hoc cases out of sample.
5. **Test the actual claim, not a proxy.** Successful workflow/CSV capture is `PASS_DATA` only; normalized OHLCV gaps are descriptive, **not executable arbitrage**. Inspect workflow runs by relevant event (a PR-filtered empty search cannot exclude a push run). Same-date archive recollections with volume restatements are **not independent experiments**: retain both versions and their sensitivity.
6. **Challenge and scope a negative.** For a hindsight upper-bound oracle, document the exact horizon, number of trades, long/short hedge, volume fraction, assumed fees and whether the no-trade action gives zero. A negative oracle rejects only the tested family under these constraints; do not falsely eliminate an entire mechanism or rescue a genuinely negative frozen expression by re-fitting it.
7. **Keep the evidence ladder strict.** `MECHANISM_DOCUMENTED → ACCESS_VERIFIED → PIT_SIGNAL_ADMISSIBLE → OBSERVED_INDICATIVE_PRICES → EXECUTION_MODEL_TESTED → NET_EXECUTION_OBSERVED → REPEATABILITY_PROVEN`. These are distinct evidence claims, **not a requirement that every mechanism follows one temporal sequence**. No profitable-edge claim from a model, CI, paper outcome or hindsight upper bound. Distinguish economic premium for assumed risk from proven alpha.
8. **Stop with one next decision.** Return a scoped `PASS/FAIL/PARK/BLOCK/UNKNOWN`, the decisive opened evidence, one counterexample, tested versus merely proposed checks, exact reopen condition and one bounded next action. Prefer `NO_CHANGE_REQUIRED` when the prior result already settles the exact expression.

**Mandatory counterexamples from actual research history:**

- A missing workflow run from a **PR-only** lookup does not prove absence of a **push** run. Confirm the correct event and inspect actual logs/artifacts.
- Two downloads covering **the same five ETF sessions** are revised measurements, not two OOS confirmations. Yahoo 1m bars are not guaranteed executable quotes.
- A negative constrained one-trade-per-session ETF oracle after **hypothetical** fees does not invalidate other horizons, instruments or all relative value; no-trade gives a zero benchmark.
- A negative predeclared crypto-carry expression must not be replayed unchanged; a Russell data-access blocker must not be mislabeled an economic falsification.
- An odd-lot tender right requires exact SEC publication/ownership deadlines, beneficial holder aggregation, broker participation, withholding and stress costs **before** using an offer-price spread as expected profit.
- A positive historical options/VIX statistic is a **locator until the exact instrument, primary run, costs, margin, sample, and entitlement are checked**; VIX-index fear-spike studies are not automatically VIX-options strategies.

**Test and claim boundary.** `governance/tests/test_economic_research_behavior_contract.py` checks the project policy, both AI profiles, explicit adversarial cases and unchanged F0–F6/authority/non-regression invariants. It is a **static contract test**. Actual fresh-context and long-context model behavior needs separate, independently executed cases on the **same frozen prompt and exact heads**; until then `behavioral_e2e_witness=NOT_PROVEN`. No test grants economic, prospective, capital or trading authority.

### 5.2.1 AI fallibility and bounded anti-drift (all roles and missions; Owner issue #59)

The objective is real net wealth after costs, tax and inflation at comparable external flows and within the mandate, not intellectual perfection. All reference frames, curricula (including Master 203), models, consensus, judges and this method itself are contestable. Preserve the existing authority and scientific boundaries, including §5.1.

Before material research or meta-research state the concrete decision, economic or gate impact (in euros or justified bound where applicable), decisive missing information and stop condition. Use one cycle: objective and mandate → decision → primary evidence → targeted challenge → minimal correction → verification → decision and stop. PARK immaterial work; UNKNOWN is local. Do not reopen methods absent a concrete decision-changing contradiction or evidence of material benefit. Do not turn abstract fallibility into infinite audits or repeated permission requests.

- Self-confirming frame: consider a genuinely distinct alternative, including no change, if it could change the decision.
- False consensus: require evidence independent of AI agreement.
- Biased judge: prefer independently checkable criteria and cases.
- Unknown opportunity: bound its material impact where justified; otherwise UNKNOWN, not claimed exhaustiveness.
- Luck versus competence: use independent observations, distinguish decision quality from outcomes.
- Fallible verifier: give an observable falsifier, including for this method; stop after bounded challenge when further checks cannot materially change the decision.

For the existing A/B pilot only, retain actual A with provenance (label any reconstruction), B as unvalidated hypothesis. If admitted and unfinished, reuse isolated equal-resource trials with precommitted economic thresholds and stopping rules, independently calculable synthetic twin cases, irrelevant changes, decoys, no-op cases and repetitions within budget. Accept justified conditional answers; do not impose unjustified priority inversions. Report discoveries, omissions, false alerts, erroneous abstentions, feasibility and research cost separately. Target judge/style controls (A/A, placebo, independent labels) only if decision-changing. Synthetic evidence covers represented mechanisms only; capture–recapture estimates and expert envelopes are not guaranteed bounds. Reproducible material B gain without material degradation warrants further qualification, not activation; demonstrated absence of material gain retains A; ambiguity or insufficient power is UNKNOWN with A provisional. Resume already authorized work. No new architecture, global score, agent consultation or economic authority follows. Written rules and static tests do not prove actual behavior.

### 5.2.2 Open financial discovery and the value of combined information

Independently look for investment decisions worth investigating within the mandate. An instrument, an observation or a contradiction can reveal a decision the project has never proposed. Name the choice it could change before committing material research effort. Draw on any relevant discipline and pursue original hypotheses or new applications of known mechanisms. Macroeconomics, quantitative analysis and news are examples. The decision determines which sources to consult and how many are worth using.

Trace each relevant input to its original observation, version and availability at the decision time. Examine common origins, dependencies and contradictions. Ask what each input adds given the others, including cases where only their interaction could change the choice, position size, hedge, execution or abstention. Two reports repeating an issuer notice convey the same observation. The notice and a custodian's independently set election deadline can jointly determine whether the holder can act.

Retain a hypothesis for documentary qualification when its mechanism, plausible effect on real net wealth and practical feasibility warrant the effort. Record uncertainty, including a hard-to-verify condition, and the next piece of evidence that could change the decision. Profitability can still be unknown at discovery. Ease of testing, complexity and novelty carry no presumption of value. A search may end without a qualifying idea.

For later evaluation, select the best simple feasible counterfactual before seeing outcomes. Compare real wealth after costs, tax and inflation at comparable risk, external cash flows, horizon and liquidity constraints. Predeclare the comparisons that could distinguish marginal and joint contributions. Keep independent validation data outside discovery and selection. Account for trials and variants, including failed attempts and previous exposure, and preserve scoped negative results under §5.1. Economic experiments require separate explicit Owner authorization.

### 5.2.3 Decision-relevant tool utilization (all roles)

During the existing bootstrap/admission, identify decision-changing information and execution gaps. Inspect existing primary evidence and tools actually exposed in the current host. REUSE > CONNECT > REPAIR > BUILD. If an authorized, available specialist tool can materially improve primary evidence, independent challenge, acquisition, computation or implementation, an actual call is mandatory before an authoritative conclusion. Otherwise record a precise reason: no material increment, valid existing evidence, duplicate origin, frozen exposure, unavailable tool, unverified permission or budget, confidentiality, or no decision gap. Do not invoke tools merely to meet a count. A local tool block does not stop independent admitted work.

Select the minimum sufficient tools. Discovery: Exa/Tavily; challenge: Parallel; extraction: Firecrawl/Olostep; interactive public access: TinyFish if needed and entitled. Scientific discovery: Consensus/Undermind/Elicit; structured comparison: SciSpace/Elicit; references: Scholar Sidekick/Wiley where relevant; Zotero for an existing library. Independent calculation: Wolfram; reproducible notebooks: Deepnote when independently useful; library documentation: Context7; OpenAI Developers for actual integration. Fundamentals: Legal Data Hunter/CourtListener for appropriate jurisdiction, Brand24 only as a sentiment locator, Amass/Life Sciences tools only for relevant biomedical evidence. DeepL for materially important translation. Manus or Codex dispatch requires existing explicit authority, verified budget and real transport. GitHub remains canonical; Drive/Documents/Spreadsheets support files; Gmail/Calendar only relevant authorized communication; the existing Laboratoire remains read-only. These are examples, not a closed tool registry or a mandatory chain.

Record in the existing admission/evidence/checkpoint surfaces a concise tool receipt: gap, tool, disposition EXECUTED/BLOCKED/SKIPPED, reason, host, access_verified, authorized, budget_verified, primary_refs, validation and decision_impact. Record sanitized request identity/time/version when available. Distinguish installed, available in host, authenticated, successful call, validated output and decision impact. A receipt is a declaration, not independent proof: link actual tool outputs or opened primary objects. Never label an unexecuted call as executed, or a blocked/skip as evidence. Duplicated syndicated sources do not count as independent confirmations; use the original issuer/regulator/exchange and independent computation or evidence where material. Use no private/restricted material externally without applicable authorization and necessity. Never transfer credentials or assume Work, Codex and VM have identical access. No new paid subscription or metered action without verified authority and budget.

For VIX require actual contract identity, exchange/broker margin, executable costs and timing; literature cannot establish fills. For fundamental research verify issuer, event clock, rights and incremental cash flows. For calibration use frozen labels and independent chronological evaluation with identical inputs and resources. Preserve prior exposure, scientific firewall and every existing authority boundary. Stop at decisive evidence or scoped BLOCK/PARK/UNKNOWN. Measure marginal benefit only when observable; no invented usage, performance or Pareto gain.

The existing machine contract and validator are the only enforcement seam. A static policy test proves rule consistency, not agent compliance, authentication or runtime behavior. Independent fresh/long-context and Work/Codex host witnesses are required for behavioral E2E. No new router, gate, scheduler, economic, prospective, capital, production or live authority is created.

## 6. Concurrency and ownership

- one primary Builder may mutate a capability/seam at a time;
- at most two active decision-changing lanes total;
- an independent Reviewer is read-only on the exact published subject;
- if a canonical head moves before publication, reconcile rather than overwrite;
- a blocked lane is `PARK/BLOCK`, not permission to create substitute architecture;
- no private/local-only SHA is shared authority.

## 7. Work lifecycle

Every material unit follows:

`RECONCILE -> ADMIT -> INSPECT -> CHOOSE(REUSE/CONNECT/REPAIR/BUILD) -> CHALLENGE -> EXECUTE -> TEST -> PERSIST -> VERIFY_REMOTE -> UPDATE_ROUTER/NEXT_ACTION -> STOP`

Construction, test, qualification, integration, activation, use and end-to-end proof are separate states. A test/review/CI run for SHA A cannot qualify SHA B unless equivalence is explicitly proven.

## 7.1 Delegated execution without unnecessary Owner round trips

A mission explicitly authorized as BUILD/REPAIR is one coherent work package, not one analysis or one test per Owner message. Within its admitted scope and remaining budget, the agent **must** reproduce a repairable defect, make the smallest permitted correction, re-test, check one material counterexample and continue toward the original acceptance criteria. An initial diagnosis, red test, routine CI failure, checkpoint or recoverable tool error is not by itself a mission-completion event. Do not change a read-only/review mandate into a build mandate.

**Owner authority is a boundary, not a review of every technical choice.** Once delegated, bounded reversible sequencing, source reuse, fixes, test reruns, evidence recovery and independent-lane continuation do not require another Owner instruction. Reconcile exact project/code/router identity and renew the admission as required when heads move; this is a technical fence, not an automatic request for a new strategic decision. A local BLOCK/PARK must not stop unaffected admitted work.

**External-agent/resource preflight.** Before any Codex, second agent, paid tool, automated dispatch or comment capable of triggering one: verify that the Owner has **explicitly authorized that dispatch**, the actual quota/budget is known and sufficient, the real execution surface can access the required canonical sources with the necessary permissions, and the seam has no competing mutator. A generic permission to build, a promising prompt, a connector reaction or a previously working checkout is not authorization or access proof. Unknown quota/permissions/access => do not dispatch; preserve the resource and continue independent work. Never hide a paid retry behind a renamed task.

**Checkpoint versus closure.** CHECKPOINT preserves progress, identities, actual tests, blocker and exact next action; it does **not** mean FINAL_HANDOFF, require an Owner relaunch or prove autonomous re-dispatch. FINAL_HANDOFF is only for an evidenced terminal work-unit result, with the existing completion binding. Distinguish (1) in-session persistence, (2) fresh-agent recovery from durable state and (3) externally triggered automatic resumption; proof of one is not proof of another. Never claim a continuous session or automatic restart merely because the instructions request perseverance.

The success measure is **qualified, materially useful progress per authorized resource**, together with avoidable Owner interruptions. Zero Owner interventions alone is not success if the agent did no useful work.

## 8. Review law

A new independent review is justified only by at least one of:

- a new exact subject;
- new evidence;
- a new counterexample class;
- a previously unavailable primary object;
- an imminent irreversible boundary.

Otherwise return `NO_CHANGE_REQUIRED`. A reviewer without the exact candidate/evidence returns `BLOCK_EVIDENCE` or `UNKNOWN`.

## 9. Durable continuation

At every material interruption preserve in canonical durable state:

- exact current subject;
- work actually completed;
- tests actually executed and result;
- decisions changed;
- blockers/unknowns;
- one bounded next action;
- reopening condition for PARKed work.

A fresh AI must be able to resume from repository state without reconstructing the chat.

Detailed audits remain historical evidence. General working rules belong here; current facts/critical path belong in `CURRENT_PROJECT_STATE.md`; objective/finish meaning belongs in `QUANT_NORTH_STAR.md`. Do not grow a parallel mandatory bootstrap stack.

## 10. Scientific and authority boundaries

Never simplify away exact identity, PIT/causal timing/provenance, frozen scientific protocol/exposure accounting, negative scientific memory, restart/idempotency semantics or fail-closed authority.

Code/tests/CI do not grant economic experiment, prospective observation, production deployment, real-capital or live-trading authority.

## 11. Bounded finish line

`QUANT_SYSTEM_V1_FINISHED` requires every required F0–F6 gate to be PASS on current canonical authority:

- `F0_TWO_BRANCH_AUTHORITY` — only intended canonical authority remains, with residual external/admin exceptions bounded and non-authoritative;
- `F1_RECOVERABLE_CANONICAL_STATE` — a genuinely fresh repository-only agent/session recovers objective, authority, fresh heads, router/blocker, next action, method, already-complete work and correct REUSE/CONNECT/REPAIR/BUILD disposition without chat context or parallel methodology;
- `F2_EXACT_HEAD_ENGINEERING_QUALIFICATION` — exact current code head passes required canonical regression/challenge suite;
- `F3_REAL_VM_MULTI_WAKE` — intended authenticated host proves at least two automatic wakes including real Codex result consumption;
- `F4_GLOBAL_MISSION_CONTINUATION` — after terminal bounded task state, system selects the next legitimate unmet mission or durable NOOP/PARK without human task substitution;
- `F5_IDENTITY_CONSERVING_E2E` — bounded non-economic/synthetic-safe witness preserves identity across the canonical path and recovery cases;
- `F6_OPERATIONAL_HANDOFF` — no P0 engineering/autonomy blocker remains and ordinary future work does not require another architecture campaign.

`QUANT_SYSTEM_V1_FINISHED` does not mean profitable edge, real-capital authorization or live-trading authorization.

## 12. Direction test

Before work starts ask:

1. Which F0–F6 gate does this close, falsify or protect?
2. If none, which current blocker/decision does it change?
3. Is equivalent capability already present?
4. What is the smallest decisive test?
5. What evidence would make us stop?

If 1 and 2 are both empty, do not do the task.

## 13. Required anti-regression behavior

The real admission interface and its tests must fail closed for at least:

- stale project/code/router identity;
- copied/unrelated receipt;
- missing exact subject or blocker/decision;
- BUILD when REUSE/CONNECT/REPAIR is established;
- duplicate review without new decision-changing input;
- local-only PASS;
- unjustified global stop from a local blocker;
- a route-specific implementation BLOCK/PARK generalized to mechanism or family failure without the bounded decision-changing §5.1 challenge;
- an alleged rescue that rewrites frozen prospective conditions, resets scientific multiplicity, or grants economic/capital/live authority;
- WIP or same-seam concurrent-Builder violation;
- missing required Owner authority;
- missing next action;
- wrong-SHA completion;
- false project finish while any required F0–F6 gate is OPEN/BLOCK/UNKNOWN;
- head movement after admission without reconciliation;
- decision-changing exact claims without opened primary provenance;
- a claim promoted despite an opened primary object contradicting it;
- current-state claims supported only by stale/historical-scoped exact evidence;
- `UNKNOWN_SOURCE` silently filled by inference.

Distinguish `TEST_PLANNED`, `TEST_EXECUTED` and `TEST_PASSED`.

## 13.5 Exact-claim provenance and freshness law

This law applies only to **decision-changing exact claims**, not to every descriptive sentence. An exact claim names or materially relies on a concrete SHA, commit title, path, blob, run, receipt, current head, runtime event or other exact identity.

For each such claim used to admit work, change a canonical decision, declare PASS/FAIL/BLOCK, or select the next action:

1. open the decisive primary object in the current mission;
2. record it in the existing admission field `primary_evidence` with at least: `claim_id`, `claim`, `source_kind`, `object_identity`, `observed_value`, `support`, `scope`, and `opened=true`;
3. use `support=SUPPORTS` only when the opened object actually supports the claim;
4. if the opened primary object conflicts with the candidate claim, the primary object wins and the claim is `CONTRADICTED`; do not invent a reconciliation;
5. if no identifiable primary source can be produced, use `UNKNOWN_SOURCE`; do not reconstruct a SHA/title/path/run from plausibility, memory, a summary or adjacent code;
6. search results, Owner statements, summaries, comments and chat memory may locate evidence but are not sufficient primary evidence for an exact decision-changing claim;
7. historical/stale evidence must be scoped as historical. It cannot prove a current-head/current-runtime claim unless freshness/equivalence is separately established;
8. `EXISTS`, `BUILT`, `QUALIFIED`, `INTEGRATED`, `PROMOTED`, `ACTIVE`, `USED` and `PROVEN_END_TO_END` remain distinct claim levels.

The evidence set must be minimal: record only exact claims that can change the decision, unblock the mission or reveal a material risk. Do not turn this rule into exhaustive repository archaeology.

The machine contract/validator must fail closed when required provenance is missing, the source was not opened, an opened primary object is declared as supporting a claim it actually contradicts, or stale-scoped evidence is used as current authority. For mechanically inspectable Git identities, exact-object validation should be performed by the existing validator/CI rather than trusted from prose alone.

## 14. Stop law

Stop a work unit when the decision is resolved, the required gate is proven/falsified, or a bounded blocker is established **after the decision-changing solution search of §5.1** (unless a hard authority, safety or resource boundary prevents that search). A blocked implementation does not by itself falsify its mechanism. Stop when further evidence cannot change the conclusion, or the affected route is correctly PARKed with an exact reopen condition.

Do not continue merely to make the report larger.

## Final operating rule

`CLOSE THE NEXT REAL GATE. REUSE BEFORE BUILD. PUBLISH BEFORE HANDOFF. TEST THE EXACT SUBJECT. PRESERVE THE NEXT ACTION. STOP WHEN THE DECISION CANNOT CHANGE.`
