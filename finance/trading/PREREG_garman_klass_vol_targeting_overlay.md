# Pré-enregistrement — Overlay de vol-targeting, estimateur Garman-Klass (1980)

**Committé AVANT tout calcul.** Cycle #215 du backlog non-ML. Le backlog
étant épuisé de lignes "à faire" (214 hypothèses testées, dont les 7
dérivés originaux du #46 désormais tous couverts par la batterie Règle 9
aux #207-#214), ce cycle introduit une NOUVELLE idée dans la même famille
mécanique (mécanisme fondateur #46, vol-targeting continu cible 20%),
avec un ESTIMATEUR de volatilité encore jamais testé.

## Hypothèse

Le #46 utilise l'écart-type close-to-close, le #50 l'estimateur
range-based de Parkinson (haut/bas intra-séance uniquement, ignore le
mouvement ouverture→clôture par construction — limite documentée
explicitement dans `data_loader.py::parkinson_var_pct`). L'estimateur de
**Garman & Klass (1980)** combine le range HAUT/BAS (comme Parkinson) ET
le mouvement OUVERTURE→CLÔTURE intra-séance (que Parkinson ignore),
utilisant ainsi l'OHLC complet — plus efficient statistiquement que
Parkinson dans la littérature originale. Hypothèse : cet estimateur, en
captant une composante de variance supplémentaire (drift intra-séance)
sans requérir de nouvelle donnée (OHLC déjà en local), produit un
mécanisme de vol-targeting qui bat Buy & Hold en Sharpe ET en rendement
total net de coûts, comme les #46/#50 déjà validés en PASS niveau 1.

Formule (par séance, en %²) :
`GK_var = 0.5*(ln(H/L))^2 - (2*ln(2)-1)*(ln(C/O))^2`, moyenne roulante sur
`VOL_WINDOW=20` séances (paramètre réutilisé à l'identique des #46/#50,
Règle 7 — pas de nouveau réglage), annualisée par `sqrt(252)`.

## Univers et période

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — mêmes
fichiers `data/*.txt` déjà en local, aucun nouveau fetch.

## Mécanisme (identique aux #46/#50, seul l'estimateur change)

`Position(t) = clip(20% / vol_GarmanKlass_20j(t-1), 0.0, 2.0x)` — CAP=2.0
et TARGET_VOL_ANNUAL=0.20 réutilisés à l'identique du #46 (Règle 7,
pas de recherche de paramètre). Coût 5 bps aller-retour, comme tout le
backlog.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#80 et à toute hypothèse depuis le 28/07/2026).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme Parkinson (#50), Garman-Klass ne capture pas le saut entre la
   clôture de la veille et l'ouverture du jour (composante overnight) —
   seul le mouvement intra-séance (H/L et O/C du MÊME jour) est utilisé.
   Le biais de sous-estimation de la vol réelle pourrait être similaire
   ou différent de celui du #50 selon l'ampleur relative des deux
   composantes.
2. Si l'estimateur GK est très proche numériquement de celui de Parkinson
   (les deux dérivés du même OHLC), le résultat pourrait être quasi
   identique au #50 (déjà PASS 5/5 niveau 1, mais Règle 9 4/5) plutôt que
   d'apporter une information réellement nouvelle.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_garman_klass_vol_targeting_overlay_backtest.py` (nouveau).
Fonction `garman_klass_var_pct` ajoutée à `data_loader.py` (aux côtés de
`parkinson_var_pct`, même convention de sortie en %², alignée sur
`df["date"].iloc[1:]`). Vérification via `nonml_anti_cheat_check.py
garman_klass_vol_targeting_overlay`.
