# Pré-enregistrement — une confrontation **par le contexte**, pas par la présence

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #501.

## Pourquoi la règle du #501 ne suffit pas

Le #501 a confronté **39** nombres empruntés en cherchant leur présence **en
gras** dans la section du cycle cité. Résultat : **22 confirmés**, dont **19**
portant sur un nombre à 1-2 chiffres — c'est-à-dire retrouvables **par
hasard**. Il ne restait que **3** confirmations probantes, et son rapport a
conclu que **la méthode ne départage pas**.

> Chercher **un nombre** ne prouve rien. Il faut vérifier qu'il apparaît **au
> même sujet**.

## La règle contextuelle — **figée ici, paramètres compris**

Pour un emprunt de chaîne `T`, citant `#NNN`, de nombre en gras `x` :

- **mots-clés de l'emprunt** : les mots de `T` d'au moins **6 lettres**,
  minusculisés, ponctuation et balisage retirés, **chiffres exclus**. Le seuil
  de 6 lettres écarte l'essentiel des mots outils du français **sans liste
  d'exclusion**, qui serait un réglage déguisé ;
- **fenêtre** : **±200 caractères** autour de chaque occurrence en gras de `x`
  dans la section `## Backlog #NNN` ;
- **recouvrement exigé** : **au moins 2** mots-clés de l'emprunt présents dans
  la fenêtre.

**Classes** :

| Classe | Condition |
|---|---|
| **confirmé en contexte** | `x` en gras dans la section **et** ≥ 2 mots-clés dans la fenêtre |
| **présent sans contexte** | `x` en gras dans la section, **< 2** mots-clés |
| **absent de la section** | `x` n'est pas en gras dans la section |
| **contexte indisponible** | l'emprunt porte **moins de 2** mots-clés — la règle **ne peut pas** conclure |
| **non vérifiable** | la section `## Backlog #NNN` n'existe pas |

**Les trois paramètres — 6 lettres, ±200 caractères, 2 mots-clés — sont figés
ici et ne bougeront pas après mesure**, quel que soit le résultat.

La classe **contexte indisponible** est déclarée d'avance parce qu'un emprunt
trop court ne peut pas être jugé : la compter parmi les échecs accuserait
l'emprunt d'un défaut de **ma règle**.

## Ce qui est mesuré

1. Les **39** nombres reclassés par la règle contextuelle.
2. La **table de transition** avec les classes du #501 — qui monte, qui tombe.
3. Les emprunts que le #501 disait **confirmés** et qui deviennent **présents
   sans contexte** : ceux que l'ancienne règle **sur-créditait**.
4. Les emprunts **confirmés en contexte** avec un nombre à **1-2 chiffres** :
   ceux que le contexte **sauve** là où la taille du nombre ne prouvait rien.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle et ses **trois paramètres** cités verbatim.
2. Les **39** nombres reclassés, **cinq classes** publiées avec leur compte.
3. La **table de transition** #501 → #502 publiée en entier.
4. Sur-crédités et sauvés **nommés individuellement**.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **confirmés en contexte** sont **≥ 10** sur 39.
2. Ils sont **plus nombreux que les 3 confirmations fortes** du #501 — la
   règle contextuelle **prouve davantage** que la coupure par taille.
3. **Au moins 1** emprunt classé « confirmé » au #501 tombe en « présent sans
   contexte » — l'ancienne règle sur-créditait.

Si la prédiction 2 est réfutée, alors **le contexte n'apporte rien** et deux
cycles auront échoué à établir la justesse de ces emprunts. Je devrai
l'écrire ainsi, et cesser d'affiner une méthode qui ne mord pas.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun emprunt.
- Il ne **déclare faux** aucun chiffre : « absent de la section » reste un
  **soupçon**, pas un verdict.
- Il ne **remplace** pas la règle du #501 — les deux sont publiées **côte à
  côte**, et c'est la comparaison qui est le résultat.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le contexte **n'apporte rien**.
2. Les **trois paramètres inchangés** après mesure.
3. Les deux règles publiées **côte à côte**, jamais la seule favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
