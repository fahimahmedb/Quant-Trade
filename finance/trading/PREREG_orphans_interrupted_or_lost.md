# Pré-enregistrement — les orphelins du #464 : **cycle interrompu** ou **trace perdue** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #473 — et
troisième piste de celle du #464, restée en attente depuis.

## La dette à lever

Le **#464** a laissé deux comptes sans diagnostic :

| Population | Nombre | Ce qu'on en sait |
|---|---|---|
| entrées citant un `PREREG_` **sans aucun fichier** portant leur `<nom>` | **10** | rien |
| `PREREG_` du dépôt dont **aucune entrée ne parle** | **24** | rien |

Le #464 les a comptés et s'est arrêté là, en inscrivant la tâche :
« établir, pour chacun, s'il s'agit d'un **cycle interrompu** ou d'une **trace
perdue** ». **Ce cycle l'établit.**

## Les deux populations — dérivées, pas recopiées

Elles sont **re-dérivées** par le code du #464 (`entrees`, `CITE`, puis la même
classification post-hoc), et non recopiées à la main. Si les comptes ont bougé
depuis le #464, **les nouveaux chiffres sont publiés tels quels** et l'écart est
signalé — un compte de backlog est daté, comme l'ont montré les #436-#438.

## La règle de classement — fixée ici, avant de regarder

Pour chaque `<nom>` des deux populations, trois faits mécaniques, lus sur le
dépôt et sur `git log --all` :

- **R** — un rapport `results/nonml_<nom>*.md` existe **aujourd'hui** ;
- **H** — un tel rapport a existé **à un commit quelconque** de l'historique ;
- **S** — un script `scripts/nonml_<nom>*.py` existe aujourd'hui.

Le classement en découle, sans jugement :

| R | H | Classe |
|---|---|---|
| faux | **vrai** | **TRACE PERDUE** — un rapport a existé, il n'existe plus |
| faux | faux | **CYCLE INTERROMPU** — aucun rapport n'a jamais été committé |
| **vrai** | — | **CYCLE COMPLET** — le rapport est là ; l'anomalie est ailleurs |

Pour les **cycles interrompus**, une sous-distinction, également mécanique :
**S vrai** = interrompu *après* écriture du script ; **S faux** = interrompu *au
pré-enregistrement*.

La règle est **exhaustive par construction** — tout `<nom>` tombe dans une
classe. **Ce n'est donc pas un critère de succès**, et je ne le compterai pas
comme une prédiction vérifiée.

## Ce que « cycle complet » voudra dire pour les 24

Un `PREREG_` orphelin dont le rapport existe n'est **pas** un cycle interrompu :
c'est un cycle qui a tourné et dont **l'entrée de backlog manque ou nomme
autrement**. C'est une anomalie de **trace écrite**, pas de travail non fait, et
le rapport devra le distinguer explicitement plutôt que de fondre les deux dans
un seul total.

## Critère de succès — chiffré, il porte sur le procédé

1. Les deux populations **re-dérivées par code**, leurs effectifs publiés, et
   tout écart au #464 **signalé**.
2. **100 %** des `<nom>` des deux populations classés, chacun **nommé** dans le
   rapport avec ses trois faits R/H/S.
3. Pour toute **trace perdue**, le **commit de suppression** publié — sinon la
   classe est un mot sans preuve.
4. Le total « cycle complet » **séparé** du total « interrompu », jamais additionné.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Sur les **24** `PREREG_` orphelins, **≥ 12** sont des **cycles complets** —
   l'anomalie y est une entrée de backlog manquante, pas du travail non fait.
   *(Fondement : le #464 a montré que 206 des 230 « orphelins » bruts étaient en
   fait mentionnés ailleurs ; la trace écrite est le maillon faible, pas le
   travail.)*
2. Sur les **10** entrées sans fichier, **≥ 6** sont des **cycles interrompus**
   (`H` faux) et non des traces perdues.
3. **Au moins 1 trace perdue** est trouvée sur l'ensemble des deux populations.
   *(Fondement : le #450 a effacé des rapports, et le #451 en a rétabli 4.)*

Si la prédiction 3 est réfutée — **zéro trace perdue** — alors la dette du #464
se réduit entièrement à des cycles inachevés et à des entrées manquantes, et
**aucun rapport n'a jamais été perdu par ce dépôt**. Ce serait un résultat
favorable, et je devrai me méfier de lui : le critère 3 impose alors de publier
la commande exacte qui a cherché, pour qu'un lecteur puisse la refaire.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien : ni entrée de backlog ajoutée, ni `PREREG_` supprimé,
  ni rapport régénéré.
- Il n'**exécute** aucun script du dépôt : lecture du disque et de `git log`,
  **aucun effet de bord**.
- Il ne **réécrit** aucun verdict passé.
- Il ne conclut rien sur la **qualité** des cycles concernés — seulement sur la
  présence ou l'absence de leur trace.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, **aucune position**, aucun paramètre
numérique à perturber. Le dire est requis par le protocole, l'inventer serait
pire que de l'omettre.

## Engagements

1. Résultat rapporté tel quel, y compris si les effectifs du #464 ne se
   retrouvent pas.
2. Règle de classement et populations **inchangées** après mesure.
3. **Chaque `<nom>` nommé**, jamais seulement compté — leçon des #462, #464,
   #465, #469.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
