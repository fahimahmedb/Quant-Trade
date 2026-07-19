# Audit honnête du module « Prédiction politique »

Auto-audit demandé, puis **correction appliquée**. Ce document garde la trace de
l'erreur ET de sa réparation. Écrit sans complaisance.

## Verdict en une phrase

**Un premier jet gonflait les scores en backtestant des données rédigées en
connaissant l'issue (hindsight). Ces données ont été SUPPRIMÉES.** La base
honnête qui reste (fondamentaux sur macro exogène) est faible — elle ne bat même
pas nettement une heuristique d'une ligne — et c'est le résultat réel à n≈11.

---

## 1. La faille (identifiée puis corrigée)

Les instantanés `data/fr_markets_snapshot.json` et `data/fr_nlp_snapshot.csv`
avaient été **rédigés en connaissant l'issue des élections** (par les sous-agents
et moi) : `p(Macron 2017)=0.87`, `trends(Sarkozy 2012)=0.47`, etc. Le backtest à
fenêtre expansive (`src/pp_backtest.py`) n'entraîne jamais sur le futur, **mais il
ne peut pas laver une donnée qui encode déjà le futur dans sa valeur**. Résultat :
les marchés (Brier 0.000) et le NLP (0.063) mesuraient un **ajustement
rétrospectif**, et la fusion affichait un trompeur Brier 0.14 / 86 %.

### Correction appliquée

1. **Suppression des données rétrospectives** : entrées marchés 2017/2022 et
   lignes NLP 2007-2022 retirées. Ces sources ne portent plus **aucune** donnée
   historique → indisponibles sur les 7 plis (`available=False`), **forward-only**.
   La contrainte est désormais **imposée par le code**, plus seulement documentée.
2. **Correction de la référence 2017** : `hamon` (PS = vrai camp sortant) au lieu
   de `macron`. L'approbation de Hollande (~20) s'applique alors correctement, et
   les fondamentaux prédisent l'effondrement du PS — un call honnête, au lieu d'un
   faux « raté » sur Macron.
3. **Durcissement du backtest** : l'ISSUE (victoire) est scorée même quand le camp
   sortant est éliminé au 1er tour (part = NaN) ; on ne jette plus ces plis.
4. **Baselines** ajoutées (pile ou face, « sortant gagne toujours », « avantage
   sortant ») pour tester si les fondamentaux battent le trivial.

## 2. Le chiffre honnête après correction

| Prédicteur (OOS, 7 plis) | Brier | Log-loss | Bonne issue |
|---|---|---|---|
| Pile ou face (p=0.5) | 0.250 | 0.693 | 43 % |
| « Camp sortant gagne toujours » | 0.318 | 0.888 | 57 % |
| **« Avantage sortant si concourt »** (1 ligne) | **0.216** | 0.623 | **71 %** |
| **Fondamentaux (le modèle)** | 0.295 | 0.909 | 57 % |
| Marchés / NLP | — forward-only (0 pli) — | | |
| Fusion (historique = fondamentaux) | 0.294 | 0.892 | 57 % |

**Constat brutal et honnête** : la régression structurelle **ne bat pas** la
simple règle « le sortant a un léger avantage s'il se représente » (0.216 vs
0.295). À n=7, aucun écart n'est significatif. L'économie politique n'explique
qu'une part modeste du 2nd tour, et le petit échantillon interdit toute
conclusion forte. C'est le vrai visage de la prévision présidentielle structurelle.

## 3. Ce qui est SAIN (vérifié)

- **Discipline OOS** : `run_oos` entraîne sur `ex[:i]` (années strictement
  antérieures). Aucune fuite de code.
- **Standardisation / résidus fondamentaux**, **`fit` no-op marchés**, **`scale`
  NLP** : calibrations bornées sur le passé strict.
- **Aucune requête réseau bloquante** ; reproductible hors-ligne.
- **Fusion** : pondération de précision en logit + plancher d'incertitude
  anti-sur-confiance (sans lui, `P(victoire)` saturait à 1.000).
- **P5 ML** : montre honnêtement le sur-ajustement (GB/XGBoost log-loss > 3 à n≈11).

## 4. Faiblesses résiduelles (documentées)

- **Choix de référence** : coller l'approbation du sortant au « camp » est net pour
  les présidents sortants, plus discutable pour les sièges ouverts (2007, 1974).
- **Macro anciennes approximatives** (surtout l'approbation avant 2002).
- **n = 7 plis** : ordres de grandeur, pas des mesures.

## 5. Prochaine étape : la seule voie honnête pour valider marchés/NLP

Un scrutin **futur** (présidentielle 2027), où le hindsight est **impossible par
construction** : on capte des prix de marché et des signaux Trends **horodatés
avant** le vote, on publie la prévision, puis on compare après coup. C'est l'objet
de la phase suivante (`scripts/run_etape_P6_pred2027.py`, à venir). Le jeu par
circonscription (législatives) reste la voie pour donner au ML des effectifs
suffisants, si cela améliore la prévision.
