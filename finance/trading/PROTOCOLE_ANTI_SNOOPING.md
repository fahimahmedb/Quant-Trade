# Protocole anti-snooping — règles strictes, applicables à tout travail futur

Ce document codifie des règles **obligatoires** pour toute analyse quantitative
du projet (ML ou non), déclenchées par les failles concrètes trouvées lors de
l'audit adversarial du 27/07/2026 (`results/ADVERSARIAL_AUDIT_v2.md`). Chaque
règle cite l'erreur réelle qui l'a motivée — ce ne sont pas des principes
abstraits, ce sont des corrections de bugs déjà commis dans ce repo.

Ces règles s'ajoutent à la discipline déjà en vigueur (CLAUDE.md : univers figé
a priori, N_essais compté, DSR/SPA, R² interdit) — elles ne la remplacent pas.

---

## 1. Pré-enregistrement obligatoire

Toute grille de paramètres ou univers de variantes doit être **figé dans un
fichier committé AVANT que le premier résultat ne soit vu**. Aucune valeur
ajoutée, retirée ou modifiée après avoir observé un résultat, même partiel.

*Déjà la pratique côté ML (`scripts/iterations/iterN.py`) — cette règle
l'étend explicitement à tout script `run_etape_*.py` et à tout futur travail
hors ML (statistiques, séries temporelles, etc.).*

## 2. N_trials du DSR = taille réelle de la famille testée

Le nombre d'essais utilisé dans le calcul du Deflated Sharpe Ratio (`dsr()`,
`finance/src/prediction.py`) doit **toujours** correspondre au nombre réel de
variantes évaluées avant la sélection de la "gagnante" — **jamais réduit à 1**
sous prétexte qu'"un seul a été déployé au final".

**Exemple canonique de la violation** (trouvé le 27/07/2026) : l'audit du
24/07/2026 a affirmé `DSR: 1.000 (no trials inflation; only 1 variant selected
for deployment)` pour la combinaison cap=2,0×/coupe=90e — alors que ce
combo provenait d'une grille de **12 combinaisons** testées
(`run_etape_d_optimize.py`, avant le fix `ee8a2fd`). "Un seul déployé" décrit
CE QUI SE PASSE TOUJOURS après une sélection multi-tests — ce n'est jamais une
justification pour ignorer l'inflation. Le DSR correct doit utiliser
`n_trials=12`.

**Règle pratique** : si un script fait un grid-search de N combinaisons puis
choisit la meilleure, le rapport doit citer le DSR calculé avec CE `N`, pas
`N=1`. Si le DSR avec le vrai N ne passe plus le seuil (0,95), le verdict doit
changer en conséquence — ne pas re-formuler la méthode de comptage pour éviter
la conclusion désagréable.

## 3. "Cross-marché" = marchés génétiquement indépendants

Une validation croisée n'est significative que si elle porte sur des marchés
dont les moteurs économiques sont réellement distincts. Composite (NASDAQ
large) et NDX-100 (100 plus grosses valeurs du même Composite) **ne comptent
PAS** comme deux marchés indépendants — même macro-facteurs, même
composition très recouvrante.

**Marchés considérés indépendants pour ce projet** : Russell 2000
(small-caps US), S&P 500 (marché large US différent de NASDAQ), DAX
(Allemagne — devise et cycle économique distincts). Fichiers déjà présents
dans `data/` (`russell2000_daily.txt`, `sp500_daily.txt`, `dax_daily.txt`).

**Règle pratique** : toute déclaration "validé cross-marché" doit citer au
moins un de ces trois marchés (ou un marché tout aussi distinct), jamais deux
variantes du même indice sous-jacent.

## 4. Aucun auto-audit comme validation finale

Un audit produit par la même lignée d'agents/session que celle qui a construit
la stratégie ne constitue **jamais** une validation finale suffisante — conflit
d'intérêt de relecture inhérent. Toute déclaration "approuvé pour
déploiement" ou "prêt pour le paper trading" nécessite un passage adversarial
qui **recalcule depuis les données brutes** (pas une relecture qui fait
confiance à des tableaux déjà produits).

