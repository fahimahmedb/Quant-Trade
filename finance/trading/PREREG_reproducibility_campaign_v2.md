# Pré-enregistrement — campagne de reproductibilité v2 : critère d'auto-référence, puis relance

**Écrit et committé AVANT tout tirage.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## Ce que le #436 a établi, et ce qu'il s'est interdit

Le #436 a trouvé **1 divergence sur 24** : `pnl_duplicate_sweep`. Sa cause n'est
pas un résultat périmé mais un **compteur du dépôt** embarqué dans le rapport —
figure que j'y avais moi-même ajoutée au #428, et que mes propres cycles suivants
ont fait bouger (284 → 289 scripts).

Le #436 a refusé de sauver la borne en écartant ce cas après coup :

> « La distinction est juste ; l'appliquer maintenant serait changer la règle
> après avoir vu le résultat. Elle sera pré-enregistrée dans un cycle ultérieur,
> avec son critère fixé avant tout nouveau tirage, et la campagne repartira de
> là — sans reclasser les 60 tirages actuels. »

Ce cycle tient cet engagement.

## Le critère — mécanique, et fixé avant tout tirage

> Un script est **auto-référent** si son code source contient un balayage de
> l'**ensemble du dépôt** — `glob("nonml_*_backtest.py")`, `glob("*_pnl.npz")`
> ou `glob("nonml_*_result.md")` — dont le résultat alimente une valeur publiée
> dans son rapport.

C'est une propriété du **code**, pas du résultat : elle se vérifie sans exécuter
quoi que ce soit et sans savoir si le script diverge. Un rapport auto-référent
**dérive nécessairement** dès qu'un cycle ajoute un fichier au dépôt ; sa
divergence ne dit rien sur la péremption d'un résultat.

Les scripts auto-référents sont **exclus du vivier** de la campagne, et **listés**.

## Le prix de l'honnêteté, chiffré d'avance

Les 60 tirages des #434-#436 **ne sont pas réutilisés**. La campagne v2 repart
donc de **zéro** :

| | Borne à 95 % |
|---|---|
| revendiqué au #435 (caduc depuis le #436) | 8,0 % |
| **v2 après ce lot, si 24/24** | **11,7 %** |

**La borne va donc empirer.** C'est le coût direct du refus de reclasser après
coup, et je l'inscris avant de mesurer pour qu'il ne puisse pas être présenté
autrement ensuite.

## Le lot — taille et graine fixées maintenant

> **24** scripts tirés avec la graine **20260816**, parmi les éligibles **privés
> des scripts auto-référents**.

Délai **300 s**, régime inchangé : sauvegarde, comparaison, **restauration à
l'identique**. `git status` doit finir vide de toute modification de
`results/*_result.md`.

## Ce que ce cycle ne fait pas

**Il ne corrige aucun rapport auto-référent.** Les rendre stables — ne compter
que leurs propres entrées — modifierait des rapports publiés et relève d'un cycle
de modification déclarée, régime des #428-#430. Il est inscrit à la file, pas
exécuté ici.

**Il ne re-teste pas les 60 anciens tirages.** Leur résultat reste publié tel
quel aux #434, #435 et #436.

## Critère de succès — chiffré

1. Critère d'auto-référence appliqué, scripts exclus **comptés et listés**.
2. **24** scripts tirés avec la graine annoncée, liste publiée **avant** les
   résultats individuels.
3. Chacun classé : identique / divergent (avec `diff`) / non concluant.
4. `git status` vide de toute modification de `results/*_result.md`.
5. Borne v2 publiée, **et** rappel explicite qu'elle est moins bonne que celle
   revendiquée au #435.

## Prédiction

**Aucune prédiction chiffrée** sur les 24 tirages.

Une attente **déductive** en revanche : les scripts auto-référents exclus
devraient tous diverger si on les testait, puisque le dépôt a bougé depuis leur
dernière exécution. Je ne les teste pas — ce serait vérifier une tautologie — et
je n'en tire aucun crédit.

## Engagements

1. Résultat rapporté tel quel, borne v2 comprise, **même si elle est moins
   flatteuse** que le chiffre caduc du #435.
2. Aucun script exclu du tirage après l'avoir vu ; l'exclusion ne porte que sur
   le critère d'auto-référence, appliqué au code.
3. Aucun rapport publié modifié ni committé.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
