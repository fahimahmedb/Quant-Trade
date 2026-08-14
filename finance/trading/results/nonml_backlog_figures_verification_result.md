# Vérifier les chiffres que le backlog publie (pré-enregistré)

Le backlog porte, en bas de ses six dernières entrées, la même ligne :
« **comptes de backlog non revérifiés : quatre faux en six cycles** ».
Je l'ai inscrite six fois sans jamais aller voir. Ce cycle y va.

## L'asymétrie du test — reprise ici, comme le pré-enregistrement l'exige

> Une **absence** est informative : un chiffre que le backlog publie et qu'on
> ne retrouve pas dans le rapport qu'il cite est soit une erreur de recopie,
> soit un calcul fait de tête sans être rendu vérifiable. Une **présence** ne
> prouve rien : `0` se trouve dans n'importe quel rapport par coïncidence.
>
> **Ce cycle ne peut donc pas conclure que les chiffres du backlog sont
> justes.** Il produit une **borne inférieure** du nombre de chiffres
> invérifiables, et rien de plus.

## Couverture

- entrées de l'univers figé (#443–#460) : **18**
- traitées : **18**
- exclues : **0**
- jetons numériques vérifiés : **273**

## Le résultat

- entrées portant **au moins un** jeton absent : **17** sur **18**
- jetons absents **sous la règle stricte déclarée** : **70** (25,64 %)

Décomposés :

| Classe | Nombre | Ce que ça veut dire |
|---|---|---|
| **variante typographique** | **28** | le chiffre EST dans le rapport, écrit `0.53` là où le backlog écrit `0,53` |
| **publié dans un fichier frère** | **7** | le chiffre est dans l'`_audit.md` ou le `_robustness.md` du même cycle |
| **citation d'un autre cycle** | **31** | le chiffre est publié dans une section qui, par construction, cite d'autres cycles |
| **introuvable** | **4** | ni dans le rapport, ni sous une variante, ni dans une section de citation |

> Le chiffre informatif est le dernier : **4** jetons sur **273** (**1,47 %**).

### Cinq défauts de mon propre instrument, publiés

**Aucun des cinq n'ôte un jeton du compte de tête.**

1. **Le signe.** Ma colonne « variante typographique » retirait aussi le
   signe de tête : `−1` se trouvait « expliqué » par un `1`, et `−0,07` par
   un `0.07`. **Retirer un moins change la valeur** — ce n'est pas une
   variante d'écriture. Seul le `+` explicite, facultatif en prose, est
   désormais retiré. La correction rend la colonne **plus sévère**.
