# Pré-enregistrement — Règle de Sahm en temps réel, overlay défensif

**Committé AVANT tout calcul.** Cycle #342 du backlog non-ML.

## 1. Déclaration explicite de la tension avec le canal marché du travail déjà clos (Règle 2, transparence)

Ce cycle traite une idée dont le risque de redondance a été
explicitement signalé à l'avance à DEUX reprises : (a) au #331, le
taux de chômage brut `UNRATE` a été explicitement ÉCARTÉ SANS TEST car
jugé "trop redondant avec le canal marché du travail déjà clos 0/4" ;
(b) au #340, la règle de Sahm a été identifiée comme idée disponible
mais avec la mention explicite "risque de redondance signalé à
l'avance... à trancher explicitement au PREREG du prochain cycle".

**Décision prise ici, avant tout calcul** : ce cycle TESTE la règle de
Sahm (et non `UNRATE` brut), pour deux raisons distinctes du
raisonnement qui avait justifié d'écarter `UNRATE` seul :

1. **Série sous-jacente jamais testée.** Aucune des 5 constructions du
   canal marché du travail déjà closes (ICSA #204, CCSA #322, PAYEMS
   #324, AWHMAN #330, JOLTS #335) n'utilise le TAUX DE CHÔMAGE — elles
   mesurent des flux (demandes d'allocation, embauches nettes,
   offres d'emploi) ou une marge intensive (heures travaillées). Le
   taux de chômage lui-même (stock, pas flux) n'a jamais été exploité
   numériquement dans ce backlog.
2. **Mécanisme de construction qualitativement distinct de TOUT ce qui
   a été testé jusqu'ici dans ce backlog.** La règle de Sahm n'est PAS
   un tercile empirique expanding calculé sur l'historique disponible
   (technique utilisée pour les ~30 constructions macro-externes de ce
   backlog) — c'est un **seuil FIXE, externe, calibré une fois pour
   toutes par la littérature académique** (Sahm 2019, "Direct Stimulus
   Payments to Individuals", seuil de déclenchement 0,50 point de
   pourcentage documenté comme signal de récession quasi-certaine
   depuis 1970 aux États-Unis) — analogue en esprit au design
   "purement défensif sans paramètre libre" déjà pratiqué (ex. seuils
   VIX/breakeven), mais ici le seuil lui-même n'est PAS estimé sur les
   données de ce backlog, contrairement à TOUS les seuils tercile déjà
   utilisés. C'est un test d'un OUTIL DE DÉCISION EXTERNE déjà
   entièrement spécifié, pas une nouvelle estimation empirique.

**Limite reconnue honnêtement** : la série sous-jacente au numérateur
(taux de chômage) est économiquement proche du canal marché du travail
déjà clos à 0/5 — un FAIL ici serait cohérent avec ce précédent et ne
serait pas surprenant (prédiction posée à la section 6).

## 2. Données

`SAHMREALTIME` (FRED, "Real-time Sahm Rule Recession Indicator" —
moyenne mobile 3 mois du taux de chômage U-3, moins son minimum sur
les 12 derniers mois, **vintage temps réel** : chaque observation
reflète ce qui était effectivement calculable avec les données
disponibles à ce moment, sans révision rétroactive du passé),
gratuite, mensuelle depuis décembre 1959, disponibilité déjà vérifiée
par fetch de test (HTTP 200, 798 valeurs jusqu'à 2026-06-01, 177/798
observations ≥0,50 soit ~22,2% du temps).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe (indicateur
macro US appliqué comme jauge de risque de récession globale).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier, SEUIL FIXE EXTERNE)

- Décalage de publication d'UN mois (`PUBLICATION_LAG_MONTHS=1`,
  **réutilisé à l'identique du #324 PAYEMS**, Règle 7 — même rapport
  BLS mensuel sous-jacent).
- `position(t) = 0,5x` si `SAHMREALTIME_lag(t) ≥ 0,50` (**seuil FIXE
  externe, Sahm 2019, jamais estimé sur les données de ce backlog —
  AUCUN tercile expanding ici**, contrairement à toutes les
  constructions macro-externes précédentes), `1,0x` sinon. **Jamais de
  levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un seuil fixe externe non estimé, un
critère multi-marché figé, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**FAIL anticipé, mais pas garanti** : la proximité économique avec le
canal marché du travail déjà clos à 0/5 (ICSA/CCSA/PAYEMS/AWHMAN/JOLTS)
rend un FAIL plus probable qu'un PASS a priori. Testé néanmoins car (a)
la série sous-jacente est numériquement inédite et (b) le mécanisme de
seuil fixe externe est structurellement distinct de toutes les
constructions tercile déjà closes — un résultat, quel qu'il soit, est
informatif sur cette distinction méthodologique précise. Résultat
rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme documenté pour le canal marché du travail (0/5), un signal de
   stress de l'emploi arrive structurellement souvent APRÈS le début
   de la baisse de marché (l'emploi est un indicateur RETARDÉ du
   cycle, pas avancé) — risque déjà confirmé empiriquement 5 fois dans
   ce backlog.
2. Le seuil fixe à 0,50 n'active que ~22,2% du temps sur toute
   l'histoire — mais ces activations sont TRÈS concentrées
   temporellement (récessions groupées), contrairement à un tercile
   expanding qui répartit plus uniformément le temps actif ; risque de
   sous-diversification temporelle du signal, limite reconnue à
   l'avance.
3. Design purement défensif sans levier compensatoire limite
   structurellement le rendement total, comme le reste de la famille
   macro-externe.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_sahm_rule_overlay_backtest.py`,
`scripts/nonml_sahm_rule_overlay_audit.py`,
`results/nonml_sahm_rule_overlay_{result,audit,anti_cheat}.md`.
