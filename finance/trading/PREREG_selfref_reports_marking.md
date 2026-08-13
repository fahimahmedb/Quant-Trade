# Pré-enregistrement — signaler les rapports dépendants du dépôt, plutôt que les appauvrir

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle de **modification déclarée**, régime des #428-#430. Aucune stratégie
évaluée, aucun verdict recalculé, aucun paramètre de stratégie touché.

## Je révise ma propre entrée de file, et je dis pourquoi

Le #438 avait inscrit en tête de file :

> « **Rendre stables les 10 rapports auto-référents** — ne compter que leurs
> propres entrées. C'est la correction de fond : sans elle, chaque tirage futur
> continuera de rencontrer des divergences structurelles, et le dénominateur de
> la borne restera amputé. »

**Je ne fais pas cela, et voici le calcul qui me le fait abandonner.**

Mesuré avant d'écrire : **11** scripts sur un vivier de **290** dépendent du
dépôt, soit **3,8 %**. Un tirage de 24 en rencontre donc **~0,9** en moyenne.
Le « dénominateur amputé » que j'invoquais vaut **moins d'un tirage sur vingt-quatre**.

En face, ce que coûterait le « rendre stable » : supprimer de ces rapports les
décomptes du dépôt — c'est-à-dire exactement l'information que le #428 y avait
**ajoutée à dessein**, pour empêcher un lecteur de surestimer la portée du
balayage. J'appauvrirais un diagnostic pour récupérer 0,9 tirage.

> **Un diagnostic qui décrit l'état du dépôt *doit* changer quand le dépôt
> change.** Sa divergence n'est pas un défaut : c'est son fonctionnement. Le
> défaut serait qu'un lecteur la prenne pour une péremption.

L'action utile n'est donc pas de les stabiliser mais de les **signaler**.

## Ce que ce cycle fait

Ajouter à chaque rapport concerné **une ligne** disant ce qu'il est :

```
> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).
```

Texte **fixé ici**, non ajustable après avoir vu le rendu.

## Ce qui déclenche l'ajout — un test, pas un motif

Le #437 a échoué en identifiant ces scripts par la **forme de leur code**. Le
#438 a montré que le **test comportemental** attrapait ce que le motif ratait.
Ce cycle reprend donc le test, et non la liste syntaxique :

> Pour chaque candidat, on l'exécute une fois, on sauvegarde son rapport, on
> ajoute des fichiers sentinelles neutres au dépôt, on ré-exécute et on compare.
> **Seuls les rapports effectivement modifiés par les sentinelles sont marqués.**

Un candidat repéré par la syntaxe mais que le test **ne confirme pas** n'est
**pas marqué**, et son cas est publié.

Sentinelles supprimées dans un `finally` ; `git status` doit être vide de toute
sentinelle en fin de cycle, sous peine d'échec déclaré.

## Régime de modification — déclaré, comme aux #428-#430

> **Insertions seulement.** Le `diff` de chaque rapport marqué doit contenir
> **0 suppression et 0 modification** de ligne existante. Aucun chiffre, aucun
> verdict, aucune section n'est touché.

C'est le régime du #428, repris tel quel plutôt que redécidé.

## Critère de succès — chiffré

1. Les **11** candidats soumis au test comportemental, chacun **confirmé ou
   écarté** avec sa raison publiée.
2. Chaque rapport confirmé marqué **une fois** (pas de doublon si le cycle est
   rejoué), texte identique à celui ci-dessus.
3. `diff` de chaque rapport marqué : **0 suppression, 0 modification**.
4. **0** sentinelle subsistante.
5. Le nombre de rapports marqués publié, quel qu'il soit.

## Prédiction — déductive, et partiellement déjà vérifiée

Le #438 a déjà classé `empty_pass_basket_extension` comme dépendant du dépôt par
ce même test. Les autres candidats partagent la propriété par construction.

> **Attente : 11/11 confirmés.**

Si l'un n'était **pas** confirmé, cela signifierait que la détection syntaxique
produit des faux positifs — information utile, et je la publierais comme
résultat principal plutôt que de forcer le marquage.

## Engagements

1. Résultat rapporté tel quel, y compris si le test infirme des candidats.
2. Le texte du marqueur n'est pas retouché après avoir vu le rendu.
3. Aucun chiffre ni verdict modifié dans les rapports marqués.
4. Aucune sentinelle laissée derrière.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
