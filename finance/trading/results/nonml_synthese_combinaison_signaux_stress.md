# Synthèse — Sous-thread combinaison de signaux de stress (#296-#304, 9 cycles)

Cycle #305 du backlog non-ML. Synthèse pure — aucun nouveau calcul,
relecture des résultats déjà committés.

## 1. Contexte

Après la clôture de la campagne macro-externe étendue (#276-296,
synthèse v8 au #295), la seule idée retenue comme non-redondante était
de combiner les deux MEILLEURS signaux macro-externes de la session —
défaut de paiement cartes de crédit (#286, PASS 4/5, Règle 9 3/5, le
meilleur score) et conditions financières NFCI (#291, PASS 4/5, Règle
9 2/5). Ce qui a commencé comme un test unique (#296) s'est prolongé
en un sous-thread de 9 cycles explorant systématiquement les logiques
de combinaison possibles sur un panel croissant de signaux de stress
tous individuellement pré-validés (PASS niveau 1) AVANT leur
intégration — jamais choisis après observation d'un score combiné.

## 2. Tableau récapitulatif des 9 cycles

| # backlog | Construction | Signaux | PASS niveau 1 | Score Règle 9 |
|---|---|---|---|---|
| #298 | ET (intersection) | défaut carte + NFCI | **PASS NET 5/5** | 2/5 (#299) |
| #300 | OU (union) | défaut carte + NFCI | FAIL 3/5 | — (FAIL, pas de battery) |
| #301 | Majorité ≥2/3 | défaut carte + NFCI + BAA10Y | **PASS NET 5/5** | 2/5 (#302) |
| #303 | Sizing continu (0-3 votes) | défaut carte + NFCI + BAA10Y | PASS 4/5 | 2/5 (#305) |
| #304 | Majorité élargie ≥3/4 | défaut carte + NFCI + BAA10Y + corr NDX-DAX | **PASS NET 5/5** | **3/5 (#306)** |

## 3. Enseignements

**a. La sélectivité bat la couverture large.** Le seul échec niveau 1
de tout ce sous-thread est l'OU (#300, union de deux portes) — le
Sharpe bat Buy&Hold sur les 5 marchés sans exception, mais le
rendement échoue précisément sur les 2 marchés où l'union est la plus
active (Composite 77,9%, NDX 30,9%). Toutes les autres constructions
(ET, majorité, sizing continu, majorité élargie) sont plus SÉLECTIVES
(temps actif typiquement 5-28%) et obtiennent toutes un PASS niveau 1.

**b. Le score Règle 9 était structurellement plafonné à 2/5 sur le
trio à 3 signaux, quelle que soit la logique de combinaison.** ET,
majorité ≥2/3 et sizing continu obtiennent chacun 2/5 — mais avec des
PROFILS D'ÉCHEC DIFFÉRENTS : ET et majorité échouent sur la stabilité
temporelle (2/4 folds) en tenant les coûts ; le sizing continu inverse
ce profil (stabilité OK 3/4 folds, coûts en échec à cause d'un
turnover plus élevé à 4 niveaux de position). Le total ne bouge pas,
mais la NATURE de la faiblesse change selon la construction — un
signal que le plafond n'est pas un artefact d'une seule construction
précise.

**c. L'ajout d'un 4e signal économiquement DISTINCT a levé ce
plafond.** Le passage de 3 à 4 signaux (ajout de la corrélation
cross-marché NDX-DAX #193, seul signal de la famille mesurant la
contagion internationale plutôt que le stress d'endettement/crédit)
fait passer le score Règle 9 de 2/5 à **3/5 (#306)** — égalant le
meilleur score de toute la session (#286 seul). Les TROIS contrôles
structurels (coûts, crise, stabilité) passent SIMULTANÉMENT pour la
première fois sur cette famille, et le SPA progresse nettement
(p=0,338 contre p=1,000 systématique aux 3 batteries précédentes du
même panel) sans toutefois devenir significatif à 5%. Le DSR reste en
échec net dans tous les cas (n_trials croît avec la taille du backlog,
mécaniquement défavorable).

**d. Aucun cas de "porte trop rare pour être informative".** Le risque
déclaré à chaque PREREG de ce sous-thread (intersection/majorité trop
sélective pour être utile) ne s'est matérialisé nulle part — même la
porte à 4 signaux avec vote ≥3/4 (la plus stricte, 13-21% actif) reste
un PASS net.

## 4. Réponse à la question posée au PREREG : poursuivre à 5 signaux ou clore ?

**Recommandation : clore ce sous-thread ici, sans ajouter de 5e
signal, pour les raisons suivantes.**

- Chaque signal intégré à ce jour (#286, #291, #199, #193) était un
  PASS niveau 1 déjà validé AVANT son entrée dans une combinaison —
  discipline strictement respectée sur les 9 cycles. Mais le nombre de
  signaux macro-externes ou cross-marché individuellement PASS
  DISPONIBLES dans ce backlog est maintenant restreint : en dehors du
  spread de crédit BAA10Y (FAIL global 1/5 mais Sharpe passant, déjà
  intégré) et de STLFSI4 (FAIL 3/5, économiquement trop redondant avec
  NFCI selon la conclusion du #293), il n'existe pas de 5e candidat
  clairement distinct et déjà validé à ajouter sans forcer.
- Continuer à ajouter des signaux dans l'espoir de faire encore
  progresser le score Règle 9 commencerait à ressembler à une
  RECHERCHE COMBINATOIRE — même si chaque étape individuelle reste
  défendable, la SUITE d'étapes (ET→OU→majorité→sizing→panel élargi)
  a été motivée en partie par l'observation que le score plafonnait,
  ce qui est une forme de optimisation implicite sur le nombre
  d'essais qu'il faut nommer honnêtement ici, même si chaque n_trials
  individuel a été correctement compté dans le DSR (n_trials=311 à ce
  jour).
- Le score 3/5 obtenu, bien qu'égalant le meilleur de la session,
  reste sous le seuil de promotion utilisé pour le guide de
  déploiement (Candidats A/B à 4/5) — un 5e signal ajouté uniquement
  pour chercher ce dernier point manquant serait la définition même du
  data snooping que ce protocole cherche à éviter.

## 5. Bilan chiffré du sous-thread

- 9 cycles (#296-#304), 4 PASS niveau 1 nets/quasi-nets sur 5
  constructions testées (ET, majorité 2/3, sizing continu, majorité
  élargie — seule l'OU a FAIL).
- Meilleur score Règle 9 du sous-thread : 3/5 (#304, panel à 4
  signaux) — égale le record de la session entière (#286).
- 0 bug de calcul dans un backtest livré ; 1 bug trouvé et corrigé
  dans un script d'AUDIT avant tout commit de résultat (#296, leçon
  own-start systématiquement réappliquée dans les 8 audits suivants
  sans nouvel incident).

Voir `NONML_STRATEGY_BACKLOG.md` entrées #298-#306 pour le détail
complet de chaque cycle.
