# Pré-enregistrement — Métrique de profil de couverture pour #115 (analyse, pas un nouveau backtest)

**Committé AVANT tout calcul.** Cycle #117 du backlog non-ML. Analyse
méthodologique sur le résultat DÉJÀ committé de #115
(`nonml_defensive_calmar_vol_targeting_overlay`), pas un nouveau
mécanisme, pas de nouvelle donnée.

## Question posée (fixée ici, avant tout calcul)

Le SPA (Hansen) a échoué sur #115 (p=1,0000) malgré le meilleur profil
de robustesse du backlog (stress coûts/crise/stabilité tous OK). Le SPA
est construit pour détecter un edge RÉGULIER dans le temps (moyenne du
différentiel de perte, studentisée par sa variance long terme) — hypothèse
posée ici : le profil de #115 est celui d'une COUVERTURE (petit coût en
période calme, gain important en crise), pas un edge homogène, et c'est
précisément ce type de profil qu'un test conçu pour un edge régulier
pénalise structurellement (variance du différentiel dominée par les
quelques épisodes de crise). Cette analyse teste cette hypothèse
directement, SANS changer le backtest ni chercher un nouveau verdict
PASS/FAIL global.

## Méthode (fixée ici)

1. Reprendre le pnl déjà committé de #115 sur NDX
   (`results/nonml_defensive_calmar_vol_targeting_overlay_pnl.npz`).
2. Partitionner les séances en deux groupes EXACTEMENT comme en Règle
   9b (mêmes 4 fenêtres de crise déjà utilisées, pas de nouvelle
   définition après coup) : "crise" (dot-com 2000-01→2002-12,
   2008 2007-10→2009-03, COVID 2020-02→2020-04, 2022 complet) vs
   "calme" (tout le reste).
3. Calculer séparément, sur chaque groupe : rendement total net,
   Sharpe annualisé, et le différentiel `pnl_overlay - pnl_BH` moyen
   (coût/bénéfice net par séance).
4. Rapporter le ratio "gain moyen par séance de crise" / "coût moyen
   par séance calme" (framing coût d'assurance / prime) — mesure
   descriptive, pas un nouveau test de significativité statistique
   (le SPA reste le test formel de référence, cette analyse ne le
   remplace pas).

## Ce que cette analyse NE fait PAS

Ne change pas le verdict Règle 9 de #115 (reste FAIL, SPA/DSR non
satisfaits). Ne propose pas de nouveau test statistique formel de
substitution au SPA — documente juste, de façon descriptive, POURQUOI
le profil de #115 est mal capté par un test conçu pour un edge régulier.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.
