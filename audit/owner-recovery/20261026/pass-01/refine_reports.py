from catalog import *
from collections import Counter
refs=loadrefs();C=refs['builder/convergence-wave2-canonical-20261021'];R=refs['builder/oracle-v2-core-20261020'];F=refs['builder/giga-f-idea-federation-autonomous-feed-20261023'];Q=refs['builder/giga-q-final-whole-system-hardening-20261023'];V3=refs['builder/multi-source-ideation-intake-v3-20261026'];V=refs['codex/vertical-depth-prewave2-20261021'];H=refs['codex/horizontal-completeness-convergence1-20261021'];HP=refs['codex/horizontal-completeness-prewave2-20261021'];VF=refs['builder/v2-forward-20261020'];BASE='2b99d8aeb8a342f1ef32544247d366cb8a26037e';DEFAULT=refs['blue/master-v2-2026-09-20']
REFHASH=hashlib.sha256((ROOT/'evidence/remote_refs_start.tsv').read_bytes()).hexdigest()
def md(n,s):(ROOT/'reports'/n).write_text(s.strip()+'\n')
def rd(n):return list(csv.DictReader((ROOT/'reports'/n).open()))

# Keep the short French brief and canonical snapshot; make the technical dossiers readable English.
p=ROOT/'reports/01_OWNER_BRIEF.md';s=p.read_text().replace('261 branches inventoriées;37 examinées','261 branches inventoriées ; 38 examinées').replace('1 partiellement','1 partiellement').replace('du26 octobre2026 à00:52:12UTC','du 26 octobre 2026 à 00:52:12 UTC').replace('H/V à rejouer sur la cible finale.','H/V à rejouer sur la cible finale ; contrôles V2 tardifs CP080–099 qualifiés séparément.').replace('E05/E06/E14/E15/E19.','E05/E06/E14/E15/E19/E25.').replace('dette de convergence C0/V3/F,','dette de convergence C0/V3/F et V2 tardif,');p.write_text(s)
p=ROOT/'reports/02_CANONICAL_STATE_SNAPSHOT.md';s=p.read_text().replace('| Source feeds |','| V2 forward CP099 | `'+VF+'` | CI exacte Oracle V2 Core PASS ; contrôles tardifs du chemin composé absents de W2. |\n| Source feeds |');p.write_text(s)

md('03_MASTER_TIMELINE.md',f'''
# Functional campaign timeline

This timeline describes recovered changes, with their limits. It is not an assertion that every historical qualification has been audited. Evidence IDs refer to [EVIDENCE_INDEX](EVIDENCE_INDEX.md). Git identity and content take precedence over campaign titles and nominal dates.

| Phase and fixed evidence | Before / problem | Decision and actual build | Result, qualification and integration | What remained / later change |
|---|---|---|---|---|
| Early Quant / V1, September; North Star50fd342c; Factory ca8ffe43 | Research scripts needed persistent execution and controlled outcome access. | Control clock, Data Plane, durable queue, Factory, Desk, Book and Learning code exist. b30d28c6/ca8ffe43 change the outcome firewall and proof gate. | FACT_PROVEN source. Later W2 CI reproduces the35-assertion V1 demo. Original exact-head qualification of each early change remains pending. | The replay is not a current broker account or the current Oracle queue. |
| P0 capture,18–21 September; capture348c4e42, hybrid d4d446c4 | Capture continuity, hidden retries, request accounting and coverage had to remain separate from scientific access. | Capture/provenance journals, request permits, coverage reconciliation, deployed-unit fingerprints and probes exist. | FACT_PROVEN code and durable reports. The reports describe real capture; all historical host artifacts are not independently requalified in this pass. | Raw capture later failed to become an available scientific census in some research workflows. |
| Gate A V2/V3/V4,20–21 September | Continuity and clocks required adversarial qualification. | Separate Builder, Blue and Astra rails; V3 tip2da079d8, V4 tip4d06bdbf; provenance and effective-unit repairs. | Campaign branches and changes are proven. Exhaustive final-disposition reconstruction is pending. | A GateA PASS must retain its version, target and test scope. |
| Gate B,21 September | Execution authority, locks, evidence schemas and deployed file identity. | Mechanisms845dfa36; repair2d2ff4e3; F11 lock8a30bd38; evidence schema12a666fd; multiple Blue integrations. | Source and artifacts exist; one final activation authority chain is not yet reconstructed. | Prestages and missions do not establish live-capital authority. |
| Research labs24/25 September;337c4b7c | Exploratory investigation of mechanisms and candidate expressions. | Reports, scripts and outputs cover futures trend/carry, cross-venue funding, equity calendars, prediction markets and sports. | Positive retrospective outputs are actually present, including xvenue.out and equity results.txt. They are not prospective or portfolio proof. | Four positive lab lineages remain untraced to final disposition. Private search denominator is unknown. |
| Fast Rail, September;5255ba2a→fa2aaef9 | Turn hypotheses into bounded historical or forward tests. | Versioned registries, rejected funding/weather/listing expressions, imports,14 unified H-IDs and timestamp corrections. | STOP_OWNER and unification are recorded at5255ba2a. E21. | H006 means different things on different rails. Later data capture does not establish successful forward validation. |
| Weather V2/V3/V4, September–8 October | Design failures, historical PIT limitations and overfit risk. | V2 review, V3 investigations, V4 Gold Map,33 design seeds, A2 harness and Owner/Builder/Astra lots exist. | The33-seed ledger explicitly says REPAIR_SEED_NOT_PRE_REGISTRATION. E24. | Exhaustive A2 authority/host/lot reconciliation is pending. The legacy reconciler cannot replace primary artifacts. |
| F1 / F2 / EURUSD,8–10 October | Access, permissions, trial budgets and executable expressions. | F1 sealed captures and dispositions; F2 terms decision; EURUSD frozen grid and adapters. | Artifacts exist. The reconciler preserves closed, permission-blocked and unexecuted states separately. | Original run-by-run source and authority qualifications remain in the gap register. |
| Edge Lab,11–15 October;68bbab8e | Learn cheaply before expensive infrastructure. | Persistent family, protocol, admission, look, job, exposure and result records. | Across all advertised heads,15 result paths are recovered: one promoted VX expression, two killed expressions and12 parks. SMARD uses a different result format. E16. | VX L2 is PARK_DATA; prospective register has zero observations. Historical results are not residual alpha. |
| Research OS and first loop,15–18 October;d0dc70f5 | Connect producers, freeze and independent challenge. | Four research families, frontier tasks, frozen hypotheses and validation tasks. | Fifteen current frozen hypotheses exist. Leases show interactive, manual, workflow and Oracle origins. E08. | Do not call all15 autonomous discoveries or all14 validations economic passes. |
| Economic readiness,16–19 October;e980d201 / Form1449faba4fe / USTac3b32ff | A mechanism pass did not define an executable experiment. | Readiness, identity, portfolio and experiment contracts; controlled activation; Form144 protocol/admission/run; UST validation/freeze. | Form144 reaches real source acquisition and fails SEC403 before outcomes. UST stops at the recovered post-freeze checkpoint. E11–E13. | UST execution and validation receipt not found; authority representations conflict. |
| Legacy / Scientific Memory,15–21 October;183ad65f /9d92c9f | Preserve failed and incomplete research without false novelty. |20-record imported legacy ledger, source recovery, W1 Scientific Memory and feedback. | Code and import are proven. The runtime also reports33 historical research items and PARTIAL_WITH_EXPLICIT_GAPS. E17. | The global root/variant/trial denominator remains unreconciled. |
| Oracle V1→V2,19–20 October;0837f419→16eafd0b | Need durable scheduling, leases, recovery and native Git publication. | Systemd policies, native canary, boot proof, Git CAS, epoch/trial sidecars and a restricted local commentary backend. | Dated real wakes and research artifacts exist. Latest recovered wake is26 October, without new research. E09/E23. | Frozen packet reuse, missing quant sources, flow-stage authorization and quotas stop replenishment. |
| Live Lab,12–20 October;6076774f→d14b96c6 | Connect visible activity to canonical worker events. | Frontend/backend, projection contracts, saved browser probes and real SSE/reducer events. | Historical production connection is supported by artifacts. E08/E23. | Current host/browser status is not directly observed. The UI is not a scientific ledger. |
| W1 Data/Evidence/PIT;c0fda9bd | Strengthen source qualification and PIT contracts. | Typed registry, source qualification, acquisition and evidence modules. | Functional ports exist in W2; cumulative tests pass in their declared scope. | A data contract passing does not supply missing data for a real question. |
| W1 Factory/Experiments;dfaf0bd7 | Preserve freeze, trial geometry, power and protocol identity. | Common Factory contracts and experiment infrastructure. | Code is present in the cumulative candidate. | Fixture qualification is not proof that current production hypotheses use the whole path. |
| W1 Economic/Portfolio;83bb4951 | Separate scientific claims from economic and portfolio claims. | Structural portfolio, Economic Identity and readiness. | Functional code/tests are present. | Native/shared Economic Identity binding remains unresolved in Q. |
| MEGA A;29c6faa4 | Prioritize research actions using identity and memory. | Pure pre-outcome Research Intelligence; no scheduler authority. | RI source blob equals W2. Its latest head has only SEC CI in the fetched run list. | Production execution of the newer RI path is not proved. |
| Convergence #1 / CP069-first;ac50b0c3 | Accumulate W1 on a selected checkpoint base. | CP069 rail adapts Factory and qualification; CP079 rail accumulates further work. | Git history proves distinct rails. | CP069-first is superseded as immutable-base choice, not erased as evidence. |
| CP079-first→immutable2b99 | Correct exact-base qualification and lexical overlap handling. | RI f4be6953, overlap-review97165db2, exact-base repair2b99d8ae and preflight46511058. |2b99 is the base of W2 and V3. | It does not include all later work on the forward rail. |
| Forward Builder CP080–099;ded4228d | Portfolio provenance, historical data-block memory, subject attribution, model policy, generation clock and serialization gaps. | Seven repair groups:081/084/087/090/093/096/099, with before-code findings and later scoped qualifications. | Exact-head Oracle V2 Core39660277404 and SEC39660277407 PASS. E25. | W2 lacks the named late composed proposal/model/time checks. Q overlaps the tuple membrane. Other equivalent safeguards require semantic comparison, not bulk file replacement. |
| Wave2 B;bfc9fad9 | Admitted idea must become a common testable Candidate. | Discovery engine, family guards and chain; canonical port42203de5. | Exact source qualification39656474279 PASS; W2 adapts the source. | Q still lacks production Proposal→Discovery lineage proof. |
| Wave2 C0;6dc84f35 | Bounded scientific adjudication over frozen Factory references. | Adjudication kernel; late semantic-independence repair66bdd160; broader canonical adapter. | Exact C0 qualification39662900753 PASS. W2 preserves an earlier kernel. | Latest semantic confirmation counting is unported. E19. |
| Wave2 D0;4262462e | Pre-outcome economic lifecycle without invented economic success. | Lifecycle kernel, campaign adapter and C0→W1 Economic→D0 thin binding. | D0 exact qualification39623992108 PASS; kernel bytes preserved; W2 seam tests pass. | A shadow/lifecycle contract is not a prospective result or capital permission. |
| Wave2 E;82da9758 | Durable work, outbox, retry and recovery. | Worker/runtime changes, port8d7383be. | Source exact qualification39637373986 PASS. W2's separate E workflow fails on missing pytest; cumulative CI passes. | Runtime deployment of W2 is not proved. |
| MultiSource V1/V2→V3;bbdea6a7→0691a4c1 | Bound and preserve admission, identity, duplication and retries. | Passive policy/intake V2 merged0722dc4d; V3 adds a durable hostile admission contract on2b99. | Exact V3 qualification40249296902 PASS. W2 retains V2. | V3 neither creates Candidates nor autonomously supplies sources; it remains separate. |
| Wave2 Convergence #2;ebc72b9f | Combine the reviewed B/D0/C0/E/MS ports. | Port commits, thin bindings, qualified parentf4534b8e and final manifest. | Exact cumulative39882531103 PASS; integrated SHA is explicitly not emitted. | Formal promoted trunk unknown; C0 late, forward V2 controls, F and V3 require reconciliation. |
| Horizontal H,21–22 October | Map breadth and test inter-module seams. | Pre-W2 coverage and Convergence1 probes, queue/schema repairs and L001. | Bounded local qualification; no hosted exact-tip CI found in the fetched lists. E15. | No final-W2 phaseB proof. |
| Vertical V,21–24 October | Adversarial depth, repair and honest checkpoint claims. |46 repair groups, CP039 no-defect process-death proof, out-of-sequence061, corrected rejected labels. | Qualified sourcee98a; source/evidence hashes match; Owner stopped at046. E14. | PhaseA incomplete; Q replays older92c4 corpus, not the entire latest V scope. |
| Longitudinal L findings | Preserve truth across scientific and economic owners. | H L001 and V LONGITUDINAL_001; Q04/Q10 address parts. | Findings, probes and bounded repairs exist. | No separate complete L rail found; replay after convergence remains necessary. |
| Post-Wave2 F/Q,24 October despite dated branch names | Research replenishment versus whole-system integrity. | F three commits and exact PASS; Q13 repair groups and exact FAIL. | Both are actual builds, not only prompts. E06/E07. | F remains disabled; Q remains NOT_QUALIFIED; neither replaces W2. |

The P0/Gates/Weather/lab families remain partially reconstructed. Their remaining branches and CP records are individually enumerated in the gap CSVs. A timeline row does not silently qualify the entire campaign.
''')

