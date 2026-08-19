# Pré-enregistrement — le #479 applique-t-il sa propre rétractation, déjà publiée au #482 ?

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION, réparation si confirmée**,
deuxième piste de la file ouverte au #526 (« 23 candidats restants de
`hardcoded_figures_remainder` »).

## Le cas le plus net trouvé en examinant le lot

Contrairement aux cas précédents (#523-#526, désaccord d'axe ou
contradiction à établir), celui-ci ne demande **aucune interprétation** :
le **#482** a **explicitement rétracté** un verdict du #479, en toutes
lettres :

> *« Le verdict du #479 sur cette cible est rétracté. Son total passe de
> 18 à 17. »* — à propos de `nonml_reproducibility_sample_lot3_audit.py`.

Le #482 explique : les lignes citées comme « défaut » par le #479 sont
en réalité **à l'intérieur d'un bloc de citation** (`-`/`+`, un diff
reproduit entre deux versions d'un rapport) ; le point décimal de
`73.2 %` — que le #479 avait pris pour un indice de saisie manuelle —
est au contraire **la preuve d'une citation fidèle** à sa source, qui
utilisait cette convention.

## La question à vérifier mécaniquement

Une rétractation **publiée** au #482 a-t-elle été **appliquée** au
dictionnaire `V` du #479 lui-même ? Un examen préliminaire (autorisé,
même précédent que les cycles antérieurs) montre que non — la ligne du
#479 dit encore `("nonml_reproducibility_sample_lot3_audit.py",
"defaut", ...)`. **Ce cycle le confirme mécaniquement avant toute
modification.**

## Le protocole

1. **Lire par script** l'entrée actuelle de `V` pour cette cible dans
   `nonml_hardcoded_figures_remainder_backtest.py` — verdict exact.
2. **Chercher par script**, dans la section `## Backlog #482` du
   backlog, la phrase de rétractation citée ci-dessus (recherche
   littérale, insensible aux emphases markdown).
3. **Si le verdict actuel est toujours `"defaut"` ET que la rétractation
   est bien publiée au #482** : corriger la ligne `V`, citant le #482,
   diff borné à cette seule entrée.
4. **Si le verdict a déjà été corrigé** (pas de dette) : publié comme
   tel, aucune modification.

## Critère de succès — chiffré, il porte sur le procédé

1. Le verdict actuel du #479 pour cette cible publié, cité sur pièce.
2. La phrase de rétractation du #482 retrouvée littéralement, publiée.
3. Le statut « dette confirmée » ou « déjà à jour » établi sans
   ambiguïté.
4. Si dette confirmée : ligne `V` corrigée, diff borné à cette seule
   entrée, citant le #482.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le verdict actuel du #479 est toujours **« defaut »** (la
   rétractation du #482 n'a jamais été appliquée à la source).
2. La phrase de rétractation est retrouvée littéralement dans la
   section `## Backlog #482`.
3. La correction n'affecte **aucune** autre entrée du dictionnaire `V`
   du #479 (diff borné à 1 ligne, la même que celle du #526).

## Ce que ce cycle ne fait pas

- Il ne **revérifie pas** le raisonnement du #482 (bloc de citation,
  convention décimale) — déjà établi et audité en son temps.
- Il ne **vérifie** aucun des 22 autres candidats restants — file
  distincte.
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification/réparation de dépôt, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le verdict est déjà à jour.
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code ou de texte citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
