# Pré-enregistrement — persistance du P&L, lot 2 (les 16 candidats non mesurés du #415)

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**infrastructure et de vérification**.

## Lot défini, pas « la dette entière »

Le dépôt compte 114 scripts à `savez` conditionnel et 130 sans aucun `savez`. Les
traiter en masse reproduirait le geste des #392 et #404. Ce cycle traite **un lot
fermé et vérifiable** : les **16** candidats que le balayage du #415 détecte comme
portant la structure à risque mais qu'il ne peut pas mesurer, faute de `.npz`,
**et** qui s'exécutent hors ligne.

Vérification faite avant d'écrire : les 16 n'appellent aucun `np.savez` et ne
dépendent d'aucune source externe. Les 4 autres candidats non mesurés du #415
sont écartés — trois ont déjà un `.npz` au schéma panier (que le volet B ne sait
pas lire, limite distincte), un dépend d'une source externe.

## Ce que ce lot apporte — et ce qu'il n'apporte pas

**Ce qu'il apporte** : le volet B du balayage #415 passe de 42 candidats mesurés
sur 62 à environ 58, et le balayage de doublons gagne 16 séries.

**Ce qu'il n'apporte pas** : les 16 portent tous un **FAIL**. Aucun verdict ne
peut donc changer, et le #421 a mesuré que `n_trials` est immatériel (il faudrait
`n_trials ≤ 3` pour franchir le seuil DSR). Le gain est la **complétude des
outils de diagnostic**, pas une correction de résultat. Je l'écris avant de
commencer pour ne pas être tenté de survendre l'issue après coup.

## Contrôle de non-régression — le vrai contenu du cycle

Les **16** `results/nonml_<nom>_result.md` doivent être **identiques octet à
octet** avant et après ré-exécution. Comme au #416, c'est ce contrôle qui a de la
valeur en soi : il teste seize résultats publiés contre leur propre code, dont
certains antérieurs aux corrections des #375-#404.

Toute différence bloque la conclusion et devient le résultat principal du cycle.

## Mesures publiées après ré-exécution

1. Couverture du volet B du #415, avant et après.
2. Nombre de candidats du lot **structurellement inactifs** au seuil de 2 %
   (repris tel quel du #410) — et pour chacun, la discrimination du #416 :
   P&L identique à Buy & Hold (neutralisé) ou simplement rare.
3. Balayage de doublons rejoué **sans modification** : nombre de doublons exacts,
   comparé aux 3 groupes du #419.

## Critère de succès — chiffré

1. **16/16** scripts modifiés, ré-exécutés, `.npz` produit.
2. **0 différence** sur les 16 fichiers de résultat.
3. Les trois mesures ci-dessus publiées, quelles que soient leurs valeurs.

## Prédiction

**0 différence de résultat** (déductive : ajouter une sauvegarde ne touche aucun
calcul — même raisonnement qu'au #416, où 10/10 étaient identiques).

**Aucune prédiction** sur le nombre d'inactifs ou de nouveaux doublons : je n'ai
pas de base pour l'anticiper, et les deux fois où j'ai prédit sans base
(#407, #408) je me suis trompé.

## Engagements

1. Résultat rapporté tel quel, y compris si le lot ne révèle rien.
2. Aucune ligne de calcul modifiée ; chaque script lu avant édition.
3. Dette restante re-chiffrée au backlog après ce lot.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
