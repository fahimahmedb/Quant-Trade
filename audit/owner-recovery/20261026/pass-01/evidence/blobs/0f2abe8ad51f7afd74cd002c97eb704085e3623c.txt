# B4 — pré-enregistrement `MACRO-TSMOM-001`

Date : 2026-10-08. Statut : `PREREGISTERED_NOT_EXECUTED`.

## 1. Question et a priori

Cette expérience demande si un momentum temporel simple, appliqué séparément à
`SPY`, `TLT` et `GLD`, produit sur le panel local un rendement net qui ne soit pas
expliqué par une exposition longue permanente. Elle est distincte des 36 expressions
de relatif transversal sectoriel déjà consignées, mais utilise le même jeu de données.

Probabilité a priori qu'au moins une des quatre expressions satisfasse tous les
critères ci-dessous : **4 %**. Cette valeur est volontairement faible : la fenêtre
contient notamment le choc obligataire de 2022, connu avant ce pré-enregistrement,
et la validation du dataset a déjà été observée par une autre famille. Un résultat
positif restera exploratoire et ne constituera ni validation indépendante, ni edge
weather, ni stratégie tradable.

## 2. Donnée, compteur et arrêt fail-closed

- dataset : `data/datasets/us_sector_etf_daily.csv` ;
- métadonnées : `data/datasets/us_sector_etf_daily.meta.json` ;
- empreinte requise avant et après calcul :
  `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1` ;
- instruments, dans cet ordre canonique : `SPY`, `TLT`, `GLD` ;
- découverte : 2016-09-12–2022-03-08 ;
- évaluation historique déjà dépensée : 2022-03-09–2025-03-11 ;
- toute date à compter du 2025-03-12 : interdite à la recherche.

Le harnais lit en lecture seule et filtre le CSV avant de matérialiser les barres :
aucune barre datée du 2025-03-12 ou après ne peut atteindre les calculs. Le hachage
de l'enveloppe brute peut lire tous les octets uniquement pour vérifier l'identité ;
il ne doit interpréter aucune barre interdite.

Le registre vivant doit être lu en lecture seule avant l'essai. La précondition est
exactement `PRIOR_DECLARED_EXPRESSIONS_ON_DATASET = 36`. Toute valeur différente,
registre absent ou ambiguïté produit `INVALID_TRIAL_COUNT` et interdit le calcul.
Après ajout des quatre expressions ci-dessous :

```text
DATASET_LEVEL_TRIAL_COUNT = 40
BONFERRONI_TWO_SIDED_T_THRESHOLD = 3.227
```

Le seuil est celui pré-enregistré pour cette réplication. Aucun arrondissement ou
recalcul postérieur à l'observation ne peut l'abaisser.

## 3. Quatre expressions fermées

Les quatre expressions ne diffèrent que par `L ∈ {21, 63, 126, 252}` séances.
Pour chaque instrument `i` et chaque clôture `t`, le rendement de signal est :

`r_i(t,L) = adj_close_i(t) / adj_close_i(t-L) - 1`.

Le signal vaut `+1` si `r_i(t,L) > 0`, `-1` si `r_i(t,L) < 0`, et `0` si le
rendement est exactement nul ou indisponible. Il n'existe aucun autre seuil, buffer,
hystérésis, filtre de volatilité, stop, take-profit ou réglage par instrument.

Chaque jour de séance, après la clôture de `t`, les trois signaux déterminent les
positions exécutées à l'ouverture de `t+1`, conservées jusqu'à l'ouverture suivante.
Le portefeuille alloue **un tiers du notionnel absolu à chacun des trois
instruments**, sans normalisation de volatilité : poids `signal / 3`. Le cash non
engagé par un signal nul rapporte zéro. Le levier brut maximal est 1 ; aucun
rééquilibrage intrajournalier n'est permis.

Une inversion `+1 ↔ -1` implique un turnover de 2/3 pour l'instrument concerné ;
une entrée ou sortie via zéro implique 1/3. Les coûts sont donc appliqués à la
variation absolue complète des poids, y compris les inversions de signe.

## 4. Traitement du démarrage et chronologie commune

Toutes les expressions sont évaluées sur les mêmes fenêtres calendaires gelées.
Toutefois, une expression ne produit aucun rendement avant de disposer de `L+1`
clôtures antérieures causalement disponibles. Les jours sans signal pendant ce
démarrage restent explicitement cash et ne sont pas supprimés de la fenêtre.

Les métriques de comparaison sont calculées sur l'intersection commune où les quatre
expressions sont toutes éligibles, c'est-à-dire à partir du premier signal causal de
`L = 252`; les métriques propres à chaque expression sont aussi publiées sur sa
période éligible et étiquetées comme telles. La sélection utilise uniquement les
métriques de découverte sur l'intersection commune. Ainsi, aucune expression courte
ne reçoit davantage d'observations pour gagner la sélection.

