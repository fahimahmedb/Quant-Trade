# Pré-enregistrement — Différentiel de taux US-Allemagne (DGS10 − DE10Y), overlay défensif

**Committé AVANT tout calcul.** Cycle #195 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

La divergence de politique monétaire entre la Fed et la BCE, mesurée par
l'écart entre les taux longs américain et allemand, est un moteur
documenté des flux de capitaux internationaux et de la force relative
du dollar (carry trade, littérature sur la parité des taux d'intérêt).
Un écart qui se CREUSE (taux US relativement plus élevé) signale un
resserrement relatif de la politique américaine, historiquement associé
à des flux de capitaux VERS les actifs américains et hors des actifs
risqués internationaux — hypothèse testée ici comme signal de RISQUE
plutôt que d'opportunité. Distinct de tous les signaux de taux déjà
testés dans ce backlog (#44/#114/#134/#149 pente domestique US 10a-3m/
10a-2a, #175/#178/#186/#187 niveau/volatilité/inversion domestique US
seul) : ici le signal est un ÉCART ENTRE DEUX PAYS, jamais testé sous
cette forme.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — appliqué de
façon uniforme comme les autres signaux macro-économiques externes de
ce backlog (#175/#178/#186/#187/#191/#192/#193).

## 3. Traitement de la fréquence mensuelle (déclaré AVANT calcul, limite critique)

`data/de10y_monthly.csv` (FRED `IRLTLT01DEM156N`) est une série
**MENSUELLE représentant la moyenne du taux allemand 10 ans sur le
mois**, datée au premier jour du mois couvert. Cette moyenne n'est
matériellement connaissable qu'APRÈS la fin du mois qu'elle résume — un
`ffill` naïf depuis la date du 1er du mois introduirait donc une fuite
d'environ un mois. **Correction pré-enregistrée** : la date de chaque
observation est décalée d'un mois calendaire complet
(`pd.DateOffset(months=1)`) AVANT le `ffill` — la moyenne de mai devient
ainsi disponible à partir du 1er juin, jamais avant. Un `shift(1)`
supplémentaire (jour de bourse) est appliqué ensuite par cohérence avec
l'alignement causal quotidien déjà utilisé pour DGS10
(`load_rate_lag()`, Règle 7). Cette double correction est conservatrice
(staleness effective jusqu'à ~31-60 jours selon la position dans le
mois), documentée comme limite structurelle assumée, pas comme
optimisation.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `RateDiff(t) = DGS10_lag(t) − DE10Y_lag_décalé(t)` (les deux termes
  déjà causaux selon leur traitement respectif ci-dessus).
- Seuil : **tercile EXPANDING** de `RateDiff(t)` (technique établie aux
  #169/#177/#183/#191/#192/#193, aucune fenêtre fixe à choisir).
- Direction (choisie AVANT calcul, aucune connaissance du résultat) :
  `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique** des
  #175/#176/#178/#186/#187/#191/#192/#193) si `RateDiff(t)` est dans son
  tercile expanding le PLUS HAUT (écart US-Allemagne le plus large,
  resserrement relatif US le plus marqué), `1,0x` sinon. **Jamais de
  levier** — design purement défensif, cohérent avec la pratique établie
  de cette famille de signaux. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les #175/#178/#186/#187/#191/#192/#193)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La littérature sur les différentiels de taux concerne principalement
   les flux de CHANGE (carry trade), pas directement les rendements
   d'indices ACTIONS — le lien avec le risque equity est une
   extrapolation, pas un résultat établi pour ce cas précis.
2. La staleness structurelle du signal (jusqu'à ~2 mois) pourrait le
   rendre trop lent pour capter des régimes de marché qui évoluent plus
   vite.
3. Comme pour toute la famille de signaux de taux déjà testée
   (#175/#178/#186/#187), un design purement défensif sans levier
   compensatoire limite structurellement le rendement total, et le
   niveau/écart de taux pourrait à nouveau se révéler contre-productif
   (coïncidant mal avec les régimes de croissance/crise).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
