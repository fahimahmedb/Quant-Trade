# Pré-enregistrement — Effet du changement d'heure (DST)

**Committé AVANT tout calcul.** Cycle #310 du backlog non-ML.

## Hypothèse

Anomalie documentée (Kamstra, Kramer & Levi 2000, *American Economic
Review*, "Losing Sleep at the Market: The Daylight Saving Anomaly") :
rendement anormalement NÉGATIF le premier jour de bourse suivant
chaque changement d'heure (printemps ET automne), attribué à une
désynchronose du sommeil documentée en médecine (perturbation du
rythme circadien affectant l'aversion au risque des investisseurs),
effet retrouvé sur plusieurs marchés internationaux (États-Unis,
Royaume-Uni, Allemagne, Canada dans l'étude originale). Jamais testé
dans ce backlog.

## Sourcing des dates AVANT tout calcul (Règle 2)

**Règles officielles de changement d'heure, par marché et par période
historique** (sourcées avant toute exécution) :

**Marchés US (Composite, NDX-100, Russell 2000, S&P 500)** :
- 1970-1973 : dernier dimanche d'avril → dernier dimanche d'octobre
  (Uniform Time Act de 1966).
- **1974** (exception documentée, Emergency Daylight Saving Time
  Energy Conservation Act de 1973, réponse au choc pétrolier) :
  6 janvier 1974 → 27 octobre 1974.
- **1975** (même loi, 2e année) : 23 février 1975 → 26 octobre 1975.
- 1976-1986 : dernier dimanche d'avril → dernier dimanche d'octobre
  (retour à la règle standard).
- 1987-2006 : premier dimanche d'avril → dernier dimanche d'octobre
  (extension signée en 1986, effective 1987).
- 2007-présent : 2e dimanche de mars → 1er dimanche de novembre
  (Energy Policy Act de 2005, effectif 2007).

**Marché DAX (Allemagne/UE)** : dernier dimanche de mars → dernier
dimanche d'octobre, règle harmonisée UE en vigueur sans interruption
depuis 1996 (directive 2000/84/CE et prédécesseures) — couvre
intégralement l'historique DAX disponible (1999+), aucune exception
nécessaire.

## Construction data-driven (fixée ici, AVANT tout calcul)

`DSTMondayMask(t)` = 1 si la date de bourse `t` est le PREMIER jour de
bourse strictement postérieur à un dimanche de changement d'heure
(printemps OU automne) pour le calendrier applicable au marché testé
(règles US ou UE ci-dessus selon le marché), sinon 0. Détection
data-driven à partir des dates de calendrier de bourse (pas de
troncature arbitraire — le premier jour de bourse après le dimanche,
quel qu'il soit, y compris si un jour férié décale le lundi).

**Position** : `CUT=0,5x` (design purement défensif, jamais de
levier, cohérent avec la convention des signaux d'évitement de risque
déjà utilisée dans ce backlog) si `DSTMondayMask(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500 (règles US), DAX (règles UE) — `data/*.txt`, aucune
nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule fenêtre testée : le jour J+1 suivant chaque transition,
valeur reprise directement de l'étude de référence, pas une grille).

## Risque déclaré à l'avance

Comme pour l'effet lunaire (#309, FAIL par manque de puissance), le
nombre d'occurrences est très faible (2 par an × nombre d'années =
quelques dizaines à ~110 jours sur l'historique le plus long) — un
échec par manque de puissance statistique plutôt que par absence
réelle d'effet est plausible. De plus, contrairement à l'effet
lunaire, cet effet est documenté comme NÉGATIF (pas positif) : le
design défensif (CUT, jamais d'amplification) est cohérent avec cette
direction, mais un design purement défensif sans amplification limite
structurellement le gain de rendement total même si l'effet est réel
(même limite déjà documentée pour toute la famille macro-externe
défensive de ce backlog).

## Anti-cheat

Ce fichier committé avant `nonml_dst_change_overlay_backtest.py`.
Aucune nouvelle donnée (règles calendaires officielles publiques,
vérifiables indépendamment). Sortie :
`results/nonml_dst_change_overlay_result.md`.
