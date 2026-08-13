# Pré-enregistrement — la phrase figée du balayage : « les deux » contre un compte calculé

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, second du genre après le #445, et conduit avec la même
discipline : régime de modification annoncé ligne à ligne, effet attendu déclaré,
critère qui peut échouer.

## Le défaut, exposé au #445

Le rapport du balayage contient (lignes 194-195 du script) :

```python
L.append(f"**{verdicts['PASS']}** PASS sont les deux candidats écartés au #427 avec leur raison")
L.append("publiée (variantes multiples, et un diagnostic qui n'est pas une stratégie).")
```

Le **compte est calculé**, la **prose est figée**. Tant que le compte valait 2, la
phrase était vraie. La dérive du dépôt l'a portée à **4**, et le rapport publie
désormais « **4** PASS sont **les deux** candidats… » — une phrase fausse, et
fausse deux fois : le nombre ne concorde pas, et l'**identité** affirmée (« les
candidats du #427 ») ne peut pas couvrir des scripts apparus depuis.

C'est le même genre de défaut que le #428 (`284 − 208`) : une **affirmation non
mesurée** enchâssée dans une phrase d'apparence factuelle.

## Ce que je n'ai pas encore regardé

**Je n'ai pas listé les 4 scripts concernés.** Le #445 n'a mesuré que leur
nombre. Leur identité est inconnue au moment où j'écris ces lignes, et le
critère ci-dessous est fixé sans elle.

## La modification — régime annoncé

**Remplacement du bloc des lignes 194-195** (2 lignes) par une énumération
**calculée** des scripts concernés. Régime : *remplacement d'un bloc annoncé,
insertions autorisées à l'intérieur de ce bloc uniquement*.

Toute ligne du balayage touchée **hors de ce bloc** vaut **échec du cycle**,
indépendamment du résultat.

Le remplacement doit satisfaire une exigence de fond : **ne plus jamais affirmer
d'identité non calculée**. La phrase nouvelle nomme les scripts qu'elle compte,
et n'attribue au #427 que ceux qui s'y rattachent réellement.

## Critère de succès — chiffré, et il peut échouer

1. `git diff` du balayage **confiné au bloc annoncé** : aucune ligne modifiée
   hors de l'intervalle 194-195.
2. Chaque nom publié par la phrase nouvelle est **vérifié indépendamment** par
   l'audit : il est bien un script non-ML sans `.npz` dont le rapport porte un
   PASS. **Aucun nom affirmé sans contrôle.**
3. **Idempotence** : deux exécutions successives du balayage produisent un
   rapport **identique au bit près**. Une phrase calculée qui varierait d'une
   exécution à l'autre n'aurait rien réglé.
4. Chaque différence entre le rapport committé et le rapport régénéré est
   **attribuée** : au bloc modifié, ou à la dérive du dépôt. Aucun changement
   inexpliqué — discipline du #445, où 9 des 10 lignes n'étaient pas de moi.

> **PASS** = les quatre points tenus.
> **FAIL** = diff hors bloc, ou un nom non vérifiable, ou un rapport non
> idempotent, ou une différence inexpliquée.

## Prédiction — falsifiable

Déductive, faute d'avoir regardé : le compte est passé de 2 à 4 pendant les
cycles #442-#445, qui ont ajouté des scripts d'**inventaire** produisant un
rapport sans `.npz`. J'attends donc que **les 2 nouveaux soient des scripts
d'inventaire récents**, et non des stratégies.

Si ce sont en réalité des **stratégies** portant un PASS et échappant au
balayage de doublons, ce serait un résultat **plus important que la correction
de prose** : cela signifierait que des candidats PASS ne sont pas contrôlés
contre les doublons. Il serait publié en tête du rapport de cycle.

## Ce qui n'est pas fait ici

- **Aucun verdict de stratégie n'est recalculé.**
- Les **3 consommateurs de catégorie C** du #444 restent inchangés.
- Aucun autre rapport que celui du balayage n'est régénéré.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL** de ma propre correction.
2. Aucune ligne touchée hors du bloc annoncé — vérifié par `git diff`, pas
   affirmé.
3. Aucun nom publié sans vérification indépendante.
4. Aucun retuning : le remplacement est celui décrit ci-dessus, décidé avant
   d'avoir vu quels scripts il nomme.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