md('14_END_TO_END_LINEAGE.md',f'''
# Artifact-backed end-to-end lineage

Scope: the15 frozen hypotheses in Oracle state`{R}`, recovered descendants on separate branches, and the historical VX expression. Current V3 did not exist when these roots were created; its absence from an old chain is not itself a defect. [Idea ledger](10_IDEA_MASTER_LEDGER.csv), [positive lineage register](11_POSITIVE_IDEA_LINEAGE.csv), evidenceE08/E11–E13/E16/E23.

## Every current frozen hypothesis

| Hypothesis, abbreviated | Proven root task | Last recovered actual descendant | Current disposition |
|---|---|---|---|
|ASML service |PROD-FUNDAMENTAL-001 |Validation, cross-examination, red-team and final assessment |Business mechanism only; claim/authority blocked |
|ASML pricing |FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-001 |VALIDATE assessment |Bounded pass with claim block; overlap with service remains a review issue |
|TSMC N2 |FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-002 |VALIDATE stages and receipt |Bounded learning mechanism; stronger claim blocked |
|Apple DOC-FUND |FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003 |Five-stage validation, g5 receipt and terminal handoff artifact |PARK_BLOCKED_NO_INTEGRATION_AUTHORITY |
|DueBill |PROD-EVENTDOC-001 |Source-readiness assessment onb9f6ee8a |VALIDLY_PARKED; paired historical prices missing |
|Stapled CVR/PRV |FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-001 |VALIDATE assessment |Population/data block |
|Schedule13D |FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-002 |VALIDATE assessment |Documentary pass with BLOCK_CLAIM_LEVEL |
|FDA Adcom |FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-003 |VALIDATE assessment |PARK_DATA; historical publication clocks/classification |
|Apple DOC-EVENT |FRONTIER-EVENT-DOCUMENT-DISTINCT-MECHANISM-004 |Five-stage validation, g5 receipt and terminal handoff artifact |PARK_BLOCKED_NO_INTEGRATION_AUTHORITY |
|ADR termination |PROD-FLOWS-001 |VALIDATE EXPLORE assessment |Frozen design not found; documentary-only authority |
|Russell |FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-001 |VALIDATE assessment |PIT weights/flow sizing block |
|UST primary dealer |FRONTIER-INSTITUTIONAL-FLOW-DISTINCT-MECHANISM-002 |Frozen screen protocol and post-freeze CP2 |Expected execution/result not found; suspected positive orphan |
|Form144 supply |PROD-QUANT-001 |Protocol, admission, execution attempt and result on9faba4fe |SEC403 before outcomes; VALIDLY_BLOCKED |
|Closing auction |FRONTIER-QUANT-MECHANISM-DISTINCT-SIGNAL-001 |Frozen hypothesis; separate source-readiness rail found |No authorized validation handoff; off-rail source assessment still partly unaudited |
|LETF reset |FRONTIER-QUANT-MECHANISM-DISTINCT-002 |VALIDATE assessment |Pre-close fund state and hedge mapping missing |

Full IDs, exact paths and pinned SHAs are in CSV10. FACT_PROVEN means the objects exist; it does not validate the economic claim. The two ASML roots are not treated as independent evidence merely because they have different IDs.

## Automatic documentary continuation: Apple

```
registered apple_fy2025_statement_cells.json packet
→ FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003
→ documentary research artifact → disconfirmation
→ freeze DOC-FUND-9219d7f488ada3c2:G1
→ actual validation_handoff.json and actual VALIDATE task
→ independent_validation → cross_examination → red_team
→ claim_restriction → integration_handoff.json(handoff_created=false)
→ g5 completion receipt and COMPLETE task
→ PARK_BLOCKED_NO_INTEGRATION_AUTHORITY
```

FACT_PROVEN, E23: hypothesis/G1, frozen hash and source provenance are transmitted through these durable artifacts. The source clock is explicitly a first verified capture, not a historical publication PIT guarantee. The freeze is20 October00:51:29Z and validation completion01:50:08Z. The DOC-EVENT sibling freezes03:40:27Z and completes validation04:40:29Z. Both stop with12 named readiness blockers. Their producer EXPLORE decisions did continue through real challenge; no economic pass follows.

NOT_FOUND in these lineages: current V3 admission, completed economic experiment, formal new C0 verdict, D0 economic state, capital handoff and Learning re-entry. Further frontier tasks repeatedly regenerate these packets and are blocked as duplicates; they do not create new frozen hypotheses.

## Institutional-flow continuation: UST

```
documentary dealer/auction mechanism, as recorded in hypothesis
→ frontier institutional-flow task002
→ FLOW-UST-PRIMARY-DEALER-AUCTION-001:G1
→ initial producer stop: no handoff authority
→ separate campaign selection1c4ba096
→ validationea9299e9 / assessment1eebd6ac
→ protocol freeze7b843ddd
→ CP2ac3b32ff declares authorized outcome acquisition
→ [expected execution task/run/result NOT_FOUND]
```

The protocol preserves the hypothesis ID, generation and hypothesis blob. It freezes the nominal10-year auction population,2010–2025 sample,5/10/30-year butterfly, endpoint, decision rule and multiplicity. It is a mechanism screen, not a tradable P&L test with an executable cost model. E11.

The assessment's `integration_handoff_created=true` has a real descendant: the frozen protocol. It does **not** prove the next execution. The validation task is COMPLETE but its dedicated receipt directory is absent at the anchored runtime tree. STRONG_INFERENCE: an expected positive continuation is orphaned after the post-freeze declaration. UNKNOWN: private/uncommitted execution, or an unrecorded valid park. Global authority false and protocol-specific text authority remain unresolved, CT06/CT07.

## Quantitative mechanism: Form144

```
PROD-QUANT-001 → QUANT-FORM144-SUPPLY-001:G1
→ VALIDATE documentary EXPLORE
→ separate experiment mission
→ protocolb80cd821 → runnerf2a71f22 → admissionc479ff25
→ run39032409229: admission checksum failure
→ pre-execution integrity repair4ed7e393
→ run39032686104 / job117396188885
→ SEC master-index HTTP403 after3 attempts, before event sample/outcomes
→ durable9faba4fe result SOURCE_UNUSABLE / PARK_DATA
```

E12: exact workflow logs independently support the source failure. Protocol/generation/run identities are in the committed result. Automatic result upload is skipped after the exception; the later commit preserves the disposition. The result declares0 economic attempts and2 infrastructure attempts. This is a valid data/access block, not economic falsification. The separate campaign does not prove Oracle's scheduler generally creates and launches experiments after a positive validation.

## Event/document mechanism: DueBill

The real chain is producer→frozen hypothesis→independent EXPLORE→separateb9f6ee8a source assessment→PARK_DATA. The parity expression needs reproducible history for both entitlement-bearing and stripped/when-issued claims. The assessment finds no adequate THRM/THRMV history. E13. The legal mechanism survives; replacing it with an ordinary directional stock test would change the question. VALIDLY_PARKED, with the later disposition missing from the current runtime task tree.

## Furthest recovered historical economic result: VX

E16: v0 incomplete source→v1 reader QA failure→v2 reader repair→fixed36-trade settlement expression/9 calendar-year clusters→predeclared remove-largest-positive-year challenge→PROMOTE_EXPRESSION. `edge_validated=false`; settlement marks are not executable fills. A real L2 access qualification concludes PARK_DATA. A subsequent prospective register starts15 October with0 observations. The stored state gives6 November as a necessary earliest-exit lower bound, not an identified eligible contract. At the audit anchor this prospective exit cannot yet have occurred.

VALIDLY_PARKED. This is stronger lineage than a lone positive summary, but does not establish residual alpha, capacity, portfolio usefulness or capital authority.

## Transition proof matrix

| Transition | Object | Identity / provenance | Actual next task | Executed | Durable result |
|---|---|---|---|---|---|
|Source packet→frontier research |Yes for Apple witnesses |Packet hash, source path and capture clock |Yes |Yes |Documentary premise |
|Hypothesis→independent challenge |14 tasks for15 roots |IDs/G1/frozen references; UST receipt exception |Yes14 |COMPLETE14, with different scopes |Assessments, claim restrictions and parks |
|Positive→test design |UST/Form144 yes; DueBill source gate |Preserved for these objects |General queue task not established |Separate campaigns |Protocol or source qualification |
|Protocol→experiment |Form144 source attempt yes; UST missing |Form144 IDs/commits bind in CI |Actual Actions run |Source acquisition only |No economic outcome |
|Current production→formal C0 verdict |Not found |Unknown |Not found |Not found |Not found |
|C0→Economic Identity→D0 |Contracts and fixture seam exist |CI fixture binding passes |Production task not found |Not proved in real current roots |Pre-outcome contracts only |
|D0→Capital→Book→feedback |V1 demo topology exists |Current real-object seam unknown |Not found for these roots |Not found for these roots |No real-capital proof |
|Feedback→Memory→new root |Implementation exists |Global object mapping incomplete |Not found end to end |Unknown |Closed current loop not proved |

An eligible fixture proposal is not entered as a production orphan. Passive admission is allowed to end at its narrow handoff; a downstream obligation must be established before missing execution becomes an orphan finding.
''')

