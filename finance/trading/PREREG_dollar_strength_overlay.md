# Pré-enregistrement — Force du dollar américain (DTWEXBGS), overlay défensif

**Committé AVANT tout calcul.** Cycle #198 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Un dollar américain qui s'apprécie fortement est un frein documenté aux
bénéfices des multinationales (compétitivité à l'export dégradée,
conversion défavorable des revenus étrangers) et coïncide historiquement
avec des flux de capitaux vers la sécurité (risk-off, "dollar smile"
theory de Stephen Jen). Signal JAMAIS exploité dans ce backlog : angle
macro distinct de tous les signaux de taux (#44/#114/#134/#149/#175/
#178/#186/#187/#195), de volatilité (#191) et de corrélation (#193/#196)
déjà testés — ici c'est un signal de CHANGE, pas de niveau de taux ni de
volatilité.

## 2. Donnée (nouvelle, à récupérer — fetch réseau)

Série FRED `DTWEXBGS` (Nominal Broad U.S. Dollar Index, indice pondéré
des échanges commerciaux, quotidien) — gratuite, même mécanisme de fetch
déjà utilisé pour `vixcls_daily.csv`/`t10y2y_daily.csv` aux #114/#130.
**Limite déclarée à l'avance** : cette série FRED spécifique ne débute
qu'au 2006-01-02 (contrairement à DGS10/VIXCLS qui remontent plus loin)
— historique utilisable pour ce cycle limité à ~20 ans sur les marchés
à longue histoire (NDX, DAX), comparable au Composite (5 ans) en termes
de contrainte, mais nettement plus court que les cycles basés sur les
taux (DGS10 depuis 1962). Sauvegardée telle quelle dans
`data/dtwexbgs_daily.csv`, aucune modification.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — appliqué de
façon uniforme comme les autres signaux macro-économiques externes de
ce backlog (#175/#178/#186/#187/#191/#192/#193/#195/#196/#197).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `USDChange(t) = log(DTWEXBGS(t) / DTWEXBGS(t-21))` (appréciation du
  dollar sur le mois écoulé, **fenêtre 21j réutilisée à l'identique**
  du #192/#170, Règle 7).
- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — **technique identique à `load_rate_lag()`**
  déjà utilisée aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197,
  Règle 7.
- Seuil : **tercile EXPANDING** de `USDChange_lag(t)` (technique
  établie, #169/#177/#183/#191/#192/#193/#195/#196/#197).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `USDChange_lag(t)` est dans son tercile expanding le PLUS HAUT
  (appréciation du dollar la plus forte — frein aux bénéfices,
  risk-off), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#197)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre
réutilisée, un critère multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'historique utilisable (2006+) est nettement plus court que les
   autres signaux macro déjà testés — moins de cycles économiques
   couverts, résultat potentiellement moins généralisable.
2. Le lien dollar fort/actions US est documenté surtout pour les
   BÉNÉFICES des multinationales (effet de plusieurs trimestres, lent),
   pas nécessairement pour le RENDEMENT BOURSIER à court terme capté par
   un signal de changement sur 21 jours.
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197, un
   design purement défensif sans levier compensatoire limite
   structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
