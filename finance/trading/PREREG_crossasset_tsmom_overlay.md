# Pré-enregistrement — momentum cross-actifs (E3, fil économique/multi-actifs)

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global du backlog non-ML (dernier total publié : **372**
hypothèses testées). **Cycle de STRATÉGIE**, première exécution
réelle du fil `ECONOMIC_MULTIASSET_BACKLOG.md` (E3), débloquée au #534
(données confirmées prêtes, aucun arbitrage requis pour cette piste,
contrairement à E1/E2).

## L'hypothèse — momentum cross-actifs (time-series momentum)

**Time Series Momentum** (Moskowitz, Ooi & Pedersen 2012 ; généralisé
par Asness, Moskowitz & Pedersen 2013, *Value and Momentum
Everywhere*) : un actif dont le rendement récent est positif tend à
continuer à surperformer à court/moyen terme, indépendamment de sa
performance relative aux autres actifs (momentum en **série
temporelle**, pas en coupe transversale). Jamais testé dans ce
dépôt : le momentum déjà testé (#4, #14, #37…) est intra-indice
(action contre elle-même dans le temps, univers actions seul) ; ce
cycle teste le signal **appliqué séparément à 4 classes d'actifs**
(actions, obligations, or, dollar), formant un portefeuille dont
l'exposition à chaque jambe dépend de sa **propre** tendance.

## Univers — figé par `ECONOMIC_MULTIASSET_BACKLOG.md`, avant ce cycle

| Jambe | Instrument | Fichier |
|---|---|---|
| Actions | NASDAQ-100 (NDX) | `data/nasdaq100_daily.txt` |
| Obligations longues US | `TLT` (proxy) | `data/tlt_daily.txt` |
| Or | `GLD` (proxy) | `data/gld_daily.txt` |
| Dollar US | `UUP` (proxy) | `data/uup_daily.txt` |

**NDX choisi pour la jambe actions** (pas Composite) : la fenêtre
commune fixée par `GLD` est **19/08/2016 → 18/08/2026**, or
`nasdaq_composite_daily.txt` ne débute qu'au 13/07/2021 — trop court
pour couvrir cette fenêtre. NDX couvre depuis 1985, largement
suffisant.

**Fenêtre** : 19/08/2016 → 18/08/2026 (~10 ans), **déjà figée par la
contrainte GLD** dans `ECONOMIC_MULTIASSET_BACKLOG.md` avant ce cycle
— non ajustée ici.

## Le signal — déclaré avant tout calcul, un seul jeu de paramètres

Pour chaque jambe *i*, séparément :
- `trend_i(t) = signe(rendement log cumulé sur les 252 dernières
  séances closes avant t)` — lookback standard de la littérature TSMOM
  (12 mois, Moskowitz-Ooi-Pedersen 2012), **causal** (n'utilise que des
  clôtures strictement antérieures à `t`, décalage explicite d'1 jour
  pour l'exécution).
- Poids de la jambe : `w_i(t) = 0,25` si `trend_i(t) > 0`, **`0,0`
  sinon** (jambe en tendance négative → position nulle, capital libéré
  reste en cash à 0 % — pas de redistribution aux autres jambes, choix
  le plus simple, aucune hypothèse supplémentaire).
- **Benchmark Buy&Hold** : `w_i = 0,25` pour les 4 jambes, en
  permanence (portefeuille équipondéré statique, jamais rebalancé par
  un signal).
- **Coûts** : 5 bps aller-retour par unité de turnover
  (`Σ|Δw_i|/2`), même convention que le reste du dépôt.
- **Aucune redistribution, aucun levier** : la position brute du
  portefeuille varie entre 0 % et 100 % du capital selon le nombre de
  jambes actives (jamais > 100 %).

## Le protocole

1. Charger les 4 séries, aligner sur les dates **communes aux 4**
   (intersection stricte) dans la fenêtre 19/08/2016 → 18/08/2026.
2. Calculer `trend_i(t)` (252j, causal) et `w_i(t)` pour chaque jambe.
3. P&L brut du portefeuille et du benchmark (rendements simples,
   pondération par jambe), turnover de chacun.
4. Sauvegarder au schéma **portefeuille** de
   `nonml_pass_validation_battery.py`
   (`pnl_gross_ov`, `pnl_gross_bh`, `turn_ov`, `turn_bh`, `dates`) dans
   `results/nonml_crossasset_tsmom_overlay_pnl.npz`.
5. **Niveau 1** : `trading_metrics` net de coûts (5 bps), Sharpe et
   rendement total, overlay vs Buy&Hold.
6. **Règle 9, obligatoire dans ce cycle** (règle du fil, plus stricte
   que le reste du backlog) : appliquer telle quelle la batterie
   partagée `nonml_pass_validation_battery.py` (coûts 3x/5x, crise
   2000-2002/2008-2009/COVID/2022, stabilité temporelle 4 folds, SPA
   1-candidat, DSR à `n_trials` = dernier total publié du backlog,
   `var_trials` approximé par la même fonction partagée
   `approx_var_trials()`).

## Critère de succès — chiffré, deux niveaux distincts (convention du backlog)

1. **PASS niveau 1** : Sharpe annualisé **ET** rendement total net de
   coûts de l'overlay > Buy&Hold sur la fenêtre commune.
2. **PASS RENFORCÉ (Règle 9)** : niveau 1 **ET** les 5 contrôles de la
   batterie partagée (coûts, crise, stabilité, SPA, DSR) passent tous.
3. Les deux niveaux publiés **séparément et honnêtement**, même si
   seul le niveau 1 passe (cas le plus fréquent dans ce backlog,
   documenté sur 372 essais antérieurs).
4. Aucun ajustement du signal après avoir vu un résultat intermédiaire.
5. Audit indépendant : recalcul du signal et du P&L par une route
   distincte (vérification vectorisée vs boucle explicite, ou
   `numpy`/`pandas` alternée), confirmation de l'absence de fuite
   (le signal à `t` n'utilise aucune donnée de `t` ou postérieure).

> **PASS** (ce cycle) = les 5 points de procédure. Le **verdict de la
> stratégie elle-même** (niveau 1 et Règle 9) est rapporté
> indépendamment, PASS ou FAIL, sans conditionner la validité
> procédurale du cycle.

## Prédictions — falsifiables

1. Le portefeuille TSMOM bat Buy&Hold en Sharpe **et** en rendement
   net de coûts sur la fenêtre (PASS niveau 1) : **incertain, prédit
   à 50/50** — littérature favorable au TSMOM cross-actifs, mais le
   momentum intra-actif déjà testé dans ce dépôt (#4, #14) a
   systématiquement échoué à passer le DSR, et la fenêtre commune
   (~10 ans, dominée par un régime haussier prolongé) désavantage
   structurellement tout signal qui réduit l'exposition actions.
2. **Si PASS niveau 1** : le contrôle DSR (e) échoue, cohérent avec
   les **372** essais antérieurs du backlog (0 PASS RENFORCÉ jamais
   observé à ce n_trials pour un candidat scalaire ou panier).
3. Le contrôle de crise (b) est le plus susceptible d'échouer : un
   signal qui désinvestit après la baisse (lag 252j) rate typiquement
   le creux et le rebond initial des grandes corrections (schéma déjà
   documenté pour #13, #22, #49 dans ce dépôt).

## Ce que ce cycle ne fait pas

- Il ne **modifie** ni E1 ni E2, toujours bloqués sur l'arbitrage #432.
- Il ne **teste** aucune variante du lookback (252j fixé, robustesse
  ±20% en 7a seulement si PASS niveau 1, jamais un retuning).
- Il ne **redistribue** pas le capital libéré par une jambe inactive
  (design le plus simple, pas d'hypothèse de substitution).

## Simulation 300 € et robustesse

**Si PASS niveau 1 uniquement** (voir protocole général du firing) :
grille de perturbation ±20% sur le lookback (202j, 302j, non
retunées après résultat) ; simulation 300 € sur les ~3 derniers mois
disponibles de la fenêtre commune.

## Engagements

1. Résultat rapporté tel quel, y compris si les deux niveaux échouent.
2. Univers, fenêtre et signal **inchangés** après mesure.
3. **Aucune redistribution ni retuning découverts en cours de calcul**
   ne sera ajouté sans le déclarer comme limite, pas comme correction
   silencieuse.
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
