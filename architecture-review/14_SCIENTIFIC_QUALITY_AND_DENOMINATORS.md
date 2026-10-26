# Scientific quality and denominator challenge

Review date: 2026-10-26. This is an architecture review, not a new research look. No market outcomes were acquired and no product state was changed.

## Verdict

Quant already has meaningful contracts for semantic identity, variant accounting, negative memory, independent challenge and outcome separation. These contracts are split across rails, and their classifications should not be mistaken for independently established economic novelty. The missing measurement is an identity-preserving join from **all attempted roots and variants to their actual downstream dispositions**, including blocked and unexecuted work. A new idea ledger or a new validator is unnecessary.

There is insufficient evidence for hypothesis I: that validation systematically rejects useful edges. The present 15-hypothesis campaign mostly stopped before admissible economic measurement. Its parks cannot estimate a false-rejection rate. Conversely, at least one W2 confirmation-counting contract is demonstrably weaker than an existing qualified source repair. Increasing throughput by loosening this boundary would reduce scientific reliability.

## Evidence boundary and primary checks

Primary objects inspected:

- W2 `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`: `research/research_os/research_intelligence.py`, `scientific_memory.py`, `scientific_memory_feedback.py`, `expansion/v2_core.py`, `v2_pipeline.py`, `v2_stage_executor.py`, `v2_state.py`, `expansion/scientific_adjudication.py`, `_scientific_adjudication_c0.py`, and `tests/test_wave2_c2_scientific_adjudication.py`.
- F `79329f15bbf02c25fa61e5d5ef6028e5abfb1493`: `research/research_os/idea_feed/contracts.py:novelty`, `registry.py:metrics`, and exposure/state contracts.
- V3 `0691a4c1c905c8cfa1e68d521b12d66655ec4dd3`: `research/research_os/ideation_intake.py:_proposal_relation`, `_classify_novelty`, `_novelty_rejections`.
- Latest C0 `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf`: `research/research_os/expansion/scientific_adjudication.py:bind_independence_ref` and `validate_independence_ref`.
- Forward `ded4228de74ce3b6926d9ea3e3c2114ff1be8208`: `research/research_os/expansion/v2_core.py` and `v2_pipeline.py`.
- Runtime `16eafd0b3c8d9e0c633ef01dd191cbd32ae50b42`: task/hypothesis trees and LETF assessment. The source snapshot count was independently recomputed: **72 tasks = 34 COMPLETE + 38 BLOCKED; 15 hypothesis files; 14 COMPLETE VALIDATE tasks**. These are scoped object counts, not 15 independent discoveries or 14 edge confirmations.

The frozen audit's denominator and contradiction reports were used as pointers, not substituted for these code checks. Snapshot file paths resolve under `audit/owner-recovery/20261026/pass-01/snapshots/`; full source SHAs above identify the corresponding original Git objects.

## What current classifications can and cannot establish

| Distinction | Existing capability | Adequacy and limitation | Minimum action |
|---|---|---|---|
| New name vs new idea | RI `semantic_identity`/`mechanism_key`; V3 normalized critical identity and proposal fingerprint | Rejects exact and lexical variants when structured fields match. Semantic fields remain supplied assertions; different wording can evade exact structural equality. | Preserve a reviewed relation to prior roots; treat machine novelty as provisional, not scientific proof. |
| Parameter variant vs economic novelty | F `novelty` gives PARAMETRIC_VARIANT; V3 gives PARAMETER_VARIANT and near-duplicate rejection | Real separation exists. Variant exposure must survive rejection and cohort changes. | Reuse F root/variant ancestry and native trial attempts; do not drop rejected variants from denominator. |
| Cross-asset transfer vs new mechanism | F separates STRUCTURAL_TRANSFER from ECONOMICALLY_DISTINCT; V3 separates UNIVERSE_VARIANT, MECHANISM_VARIANT and HORIZON_VARIANT | Useful bookkeeping; transfer is not independent discovery or empirical confirmation. | Record transfer as a child of the mechanism root with a separately frozen test and cumulative exposure. |
| Source novelty vs hypothesis novelty | F source/version, origin family and discovery method are separate from mechanism; V3 source-binding docstring explicitly denies proving semantic novelty | A new source packet can support an old question. Multiple sources may reproduce the same issuer fact. | Keep source identity separate from root identity; do not count a source swap as a new mechanism. |
| Mechanism plausibility vs empirical anomaly | Documentary assessments preserve claim ceilings; C0 authority/outcome membranes distinguish pre-economic readiness | LETF explicitly passes daily-reset mechanism while parking executable flow claims. Mechanism plausibility is not positive expected return. | Retain mechanism screen results; require frozen measurement for empirical/economic claims. |
| Replication vs discovery | F origin family REPLICATION plus PAPER_SEEN exposure | Existing schema can preserve this distinction; no production yield comparison is established. | Treat replication as valuable evidence with inherited prior exposure; do not relabel its known direction as a fresh blind discovery. |
| Data availability vs edge quality | Scientific Memory distinguishes BLOCKED, UNEXECUTED, INVALIDATED_PROTOCOL and NEGATIVE | Correct scientific separation exists; historical formats and incomplete imports limit coverage. | Link data/source parks to canonical memory with explicit reopen conditions, not economic KILL. |
| Scientific vs economic rejection | Qualified negative references, claim ceilings and separate readiness/economic states | Current documentary BLOCK/PARK does not measure net profitability; KILL must remain scoped to admissible evidence. | Preserve separate result axes: source validity, scientific claim, implementability, costs/capacity and authority. |
| Duplicate exposure vs independent confirmation | RI evidence identity; F exposure journal; C0 independence reference | Components exist, but W2 counts structural reconstruction as one independent confirmation even with semantic review explicitly unproven. | Port/reconcile the latest C0 counting repair and qualify it on the selected target. |

