# Voie A — cadre de déploiement de #134/#149 comme outils de gestion du risque

Document de synthèse opérationnelle, pas un nouveau cycle de backtest. Écrit
le 31/07/2026 à la demande explicite de l'utilisateur, en réponse aux
questions posées en cours de session sur la valeur du PASS RENFORCÉ, les
risques d'un déploiement prématuré, et les garde-fous à ajouter avant tout
capital réel. S'appuie exclusivement sur des résultats déjà committés
(`results/nonml_defensive_diversification_bond_overlay_*`,
`results/nonml_cash_rate_correction_defensive_vol_targeting_44_*`,
`results/nonml_diversification_bond_carry_price_decomposition.md`).

## 1. Ce qu'on déploie réellement — statut honnête, pas une "stratégie validée"

**Ni #134 ni #149 n'ont atteint le PASS RENFORCÉ.** Score de la batterie
Règle 9 pour les deux : **3/5**.

| Contrôle | #134 | #149 |
|---|---|---|
| a. Stress coûts ×5 | OK | OK |
| b. Stress crise (4 fenêtres) | OK | OK |
| c. Stabilité temporelle (4 folds) | OK (4/4) | OK (4/4) |
| d. SPA 1-candidat vs BuyHold | **ÉCHEC** (p=0,443) | **ÉCHEC** (p=1,000) |
| e. DSR à n_trials=125 (backlog) | **ÉCHEC** (DSR=0,0008) | **ÉCHEC** (DSR=0,0122) |

Le DSR quasi nul pour les deux signifie : après correction pour les 125
essais du backlog, on ne peut **pas** conclure statistiquement à un edge de
sélection de timing au-delà du hasard. Ce n'est cependant pas une preuve que
le mécanisme est du bruit — la décomposition du #142 explique pourquoi :

> **89% du gain de Sharpe et 86% de la réduction de MDD de #134** viennent du
> **portage seul** (détenir un proxy obligataire rémunéré au lieu de cash à
> 0% pendant les phases hors-marché), **pas d'un timing prédictif de crise**.
> Le #141 confirme : un proxy 3 mois (quasi sans effet duration/prix) obtient
> un résultat quasi identique à un proxy 10 ans.

