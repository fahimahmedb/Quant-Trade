# Étape P9 — ML par circonscription, statistiquement significatif

## 0. Pourquoi cette étape (retour au plan + significativité)

Le plan initial visait un **ML par circonscription** (« le vrai terrain ML »). Le modèle national (P1–P6) plafonnait à n=11 élections : **rien n'y était significatif**. Ici, la maille circonscription donne **~566 circos × 9 partis = 5094 prédictions hors-échantillon** — assez pour un vrai test de significativité. Partis EXPLICITES (Mélenchon = **LFI**, jamais un bloc).

## 1. Modèle et protocole

- **Cible** : part 2022 de chaque parti dans une circonscription.
- **Entrées** : composition 2017 **complète** de la circo (11 familles) + moyenne départementale du parti (apprise sur le train, sans fuite).
- **Modèle** : Gradient Boosting (200 arbres, prof. 3), **validation croisée 5-fold** — chaque circo prédite hors de son pli.
- **Baselines** : persistance (= 2017) et **swing national uniforme** (2017 + Δ national) — la référence de la littérature (Hanretty 2021).
- **Test** : Wilcoxon apparié sur les erreurs absolues par circo (GB vs swing).

## 2. Résultat : le modèle bat le swing (DOWNSCALING), significativement

⚠️ **Baseline corrigée (audit)** : on compare au **swing PROPORTIONNEL** (part 2017 × ratio national), nettement plus fort que le swing additif — c'est la vraie référence à battre. Le GB la bat quand même, pour les 9 partis.

| Parti | Persist. | Swing additif | **Swing proportionnel** | MAE **GB** | Gain vs prop. | p-value |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) | 4.02 | 4.23 | 3.99 | **1.47** | −63 % | 9.3e-64 ✅ |
| Le Pen (RN) | 2.44 | 1.87 | 1.85 | **1.03** | −44 % | 2.3e-36 ✅ |
| Macron (Ensemble) | 4.62 | 3.28 | 3.49 | **1.35** | −61 % | 2.8e-56 ✅ |
| Pécresse (LR) | 15.03 | 3.32 | 0.66 | **0.47** | −29 % | 8.8e-17 ✅ |
| Hidalgo (PS) | 4.72 | 1.42 | 0.37 | **0.17** | −54 % | 2.8e-39 ✅ |
| Dupont-Aignan (DLF) | 2.60 | 0.81 | 0.31 | **0.18** | −42 % | 1.1e-31 ✅ |
| Lassalle (Résistons) | 1.87 | 0.79 | 0.48 | **0.27** | −45 % | 4.6e-25 ✅ |
| Arthaud (LO) | 0.11 | 0.10 | 0.07 | **0.05** | −29 % | 9.6e-09 ✅ |
| Poutou (NPA) | 0.36 | 0.16 | 0.10 | **0.06** | −38 % | 1.6e-12 ✅ |

**Global poolé** (n = 5094) : swing proportionnel **1.259** → GB **0.561** (−55 %), Wilcoxon **p = 7.0e-249**. Significatif pour **tous** les partis, LFI compris.

> 🔴 **MAIS ce n'est PAS de la prévision — c'est du DOWNSCALING.** Le modèle voit la transition 2017→2022 pendant l'entraînement (CV spatiale *dans* la même transition) : il apprend à répartir un résultat 2022 **déjà connu** vers les circos. Testé en **vraie prévision** (apprendre 2012→2017, prédire 2017→2022 inédit), il **SUR-APPREND et PERD contre le swing proportionnel** — voir **Étape P10**. La significativité ci-dessus vaut pour le downscaling, pas pour la prévision d'un scrutin futur.

## 3. Connexion national ↔ circonscription (E4) : projection de sièges

La carte réelle par circonscription devient le **substrat de désagrégation** d'un scénario national. Exemple : on projette un scénario national hypothétique sur la carte 2022 (swing proportionnel, renormalisé) et on compte les têtes par circonscription — une capacité que le modèle national (P1–P6) n'a pas.

Scénario **illustratif** (national : RN 30%, LFI 25%, ENS 20%, LR 12%, REC 6%, EELV 4%, PS 3%) — PAS une prévision, juste une démonstration de la mécanique :

| Parti | Circonscriptions en tête (projection) |
|---|---|
| Le Pen (RN) | 370 / 577 |
| Mélenchon (LFI) | 146 / 577 |
| Macron (Ensemble) | 57 / 577 |
| Pécresse (LR) | 4 / 577 |

*La projection actuelle applique un **swing proportionnel** (baseline). Le modèle GB ci-dessus, qui bat ce swing de ~68 %, raffinerait cette carte dès qu'un nouveau scrutin fournira la transition à apprendre — c'est le branchement prévu, pas encore un pronostic 2027.*

## 4. Ce que ça règle (audit) et ce qui reste

- **E1 résolu** : le ML par circonscription (ambition du plan) existe, sur données réelles, et il est **statistiquement significatif** (contrairement au national à n=11).
- **E4 amorcé** : national et circonscription sont connectés (désagrégation).
- **Limites restantes** : une seule transition (2017→2022) ; skill de downscaling, pas de prévision d'un scrutin inconnu ; pas encore de covariables socio-éco (INSEE) par circonscription, qui pousseraient vers une vraie régression de Dirichlet compositionnelle (Hanretty 2021).
