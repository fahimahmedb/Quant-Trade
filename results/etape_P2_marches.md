# Étape P2 — Marchés de prédiction

## 1. Description de la source

Les **marchés de prédiction** (Polymarket, PredictIt, Betfair Exchange...) publient un
prix qui s'interprète comme une probabilité implicite de victoire : des agents engagent
de l'argent réel (ou virtuel liquide) sur l'issue du 2nd tour, ce qui agrège en principe
l'information disponible plus vite et plus largement qu'un sondage ponctuel.

**Loader hybride** (`pp_markets.load_market_prob`) :

1. Tentative **live** (`_fetch_live`, timeout court de 2 s) — non câblée vers un endpoint précis dans
   ce dépôt (les URLs des marchés électoraux changent au fil des campagnes) ; lève
   `NotImplementedError` par construction, capturée silencieusement.
2. **Fallback** systématique sur `data/fr_markets_snapshot.json` (instantané offline).
3. Si l'élection n'a ni prix live ni entrée snapshot → aucune tentative de deviner :
   `SourceSignal(available=False)`.

**Couverture réelle** : les marchés de prédiction grand public sur la présidentielle
française n'existent avec un volume significatif que depuis 2017 (essor Polymarket /
PredictIt / Betfair sur les élections). Le snapshot ne couvre donc que **FR_pres_2017** et
**FR_pres_2022**, plus une entrée d'exemple `FR_pres_2027` illustrant l'usage live pour une
élection à venir. Les prix du snapshot sont **approximatifs/illustratifs** (ordre de
grandeur des cotes de fin de campagne d'entre-deux-tours), pas un relevé tick-by-tick
audité — voir `_meta.avertissement` dans le fichier.

## 2. Calibration du biais favori-outsider (favorite-longshot bias)

La littérature empirique sur les marchés de paris et de prédiction (Wolfers & Zitzewitz
2004 ; Snowberg & Wolfers 2010) documente un biais systématique : les prix **sous-estiment**
les favoris et **sur-estiment** les outsiders (prime payée pour le gain "loterie" improbable
de l'outsider). Le marché compresse donc les probabilités vers 0.5 par rapport à la vérité.

**Correction retenue** — extrémisation en espace logit, prior FIXE (jamais ajusté sur le
jeu de test, donc sans fuite d'information) :

```
p_debiaisee = sigmoid(k * logit(p_marche)),   k = FAVORITE_LONGSHOT_K > 1
```
avec **k = 1.15** : k > 1 repousse la probabilité plus loin de 0.5 (favori
poussé vers 1, outsider poussé vers 0), ce qui compense la compression du marché vers le
centre.

Conversion en part de vote 2nd tour, mapping monotone amorti (une quasi-certitude de
marché ne se traduit pas en score plébiscitaire improbable) :

```
r2_share_mean = clamp_share(0.5 + K * (p_debiaisee - 0.5)),   K = SHARE_SLOPE_K
```
avec **K = 0.35**, et un écart-type fixe **sd = 0.04** (marché jugé plutôt
fiable, moins incertain que le prior "sans information" à 0.08 des fondamentaux).

### Avant / après sur les deux élections où un prix de marché est connu

| Élection | Référence | p marché brut | p débiaisé (k=1.15) | Part prévue | Part réelle |
|---|---|---|---|---|---|
| FR_pres_2017 | macron_2017 | 0.87 | 0.90 | 0.640 | 0.661 |
| FR_pres_2022 | macron_2022 | 0.74 | 0.77 | 0.594 | 0.586 |

Le débiaisage accentue l'écart à 0.5 : par exemple un prix brut de 0.87 devient ≈ 0.90 avant conversion en part de vote.

## 3. Backtest hors-échantillon (OOS)

**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :

- Pour prédire l'élection T, `fit()` reçoit l'historique < T — mais c'est un **no-op** pour
  cette source (un prix de marché ne s'entraîne pas sur le passé électoral ; le facteur de
  débiaisage `k` et la pente `K` sont des priors fixes, choisis avant de lire les scores,
  pas ajustés élection par élection).
- Seules **FR_pres_2017** et **FR_pres_2022** ont un prix de marché disponible : toutes les
  élections antérieures sont marquées **indisponibles** par construction (pas de marché
  électoral liquide avant l'essor de ces plateformes). C'est le comportement attendu du
  contrat (`SourceSignal(available=False)`), pas un défaut du modèle — le tableau ci-dessous
  l'illustre par la colonne « (source indispo.) ».

| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |
|---|---|---|---|---|---|---|
| 1988 | FR_pres_1988 | mitterrand_1988 | — | — | 0.540 | (source indispo.) |
| 1995 | FR_pres_1995 | jospin_1995 | — | — | 0.474 | (source indispo.) |
| 2002 | FR_pres_2002 | chirac_2002 | — | — | 0.822 | (source indispo.) |
| 2007 | FR_pres_2007 | sarkozy_2007 | — | — | 0.531 | (source indispo.) |
| 2012 | FR_pres_2012 | sarkozy_2012 | — | — | 0.484 | (source indispo.) |
| 2017 | FR_pres_2017 | macron_2017 | 0.640 | 1.00 | 0.661 | ✓ gagne |
| 2022 | FR_pres_2022 | macron_2022 | 0.594 | 0.99 | 0.586 | ✓ gagne |

**OOS (n=2)** — Brier 0.000 | log-loss 0.005 | MAE part 0.015 | taux de bonne issue 100%

## 4. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Couverture minimale (n=2)** : le backtest OOS ne score que 2017 et 2022 — bien trop peu
   pour valider statistiquement le facteur de débiaisage `k` ou la pente `K`. Ils restent des
   priors motivés par la littérature, pas des paramètres estimés sur ce dépôt.

2. **Snapshot illustratif** : les prix de `data/fr_markets_snapshot.json` reconstituent un
   ordre de grandeur plausible de fin de campagne, pas un relevé horodaté et audité d'un
   flux réel. À remplacer par des données primaires (archives Polymarket/PredictIt/Betfair)
   avant toute publication.

3. **Live non câblé** : `_fetch_live` est un point d'extension qui lève systématiquement
   `NotImplementedError` — le fallback snapshot est donc la voie d'exécution normale de ce
   dépôt, pas un filet de sécurité occasionnel.

4. **Biais favori-outsider potentiellement variable dans le temps/plateforme** : le facteur
   `k` unique appliqué ici ne distingue pas Polymarket de PredictIt, ni les régimes de forte
   vs faible liquidité, alors que l'intensité du biais en dépend empiriquement.

**Conclusion** : ce modèle est un **composant d'un ensemble** (fusion avec fondamentaux,
NLP). Sa faible couverture historique en fait un signal complémentaire tardif (utile
surtout à partir de 2017), pas un substitut aux autres sources.
