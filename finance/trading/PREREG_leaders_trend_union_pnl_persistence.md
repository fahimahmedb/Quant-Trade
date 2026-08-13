# Pré-enregistrement — lever l'angle mort des balayages de doublons

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**infrastructure et de test**.

## Le problème, documenté deux fois

Le **#403** a établi que `sma200_leaders_overlay` (#33) et
`leaders_trend_union_overlay` (#41) sont **la même stratégie** : sur les 10273
séances disponibles, le signal « indice à ≥ 95 % de son plus haut 252 j » n'est
**jamais** actif sans le signal « indice au-dessus de sa SMA200 ». Leur union est
donc identiquement égale à SMA200 seul.

Le **#406** puis le **#418** ont balayé les paires à P&L identique. Les deux ont
manqué cette paire sur l'univers d'origine, pour une raison unique et bête :
`nonml_leaders_trend_union_overlay_pnl.npz` **n'existe pas**. Les deux rapports
ont donc dû conclure à une **borne inférieure** plutôt qu'à un décompte.

**Vérification faite avant d'écrire ce pré-enregistrement** (règle étendue au
#417 après une tâche inscrite à tort) : le script ne contient aucun appel à
`np.savez`. La tâche est réelle.

## Modification — une seule

Ajout d'un `np.savez` **inconditionnel** au schéma « panier » déjà utilisé par
son jumeau `sma200_leaders_overlay` (`pnl_gross_ov`, `pnl_gross_bh`, `turn_ov`,
`turn_bh`, `dates`, `cost_bps`). **Aucune ligne de calcul n'est modifiée.**

## Prédiction — tranchée, cette fois

Contrairement aux cycles précédents où je me suis abstenu de prédire, celui-ci
comporte une attente **falsifiable et fondée sur une mesure déjà faite** :

> Le balayage de doublons, rejoué après cet ajout, doit détecter la paire
> `sma200_leaders_overlay` / `leaders_trend_union_overlay` comme **doublon
> exact**, et le décompte d'essais surnuméraires doit passer de **1 à 2**.

Ce n'est pas une intuition sur le marché mais une conséquence arithmétique du
#403 : si les deux signaux coïncident sur toute l'histoire, les deux P&L
coïncident aussi. **Si la prédiction échoue**, c'est que le #403 se trompait ou
que le balayage a un second défaut — dans les deux cas, un résultat plus
important que la tâche elle-même, et à rapporter comme tel.

## Contrôle de non-régression

`results/nonml_leaders_trend_union_overlay_result.md` doit être **identique
octet à octet** avant et après ré-exécution. Toute différence bloque la
conclusion.

## Critère de succès — chiffré

1. `.npz` produit, schéma panier conforme à celui du jumeau.
2. **0 différence** sur le fichier de résultat.
3. Le balayage rejoué **sans modification** publie son décompte ; l'écart avec la
   prédiction ci-dessus est rapporté quel qu'il soit.

**Aucune correction du DSR n'est appliquée** — c'est une opération distincte,
comme aux #406 et #418.

## Engagements

1. Résultat rapporté **tel quel**, y compris si la prédiction est démentie.
2. Aucun seuil du balayage ajusté.
3. **Relecture intégrale des rapports produits avant commit** (engagement #414).
