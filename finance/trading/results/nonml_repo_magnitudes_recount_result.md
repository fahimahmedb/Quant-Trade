# Re-mesurer les **grandeurs** du dépôt, pas les recopies (pré-enregistré)

Le #461 comparait un texte à un texte, et a établi **contre lui-même**
pourquoi cela ne pouvait pas suffire :

> les quatre faux connus étaient faux **par rapport au dépôt**, pas par
> rapport au rapport cité — qui portait souvent la même erreur.

Ce cycle est l'outil manquant : il **recompte dans le dépôt**, au commit
épinglé de chaque entrée.

## 1. La table de référence

**108/108** cellules — six grandeurs, **18** commits épinglés.

| Entrée | Commit | backtests | resultats | npz | batteries | robustesses | audits |
|---|---|---|---|---|---|---|---|
| #443 | `7d1fe406` | 296 | 298 | 208 | 92 | 126 | 294 |
| #444 | `d33c53ad` | 297 | 299 | 208 | 92 | 126 | 295 |
| #445 | `a0c7b818` | 298 | 300 | 208 | 92 | 127 | 296 |
| #446 | `98858d2e` | 299 | 301 | 208 | 92 | 127 | 297 |
| #447 | `bda9171d` | 300 | 302 | 208 | 92 | 127 | 298 |
| #448 | `64c19b43` | 301 | 303 | 208 | 92 | 128 | 299 |
| #449 | `8aea8994` | 302 | 304 | 208 | 92 | 128 | 300 |
| #450 | `fcef6f48` | 303 | 305 | 208 | 92 | 128 | 300 |
| #451 | `1d764963` | 304 | 306 | 208 | 92 | 128 | 300 |
| #452 | `2dd64b47` | 305 | 307 | 209 | 92 | 129 | 300 |
| #453 | `d01dd7a9` | 306 | 308 | 209 | 92 | 129 | 300 |
| #454 | `76a60944` | 307 | 309 | 209 | 92 | 129 | 300 |
| #455 | `88b45b8a` | 308 | 310 | 209 | 92 | 129 | 300 |
| #456 | `d33c32ca` | 309 | 311 | 209 | 92 | 129 | 300 |
| #457 | `7e1414ca` | 310 | 312 | 209 | 121 | 129 | 300 |
| #458 | `7e310dd6` | 311 | 313 | 209 | 121 | 129 | 300 |
| #459 | `e2f80f77` | 312 | 314 | 209 | 121 | 129 | 300 |
| #460 | `5d98fce5` | 313 | 315 | 209 | 121 | 129 | 300 |

> **C'est le chiffre vrai.** Les cycles suivants peuvent le citer au lieu
> de recopier de la prose — ce qui est précisément la façon dont les
> quatre faux se sont propagés.

## 2. Monotonie — contrôle de mon propre comptage

**Aucune décroissance** sur les six grandeurs. Le dépôt ne fait
qu'ajouter, et mon comptage se comporte comme il le devrait.
**Prédiction 3 vérifiée.**

## 3. Les quatre faux connus — **un seul est recomptable**

| Entrée | Annoncé | Ce que les six grandeurs peuvent en dire |
|---|---|---|
| #449 | 8 scripts consommateurs de la règle | **rien** — ensemble défini par le *contenu* des fichiers, pas par leur nom |
| #451 | 6 rapports portant l'encart | **rien** — idem |
| #453 | 13 `.npz` orphelins | **rien directement** — un orphelin est une *relation* entre deux globs, pas un total |
| #457 | 29 batteries en échec d'exécution | **92 → 121** entre les deux commits, soit **+29** |

> **Trois des quatre sont hors de portée de cet instrument**, et je ne le
> masque pas. « Consommateurs d'une règle » et « porteurs d'un encart » se
> définissent par le **contenu** des fichiers ; « orphelin » est une
> **relation** entre deux globs. Les six grandeurs déclarées comptent des
> totaux, et **en ajouter une maintenant serait ajuster l'instrument au
> résultat.**

### Le seul recomptage qui mord — et il confirme le #457

La grandeur `batteries` est **plate à 92** de #443 à #456, puis
passe à **121** exactement au commit du #457 : **+29**.

