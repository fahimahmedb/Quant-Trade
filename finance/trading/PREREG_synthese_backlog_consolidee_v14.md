# Pré-enregistrement — Synthèse consolidée v14 (cycles #363-367)

**Committé AVANT toute rédaction.** Cycle #368 du backlog non-ML.

## Nature de ce cycle

Synthèse, PAS un nouveau backtest — aucune nouvelle donnée, aucun
nouveau calcul. Consolide les cycles #363-#367 depuis la synthèse v13
(#362, qui couvrait jusqu'à la découverte du positionnement CFTC).
Arc de 5 cycles marqué par deux extensions consécutives et réussies
du panel de portes combinées (avec MOVE puis CPI), la clôture formelle
de cette famille désormais mature (7 constructions, plafond Règle 9
confirmé à 3/5), et l'exploration d'une nouvelle source de données
(FINRA Reg SHO) qui a révélé un bug de format de données corrigé
avant tout calcul de signal.

## Méthode

Relecture des résultats déjà committés (`results/nonml_*_result.md`,
`*_audit.md`, `*_pass_validation_battery.md`) et du backlog
(`NONML_STRATEGY_BACKLOG.md`, entrées #363-#367) — pas de recalcul,
pas de nouvelle exécution de script.

## Question posée (fixée ici, avant rédaction)

1. Bilan chiffré complet de l'arc #363-367 : combien de PASS niveau 1,
   quels canaux/sous-méthodes fermés, quels enseignements
   méthodologiques.
2. Bilan complet de la famille des portes combinées macro-externes,
   désormais close : quel est le plafond Règle 9 observé et pourquoi
   ne progresse-t-il plus au-delà de 3/5 malgré 7 constructions ?
3. Bilan de la découverte FINRA Reg SHO (short volume) : la source
   est-elle réutilisable, et à quelles conditions ?
4. État global du backlog après 367 hypothèses testées : quelles
   voies restent réellement ouvertes ?

## Sortie

`results/nonml_synthese_backlog_consolidee_v14.md`.
