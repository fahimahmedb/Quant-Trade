# Q21 — réponse adverse C7/C8 et pré-enregistrement B2 corrigé

Date : 2026-10-08. Statut : `PREREGISTERED_NEGATIVE_REPLICATION_ONLY`.

## 1. Décision C7

Voie choisie : **(c), réplication négative**. `SECTOR-XREV-001` n'est ni une nouvelle
famille, ni une découverte, ni une validation hors échantillon. La proposition Q21
antérieure qui le présentait avec une partition découverte/validation est retirée.

Le panel `us_sector_etf_daily` a déjà servi à 36 expressions déclarées de relatif
transversal sectoriel. Sa fenêtre 2022-03-09–2025-03-11 a déjà été dépensée par
`xs_execution_aware_relative_value`; elle ne peut plus être qualifiée de validation.
La fenêtre commençant le 2025-03-12 demeure réservée au desk et invisible à la
recherche. B2 ne doit ni la lire, ni en dériver une statistique, ni déplacer ses bornes.

Taille de famille à déclarer dans le résultat : `36 EXISTING + 0 DISCOVERY CLAIMS`.
Si le harnais évalue une expression nouvelle, il doit aussi afficher
`EXPRESSION_ORDINAL = 37` et le seuil Bonferroni recalculé, mais aucun résultat ne
pourra devenir une découverte ou une validation sur ce panel.

Probabilité a priori qu'une nouvelle expression de cette famille franchisse le seuil
conjonctif : **1 %**, donc inférieure à 5 %. Cette probabilité est un jugement de
priorisation, pas une fréquence estimée. Une famille hors relatif transversal sur
SPY/TLT/GLD aurait probablement plus de valeur d'information, mais elle exige un
pré-enregistrement séparé et une fenêtre honnêtement vierge. Elle n'est pas autorisée
par le présent texte.

## 2. Objet exact de B2

B2 est un contrôle de reproductibilité et de mémoire scientifique : vérifier qu'un
harnais indépendant, en lecture seule, retrouve le verdict négatif déjà consigné pour
la famille transversale sectorielle et ne transforme pas des fenêtres dépensées en
preuve neuve.

Hypothèse nulle opérationnelle : aucune expression transversale sectorielle évaluée
ici ne constitue une source d'edge net reproductible sur ce panel.

Résultat attendu, sans être imposé : réplication du rejet. Une divergence est
consignée comme `REPLICATION_DIVERGENCE` et déclenche un audit du calcul; elle ne vaut
pas découverte.

## 3. Donnée et bornes immuables

- dataset : `data/datasets/us_sector_etf_daily.csv`;
- métadonnées : `data/datasets/us_sector_etf_daily.meta.json`;
- empreinte requise avant et après lecture :
  `sha256:f108a6f41552afdb42100d3188d7194006de1aae6a27bd7722330818e6dcb6d1`;
- univers sectoriel : `XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY`;
- benchmark d'attribution seulement : `SPY`;
- fenêtre de reproduction découverte : 2016-09-12–2022-03-08;
- fenêtre de reproduction historique déjà dépensée : 2022-03-09–2025-03-11;
- fenêtre interdite à la recherche : toute date à partir du 2025-03-12.

Le harnais échoue fermé si l'empreinte, les symboles, les bornes ou les métadonnées
divergent. Il ne télécharge, ne complète et ne réécrit aucune donnée.

## 4. Expressions et chronologie

Le harnais ne cherche aucun paramètre. Il relit les grilles déjà déclarées dans
`src/quant/factory/lanes.py` : 24 expressions `xs_daily_relative_value`, puis 12
expressions `xs_execution_aware_relative_value`, soit 36 au total.

Chronologie causale obligatoire : information jusqu'à la clôture de `t`, décision
après cette clôture, entrée à l'ouverture de `t+1`, sortie à l'ouverture suivant la
durée de détention. Toute autre chronologie produit `INVALID_REPLICATION_TIMELINE`.

Les classements et paramètres sélectionnés par le code existant sont reproduits sans
ajout, retrait, substitution, optimisation ou décision humaine après lecture.

## 5. Mesures et critère pré-enregistré

Le résultat écrit, pour chaque lane et pour l'expression historiquement sélectionnée :
rendement brut et net, coûts modélisés, turnover annualisé, Sharpe, t-statistique,
bêta SPY, sous-périodes et concentration disponibles dans l'évaluateur existant.

Coût de référence : 5 points de base par changement d'exposition, plus le contrôle à
coût doublé déjà prévu. **Limite connue :** cette enveloppe ne modélise pas le coût
propre à la jambe courte; aucun résultat net ne doit être qualifié de réaliste sans
ce modèle. `adj_close` est retraité rétrospectivement et n'est pas strictement
point-in-time; cette limite doit figurer dans le résultat.

Critère de réplication : `NEGATIVE_REPLICATION_CONFIRMED` seulement si le harnais
retrouve, à la tolérance numérique déclarée avant exécution, (a) le filtrage de la
lane 1 avant validation et (b) le rejet hors échantillon de la lane 2, sans accéder à
la fenêtre shadow. Sinon : `REPLICATION_DIVERGENCE`. Aucun des deux statuts ne vaut
validation, stratégie tradable ou autorité de Book.

## 6. Contrat du harnais et sortie obligatoire

Avant toute observation, le Builder peut préparer uniquement un harnais générique qui :

1. vérifie l'empreinte avant lecture et après calcul;
2. interdit les dates à partir du 2025-03-12;
3. charge exclusivement les 36 expressions déclarées dans le code référencé;
4. journalise versions, commande, commit, paramètres, tolérance, sorties et code retour;
5. écrit un résultat même négatif ou divergent;
6. n'écrit jamais dans le panel ni dans les états du desk ou du Book.

Le livrable B2 se termine obligatoirement par :

```text
RESULT: NEGATIVE_REPLICATION_CONFIRMED | REPLICATION_DIVERGENCE | INVALID_INPUT
LESSON: <ce que la reproduction établit, sans revendication de découverte>
PRIORITY_UPDATE: abandonner ou auditer la famille; ne pas recycler la validation
NEXT_ACTION: choisir une famille hors relatif transversal avec fenêtre vierge, ou améliorer le modèle de coûts avant toute nouvelle prétention économique
DISCOVERY_CLAIM = FALSE
VALIDATION_CLAIM = FALSE
SHADOW_READ = FALSE
TRADABLE_STRATEGY = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 7. Autorité et ordre

Ce texte ne lance pas B2. B2 peut commencer seulement après publication horodatée de
ces octets et vérification de leur SHA-256. Il autorise une réplication historique en
lecture seule, pas une recherche, pas une observation shadow, pas une écriture Book et
pas une décision de capital.

`NEXT_ACTION`: Builder — préparer puis exécuter une seule fois le harnais générique
conforme à ce texte; critère de fin : résultat persistant avec empreintes pré/post et
statut obligatoire.

`CHALLENGE`: vérifier avant exécution que le harnais importe exactement les 36
expressions existantes et qu'aucun accès postérieur au 2025-03-11 n'est possible.

`WAKE_EVENT`: publication horodatée de ce pré-enregistrement et de son SHA-256.
