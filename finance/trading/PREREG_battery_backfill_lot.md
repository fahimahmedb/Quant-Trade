# Pré-enregistrement — soumettre à la batterie les PASS postérieurs à la Règle 9

**Écrit et committé AVANT toute exécution.** `n_trials = 1` pour ce cycle
d'infrastructure. Aucune stratégie nouvelle, aucun paramètre touché, **aucun
verdict de niveau 1 modifié**.

## La dette, telle que le #431 l'a établie

L'inventaire du #431 a trouvé **6** PASS publiés strictement après l'introduction
de la Règle 9 (2026-07-29) sans avoir été soumis à la batterie de validation.
L'un des six, `capitulation_gate_floor_sweep`, est un **diagnostic et non une
stratégie** (faux positif de détection, établi au #427) : il est écarté d'office.

Restaient **5** candidats. Vérification faite **avant** ce pré-enregistrement, en
lisant les `.npz` :

| Candidat | Schéma | Séances | Activation |
|---|---|---|---|
| `gjr_vol_managed_russell2000` | indiciel | 9031 | 65,8 % |
| `gjr_vol_managed_sp500` | indiciel | 13501 | 83,9 % |
| `deep_drawdown_breadth_vol_targeting_overlay_pit_universe` | indiciel | 2645 | 25,8 % |
| `weakness_breadth_vol_targeting_overlay_pit_universe` | indiciel | 2896 | **0,00 %** |
| `january_effect_lowprice_overlay_pit_universe` | **panier** | 2900 | — |

## Deux écarts au « lot de 5 », constatés avant de commencer

**1. Un candidat est hors de portée de l'outil.**
La batterie exige le schéma indiciel (`pos`, `r_asset`, `dates`, `cost_bps`) —
sa docstring le dit. `january_effect_lowprice_overlay_pit_universe` porte le
schéma **panier**. Il est **écarté et listé**, pas forcé : lui fabriquer une
position scalaire serait inventer une donnée. Le lot exécutable est donc de
**4**.

**2. Un candidat est un PASS structurellement vide.**
`weakness_breadth_vol_targeting_overlay_pit_universe` active l'overlay **0,00 %**
du temps : son P&L est identique à celui de Buy & Hold, fait établi au #415 puis
au #417, et son rapport porte déjà l'étiquette « PASS NON INFORMATIF ».

Je le soumets quand même — l'écarter serait choisir quels candidats passent
l'examen — mais **je déclare d'avance** que son résultat ne dira rien d'un edge :
une série identique au benchmark ne peut ni le battre ni lui être inférieure.
Tout verdict le concernant doit se lire ainsi, et non comme une validation.

## Prédiction — déductive, et défavorable

Le contrôle (e) de la batterie calcule le **DSR** avec `n_trials` = taille du
backlog. Aux #111 et #112, ce contrôle a été mesuré à `n_trials = 110` et la
conclusion écrite alors était sans ambiguïté :

> « à n_trials=110, le seuil de sélection DSR est si élevé qu'**aucune hypothèse
> individuelle de ce backlog n'a de chance réaliste de le dépasser seule** ».

Le backlog compte aujourd'hui **plus de 430** entrées. Le seuil est donc **plus
sévère encore** qu'à l'époque où il était déjà jugé inatteignable.

> **Attente : 0 des 4 candidats ne passe les 5 contrôles**, l'échec venant au
> minimum du DSR.

C'est une prédiction **déductive** — elle découle d'un résultat déjà mesuré, pas
d'un mécanisme économique supposé. Les deux fois où j'ai prédit un mécanisme
(#407, #408), je me suis trompé ; les prédictions déductives (#419, #422, #425 à
#430) se sont vérifiées. Je maintiens la distinction.

**Ce cycle ne cherche donc pas à valider quoi que ce soit.** Il applique un
filtre que le backlog s'impose, à des candidats qui y avaient échappé, et publie
le résultat quel qu'il soit. Si un candidat passait malgré tout, ce serait le
résultat principal du cycle et il devrait être ré-examiné avant toute célébration.

## Critère de succès — chiffré

1. **4/4** candidats exécutables soumis à la batterie, résultats publiés.
2. **1/1** candidat écarté avec sa raison publiée (schéma panier).
3. Pour chacun des 4 : les **5** contrôles reportés individuellement, y compris
   ceux qui passent.
4. **Aucun verdict de niveau 1 modifié** : la batterie **ajoute** un jugement,
   elle n'annule pas le PASS pré-enregistré. Toute reclassification éventuelle
   est signalée comme telle, pas appliquée en silence.

## Engagements

1. Résultat rapporté tel quel, y compris si les 4 échouent — ce serait l'issue
   annoncée, donc sans mérite particulier, et je l'écrirai ainsi.
2. Aucun seuil de la batterie modifié, aucun `n_trials` ajusté. Le fait que
   `n_trials` soit lu par expression régulière dans la prose du backlog reste
   **porté à l'arbitrage** (#421) et n'est pas contourné ici.
3. Aucun candidat retiré du lot après avoir vu son résultat.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
