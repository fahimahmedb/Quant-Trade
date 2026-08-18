# Pré-enregistrement — **réparer le 13ᵉ**, et dire ce qui reste non réparé

**Écrit et committé AVANT toute mesure et avant toute modification.**
`n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #498.

## La cible

Le **#493** a montré que le verdict « irréparable » du #485 sur
`nonml_reproducibility_campaign_v3_lot2_audit.py` reposait sur une
**justification fausse** (« projection contrefactuelle, aucun univers ») : le
script **possède** `def bound(n)` et publie déjà `{100*bound(cum):.1f} %` à
plusieurs lignes. Le 13ᵉ réparable est donc **ce script**.

## Ce que je répare — **délimité avant de regarder le résultat**

Les chiffres **littéraux du texte publié**, remplacés par la fonction que le
script possède déjà :

- le **titre**, qui écrit la borne en dur ;
- la phrase « 24 tirages de plus feraient passer la borne de **6,2 %** à
  **~4,1 %** » — les deux valeurs deviennent `bound(cum)` et
  `bound(cum + TIRAGES_SUP)`, avec `TIRAGES_SUP = 24` **nommé une fois** et
  utilisé **à la fois** dans la phrase et dans le calcul, pour que les deux ne
  puissent plus diverger.

## Ce que je **ne** répare **pas**, et pourquoi je le déclare d'avance

Le script contient `ok_bound = abs(100 * bound(cum) - 6.2) < 0.2` — un
**littéral de contrôle** qui **garde une section** : si la borne dérivait, tout
un paragraphe disparaîtrait du rapport sans que rien ne le signale. C'est une
**section masquante** au sens du #475.

> **Je n'y touche pas.** Le changer modifierait la **logique** du script, pas
> sa typographie — ce serait sortir de « une interpolation suffirait ». Il sera
> **nommé comme dette restante**, pas corrigé en douce.

Déclarer cette limite **maintenant** est le seul moyen qu'elle ne soit pas
rétrospective.

## La règle du geste borné — reprise du #489, appliquée telle quelle

1. La **classe** du script est établie **par AST**, avec la règle du #497
   (12 primitives) — **pas supposée**. S'il exécute un tiers, **on s'arrête**.
2. Le script est exécuté **une fois**.
3. Le **diff de son rapport** doit se réduire **aux lignes portant ces
   chiffres**. **Toute autre ligne modifiée fait échouer le cycle.**
4. En cas d'échec : **restauration ciblée** du rapport et du script, **rien
   n'est committé**, et le FAIL est publié.

> Le #495 a échoué sur ce point et a tout restauré. Le même barème s'applique
> ici, sans adoucissement.

## Ce qui est mesuré

1. La **classe** du script cible, par les 12 primitives du #497.
2. Le **diff du `.py`** : lignes changées, publiées.
3. Le **diff du rapport** : lignes changées, publiées **en entier**.
4. Les **valeurs calculées** face aux littéraux qu'elles remplacent :
   `100*bound(cum)` vs `6,2` et `100*bound(cum+24)` vs `4,1`.

## Critère de succès — chiffré

1. Classe du script établie **par AST** et non supposée ; **0** primitive
   d'exécution d'un tiers.
2. Diff du `.py` publié, **limité** aux lignes de ces chiffres.
3. Diff du rapport **réduit aux lignes portant ces chiffres** — **0** autre
   ligne.
4. Valeurs calculées publiées **face aux littéraux**, écart compris.
5. Le littéral de contrôle `6.2` **nommé comme dette restante**, non modifié.

> **PASS** = les cinq points. **FAIL** = un seul manque, et tout est restauré.

## Prédictions — falsifiables

1. Le script est de **classe A** : **0** primitive d'exécution d'un tiers.
2. `100*bound(cum)` vaut **6,2** à l'arrondi publié — donc le rapport
   régénéré est **identique** sur cette valeur, et le diff se réduit au titre
   et à la phrase seulement si l'écriture change, **sinon il est vide**.
3. `100*bound(cum+24)` **diffère** de `4,1` — le « ~4,1 » était une
   approximation tapée à la main, pas un arrondi de la fonction.

Si la prédiction 2 est réfutée, alors le littéral **6,2** était **périmé** :
le rapport publiait depuis sa création un chiffre que son propre code
contredisait, et ce serait un défaut plus grave que la simple duplication.

## Ce que ce cycle ne fait pas

- Il ne modifie **aucun autre script**, ne régénère **aucun autre rapport**.
- Il ne touche **pas** au littéral de contrôle `6.2`.
- Il ne touche **pas** aux données (`data/`), jamais.

## Simulation 300 € et robustesse

**Sans objet** : cycle de réparation, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **FAIL et restauration compris**.
2. Périmètre de réparation **inchangé** après mesure.
3. La dette laissée en place est **nommée**, jamais tue.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
