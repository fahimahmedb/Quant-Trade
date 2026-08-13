# Pré-enregistrement — persistance du P&L, lot 5 (les 17 PASS invisibles au balayage de doublons)

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**infrastructure et de vérification**. Aucune stratégie évaluée, aucun
verdict recalculé, aucun paramètre de stratégie touché.

## Pourquoi ce lot n'est pas comme les quatre précédents

Les lots #416, #423, #424 et #426 ne portaient que des **FAIL** : aucun verdict
ne pouvait bouger, et je l'écrivais chaque fois pour ne pas survendre l'issue.

**Celui-ci porte des PASS.** Un doublon exact entre deux d'entre eux signifierait
que deux « hypothèses indépendantes » n'en sont qu'une — ce qui gonfle le
décompte « X PASS sur Y hypothèses testées », affirmation de tête du backlog et
entrée directe du `n_trials` utilisé par le DSR.

Je ne prédis pas qu'il y en aura. Je dis que **la question est décidable et ne
l'a jamais été** pour ces 17 candidats.

## Décompte re-mesuré à l'instant, pas recopié

Règle du #425, dont le #426 a montré que je ne me l'étais pas appliquée. Mesure
faite par lecture du code avant d'écrire ce pré-enregistrement :

- rapports portant un PASS : **101**
- parmi eux, **sans `.npz`** : **18**
- dont **1 diagnostic** à écarter : `capitulation_gate_floor_sweep`, dont la
  docstring dit « Diagnostic, pas une stratégie » — son PASS est un faux positif
  de détection (le mot apparaît dans son propre rapport de balayage).

> **Lot retenu : 17 candidats.** Aucun n'appelle `np.savez` — il faut **ajouter**
> la sauvegarde, non retirer une condition comme au #426.

| Structure | Nombre | Candidats |
|---|---|---|
| **indiciel simple** (`pos`, `bh_t`) | **2** | `breadth_confirmation_overlay`, `intl_breadth_confirmation_overlay` |
| boucle **multi-marchés** (`MARKETS`) | **11** | `golden_cross_overlay`, `halloween_effect`, `index_52w_high_overlay`, `intraday_range_regime_overlay`, `santa_claus_rally_overlay`, `sma200_tom_halloween_union_overlay`, `sma50_trend_overlay`, `tom_decomposition_overlay`, `tom_halloween_union_overlay`, `tom_overlay`, `turn_of_month` |
| **panier** de titres (`weights`) | **4** | `january_effect_lowprice_overlay`, `lowvol_sma200_overlay`, `momentum_12_1`, `short_term_momentum` |

## Conventions — posées avant toute édition, aucune inventée

**Indiciel** : schéma `pos`, `r_asset`, `dates`, `cost_bps` (#416).
**Multi-marchés** : sauvegarder le marché **NDX**, marché de référence du
backlog — convention tranchée au #416 pour `santa_vol_targeting_overlay`, reprise
telle quelle plutôt que redécidée.
**Panier** : schéma `pnl_gross_ov`, `pnl_gross_bh`, `turn_ov`, `turn_bh`,
`dates`, `cost_bps` (#419).

Dans les trois cas : **aucune ligne de calcul modifiée**, chaque script lu avant
édition, et le `diff` vérifié avant exécution. Tout script dont la structure ne
correspond à aucune des trois conventions est **écarté et listé**, pas forcé —
le détecteur a déjà écarté 12 candidats au #423 et je ne suis pas passé outre.

## Contrôle de non-régression — le vrai contenu du cycle

Les 17 `results/nonml_<nom>_result.md` doivent être **identiques octet à octet**
avant et après ré-exécution. Toute différence bloque la conclusion et devient le
résultat principal du cycle.

C'est le cinquième lot soumis à ce contrôle (#416 : 10/10 ; #423 : 4/4 ;
#424 : 12/12 ; #426 : 2/2). Dix-sept résultats publiés de plus seraient testés
contre leur propre code, portant le total à **45** — et cette fois ce sont des
**PASS** qui seraient testés, non des FAIL.

## Contrôle de cohérence — repris du #426

Pour chaque `.npz` produit, le nombre de séances stocké doit coïncider avec le
nombre de séances que le rapport du candidat annonce déjà (« N séances
testables »). Un `.npz` produit sans être confronté à rien ne prouve rien.

Écart toléré : **0**. Un désaccord signifierait que la série sauvegardée n'est
pas celle du candidat, et bloquerait la conclusion.

## Mesures publiées après ré-exécution

1. Balayage de doublons rejoué **sans modification** : nombre de séries, de
   groupes exacts et de quasi-doublons, comparés aux 202 / 3 / 1 du #426.
2. **Si un doublon implique deux PASS** : les deux candidats nommés, et l'effet
   chiffré sur le décompte d'hypothèses — sans le corriger dans ce cycle, la
   requalification étant une opération distincte à déclarer séparément (règle
   posée au #415 et tenue depuis).
3. Couverture du balayage de doublons, décomposée non-ML / ML (piste 2 du #426).

## Critère de succès — chiffré

1. **17/17** scripts modifiés et ré-exécutés avec `.npz` produit, ou chaque
   échec **écarté avec sa raison publiée**.
2. **0 différence** sur les 17 fichiers de résultat.
3. **17/17** en accord sur le contrôle de cohérence.
4. Les trois mesures ci-dessus publiées, quelles que soient leurs valeurs.

## Prédiction

**0 différence de résultat** — déductive, comme aux #416, #423, #424 et #426,
tous quatre vérifiés : ajouter une sauvegarde ne touche aucun calcul.

**Aucune prédiction sur le nombre de doublons.** Je n'ai pas de base pour
l'anticiper, et les deux fois où j'ai prédit sans base (#407, #408) je me suis
trompé. C'est précisément la question ouverte du cycle : je refuse de l'orienter
d'avance dans un sens ou dans l'autre.

## Engagements

1. Résultat rapporté tel quel, y compris si aucun doublon n'apparaît — auquel cas
   le lot aura coûté 17 éditions pour confirmer une absence, ce qui reste un
   résultat et sera écrit comme tel.
2. Aucune ligne de calcul modifiée ; chaque script lu avant édition.
3. Aucun verdict PASS/FAIL modifié, aucun décompte d'hypothèses corrigé dans ce
   cycle.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