md('15_HVL_HISTORY_AND_CURRENT_VALUE.md',f'''
# H / V / L: actual work, current scope and reusable value

## H before Wave2

Tip`{HP}`; base`01c2e520fa4116645870f96acf6770ea83f1881c`. The manifest binds source`30bd72452273afb3e8177939b969e4d3a540caf7` and evidence snapshot`3adbcd2ef3fe969f7f69b1f463e23ecaca7ee843`. Declared coverage is35 modules,73 families and40 scoped surfaces. Saved local qualification reports809 root,273 Research OS,57 JS and35 demo assertions. These suites overlap and are not independent experiments. No hosted exact-tip CI was found in the fetched run list. E15.

H001 repairs FAILED terminal accounting; H002 blocks refill when state is unknown. Future Wave2 gaps are not automatically current product defects. PhaseB requires an Owner-pinned qualified final Wave2 target; no proof of that phase on ebc was recovered.

## H on Convergence1

Tip`{H}`; base`97165db2faa3300cef1f23de0045ed93d25eb9cb`; declared tested source`d88107fb2d872d203ca6f361df1adbb5fb8d24e4`; evidence snapshot`d90a353e8a699397b491c24386e6b867b24242f2`; lastCP004. Coverage is43 modules,95 family entries and59 scoped surfaces. Local suites report799 root,433 Research OS,94 RI bridge and57 JS.

H001/H002 address queue semantics. H003 addresses the Implementability auxiliary schema. H004 addresses frozen-object/null behavior in ExperimentEnvelope. T001 records3 fixture alignments. U002 leaves the native/shared Economic Identity wire owner unresolved. L001 contains an actual probe showing loss of frozen instrument/universe/clock and a changed horizon at economic readiness. This is more than a coverage declaration. E15.

## V: the current corrected truth

Tip`{V}`; qualified executable source`e98a1b22f98935302c26a749fdb84638ffbeac41`. The executable-tree diff from that source to the tip is empty. All83 source fingerprints and334 evidence hashes in the qualification match the actual files. [Hash verification](../evidence/qualification_hash_verification.json). This is an integrity check on saved proof, not a new product test or target requalification. E14.

FACT_PROVEN current disposition: sequential substantive work stops atCP046; CP061 was rebuilt out of sequence.47 substantive entries=CP001–046 plus061.46 groups are repair-bearing; CP039 supplies a real process-death proof without a new defect.53 labels, CP047–060 and062–100, remain rejected as insufficient depth. Earlier claims that replay labels represented completed depth are explicitly retracted. Some initially rejected checkpoints were later rebuilt; the old62-replay count is not the current rejected-label count.

The118 enumerated repair items are **not118 independent root causes**.45 scoped capability units cover30 modules,32 source files and1 schema. D2=25/D3=13/D4=7 refer to these units.1134 new cases are reported in the hash-bound proof; final local suites report1942 root,268 Research OS and57 JS. This pass verified proof bytes, not the scientific independence or semantics of every test case.

| CP scope | Functional work or bounded proof |
|---|---|
|001–010 |Book; core hashing/firewall; evidence; Learning; JSON journal; Risk NaN; queue/campaign; fills; PIT corporate actions; decay under optimized Python |
|011–020 |Exact-head qualification; Desk journal; operation fingerprints; Learning concurrency; queue; journal isolation; scientific ledger; artifact registry; legacy; Red Team |
|021–030 |Price panel; acquisition; typed PIT; source qualification; implementability; negative knowledge; portfolio; Edge; forward registry; Git paths |
|031–037 |Freeze; source-input isolation; adapter registry; documentary execution; immutable pipeline; whole outcome record; nested plan |
|038 |Rebuilt frozen replay proof |
|039 |Actual process-death/crash proof; no new defect |
|040–043 |Export input; core input; campaign fencing; PIT lineage |
|044–046 |Pause settlement; watchdog clock; typed queue-document fencing |
|061 |Observability input snapshot; out of sequence |
|047–060 /062–100 |REJECTED_AS_INSUFFICIENT for new depth claims |

The current artifacts state `mission_active=false`, `phase_a_complete=false`, `cp100_depth_completion=false`, stop reasonOWNER_REQUEST_20261024, stopped atCP046. NoCP101 is invented. The private conversation behind the stop is unknown beyond its durable representation.

## L: recovered defects, not an assumed completed campaign

Two concrete truth-transmission findings exist. H L001 loses frozen protocol metadata before readiness. V`LONGITUDINAL_001.json` shows REVIEW_LEGACY_OVERLAP surviving in LegacyKnowledgeBase but not stopping canonical_spine, which only stops exact duplicates. V deliberately leaves that cross-stage repair outside its own rail.

Q04 adds a legacy-review stop to a spine path; Q10 preserves some frozen protocol metadata into Economic Identity. Q's own unresolved native/shared identity seam and full lineage limitations remain. Exact Q ordinary suites pass; the mandatory historical replay fails. E07.

No separately named complete L rail was found among the advertised branches. That is NOT_FOUND in this corpus, not proof that no private/unpushed work exists. Q pins old V source`92c4ee0a5e2d9387167f6deec24e7edec1c15b6d`; latest V attacks, especially044–046, cannot be assumed covered by that replay.

## Current value and supersession

H contributes coverage and seam probes. V contributes scoped repairs and an attack corpus. L findings test whether earlier truth reaches later owners without promotion or loss. They should be replayed against a selected converged target; old source files should not be merged wholesale.

Builder V2-forward CP080–099 is a **different CP family**. Its20 recovered labels include7 repairs and exact source CI39660277404. The proposal/model/time guards missing from W2 overlap neither a blanket claim that V is integrated nor a claim that all late forward work is absent. E25. Keep both rail identity and semantic scope when selecting reusable tests.
''')