Le #457 racontait avoir soumis **29** stratégies à la batterie après
avoir corrigé un défaut de son pilote (le code de sortie **2** signifie
« pas de PASS renforcé », pas un échec d'exécution). **Le dépôt le
confirme, indépendamment de tout texte** : 29 rapports de batterie
apparaissent à ce commit, ni plus ni moins.

> C'est **le résultat de ce cycle** : la première confirmation d'une
> affirmation du backlog obtenue **en comptant dans le dépôt** plutôt
> qu'en relisant un rapport.

## 4. L'appariement de prose — étroit, et publié en entier

Deux mots-clés seulement : un entier en gras suivi sur la même ligne de
`.npz` ou de « batterie ». **« scripts » et « rapports » ne sont pas
appariés** — selon la phrase ils désignent des ensembles différents, et
un appariement large produirait des écarts qui ne diraient rien.

- appariements trouvés : **9**
- **concordants** : **0**
- **discordants** : **9**

### Les « écarts » — et pourquoi aucun n'en est un

| Entrée | Mot | Annoncé | Total vrai | Ligne |
|---|---|---|---|---|
| #443 | `.npz` | **99** | 208 | - **1** PASS non évaluable par la batterie ; **99** scripts sans `.npz` (#428). |
| #443 | batterie | **1** | 92 | - **1** PASS non évaluable par la batterie ; **99** scripts sans `.npz` (#428). |
| #444 | `.npz` | **20** | 208 | 4 jambes du troisième schéma) ; restent **20** `.npz` sans rapport. |
| #444 | `.npz` | **99** | 208 | - **1** PASS non évaluable par la batterie ; **99** scripts sans `.npz` (#428). |
| #444 | batterie | **1** | 92 | - **1** PASS non évaluable par la batterie ; **99** scripts sans `.npz` (#428). |
| #445 | `.npz` | **113** | 208 | - **1** PASS non évaluable par la batterie ; **113** scripts sans `.npz` (#428, |
| #445 | batterie | **1** | 92 | - **1** PASS non évaluable par la batterie ; **113** scripts sans `.npz` (#428, |
| #457 | batterie | **29** | 121 | Les **29** ont passé la batterie, dans l'ordre **alphabétique** déclaré. |
| #457 | batterie | **29** | 121 | Les **29** rapports de batterie sont classés **« indéterminé »** par la règle de |

> **Ma règle d'appariement a échoué, et il faut le dire avant de lire
> ce tableau comme une liste d'erreurs du backlog.**

Lisez les lignes : « **99** scripts **sans** `.npz` », « **20** `.npz`
**sans** rapport », « **1** PASS **non évaluable par** la batterie »,
« les **29** **ont passé** la batterie ». Ce sont des **sous-ensembles**
et des **relations entre** deux globs — jamais le **total** que mon glob
compte. Les comparer au total n'a aucun sens.

**Aucune de ces 9 lignes n'est une erreur du backlog.** Les présenter
comme telles serait une accusation fausse portée contre la trace du
dépôt — plus grave qu'un résultat flatteur.

J'avais écrit dans le pré-enregistrement qu'apparier « scripts » ou
« rapports » « produirait des écarts qui ne diraient rien ». **J'ai
commis exactement cette faute sur les deux mots-clés que je croyais
sûrs.** La règle reste publiée telle que déclarée ; c'est sa **lecture**
qui est corrigée, pas la règle.

## Mes trois prédictions, confrontées

| Prédiction | Mesuré | Verdict |
|---|---|---|
| les 4 faux connus confirmés faux par recomptage | **1 recomptable sur 4** (#457) | **largement intestable** |
| ≥ 1 appariement supplémentaire en désaccord | 9 | **vérifiée — et sans valeur** |
| grandeurs croissantes | 0 décroissance(s) | **vérifiée** |

**La prédiction 2 « passe » et ne vaut rien.** Les 9 désaccords sont
des artefacts de ma règle d'appariement, pas des erreurs du backlog —
voir la section 4. C'est, pour la deuxième fois consécutive après le
#461, une prédiction vérifiée mécaniquement par une mesure qui ne
mesure pas ce qu'elle annonce.

> **Deux cycles de suite, mon instrument s'est trompé dans le sens qui
> confirme ma prédiction.** Ce n'est plus une malchance : c'est que je
> conçois des règles d'appariement trop lâches et que je les déclare
> « étroites » sans les avoir éprouvées sur un cas.

## Critères de succès

1. **108/108** cellules produites — **OUI**.
2. Tout appariement publié, concordances comprises — **OUI**.
3. Les quatre faux recomptés, ou déclarés non recomptables — **OUI**.
4. Globs inchangés après mesure — **OUI**.

**PASS** — le critère porte sur le procédé.

## Ce que ce cycle n'établit pas

- **Il ne couvre pas les ensembles définis par le contenu** des fichiers,
  ni les **relations** entre deux globs. **Trois des quatre faux connus**
  sont de cette nature — **l'essentiel de la dette reste hors de portée**.
- **Son appariement de prose est un échec**, publié comme tel : les 9
  désaccords sont des sous-ensembles comparés à des totaux, pas des
  erreurs. Le seul acquis est la **table de référence** et la
  confirmation du #457 par le saut `batteries` 92 → 121.
- Il ne remplace pas le #461 : recopie et grandeur sont deux contrôles
  différents, et le premier reste publié avec ses limites.


> **Rapport épinglé** — chaque grandeur est comptée au commit qui a créé
> l'entrée. Il ne dérive pas avec le dépôt : réexécuté dans dix cycles, il
> doit rendre les mêmes chiffres.