**Exemple canonique** : l'audit du 24/07/2026 (`AUDIT_CANONICAL_FRAMEWORK_
FINAL.md`) synthétisait des tableaux déjà calculés sans aucune ré-exécution
indépendante — il n'a donc pas détecté que le fichier de résultats qu'il
citait (`etape_D_overlay_optimized.md`) était **obsolète** (produit avant un
correctif du 15/07/2026 qui avait déjà réduit la grille de 12 à 1 combo), ni
que le pipeline entier (`run_etape_a/b/c/d*.py`) était **cassé** depuis la
réorganisation du repo du 25/07/2026 (chemin d'import erroné,
`ModuleNotFoundError` immédiat) — un problème qu'une seule tentative
d'exécution aurait révélé instantanément.

## 5. Un test différé bloque le verdict global

Une vérification explicitement notée "non exécutée" ou "différée" (ex.
"Not executed (tokens)") ne peut **jamais** être absorbée silencieusement
dans un verdict global "PASS" ou "READY". Le rapport doit afficher un statut
distinct (`PENDING`) pour cette dimension et NE PAS inclure la conclusion
globale tant qu'elle n'est pas résolue.

## 6. Traçabilité totale

Chaque statistique citée dans un rapport doit pointer vers la commande, le
script et — idéalement — la ligne exacte qui l'a produite. Un chiffre sans
source vérifiable ne doit pas apparaître dans un document de décision.

## 7. Vérification opérationnelle avant tout audit statistique

Avant même de discuter de DSR ou de SPA, vérifier que le code **s'exécute
réellement** de bout en bout (import, chargement des données, écriture du
rapport). Ce n'est pas un détail — un pipeline cassé invalide silencieusement
toute conclusion qui en dépend, même si les résultats *déjà écrits sur disque*
semblent cohérents.

## 8. Verrou temporel + validation prospective avant capital réel

(Déjà discuté en conversation, formalisé ici.) Avant tout déploiement réel :
- Réserver une tranche de données jamais vue par aucun essai (les derniers
  6-12 mois), ouverte seulement après qu'un candidat ait déjà passé les
  critères sur design/test.
- Validation prospective (paper trading réel) d'au moins 3-6 mois sur la
  définition figée, sans aucune modification en cours de route.
- Si le prospectif déçoit : le modèle est abandonné, jamais retouché puis
  re-testé sur la même fenêtre (ce serait à nouveau du data snooping).

## 9. Batterie de validation renforcée pour tout PASS du backlog non-ML
   (ajoutée le 29/07/2026, suite à la validation SPA/DSR + audit adversarial
   de la famille des 13 overlays vol-targeting — `results/nonml_backlog_
   spa_dsr_validation.md` et `..._audit.md` — qui a montré que des PASS
   individuels honnêtes (n_trials=1 chacun) ne survivaient PAS à une
   correction jointe pour essais multiples : SPA p=0,19, DSR=0,89<0,95,
   meilleur membre instable d'une sous-période à l'autre. Demande explicite
   utilisateur : appliquer systématiquement cette rigueur à CHAQUE futur PASS,
   pas seulement à une famille homogène ex post, pour éviter les "fausses
   joies".)

Un résultat individuel PASS (Sharpe ET rendement > référence, n_trials=1,
règle renforcée habituelle) n'est **jamais** un verdict final. Avant de le
déclarer validé, `scripts/nonml_pass_validation_battery.py <nom>` doit
tourner et passer TOUS les contrôles suivants :

a. **Stress de coûts** : le PASS doit tenir à 3x et 5x le coût
   pré-enregistré (5 bps → 15 bps et 25 bps), pas seulement au coût nominal.
b. **Stress de crise** : sur les fenêtres 2000-2002, 2007-2009, 02-04/2020,
   2022 (quand couvertes par l'historique dispo), le MDD de l'overlay ne
   doit pas être PIRE que celui de Buy&Hold sur la même fenêtre — un
   mécanisme qui amplifie les pertes en crash est disqualifié même s'il
   gagne en moyenne.
c. **Stabilité temporelle** : découpage en folds non chevauchants + embargo
   5j (analogue au walk-forward d'Étape B, adapté puisqu'aucun paramètre
   n'est ajusté sur un train set ici — voir note méthodologique dans
   `results/nonml_backlog_spa_dsr_validation_audit.md`). Le candidat doit
   battre le benchmark sur une MAJORITÉ des folds, pas seulement en moyenne
   pleine période.
d. **SPA à 1 candidat** contre le benchmark (`spa_test`, bootstrap
   stationnaire) — teste CE candidat spécifiquement, distinct du SPA
   famille-entière (qui reste le test le plus sévère dès qu'un groupe de
   PASS structurellement apparentés s'accumule, comme pour la famille
   vol-targeting).
e. **DSR avec `n_trials` = nombre total d'hypothèses testées dans le
   backlog à cette date** (lu automatiquement dans
   `NONML_STRATEGY_BACKLOG.md`, ligne "X PASS sur Y hypothèses testées"),
   **jamais 1** — extension directe de la Règle 2 au niveau du backlog
   entier plutôt qu'à une seule grille locale. `var_trials` estimé à partir
   des Sharpe déjà extractibles de l'historique du backlog.

**Seulement si TOUS les contrôles a-e tiennent** : notifier l'utilisateur
via le bot Telegram (`scripts/notify_telegram.py`) — CE résultat mérite une
alerte immédiate, contrairement aux rapports périodiques de routine — PUIS,
seulement après cette notification, lancer un audit adversarial fin
(recalcul indépendant par seconde implémentation, test anti-lookahead par
mutation, calibration des outils sur données synthétiques sans edge — même
gabarit que `nonml_backlog_spa_dsr_validation_audit.py`) pour chercher
activement les failles restantes.

**Si l'audit révèle un bug de code** (pas seulement un résultat
défavorable) : corriger le bug ET RELANCER tous les tests de cette
batterie sur ce PASS avant toute nouvelle déclaration de statut — ne
jamais laisser un verdict PASS reposer sur un calcul dont un bug a déjà
été trouvé ailleurs dans la même batterie.

---

## 10. Rémunération explicite de la fraction "hors-marché" des mécanismes défensifs
    (ajoutée le 30/07/2026, suite au cycle #142 du backlog non-ML — la
    décomposition du meilleur candidat du backlog (#134, diversification
    obligataire) a montré que 86-89% de son gain venait d'une correction
    implicite d'une hypothèse de backtest irréaliste (0% de taux sans
    risque sur la fraction "hors-marché" du mécanisme défensif sous-jacent
    #115), pas d'un edge de couverture actions/obligations authentique.
    Le cycle #146 a ensuite montré que cette correction ne sauve PAS un
    signal structurellement mauvais et ne s'applique pas à la majorité des
    overlays du backlog, construits pour rester ≥1,0x en permanence —
    l'effet est réel mais spécifique, pas une variable universelle à
    exploiter systématiquement.)

Tout NOUVEAU mécanisme qui réduit l'exposition sous 1,0x (donc détient
implicitement une fraction du capital "hors-marché") doit être
pré-enregistré avec une hypothèse EXPLICITE sur la rémunération de
cette fraction :

a. Soit 0% (cash), hypothèse à justifier explicitement dans le PREREG
   si retenue — ce n'est plus une valeur implicite non déclarée.
b. Soit un proxy de taux sans risque réaliste (ex. `data/dgs3mo_daily.csv`,
   `data/dgs10_daily.csv`, déjà disponibles), avec la maturité choisie
   et la formule de calcul du rendement (ex. duration modifiée) fixées
   AVANT tout calcul.

Si un mécanisme défensif rapporté avec l'hypothèse 0% s'avère PASS ou
proche du seuil de la Règle 9, la décomposition portage/effet-prix
(méthode du #142 : construire un proxy "portage seul" en retirant le
terme d'effet-prix, comparer sa contribution à celle du mécanisme
complet) doit être appliquée AVANT de communiquer le résultat comme une
découverte de diversification ou de couverture — pour ne jamais
confondre une correction de biais de backtest avec un edge authentique.

**Règle pratique** : cette règle ne s'applique PAS rétroactivement à
tous les mécanismes déjà committés (une nouvelle campagne systématique
n'est pas justifiée, cf. #146) — elle s'applique aux mécanismes
FUTURS. Le #134 (backlog non-ML, `finance/trading/`) reste la
référence documentée du phénomène et de sa décomposition.

---

## Application immédiate

Ces règles s'appliquent rétroactivement à la relecture des Étapes C et D
(voir `results/ADVERSARIAL_AUDIT_v2.md`) et prospectivement à toute
Phase 3 (optimisation) qui suivra.
