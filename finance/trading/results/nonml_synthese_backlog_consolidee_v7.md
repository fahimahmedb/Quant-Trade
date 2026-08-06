# Synthèse consolidée v7 — cycles #276-289

Pas un nouveau backtest. Consolide 14 cycles depuis la v6 (#267,
couvrait jusqu'au #266). État au moment de cette synthèse : **90 PASS
niveau 1 sur 294 hypothèses testées**, 0 PASS RENFORCÉ Règle 9 sur
l'ensemble du backlog.

## A. Correction de doublons (#276) — leçon de discipline anti-snooping

Deux idées proposées à la clôture du #275 (skewness glissante,
proximité du plus bas 52-semaines) se sont révélées être des DOUBLONS
non détectés d'hypothèses déjà testées (#218 et #75 respectivement,
toutes deux déjà FAIL). Corrigées avant tout calcul. **Leçon
opérationnelle directe** : depuis cette correction, chaque nouvelle
idée proposée en fin de cycle est systématiquement vérifiée par grep
explicite (et, pour les données macro externes, par un fetch de test
de disponibilité) avant d'être ajoutée au backlog — discipline
appliquée sans exception aux 13 cycles suivants (#277-289), aucun
nouveau doublon détecté depuis.

## B. Effets calendaires marginaux (#276-277) — confirment le schéma déjà établi

- **#278 (backlog) / effet mi-mois** : FAIL net 0/5 — le milieu du mois
  ne porte pas le même edge que sa frontière (ToM #2/#8, PASS).
- **#279 (backlog) / expiration d'options mensuelle** : FAIL net 0/5 —
  élargir le triple witching (#26) à tous les mois DILUE l'effet
  plutôt que de le renforcer (résultat pire que le #26 lui-même).

Ces deux résultats confirment que les effets calendaires exploitables
dans ce backlog restent concentrés sur des FRONTIÈRES précises
(changement de mois, changement de trimestre, triple witching
trimestriel) — les variantes qui élargissent la fenêtre ou déplacent
le point d'ancrage échouent systématiquement.

## C. Nouveaux mécanismes de régime testés (#279-280)

- **Durée du drawdown** (#281 backlog) : FAIL 2/5 — MDD amélioré sur
  les 5 marchés sans exception, mais rendement insuffisant sur 3/5,
  même schéma "Sharpe/MDD améliorés, rendement insuffisant" que la
  famille macro-externe défensive.
- **Vitesse du taux court DGS3MO** (#282 backlog) : FAIL 1/5 —
  construction méthodologiquement distincte du #175 (magnitude par
  tercile vs signe brut), confirmée non contre-productive (contrairement
  au #175) mais toujours insuffisante.

## D. Famille matière première/sectorielle (#281-283) — premiers signaux hors financier pur

Trois premiers signaux non-financiers de ce backlog, tous FAIL mais
avec des profils informatifs :
- **Immobilier (HOUST, #283 backlog)** : FAIL 1/5, premier signal
  sectoriel.
- **Cuivre (PCOPPUSDM, #284 backlog)** : FAIL 3/5 — le score le PLUS
  PROCHE du seuil renforcé de toute la famille macro-externe récente
  (PASS sur 3/5 marchés).
- **Pétrole WTI (#285 backlog)** : FAIL 2/5, épisode du prix négatif
  du 20/04/2020 vérifié explicitement comme un événement réel (crise
  de stockage COVID), pas un bug.

## E. Le mini-thread stress d'endettement des ménages (#284-287) — le seul PASS de cette période

- **Crédit carte (DRCCLACBS, #286 backlog)** : **PASS net 4/5** — le
  premier PASS niveau 1 de la famille macro-externe depuis le #200 à
  ne PAS être limité en rendement (Sharpe ET rendement tous deux
  supérieurs sur 4 marchés). Robustesse 12/15, plateau cohérent.
- **Batterie Règle 9 sur ce PASS (#287 backlog)** : **3/5**, le
  MEILLEUR score Règle 9 obtenu depuis le début de cette session macro
  (coûts, crise, ET stabilité temporelle — 4/4 folds, une première —
  tous OK ; seuls SPA et DSR échouent). Reste sous les Candidats A et
  B du guide de déploiement (4/5 chacun), pas de promotion.
- **Hypothécaire (DRSFRMACBS, #288 backlog)** : FAIL 1/5, construction
  STRICTEMENT IDENTIQUE au crédit carte — résultat DIVERGENT anticipé
  et confirmé au PREREG.
- **Prêt auto (DRALACBN, #289 backlog)** : FAIL 1/5 — **RÉFUTE LA
  PRÉDICTION EXPLICITE** formulée après les deux résultats précédents
  (hypothèse "déclencheur court-terme = exploitable, long-terme = non"
  attendue confirmée, mais infirmée par ce 3e test).

**Enseignement principal de ce mini-thread** : la divergence entre
crédit carte (PASS) et hypothécaire/auto (FAIL) ne s'explique PAS par
une loi générale simple (durée de la dette, nature du déclencheur
économique) — elle semble plus idiosyncrasique à la série DRCCLACBS
elle-même qu'à une catégorie économique généralisable. Ceci est cohérent
avec un schéma déjà observé ailleurs dans ce backlog (ex. #96 SMA200
breadth PASS vs #78 dispersion FAIL sous PIT, cycle #270-271 : la survie
d'un signal dépend de sa construction précise, pas de sa catégorie).

## F. Leçons méthodologiques transversales de cette période

1. **Le bug "même barre" continue d'apparaître sous de nouvelles
   formes** : au #278 (DAX lead-lag), l'alignement causal
   `ffill+shift(1)` décalait par POSITION dans l'index cible plutôt que
   par comparaison de date réelle — perdant silencieusement une séance
   DAX lors d'un jour férié asymétrique (174 désaccords détectés et
   corrigés avant tout commit). Au #280 (vitesse des taux), un
   indexage `pos_full[1:]` au lieu de `pos_full[:-1]` reproduisait
   exactement le motif du bug même-barre déjà documenté ailleurs dans
   ce backlog — trouvé et corrigé avant tout commit. **Cette famille de
   bugs de décalage causal reste la source d'erreur la plus récurrente
   de tout ce backlog**, malgré une discipline de relecture systématique.
2. **Un bug peut se cacher dans le script d'AUDIT lui-même, pas
   seulement dans le backtest** (#283, mises en chantier) : le
   recalcul indépendant utilisait `searchsorted(side="left")-1` (strict
   `<`) au lieu de `side="right")-1` (inclusif `<=`, la méthode déjà
   prouvée correcte au #203) — 39 à 433 faux désaccords selon le
   marché, tous résolus après correction de l'AUDIT (le backtest était
   déjà correct). Rappel que la vérification indépendante elle-même
   n'est pas à l'abri d'erreurs et doit être scrutée avec la même
   rigueur que le code testé.
3. **Une anomalie de taux de coupure élevé n'est pas automatiquement un
   bug** : le taux de coupure anormalement élevé sur Composite observé
   à deux reprises (#286 : 70% ; #289 : 60,9%) s'explique intégralement
   par l'effet de fenêtre courte du tercile expanding calculé
   indépendamment par marché (Composite ne couvre que 2021-2026,
   période de hausse réelle et documentée des défauts de paiement
   post-COVID) — confirmé chaque fois par un recalcul indépendant
   identique, jamais un défaut de calcul.

## Bilan chiffré de la période #276-289

| Catégorie | Cycles | PASS | FAIL | Score Règle 9 |
|---|---|---|---|---|
| Doublons corrigés | #276 (x2) | — | — (déjà FAIL ailleurs) | — |
| Calendaire | #276, #277 | 0 | 2 | — |
| Régime nouveau (drawdown, taux) | #279, #280 | 0 | 2 | — |
| Matière première/sectoriel | #281, #282, #283 | 0 | 3 | — |
| Stress d'endettement ménages | #284, #286, #287 | 1 (#284) | 2 | 3/5 (#284/#285) |

**+1 PASS niveau 1 net sur cette période** (90 au lieu de 89 au début
du #276), le score Règle 9 le plus élevé de cette session mais toujours
sous les Candidats A/B existants — aucun changement au guide de
déploiement. Recherche de nouvelles idées de plus en plus difficile
(deux cycles consécutifs, #287 et ce cycle, n'ont trouvé respectivement
qu'une seule idée ou aucune idée backtestable fraîche) — signe que les
catégories de données librement accessibles et économiquement motivées
de ce backlog approchent d'un point de saturation, cohérent avec le
constat déjà posé au #257.
