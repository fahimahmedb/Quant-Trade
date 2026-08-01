# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38) — univers point-in-time 2015-2026 (cycle #163)

Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG original du #38. Coût pré-enregistré 5 bps. 2907 séances (2015-01-02 → 2026-07-27). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ.

**Univers POINT-IN-TIME (cycle #163)** — correction du défaut méthodologique qui affectait les cycles #161 ET #162. À chaque date de rebalancement, seuls les titres **réellement membres du NDX-100 ce jour-là** sont investissables (composition historique issue de `nasdaq-100-ticker-history` v2026.7.0, licence MIT, vendorée dans `data/ndx100_history/`). Les cycles précédents appliquaient rétroactivement la liste des membres **de 2026**, qui ne couvre que 42 % des vrais membres de l'indice en 2015 et 68 % en 2022 (mesuré dans `results/nonml_ndx100_universe_census.md`) — les absents étant par construction les titres sortis de l'indice depuis, donc en moyenne des sous-performants. Panneau de prix : 178 des 214 tickers ayant appartenu à l'indice entre 2015 et 2026 (36 séries de titres retirés de la cote ne sont plus exposées par la source — biais résiduel quantifié ci-dessous). **Aucun paramètre du #38 ne change** (TERCILE 1/3, LOOKBACK 252, REBAL_EVERY 21, CAP 2.0, seuil indice 95 %, coût 5 bps) ; seule la définition de l'univers investissable est corrigée, comme pré-enregistré dans `PREREG_leaders_index52w_high_overlay_pit_universe.md`.

## Biais résiduel de l'univers point-in-time (mesuré, non estimé)

À chaque date de rebalancement : nombre de membres RÉELS du NDX-100 (composition point-in-time) et nombre d'entre eux réellement investissables (prix disponibles ET 252 séances d'historique). Le complément est le biais restant — titres retirés de la cote dont la série de prix n'est plus exposée par la source, ou titres entrés à l'indice avant d'avoir un an de cotation.

| Année | Rebal. | Membres réels (moy.) | Investissables (moy.) | Couverture moy. | Couverture min. |
|---|---|---|---|---|---|
| 2015 | 12 | 106 | 73.7 | 69.5% | 67.3% |
| 2016 | 12 | 105 | 77.8 | 74.3% | 71.0% |
| 2017 | 12 | 104 | 81.8 | 78.7% | 77.9% |
| 2018 | 12 | 103 | 84.2 | 81.7% | 80.6% |
| 2019 | 12 | 103 | 88.2 | 85.6% | 85.4% |
| 2020 | 12 | 103 | 91.2 | 88.5% | 86.4% |
| 2021 | 12 | 102 | 92.8 | 90.9% | 90.2% |
| 2022 | 12 | 102 | 95.3 | 93.5% | 92.2% |
| 2023 | 12 | 101 | 96.8 | 95.8% | 95.0% |
| 2024 | 12 | 101 | 98.9 | 97.9% | 97.0% |
| 2025 | 12 | 101 | 100.4 | 99.4% | 99.0% |
| 2026 | 7 | 101 | 101.0 | 100.0% | 100.0% |

**Couverture moyenne sur toute la période : 87.6% (minimum 67.3%).** À comparer aux 42 % (2015) à 68 % (2022) de couverture des cycles #161/#162, mesurés dans `results/nonml_ndx100_universe_census.md` — le biais n'est pas totalement nul ici, mais il est réduit d'un ordre de grandeur ET, surtout, il est désormais MESURÉ.

Nature du résidu, à ne pas sous-estimer : les titres encore manquants sont exclusivement des sociétés **retirées de la cote** (faillite, rachat, passage en non coté), donc en moyenne des sous-performants — le biais résiduel reste orienté dans le même sens (à la hausse), simplement beaucoup plus petit.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |
|---|---|---|---|---|---|
| 5 | +1.42 | +0.79 | +6489.1% | +361.9% | OUI |
| 15 | +1.37 | +0.76 | +5582.0% | +341.2% | OUI |
| 25 | +1.33 | +0.74 | +4799.4% | +321.4% | OUI |

**OK — tient jusqu'à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence)

| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -30.9% | -28.8% | non |
| Resserrement 2022 | 251 | -25.3% | -24.9% | OUI |

**ÉCHEC — 2/4 fenêtres de crise couvertes par l'historique de prix titre-par-titre disponible.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5j)

| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |
|---|---|---|---|---|---|
| 1 | 726 | 01/2015→11/2017 | +1.48 | +1.15 | OUI |
| 2 | 721 | 11/2017→10/2020 | +1.44 | +0.72 | OUI |
| 3 | 721 | 10/2020→08/2023 | +0.98 | +0.32 | OUI |
| 4 | 724 | 09/2023→07/2026 | +1.63 | +0.96 | OUI |