md('16_RUNTIME_REALITY.md',f'''
# Runtime reality

FACT_PROVEN: durable Oracle state at`{R}` contains the latest recovered wake at2026-10-26T00:50:15Z. UNKNOWN: the live cloud process or site at the current second; this audit did not directly probe the remote host. A recent committed wake is evidence of recent activity, not an open-ended liveness guarantee. E08/E09.

| Surface | Fixed observation | What it proves |
|---|---|---|
|Research queue |72 tasks;34 COMPLETE,38 BLOCKED;0 READY or CLAIMED |No runnable work at the anchored state; completion is not an economic verdict |
|Frontier |49 historical tasks;48 from4 current families at12 each plus1 older quant-signal task |The configured issuance budgets are exhausted |
|New hypothesis |Latest freeze20 October03:40:27Z |A26 October wake is not a new discovery |
|Task activity |Latest task updated20 October20:50:25Z |No later new task result in this snapshot |
|Latest wake |NOOP_FRONTIER_EXHAUSTED; writes0; hosted_model_calls0 |Recent polling, no new research execution |
|Executable release |a67ffec48fff895d5edc42171855e2213e49cf0d |Does not establish deployment of W2, F, Q or intakeV3 |
|Runtime files |306 event JSONs,176 receipt JSONs,273 artifact JSONs,744 wake JSONs |File counts, not counts of independent business events or trials |
|Separate data-feed rail |25 October23:35:32Z, odds statusOK,68 observations/137 duplicates/1 restatement |Recent data production; not68 ideas |
|Live Lab |Saved20 October real SSE, reducer and duplicate-handling proofs |Historical worker connection; current browser/host status unknown |
|Book / Desk |V1 replay has377 sessions,76 BOOKED and301 NO_TRADE; capital Book has0 fills |Controlled replay, not an audited broker balance |
|Evaluation ledger |Replay NAV993757.74 and counterfactual P&L-6242.26 |Zero-authority counterfactual evaluation, not realized real-capital P&L |

## Exact blocked-task partition

The38 reasons come from task artifacts rather than status labels alone. [Blocker register](13_BLOCKER_REGISTER.csv) and `blocked_tasks_reason_census.json` preserve each object.

| Count | Recorded reason | Useful next condition |
|---:|---|---|
|18 |BLOCK_EXACT_CURRENT_DUPLICATE for the existing Apple premises |A distinct question/source, not a new name for the same packet |
|10 |MISSING_QUALIFIED_DOCUMENTARY_SOURCE_FOR_ENGINE:quant |An admissible registered source packet and testable question |
|9 |STAGE_NOT_EXPLICITLY_AUTHORIZED:mechanism_research |Reconcile the old task action contract with the execution stage, without silently extending authority |
|1 |LEGACY_CONTEXT_REQUIRES_NEW_V2_TRIAL |Explicit enrollment in the correct epoch/context; no rewritten historical verdict |

For the9 flow tasks, the actual allowed-action text fails the worker's authorization pattern. The current frontier template has different text, but it does not retroactively authorize old tasks. That mismatch is a proven fact. Treating it as an OPERATIONAL_GAP rather than an intentional Owner prohibition is a STRONG_INFERENCE requiring later scope reconciliation. No guard is bypassed here.

## Autonomy by stage

| Requested capability | Rating | Evidence and boundary |
|---|---|---|
|AUTONOMOUS_IDEA_GENERATION |PARTIAL |Real Oracle Apple roots; mixed origins elsewhere; no broad continuous novel generation |
|AUTONOMOUS_IDEA_ADMISSION |PARTIAL |Real legacy/current screens; newV3 qualified separately, not observed deployed |
|AUTONOMOUS_DISCOVERY |PARTIAL |Older documentary stages run; newB production Proposal→Candidate chain not established |
|AUTONOMOUS_VALIDATION |PROVEN_WORKING |Scoped to actual documentary challenge with receipts and terminal parks, not economic confirmation |
|AUTONOMOUS_POSITIVE_CONTINUATION |PARTIAL |Hypothesis→challenge works; general challenge→economic design/experiment not established |
|AUTONOMOUS_NEGATIVE_DISPOSITION |PROVEN_WORKING |Duplicate blocks, claim restrictions and durable parking |
|AUTONOMOUS_TEST_DESIGN |UNKNOWN |Separate UST/Form144 campaigns produced designs; generic Oracle creation not proved |
|AUTONOMOUS_EXPERIMENT_CREATION |PARTIAL |Form144 admission/run exists; Oracle-scheduler attribution not established |
|AUTONOMOUS_SCIENTIFIC_ADJUDICATION |PARTIAL |C0 contract tests exist; production current roots through formalC0 not found |
|AUTONOMOUS_ECONOMIC_HANDOFF |NOT_AUTHORIZED |Current global policy is closed; protocol-specific UST grant is unresolved; contracts alone are partial evidence |
|AUTONOMOUS_LEARNING_FEEDBACK |PARTIAL |V1 feedback and Memory code tested; current closed research lineage not proved |

The PROVEN_WORKING ratings have the explicit documentary or negative-disposition scope above. They are not a system-wide autonomy score. F's qualified but disabled feeder and V3's CI success do not change the deployed evidence.
''')

md('17_AUTHORITY_MAP.md',f'''
# Authority and exposure map

## Recovered scopes

| Scope | Economic experiment | Prospective observation | Real capital | Live trading | Outcome exposure |
|---|---|---|---|---|---|
|Current Oracle Control Plane`{R}` |FALSE |FALSE |FALSE |FALSE |Not a complete historical exposure register |
|Latest recovered wake |FALSE |FALSE |FALSE |FALSE |No new outcome acquisition; writes0 |
|W2/F/V3 current qualification contracts |FALSE |FALSE |FALSE |FALSE |Pre-outcome qualification only |
|Q authority gate |FALSE |FALSE |FALSE |FALSE |Gate passes; mission fails a different mandatory gate |
|UST protocol and CP2 |Specific documentary authorization after freeze |Conditional scope inCP1 if required |Not required |Not required |Protocol says NOT_OBSERVED; execution not recovered |
|Form144 isolated admission |One frozen look under its own campaign |No prospective proof |FALSE |FALSE |Source fails before outcomes |
|Historical VX expression |An economic look actually occurred |Prospective register has0 observations |FALSE |FALSE |Historical settlement outcomes inspected |
|Older Treasury5Y expression |Predeclared claim, failed population gate |Not prospective proof |FALSE |FALSE |Proxy outcomes were inspected and quarantined |

E02/E05–E12/E16. The scoped literal scan is saved in `authority_true_occurrences_scoped.json`. A true field named `outcome_access_may_not_be_opened_by_this_authorization` is a prohibition, not a grant; keyword matching alone is insufficient.

## High-priority unresolved UST scope

CONTRADICTORY_EVIDENCE, CT06: the same current trees preserveCP1's recorded conversational grant, CP2's `AUTHORIZED_OUTCOME_ACQUISITION_AND_EXECUTION_OF_FROZEN_SCREEN`, the frozen protocol's post-commit authorization, and global Control Plane economic/prospective flags false. No normalized scope-resolution or revocation object was found.

The audit cannot infer that a later global flag revoked every specific grant, or that a checkpoint text overrides an operational task/global denial. OWNER_DECISION_REQUIRED in a later mission: establish the active scope. The concrete protocol and competing representations are already available for review. No permission question or outcome acquisition is needed to complete this read-only audit.

## Exposure cannot be reset by a new flag

FACT_PROVEN: older studies inspected prices or payoffs. Current pre-outcome authority can close future access while preserving that history. The legacy ledger, older results and11 nativeV2 trial records describe different scopes. `OUTCOME_ACCESSED=false` in a qualification receipt does not prove the model, Owner or an earlier research campaign never saw future results.

UNKNOWN: complete private human/model knowledge, current credentials/rights on the host, actual broker balances, or an unrecorded specific authorization. No inspected current-rail governance artifact proves real-capital or live-trading authority true. This is scoped absence, not a claim about every private conversation.

## Flow-task stage authority

Nine actual tasks persist a stage-authorization refusal. The general frontier objective is not itself authorization for an older task. Recovering a valid continuation requires contract reconciliation without changing earlier scientific state or bypassing the guard. This is recorded separately from a legitimate market-data or scientific-power block.
''')

