# Les PASS jamais passés par la batterie Règle 9 (pré-enregistré)

**Piste B.** Ce cycle ne se contente pas de mesurer une lacune : il la
**comble**.

## Le recompte, et l'écart au #431

| | Nombre |
|---|---|
| PASS possédant un `.npz` | **100** |
| **sans batterie Règle 9** | **29** |
| annoncé par le #431, jamais revérifié | **33** |
| écart | **-4** |

**Prédiction vérifiée** : le chiffre du #431 était faux. Je n'avais pas parié
sur le sens, et c'était la bonne prudence — **quatrième compte de backlog
faux** après les #449, #451 et #453.

## Les batteries exécutées

Ordre **alphabétique**, budget **25 minutes**, tous deux fixés
au pré-enregistrement — **avant** de savoir combien passeraient. Un budget
fixé après coup aurait permis de s'arrêter juste après un bon résultat.

- exécutées : **29**
- non traitées : **0**

| Candidat | Verdict de la batterie | Contrôles ✔ / ✘ |
|---|---|---|
| `breadth_confirmation_overlay` | non validé | 7 / 3 |
| `dispersion_trend_vol_targeting_overlay` | non validé | 5 / 3 |
| `golden_cross_overlay` | non validé | 6 / 2 |
| `halloween_effect` | non validé | 4 / 3 |
| `index_52w_high_overlay` | non validé | 5 / 3 |
| `intl_breadth_confirmation_overlay` | non validé | 5 / 3 |
| `intraday_range_regime_overlay` | non validé | 9 / 2 |
| `january_effect_lowprice_overlay` | non validé | 5 / 4 |
| `january_effect_lowprice_overlay_pit_universe` | non validé | 7 / 3 |
| `leaders_trend_union_overlay` | non validé | 4 / 3 |
| `lowvol_sma200_overlay` | non validé | 6 / 2 |
| `momentum_12_1` | non validé | 5 / 3 |
| `momentum_breadth_vol_targeting_overlay` | non validé | 5 / 3 |
| `momentum_dispersion_trend_and_overlay` | non validé | 7 / 2 |
| `multimarket_breadth_vol_targeting_overlay` | non validé | 5 / 4 |
| `net_breadth_vol_targeting_overlay` | non validé | 6 / 3 |
| `santa_claus_rally_overlay` | non validé | 8 / 2 |
| `santa_vol_targeting_overlay` | non validé | 10 / 2 |
| `short_term_momentum` | non validé | 3 / 5 |
| `sma200_breadth_vol_targeting_overlay` | non validé | 5 / 3 |
| `sma200_momentum_breadth_and_overlay` | non validé | 5 / 3 |
| `sma200_tom_halloween_union_overlay` | non validé | 6 / 2 |
| `sma50_trend_overlay` | non validé | 7 / 2 |
| `tom_decomposition_overlay` | non validé | 5 / 3 |
| `tom_halloween_union_overlay` | non validé | 4 / 4 |
| `tom_overlay` | non validé | 4 / 4 |
| `turn_of_month` | non validé | 6 / 4 |
| `weakness_breadth_vol_targeting_overlay` | non validé | 8 / 2 |
| `winners_trend_vol_targeting_overlay` | non validé | 7 / 1 |

**0 / 29** validés par la batterie.

### Une limite de la règle unifiée, découverte ici

Sur les **29** rapports de batterie, **29** sont
classés « indéterminé » par la règle de verdict unifiée (#448/#449).
Ce n'est pas un défaut de ces rapports : la batterie énonce son verdict
dans **sa propre formulation** — *« PAS de PASS RENFORCÉ »* — et non
avec les marqueurs `**PASS` / `**FAIL` que la règle sait lire.

La règle du #448 avait été **taillée sur les rapports de stratégie**.
Elle ne couvre pas les rapports de batterie, et **personne ne l'avait
remarqué** — ni le #448, ni le #449, ni le #454 qui a unifié le dernier
consommateur. Ce cycle le découvre **en passant**, en cherchant autre
chose.

**Ce n'est pas corrigé ici** : élargir la règle serait une modification
non déclarée, et le #448 a montré qu'une couche ajoutée pour un cas
connu est difficile à distinguer d'un ajustement. **Inscrit à la file.**

## Ce que la batterie établit, et ce qu'elle n'établit pas

Elle **ajoute** une information à un PASS ; elle ne l'**annule** pas. Un
candidat qui échoue à la batterie garde le verdict de son propre
pré-enregistrement — ce qu'il perd, c'est la prétention à avoir été
**éprouvé** au-delà de son critère d'origine.

Elle ne corrige pas non plus la réserve du #456 : son contrôle (e) déflate
par un `n_trials` égal à la taille du backlog, qui **sous-estime** le nombre
d'hypothèses réellement essayées. La batterie est donc, elle aussi, un test
**indulgent** sur ce point précis.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).