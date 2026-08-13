# Audit indépendant — la règle complète du détecteur (#448)

## Contrôle 1 — l'écriture correspond-elle à la règle déclarée ?

Le pré-enregistrement montrait la règle en **expressions régulières**. Le
balayage l'écrit en **opérations de chaînes**, pour ne pas ouvrir une troisième
région de modification (un `import re`). Les deux doivent être équivalentes —
et cela se vérifie, cela ne s'affirme pas.

Cet audit réimplémente la **forme déclarée** et compare les deux sur **chaque
ligne de chaque rapport du dépôt** :

- rapports comparés : **303**
- lignes comparées : **6815**
- lignes où les deux écritures divergent : **0**
- rapports où le **verdict** diffère : **0**

**Aucune divergence.** Les deux écritures sont équivalentes sur l'intégralité
du corpus — ce n'est pas une preuve mathématique, mais une vérification sur
tout le matériau réellement traité.

## Contrôle 2 — non-régression

- rapports classés **identiquement** par le #447 et le #448 : **112**
- rapports **reclassés** : **3**

La règle nouvelle étant plus permissive sur la forme (elle voit les titres) et
plus stricte sur la position (le littéral ne compte plus en cours de phrase),
les deux effets pouvaient se compenser. Ils ne se sont pas annulés : les
reclassements sont tous documentés dans le rapport de cycle.

## Verdict de l'audit

**CONFORME**

- écriture équivalente à la règle déclarée : **oui**
- aucun verdict divergent entre les deux écritures : **oui**

### Ce que cet audit ne prouve pas

Il ne dit pas que la règle est **la bonne façon** de lire un verdict — seulement
qu'elle est **celle qui a été déclarée**, et qu'elle est appliquée partout de la
même manière. Un rapport qui énoncerait son verdict sous une forme encore
différente resterait invisible, et rien ici ne l'exclut.