F's `novelty()` uses normalized field equality. A changed known actor/mechanism/constraint/transfer/rule field can yield ECONOMICALLY_DISTINCT. V3 `_classify_novelty()` returns GENUINELY_NOVEL when no prior proposal or qualified memory relation matches. Neither implementation can prove an economic mechanism is new to the project, let alone to the market. This is **classification uncertainty**, not evidence the modules should be replaced. Retain the taxonomy, attach reviewed evidence and coverage limits, and keep UNKNOWN available.

## A concrete confirmation-counting mismatch

A bounded, read-only Python probe loaded the W2 test fixture `independence_record()` from `tests/test_wave2_c2_scientific_adjudication.py`. It bound the same fixture through W2 and latest C0, using each version's own Factory binding. No actual candidate or outcomes were introduced. `PYTHONDONTWRITEBYTECODE=1` prevented product cache writes.

| Field | W2 public adapter → preserved kernel | Latest C0 |
|---|---|---|
| `structural_independence_proven` | true | true |
| `semantic_diverse_review` | NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED | same |
| `status` | PASS | PASS |
| `independent_confirmation_count` | **1** | **0** |
| `semantic_independent_confirmation_proven` | absent | false |

The W2 public adapter delegates `bind_independence_ref` and `validate_independence_ref` to the preserved kernel. Latest C0 requires `PROVEN_INDEPENDENT_SEMANTIC_REVIEW` before incrementing confirmation count. This verifies the audit's **specific missing counting repair**. It does not prove a production result was falsely promoted: no current real research object through this formal C0 path was demonstrated. Latest C0 also does not by itself establish actual cognitive independence; it binds an asserted proof state that must have an admissible independent-review origin.

The legitimate target behavior keeps structural PASS while recording semantic confirmation count zero until semantic review is established. A deterministic structural reconstruction remains useful, with its narrower claim.

## Late forward controls: challenge the blanket absence interpretation

The audit is correct that W2's composed `v2_pipeline.py:run_pre_outcome_pipeline` lacks the late forward calls:

1. `assert_trial_proposal_binding(candidate, trial)` binds subject, generation, generated-proposal hash and documentary packet;
2. `assert_trial_epoch_window(epoch, trial)` checks **trial.generated_at**, not just current execution time;
3. `assert_model_allowed` checks both recorded producer and validator model identities at the composed boundary.

However, **W2 is not wholly devoid of these protections**:

- `v2_stage_executor.py:_assert_native_trial_lineage` already verifies native generated-proposal subject/hash and source-packet binding.
- `V2StageExecutor.execute` already rejects current execution outside the active research window, and checks export cutoff and budget.
- `v2_state.py:_preflight` already calls `assert_model_allowed(epoch, self.model_identity)` and verifies epoch policy hashes.
- `v2_core.py:assert_model_allowed` already exists.

These are not complete substitutes for the missing composed checks: native-route enforcement does not secure every caller of the generic composed function; `now` inside a window does not prove `generated_at` was inside it; store model admission does not automatically establish a recorded validator model's admission. Therefore the minimal delta is a **boundary-by-boundary control equivalence review and selected port**, not replacing expanded W2 files with the older forward rail. Absence of a named helper alone is not an exploit demonstration. This review did not execute an attack against a deployed runtime.

## Denominator capability: partial, reusable, not solved

