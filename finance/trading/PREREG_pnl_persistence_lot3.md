# Pré-enregistrement — persistance du P&L, lot 3 (les 12 différés du #423)

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**infrastructure et de vérification**.

## Ce que le #423 a différé, et pourquoi

Le #423 devait doter 16 candidats d'un `.npz`. La lecture script par script en a
écarté 12 : ils ne suivent pas la convention indicielle simple. Le détecteur les
a refusés de lui-même, et je ne suis pas passé outre.

**Vérification faite avant d'écrire ce pré-enregistrement** (règle du #400,
étendue au #417 puis au #420) : les 12 se répartissent en **deux structures**,
comptées par lecture du code.

| Structure | Nombre | Candidats |
|---|---|---|
| boucle **multi-marchés** (`MARKETS`) | **9** | `acf_lag1`, `bollinger_width`, `drawdown_depth`, `gap_risk`, `goldencross`, `lowvol_regime`, `skewness`, `trend_lowvol`, `parkinson_c2c_ratio` |
| **panier** de titres (`weights`) | **3** | `lowvol_trend`, `momentum_consistency_trend`, `momentum_consistency_trend_15` |

## Conventions — posées avant toute édition

**Multi-marchés** : sauvegarder le marché **NDX**, marché de référence du
backlog. C'est la convention déjà tranchée au #416 pour `santa_vol_targeting_overlay`,
reprise ici telle quelle plutôt que redécidée. Schéma indiciel
(`pos`, `r_asset`, `dates`, `cost_bps`).

**Panier** : schéma panier (`pnl_gross_ov`, `pnl_gross_bh`, `turn_ov`, `turn_bh`,
`dates`, `cost_bps`), comme au #419 pour `leaders_trend_union_overlay`.

Dans les deux cas : **aucune ligne de calcul modifiée**, chaque script lu avant
édition. Tout script dont la structure ne correspond à aucune des deux
conventions est **écarté et listé**, pas forcé.

## Contrôle de non-régression — le vrai contenu du cycle

Les fichiers `results/nonml_<nom>_result.md` de tous les scripts modifiés doivent
être **identiques octet à octet** avant et après ré-exécution. Toute différence
bloque la conclusion et devient le résultat principal.

C'est le troisième lot soumis à ce contrôle (#416 : 10/10 identiques ; #423 :
4/4). Quatorze résultats publiés supplémentaires seraient ainsi testés contre
leur propre code.

## Mesures publiées après ré-exécution

1. Couverture du volet B du balayage #415, avant et après (46/62 actuellement).
2. Nombre de candidats **structurellement inactifs** au seuil de 2 % (repris du
   #410), avec la discrimination du #416 pour chacun.
3. Balayage de doublons rejoué **sans modification** : nombre de groupes exacts,
   comparé aux 3 du #419.

## Critère de succès — chiffré

1. Chaque script du lot est soit modifié et ré-exécuté avec `.npz` produit, soit
   **écarté avec sa raison publiée**.
2. **0 différence** sur les fichiers de résultat des scripts modifiés.
3. Les trois mesures ci-dessus publiées, quelles que soient leurs valeurs.

## Prédiction

**0 différence de résultat** — déductive, comme aux #416 et #423 : ajouter une
sauvegarde ne touche aucun calcul.

**Aucune prédiction** sur le nombre d'inactifs ou de nouveaux doublons.

## Engagements

1. Résultat rapporté tel quel, y compris si le lot ne révèle rien — les 12
   portent tous un FAIL, donc aucun verdict ne peut changer, et je l'écris avant
   de commencer pour ne pas survendre l'issue.
2. Aucune ligne de calcul modifiée.
3. Dette restante re-chiffrée au backlog.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