md('18_SECOND_TRUTH_REGISTER.md',f'''
# Competing truth representations

A copied file, a compatibility adapter or a separate counterfactual ledger is not automatically an unauthorized second truth. This register identifies owners, projections and unresolved boundaries in the pinned corpus.

| Truth | Recovered owner | Representations | Verdict and next check |
|---|---|---|---|
|Canonical project HEAD |Owner/external seal |Default9026, candidateebc, runtime16e/releasea67 |UNKNOWN final promoted identity; CT01 |
|North Star |Owner through the normative document |a328 in W2/F/Q/V3; older8295 in default/runtime |Version split proven; current operational routing not reconciled |
|Task state |Canonical Git task blob and lease generation |Task JSON, receipt, event, SSE/UI projection |Owner clear; global correlations not fully audited; UST receipt missing |
|Frontier status |Control Plane/config plus issued tasks |ACTIVE configuration versus exhausted issuance/runtime |Different scopes, not proof of actionable inventory |
|Hypothesis/Candidate identity |Scientific Core/Factory |Old CandidateHypothesisG1, shared Candidate, native V2 candidate drafts |Cross-generation mappings need proof; IDs cannot be equated by labels |
|Economic Identity |W1/shared structural owner |Native module and shared representation |Q's native/shared wire binding remains unresolved |
|Scientific verdict |C0 over Factory references |Old preserved kernel, public adapter, latest C0 source |Adapter is intentional; later semantic-independence guard is unported |
|Composed V2 qualification |Existing V2 pipeline |CP079-era W2 path versus CP099 source-qualified forward path |Named proposal/model/time checks missing from W2; do not invent a new pipeline |
|Economic Lifecycle |D0 |Preserved byte-equal kernel plus campaign adapter |No second lifecycle shown by this decomposition; production use still unproved |
|Proposal/admission identity |V3 for its new contract |W2V2 ledger, V3 durable ledger, F seed registry/intake |Separate unintegrated stages/rails; reconcile ownership before deployment rather than assuming three active ledgers |
|Research denominator |Several scoped historical owners |Fast versions, Weather seeds, Edge looks, legacy20, nativeV2 trials, F demo, V3 proposals |Global deduplicated denominator unknown; no isolated ledger supplies it |
|Authority |Owner plus task/global policy |Global false, UST specific text grant, older admissions |CT06 unresolved scope; audit confers no authority |
|Book |Capital Book |Capital ledger and zero-authority evaluation ledger |Intentional separation; do not interpret replay NAV as actual assets |
|Learning / Memory |Learning store, then Scientific Memory for research |Feedback, imported legacy, scoped negative knowledge, UI status |Current real-root→experiment→Learning→Memory re-entry not proved |
|Live Lab activity |Projection of canonical events |Sessions, worker events, SSE/reducer and saved browser proofs |Historical activity evidence; UI must not become an orchestration authority |
|CP/H identifiers |Rail plus object identity |DifferentCP017s; listing-fadeH006 versus sportsH006 |Scope IDs by rail/SHA; preserve imports and retractions |

The audit CSVs are frozen projections, not a new product ledger. UNKNOWN and NOT_FOUND must survive any later Owner-facing projection; neither may silently become KILL, PASS or a fabricated missing task.
''')

md('19_RESEARCH_DENOMINATOR.md',f'''
# Recovered research denominator

## Exact operational scope

FACT_PROVEN counts below refer to`{R}:research/research_os/`. E08/E10. They do not estimate the entire project's private or historical search denominator.

| Requested field | Demonstrable value | Boundary |
|---|---|---|
|TOTAL_FRONTIER_TASKS |49 |48 from4 configured families plus1 older quant-signal task; not49 ideas |
|TOTAL_ROOT_IDEAS |15 frozen hypothesis objects in this corpus |Global independent roots unknown; ASML overlap explicitly flagged |
|TOTAL_HYPOTHESES |15 frozenG1 files |Repeated generated drafts are separate attempts, not new frozen hypotheses |
|TOTAL_DUPLICATES |18 exact-current-duplicate blocked tasks |Not18 distinct hypotheses;11 nativeV2 trial rows generate11 discarded drafts |
|TOTAL_REJECTED |UNKNOWN globally |BLOCKED and PARK_DATA are not economic rejection |
|TOTAL_BLOCKED |38 tasks |18 duplicate +10 quant-source +9 stage-authorization +1 epoch-context |
|TOTAL_PARKED |7 of15 frozen hypotheses classified VALIDLY_PARKED in this audit |Seven others VALIDLY_BLOCKED and one suspected positive orphan; audit classification, not a uniform stored enum |
|TOTAL_KILLED |UNKNOWN globally |Two Edge result files have KILL_EXPRESSION; no completed economic rejection established for the current15 |
|TOTAL_POSITIVE_VALIDATIONS |8 bounded positive documentary dispositions among the15 |Includes EXPLORE and passes with blocks; not8 economic passes. Two additional Apple producer EXPLORE premises actually continue to parks |
|TOTAL_TEST_DESIGNS |At least2 recent protocols tied to these roots: UST and Form144 |Form144 exists off runtime/W2; additional historical protocols exist; global count unknown |
|TOTAL_EXPERIMENTS |One source-acquisition execution attempt for current15, Form144 |No completed economic outcome found for these15; global experiment count unknown |
|TOTAL_SCIENTIFIC_VERDICTS |14 COMPLETE validation tasks; formal new C0 production count unknown |Do not rename14 task completions14 validated-edge verdicts |
|TOTAL_ECONOMIC_IDENTITIES |Production objects for current15 NOT_FOUND; global UNKNOWN |Contracts and fixtures exist |
|TOTAL_PORTFOLIO_READY |Observed production current15 NOT_FOUND; global UNKNOWN |Pre-outcome readiness is not observed portfolio utility |
|TOTAL_ORPHANED_POSITIVE_HANDOFFS |One suspected UST expected execution missing; global UNKNOWN |Four older positives remain untraced and are not automatically called orphans |

The current classification is7 parked /7 blocked /1 suspected orphan. [CSV10](10_IDEA_MASTER_LEDGER.csv) enumerates the exact objects. This does not measure the conditional probability that a research source produces an edge.

## Why146 recovered rows are not146 ideas

The master ledger contains15 frozen hypotheses,14 family/program records,11 queue expressions/software generations,20 legacy reconciliation records,33 Weather design seeds,9 expression result records absent from that queue, and44 version-scoped Fast records. These overlap. Six versions of one Fast journal, a copied legacy result and its underlying expression cannot be added as independent roots. H006 also changes meaning between rails. The Weather ledger explicitly says REPAIR_SEED_NOT_PRE_REGISTRATION.

UNKNOWN: the deduplicated historical root count, all attempted variants, exposure before registration, private failed ideas and any uncommitted attempts. The15 current hypotheses and14 unified Fast H-IDs are valid scoped counts, not additive project totals.

## Accounting already present

- Fast Rail records declared grids, trial and prior-trial counts, imports and amendments. It also records a correction that some `at` times were planned rather than actual commit chronology.
- Edge Lab records admissions, looks, protocols, jobs, trial charges and exposure. VXv0/v1/v2 are not three independent confirmations.
- RuntimeV2 records epoch/trial intents, model/prompt/source/retrieval hashes. Eleven RESEARCH_GENERATION_TRIAL records generate11 proposals and discard11; model identity is DETERMINISTIC_ENGINE. Earlier V1/migrated work is not made equivalent by these later sidecars.
- F implements root/seed/variant/exposure accounting on a qualified separate branch. Its deterministic demo reports7 roots,5 parameter variants and0 tested variants. Those are not production research discoveries.
- V3 preserves accepted/rejected proposals, identity, provenance, duplication and replay. It does not enroll every historical root question or native generation trial, and production use is not shown here.

Therefore both “no denominator exists” and “the denominator is solved by V3” are false descriptions of the recovered evidence. Late Builder CP090/093/096 additionally strengthens attribution/model/time controls beyond the selected CP079-era composed path. E25.

## Actual historical result objects

Across advertised heads,15 Edge Lab `*.result.json` paths exist:1 PROMOTE_EXPRESSION,2 KILL_EXPRESSION and12 PARK/PARK_DATA. Some contain invalid source/capture attempts or quarantined outcome exposure. They are not15 admissible independent economic tests. SMARD, Form144, Fast and earlier labs use other formats. The exact global trial count remains UNKNOWN.

Outstanding reconciliation: root question→mechanism→generation→variant→trial→look→outcome; commit clock versus recorded clock; original run/receipt; authority and prior knowledge; cost/time; blocked, abandoned and negative outcomes; delayed observation. These are recovery requirements, not authorization to rebuild F or V3 during this mission.
''')