**Conclusion à retenir pour tout déploiement** : ce n'est pas une stratégie
de market-timing avec un edge statistique démontré. C'est une **correction
d'hypothèse de backtest** (ne pas modéliser le cash hors-marché à 0% quand un
proxy de taux sans risque existe) appliquée à un mécanisme défensif de
vol-targeting déjà connu (#44). Le SPA/DSR échouent précisément parce qu'ils
sont conçus pour détecter du market-timing skill — il n'y en a
structurellement pas à détecter ici, la valeur ajoutée est mécanique
(portage), pas prédictive.

## 2. Implication directe : cadre de déploiement, pas de capital agressif

En conséquence, #134/#149 doivent être déployés comme **des overlays de
gestion du risque documentés**, jamais présentés en interne ou à un tiers
comme une "stratégie alpha validée". Concrètement :

- **Sizing proportionnel à la confiance DSR** (demande explicite de
  l'utilisateur) : DSR≈0 ⇒ **aucune allocation de capital pilotée par le
  signal de timing lui-même**. Le déploiement doit se limiter au mécanisme
  mécanique compris et validé (b, c) : réduire l'exposition actions en
  régime de vol élevée ET rémunérer la fraction hors-marché au taux sans
  risque au lieu de 0%. Le sizing du switch equity/bond reste celui déjà
  figé dans #44/#149 (vol-targeting 15%/20% annualisé, cap 1,0×) — **aucun
  paramètre nouveau à optimiser en live**, ce serait une nouvelle source de
  data-snooping hors protocole.
- **Comparateur obligatoire** : avant tout déploiement, comparer #134/#149
  à un simple **blend statique actions/obligations** (ex. 80/20, rebalancé
  périodiquement, sans switch dynamique) sur la même fenêtre. Si le blend
  statique capture l'essentiel du bénéfice (ce que suggère le résultat "89%
  = portage"), c'est LUI qui doit être déployé — plus simple, moins de
  paramètres, moins de surface de bug, même bénéfice économique.
  **Action concrète : ce comparateur doit être calculé AVANT toute mise en
  production, en un seul essai pré-enregistré (n_trials=1 pour cette
  question précise), pas après avoir vu s'il gagne.**

  **Fait** (`PREREG_static_blend_comparator_149.md`,
  `results/nonml_static_blend_comparator_149.md`) : blend statique au même
  poids moyen que #149 (0,761) → Sharpe +0,60, MDD -71,9% ; #149 dynamique →
  Sharpe +0,84, MDD -37,9% (BH : Sharpe +0,53, MDD -82,9%). Écart de Sharpe
  -0,239, largement sous le seuil -0,05 pré-enregistré. **Conclusion :
  NE PAS simplifier vers le statique — la réduction de MDD dynamique
  (vol-targeting réactif) apporte une valeur mesurable au-delà du simple
  portage moyen, même si cette valeur ne clarifie pas le SPA/DSR (§1).**
  Le shadow-trading (§5) porte donc bien sur le mécanisme dynamique.

## 3. Kill-switch — 3 déclencheurs indépendants

### 3.1 Kill-switch niveau de taux

Le mécanisme dépend d'un proxy de taux sans risque positif et significatif
(Règle 10). Si le taux utilisé (`DGS3MO`/`DGS10`) reste **≤ 0,5% pendant
plus de 60 séances consécutives**, désactiver le switch dynamique et revenir
à Buy&Hold pur (le #146 a montré que la correction ne "sauve" pas un signal
déjà mauvais — un taux quasi nul annule le principal moteur du gain sans
compensation).

### 3.2 Kill-switch corrélation actions/obligations

Le mécanisme suppose une corrélation actions/obligations imparfaite (voire
négative en crise, l'effet "flight-to-quality" marginal mesuré au #142). Si
la corrélation glissante 60 séances entre rendements NDX et rendements du
proxy obligataire **dépasse +0,3 pendant plus de 20 séances consécutives**
(régime de corrélation positive prolongé — ex. choc de taux généralisé,
inflation non ancrée), c'était initialement défini comme désactivation
immédiate du switch.

**Révision du 31/07/2026 (décision utilisateur, sourcée par
`results/nonml_correlation_regime_episodes_149.md`)** : l'analyse des 21
épisodes historiques (1985-2026) où cette condition s'est produite montre
un MDD overlay jamais pire que Buy&Hold (0/21) et un Sharpe overlay-BH
médian quasi nul (-0,04) — le portage protège indépendamment du régime de
corrélation. **Ce kill-switch passe donc de "arrêt dur" à "signal de
vigilance"** : il reste calculé et rapporté chaque semaine
(`scripts/monitoring_correlation_kill_switches_149.py`), mais ne bloque
plus le démarrage ou la poursuite du shadow-trading. Limite explicite de
cette révision : 21 épisodes ne couvrent pas tous les régimes futurs
possibles (ex. taux durablement négatifs, choc jamais vu dans
l'historique) — à revoir si un futur épisode diffère qualitativement des
21 précédents (ex. MDD overlay effectivement pire que BH pour la première
fois).

### 3.3 Kill-switch performance

Seuil pré-enregistré, non révisable après observation : si l'overlay
sous-performe le comparateur statique (§2) de plus de **5 points de Sharpe
annualisé cumulés sur une fenêtre glissante de 252 séances**, désactiver et
revenir au comparateur statique — pas de tuning, abandon direct.

## 4. Monitoring de corrélation — mécanique

- Fenêtre glissante 60 séances, recalcul quotidien, alerte automatique
  (script à écrire, réutilisant `data_loader.log_returns_pct`) dès que le
  seuil §3.2 est franchi.
- Rapport hebdomadaire committé (pas seulement une alerte ponctuelle) :
  corrélation courante, niveau de taux courant, statut des 3 kill-switches.

## 5. Protocole de shadow-trading avant capital réel

**État au 31/07/2026** : le kill-switch corrélation (§3.2) est actif
(corrélation glissante 60j à +0,495, 48 séances consécutives) mais a été
révisé en signal de vigilance (§3.2) suite à l'analyse des 21 épisodes
historiques — **ne bloque plus le démarrage**. Le kill-switch taux (§3.1)
est OK (DGS10=4,62%). **Décision : démarrage du shadow-trading autorisé.**
Voir `results/shadow_trading_149_journal.md` pour le journal officiel
(date de départ, paramètres figés, positions).

- Durée minimale **6 mois** (Règle 8 du protocole, déjà en vigueur),
  paramètres strictement figés à ceux de #149 (le meilleur des deux sur la
  batterie renforcée reste marginal — utiliser #149 par défaut, #134 comme
  variante NDX si le marché cible diffère).
- **Aucune modification de paramètre en cours de route.** Si le shadow
  déçoit, le mécanisme est abandonné tel quel, jamais retouché puis
  re-testé sur la même fenêtre (ce serait à nouveau du data snooping,
  Règle 8).
- Critère de sortie du shadow vers capital réel : le shadow doit répliquer
  au moins qualitativement le comportement backtesté (Sharpe overlay >
  Sharpe BH sur la fenêtre shadow, MDD overlay ≤ MDD BH) — sinon retour au
  Buy&Hold pur ou au comparateur statique (§2), pas d'ajustement.

## 6. Cadence de ré-audit

- **Trimestrielle** : revérifier la fraîcheur/qualité de la source de taux
  (le #140 a documenté un piège réel : une série de taux allemande
  disponible seulement en fréquence mensuelle donnait une fausse impression
  de série quotidienne — vérifier explicitement la granularité et
  l'absence de gaps à chaque ré-audit, pas seulement au lancement).
- **Annuelle** : recalcul complet de la batterie Règle 9 (a-e) sur la
  fenêtre étendue (données de l'année écoulée incluses) — si le SPA/DSR
  s'améliore significativement avec plus de données, ce serait un signal
  fort pour reconsidérer le statut ; si la performance se dégrade, c'est un
  signal d'abandon anticipé.

## 7. Budget n_trials pour itérations futures

Toute modification future du mécanisme (nouveau seuil de vol-targeting,
nouvelle maturité de proxy, nouveau marché) est un **nouvel essai** et doit
être ajoutée au compteur du backlog non-ML (`NONML_STRATEGY_BACKLOG.md`,
actuellement 160 hypothèses) avant tout calcul — jamais traitée comme un
ajustement "gratuit" hors comptage. Toute évolution en production doit être
documentée dans un PREREG dédié, committé avant changement, exactement comme
en recherche.

## 8. Critères d'abandon pré-enregistrés (fixés ici, non révisables après coup)

1. Kill-switch performance (§3.3) déclenché deux fois sur 24 mois glissants
   ⇒ abandon définitif du switch dynamique, retour au comparateur statique.
2. Le comparateur statique (§2) s'avère à moins de 1 point de Sharpe annualisé
   du switch dynamique sur les données déjà disponibles ⇒ ne jamais déployer
   le dynamique, déployer directement le statique (plus simple = préféré à
   égalité de résultat, principe de parcimonie).
3. Deux ré-audits trimestriels consécutifs (§6) révèlent un problème de
   qualité de données non trivial (gap, granularité, arrondi) ⇒ suspension
   immédiate jusqu'à correction ET re-validation complète de la batterie.

## 9. Ce que ce document NE fait PAS

Ne déclare aucun PASS RENFORCÉ (aucun n'existe à ce jour sur l'ensemble du
backlog non-ML, 0/160). Ne recommande PAS d'allocation de capital réel
immédiate — recommande le shadow-trading (§5) comme étape obligatoire
suivante, avec le comparateur statique (§2) à calculer en premier lieu
puisqu'il pourrait rendre tout le mécanisme dynamique inutile.
