# Les **résidus** dans les sources **non publiées** (pré-enregistré)

Cinq cycles ont réduit **39** nombres empruntés à quelques **résidus** :
introuvables **au registre** comme **aux rapports** du cycle cité.
Restent trois sources qui ne sont pas publiées.

## Les trois familles et leurs règles, citées verbatim

| Famille | Extraction | Appariement du nombre |
|---|---|---|
| PREREG du cycle cité | fichier entier | **en gras** |
| autre PREREG | fichier entier | **en gras** |
| commentaire ou docstring | jetons `COMMENT` de `tokenize` + docstrings par AST | **jeton nu** |
| message de commit | `git log --format=%B` sur tout l'historique | **jeton nu** |

**Le nombre nu est plus permissif que le gras** : un commentaire ou un
message de commit n'emploie pas de balisage. Pour compenser, **la
contrainte de contexte est identique** — ≥ **2**
mots-clés dans **±200 caractères**, règle du #502 **reprise
sans modification**.

## Le corpus fouillé

- résidus repris de la chaîne #500-#504 : **5**
- fichiers `PREREG_*.md` : **480**
- scripts dont commentaires et docstrings sont extraits : **987**
- messages de commit : **2339**

## Les cinq classes

| Classe | Nombre |
|---|---|
| **sourcé au PREREG du cycle cité** | **0** |
| **sourcé dans un autre PREREG** | **3** |
| **sourcé dans un commentaire ou une docstring** | **0** |
| **sourcé dans un message de commit** | **0** |
| **introuvable partout** | **2** |

## La contribution de chaque famille

*L'engagement 3 l'exige : toutes publiées, jamais la seule qui arrange.*

| Famille | Résidus touchés | Dont elle est **seule** à expliquer |
|---|---|---|
| PREREG du cycle cité | **0** | **0** |
| autre PREREG | **3** | **0** |
| commentaire ou docstring | **0** | **0** |
| message de commit | **3** | **0** |

## Chaque résidu, avec **toutes** ses trouvailles

*Ne montrer que la famille gagnante masquerait la redondance des
sources.*

### `nonml_content_defined_magnitudes_audit.py` — cite `#449` pour **2**

- classe : **introuvable partout**
- **aucune trouvaille dans les trois familles**
- extrait : « Le rapport n'accuse pas le #449 parce que **2** des importateurs sont… »

### `nonml_report_idempotence_backtest.py` — cite `#443` pour **5,7**

- classe : **introuvable partout**
- **aucune trouvaille dans les trois familles**
- extrait : « soit **5,7 %** — ceux des entrées #443-#460, même univers figé que les #461… »

### `nonml_content_defined_magnitudes_backtest.py` — cite `#451` pour **8**

- classe : **sourcé dans un autre PREREG**
- **autre PREREG** : **1** — `PREREG_momentum_decile_spread_vol_targeting_overlay_pit_universe.md`
- **message de commit** : **1** — `(historique)`
- extrait : « Vérifié plutôt que supposé : au commit du #451, **8** fichiers… »

### `nonml_self_inclusion_detector_backtest.py` — cite `#463` pour **16**

- classe : **sourcé dans un autre PREREG**
- **autre PREREG** : **1** — `PREREG_self_inclusion_detector.md`
- **message de commit** : **1** — `(historique)`
- extrait : « Le #463 fournit une **vérité terrain** : **2** fautifs, **16** sains.… »

### `nonml_self_inclusion_detector_backtest.py` — cite `#463` pour **2**

- classe : **sourcé dans un autre PREREG**
- **autre PREREG** : **1** — `PREREG_self_inclusion_detector.md`
- **message de commit** : **1** — `(historique)`
- extrait : « Le #463 fournit une **vérité terrain** : **2** fautifs, **16** sains.… »

## Une source qui n'en est pas une : le `PREREG_` du script lui-même

- trouvailles en « autre PREREG » : **3**
- dont le `PREREG_` **du script lui-même** : **2**
- dont un `PREREG_` **tiers** : **1**

> **Trouver un chiffre dans le pré-enregistrement du script qui le
> publie ne le source pas** : c'est le même auteur, le même cycle, la
> même erreur possible. **La trouvaille est circulaire.**

- `nonml_self_inclusion_detector_backtest.py` pour **16** → `PREREG_self_inclusion_detector.md` *(le sien)*
- `nonml_self_inclusion_detector_backtest.py` pour **2** → `PREREG_self_inclusion_detector.md` *(le sien)*

Les trouvailles en `PREREG_` **tiers** :

- `nonml_content_defined_magnitudes_backtest.py` pour **8** → `PREREG_momentum_decile_spread_vol_targeting_overlay_pit_universe.md`

> **Un `PREREG_` tiers sans rapport thématique avec le cycle cité**
> est un appariement de coïncidence : l'appariement nu est permissif,
> et deux mots-clés suffisent. Ces trouvailles **ne valent pas
> source** ; elles montrent surtout ce que la règle ramasse.

> **En retirant les trouvailles circulaires**, les résidus réellement
> rattachés à une source indépendante tombent à **1**
> sur **5**.

## Les introuvables partout

- effectif : **2**

> Ce sont les **premiers candidats sérieux** de toute la série : leur
> nombre n'apparaît, au voisinage de leur sujet, **dans aucune source
> du dépôt** — ni publiée, ni interne. **L'appariement nu est pourtant
> permissif**, ce qui rend son échec d'autant plus net.
>
> **Cela ne les déclare pas faux.** Une absence de trace reste une
> absence de preuve, pas une preuve d'absence.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 2 résidus sourcés hors publication | ≥ 2 | 3 | **vérifiée** |
| ≥ 1 introuvable partout | ≥ 1 | 2 | **vérifiée** |
| les commits expliquent ≤ 1 résidu | ≤ 1 | 3 | **réfutée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population et règles sont **importées** des backtests des #500 à #504 —
leurs fonctions, jamais leur `main()`.

## Critères de succès

1. Trois familles et règles citées verbatim, appariement nu justifié — **OUI**.
2. Les **5** résidus cherchés dans les **3** familles (**4** lignes, le `PREREG_` étant scindé selon qu'il est celui du cycle cité) — **OUI**.
3. Classement par priorité **et** liste complète des trouvailles — **OUI**.
4. Introuvables partout nommés avec extrait (**2**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts, des
> pré-enregistrements et de l'historique à la date de son exécution.
