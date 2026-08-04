# Pré-enregistrement — Corrélation cross-marché NDX-Russell 2000 (domestique), overlay défensif

**Committé AVANT tout calcul.** Cycle #196 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Étend le SEUL mécanisme macro-externe purement défensif à avoir
dépassé le seuil niveau 1 à ce jour dans ce backlog (#193, corrélation
internationale NDX-DAX, PASS 4/5 mais FAIL Règle 9 au #194) à une paire
DOMESTIQUE : large-cap technologique (NDX) vs small-cap (Russell 2000).
Histoire économique DISTINCTE du #193 : une hausse de la corrélation
NDX-Russell 2000 signalerait une perte de la diversification interne au
marché américain par CAPITALISATION (rotation sectorielle/de taille qui
s'efface en période de stress), plutôt qu'une perte de diversification
GÉOGRAPHIQUE internationale. Distinct aussi du #90 (corrélation moyenne
PAR PAIRES entre les 100 titres INTRA-NDX-100). Direction du signal
réutilisée à l'identique du #90/#193 (corrélation ÉLEVÉE = défavorable),
Règle 7.

**Déclaration explicite (Règle 2)** : ce cycle est pré-engagé comme la
**DERNIÈRE extension de paire de corrélation cross-marché testée dans ce
backlog**, quel que soit le résultat obtenu ici. Après le #90 (intra-
titre), le #193 (international NDX-DAX) et ce #196 (domestique
NDX-Russell 2000), la sous-famille "corrélation comme porte défensive"
sera considérée close — pas un point de départ pour tester
systématiquement toutes les paires de marchés restantes (NDX-Composite,
DAX-Russell2000, DAX-S&P500, etc.), ce qui constituerait une recherche
de paramètre déguisée en hypothèses indépendantes.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — appliqué de
façon uniforme comme au #193, y compris à NDX et Russell 2000
eux-mêmes (le signal est un ÉCART de co-mouvement, pas un rendement
absolu de l'un des deux, cohérent avec le #192).

## 3. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier — identique au #193)

- Corrélation glissante : `corr(t) = Pearson(rendements log NDX,
  rendements log Russell 2000)` sur une fenêtre glissante de **60 jours,
  réutilisée à l'identique du #90/#193** (aucun nouveau paramètre de
  fenêtre), calculée sur les dates communes aux deux séries (calendriers
  américains, alignement direct sans décalage de fuseau horaire
  contrairement au #193 international).
- Alignement causal sur le marché cible : `ffill` (calendrier du marché
  cible) puis `shift(1)` — identique aux #175/#178/#186/#187/#191/#192/
  #193, Règle 7.
- Seuil : **tercile EXPANDING** de `corr_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `corr_lag(t)` est dans son tercile expanding le PLUS HAUT (corrélation
  NDX-Russell 2000 élevée — perte de diversification interne par
  capitalisation), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #193)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre de
corrélation réutilisée, un critère multi-marché figé, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Contrairement au #193 (NDX-DAX, deux calendriers distincts avec un
   décalage horaire documenté comme limite), NDX et Russell 2000
   partagent EXACTEMENT le même calendrier de bourse américain — le
   signal pourrait donc être plus bruité s'il capture une corrélation
   quasi-mécanique entre deux indices déjà fortement co-intégrés au sein
   du même marché domestique, diluant l'information distincte apportée
   par la mesure (contrairement à NDX-DAX, deux marchés véritablement
   indépendants géographiquement).
2. Comme au #193, la robustesse pourrait ne pas être parfaite et un
   éventuel PASS niveau 1 pourrait ne pas survivre à la Règle 9 (déjà
   observé au #194 pour le #193 lui-même).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
