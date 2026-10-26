# Avancement — Lot IA-0, trois décisions

> Sauvegardé ici lors de son traitement (docs/context-strategy.md) plutôt que
> de rester seulement dans l'historique de conversation. Voir
> `docs/bilan-ia-0.md` §3/§6 et `docs/handoffs/` pour l'état d'application.

## F6 / IA-08 — lecture confirmée

**Décision** : la lecture retenue par Claude Code est validée par le porteur du projet — « détecter et exclure les occurrences aberrantes (> 3× la médiane du jour), puis appliquer la moyenne pondérée par récence du document sur le reste » est la résolution correcte de la contradiction entre §4 et §6.3 (IA-08) de `specs-v2-ia-plan-test.md`.

**Ce qui est demandé** : ce n'était pas une hypothèse à retester, seulement à faire confirmer — aucun changement de comportement. Seule action : retirer la mention « à faire confirmer, c'est une lecture, pas un arbitrage du porteur du projet » du bilan et des commentaires de code associés, et la remplacer par une simple référence à ce document comme confirmation actée.

---

## SYN-D — garde-fou du cas dégénéré, formalisé

**Le problème, rappelé** : la règle « anomalie ponctuelle si écart > 3 × la médiane des écarts historiques » est dégénérée quand l'ingrédient a été conforme jusqu'ici — médiane nulle, donc 3 × 0 = 0, donc le moindre gramme de bruit déclencherait le badge. Le repli actuel (50 % du stock) est arbitraire : trop sensible sur un petit stock, jamais déclenché sur un gros — ce n'est pas une mesure de valeur, alors que tout le reste du système raisonne en euros.

**Règle formalisée, à implémenter** :

> Quand la médiane des écarts historiques valorisés de l'ingrédient est nulle, remplacer le seuil « 3 × médiane » par un **seuil absolu en euros**, identique et **réutilisant la même variable réglable** que celle déjà définie pour la perte récurrente (défaut 10 €, réglage `Settings`) — pas une nouvelle constante à maintenir séparément. Un écart ponctuel valorisé au-delà de ce seuil, sur un ingrédient jusqu'ici toujours conforme, est badgé « inhabituel ».

**Pourquoi cette formalisation plutôt qu'une autre** : elle réutilise un seuil déjà défini et réglable par le restaurateur (cohérence avec §8 des specs — « valeurs de départ raisonnées, réglables, à revoir après le pilote »), elle raisonne en euros comme tout le reste du système d'écarts (au lieu d'un pourcentage de stock, qui n'a pas de sens comparable d'un ingrédient à l'autre), et elle évite une constante supplémentaire à faire vivre en parallèle du seuil de perte récurrente pour un concept très proche.

**Ce qui est demandé** :
1. Remplacer le repli « 50 % du stock » par ce seuil absolu réutilisé.
2. Étendre SYN-D pour couvrir explicitement les deux régimes, pas seulement le cas dégénéré actuel :
   - **SYN-D1** (médiane non nulle) : ingrédient avec un historique d'écarts variables ; injecter une occurrence à exactement 3,1× la médiane → badge déclenché ; à 2,9× → pas de badge. Vérifie que la règle nominale du document reste bien celle qui s'applique dès que la médiane est utilisable.
   - **SYN-D2** (médiane nulle, cas actuel) : injecter un écart juste au-dessus du seuil de 10 € → badge ; juste en dessous → pas de badge. Remplace le test actuel basé sur 50 % du stock.
3. Mettre à jour le commentaire du code et le bilan pour retirer la mention « garde-fou ad hoc, à trancher au pilote » — ce n'est plus ad hoc, c'est spécifié.

---

## Modèle et effort recommandés

**Sonnet, effort par défaut**, pour les trois points. Le seul qui demandait un vrai jugement — le choix du garde-fou SYN-D — vient d'être tranché ci-dessus ; il ne reste que de la traduction en code et en tests d'une règle déjà précisée, pas de la conception à inventer. Si en écrivant le fixture du point 1 ou les cas limites du point 3 une ambiguïté apparaît que ce document ne couvre pas, la remonter plutôt que trancher seul.
