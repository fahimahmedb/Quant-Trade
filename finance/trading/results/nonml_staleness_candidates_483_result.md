# Vérification des 2 candidats de staleness du #483 (pré-enregistré)

Le #522 a signalé 2 candidats dans le dictionnaire `V` du
#483, tous deux mentionnés au #518 avec des marqueurs de
contradiction. Ce cycle vérifie si le #518 parle vraiment du
même objet, ou d'un objet distinct confondu par la
réduction de nom du screen mécanique du #522.

## `coverage_wording_fix`

- mention au #518 (prose sans suffixe `.py`) : trouvée
  - citation : « | `coverage_wording_fix_audit`, `report_idempotence_backtest`, `reproducibility_campaign_v2_audit` | **FAUSSE, VERDICT À REVOIR** (3) | »
- `PREREG_coverage_wording_fix.md` est-il le pré-enregistrement du même cycle que `nonml_coverage_wording_fix_audit.py` (vérifié sur pièce, en-tête du PREREG) : **OUI**
- l'axe d'évaluation du #518 est-il « le chiffre cité par le #485 » (réparabilité d'un littéral), distinct de « MAL CLASSÉ » (mot de la self-déclaration absent de `MOTS`) : **OUI, axe distinct**

- `PREREG_coverage_wording_fix.md` existe : **OUI**
- `nonml_coverage_wording_fix_result.md` (sans suffixe) existe : **NON**
- toujours orphelin (population du #483 valide) : **OUI**

- auto-déclaration actuelle : « outillage documentaire »
- classement mécanique aujourd'hui : **RÉSULTAT ATTENDU (aucun mot de la liste)**
- verdict `MAL CLASSÉ` du #483 toujours exact (la règle se trompe encore de la même façon) : **OUI**

> **Faux positif confirmé — pour une raison différente de l'hypothèse du pré-enregistrement.** L'hypothèse annoncée (deux objets distincts, confondus par une collision de nom) **est fausse** : `PREREG_coverage_wording_fix.md` est bien le pré-enregistrement du même cycle que `nonml_coverage_wording_fix_audit.py`. **Mais le #518 porte sur un axe d'évaluation entièrement différent** — la réparabilité d'un chiffre cité par le #485 — **sans rapport** avec l'axe du #483 (un mot de self-déclaration absent de `MOTS`). Les deux vérifications mécaniques (population toujours orpheline, règle encore mal calibrée de la même façon) confirment que **le verdict du #483 n'est pas contredit.**

## `duplicate_sweep_coverage`

- mention au #518 (prose sans suffixe `.py`) : trouvée
  - citation : « | `duplicate_sweep_coverage_audit`, `content_defined_magnitudes_audit`, `content_defined_magnitudes_backtest`, `dsr_corrected_trials_backtest`, `idempotence_fam »
- `PREREG_duplicate_sweep_coverage.md` est-il le pré-enregistrement du même cycle que `nonml_duplicate_sweep_coverage_audit.py` (vérifié sur pièce, en-tête du PREREG) : **OUI**
- l'axe d'évaluation du #518 est-il « le chiffre cité par le #485 » (réparabilité d'un littéral), distinct de « MAL CLASSÉ » (mot de la self-déclaration absent de `MOTS`) : **OUI, axe distinct**

- `PREREG_duplicate_sweep_coverage.md` existe : **OUI**
- `nonml_duplicate_sweep_coverage_result.md` (sans suffixe) existe : **NON**
- toujours orphelin (population du #483 valide) : **OUI**

- auto-déclaration actuelle : « outillage documentaire »
- classement mécanique aujourd'hui : **RÉSULTAT ATTENDU (aucun mot de la liste)**
- verdict `MAL CLASSÉ` du #483 toujours exact (la règle se trompe encore de la même façon) : **OUI**

> **Faux positif confirmé — pour une raison différente de l'hypothèse du pré-enregistrement.** L'hypothèse annoncée (deux objets distincts, confondus par une collision de nom) **est fausse** : `PREREG_duplicate_sweep_coverage.md` est bien le pré-enregistrement du même cycle que `nonml_duplicate_sweep_coverage_audit.py`. **Mais le #518 porte sur un axe d'évaluation entièrement différent** — la réparabilité d'un chiffre cité par le #485 — **sans rapport** avec l'axe du #483 (un mot de self-déclaration absent de `MOTS`). Les deux vérifications mécaniques (population toujours orpheline, règle encore mal calibrée de la même façon) confirment que **le verdict du #483 n'est pas contredit.**

## Le compte

- candidats vérifiés : **2**
- faux positifs confirmés (population et verdict intacts) : **2**
- vrais candidats (correction nécessaire) : **0**

> **Les 2 candidats du #522 pour le #483 sont des faux positifs — mais pas pour la raison annoncée au pré-enregistrement.** L'hypothèse d'une collision de nom (objets distincts) est **fausse** : `PREREG_coverage_wording_fix.md` et `PREREG_duplicate_sweep_coverage.md` sont bien les pré-enregistrements des mêmes cycles que les scripts `_audit.py` discutés au #518. **La vraie raison est un désaccord d'axe d'évaluation** : le #518 juge la réparabilité d'un chiffre cité par le #485, le #483 juge si le mot de self-déclaration figure dans `MOTS` — deux questions indépendantes sur le même objet. **Aucune correction du dictionnaire `V` du #483 n'est nécessaire.** Le lot est clos.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Les 2 sont des objets distincts (mécanisme du faux positif = collision de nom) | 2 objets distincts | 2/2 sont en fait le même cycle | **réfutée** |
| Population du #483 tient pour les 2 | 2 | 2 | **vérifiée** |
| Verdict MAL CLASSÉ reste exact pour les 2 | 2 | 2 | **vérifiée** |

**La prédiction 1 est réfutée sur son mécanisme précis, et c'est le résultat le plus instructif du cycle.** J'avais annoncé une collision de nom ; la vraie cause est un désaccord d'axe d'évaluation. **La conclusion pratique (faux positif, pas de correction nécessaire) tient quand même** — mais pour une raison que je n'avais pas anticipée, publiée telle quelle plutôt que présentée comme si l'hypothèse initiale avait été confirmée.

## Critères de succès

1. Les 2 candidats vérifiés, verdict et fichier cités — **OUI**.
2. Statut identique/distinct publié pour chacun — **OUI**.
3. Si faux positifs : cause précise publiée (2/2) — **OUI**.
4. Si vrai candidat : correction appliquée avec diff borné (0 vrai(s)) — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : vérifier un candidat de staleness signalé par un écran mécanique, sans se fier au screen ni forcer une correction non nécessaire.

Simulation 300 € et robustesse **sans objet** : cycle de vérification bibliographique/code, aucune position.
