# Pré-enregistrement — Synthèse du sous-thread combinaison de signaux de stress (#296-#304)

**Committé AVANT toute rédaction.** Cycle #305 du backlog non-ML.

## Nature de ce cycle

Synthèse, PAS un nouveau backtest — aucune nouvelle donnée, aucun
nouveau calcul. Consolide les 9 cycles #296-#304 de ce backlog, tous
construits sur le MÊME panel de base (défaut carte de crédit #286,
NFCI #291, BAA10Y #199, puis corrélation cross-marché NDX-DAX #193
ajoutée au #304) combiné selon 4 logiques successives (ET, OU,
majorité ≥2/3, sizing continu, majorité élargie ≥3/4), chacune suivie
de sa batterie Règle 9 dédiée.

## Méthode

Relecture des résultats déjà committés (`results/nonml_*_result.md`,
`*_audit.md`, `*_robustness.md`, `*_pass_validation_battery.md`) et du
backlog (`NONML_STRATEGY_BACKLOG.md`, entrées #296-#306) — pas de
recalcul, pas de nouvelle exécution de script.

## Question posée (fixée ici, avant rédaction)

La synthèse doit répondre explicitement à une question opérationnelle
laissée ouverte par la note du #306 : l'amélioration du score Règle 9
observée en passant de 3 à 4 signaux (2/5 → 3/5) justifie-t-elle de
poursuivre l'élargissement à un 5e signal, ou ce sous-thread doit-il
être considéré comme suffisamment exploré ? La réponse doit peser
explicitement le risque de RECHERCHE COMBINATOIRE DÉGUISÉE EN NOUVELLES
HYPOTHÈSES (ajouter des signaux jusqu'à obtenir un score plaisant,
contraire à la discipline anti-snooping) contre le fait que chaque
signal ajouté à ce jour a été individuellement pré-validé (PASS
niveau 1 propre) avant son intégration au panel — pas choisi après
observation du score combiné.

## Sortie

`results/nonml_synthese_combinaison_signaux_stress.md`.
