# Bilan des témoins de la série #500-#515, et le témoin faible est-il utilisé seul ailleurs ? (pré-enregistré)

## Partie 1 — la consolidation, aucun nombre recalculé

| Couche | Cycle d'origine | Témoin | Valeur | Verdict |
|---|---|---|---|---|
| Extraction (D500) | #500, témoin #515 | lift | **6,4** | discrimine |
| Confirmation brute (D501, `en_gras_dans`) | #501, témoin #515 | rapport decoy | **1,5** | ne discrimine pas seul |
| Contextuelle (#502) | #502, témoin #514 | spécificité | **35,9 %, 64 % faux positifs** | discrimine, avec réserve |
| Primitive d'exécution (D497-P10) | #497, témoin #515 | lift | **12,1** | discrimine |

> **2 couches sur 4 discriminent sans réserve** (D500, D497-P10). **1 discrimine avec une réserve chiffrée** (contextuelle, 64 % de faux positifs). **1 ne discrimine pas seule** (D501, confirmation brute) — sa faiblesse est **précisément** ce qui a motivé la construction de la couche contextuelle au #502.

## Partie 2 — `en_gras_dans` est-elle utilisée ailleurs, sans compensation ?

- fichiers appelant `en_gras_dans(` (hors sa propre définition dans `nonml_borrowed_figures_confrontation_backtest.py`) : **3**
  - `nonml_borrowed_figures_confrontation_audit.py`
  - `nonml_contextual_confrontation_backtest.py`
  - `nonml_untested_detectors_lift_backtest.py`

| Fichier | Catégorie |
|---|---|
| `nonml_borrowed_figures_confrontation_audit.py` | **Cas 3 — LACUNE** : verdict substantiel sans compensation |
| `nonml_contextual_confrontation_backtest.py` | **Cas 1** — le #502 lui-même : compense par le contexte |
| `nonml_untested_detectors_lift_backtest.py` | **Cas 2** — le #515 lui-même : teste D501, ne s'appuie pas dessus |

> **1 cas non prévu(s) par le nom exact, nommé(s) ci-dessus.** Le pré-enregistrement ne désignait par leur nom que le script du #502 et celui du #515 ; il n'avait pas anticipé le compagnon évident des deux — l'**audit du #501 lui-même**.

### Ce que ce cas non prévu est réellement — mesuré après coup

`nonml_borrowed_figures_confrontation_audit.py` appelle `en_gras_dans` aux lignes 95-97 pour **recalculer par une route indépendante les mêmes classes que le #501 backtest** — c'est le rôle documenté de tout script `_audit.py` de cette série (recalcul, pas nouvelle conclusion). Il ne publie **aucun verdict substantiel distinct** de celui du #501 : il vérifie sa cohérence interne. **Ce n'est pas une lacune au sens de la question posée** — mais le pré-enregistrement ne l'excluait pas par son nom, donc il est compté et publié ici plutôt que retiré après coup.

## Partie 3 — ce que consomment les scripts important le module du #501 sans celui du #502

- scripts important `nonml_borrowed_figures_confrontation_backtest` sans `nonml_contextual_confrontation_backtest` : **8**

| Script | Attributs `c501.*` consommés |
|---|---|
| `nonml_borrowed_figures_confrontation_audit.py` | `chiffres_seuls`, `en_gras_dans` |
| `nonml_borrowings_temporal_direction_audit.py` | `sections_backlog` |
| `nonml_contextual_confrontation_backtest.py` | `MOI`, `chiffres_seuls`, `en_gras_dans`, `sections_backlog` |
| `nonml_rectification_rate_audit.py` | `sections_backlog` |
| `nonml_rectification_rate_backtest.py` | `sections_backlog` |
| `nonml_structured_rectification_audit.py` | `sections_backlog` |
| `nonml_structured_rectification_backtest.py` | `sections_backlog` |
| `nonml_untested_detectors_lift_backtest.py` | `MOI`, `chiffres_seuls`, `en_gras_dans`, `sections_backlog` |

> `chiffres_seuls` est un simple découpage de texte en valeurs numériques candidates — **pas** un jugement de confirmation. `sections_backlog`/`git`/`recensement_500` sont des utilitaires génériques sans rapport avec la fiabilité du témoin. Seul `en_gras_dans` porterait le défaut mesuré au #515.

> **3** script(s) consomment `en_gras_dans` via cette voie : `nonml_borrowed_figures_confrontation_audit.py`, `nonml_contextual_confrontation_backtest.py`, `nonml_untested_detectors_lift_backtest.py` — le même ensemble que la Partie 2 (accord entre les deux routes de comptage), pas des cas supplémentaires.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| `en_gras_dans` appelée dans exactement 2 fichiers | 2 | 3 | **réfutée** |
| 0 « troisième cas » | 0 | 1 | **réfutée** |
| scripts sans #502 : jamais `en_gras_dans` | 0 | 3 | **réfutée** |

## Critères de succès

1. Table des 4 témoins publiée, aucun recalculé — **OUI**.
2. Fichiers `en_gras_dans` recensés et classés (3 recensés) — **OUI**.
3. Attributs `c501.*` publiés pour les 8 scripts sans #502 — **OUI**.
4. Tout « troisième cas » nommé et signalé comme témoin invalidé — **OUI**.
5. Absence de troisième cas publiée sans minimiser si applicable — **OUI**.

**PASS** — le critère porte sur le **procédé** : une synthèse bibliographique/code, pas une nouvelle mesure de marché.

Simulation 300 € et robustesse **sans objet** : cycle de synthèse, aucune position, aucun paramètre numérique.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date de son exécution.