md('20_NORTH_STAR_DELTA.md',f'''
# Delta against the actual North Star document

FACT_PROVEN: `QUANT_NORTH_STAR.md` bloba328b4e6d7d71dafd532938888ebf9818b1b610f is identical on W2/F/Q/V3. The20 October revision8b1ff1d0 expands the final research architecture and explicitly makes the links part of the target. Default/runtime retain older blob8295041a. UNKNOWN: one formal Owner promotion resolving target, default and operational routing. E18/CT14.

| Normative component | Recovered reality | Delta category | Evidence / unfinished question |
|---|---|---|---|
|Net real wealth objective |Explicit objective; no current capital proof |PRESENT_AND_MATCHING objective; MISSING final proof |North Star§1, closed authority, replay Book |
|Owner / Governance |Global/task policies plus unresolved UST specific grant |PRESENT_BUT_DIFFERENT |Scope/revocation normalization missing |
|Canonical Research Core |Hypotheses, generations, freeze, trials, evidence and negatives |PARTIAL |Historical denominator and contract generations not globally reconciled |
|Research Control Plane |Queue, leases, CAS, permissions and durable wakes |PRESENT_AND_MATCHING bounded machinery |Exhausted configured inventory; not unlimited self-authorizing research |
|Producer families |Four frontiers, documentary packets and producer templates |PARTIAL |Missing quant sources, repeated Apple packets, flow authorization mismatch |
|Archaeology |Legacy20, recovery tasks and memory bridge |PARTIAL |Explicit historical provenance gaps remain |
|Early Implementability |Contracts and tests |PARTIAL |Real-question source/cost/capacity evidence missing |
|Experiment Infrastructure |Registry, freeze, geometry, power and runner code |PARTIAL |Only source-stage Form144 attempt recovered for current15 |
|Cross-examination |Code and actual documentary stages |PRESENT_AND_MATCHING within scope |No independent economic confirmation implied |
|Validator / Red Team |Actual challenge tasks and claim restrictions |PARTIAL |Latest C0 semantic-independence and late composed V2 controls not all integrated |
|Economic Identity |W1/shared/native contracts |PARTIAL |Q's native/shared wire owner unresolved |
|Portfolio Map / Engine |Readiness and structural portfolio code |PARTIAL |No observed marginal portfolio utility for current roots |
|Shadow / Prospective |Forward contracts and VX register |PARTIAL |Zero VX observations, current global authority closed |
|Shadow Book |Persistent V1 implementation |PRESENT_AND_MATCHING topology; PARTIAL production |No current real research identity traced through it |
|Prospective Validation |Registered future work; no positive prospective sample found |PLANNED_ONLY / NOT_YET_DUE in recovered witness |Eligible future observation still required |
|Decay Monitoring |Modules and D0 states |PARTIAL |No durable economically validated current edge to monitor |
|Real Events / Receipts |Actual files and historical SSE |PARTIAL |UST receipt gap; full outbox/state correlation unaudited |
|Live Research Lab |Implemented projection and saved host/browser proofs |PRESENT_AND_MATCHING projection; PARTIAL freshness |Fresh deployment/process/browser state unknown |
|Data Plane |Daily proxy panels and source/PIT infrastructure |PARTIAL |Per-question population, security clocks and executable costs absent |
|Capital Desk stages |SCAN/VET/SIZE/RISK/FILLS/BOOK code and replay |PRESENT_AND_MATCHING topology; PARTIAL real connectivity |Research-to-capital identity/authority proof missing |
|Learning / Memory feedback |V1 feedback and Scientific Memory code |PARTIAL |Current experiment→Learning→Memory→new-root loop not found |
|Build Plane |BuildTask gaps and engineering workflows |PARTIAL |No inferred autonomous deployment authority |
|Two-speed intelligence |Backend policy and local commentary qualification |PARTIAL |Not evidence of superior autonomous discovery yield |
|Autonomy |Real bounded loop |PARTIAL |F disabled; general positive economic continuation not proved |
|Authority membranes |Mostly closed pre-outcome scope |PRESENT_BUT_DIFFERENT representations |UST exception and historical outcome exposure remain visible |
|Final convergence / completeness |W2 candidate and exact cumulative CI |PARTIAL |No integrated SHA emission; Q blocked; qualified separate work remains |

No component is labeled NO_LONGER_JUSTIFIED or SUPERSEDED_BY_NEWER_DESIGN without a recovered Owner decision. F/V3 additions do not revoke the North Star. Whether an Advanced Research capability/subsystem/tab is needed belongs to the subsequent evidence-based research mission, not this reconstruction.
''')

md('21_SUPERSESSION_GRAPH.md',f'''
# Supersession and reuse graph

An arrow states a particular succession, port or reuse relation. It does not imply complete semantic integration or authority transfer. Unknown historical supersession remains explicit in the branch ledger.

```mermaid
flowchart TD
  V1[Early persistent V1] --> OS[Research OS tasks and documentary workers]
  OS --> OV1[Oracle V1 state0837f419]
  OV1 -->|timer successor| OV2[Oracle V2 state16eafd0b / releasea67ffec]
  W1[W1 Memory / Data / Factory / Economic] --> C69[CP069-first attemptac50b0c3]
  C69 -->|base role superseded| C79[CP079-first cumulative rail]
  A[MEGA A RI] --> C79
  C79 --> IMM[Repaired immutable base2b99d8ae]
  IMM --> W2[W2 candidateebc72b9f]
  IMM --> VF[V2 forward CP080-099 /ded4228]
  B[MEGA B] -->|adapted port| W2
  COLD[C0 old kernel3f0e1b7] -->|preserved plus adapter| W2
  D0[D0 kernel] -->|preserved plus adapter| W2
  E[MEGA E] -->|port| W2
  MS[MultiSource V1/V2bbdea6a7] -->|actual merge| W2
  IMM --> I3[Intake V30691a4c1 / qualified separate]
  W2 --> F[GIGA F79329f15 / qualified disabled]
  W2 --> Q[GIGA Q4efadddf / not qualified]
  COLD --> CNEW[C0 semantic repair66bdd160 / latest6dc84]
  HP[H pre / Convergence1] -->|bounded probes and overlap| Q
  VO[V old92c4ee0] -->|retained replay| Q
  VN[V current e98a source /5d6 tip] -->|latest attacks to reconcile| FUT[Future pinned target qualification]
  CNEW -->|unported repair| FUT
  VF -->|named late controls absent in W2| FUT
  I3 -->|integration not proved| FUT
  F -->|integration not proved| FUT
```

FACT_PROVEN: F/Q parentage, V3's base, actual MS merge, named byte-preserved ports and late control differences. STRONG_INFERENCE: the FUT node is a dependency order for later work, not an existing build. E01/E19/E25.

| Older object | Successor / retained role | Evidence that must survive |
|---|---|---|
|CP069-first |CP079-first/2b99 replaces its base role |Old qualification/failure scopes remain useful |
|97165db2 |Historical C0/D0 base;2b99 is later Wave2 base law |Qualified source adapted, not blindly overwritten |
|CP079-era composed controls |Forward CP080–099 adds later controls; W2 did not absorb all |Before/after attacks, subject/model/time guards and source qualification |
|MultiSource policies interpreted as independent sources |Passive V2/V3 admission and F distinguish policies/origins |A/B/C remain policies; no measured independent source productivity |
|Earlier V replay-depth claims |Current corrections and rebuilt038–046/061 |53 rejected labels,46 repair groups and CP039 no-defect proof remain distinct |
|V completion claim |Current phaseA incomplete / Owner stop046 |Scoped repairs and attack cases, not an invented CP100 pass |
|H L001 |Q10 partially addresses metadata transport |Original probe still required on final target |
|V LONGITUDINAL_001 |Q04 adds a legacy-review guard |Original truth-transmission counterexample |
|Oracle V1 timer |V2 timer/boot lineage |Old hypotheses/receipts/exposure, without enrollment reset |
|Parallel Fast3ujgeu |STOP_OWNER and unified0ydmkg |Imports, trial charges, timestamp correction and local-ID mapping |
|VXv1 reader failure |v2 reader repair under the same economic expression |Old failure and exposure retained; no independent-trial inflation |
|C0 preserved old kernel |Later qualified C0 remains unported |Semantic-independence policy must be reconciled explicitly |
|Future GIGA F prompt |A real qualified partial build now exists |Reuse its code/contracts/accounting before authorizing any replacement build |

Q has not replaced W2: Q fails its final qualification. V3 has not replaced the entire cumulative system: it is upstream and based on an earlier immutable base. Deployment is not inferred from either branch name.
''')

