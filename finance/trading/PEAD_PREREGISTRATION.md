# Pré-enregistrement — Stratégie PEAD (Post-Earnings Announcement Drift)

**Committé AVANT toute exécution du backtest.** L'horodatage git de ce
fichier fait foi de pré-enregistrement (règle #1,
`PROTOCOLE_ANTI_SNOOPING.md`). Toute modification ultérieure de ce
document APRÈS avoir vu un résultat serait elle-même une violation du
protocole qu'il définit.

## Contexte

Recherche précédente (`résultats de recherche web, session du 28/07/2026`) :
PEAD est l'anomalie la plus résistante documentée en finance de marché —
persiste malgré 50+ ans de publication académique et d'arbitrage actif,
attribué aux limites à l'arbitrage (contrainte de vente à découvert,
capacité insuffisante des fonds quant pour absorber tous les cas
individuels). C'est la seule piste actions identifiée dans la recherche du
28/07/2026 avec un niveau de preuve académique jugé solide ET construisible
avec les moyens de ce projet (contrairement au carry obligataire ou aux
style premia multi-actifs, hors budget/infrastructure).

## Univers

**Constituants ACTUELS du NASDAQ-100** (103 tickers au 27/07/2026, récupérés
via `api.nasdaq.com/api/quote/list-type/nasdaq100`).

**Limite assumée et non masquée : biais de survie.** Il n'existe pas de
source gratuite et rapide donnant les constituants POINT-IN-TIME
historiques du NDX-100. Les entreprises retirées de l'indice pour cause de
sous-performance, rachat ou faillite sur la période testée ne sont donc pas
dans l'échantillon. Ce biais tend à surestimer légèrement la performance
d'un panier long-only sur cet univers ; pour un portefeuille long-short
comme PEAD, l'effet est moins direct mais reste réel (les deux jambes,
longue et courte, sont piochées dans un univers de "survivants"). Signalé
ici, pas découvert après coup.

## Période

Événements de résultats du **01/07/2021 au 27/07/2026** (5 ans), alignée
sur la fenêtre du Composite pré-enregistré du reste du projet.

## Source des données

- Surprises de résultats : `api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD`
  (EPS réel, consensus, % de surprise), interrogé jour par jour sur la
  période, filtré à l'univers NDX-100 ci-dessus.
- Prix quotidiens par titre : Yahoo Finance (`query2.finance.yahoo.com`,
  déjà utilisé et validé dans ce projet pour ^BXM/^PUT/^GSPC).

## Définition du signal (fixée ICI, avant tout résultat)

1. Pour chaque date d'annonce dans la période, calcul du % de surprise
   (fourni directement par la source).
2. **Tri en terciles sur la distribution des surprises elles-mêmes**
   (pas sur les rendements ultérieurs — évite tout ajustement du seuil
   au résultat) : tercile supérieur → position LONGUE, tercile inférieur
   → position COURTE, tercile médian → ignoré.
3. **Délai d'entrée** : le portefeuille prend position à la clôture du
   jour de bourse SUIVANT l'annonce (jamais le jour même — l'heure exacte
   avant/après-bourse n'est pas connue via cette source, choix
   conservateur pour exclure tout lookahead).
4. **Durée de détention** : H = 60 séances (~1 trimestre), convention
   académique standard (Bernard & Thomas 1989/1990) — PAS optimisée sur
   nos données.
5. **Pondération** : équipondérée sur toutes les positions ouvertes
   simultanément ; rendement du portefeuille = moyenne(longues) −
   moyenne(courtes), dollar-neutre.
6. **Coûts** : 10 bps aller-retour par position (plus élevé que les 5 bps
   indices utilisés ailleurs dans le projet — actions individuelles =
   spreads plus larges), fixé a priori.

## Critère de succès (pré-enregistré, avant tout résultat)

Le portefeuille long-short net de coûts doit satisfaire **simultanément** :
1. Sharpe annualisé > 0 avec t-stat > 2 sur l'ensemble de la période.
2. Split temporel design (2021-2023) / test (2024-2026) : le Sharpe sur
   le test ne doit pas être dégradé de plus de 50% relatif au design
   (même logique que `scripts/ml_brute_force.py`), ET rester positif.

N_trials = **1** (une seule spécification, aucune grille de seuils/durée
de détention testée). Si le critère échoue, ce chantier est clos pour
cette hypothèse précise — toute variante nécessiterait un nouveau
pré-enregistrement séparé, pas un ajustement de celui-ci après résultat.

## Protocole anti-cheat spécifique à ce chantier

1. Ce fichier est committé AVANT l'exécution de `pead_backtest.py`
   (vérifiable : le commit de ce fichier doit précéder chronologiquement
   le commit des résultats).
2. Aucune modification de ce document après avoir vu un résultat.
3. Test de mutation anti-lookahead automatique sur le calcul de position
   (perturber une surprise future, vérifier que les positions passées ne
   changent pas) — `pead_adversarial_audit.py`.
4. Audit adversarial indépendant : recalcul depuis les données brutes
   téléchargées (pas confiance aux tableaux intermédiaires).
5. Biais de survie documenté ci-dessus, répété dans le rapport final, pas
   dilué.
