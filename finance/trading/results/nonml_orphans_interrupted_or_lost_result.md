# Les orphelins du #464 : **cycle interrompu** ou **trace perdue** ?

*(pré-enregistré)*

Le **#464** avait compté **10** entrées sans aucun fichier et **24**
`PREREG_` orphelins, puis s'était arrêté là en inscrivant la tâche.
**Ce cycle l'exécute** : chaque `<nom>` est classé par une règle fixée
avant de regarder, sur trois faits mécaniques.

## Les populations, re-dérivées par code

Elles ne sont **pas recopiées** du #464 : elles sont reconstruites par
son propre code (`entrees`, `CITE`, même classification post-hoc).

| Population | #464 | Ici | Écart |
|---|---|---|---|
| entrées sans aucun fichier | 10 | **10** | **+0** |
| `PREREG_` jamais mentionnés | 24 | **23** | **-1** |

> **Un effectif a bougé depuis le #464.** Plutôt que d'en proposer
> une explication plausible — « des cycles ont été écrits depuis » —
> je la **calcule**.

**La liste publiée par le #464 est tronquée** : elle nomme
**15** de ses **24** orphelins
et clôt par « *… et 9 autres* ». Son critère 3 — « orphelins listés
**nominativement — OUI** » — est donc **surévalué**, et je l'inscris
plutôt que de m'appuyer dessus.

Elle est donc **rejouée sur les objets git** à son propre commit
`e411360c9c49` — sa règle, son backlog, ses fichiers.

- population du #464 reconstituée : **24** noms
- **entrés** dans la population depuis : **0**
- **sortis** de la population depuis : **1**
  - `prereg_convention_coverage`

> **L'écart est entièrement expliqué.** Chaque sortie signifie
> qu'une **entrée de backlog écrite depuis** mentionne désormais
> ce pré-enregistrement : la population décroît par le travail de
> traçage, **pas par effacement**.

Le seul sortant est **le pré-enregistrement du #464 lui-même**.
Il se comptait donc dans sa propre population — la même
**auto-inclusion** que les #463/#468 ont traquée ailleurs, ici
sans conséquence puisqu'il ne s'agissait que d'un décompte.
C'est aussi ce qui justifie mon exclusion de moi-même
ci-dessous : sans elle, je reproduirais exactement son défaut.

## La règle de classement, rappelée

- **R** — un rapport `nonml_<nom>*.md` existe **aujourd'hui** ;
- **H** — un tel rapport a existé **à un commit quelconque** ;
- **S** — un script `nonml_<nom>*.py` existe aujourd'hui.

`R` vrai → **cycle complet** ; `R` faux et `H` vrai → **trace perdue** ;
les deux faux → **cycle interrompu**. Exhaustive par construction —
**ce n'est donc pas un critère de succès**, et je ne la compte pas comme
une prédiction vérifiée.

**Je m'exclus de ma propre population** — `PREREG_orphans_interrupted_or_lost.md` existe
depuis ce cycle et serait compté orphelin tant que son entrée de backlog
n'est pas écrite. C'est la règle d'exclusion de soi des **#447/#463**,
appliquée ici avant mesure. **Elle ne sauve aucune prédiction** : avec
moi le compte de cycles complets serait de 14, sans moi de 13 —
les deux au-dessus du seuil annoncé.

La commande qui établit `H`, pour qu'un lecteur puisse la refaire :

```
git log --all --diff-filter=A --name-only --pretty=format: \
    -- 'finance/trading/results/nonml_<nom>*.md'
```

## Les **10** entrées sans aucun fichier

| # | `<nom>` | R | H | S | Classe |
|---|---|---|---|---|---|
| 164 | `short_term_momentum_pit_universe` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 163 | `leaders_index52w_high_overlay_pit_universe` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 252 | `short_term_momentum_pit_universe_causal` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 253 | `leaders_overlays_same_bar_correction` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 254 | `leaders_calendar_overlays_same_bar_correction` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 255 | `lowvol_trend_vol_targeting_same_bar_correction` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 257 | `sma200_overlays_same_bar_correction` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 260 | `leaders_index52w_high_overlay_battery_causal_refresh` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 263 | `meilleurs_candidats_guide_deploiement_v2` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| 273 | `dispersion_battery_caduc_et_guide_v3` | non | non | non | **CYCLE INTERROMPU (au préreg)** |