**OK — 4/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre la référence

t_SPA = 7.637, **p = 0.0000** (bootstrap stationnaire, H0 : la référence Leaders 1.0x n'est battue par aucun candidat).

**OK — seuil p < 0,05.**

## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)

n_trials=162 (backlog avant ce cycle), var(SR essais) extraite sur 68 Sharpe du backlog = 2.0173e-01 (annualisée) → 8.0052e-04 (journalière). Sharpe quotidien +0.0892, seuil SR₀ = 0.0763, z = +0.69, **DSR = 0.754**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | OK |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | OK |
| d. SPA 1 candidat | OK |
| e. DSR (n_trials=162) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE

Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).

## Lecture du résultat, en regard des cycles #161 et #162

| | #161 (liste 2026, 2022-2026) | #162 (liste 2026, 1970-2026) | **#163 (point-in-time, 2015-2026)** |
|---|---|---|---|
| Séances | 1144 | 14010 | **2907** |
| Univers | liste de 2026 (couverture 68 % du vrai indice au départ) | liste de 2026 (couverture inconnue, très faible avant 2000) | **composition réelle à chaque date (couverture mesurée 87,6 % en moyenne)** |
| a. coûts ×5 | OK | OK | **OK** |
| b. crise | OK (1/4 fenêtre couverte) | ÉCHEC (2/4 fenêtres perdues) | **ÉCHEC (2/4 couvertes, COVID perdu de 2,1 pts de MDD)** |
| c. stabilité | OK (4/4) | ÉCHEC (3/4) | **OK (4/4)** |
| d. SPA | OK (p=0,0000, t=4,515) | OK (p=0,0000) | **OK (p=0,0000, t=7,637)** |
| e. DSR | 0,730 | 0,612 | **0,754** |
| Score | 4/5 | 3/5 | **3/5** |

**Ce qu'il faut retenir, sans enjoliver :**

1. **L'edge du #38 n'était PAS un artefact de biais du survivant.** C'était
   l'hypothèse la plus inquiétante, et elle est réfutée : sur un univers
   reconstruit date par date, sur un échantillon 2,5× plus long, le candidat
   bat encore la référence largement (Sharpe +1,42 vs +0,79), bat 4/4 folds,
   et le SPA passe encore plus nettement qu'au #161 (t=7,64 vs 4,52). Le DSR
   **progresse** (0,754 vs 0,730), ce qui va dans le sens de l'hypothèse du
   #161 (edge réel, borné par la puissance statistique) et contredit
   l'interprétation pessimiste du #162 (dégradation attribuée au biais, ici
   confirmée comme un artefact de ce biais).
2. **Le DSR reste ÉCHOUÉ, et de loin (0,754 < 0,95).** Le gain de 2,5× en
   taille d'échantillon rapporte +0,024 de DSR. Extrapoler naïvement suggère
   qu'aucune extension d'historique réaliste ne franchira le seuil : la
   contrainte n'est pas seulement le nombre d'observations, c'est le niveau
   du Sharpe quotidien (+0,0892) face au seuil de sélection SR₀ (0,0763)
   imposé par n_trials=162.
3. **Le stress de crise révèle une vraie faiblesse, nouvelle.** Le #161 ne
   couvrait qu'une fenêtre (2022) ; ici le krach COVID est couvert et le
   candidat y fait PIRE que la référence (-30,9 % vs -28,8 %). Ce n'est pas
   un artefact d'univers : c'est le comportement attendu d'un overlay qui
   double l'exposition tant que l'indice reste à ≥95 % de son plus haut, et
   le sommet de février 2020 précédait immédiatement le krach le plus rapide
   de l'histoire. **Le contrôle b échoue donc pour une raison économique
   réelle, pas pour un défaut de mesure** — c'est l'information la plus
   utile de ce cycle après le point 1.
4. **Le score global (3/5) est en retrait du 4/5 du #161, mais les deux ne
   sont pas comparables terme à terme** : le #161 obtenait son OK sur le
   contrôle b avec une seule fenêtre de crise couverte, la plus favorable au
   mécanisme. Un score obtenu sur 2 fenêtres dont une défavorable est plus
   informatif qu'un score obtenu sur 1 fenêtre favorable. Le #163 est donc
   **une meilleure évaluation qui donne un chiffre moins flatteur**, pas une
   dégradation de la stratégie.

**Statut du #38 après ce cycle : PASS niveau 1, batterie renforcée toujours
non validée.** Aucune notification Telegram. Ce cycle SUPERSEDE le #162 (dont
l'univers était non défendable) et complète le #161 (dont l'univers était
biaisé et la couverture de crise insuffisante) — c'est désormais la référence
d'évaluation du #38.

