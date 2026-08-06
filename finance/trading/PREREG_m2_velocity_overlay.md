# Pré-enregistrement — Vitesse de circulation de la monnaie (M2V)

**Committé AVANT tout calcul.** Cycle #320 du backlog non-ML.

## Hypothèse

La vitesse de circulation de M2 (FRED `M2V` = PIB nominal / M2, trimestrielle
depuis 1959) mesure un concept monétariste DISTINCT de la croissance de
la masse monétaire déjà testée et FAIL (#203, M2SL, glissement annuel) :
la croissance de M2 mesure la QUANTITÉ de monnaie créée, la vitesse de
circulation mesure la RAPIDITÉ avec laquelle cette monnaie circule dans
l'économie réelle. Une vitesse de circulation FAIBLE ou en déclin est
documentée comme un signal de thésaurisation/aversion au risque et de
malaise économique — la vitesse de M2 s'est effondrée pendant la crise
2008-2009 et de façon spectaculaire en 2020 (chute la plus abrupte de
l'historique de la série). Jamais testée dans ce backlog.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `M2V` (gratuite, trimestrielle,
1959-2026, disponibilité confirmée par fetch de test le 06/08/2026,
`data/m2_velocity_quarterly.csv`). Réutilisation intégrale des
conventions déjà établies : `expanding_tercile_gate_high`/tercile bas
(direction inversée comme pour #203, extension de `data_loader`/loaders
FRED déjà en place), CUT=0,5x défensif, décalage de publication d'UN
TRIMESTRE (3 mois, même convention que les séries trimestrielles déjà
testées — défaut de paiement DRCCLACBS #286, extension proportionnelle
de la convention mensuelle #195 et suivantes), CUT=0,5x, COST_BPS=5,0.

## Définition (fixée ici, AVANT tout calcul)

- `GateVelocity(t)` = 1 si `M2V_lag(t-1)` (décalé de 3 mois calendaires
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus BAS
  (vitesse faible = signal de stress/thésaurisation), sinon 0.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé de toute la famille macro-externe) si
  `GateVelocity(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — vitesse basse = défensif — pas de grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (#191/#195/#198/#199/#203...), le design purement défensif sans
amplification limite structurellement le gain de rendement même si le
signal identifie un vrai régime de risque (Sharpe amélioré mais
rendement insuffisant) — schéma déjà observé sur la majorité des
cycles de cette famille. Par ailleurs, la fréquence trimestrielle très
basse (comme #286, quelques dizaines d'observations réelles sur les
40 ans NDX) pourrait limiter la robustesse et la significativité
statistique, indépendamment de la validité du signal. Rapporté
honnêtement dans les deux cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout fetch et tout calcul. Sortie :
`results/nonml_m2_velocity_overlay_result.md`.
