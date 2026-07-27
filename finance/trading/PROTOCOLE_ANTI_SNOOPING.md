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

---

## Application immédiate

Ces règles s'appliquent rétroactivement à la relecture des Étapes C et D
(voir `results/ADVERSARIAL_AUDIT_v2.md`) et prospectivement à toute
Phase 3 (optimisation) qui suivra.
