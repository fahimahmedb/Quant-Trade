# Pré-enregistrement — Décomposition portage vs effet-prix du gain du #134

**Committé AVANT tout calcul.** Cycle #142 du backlog non-ML. **Analyse
de décomposition du #134 (PAS un nouveau candidat indépendant, pas de
batterie Règle 9 séparée)** — répond à la question soulevée par le
#141 : un proxy 3 mois (quasi sans effet-prix, duration~0,25 an) a
obtenu un gain presque identique au proxy 10 ans du #134
(Sharpe +0,74 vs +0,77, MDD -55,9% vs -50,9%).

## Hypothèse

Le rendement obligataire du #134 a DEUX composantes dans la formule de
duration modifiée : le PORTAGE (`y_lag/252`, le taux d'intérêt couru
chaque jour, indépendant des mouvements de taux) et l'EFFET-PRIX
(`-D_mod*(y-y_lag)`, la variation de valeur de l'obligation quand le
taux bouge — c'est le canal "flight to quality" qui devrait s'activer
pendant les chocs de vol). Hypothèse a priori, motivée par le résultat
du #141 : le PORTAGE SEUL explique l'essentiel du gain du #134, pas
l'effet-prix.

## Définition (fixée ici, avant tout résultat)

- Position équity : IDENTIQUE au #134 (#115, strictement inchangée).
- **Proxy "portage seul"** : `r_bond_carry(t) = y_lag(t)/252` (retire
  purement et simplement le terme `-D_mod*(y-y_lag)` de la formule
  déjà committée du #134 — même série DGS10, même décalage causal,
  AUCUN paramètre nouveau).
- `r_combiné_carry(t) = pos_eq(t)*r_NDX(t) + (1-pos_eq(t))*r_bond_carry(t)`.
- Comparaison à TROIS points (pas de sélection du "meilleur" après
  coup) : Buy&Hold, #134 complet (portage+prix, déjà committé), et ce
  nouveau proxy portage-seul.
- Coûts : 5 bps par unité de turnover (identique).

## Ce que ce cycle NE fait PAS

N'est pas un nouveau candidat indépendant soumis à sa propre Règle 9 —
une décomposition analytique du mécanisme déjà validé du #134. Ne
change AUCUN verdict Règle 9 déjà rendu.

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_carry_price_decomposition.py`. Aucune
nouvelle donnée (recalcul sur DGS10 et #115 déjà committés).
