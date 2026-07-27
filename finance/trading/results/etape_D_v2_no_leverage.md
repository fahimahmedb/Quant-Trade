# Étape D v2 — Overlay sans effet de levier (cap=1.0×) — test final unique

Hypothèse unique, pré-enregistrée AVANT ce test (voir docstring du script). Seul changement vs Étape D d'origine : cap=1.0× au lieu de 1.5× (coupe extrême 95e percentile inchangée). Testé UNE SEULE FOIS sur Russell 2000/S&P 500/DAX — pas de recherche de paramètres.

## Résultat sur les données de conception (sanity check, PAS le test final)

| Marché | BuyHold Sharpe | BuyHold MDD% | v2 Sharpe | v2 MDD% | ΔMDD rel. | Rdt/BH | Critère |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.78 | -24.3 | +0.67 | -17.2 | +29.4% | 69.2% | non |
| NDX (40 ans) | +0.52 | -82.9 | +0.65 | -57.2 | +31.0% | 87.9% | **OUI** |

## Test final unique — marchés indépendants (Russell 2000 / S&P 500 / DAX)

| Marché | BH Sharpe | BH MDD% | v2 Sharpe | v2 MDD% | Expo moy. | %j expo>1.0× | ΔMDD rel. | Rdt/BH | Critère |
|---|---|---|---|---|---|---|---|---|---|
| Russell 2000 | +0.39 | -59.9 | +0.44 | -47.9 | 0.84 | 0.0% | +20.1% | 76.2% | NON |
| S&P 500 | +0.44 | -56.8 | +0.49 | -49.8 | 0.78 | 0.0% | +12.3% | 65.6% | NON |
| DAX | +0.43 | -54.8 | +0.40 | -49.0 | 0.96 | 0.0% | +10.6% | 81.0% | NON |

**0/3 marchés indépendants atteignent le critère de succès avec Overlay v2.**

**Verdict honnête** : le retrait du levier (cap=1.0×) était motivé par le mécanisme d'amplification identifié sur DAX/Russell/NDX (exposition souvent >1.0×, aggravant le drawdown), pas par un ajustement a posteriori aux chiffres de Russell/S&P 500/DAX. Il ne corrige PAS le mode d'échec spécifique du S&P 500 (érosion du rendement, exposition déjà <1.0× en moyenne dans la version originale) — signalé ici, pas masqué. Toute nouvelle tentative sur ces mêmes 3 marchés constituerait à partir de maintenant du data-snooping (cf. protocole anti-snooping, règle #1) : une correction du mode d'échec S&P 500 devra être validée sur un marché encore jamais touché.
