# Pré-enregistrement — Synthèse consolidée v4 (cycles #156-243)

**Committé AVANT toute rédaction.** Cycle #244 du backlog non-ML. Pas un
nouveau backtest — ce cycle ne teste aucune hypothèse, il consolide 88
cycles déjà exécutés et committés depuis la dernière synthèse (v3, cycle
#156, qui couvrait jusqu'au #155).

## Motivation

Trois propositions ont été faites à la clôture du #241/#243 : un signal
ACF single-lag (risque de redondance avec le VR #217, non tranché), et
une synthèse consolidée. Le volume accumulé depuis la v3 (88 cycles,
dont la totalité de la famille mega-exploration estimateurs/portes de
vol-targeting #215-243, jamais synthétisée) et le schéma de rendements
décroissants observé sur les variantes les plus récentes (FAIL #233,
#236, #239 après une série presque intégralement PASS #215-223)
justifient une consolidation avant de continuer à empiler des variantes
individuelles.

## Méthode

Lecture systématique des 88 lignes de suivi ("X PASS niveau 1 sur Y
hypothèses testées") du #156 au #243, complétée par relecture des
entrées de tableau complètes pour les cycles structurants (bug
d'exécution #166, correction de biais du survivant #161-164, familles
#165-170, #207-214, #215-243). Aucun nouveau calcul, aucune nouvelle
donnée — uniquement une lecture et une rédaction de synthèse honnête,
dans le même esprit que les v1/v2/v3.

## Anti-cheat

Ce fichier committé avant toute rédaction. Sortie :
`results/nonml_synthese_backlog_consolidee_v4.md`. Pas de vérification
anti-cheat automatisée applicable (pas de backtest, convention identique
aux v1/v2/v3).
