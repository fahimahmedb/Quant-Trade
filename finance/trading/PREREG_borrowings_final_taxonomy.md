# Pré-enregistrement — une **taxonomie complète** des 39 emprunts, et la classe qui manquait

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #507.

## Le trou dans le classement

L'audit du **#505** a montré que les **2** derniers « introuvables » ne le sont
pas : leur nombre **existe** dans le dépôt — l'un dans **1335** fichiers — mais
**jamais au voisinage de son sujet**.

**Ce statut n'a pas de classe.** Les six cycles #500-#505 ont produit des
classes **ad hoc**, chacune répondant à la question du cycle précédent :
« confirmé », « retrouvé ailleurs », « sur-crédité », « valeur suspecte »,
« référence probable ailleurs », « introuvable partout ». Aucune ne dit
*« le nombre existe, mais nulle part au sujet »*.

> Une série qui a produit six vocabulaires successifs doit finir par en fixer
> **un seul**, appliqué à **toute** la population — sinon ses conclusions ne
> sont pas comparables entre elles.

## La taxonomie — **figée ici**, appliquée aux **39** nombres

Sources consultées, **toutes** : les sections `## Backlog #NNN` du registre,
tous les `results/*.md`, tous les `PREREG_*.md`.

Règle contextuelle du **#502 reprise sans modification** — **6 lettres**,
**±200 caractères**, **2 mots-clés**. *(Quatrième cycle consécutif sans y
toucher.)*

| Classe | Condition |
|---|---|
| **A — sourcé au sujet, dans le cycle cité** | nombre **au sujet** dans la section **ou** un rapport du cycle cité |
| **B — sourcé au sujet, ailleurs** | pas en **A**, mais **au sujet** dans une autre source |
| **C — orphelin de contexte** | le nombre **existe** dans le dépôt, mais **jamais au sujet** |
| **D — absent du dépôt** | le nombre n'apparaît **nulle part**, même nu |

**« Au sujet »** = nombre **en gras** (ou **nu**, pour les `PREREG_`) avec
**≥ 2 mots-clés** de l'emprunt dans la fenêtre. **C** est la classe qui
manquait.

Les quatre classes sont **exclusives et exhaustives par construction** : leur
somme doit valoir **39**, et l'audit le vérifiera.

## Le contrôle intégré

Les **2 résidus** du #505 — `content_defined_magnitudes_audit` (#449, **2**) et
`report_idempotence_backtest` (#443, **5,7**) — doivent tomber en **C**. S'ils
tombent ailleurs, **la taxonomie ne recouvre pas le fait qui l'a motivée** et
le cycle échoue son propre contrôle.

## Ce qui est mesuré

1. Les **39** nombres classés par les quatre classes.
2. La **vérification de partition** : somme = effectif.
3. La **classe des 2 résidus du #505** — le contrôle.
4. Les membres de **C**, nommés individuellement.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **quatre classes** citées verbatim, paramètres du #502 **inchangés**.
2. Les **39** classés, partition vérifiée (**somme = effectif**).
3. Les **2 résidus du #505** classés **C** — sinon **FAIL**.
4. Les membres de **C** nommés individuellement.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque, **le contrôle
> compris**.

## Prédictions — falsifiables

1. La classe **D** est **vide** — aucun nombre emprunté n'est absent du dépôt.
2. La classe **C** compte **≥ 2** membres — au moins les deux du #505.
3. La classe **A** est la **plus nombreuse** des quatre.

Si la prédiction 3 est réfutée et que **B** ou **C** domine, alors la majorité
des emprunts de ce dépôt **ne se justifient pas par le cycle qu'ils citent** —
un fait plus grave que tout ce que la série a établi, et qu'il faudra écrire
sans l'atténuer.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun emprunt.
- Il ne **déclare faux** aucun nombre. **C** signifie « je n'ai pas su le
  rattacher », **pas** « il est faux » — six cycles ont montré que la
  distinction est tout.
- Il ne **remplace pas rétroactivement** les classes des #501-#505 dans leurs
  rapports : elles restent telles qu'elles ont été publiées.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **échec du contrôle compris**.
2. Classes, paramètres et population **inchangés** après mesure.
3. Le mot **« orphelin »** ne sera pas durci en « faux » après coup.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
