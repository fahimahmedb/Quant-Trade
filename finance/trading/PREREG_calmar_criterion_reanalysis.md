# Pré-enregistrement — Ré-analyse du critère Calmar sur le résultat Étape D v2 déjà committé

**Committé AVANT tout calcul.** Cycle #119 du backlog non-ML. Ce cycle
N'EST PAS un nouveau backtest, PAS un nouvel essai, PAS une recherche de
paramètres sur Russell 2000/S&P 500/DAX (qui resteraient interdits par
le pré-enregistrement de `run_etape_d_v2.py`, déjà "brûlés" pour toute
nouvelle TENTATIVE de correction de mode d'échec). Il s'agit de
recalculer une métrique DÉTERMINISTE (Calmar = rendement annualisé /
|MDD|) à partir du MÊME calcul déjà exécuté (mêmes paramètres exacts :
CAP=1.0×, coupe 95e percentile, T0=750, REFIT_EVERY=21, GJR-GARCH(1,1)-t)
-- aucun paramètre ne change, aucune nouvelle donnée, aucun nouveau
résultat de marché n'est produit qui n'existait pas déjà implicitement
dans le calcul original (`trading_metrics()` calcule déjà `calmar` en
interne, simplement pas affiché dans le rapport d'origine).

## Question posée (fixée ici, avant tout calcul)

La divergence observée entre #115 (défensif vol réalisée, critère Calmar
simple, PASS 4/5 marchés) et `etape_D_v2_no_leverage.md` (défensif
GJR-GARCH, critère >25%MDD/≥80%rendement, PASS 0/3 sur Russell/S&P/DAX)
vient-elle du CRITÈRE de succès (bar plus stricte en Étape D) ou du
MOTEUR de volatilité (GARCH vs réalisé) ? Recalculer le Calmar (critère
du #115) sur les MÊMES résultats Russell/S&P/DAX déjà committés en
Étape D v2 permet de trancher : si Calmar_overlay > Calmar_BH sur ces
3 marchés malgré l'échec du critère >25%/≥80%, la divergence vient du
CRITÈRE ; sinon elle vient du MOTEUR.

## Méthode (fixée ici)

Ré-exécuter EXACTEMENT `_one_index()` de `run_etape_d_v2.py` (mêmes
paramètres, mêmes données, aucune modification) pour Russell 2000,
S&P 500, DAX, et extraire le champ `calmar` déjà calculé par
`trading_metrics()` (jamais affiché dans le rapport d'origine, pas
recalculé différemment).

## Ce que cette analyse NE fait PAS

Ne relance aucune recherche de paramètres sur ces 3 marchés. Ne change
rien au verdict déjà rendu par `etape_D_v2_no_leverage.md` (0/3 sous son
propre critère, qui reste le verdict officiel de l'Étape D). N'ouvre pas
la porte à une "correction du mode d'échec S&P 500" (toujours interdite
par le pré-enregistrement de `run_etape_d_v2.py`).

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.
