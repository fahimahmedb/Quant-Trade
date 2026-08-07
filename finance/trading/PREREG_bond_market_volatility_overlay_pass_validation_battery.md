# Pré-enregistrement — Batterie Règle 9 sur le #357 (volatilité obligataire MOVE)

**Committé AVANT tout calcul.** Cycle #358 du backlog non-ML.

## Contexte et motivation

Le #357 (volatilité implicite obligataire MOVE, PASS 4/5, première
catégorie "volatilité implicite" à atteindre le seuil renforcé dans ce
backlog — la famille VIX-dérivés equity restait à 0/4) n'a **jamais**
été soumis à la batterie de validation renforcée (Règle 9). Suite
directe et naturelle du cycle précédent, dans la continuité de la
pratique déjà établie (#200→#201, #335→#336, #338→#340, #344→#345,
#350→#351).

## Adaptation technique

Le script `nonml_bond_market_volatility_overlay_backtest.py` sauvegarde
déjà le couple `(pos, r_asset, dates, cost_bps)` sur le marché NDX au
format attendu par le script générique
`nonml_pass_validation_battery.py` (convention `.npz`, marché de
référence NDX, comme tous les cycles récents) — **aucune modification
nécessaire**.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #357.

## Critère de succès (Règle 9, identique aux cycles #111-#357)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour = 362) doivent TOUS passer
pour un PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel
quel, sans retuning.

## Risque déclaré à l'avance (spécifique à ce candidat)

**Prédiction explicite** (déclarée avant calcul, testable) :

1. **Couverture de crise attendue LARGE** — contrairement au Bitcoin
   (#344/#345, historique 2015+, seulement COVID+2022 couverts) ou au
   sleeve dollar-neutre (#349/#350, univers PIT ~2015+), la série MOVE
   couvre le NDX depuis 2002+ sur ce marché de référence — le
   resserrement 2022 et potentiellement une partie de la crise
   financière 2008 (selon la disponibilité effective de l'historique
   NDX/MOVE combiné) devraient être couverts, contrairement aux
   candidats crypto/PIT récents.
2. **Design purement défensif (jamais de levier, CUT=0,5x) attendu
   robuste au stress de coûts** — cohérent avec le schéma observé sur
   la quasi-totalité des candidats macro-externes défensifs déjà
   testés à la Règle 9 (coûts rarement le point de rupture).
3. **DSR à n_trials=362 attendu en échec, comme TOUS les candidats
   testés à ce jour dans ce backlog** (confirmé empiriquement par
   l'investigation Piste A/C complète des cycles #349-#351 : même la
   construction la plus favorable jamais testée — portefeuille
   dollar-neutre redimensionné par sa vol, Sharpe +0,61 — échoue le
   DSR par un ordre de grandeur, 0,04 vs 0,95 requis). Le Sharpe brut
   du #357 (NDX +0,74) est notable mais reste loin des ~1,7-2,0
   requis par la théorie à ce niveau de n_trials. **Le sujet DSR est
   considéré clos empiriquement depuis la synthèse v12** — ce contrôle
   est exécuté pour complétude de la batterie (Règle 9 systématique
   sur tout PASS niveau 1), pas pour rouvrir cette question.

**Score anticipé, non garanti** : compte tenu de la solidité du
niveau 1 (4/5, Sharpe net partout, MDD amélioré partout) et de la
couverture de crise potentiellement la plus large de tout candidat
Règle 9 récent, un score 2-3/5 est plausible (coûts+crise+stabilité
OK, SPA/DSR probables points de rupture, cohérent avec le schéma déjà
observé pour le CPI #338→#340 3/5). Rapporté honnêtement dans tous les
cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #357. Sortie :
`results/nonml_bond_market_volatility_overlay_pass_validation_battery.md`.