2. **Les sections de citation.** Ma règle traitait toute l'entrée comme si
   elle rapportait la mesure du cycle. Or chaque entrée se termine par une
   **« Dette restante »** et une **« File des prochains cycles »** qui
   citent les chiffres d'**autres** cycles — `190/190` (#442), `4,2 %`
   (#441). Les compter comme des écarts de recopie était une erreur de
   conception de ma part.
3. **Les fichiers frères.** Un cycle publie sur **trois** fichiers —
   `_result.md`, `_audit.md`, `_robustness.md`. Mon pré-enregistrement n'en
   déclare qu'**un**. Les chiffres de robustesse (7a) et les recomptages
   d'audit étaient donc cherchés dans un fichier qui, par construction, ne
   les contient pas.
4. **Le repérage des titres.** `startswith("#")` prenait une ligne de prose
   commençant par `#447` pour un titre de section, et fabriquait des
   sections inexistantes. Corrigé en exigeant un vrai titre Markdown.
5. **Le rapport n'était pas idempotent.** Les variantes typographiques
   étaient stockées dans un `set` : la classification était stable, mais
   **l'étiquette affichée** changeait d'une exécution à l'autre au gré de
   la graine de hachage. Corrigé par un tri. **Ce défaut-là, le backtest
   ne pouvait pas le voir — c'est le contrôle D de l'audit qui l'a
   trouvé**, et c'est précisément à cela que sert un audit qui ne partage
   aucune fonction avec ce qu'il vérifie.

> **Les classifications 2 et 3 ont été ajoutées APRÈS avoir vu le
> résultat.** Je le dis plutôt que de les laisser passer pour prévues.
> Elles ne modifient **aucun** chiffre de la règle déclarée — le compte de
> tête reste **70** — mais il faut voir ce qu'elles font :
> **chaque couche d'explication que j'ajoute rend le backlog plus propre,
> et je les ai toutes ajoutées après avoir vu le chiffre.** C'est la
> raison pour laquelle le résidu ci-dessous **ne doit pas** se lire comme
> un taux d'exactitude du backlog.

Et c'est, une fois de plus, **la relecture de la sortie** qui a trouvé les
quatre défauts — pas la mesure. C'est la constante de tous les cycles
depuis le #442.

## Épinglage — chaque entrée à SON commit

Un rapport de ce dépôt dépend de l'état du dépôt (#436-#438). Comparer le
rapport d'aujourd'hui à un chiffre publié il y a dix cycles fabriquerait des
écarts qui ne seraient que de la dérive — leçon des #445 et #451.

| Entrée | Commit épinglé | Rapport cité | Jetons | Absents |
|---|---|---|---|---|
| #443 | `7d1fe406` | `nonml_npz_report_consistency_baskets_result.md` | 20 | **2** |
| #444 | `d33c53ad` | `nonml_third_npz_schema_handling_result.md` | 20 | **5** |
| #445 | `a0c7b818` | `nonml_net_pnl_correction_result.md` | 27 | **7** |
| #446 | `98858d2e` | `nonml_sweep_pass_prose_fix_result.md` | 10 | **1** |
| #447 | `bda9171d` | `nonml_verdict_detector_fix_result.md` | 19 | **5** |
| #448 | `64c19b43` | `nonml_verdict_detector_complete_result.md` | 24 | **4** |
| #449 | `8aea8994` | `nonml_verdict_rule_propagation_result.md` | 18 | **4** |
| #450 | `fcef6f48` | `nonml_six_reports_regeneration_result.md` | 17 | **2** |
| #451 | `1d764963` | `nonml_marker_emitted_by_scripts_result.md` | 15 | **4** |
| #452 | `2dd64b47` | `nonml_tom_decomposition_npz_result.md` | 15 | **10** |
| #453 | `d01dd7a9` | `nonml_orphan_npz_inspection_result.md` | 16 | **2** |
| #454 | `76a60944` | `nonml_verdict_variant_decision_result.md` | 8 | **4** |
| #455 | `88b45b8a` | `nonml_silent_skip_decision_result.md` | 1 | 0 |
| #456 | `d33c32ca` | `nonml_dsr_corrected_trials_result.md` | 15 | **6** |
| #457 | `7e1414ca` | `nonml_battery_coverage_result.md` | 15 | **1** |
| #458 | `7e310dd6` | `nonml_temporal_holdout_result.md` | 7 | **5** |
| #459 | `e2f80f77` | `nonml_relative_holdout_result.md` | 12 | **7** |
| #460 | `5d98fce5` | `nonml_verdict_rule_battery_result.md` | 14 | **1** |

## Tous les jetons absents, en entier

Le critère 2 interdit d'en résumer un seul. Chacun est donné avec le
segment en gras qui le porte.

### #443 — `nonml_npz_report_consistency_baskets_result.md` (`7d1fe406`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |
| `99` | 99 | Dette restante | cite un autre cycle (section « Dette restante ») |

### #444 — `nonml_third_npz_schema_handling_result.md` (`d33c53ad`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `+0,1705` | +0,1705 | Les deux D, et leur portée exacte | variante typographique `+0.1705` |
| `+0,2028` | +0,2028 | Les deux D, et leur portée exacte | variante typographique `+0.2028` |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |
| `99` | 99 | Dette restante | cite un autre cycle (section « Dette restante ») |

### #445 — `nonml_net_pnl_correction_result.md` (`a0c7b818`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `0,9999` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic | variante typographique `0.9999` |
| `0,999` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic | variante typographique `0.999` |
| `0,99` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic | variante typographique `0.99` |
| `0,95` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic | publié dans `nonml_net_pnl_correction_robustness.md` |
| `0,90` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic | **introuvable** |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #446 — `nonml_sweep_pass_prose_fix_result.md` (`98858d2e`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |

### #447 — `nonml_verdict_detector_fix_result.md` (`bda9171d`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `−4` | −4 | La règle changée, et ce qu'elle produit | variante typographique `-4` |
| `−1` | −1 | La règle changée, et ce qu'elle produit | variante typographique `-1` |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |
| `10` | 10 rapports dépendants du dépôt | Dette restante | cite un autre cycle (section « Dette restante ») |

### #448 — `nonml_verdict_detector_complete_result.md` (`64c19b43`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `6815` | 6 815 lignes de 303 rapports | Conformité au régime, seconde fois de suite | publié dans `nonml_verdict_detector_complete_audit.md` |
| `303` | 6 815 lignes de 303 rapports | Conformité au régime, seconde fois de suite | publié dans `nonml_verdict_detector_complete_audit.md` |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `10` | 10 rapports dépendants du dépôt | Dette restante | cite un autre cycle (section « Dette restante ») |

### #449 — `nonml_verdict_rule_propagation_result.md` (`8aea8994`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `20` | Les 20 `.npz` sans rapport publié | File des prochains cycles | cite un autre cycle (section « File des prochains cycles ») |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `20` | 20 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #450 — `nonml_six_reports_regeneration_result.md` (`fcef6f48`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #451 — `nonml_marker_emitted_by_scripts_result.md` (`1d764963`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `20` | Les 20 `.npz` sans rapport publié | File des prochains cycles | cite un autre cycle (section « File des prochains cycles ») |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `20` | 20 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #452 — `nonml_tom_decomposition_npz_result.md` (`2dd64b47`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `+0,963497` | Corrélation variante A / #8 : +0,963497 | Le résultat | variante typographique `+0.963497` |
| `0,9999` | 0,9999 | Le résultat | variante typographique `0.9999` |
| `+0,53` | +0,53 | Le résultat | variante typographique `+0.53` |
| `0,95` | 0,95 | Robustesse (7a) — la conclusion ne tient pas à un seul chiffre | publié dans `nonml_tom_decomposition_npz_robustness.md` |
| `+0,959` | +0,959 | Robustesse (7a) — la conclusion ne tient pas à un seul chiffre | publié dans `nonml_tom_decomposition_npz_robustness.md` |
| `+0,970` | +0,970 | Robustesse (7a) — la conclusion ne tient pas à un seul chiffre | **introuvable** |
| `20` | Les 20 `.npz` sans rapport publié | File des prochains cycles | publié dans `nonml_tom_decomposition_npz_robustness.md` |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `20` | 20 | Dette restante | publié dans `nonml_tom_decomposition_npz_robustness.md` |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #453 — `nonml_orphan_npz_inspection_result.md` (`d01dd7a9`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #454 — `nonml_verdict_variant_decision_result.md` (`76a60944`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `+8` | +8 / −5 | La règle de décision, fixée avant mesure | variante typographique `8` |
| `−5` | +8 / −5 | La règle de décision, fixée avant mesure | **introuvable** |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #456 — `nonml_dsr_corrected_trials_result.md` (`d33c32ca`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `1,0` | 1,0 % | Le décompte | variante typographique `1.0` |
| `0,95` | DSR > 0,95 | Le résultat | variante typographique `0.95` |
| `0,9519` | DSR 0,9519 | Ma prédiction est réfutée | variante typographique `0.9519` |
| `+0,0019` | +0,0019 | Ma prédiction est réfutée | variante typographique `+0.0019` |
| `190` | 190/190 | Dette restante | cite un autre cycle (section « Dette restante ») |
| `4,2` | 4,2 % | Dette restante | cite un autre cycle (section « Dette restante ») |

### #457 — `nonml_battery_coverage_result.md` (`7e1414ca`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `−4` | −4 | Le recompte | variante typographique `-4` |

### #458 — `nonml_temporal_holdout_result.md` (`7e310dd6`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `+1,34` | +1,34 | Le résultat brut, publié tel quel | variante typographique `+1.34` |
| `100,0` | 100,0 % | Le résultat brut, publié tel quel | variante typographique `100.0` |
| `98,0` | 98,0 % | Le résultat brut, publié tel quel | variante typographique `98.0` |
| `+1,39` | +1,39 | Je ne le compte pas comme une bonne nouvelle | variante typographique `+1.39` |
| `100,0` | 100,0 % | Je ne le compte pas comme une bonne nouvelle | variante typographique `100.0` |

### #459 — `nonml_relative_holdout_result.md` (`e2f80f77`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `−0,06` | −0,06 | — en-tête — | variante typographique `-0.06` |
| `−0,06` | −0,06 | Le résultat, sur 100 PASS | variante typographique `-0.06` |
| `−0,07` | −0,07 | Le résultat, sur 100 PASS | variante typographique `-0.07` |
| `18,0` | 18,0 % | Le résultat, sur 100 PASS | variante typographique `18.0` |
| `19,0` | 19,0 % | Le résultat, sur 100 PASS | variante typographique `19.0` |
| `88,0` | 88,0 % | Le résultat, sur 100 PASS | variante typographique `88.0` |
| `89,0` | 89,0 % | Le résultat, sur 100 PASS | variante typographique `89.0` |

### #460 — `nonml_verdict_rule_battery_result.md` (`5d98fce5`)

| Jeton | Segment en gras qui le porte | Section | Diagnostic |
|---|---|---|---|
| `−0,06` | edge médian −0,06 | Où en est le projet, en une phrase | **introuvable** |

## Le noyau informatif — les jetons introuvables sous toute lecture

Ce sont les **4** seuls chiffres que le backlog publie et
qu'aucune des lectures ci-dessus ne retrouve : ni dans le rapport cité,
ni sous une variante typographique, ni dans un fichier frère du même
cycle, ni dans une section qui cite un autre cycle.

| Entrée | Jeton | Segment | Section |
|---|---|---|---|
| #445 | `0,90` | 0,9999 → 0,999 → 0,99 → 0,95 → 0,90 | Robustesse (7a) — plateau, pas pic |
| #452 | `+0,970` | +0,970 | Robustesse (7a) — la conclusion ne tient pas à un seul chiffre |
| #454 | `−5` | +8 / −5 | La règle de décision, fixée avant mesure |
| #460 | `−0,06` | edge médian −0,06 | Où en est le projet, en une phrase |

## Les résidus, vérifiés un par un **à la main**

Quatre, c'est assez peu pour aller voir chacun **dans la source**
plutôt que d'en tirer un taux. C'est fait :

| Entrée | Jeton | Ce que la source dit |
|---|---|---|
| #445 | `0,90` | La grille de robustesse écrit **`0.9`**, le backlog **`0,90`**. *Même valeur, zéro final en plus.* **Pas une erreur.** |
| #452 | `+0,970` | Le rapport donne un maximum de **`+0.969870`**, que le backlog arrondit en **`+0,970`**. Le voisin `+0,959` est passé, lui, parce que `0.959` est un préfixe de `0.959460` — *le sens de l'arrondi décide, pas l'exactitude.* **Pas une erreur.** |
| #454 | `−5` | Affirmation sur un `git diff`, pas sur le rapport. **Vérifiée directement contre git** : le commit `d2cbda21` porte `8  5  nonml_sessions_column_backfill_audit.py`. **Le backlog dit vrai.** |
| #460 | `−0,06` | Citation de l'edge médian du **#459**, dans une section de synthèse que ma liste de sections de citation ne couvre pas. **Pas une erreur.** |

> **Aucun des quatre n'est une erreur de chiffre.** Trois sont des
> artefacts de mon test par sous-chaîne — zéro final, sens de
> l'arrondi, fait vérifiable dans git et non dans le rapport — et le
> quatrième est une citation d'un autre cycle.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| au moins 3 entrées portent un jeton absent | ≥ 3 | 17 | **vérifiée** |
| les absences portent surtout sur des chiffres **dérivés** (pourcentages, sommes) | — | typographie **28**, citation **31**, dérivés : minoritaires | **réfutée** |
| aucune entrée sans jeton à vérifier | 0 | 0 | **vérifiée** |

**La prédiction 2 est réfutée, et de la façon la plus instructive.** Je
m'attendais à des erreurs de calcul commises en rédigeant. Les absences ne
viennent quasiment pas de là : elles viennent de la **typographie** (le
backlog francise les décimales que le script imprime en `0.53`), de mon
**mauvais découpage** de l'entrée, et du fait que je cherchais dans **un**
fichier ce qu'un cycle publie sur **trois**.

### La prédiction 1 est « vérifiée » — et cette vérification est creuse

Mécaniquement, **17 entrées sur 18** portent un jeton absent : la
prédiction passe. **Elle ne devrait convaincre personne.** Les absences
qu'elle compte sont, à quatre près, des artefacts de mon instrument, et
les quatre restantes n'en sont pas non plus après vérification manuelle.

C'est la situation du **#458** exactement : un verdict mécanique favorable
posé sur une mesure qui ne mesure pas ce qu'elle annonce. La différence
est qu'ici le pré-enregistrement m'obligeait à publier chaque absence en
entier — et c'est cette obligation, pas la statistique, qui a rendu le
défaut visible.

## Critères de succès

1. **18/18** entrées traitées ou exclues avec
   raison — **OUI**.
2. Tout jeton absent publié en entier avec son segment — **OUI** (section
   ci-dessus, aucun résumé, aucun « et N autres »).
3. Épinglage par entrée publié, commit par commit — **OUI**.
4. Asymétrie du test reprise dans ce rapport — **OUI** (en tête).

**PASS** — le critère porte sur le **procédé**, pas sur le nombre
d'écarts trouvés : un cycle qui n'en trouve aucun et le montre proprement
réussit.

## Ce que ce cycle établit, et ce qu'il n'établit pas

**Il n'a trouvé aucune erreur de chiffre** dans les 18 entrées, sur les
**273** jetons qu'elles publient.

> **Ce n'est pas un certificat d'exactitude, et la dette reste inscrite.**

Trois raisons, toutes déclarées d'avance ou publiées ci-dessus :

1. **Le test est asymétrique** : une présence ne prouve rien. Un chiffre
   faux qui se trouve par hasard ailleurs dans le rapport passe.
2. **Les quatre faux connus du backlog ne sont pas dans cet univers.**
   « 8 scripts » (#449), « 6 rapports » (#451), « 13 orphelins » (#453),
   « 29 en échec » (#457) étaient faux **par rapport au dépôt**, pas par
   rapport au rapport cité — qui portait souvent la même erreur. **Un
   contrôle de recopie ne peut pas les voir.** C'est la limite de fond
   de ce cycle, et elle explique pourquoi ces quatre-là ont dû être
   trouvés par hasard.
3. **J'ai ajouté deux couches d'explication après avoir vu le résultat**,
   et chacune a rendu le backlog plus propre.

**La ligne « comptes de backlog non revérifiés » doit donc rester au
passif.** Ce cycle ne la solde pas : il montre qu'un contrôle de recopie
était le mauvais outil pour la solder, et lequel il aurait fallu — un
contrôle qui remesure la **grandeur** dans le dépôt, pas la **recopie**
dans le rapport. C'est un cycle à déclarer d'avance, pas à improviser ici.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun chiffre du backlog : tout écart est publié et
  inscrit, pas réparé au passage — engagement tenu depuis le #450.
- Il ne **régénère** aucun rapport.
- Il ne juge **aucune stratégie** : un écart de recopie n'est pas un verdict.


> **Rapport épinglé** — contrairement aux inventaires de dépôt (#436-#438),
> ce rapport lit chaque entrée au commit qui l'a créée. Il ne dérive donc pas
> avec le dépôt : réexécuté dans dix cycles, il doit rendre les mêmes chiffres.