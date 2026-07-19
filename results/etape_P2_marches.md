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

**Correction d'audit — source forward-only** : un premier jet backtestait cette source sur
des prix 2017/2022 **rédigés en connaissant l'issue** (hindsight), ce qui gonflait
artificiellement les scores (cf. `results/AUDIT.md`). Ces prix ont été **supprimés**. Un prix
de marché ne peut être honnêtement backtesté que s'il a été **horodaté avant le scrutin** par
une source vérifiable. Faute d'archives fiables hors-ligne, la source marchés est désormais
**réservée à la prévision d'élections à venir** (2027) : sur tout l'historique 1965-2022 elle
se déclare indisponible. Seule reste une entrée `FR_pres_2027` **vide** (`p=null`), à remplir
par un vrai relevé daté (ou via `_fetch_live`) le moment venu.

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

### Démonstration de la transformation (grille HYPOTHÉTIQUE, pas des élections réelles)

Pour illustrer la mécanique sans aucune donnée rétrospective, on applique la calibration à
une grille de prix de marché fictifs :

| p marché brut | p débiaisé (k=1.15) | Part 2nd tour prévue (K=0.35) |
|---|---|---|
| 0.55 | 0.56 | 0.520 |
| 0.65 | 0.67 | 0.560 |
| 0.75 | 0.78 | 0.598 |
| 0.85 | 0.88 | 0.633 |
| 0.95 | 0.97 | 0.664 |

Le débiaisage accentue l'écart à 0.5 (favori renforcé) ; la conversion en part reste amortie
(une quasi-certitude de marché ne devient pas un score plébiscitaire). Ces lignes sont de la
**pure arithmétique de démonstration**, sans lien avec un scrutin passé.

## 3. Backtest hors-échantillon (OOS)

**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :

- Pour prédire l'élection T, `fit()` reçoit l'historique < T — mais c'est un **no-op** pour
  cette source (un prix de marché ne s'entraîne pas sur le passé électoral ; le facteur de
  débiaisage `k` et la pente `K` sont des priors fixes, choisis avant de lire les scores,
  pas ajustés élection par élection).
- **Aucune** élection historique n'a de prix de marché honnête (données rétrospectives
  supprimées) : toutes sont marquées **indisponibles** (`available=False`). Le backtest ne
  score donc **0 pli** — c'est voulu. Cette source n'apportera de valeur mesurable que sur
  un scrutin futur (2027), où un prix live est capté sans hindsight possible.

| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |
|---|---|---|---|---|---|---|
| 1988 | FR_pres_1988 | mitterrand_1988 | — | — | 0.540 | (source indispo.) |
| 1995 | FR_pres_1995 | jospin_1995 | — | — | 0.474 | (source indispo.) |
| 2002 | FR_pres_2002 | chirac_2002 | — | — | 0.822 | (source indispo.) |
| 2007 | FR_pres_2007 | sarkozy_2007 | — | — | 0.531 | (source indispo.) |
| 2012 | FR_pres_2012 | sarkozy_2012 | — | — | 0.484 | (source indispo.) |
| 2017 | FR_pres_2017 | hamon_2017 | — | — | — (élim. T1) | (source indispo.) |
| 2022 | FR_pres_2022 | macron_2022 | — | — | 0.586 | (source indispo.) |

## 4. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Couverture historique nulle (n=0)** : après suppression des prix rétrospectifs, aucun
   pli n'est scoré. Le facteur de débiaisage `k` et la pente `K` restent des priors motivés
   par la littérature, **non validés** sur données réelles dans ce dépôt.

2. **Validation reportée au futur** : la seule façon honnête de mesurer cette source est de
   capter un prix live **avant** un scrutin à venir (2027) et de comparer après coup. Tout
   prix historique reconstitué a posteriori serait du hindsight — précisément l'erreur
   corrigée ici (cf. `results/AUDIT.md`).

3. **Live non câblé** : `_fetch_live` est un point d'extension qui lève systématiquement
   `NotImplementedError` — le fallback snapshot est donc la voie d'exécution normale de ce
   dépôt, pas un filet de sécurité occasionnel.

4. **Biais favori-outsider potentiellement variable dans le temps/plateforme** : le facteur
   `k` unique appliqué ici ne distingue pas Polymarket de PredictIt, ni les régimes de forte
   vs faible liquidité, alors que l'intensité du biais en dépend empiriquement.

**Conclusion** : ce modèle est un **composant d'un ensemble** (fusion avec fondamentaux,
NLP). Sa faible couverture historique en fait un signal complémentaire tardif (utile
surtout à partir de 2017), pas un substitut aux autres sources.
