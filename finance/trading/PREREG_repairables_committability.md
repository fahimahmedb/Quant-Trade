# Pré-enregistrement — les **13 réparables**, sous le critère de **committabilité**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #506.

## Ce que le #499 a établi

Le **#485** puis le **#493** ont compté **13 réparables** : des chiffres
publiés en dur qu'une **interpolation** suffirait à dériver, puisque le script
possède déjà de quoi les calculer.

Le **#499** a tenté la réparation du 13ᵉ. Elle était **parfaite** — le `.py`
correct, **0 ligne** de diff sur les valeurs. **Et elle a échoué** : régénérer
le rapport en réécrivait **28 lignes** de dérive, sans rapport avec la
réparation.

> **Un chiffre dérivable n'est pas pour autant réparable par un geste borné.**
> Le compte « 13 réparables » mesure la **dérivabilité** ; personne n'a mesuré
> la **committabilité**.

## La règle — **figée ici**, statique, sans aucune exécution

Un rapport ne peut être régénéré proprement que si son script ne **dépend pas
de l'état courant du dépôt**. Deux causes de dérive, établies par **AST** :

- **NC1 — exécute un tiers** : le script déclenche l'une des primitives
  **P1, P2, P9 ou P10** du **#497** (règle **importée**, non recopiée). Le
  régénérer déclencherait une **cascade** de périmètre inconnu ;
- **NC2 — lit l'état courant** : il appelle `glob`/`iterdir`/`rglob` sur
  `scripts/` ou `results/`, **ou** invoque `git`. Sa sortie **bouge avec le
  dépôt**, indépendamment de toute réparation.

| Classe | Condition |
|---|---|
| **NC1** | exécute un tiers |
| **NC2** | ne l'exécute pas, mais lit l'état courant |
| **C** | ni l'un ni l'autre — **candidat** committable |
| **?** | script ou rapport introuvable |

## Ce que cette règle **ne peut pas** faire, dit d'avance

Elle donne une **borne supérieure** de la committabilité. Un script classé
**C** peut encore dériver pour une raison qu'elle n'énumère pas — une lecture
de fichier daté, un compteur externe. **Seule l'exécution trancherait, et le
#499 a montré ce qu'elle coûte.**

> **C** se lit donc « **candidat** », jamais « committable ». Le mot est choisi
> avant la mesure pour que le rapport ne puisse pas le durcir après.

## Le contrôle intégré

La cible du **#499** — `nonml_reproducibility_campaign_v3_lot2_audit.py` — est
**connue non committable par l'expérience**. Si la règle statique la classe
**C**, **la règle est fausse** et le cycle échoue son propre contrôle.

## Ce qui est mesuré

1. La population des **13 réparables**, dérivée par code : les `### … —
   réparable` du recensement du #485, **plus** le 13ᵉ requalifié au #493.
2. Les **quatre classes**, comptées.
3. La classe de la **cible du #499** — le contrôle.
4. Les **candidats C** nommés individuellement.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle et ses **quatre classes** citées verbatim, établies par **AST**,
   la règle du #497 **importée**.
2. Population **dérivée par code** (**13** attendus), et son écart publié si
   elle diffère.
3. Les quatre classes comptées, et la **cible du #499** classée **NC1 ou
   NC2** — sinon **FAIL**.
4. Les **candidats C** nommés individuellement.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque, **le contrôle
> compris**.

## Prédictions — falsifiables

1. La cible du #499 est classée **NC2** — elle globbe et appelle `git`.
2. **≥ 8** des 13 sont **non committables** (NC1 ou NC2).
3. **≥ 1** reste **candidat C** — la règle ne condamne pas tout.

Si la prédiction 3 est réfutée et qu'**aucun** des 13 n'est candidat, alors
**le compte « 13 réparables » du dépôt ne décrit rien d'actionnable**, et il
faudra le dire : la dette serait **non pas partiellement, mais entièrement**
hors de portée d'un geste borné.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, n'en **modifie** aucun, ne **répare** rien.
- Il ne **contredit** pas le #485/#493 : la dérivabilité qu'ils ont mesurée
  reste vraie. **Ce cycle mesure autre chose.**

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **échec du contrôle compris**.
2. Règle, classes et population **inchangées** après mesure.
3. Le mot **« candidat »** n'est pas durci après coup.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
