# Pré-enregistrement — trancher la **réserve du #485**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #487.

## La réserve à lever

Le **#485** a classé **5 défauts irréparables sur 17**, chacun avec sa raison.
Son audit en a **confirmé 4** par une route AST — et **pas le cinquième** :

> `pnl_duplicate_sweep_audit` **énumère `results/` sans liste codée en dur** :
> sa route ne confirme pas l'irréparabilité. **Le verdict à la main n'est pas
> révisé** *(ce serait un retuning)*, **le doute est inscrit**.

La raison écrite à la main était :

> « **Correction retenue : 1 essai surnuméraire**, soit 372 → **371** » : le
> **372** est le décompte d'essais du backlog entier, que cet audit ne construit
> pas et qu'aucun module n'expose.

**Ce cycle vérifie cette phrase**, qui n'a jamais été confrontée au code.

## Le protocole — lecture, et rien d'autre

1. **Ce que le script énumère**, établi par AST : quels corpus parcourt-il
   réellement — `results/`, `scripts/`, le backlog ?
2. **Le 372 est-il dérivable** de ces corpus ? Recherche du nombre comme
   **grandeur calculée** (variable, `len()`, somme) et non comme littéral.
3. **Aucun module du dépôt ne l'expose-t-il ?** vérifié par recherche du motif
   « essais / trials » parmi les scripts importables.

## Les trois lectures — toutes publiables

- **A. Irréparable confirmé** — le script énumère **autre chose** que les essais
  du backlog, et 372 n'est dérivable d'aucun de ses corpus.
- **B. Réparable** — le script construit, ou peut construire trivialement, le
  décompte d'essais. **Le verdict du #485 serait alors faux**, et je le dirais.
- **C. Indéterminable** — trancher exigerait de reconstituer la comptabilité
  `n_trials`, **la question précisément en attente d'arbitrage depuis le #421**.

## L'examen à la main — DÉCLARÉ ICI

Les #480 et #483 ont montré ce que coûte un examen non déclaré. Celui-ci l'est :
**le code entourant la ligne fautive est lu**, et la lecture peut **contredire**
les trois faits mécaniques ci-dessus. Si elle les contredit, **c'est la lecture
qui est publiée comme verdict**, et l'écart est signalé.

## Critère de succès — chiffré, il porte sur le procédé

1. Le code **cité verbatim** autour de la ligne, et **ce que le script énumère**
   publié.
2. La recherche du **372 comme grandeur calculée** publiée, avec son résultat.
3. **Une** des trois lectures explicitement nommée.
4. La réserve de l'audit du #485 **explicitement levée ou maintenue** — jamais
   laissée sans réponse.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. La lecture **A** est retenue : l'irréparabilité est confirmée.
2. Ce que le script énumère est **`results/`** — des fichiers — et **non les
   entrées du backlog**.
3. Le nombre **372 n'apparaît nulle part** comme grandeur calculée dans le
   script.

Si la lecture **B** sort, **le #485 s'est trompé sur ce cas**, son compte de
5 irréparables tombe à 4, et je devrai l'écrire aussi nettement qu'il avait
écrit « irréparable ». Ce résultat doit rester atteignable : c'est celui qui
m'arrangerait le moins, puisque j'ai signé le verdict du #485.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien, ni ne modifie aucun script.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **rouvre pas** les 4 autres irréparabilités, confirmées au #485.
- Il ne **tranche pas** la question `n_trials` du #421, qui relève de
  l'arbitrage de l'utilisateur.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que mon verdict du #485
   était faux.
2. Protocole et lectures **inchangés** après mesure.
3. **Code cité verbatim**, jamais paraphrasé — leçon « code contre discours sur
   le code » des #446 à #449.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
