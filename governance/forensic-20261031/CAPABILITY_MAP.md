# Quant-Trade — carte canonique des capacités après reconstruction de surface

STATUT : `CAPABILITY_RECONCILIATION_COMPLETE_FOR_PLANNING`

Cette carte est construite après la chronologie de surface complète de la photographie initiale : 6 393 commits / 71 journées actives. Elle ne prétend pas que chaque diff ou chaque version documentaire a été relu sémantiquement. Elle sert à arrêter le recommencement et à décider quoi réutiliser, connecter, réparer, parquer ou retirer de la future surface active.

## Règle de décision

Ordre obligatoire : `REUSE > CONNECT > REPAIR > BUILD`.

États valides : `REUSE`, `CONNECT`, `REPAIR`, `PARK`, `RETIRE_FROM_ACTIVE_SURFACE`, `UNKNOWN_DECISION_RELEVANT`, `NO_CHANGE_REQUIRED`.

`BUILT != QUALIFIED != MERGED != PROMOTED != ACTIVE != USED != PROVEN_END_TO_END`.

## Fait de topologie qui change la stratégie

Wave2 C2 est scellé à `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Comparaisons Git fraîches :

- `ebc72b9f…` vs default actuel `blue/master-v2-2026-09-20` / `2d0af7cb…` : `DIVERGED`, merge-base `09ba64b8bee1419076ec8a30f8d75a916932c2ba`, default +31 commits depuis le merge-base, Wave2 +1 221 ;
- `ebc72b9f…` vs Issue #44 / PR #46 `afedfd57986aa042e9e97aa53b9db53b4619764f` : `DIVERGED`, même merge-base `09ba64b8…`, PR46 +44, Wave2 +1 221.

Conclusion : **aucune des branches récentes Blue/PR46 ne peut remplacer Wave2 en bloc sans perte massive de convergence**. Inversement, Wave2 seul ne contient pas les réparations récentes d'orchestration/autonomie. La convergence finale doit partir du socle Wave2 puis importer sélectivement des deltas qualifiés récents.

`capability-lineages.csv` confirme ce point au niveau fichier : de nombreux objets Mega-B sont byte-identiques dans Wave2, one-shot, C0 et WP2, alors que plusieurs chemins Research OS sont absents dans PR46 et son workflow SEC est modifié. `PATH_ABSENCE != CAPABILITY_LOSS`, mais cette absence impose une revue sémantique avant port.

## Carte de capacités

| Famille canonique | État | Source/ancre principale | Décision |
|---|---|---|---|
| Objective / North Star / authority laws | QUALIFIED_AS_GOVERNANCE | Blue + constitution/Owner checkpoints | `REUSE` dans projet/gouvernance |
| Scientific memory / immutable experiment ledger | CONVERGED_IN_WAVE2 | W1/Mega → Wave2 C2 | `REUSE` |
| Stable hypothesis identity / novelty / negative memory | CONVERGED + later hardening | Wave2 + Research OS CP2 | `REUSE` |
| Preregistration / anti-snooping / sealed single-look | CONVERGED / proven patterns | July→Research OS | `REUSE` |
| Candidate gate / adversarial Judge | BUILT_AND_REUSED | Sep12+ / Wave2 descendants | `REUSE` |
| Evidence Store / content-addressed provenance | EXACT_HEAD_QUALIFIED then ported | Builder C + Wave2 | `REUSE` |
| PIT security identity / corporate actions / lineage | QUALIFIED / converged | Builder C + Wave2 | `REUSE` |
| Data ingestion / SEC raw capture / one-request identity | PARTLY_INTEGRATED | PR16 Blue + Wave2 descendants | `CONNECT`, preserve fail-closed semantics |
| Visibility firewall / irreversible contamination records | REQUIRED_GUARDRAIL | Sep18+ | `REUSE` |
| Causal timeline / fill-aware scientific accounting | REQUIRED_GUARDRAIL | V1 corrective pass + Wave2 | `REUSE` |
| Crash-idempotent economic state / WAL | CONVERGED_CANDIDATE | V1/Wave2 | `REUSE` |
| Sleeves / attribution / portfolio constraints | CONVERGED | V1 + PR31/33 Wave2 | `REUSE` |
| Final-state risk / liveness / watchdog leases | CONVERGED | V1 + later ports | `REUSE` |
| Research Factory / discovery engine / proposal export | CONVERGED_IN_WAVE2 | Mega-B → Wave2 | `REUSE`; do not rebuild from PR46 absence |
| Multi-source / horizontal feature contracts | MERGED_IN_WAVE2 | PR30/31/33 | `REUSE` |
| PR32 deep-horizontal-only extras | CLOSED_UNMERGED | PR32 | `PARK`; import only if exact capability gap remains |
| Wave2 C2 canonical integration | SEALED_ENGINEERING_ANCHOR | `ebc72b9f…` | `REUSE` as provisional code root |
| GIGA-F / GIGA-Q | DESCENDANT_HARDENING | post-Wave2 | `CONNECT` selectively; not separate product |
| Oracle V2 qualification-source provenance / CP057 | EXACT_HEAD_ENGINEERING_PASS | `fecd09e0…`, run `39517451814` | `CONNECT` if not already present |
| Scheduled data collection | ACTIVE_INFRA_CAPABILITY | owner-approved data-feeds | `REUSE`, but generated snapshots are not architecture |
| Edge Lab single-use execution / receipts | QUALIFIED_PATTERN | Oct9+ | `CONNECT` only if not subsumed by Wave2 experiment semantics |
| Live Lab / 3D observability | DOMAIN_CI_QUALIFIED_CANDIDATE | `6076774f…`, run `38744604683` | `PARK/OPTIONAL_CONNECT`; UI never research truth |
| Bounded autonomous Research OS wakes | QUALIFIED_BEHAVIOR | Oct15+ | `REUSE` bounded; `FRONTIER_EXHAUSTED -> NOOP` |
| C0 repair / membrane qualification | EXACT_HEAD_PASS | `13721384…`, run `40437918834` | `CONNECT` only exact repaired semantics; historical one-shot remains NOT_QUALIFIED |
| WP2 synthetic single-lineage causality | BOUNDED_ENGINEERING_PROOF | `8f8df47d…`, run `41069767444` | `PARK_AS_PROOF`; not global autonomy claim |
| GPT-OSS -> Codex bridge | REPAIRED_EXACT_HEAD_HOSTED_PASS | `afedfd579…`, run `41203216122` | `CONNECT` selectively into Wave2-derived code candidate |
| Actual VM GPT-OSS -> Codex -> GPT-OSS multi-wake loop | NOT_PROVEN | host evidence absent in current session | `REPAIR/BLOCK` before autonomy claim |
| WP1 real-science witness / Book Pressure successor | BLOCKED_PRE_EXPOSURE | issue #36 / Oct28 | `PARK`; do not force outcome access |
| Weather prospective transport | PRIOR_POSITIVE_SUPERSEDED | R3 2026-09-30 | `REUSE` correction/abstention rule, not old label |
| Historical hypothesis families / failed trials | NEGATIVE_KNOWLEDGE | July-Oct ledgers | `REUSE` in governance only; not active modules |
| Restaurant-stock | OUT_OF_SCOPE_SIDE_PROJECT | Sep1-11 | `RETIRE_FROM_ACTIVE_QUANT_SURFACE` |
| CI-only / review / challenger / handoff branches | EVIDENCE_SURFACES | many branches | `RETIRE_FROM_ACTIVE_PRODUCT`; retain SHA references |
| Automated feed/telemetry/heartbeat commits | OBSERVATIONS | schedules | `RETIRE_FROM_CAPABILITY_COUNT`; preserve data/receipts as required |

## Scientific conclusions that must not be accidentally resurrected

1. July false positives invalidated after `calc_mdd` / `frac_diff` corrections.
2. July adversarial SPA/DSR ends with `H0 non rejetée`.
3. F1 sealed Stage-B family = `REJECT`; no retune/rerun.
4. F2 = `BLOCKED_DATA_PERMISSION`.
5. Weather unconditional prospective label = `SUPERSEDED` by transport repair.
6. 0DTE dealer-hedging frontier = `NO_CANDIDATE` after mechanism disconfirmation.
7. Historical one-shot = `NOT_QUALIFIED`, even though later C0/membrane repair passes.
8. WP1 successor = `BLOCKED_PRE_EXPOSURE`, not failed/positive outcome.

These belong in durable governance memory so future agents do not recreate them.

## Authority state that remains closed

- `REAL_CAPITAL_AUTHORIZED = FALSE`.
- `LIVE_TRADING_AUTHORIZED = FALSE`.
- Real capital amount remains unknown for decision purposes; the historical 1M value is simulation configuration, not proof of owned capital.
- Fixed-cost baseline remains an economic unknown where required.
- CI green does not establish deployment, activation, science authority or production use.

## Decision-relevant unknowns remaining

Only unknowns that can change convergence are retained:

1. exact semantic delta from Wave2 C2 through each selected GIGA hardening descendant before final code root is chosen;
2. exact collision/compatibility of PR46 files (`codex_adapter.py`, `codex_policy.py`, launcher/workflow/tests) when ported onto the Wave2-derived candidate;
3. actual Oracle VM state and real E2E multi-wake runtime after deployment;
4. storage destination for scheduled generated data if the final repository truly permits only two long-lived branches;
5. 969 undated source occurrences only if a future SHA contradiction makes one decision-relevant.

Everything else is `PARK` or historical evidence and must not trigger another global audit.

## Result

The project is not missing all of its former horizontal/vertical/transversal work. A large portion is already converged in Wave2 C2 and descendants. The current fragmentation problem is primarily **authority + branch topology + duplicate evidence surfaces**, not absence of every capability.

Next file: `TWO_BRANCH_CONVERGENCE_PLAN.md`.