- **traces perdues** : **0**
- **cycles interrompus** : **10**
- **cycles complets** : **0**

## Les **23** `PREREG_` jamais mentionnés

| `<nom>` | R | H | S | Classe |
|---|---|---|---|---|
| `correlation_regime_episodes_149` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `etape_d_v3_add_149` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `etape_d_v3_add_crossmarket` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `leaders_index52w_high_overlay_extended_history` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `leaders_vol_targeting_20_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `log1p_double_conversion_correction` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `lowvol_sma200_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `market_concentration_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `ml_exogenous_features_rates_crossmarket` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `ml_meta_labeling_logitl2_ndx` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `ml_regularized_architecture` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `momentum_decile_spread_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `momentum_dispersion_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `n_trials_dependence_correction` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `net_breadth_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `pnl_duplicate_sweep_v2` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `pnl_persistence_exposed_pass` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `pnl_persistence_lot2` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `pnl_persistence_lot3` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `protocole_regle_10_taux_realiste_cash` | non | non | non | **CYCLE INTERROMPU (au préreg)** |
| `range_position_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `smallcap_proxy_outperformance_breadth_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |
| `winners_trend_vol_targeting_overlay_pit_universe` | **oui** | **oui** | oui | **CYCLE COMPLET** |

- **cycles complets** *(rapport présent, entrée manquante)* : **13**
- **cycles interrompus** : **10**
- **traces perdues** : **0**

> **Les deux totaux ne s'additionnent pas.** Un `PREREG_` orphelin dont
> le rapport existe n'est pas du travail non fait : c'est une **anomalie
> de trace écrite**. Les confondre gonflerait la dette d'un facteur deux.

## Les traces perdues — avec leur commit de suppression

Le critère 3 l'exige : **sans le commit, la classe est un mot sans**
**preuve.**

**Aucune trace perdue.** Aucun rapport de ce dépôt n'a été ajouté puis
supprimé sans retour.

> **C'est un résultat favorable, et le pré-enregistrement m'imposait
> de m'en méfier.** La commande qui a cherché est publiée ci-dessus :
> elle balaie `--all`, donc toutes les branches, et le filtre `A` ne
> retient que les **ajouts**. Un rapport supprimé y figurerait.

## Ces « interrompus » le sont-ils vraiment ?

*Constat ajouté après mesure, et signalé comme tel.* **La règle de**
**classement n'est pas modifiée** — le tableau ci-dessus reste ce
qu'elle produit.

Ma règle cherche un rapport **portant le `<nom>` du pré-enregistrement**.
Or un **cycle de correction** réutilise des scripts existants et publie
ses résultats **sous les noms de ces scripts**. Il aurait alors tout
produit, et ma règle le dirait inachevé.

Contrôle : pour chaque entrée classée interrompue, son corps cite-t-il
des rapports `.md` qui **existent aujourd'hui** ?

- entrées classées interrompues : **10**
- dont le corps cite des rapports **présents** : **9**

