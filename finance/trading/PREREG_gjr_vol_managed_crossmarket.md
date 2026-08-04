# Pré-enregistrement — Généralisation du portefeuille volatility-managed GJR-t (#165) à 3 marchés indépendants (S&P 500, Russell 2000, DAX)

**Committé AVANT tout calcul.** Cycle #166 du backlog non-ML (ligne "à faire"
suivante après le #165). Sous la **Règle 9** et la **Règle 10** de
`PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Pourquoi ce cycle teste DEUX questions à la fois, explicitement séparées

Le #165 (`PREREG_volatility_managed_portfolio_gjr.md`) a délibérément limité
son périmètre au NDX, seul marché où le GJR-GARCH(1,1)-t avait déjà passé le
test SPA de Hansen à l'Étape C (`results/etape_C_ndx_40ans.md`,
`t_SPA=6,07, p=0,0000` h=1). La ligne #166 du backlog propose explicitement
de généraliser — mais le moteur GJR-t **n'a jamais été validé au SPA** sur
S&P 500, Russell 2000 ou DAX. Ce cycle teste donc **conjointement** :

- **Q1 (prévision)** : le GJR-t bat-il le benchmark GARCH-n et passe-t-il le
  SPA famille entière sur CE marché ? (ré-exécution de l'Étape C, pas de
  nouveau modèle, mêmes specs `ARCH_SPECS`.)
- **Q2 (mécanisme)** : SI ET SEULEMENT SI Q1 est validé sur ce marché, le
  portefeuille volatility-managed (§5, paramètres IDENTIQUES au #165, aucun
  retuning par marché) bat-il Buy & Hold en Sharpe ET rendement ?

**Séquencement pré-engagé, non négociable** : Q2 n'est testé que sur les
marchés où Q1 est validé. Un marché où Q1 échoue est rapporté comme tel et
Q2 n'est PAS exécuté sur ce marché (exécuter le mécanisme sur une prévision
non validée mélangerait les deux questions, exactement ce que le #165 avait
refusé de faire pour NDX vs les 3 autres marchés).

## 2. Marchés et échantillons (figés, OHLC déjà en local)

| Marché | Fichier | Séances (approx.) |
|---|---|---|
| S&P 500 | `data/sp500_daily.txt` | ~14252 |
| Russell 2000 | `data/russell2000_daily.txt` | ~9782 |
| DAX | `data/dax_daily.txt` | ~6777 |

Aucun nouveau fetch réseau. `REFIT_EVERY=21` (convention `CLAUDE.md` pour les
historiques longs, déjà utilisée par le #165 sur NDX).

## 3. Étape C — ré-exécution SPA (Q1), aucune modification de la logique

Réutilisation stricte de `scripts/run_etape_c.py` (Règle 7 : aucune
réimplémentation). Pour chaque marché :
`REFIT_EVERY=21 python3 scripts/run_etape_c.py data/<marché>.txt results/etape_C_<marché>.md`.

**Critère Q1 (figé)** : GJR-t est "validé" sur ce marché si et seulement si
(a) il bat le benchmark GARCH-n en QLIKE au test Diebold-Mariano à h=1
(p<0,05) **ET** (b) le test SPA famille entière désigne GJR-t ou GJR-skewt
comme meilleur modèle avec p<0,05 à h=1. Ce sont exactement les deux
critères déjà utilisés pour valider GJR-t sur NDX (Étape C).

## 4. Étape D/mécanisme (Q2) — paramètres IDENTIQUES au #165, aucun retuning par marché

```
position(t) = clip( 20% / vol_prévue_GJR-t(t) , 0.0 , 2.0 )
```

TARGET_VOL=20%, CAP=2.0x, T0=750, REFIT_EVERY=21, coûts 5 bps — **valeurs
copiées du #165 sans modification**, y compris sur les marchés où elles
n'ont jamais été calibrées : le but explicite de ce cycle est de tester la
**généralisation sans retuning**, pas d'optimiser marché par marché (un
retuning par marché serait un essai caché, Règle 2). Rebalancement
quotidien. Rémunération Règle 10 : 0 % cash, 0 % financement (identique
au #165, pour rester comparable).

## 5. Critère de succès (RENFORCÉ, par marché, sur la fenêtre OOS t≥750)

Pour chaque marché où Q1 est validé :
> **PASS si et seulement si** `Sharpe(volatility-managed) > Sharpe(Buy&Hold)`
> **ET** `rendement total > rendement total(Buy&Hold)`, net de coûts 5 bps.

**n_trials = 3** pour ce cycle (un essai par marché, même mécanisme, aucun
balayage de paramètre) — s'ajoute au compteur cumulé du backlog, ne le
remplace pas. Verdict global du cycle : rapporté marché par marché, PAS agrégé
en un seul chiffre (3 marchés indépendants avec des dynamiques différentes).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. GJR-t peut ne pas passer le SPA sur un ou plusieurs de ces 3 marchés
   (moins de données que NDX pour Russell 2000/DAX, régimes de vol différents)
   — dans ce cas Q2 n'est pas testé sur ce marché, ce n'est pas un FAIL du
   mécanisme mais une non-applicabilité de Q1.
2. Même si Q1 passe, les paramètres 20%/2.0x ont été calibrés implicitement
   sur NDX (via #43/#46) et pourraient ne pas transférer — un FAIL de Q2 sur
   un marché où Q1 passe serait informatif (le mécanisme n'est pas
   universel), pas retesté avec d'autres paramètres dans ce cycle.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
