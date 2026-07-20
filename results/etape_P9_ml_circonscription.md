# Étape P9 — ML par circonscription, statistiquement significatif

## 0. Pourquoi cette étape (retour au plan + significativité)

Le plan initial visait un **ML par circonscription** (« le vrai terrain ML »). Le modèle national (P1–P6) plafonnait à n=11 élections : **rien n'y était significatif**. Ici, la maille circonscription donne **~566 circos × 9 partis = 5094 prédictions hors-échantillon** — assez pour un vrai test de significativité. Partis EXPLICITES (Mélenchon = **LFI**, jamais un bloc).

## 1. Modèle et protocole

- **Cible** : part 2022 de chaque parti dans une circonscription.
- **Entrées** : composition 2017 **complète** de la circo (11 familles) + moyenne départementale du parti (apprise sur le train, sans fuite).
- **Modèle** : Gradient Boosting (200 arbres, prof. 3), **validation croisée 5-fold** — chaque circo prédite hors de son pli.
- **Baselines** : persistance (= 2017) et **swing national uniforme** (2017 + Δ national) — la référence de la littérature (Hanretty 2021).
- **Test** : Wilcoxon apparié sur les erreurs absolues par circo (GB vs swing).

## 2. Résultat : le modèle bat le swing uniforme, significativement

| Parti | MAE persistance | MAE swing | MAE **GB** | Gain vs swing | p-value | Signif. |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) | 4.02 | 4.23 | **1.47** | −65 % | 5.7e-67 | ✅ p<0.001 |
| Le Pen (RN) | 2.44 | 1.87 | **1.03** | −45 % | 1.0e-42 | ✅ p<0.001 |
| Macron (Ensemble) | 4.62 | 3.28 | **1.35** | −59 % | 9.9e-52 | ✅ p<0.001 |
| Pécresse (LR) | 15.03 | 3.32 | **0.47** | −86 % | 1.2e-88 | ✅ p<0.001 |
| Hidalgo (PS) | 4.72 | 1.42 | **0.17** | −88 % | 1.9e-88 | ✅ p<0.001 |
| Dupont-Aignan (DLF) | 2.60 | 0.81 | **0.18** | −78 % | 1.3e-81 | ✅ p<0.001 |
| Lassalle (Résistons) | 1.87 | 0.79 | **0.27** | −66 % | 5.9e-64 | ✅ p<0.001 |
| Arthaud (LO) | 0.11 | 0.10 | **0.05** | −45 % | 4.4e-27 | ✅ p<0.001 |
| Poutou (NPA) | 0.36 | 0.16 | **0.06** | −61 % | 6.4e-46 | ✅ p<0.001 |

**Global poolé** (n = 5094 prédictions) : MAE swing **1.776** → GB **0.561** (−68 %), Wilcoxon **p = 0.0e+00**. Le modèle de circonscription capture la transition électorale 2017→2022 bien mieux qu'un swing uniforme, pour **tous** les partis, LFI compris.

*Cadre honnête : c'est une skill de **downscaling** (répartir un résultat national vers les circos), testée sur circos held-out — pas une prévision d'un scrutin futur inconnu. Les deux prédicteurs comparés utilisent le même agrégat national ; seule la répartition diffère. La significativité porte sur « le modèle répartit mieux que le swing uniforme », ce qui est solidement établi.*

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