Chronologie : information disponible après la clôture de `t`, décision ensuite,
entrée à l'ouverture de `t+1`, sortie/rééquilibrage à l'ouverture de `t+2`. Les
rendements d'exécution utilisent les ouvertures non ajustées. `adj_close` sert
uniquement au signal : celui de TLT incorpore rétrospectivement distributions et
splits, contrairement à GLD sur la période observée. Cette asymétrie et le caractère
non strictement point-in-time de `adj_close` sont des limites obligatoires du résultat.

## 5. Coûts et comparateurs

Cas central : 5 points de base par unité de turnover à chaque ouverture, plus
100 points de base annualisés sur la valeur absolue de toute position courte dans
`TLT` ou `GLD`. Aucun borrow n'est ajouté à `SPY`. Stress conjoint : 10 points de
base de transaction et 300 points de base annualisés de borrow TLT/GLD. Le borrow
est débité quotidiennement selon `taux / 252` sur le poids court absolu.

Comparateurs obligatoires, sans sélection entre eux : cash ; buy-and-hold équipondéré
SPY/TLT/GLD ; portefeuille équipondéré `+1/3` permanent ; et exposition signée moyenne
du candidat. Les rendements SPY, bêtas SPY, contribution par instrument, années et
sous-périodes sont publiés pour distinguer timing, beta et concentration.

## 6. Sélection et critères conjonctifs

La seule expression candidate est celle qui maximise le Sharpe **net central de
découverte sur l'intersection commune**. Les égalités à `1e-12` sont départagées par
le plus petit `L`. Les trois autres restent des essais comptés ; aucune combinaison,
moyenne ou cinquième variante n'est permise.

Le candidat ne reçoit le statut `PROVISIONAL_POSITIVE_ON_SPENT_DATA` que si les sept
conditions suivantes sont toutes vraies sur l'évaluation historique dépensée :

1. rendement net central strictement positif ;
2. Sharpe net central strictement positif ;
3. statistique t du rendement net `>= 3.227` ;
4. rendement net positif dans chacune des deux moitiés chronologiques ;
5. rendement net positif sous le stress 10/300 points de base ;
6. aucune année civile ne fournit plus de 60 % du P&L net positif total ;
7. au moins deux des trois instruments contribuent positivement au P&L net.

Tout autre résultat est `FAMILY_REJECTED`. Un résultat positif ne change pas le fait
que 2022-03-09–2025-03-11 est déjà dépensée au niveau du dataset ; il exige une
nouvelle donnée point-in-time et une validation réellement vierge avant promotion.

## 7. Reproductibilité, résultat négatif et autorité

Deux exécutions internes du même harnais doivent produire les mêmes décisions
discrètes exactement et les mêmes nombres à une erreur relative `<= 1e-9`. Le
harnais publie paramètres, versions, commande, commit, empreintes pré/post, dates
effectivement analysées, turnover, coûts, borrow, métriques, attribution, tests
échoués et code retour. Il écrit un seul résultat persistant et ne modifie ni donnée,
registre, desk, Book, ni état de recherche.

Si le résultat est négatif, la famille est abandonnée sans cinquième lookback,
nouveau seuil, nouvel instrument ou recyclage de la fenêtre. La leçon doit séparer
absence d'edge, coût, beta et concentration ; la prochaine priorité devient soit une
famille causalement différente sur données vierges, soit l'acquisition autorisée de
données point-in-time. Une divergence de reproduction déclenche un audit du harnais,
pas une revendication d'edge.

```text
RESULT: PROVISIONAL_POSITIVE_ON_SPENT_DATA | FAMILY_REJECTED | INVALID_INPUT | REPRODUCTION_DIVERGENCE
LESSON: <constat borné>
PRIORITY_UPDATE: <abandon, audit ou besoin de données vierges>
NEXT_ACTION: <action falsifiable suivante>
DISCOVERY_CLAIM = FALSE
INDEPENDENT_VALIDATION_CLAIM = FALSE
SHADOW_BAR_ANALYSED = FALSE
TRADABLE_STRATEGY = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

Ce texte ne lance pas B4 et n'autorise aucune donnée externe, aucun `t0`, aucune
lecture de barre shadow, aucune écriture Book et aucune décision de capital.

`NEXT_ACTION`: Builder — vérifier le SHA-256 publié, construire un harnais non
exécuté et ses tests adverses, puis le soumettre à contre-lecture avant l'unique essai.

`CHALLENGE`: vérifier le compteur vivant égal à 36, la causalité ouverture-à-ouverture,
le démarrage commun, les inversions de signe, le borrow court et l'absence de degré
de liberté après observation.

`WAKE_EVENT`: publication du harnais non exécuté et de son identité exacte.