md('24_FUNCTIONAL_PROGRESS_MATRIX.md',f'''
# Functional progress without a project percentage

Comparison candidate`{C}`; operational state`{R}`. File/CI/artifact facts are FACT_PROVEN. Progress judgments are STRONG_INFERENCE within the stated scope; none is a productivity estimate or proof of an edge.

| Dimension | Status | Evidence | Why incomplete | Next true milestone |
|---|---|---|---|---|
|DATA / PIT |Implemented/tested; real question blockers |E03/E10/E12/E13 |A daily proxy is not a complete PIT executable population |One existing question with qualified source/security/clock/cost chain |
|RESEARCH INPUT |Multiple historical origins; F qualified but disabled |E06/E08/E16/E21 |Distinct productive feed not proved; packets repeated |A distinct enrolled question or justified NOOP |
|AUTONOMOUS IDEA GENERATION |PARTIAL with real documentary production |E23/E09 |Two Apple roots do not establish continuous novelty; frontier exhausted |Authorized fresh source/mandate→distinct root, under budget |
|IDEA ADMISSION |V2 in candidate; V3 qualified separately |E05/E03 |V3 not converged/deployed |Connect without duplicating V3 identity/admission |
|DISCOVERY |B implemented/tested; production seam unproved |E20/E07 |Actual admitted Proposal→Candidate lineage missing |One real exact-ID transition with task/receipt |
|SCIENTIFIC FACTORY |W1 infrastructure and actual isolated campaigns |E03/E11/E12 |No completed current-root costed economic outcome |Existing protocol→bounded execution and durable disposition |
|SCIENTIFIC ADJUDICATION |C0 contracts; late controls unintegrated |E19/E25 |Independence, model, subject and time policies diverge |Reconcile existing guards and target replay |
|ECONOMIC IDENTITY |Modules and readiness contracts |E07 |Native/shared wire owner unresolved |One canonical owner and frozen-identity round trip |
|PORTFOLIO READINESS |Pre-outcome contracts |E03/E07 |No observed marginal utility |Admissible object with costs, risks and co-exposure, then evidence |
|ECONOMIC LIFECYCLE |D0 kernel/adapter present |E20 |Contract status is not economic proof |Real C0→Economic→D0 lineage under authority |
|RUNTIME AUTONOMY |Durable wakes; now NOOP |E09/E10 |Source, task-contract and quota limits |Qualified release plus admissible mandate, not artificial quota work |
|CRASH / RECOVERY |Bounded V1/Oracle/V evidence |E03/E14/E07 |Latest attacks not qualified on one final target |Exact-target process-death, fencing and outbox replay proof |
|RESEARCH→CAPITAL CONNECTIVITY |Partial contracts |E07 |Economic Identity and authority binding unresolved |Real research ID preserved into paper/shadow Opportunity |
|BOOK |Implemented/tested; zero-fill replay Book |E03/STATE |No audited current real account or live authority |Authorized paper position linked to qualified object |
|FEEDBACK / LEARNING |V1 feedback and Memory code |E03/E08 |Current experiment→Memory re-entry not traced |Scoped negative/result consumed with provenance |
|CLOSED RESEARCH LOOP |Not proved end to end |E07/E11/E23 |Economic continuation and learning loop missing evidence |One real root to terminal result and informed next question |
|PROSPECTIVE PROOF |No positive proof found; VX registered, not due |E16 |Zero observations; authority restrictions |Eligible future predeclared observation without leakage |
|ECONOMIC PROOF |Exploratory historical expressions only |E16/E17 |Execution, cost, capacity and independence unresolved |Costed expression with appropriate independent/prospective evidence |
|LIVE CAPITAL READINESS |NOT_AUTHORIZED / NOT_PROVEN |E09/E17 |No authority or full economic/operational proof |Explicit future Owner authority after required evidence |

Negative findings, a valid park and justified NO_TRADE are useful outputs. More proposals would not by itself close the blockers already present.
''')

md('25_RECOMMENDED_NEXT_SEQUENCE.md',f'''
# Recommended next sequence — provisional until the forensic gaps close

These are reviewable dependency steps, not actions executed by this audit. No product change, deployment or new outcome access is authorized here.

| Action | WHY NOW | DEPENDENCY | INPUT SHA | REUSES / MUST NOT REBUILD | QUESTION CLOSED | STOP CONDITION | SUCCESS EVIDENCE |
|---|---|---|---|---|---|---|---|
|1. Finish targeted recovery |Owner cannot yet point to every historical rail or positive lineage |None; use the frozen corpus |E01 ref vector; lab337c4b7c; Fastfa2aaef9; Weather/P0/Gate rails |Reuse261 branch/704 CP records and146 recovered idea rows; do not rerun sources or recreate old trials |Four old positives,223 unclosed branches,584 CP records, historical authority/denominator |An item resolves to exact proof or a documented NOT_FOUND/access boundary; no length-based completion claim |Gap files closed or explicit impossibility established |
|2. Resolve canonical identity and seal policy |Default, candidate and installed release differ |Review exact W2 cumulative and separate gate evidence |W2`{C}`; releasea67ffec; default`{DEFAULT}` |Reuse exact CI/preflight; no second Control Plane, Oracle or Factory |Which SHA is Owner-promoted and which gates are mandatory |Unresolved promotion rule or source change invalidating reused qualification |SHA-bound Owner seal, exact remote identity, gate scope, authority and installed-version evidence |
|3. Resolve UST continuation and authority |A real promising protocol lacks its expected execution/receipt |Specific grant versus global policy clarified before outcomes |Freeze7b843ddd; CP2ac3b32ff; runtime`{R}` |ReuseG1, frozen endpoint/sample/multiplicity; no retuned10Y test or new Discovery |Valid block/park versus missing authorized execution |Unestablished authority, inadequate source or undeclared exposure |A linked execution/result or explicit park, with receipt gap explained without retroactive fabrication |
|4. Reconcile scientific integrity on one target |Latest C0 and forward controls are qualified separately; Q is blocked |Pinned target and later separately authorized change mission |C0latest6dc84/repair66bdd160; forward`{VF}`; Q`{Q}`; V sourcee98a; H`{H}` |Reuse existing C0 and V2 guards,13 Q repair groups,46 V groups, L probes; no parallel adjudicator/identity/scheduler; no bulk old files |Independence count; subject/model/time admission; Economic Identity ownership; frozen metadata and legacy-review transport |Unexplained hostile failure, owner conflict, inadequate independent confirmation capacity |Applicable attacks and controls pass on target, or are rejected with semantic evidence; no PASS by unexplained test exclusion |
|5. Reuse F and V3 with explicit stage ownership |Two qualified upstream builds already exist |Stable contracts and known downstream capacity |V3`{V3}` on2b99; F`{F}` on ebc |Reuse V3 admission/ledger/replay and F roots/exposure/budgets; no new Discovery or duplicate admission |Seed→V3→existing Discovery under one lineage, without second truths |High duplicates, unavailable source, budget/backlog or no distinct question |One durable exact-ID transition or justified NOOP; not proposal volume |
|6. Resume research from actual blockers |Current roots mostly need evidence/data/authority rather than more module names |Appropriate operational authority and preserved identities |Runtime15 roots; Form1449faba4fe; DueBillb9f6ee8a; VX68bbab8e |Reuse protocols and negative memory; do not repeat known source failures or retune exposed expressions |Which low-cost missing fact produces a discriminating next decision |Same failed route, unauthorized sourcing, missing independent confirmation or changed post-outcome expression |A resolved blocker or informative rejection/park; zero new ideas remains valid |
|7. Resume the architecture/literature question afterward |Avoid calling a branch-existing capability missing |Forensic gaps closed or explicitly accepted as bounded limitations |This frozen dossier plus separately recorded later seals |Reuse prior research question/protocol; complete positive/negative external evidence; do not conflate capability, subsystem and tab |Smallest genuinely missing research architecture given actual questions, continuations and discovery literature |A conclusion supported only by survivors or an unknown denominator disguised as yield |Evidence-supported functional gap, separated from integration debt and operational/data blockers |

## Concrete Owner decisions after the audit

1. Select the promoted SHA and mandatory qualification policy from the concrete W2/F/V3/Q/forward evidence. A FINAL label is not that selection.
2. Resolve whether UST's recorded specific grant is active and applicable to the current runtime; the frozen protocol and conflicting global state are available for review.
3. Choose which data dependencies warrant an authorized acquisition/license versus a durable park. Use the actual question and task blocker register before proposing budgets.

These are not blocking permission requests during the current read-only work. They identify facts of authority or priority Git cannot invent.

The observed immediate bottleneck is a **fragmented, incompletely converged research continuation chain constrained by real data and task authority**, not a proven shortage of idea-generating agents. STRONG_INFERENCE from E05–E13/E19/E23/E25. It is not yet a verdict on whether Advanced Research should exist; that requires the later comparative research requested by the Owner.
''')

# Refresh the evidence index wording and include newly recovered late controls / original lab evidence.
p=ROOT/'reports/EVIDENCE_INDEX.md';s=p.read_text()
s=s.replace('33canonical','33 canonical')
s+='''\n| E25 | V2 forward `ded4228de74ce3b6926d9ea3e3c2114ff1be8208`: exact Oracle V2 Core run39660277404 and SEC run39660277407 both PASS. CP080–099 includes7 source repair groups. W2 lacks the named composed proposal/model/time guards; Q overlaps tuple scanning. `late_v2_control_recovery.json` preserves the source diff and scope. |\n| E26 | Original lab head `337c4b7c78cb769550e165be00e0b12da4c9d65d`: `research/structural_edges_2026-09-25/scripts/lab2_crypto/xvenue.out`, `scripts/lab2_eq/results.txt` and `research/deep_research_2026-09-24/REPORT.md` are actually present and were read. This verifies the existence of old reported positives, not their independent validity or downstream completion. |\n'''
p.write_text(s)

