# Les **13 cycles complets sans entrée de backlog** (pré-enregistré)

Le **#474** les a trouvés : rapport présent, script présent, **aucune
entrée ne les mentionne**. La tâche inscrite était « écrire les entrées
manquantes, **ou établir qu'elles sont couvertes autrement** ».
**L'ordre compte** : on établit d'abord, on écrit ensuite — et seulement
ce qui reste.

## La population, re-dérivée

- « cycles complets » au #474 : **13**
- re-dérivés ici : **13** (**+0**)

**Effectif inchangé.**

## Volet A — la règle de couverture

Le #474 cherchait la mention sous la forme `PREREG_<nom>.md`. C'est **une**
forme, pas la seule — le #464 avait déjà buté là-dessus : *« non cité sous
cette forme » n'est pas « jamais mentionné »*.

**Couvert autrement** = son **rapport** ou son **script** est cité
nominativement quelque part dans le backlog.

- **couverts autrement** : **0 / 13**
- **non couverts** : **13**

### Les couverts — avec la citation qui le prouve

**Aucun.**

### Les non couverts — nommés un par un

| `<nom>` | Rapport présent |
|---|---|
| `correlation_regime_episodes_149` | `nonml_correlation_regime_episodes_149.md` |
| `leaders_vol_targeting_20_overlay_pit_universe` | `nonml_leaders_vol_targeting_20_overlay_pit_universe_audit.md` |
| `lowvol_sma200_overlay_pit_universe` | `nonml_lowvol_sma200_overlay_pit_universe_audit.md` |
| `market_concentration_vol_targeting_overlay_pit_universe` | `nonml_market_concentration_vol_targeting_overlay_pit_universe_audit.md` |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` | `nonml_momentum_decile_spread_vol_targeting_overlay_pit_universe_audit.md` |
| `momentum_dispersion_vol_targeting_overlay_pit_universe` | `nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_audit.md` |
| `n_trials_dependence_correction` | `nonml_n_trials_dependence_correction_audit.md` |
| `net_breadth_vol_targeting_overlay_pit_universe` | `nonml_net_breadth_vol_targeting_overlay_pit_universe_audit.md` |
| `pnl_duplicate_sweep_v2` | `nonml_pnl_duplicate_sweep_v2_audit.md` |
| `pnl_persistence_exposed_pass` | `nonml_pnl_persistence_exposed_pass_audit.md` |
| `range_position_vol_targeting_overlay_pit_universe` | `nonml_range_position_vol_targeting_overlay_pit_universe_audit.md` |
| `smallcap_proxy_outperformance_breadth_overlay_pit_universe` | `nonml_smallcap_proxy_outperformance_breadth_overlay_pit_universe_audit.md` |
| `winners_trend_vol_targeting_overlay_pit_universe` | `nonml_winners_trend_vol_targeting_overlay_pit_universe_audit.md` |

Ce sont **les seuls** pour lesquels une entrée manque réellement.

## De quel type de rapport parle-t-on ? — constat post-mesure

*Ajouté après mesure, et signalé comme tel. **La classification du #474
n'est pas modifiée.***

Le #474 appelait « cycle complet » tout `<nom>` ayant **un** rapport
`nonml_<nom>*.md`. Ce n'est pas la même chose selon le rapport trouvé :

- avec un **`_result.md`** *(cycle publié au sens plein)* : **9**
- avec un **`_audit.md` seul** *(l'audit existe, pas le résultat)* : **3**
- autre convention *(rapport sans suffixe, schéma batterie)* : **1**

  - `n_trials_dependence_correction` — seulement `nonml_n_trials_dependence_correction_audit.md`
  - `pnl_duplicate_sweep_v2` — seulement `nonml_pnl_duplicate_sweep_v2_audit.md`
  - `pnl_persistence_exposed_pass` — seulement `nonml_pnl_persistence_exposed_pass_audit.md`

> **« Cycle complet » était donc trop généreux pour ceux-là.** Un
> `_audit.md` sans `_result.md` n'est pas un cycle publié : c'est un
> **audit orphelin**. Le #474 ne s'en est pas aperçu parce que sa
> règle cherchait `nonml_<nom>*.md` **sans regarder le suffixe**.

**Ce n'est pas une erreur de comptage** — les fichiers existent bien —
**c'est une erreur d'étiquette**, et elle m'appartient : c'est moi qui
ai écrit cette règle au #474.

## Volet B — ce qui sera écrit, et ce qui ne le sera pas

**Une seule entrée collective** nommant les **13**
est ajoutée au backlog, avec leurs rapports.

**Ce qui ne sera pas fait, dans tous les cas.** Aucune entrée
**rétro-datée**, aucun numéro inséré dans la suite existante. Fabriquer
des entrées à la place de cycles qui n'en ont jamais écrit reviendrait à
**falsifier la chronologie** du dépôt pour faire disparaître une lacune —
exactement le geste que ces cycles reprochent ailleurs.

> **Une entrée qui dit la lacune vaut mieux qu'une trace qui la masque.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 8 sur 13 couverts autrement | ≥ 8 | 0 | **réfutée** |
| tous les non couverts ont leur rapport | tous | tous  | **vérifiée** |
| aucun n'est cité via son `PREREG_` | 0 | 0 | **vérifiée** |

**La prédiction 1 est réfutée.** La lacune de trace est **plus large**
que le #474 ne le laissait croire, et l'entrée collective doit le dire
sans l'atténuer — le pré-enregistrement l'exigeait.

## Critères de succès

1. Population re-dérivée, écart au #474 signalé — **OUI** (**+0**).
2. **13/13** classés et nommés, citation publiée pour les couverts — **OUI**.
3. Une seule entrée collective, sans rétro-datation — **OUI**.
4. Aucun `PREREG_` supprimé, aucun rapport régénéré, aucune entrée
   existante réécrite — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date
> de son exécution (cycles #436-#438).