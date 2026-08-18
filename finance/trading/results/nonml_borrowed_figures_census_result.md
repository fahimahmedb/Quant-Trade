# Les **chiffres empruntés sans relecture** (pré-enregistré)

Au **#497**, une prédiction reposait sur un « + 2 » emprunté à
l'audit du **#496** sans être recalculé. Il valait **3**. **Ce canal
d'erreur n'avait jamais été dénombré.**

> **Ces deux nombres sont lus dans les rapports du #496 et du #497**, pas
> retapés. Une première version de ce rapport les tapait — **mon propre
> audit l'a signalé**, et il aurait fallu qu'un rapport sur les emprunts
> soit lui-même porteur pour que la démonstration soit complète. Elle
> l'est autrement : le détecteur a mordu son auteur.

## Les trois définitions, citées verbatim

> **Chaîne publiée** — littéral (`Constant`) ou f-string (`JoinedStr`)
> argument d'un appel à `.append(`, `print(`, `.write_text(`.
> Commentaires et docstrings exclus **par construction**.
>
> **Chiffre emprunté** — chaîne publiée portant **à la fois** `#\d{3}`
> et un nombre en gras présent **en texte littéral**, hors de tout champ
> interpolé. *(Un champ `f"**{n}**"` **calcule** ; le même texte tapé
> avec ses chiffres **recopie**.)*
>
> *L'exemple est écrit sans chiffre à dessein : rédigé avec un nombre en
> gras, il était lui-même détecté comme littéral — le contrôle ne
> distingue pas un exemple typographique d'un chiffre en dur, et je n'ai
> pas voulu affaiblir le contrôle pour sauver ma phrase.*
>
> **Relecteur** — script appelant `.read_text(` **et** portant un littéral
> `.md` **autre** que son propre rapport.

## Le recensement

- scripts `nonml_*.py` analysés : **977**
- scripts **porteurs** d'au moins un chiffre emprunté : **24**
- **emprunts** au total : **31**
- scripts **relecteurs** : **133**

## Le croisement — le cœur de la question

| | Nombre | Part des porteurs |
|---|---|---|
| porteurs **qui lisent aussi** | **19** | **79,2 %** |
| porteurs **qui ne lisent pas** | **5** | **20,8 %** |

> **La majorité des porteurs lit aussi des rapports tiers.** Le défaut
> n'est donc pas « ne pas savoir lire » mais **lire et retaper quand
> même** — ce qui est pire : l'outil était là et n'a pas servi.

## Les cycles cités dans les emprunts

- cycles distincts cités : **26**

| Cycle cité | Emprunts |
|---|---|
| `#427` | **4** |
| `#451` | **4** |
| `#449` | **2** |
| `#463` | **2** |
| `#479` | **2** |
| `#481` | **2** |
| `#414` | **1** |
| `#416` | **1** |
| `#428` | **1** |
| `#434` | **1** |
| `#435` | **1** |
| `#442` | **1** |
| `#443` | **1** |
| `#445` | **1** |
| `#450` | **1** |

*(**11** autres cycles, cités **1** fois chacun, non listés.)*

## Les porteurs qui ne lisent pas, nommés

- effectif : **5**

- `nonml_citer_451_definition_backtest.py` — cite `#472` : « trouvé **0**. Le #472 a laissé **deux lectures** ouvertes sans pouvoir les… »
- `nonml_citer_451_resolution_backtest.py` — cite `#469` : « est reproduit par une méthode indépendante, et le **0** du #469… »
- `nonml_content_defined_magnitudes_backtest.py` — cite `#449` : « | #449 | **8** consommateurs, corrigé en **6** | **** importateurs dont **** d'instrument,… »
- `nonml_repo_magnitudes_recount_backtest.py` — cite `#457` : « Le #457 racontait avoir soumis **29** stratégies à la batterie après… »
- `nonml_self_inclusion_detector_backtest.py` — cite `#463` : « Le #463 a trouvé **2** scripts non idempotents en en rejouant **18**. Le… »

## Ce que ce recensement **ne dit pas**

Il mesure une **exposition**, pas une **erreur**. Aucun emprunt n'est ici
confronté à sa source : un chiffre retapé peut être **exact**, comme le
« ~4,1 % » du **#499** l'était. **Vérifier chaque emprunt est un autre
cycle**, et il est proposé en fin de rapport.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| porteurs ≥ 10 | ≥ 10 | 24 | **vérifiée** |
| majorité des porteurs ne lisent pas | > 50 % | 20,8 % | **réfutée** |
| le backtest du #497 est relecteur | oui | oui | **vérifiée** |

> La prédiction 3 dit aussi ce que la mesure **ne peut pas** voir : le
> « + 2 » fautif du #497 était dans son **pré-enregistrement**, pas dans
> son code. **Ce recensement ne l'aurait pas attrapé** — et c'est une
> limite de la définition, déclarée d'avance.

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Les seuls appels externes visent `git status`, **en lecture**.

## Critères de succès

1. Les trois définitions citées verbatim, établies par AST — **OUI**.
2. Population (**977**), porteurs (**24**), emprunts (**31**), relecteurs (**133**) — **OUI**.
3. Croisement publié avec la part des porteurs non relecteurs — **OUI**.
4. Cycles cités nommés avec leur compte (**26**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution.