# Current gap enumerations and unambiguous metrics.
br=rd('05_BRANCH_AND_RAIL_LEDGER.csv');cp=rd('04_CP_MASTER_INDEX.csv');ps=rd('11_POSITIVE_IDEA_LINEAGE.csv')
pending_br=[x for x in br if x['AUDIT_REVIEW_STATUS']!='SCOPED_REVIEW_COMPLETE'];pending_cp=[x for x in cp if not x['AUDIT_REVIEW_STATUS'].startswith('CURRENT_LABEL')];pending_ps=[x for x in ps if x['TRACED_TO_TERMINUS']=='NO']
csvout('GAP_BRANCHES.csv',pending_br);csvout('GAP_CP_RECORDS.csv',pending_cp);csvout('GAP_POSITIVE_LINEAGES.csv',pending_ps)
metrics=dict(RELEVANT_BRANCHES_DISCOVERED=len(br),RELEVANT_BRANCHES_CLASSIFIED=len(br)-len(pending_br),BRANCHES_PARTIALLY_CLASSIFIED=sum(x['AUDIT_REVIEW_STATUS']=='PARTIAL_REVIEW' for x in br),CP_RECORDS_DISCOVERED=len(cp),CP_RECORDS_CLASSIFIED=len(cp)-len(pending_cp),CP_RECORD_COUNT_SCOPE='517 artifact versions +187 unbound subject-label records, not704 completed CPs; classified120=100 current V label dispositions +20 current Builder V2-forward label dispositions',POSITIVE_RESEARCH_ITEMS_DISCOVERED=len(ps),POSITIVE_RESEARCH_ITEMS_TRACED_TO_TERMINUS=len(ps)-len(pending_ps),POSITIVE_RESEARCH_SCOPE='Recovered unique positive leads; global completeness unknown',QUALIFIED_HEADS_DISCOVERED='UNKNOWN_GLOBAL;8 exact-head component/cumulative CI qualification scopes plus3 locally bound H/V source scopes documented',QUALIFIED_HEADS_ACCOUNTED_FOR='11_SCOPED; other historical qualification claims pending',ARCHITECTURE_CAPABILITIES_DISCOVERED=63,ARCHITECTURE_CAPABILITIES_CLASSIFIED=63,ARCHITECTURE_SCOPE='Requested/recovered functional surfaces, not every historical module semantically closed',UNRESOLVED_CONTRADICTIONS=8,UNTRACED_POSITIVE_HANDOFFS=len(pending_ps),UNTRACED_POSITIVE_HANDOFFS_SCOPE='1 suspected UST missing execution +4 historical positives with unknown descendant; not5 proven orphans',UNKNOWN_CRITICAL_ITEMS=12,AUDIT_COMPLETENESS='INCOMPLETE')
dump('audit_completeness_metrics.json',metrics)
md('00_AUDIT_PROTOCOL_AND_GAP_PASS.md',f'''
# Protocole, couverture et lacunes restantes

**AUDIT_COMPLETENESS=INCOMPLETE.** Les25livrables forment une photographie de reconstruction; ils ne certifient pas la clôture de toute l'histoire. La synthèse Owner est en français et les dossiers techniques en anglais.

## Mission appliquée

La mission courante est une récupération forensique. Le premier prompt reste le contexte d'une recherche externe ultérieure sur l'architecture manquante. Pendant cette passe : aucune recherche de littérature nouvelle, modification du produit, correction de défaut, exécution de test produit, nouvelle capacité, activation, publication ou message à un tiers.

Les écritures se trouvent dans `/workspace/quant-trade-owner-recovery`, hors du dépôt produit. Le miroir bare et les extractions sont des supports de lecture. Les CSV sont des projections d'audit figées, pas une nouvelle base opérationnelle.

```
AUDIT_STARTED_AT=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_TIME=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_SHA={C}
AUDIT_AS_OF_SHA_SCOPE=W2_COMPARISON_CANDIDATE_NOT_OWNER_PROMOTION
AUDIT_REF_VECTOR_SHA256={REFHASH}
```

La vérité multi-rails repose sur le vecteur des261refs. Un seul SHA ne peut pas représenter des branches divergentes. Les observations ultérieures de CI ont été interrogées par SHA exact. Le miroir n'a pas été actualisé sous les analyses.

## Travail réellement effectué

1. Métadonnées GitHub, default et refs figés; miroir du graphe accessible :5509commits,261branches,252HEAD distincts.
2. Catalogue des162087entrées d'arbres de HEAD et9267paths distincts. Extraction de4483blobs de texte,4669couples path/blob, dont des artefacts historiques. Les objets binaires/gros et les chemins sensibles ne sont pas injectés dans le contexte; le miroir conserve les objets Git accessibles.
3. Export de12snapshots matériels; lectures d'implémentations, contrats, tâches, reçus et résultats. Les README et prompts ne sont pas considérés comme preuve d'exécution.
4. Ledger des261branches avec merge-base/ahead/behind; index de704records CP/mentions. Git ne conserve pas directement la création d'une branche : CREATED_FROM reste UNKNOWN si rien ne la prouve.
5. CI exacte W2/F/Q/V3/A/B/C0/D0/E/Form144/V2-forward; jobs/logs des points critiques. Comparaison du contenu des ports. Vérification83/83hashes source V,334/334hashes de preuve V et21logs Q compressés/décompressés.
6. Census des72tasks et15hypothèses du runtime figé;49frontier tasks; motifs des38blocages; descendants réels sur branches séparées et deux continuations documentaires automatiques.
7. Extension historique :15result paths Edge Lab,20legacy records,33seeds Weather,6versions du Fast ledger, anciens résultats positifs originaux;146lignes récupérées avec chevauchements explicites.
8. Registres des autorités, représentations concurrentes, orphelins, blocs, North Star, H/V/L et dette qualifiée non intégrée. Récupération supplémentaire du rail Builder CP080–099 après sélection de la base CP079.

## Classes de preuve

FACT_PROVEN : objet, identité, contenu ou activité datée observés; pas vérité économique implicite. STRONG_INFERENCE : meilleure interprétation bornée des objets, par exemple une exécution attendue absente des corpus recherchés. WEAK_INFERENCE : indice insuffisant. CONTRADICTORY_EVIDENCE : représentations concurrentes conservées. UNKNOWN : preuve insuffisante. NOT_FOUND : recherche décrite sans objet retrouvé, pas preuve absolue d'inexistence.

`AUDIT_REVIEW_STATUS` distingue l'indexation d'un examen fonctionnel scoped. Les120records CP classifiés sont100dispositions actuelles de labels V et20du rail Builder V2-forward. Cela ne signifie ni120réparations, ni704CP compris. Les53labels V rejetés sont classifiés comme tels, pas validés comme progrès.

## Métriques

```json
{json.dumps(metrics,ensure_ascii=False,indent=2)}
```

## EXACTLY_WHAT_REMAINS_UNAUDITED

- [GAP_BRANCHES.csv](GAP_BRANCHES.csv) :223rails non clos, dont222census Git seulement et1partiel. Ils ont chacun un HEAD fixé, pas une qualification fonctionnelle inventée. Familles restantes : P0, GateA/B, Weather Owner/Astra/Lots1–3, anciens labs/fast/F1/F2, variantes Live Lab, economic-readiness sub-builders, anciens rails Claude et host/ops.
- [GAP_CP_RECORDS.csv](GAP_CP_RECORDS.csv) :584records non clos, dont187mentions de CP dans les subjects encore non liées à leur portée exacte. Des versions d'un artefact ne sont pas des CP indépendants. Un trou numérique ne prouve pas qu'un CP aurait dû exister; aucun checkpoint manquant n'est inventé.
- [GAP_POSITIVE_LINEAGES.csv](GAP_POSITIVE_LINEAGES.csv) : UST après freeze; LAB24 futures/trend/carry; LAB25 HL-CEX funding, FOMC et pensions. Les fichiers des résultats anciens existent et ont été lus; descendants finaux et comptabilité des expositions/variantes restent à réconcilier.
- Hors des72tasks Oracle : reçus/outbox/Book/Learning historiques ne sont pas intégralement corrélés. Les claims de qualification et missions anciens ne sont pas tous liés à leurs SHAs exécutables.
- Tous les raw data, binaires, gros logs et artefacts Actions non committés n'ont pas été audités intégralement. Aucun rejeu du produit n'a été effectué.
- Les764cas en échec dans le vieux rejeu Q ne sont pas triés en causes racines indépendantes et applicables. Aucun H/V/L final ne peut être certifié pour une convergence comprenant les correctifs tardifs C0/V2, F et V3.
- GIGA C : aucun artefact nommé retrouvé dans les refs/texte extraits. Les conversations privées ou builds non poussés restent UNKNOWN; ce n'est pas une preuve d'inexistence.

## Douze inconnues critiques

| ID | Inconnue restante |
|---|---|
|K01 |Promotion canonique Owner et politique exacte de seal |
|K02 |État frais du processus, release installée et site distant |
|K03 |Exécution/résultat UST et reçu de validation manquant |
|K04 |Owner et wire natif/partagé Economic Identity |
|K05 |Dénominateur historique root/variant/trial/look dédupliqué |
|K06 |Exposition privée humaine/modèle aux outcomes |
|K07 |Terminus des quatre positifs des anciens labs |
|K08 |Examen fonctionnel complet des223branches restantes |
|K09 |Interprétation scoped des584records CP restants |
|K10 |Causes applicables des échecs hostiles Q |
|K11 |Autorités et preuves hôte historiques Weather/P0/Gates |
|K12 |Provenance primaire non récupérée de claims MLB/Soccer/BoxOffice |

## Résultat du GAP PASS

Il reste des branches non classifiées fonctionnellement, des CP non interprétés, des qualifications anciennes non liées,5positifs non tracés jusqu'au terminus, des artefacts runtime non corrélés et un owner de seam inconnu. Les composants North Star portent tous un statut, mais plusieurs sont PARTIAL ou UNKNOWN. La mission n'est donc pas close.

La prochaine passe doit reprendre ces listes et ce miroir, conserver les acquis et fermer les trous. La question d'architecture du premier prompt reste en attente de cette base factuelle; elle n'est pas remplacée par une intuition tirée des lacunes de l'audit.
''')

print(json.dumps({'pending_branches':len(pending_br),'pending_cp_records':len(pending_cp),'pending_positive_items':len(pending_ps),'classified_cp_records':len(cp)-len(pending_cp)}))