| Required quantity | Current evidence | Missing join / limit |
|---|---|---|
| Attempted ideas | Native V2 generation trials include generated/discarded proposals and retries; F enrolls attempted roots even when novelty is unresolved | Pre-V2, private and off-rail attempts incomplete; root equivalence across rails unresolved |
| Admitted ideas | V3 accepted/rejected proposal ledger and replay identity | Not observed deployed or attached to historical campaign roots |
| Tested ideas | Protocols, experiment registrations, trial charges and result artifacts exist in research rails | No complete root→variant→economic-look join; infrastructure attempts must remain separate |
| Positive results | Documentary assessments, formal scientific contracts and historical expression results | Different claim levels cannot share an unqualified POSITIVE metric |
| Parks | Durable tasks, assessments and F states | Not all off-rail terminal dispositions imported to operational memory |
| Kills | Qualified negative contracts and historical expression results | Global admissible-test denominator and scope incomplete |
| Duplicates | Runtime exact-duplicate blocks; V3 relations; F seed/root/variant accounting | One duplicate event may be represented in several stores; aggregate by event/root identity |
| Blocked-data outcomes | Runtime source blocks, Form144/DueBill parks, F BLOCKED_DATA | Counts need block reason, attempt type and admissible source state; do not count as failed economic trials |

F `registry.py:metrics` concretely initializes `VARIANTS_TESTED` and `EXPERIMENTS` to zero without computing either from downstream evidence. OOS/prospective/economic passes, research cost and time-to-discovery remain UNKNOWN. Its deterministic demo is therefore **not a completed end-to-end research-process denominator**. V3 counts admission evidence, not every historical research root or trial. The historical audit's 146 rows cannot be summed because they mix versions, programs, seeds, roots and imported expressions.

## Minimum denominator contract

Use existing authoritative stores; add joins and derived projections, not a second independent ledger of research truth.

1. **Identity mapping:** preserve rail-scoped historical ID, canonical root-question ID, hypothesis/generation, seed/proposal IDs, experiment/protocol hash, trial/attempt ID, source/version and cohort/policy version. Record unresolved equivalence rather than silently merging roots.
2. **Attempt semantics:** distinguish proposal generation/retrieval exposure, admission, source acquisition, infrastructure retry, economic look and independent confirmation. Persist rejected drafts and variants; a retry cannot erase an earlier exposure or create a fresh root.
3. **Disposition semantics:** separate documentary/scientific claim, source admissibility, data availability, authority, implementability, economic after-cost result, portfolio readiness and capital state. Include valid park, block and explicit UNKNOWN.
4. **Causal transitions:** every downstream receipt names predecessor IDs/hashes, producer/evaluator identity, frozen protocol and active authority scope. Idempotent import and append-only corrections preserve earlier records.
5. **Denominator projection:** compute attempted/admitted/tested/positive/park/kill/duplicate/blocked counts by source, method, mechanism family and policy cohort. Report both unique roots and cumulative variants/looks. Separate retrospective known exposure from fresh OOS evidence. Empty or incomplete denominators remain UNKNOWN, not zero yield.
6. **Policy learning:** rank source productivity by decision-relevant evidence and cost only once attribution is sufficient. Report data censoring and blocked opportunity separately from scientific failure; preserve allocation policy before acquiring evaluation outcomes. Feed only explicitly released aggregates to RI/renewal policy.

This extends F exposure/root journaling, V3 admission receipts, native V2 trial provenance and Scientific Memory dispositions. It does not require a new research subsystem. Qualification should include a duplicate imported twice, a parameter variant rejected at admission, an infrastructure retry before outcomes, one valid data park, a scoped negative, and one known-exposure replication. Each must project once under the correct denominator while preserving all exposures.

## Hypothesis I: are standards excessively restrictive?

**Supporting evidence:** conservative UNKNOWN handling can hold work indefinitely; broad semantic-family negative suppression can become overbroad if a narrower prior result is imported without its scope; sparse memory can force review; exact-source and pre-close input requirements reduce accessible experiments. These are plausible false-negative mechanisms requiring measurement.

**Contradicting evidence:** inspected LETF requirements address real post-close leakage and gross-to-net flow mapping; a plausible daily-reset rule does not establish actionable net flow. UST, Form144 and Apple stops include authority, source acquisition and continuation issues, rather than observed economic failures under excessively high thresholds. W2's confirmation mismatch points toward a missing stricter counting control. Scientific Memory already preserves blocked/unexecuted versus negative states. No admissibly validated economically useful object systematically rejected by current standards was demonstrated.

**Confidence:** low support for systematic overrestriction; high confidence that the present campaign cannot estimate it. **Owner impact:** do not relax PIT, freeze, outcome, multiplicity or independence controls to create apparent throughput. Audit a sample of terminal decisions under the same evidence boundary, checking scope transfer and whether cheaper admissible tests were available. Any new evidence acquisition requires its existing authority gate. Record false-rejection findings only with a defensible counterfactual evidence standard, not with hindsight profitability.

**Falsifier:** a reproducible class of independently admissible, after-cost economic results is stopped solely by a rule unrelated to claim validity, data rights, scientific design or authority, and a preregistered scoped policy change improves held-out decision quality without increasing false accepts. Until then this hypothesis remains a research-policy question, not proof a new architecture is required.
