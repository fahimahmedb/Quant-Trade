# Étape 4 — Analyse par circonscription, niveau PARTI (LFI explicite)

## 0. Pourquoi cette étape, et pourquoi au niveau parti

Deux exigences : (1) **descendre au niveau parti** — LFI (Mélenchon) doit apparaître **explicitement**, pas fondu dans un bloc « NFP / Union de la gauche » ; (2) savoir si la **maille circonscription aide** le modèle.

Constat de données : les résultats **législatifs** officiels codent la gauche en bloc « UG » (en 2024, 544 candidats « Union de la gauche » contre seulement **3** codés « FI »). Impossible d'y isoler LFI. On utilise donc la **présidentielle 2022 par circonscription**, où chaque candidat — donc chaque parti — est distinct : Mélenchon = **LFI**, Hidalgo = PS, Jadot = EELV, séparés.

**Données réelles** (577 circonscriptions, source ministère de l'Intérieur / data.gouv.fr). Contrôle de parsing — l'agrégat national reconstitué colle au résultat officiel :

| Parti | Part reconstituée | Officiel |
|---|---|---|
| Macron (Ensemble) | 27.85 % | 27.85 % |
| Le Pen (RN) | 23.15 % | 23.15 % |
| Mélenchon (LFI) | 21.95 % | 21.95 % |
| Zemmour (Reconquête) | 7.07 % | 7.07 % |
| Pécresse (LR) | 4.78 % | 4.78 % |
| Jadot (Écologistes) | 4.63 % | 4.63 % |
| Lassalle (Résistons) | 3.13 % | 3.13 % |
| Roussel (PCF) | 2.28 % | 2.28 % |
| Dupont-Aignan (DLF) | 2.06 % | 2.06 % |
| Hidalgo (PS) | 1.75 % | 1.75 % |
| Poutou (NPA) | 0.77 % | 0.77 % |
| Arthaud (LO) | 0.56 % | 0.56 % |

## 1. Ce que le national CACHE : la carte des leaders

Nationalement, l'ordre est ENS > RN > LFI. Mais **par circonscription**, le premier change du tout au tout :

| Parti | Nb de circonscriptions où il arrive EN TÊTE |
|---|---|
| Macron (Ensemble) | **267** / 577 |
| Le Pen (RN) | **205** / 577 |
| Mélenchon (LFI) | **105** / 577 |

→ **LFI arrive en tête dans 105 circonscriptions** et figure dans le **duo de tête de 260** d'entre elles. Le cadrage national « Macron vs Le Pen » efface complètement ce fait. Duos de tête les plus fréquents :

| Duo de tête | Nb de circonscriptions |
|---|---|
| ENS + RN | 312 |
| ENS + LFI | 209 |
| LFI + RN | 51 |
| ENS + REC | 3 |
| ENS + RES | 1 |

## 2. Hétérogénéité spatiale (le national = 1 chiffre, la circo révèle l'étendue)

| Parti | Moyenne | Min circo | Max circo | Écart-type |
|---|---|---|---|---|
| Mélenchon (LFI) | 22.9 % | 9.3 % | 61.6 % | 9.5 |
| Le Pen (RN) | 22.8 % | 2.6 % | 47.8 % | 8.8 |
| Macron (Ensemble) | 27.6 % | 12.0 % | 51.0 % | 6.2 |
| Pécresse (LR) | 4.8 % | 0.9 % | 25.3 % | 1.8 |
| Jadot (Écologistes) | 4.5 % | 0.8 % | 11.1 % | 1.8 |

*LFI va de **9.3 %** à **61.6 %** selon la circonscription : un seul chiffre national (≈ 22–23 %) masque une géographie immense (métropoles vs zones rurales).*

## 3. « Est-ce que ça aide le modèle ? » — test OOS

Question testable : la **structure spatiale** (départementale) prédit-elle mieux la part locale d'un parti que la **moyenne nationale plate** (le seul chiffre que produit le modèle national) ? MAE (erreur absolue moyenne, en points) sur les 577 circos, modèle départemental en **leave-one-out** :

| Parti | Baseline national (plat) | Modèle départemental | Gain |
|---|---|---|---|
| Mélenchon (LFI) | 6.81 | **4.55** | −33 % |
| Le Pen (RN) | 7.12 | **4.06** | −43 % |
| Macron (Ensemble) | 4.81 | **2.84** | −41 % |
| Pécresse (LR) | 1.17 | **0.84** | −28 % |
| Jadot (Écologistes) | 1.38 | **0.95** | −31 % |
| Zemmour (Reconquête) | 1.68 | **0.94** | −44 % |

→ **Oui, ça aide — nettement.** La maille départementale/circonscription **divise l'erreur par ~2** vs le chiffre national. La géographie électorale porte un signal réel et fort, que le modèle national ignore par construction.

## 4. Test de SKILL temporel : battre le swing national uniforme (2017 → 2022)

Question de la littérature (Hanretty 2021) : étant donné le résultat NATIONAL d'une élection, comment le **distribuer aux circonscriptions** ? La baseline de référence est le **swing national uniforme** (appliquer le même Δ national partout). Un modèle de circonscription n'a de valeur que s'il la bat. On prédit les parts 2022 par circo à partir de 2017 (données réelles des deux années, 566 circos communes), en leave-one-out :

| Parti | Persistance (=2017) | Swing national uniforme | Régression locale | Skill ? |
|---|---|---|---|---|
| Mélenchon (LFI) | 4.02 | 4.23 | **3.69** | ✅ bat le swing |
| Le Pen (RN) | 2.44 | 1.87 | **1.86** | ✅ bat le swing |
| Macron (Ensemble) | 4.62 | 3.28 | **3.20** | ✅ bat le swing |
| Pécresse (LR) | 15.03 | 3.32 | **0.66** | ✅ bat le swing |
| Hidalgo (PS) | 4.72 | 1.42 | **0.34** | ✅ bat le swing |
| Dupont-Aignan (DLF) | 2.60 | 0.81 | **0.29** | ✅ bat le swing |
| Lassalle (Résistons) | 1.87 | 0.79 | **0.50** | ✅ bat le swing |
| Arthaud (LO) | 0.11 | 0.10 | **0.07** | ✅ bat le swing |
| Poutou (NPA) | 0.36 | 0.16 | **0.09** | ✅ bat le swing |

**Moyenne (9 partis) — MAE en points** : persistance 3.97 → swing uniforme 1.78 → **régression locale 1.19**. La régression de circonscription bat le swing uniforme pour **tous** les partis.

*Cas LFI, révélateur : le swing uniforme (4.23) fait même **pire** que la persistance (4.02) — la poussée de Mélenchon 2017→2022 fut **géographiquement inégale**, donc mal rendue par un Δ national uniforme ; seule la régression locale (3.69) la capture. C'est précisément l'argument de la régression de Dirichlet compositionnelle.*

*Cadre honnête : ce test mesure la skill de **downscaling** (répartir un résultat national connu/prévu vers les circos), pas la prévision du national lui-même — qui reste le rôle de P1–P6 (ou de sondages). Les deux baselines utilisent le même agrégat national ; seule la répartition diffère.*

## 5. Verdict honnête : ce que la circonscription apporte (et n'apporte pas)

**Ce que ça N'apporte PAS** : le chiffre **national** (part R1, issue R2). Agréger les circos **reproduit exactement** le national — aucun gain sur la grandeur que prédisent P1–P6.

**Ce que ça apporte vraiment** (nouvelles capacités, hors de portée du modèle national) :

- **Granularité parti** : LFI, PS, EELV, PCF séparés — la demande initiale. On voit que LFI est un acteur de 1er plan territorial (tête dans 105 circos), noyé dans tout bloc « NFP ».
- **Résolution spatiale à signal réel** : erreur locale divisée par ~2 vs le national. Base d'une projection en **sièges** (législatives) ou d'un scénario de **report** entre deux tours par circonscription.
- **Substrat pour 2027** : appliquer un swing national à cette carte réelle 2022 donne une projection territoriale/sièges — capacité que P6 (national) n'a pas.

**Skill temporel démontrée** (§4) : sur 2017→2022, la régression de circonscription **bat le swing national uniforme** pour les 9 partis appariés (MAE moyenne 1.19 vs 1.78), LFI compris. Ce n'est plus seulement du signal spatial statique : c'est une skill de **downscaling** inter-élections réelle.

**Limites restantes** : deux élections seulement (2017, 2022) ; skill de *downscaling* (le national doit être connu/prévu ailleurs) et non de prévision du national ; régression 1D par parti (une vraie Dirichlet compositionnelle multipartis + covariables socio-éco par circonscription ferait mieux). Le 2017 est provisoire (~9h30) et couvre 566 circos.