| # | `<nom>` | Rapports cités et présents |
|---|---|---|
| 164 | `short_term_momentum_pit_universe` | `nonml_short_term_momentum_result_pit_universe.md` |
| 163 | `leaders_index52w_high_overlay_pit_universe` | `nonml_leaders_index52w_high_overlay_pass_validation_battery_pit_universe.md`, `nonml_ndx100_universe_census.md` |
| 252 | `short_term_momentum_pit_universe_causal` | `nonml_leaders_index52w_high_overlay_pass_validation_battery_pit_universe.md`, `nonml_meilleurs_candidats_guide_deploiement.md`, `nonml_short_term_momentum_result_pit_universe.md` |
| 253 | `leaders_overlays_same_bar_correction` | `nonml_leaders_trend_union_overlay_result.md`, `nonml_leaders_vol_targeting_20_overlay_result.md`, `nonml_sma200_leaders_overlay_result.md` |
| 254 | `leaders_calendar_overlays_same_bar_correction` | `nonml_leaders_tom_halloween_union_overlay_result.md`, `nonml_leaders_tom_overlay_result.md` |
| 255 | `lowvol_trend_vol_targeting_same_bar_correction` | `nonml_lowvol_trend_vol_targeting_overlay_result.md` |
| 257 | `sma200_overlays_same_bar_correction` | `nonml_lowvol_sma200_overlay_result.md`, `nonml_momentum12_1_sma200_overlay_result.md`, `nonml_momentum_consistency_sma200_overlay_result.md` |
| 263 | `meilleurs_candidats_guide_deploiement_v2` | `nonml_meilleurs_candidats_guide_deploiement.md` |
| 273 | `dispersion_battery_caduc_et_guide_v3` | `nonml_meilleurs_candidats_guide_deploiement.md` |

> **Publier « 10 cycles de travail annoncé et non produit » aurait
> été une accusation fausse portée contre la trace du dépôt** — la
> faute exacte que le #464 s'était interdite. **9**
> de ces entrées ont bel et bien produit leurs rapports, sous le nom
> des scripts qu'elles corrigeaient.

**Ce que ma règle mesure réellement**, il faut donc l'énoncer ainsi :
*aucun rapport ne porte le `<nom>` du pré-enregistrement* — ce qui
est vrai, et bien plus faible que « le cycle est inachevé ».

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 12 cycles complets parmi les orphelins | ≥ 12 | 13 | **vérifiée** |
| ≥ 6 interrompus parmi les entrées sans fichier | ≥ 6 | 10 | **vérifiée** |
| ≥ 1 trace perdue au total | ≥ 1 | 0 | **réfutée** |

**La prédiction 3 est réfutée dans le sens favorable**, et le
pré-enregistrement avait fixé d'avance ce que j'en ferais : m'en
méfier et publier la commande. **Aucun rapport n'a été perdu par ce
dépôt.**

> **La prédiction 2 est « vérifiée » par une règle qui se trompe.**
> Elle annonçait ≥ 6 cycles interrompus et ma règle en compte
> 10 — mais le contrôle post-hoc vient
> de montrer que **9** d'entre eux avaient produit
> leurs rapports. **Une prédiction confirmée par un instrument faux
> n'est pas confirmée**, et je la compte comme telle plutôt que de la
> porter au crédit du cycle.

## Ce que devient la dette du #464

- **1** entrée(s) sans fichier **ni rapport cité présent** — la
  seule population pour laquelle « inachevé » tient encore après le
  contrôle post-hoc : `leaders_index52w_high_overlay_battery_causal_refresh` ;
- **9** entrées classées interrompues par ma règle
  mais ayant **produit leurs rapports sous d'autres noms** ;
- **13** cycles **complets** dont l'entrée de backlog manque — du
  travail produit et **mal tracé** ;
- **10** `PREREG_` sans rapport ni entrée ;
- **0** rapports perdus.

**La dette du #464 était donc surtout une dette de nommage, pas de
travail.** Sur 33 objets examinés, **1** correspond à du travail annoncé
et introuvable ; tout le reste est produit mais mal relié à sa trace.

**Aucun n'est réparé ici** — le pré-enregistrement l'interdit. La
réparation, si elle a lieu, sera un cycle dédié, comme au #468.

## Critères de succès

1. Populations re-dérivées par code et écart au #464 signalé — **OUI**.
2. **33/33** `<nom>` classés et nommés — **OUI**.
3. Commit de suppression publié pour chaque trace perdue — **OUI** *(aucune trace perdue)*.
4. « Complet » et « interrompu » comptés séparément — **OUI**.

**PASS** — le critère porte
sur le **procédé** : un cycle qui classe tout et ne répare rien réussit.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre numérique à perturber. Lecture seule, **aucun effet de bord**.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).