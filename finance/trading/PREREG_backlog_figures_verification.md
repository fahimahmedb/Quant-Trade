# Pré-enregistrement — vérifier les chiffres que le backlog publie

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION.** Il ne construit aucune stratégie et ne corrige rien.

## La dette que ce cycle attaque

Le backlog porte, en bas de chacune des six dernières entrées, la même ligne :

> **Comptes de backlog non revérifiés** : quatre faux en six cycles.

Quatre chiffres publiés dans le backlog se sont révélés faux quand un cycle
ultérieur a eu l'occasion de les remesurer : « 8 scripts » (#449), « 6 rapports »
(#451), « 13 orphelins » (#453), « 29 batteries en échec d'exécution » (#457).
**Aucun n'a été trouvé par une vérification ; tous par hasard, en cherchant autre
chose.** Je l'ai inscrit six fois sans jamais aller voir.

C'est le seul point de la dette que je peux traiter seul : les trois autres
attendent un arbitrage de l'utilisateur (#421, #431, #432).

## L'univers — figé ici, 18 entrées

Les entrées **#443 à #460** du `NONML_STRATEGY_BACKLOG.md`, soit tous les cycles
depuis le dernier audit de dépôt complet. Chacune cite un `PREREG_<nom>.md` et
un seul ; le rapport correspondant est `results/nonml_<nom>_result.md`.

**Vérifié avant d'écrire ce pré-enregistrement** (structure, aucun chiffre lu) :
les 18 entrées citent 18 `PREREG_` distincts, et les 18 rapports existent.

## L'épinglage — chaque entrée à SON commit

Un rapport de ce dépôt **dépend de l'état du dépôt** et porte lui-même cet
avertissement (#436-#438). Comparer le rapport d'aujourd'hui à un chiffre publié
il y a dix cycles fabriquerait des écarts qui ne sont que de la dérive.

Donc : pour chaque entrée, l'entrée **et** son rapport sont lus **au commit qui a
ajouté cette entrée** (`git log -S` sur le titre, occurrence la plus ancienne).
C'est la leçon des #445 et #451 — la base se mesure à un commit épinglé, jamais
sur le disque, jamais à `HEAD`.

## La règle d'extraction — énoncée mot pour mot

Dans le texte d'une entrée (du titre jusqu'au prochain `## `), tout segment en
gras `**…**` est retenu, et dans chaque segment tout **jeton numérique** :

- chiffres, séparateur de milliers (espace ordinaire ou insécable), virgule
  décimale, signe de tête, `%` ou `/` final ;
- **normalisation** : les espaces internes aux groupes de chiffres sont retirés
  (`1 449` → `1449`), la virgule décimale est conservée telle quelle.

**Exclus, décidés ici et pas après** : les références de cycle (`#443`), les
dates au format `JJ/MM/AAAA`, le score anti-cheat `4/4`, et `n_trials = 1`. Ce
sont des étiquettes, pas des mesures.

**Ne sont PAS exclus** les chiffres d'un seul caractère (`0`, `4`, `7`). Les
exclure rendrait le test plus facile à passer, et « **0** rapport de stratégie
reclassé » est exactement le genre d'affirmation qu'il faut vérifier.

## Le test — et son asymétrie, déclarée avant de mesurer

Un jeton est **retrouvé** si sa forme normalisée apparaît comme sous-chaîne du
rapport cité, normalisé de la même façon, au même commit.

> **Le test est asymétrique et je le dis avant de m'en servir.** Une **absence**
> est informative : un chiffre que le backlog publie et qu'on ne trouve nulle
> part dans le rapport qu'il cite est soit une erreur de recopie, soit un calcul
> que j'ai fait de tête sans le rendre vérifiable. Une **présence** ne prouve
> rien : `0` se trouve dans n'importe quel rapport par coïncidence.
>
> Ce cycle ne peut donc **pas** conclure « les chiffres du backlog sont justes ».
> Il ne peut que produire une **borne inférieure** du nombre de chiffres
> invérifiables. C'est moins que ce que je voudrais et c'est ce que la méthode
> permet.

## Critère de succès — chiffré, et il porte sur le procédé

1. **18/18** entrées traitées, ou listées exclues **avec leur raison**.
2. **Tout** jeton absent publié **en entier, avec le segment en gras qui le
   porte** — aucun résumé, aucun « et N autres ».
3. L'épinglage **par entrée** publié, commit par commit.
4. L'asymétrie ci-dessus **reprise dans le rapport final**, pas seulement ici.

> **PASS** = les quatre points. **FAIL** = un seul manque.

Le critère porte sur le procédé, pas sur le nombre d'écarts trouvés : un cycle
qui ne trouve aucun écart et le montre proprement est un PASS.

## Prédictions — falsifiables

1. **Au moins 3** des 18 entrées portent au moins un jeton absent de leur
   rapport. Fondement : le backlog dit lui-même que quatre de mes comptes se sont
   révélés faux en six cycles.
2. Les absences se concentrent sur les chiffres **dérivés** (pourcentages,
   sommes, écarts calculés en rédigeant) plutôt que sur les **compteurs de tête**
   recopiés depuis la sortie du script.
3. **Aucune** entrée ne se retrouve sans jeton à vérifier.

Si la prédiction 1 est **réfutée dans le sens flatteur** — 0, 1 ou 2 entrées
seulement —, je dois **douter de mon instrument d'abord** : c'est la leçon du
#458, où trois prédictions réfutées à mon avantage cachaient une mesure
confondue. Une extraction qui ne trouve rien est plus probablement une extraction
cassée qu'un backlog exact.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun chiffre du backlog. Tout écart trouvé est **publié et
  inscrit**, pas réparé au passage — engagement tenu depuis le #450.
- Il ne **régénère** aucun rapport.
- Il ne juge **aucune stratégie** : un écart de recopie n'est pas un verdict.

## Engagements

1. Résultat rapporté tel quel, y compris s'il m'inflige une longue liste
   d'écarts, et y compris un **FAIL** de mon propre procédé.
2. Règle d'extraction et exclusions inchangées après mesure. Si l'extraction se
   révèle cassée, le défaut est **publié** et la correction refaite **sous la
   même règle déclarée**, pas ajustée au résultat.
3. L'asymétrie du test reste dans le rapport final même si le résultat est
   spectaculaire.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
