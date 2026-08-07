# Synthèse consolidée v13 — cycles #356-361 (backlog #356-362)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v12 (#355), qui clôturait l'arc
#348-354 (découverte Yahoo Finance, investigation Piste A/C du DSR
conclue empiriquement à 0,04). L'arc #356-361 documenté ici (6 cycles)
est marqué par la découverte et l'exploitation complète de **deux
familles de mécanisme entièrement nouvelles** — la volatilité
implicite inter-classes d'actifs et le positionnement spéculatif CFTC
— ainsi que la clôture formelle de 3 sous-méthodes supplémentaires.

## 2. Bilan chiffré des 6 cycles (#356-361)

| Cycle | Sujet | Résultat |
|---|---|---|
| #356 | Momentum du fret maritime (BDRY, Yahoo Finance) | FAIL 2/5 — Sharpe bat BH sur 5/5 marchés (fait rare), rendement insuffisant |
| #357 | Volatilité implicite obligataire (MOVE, Yahoo Finance) | **PASS 4/5** — 1er PASS niveau 1 depuis le Bitcoin (#344) |
| #358 | Batterie Règle 9 sur le #357 (MOVE) | 2/5 — crise/stabilité OK (couverture la plus large de tout candidat), coûts/SPA/DSR ÉCHEC |
| #359 | Volatilité implicite pétrolière (OVX, Yahoo Finance) | FAIL NET 0/5 — le mécanisme MOVE ne généralise pas |
| #360 | Positionnement spéculatif CFTC, NASDAQ-100 (nouvelle source) | FAIL 2/5 — 1re catégorie de mécanisme "positionnement" testée |
| #361 | Positionnement spéculatif CFTC, or | FAIL NET 0/5 — pire que le #360, dérive structurelle 40 ans identifiée |

**+1 PASS niveau 1 sur la période** (#357, MOVE — numérateur
incrémenté, critère standard "bat Buy&Hold"). **3 sous-méthodes/
familles supplémentaires fermées** : volatilité implicite
inter-classes bornée à 2 constructions (1 PASS/2) ; positionnement
CFTC bornée à 2 constructions (0 PASS/2) ; famille "risque global
purement défensive" formellement déclarée close à 7 constructions
(0 PASS/7, incluant le BDRY de cette période).

## 3. Bilan de la découverte "volatilité implicite inter-classes d'actifs"

**Chaîne complète** : après la clôture formelle de la famille
VIX-dérivés EQUITY (0/4, #130/#191/#340/#341), le #357 a testé le même
mécanisme (tercile expanding sur niveau brut, Règle 7) sur une classe
d'actif sous-jacente différente — l'indice MOVE (volatilité implicite
d'options sur bons du Trésor). Résultat : **PASS 4/5**, Sharpe battant
Buy&Hold sur les 5 marchés SANS EXCEPTION, MDD amélioré partout — la
1re catégorie "volatilité implicite" à passer le seuil renforcé dans
ce backlog. Soumis à la Règle 9 au #358 : **2/5**, crise et stabilité
OK (la meilleure couverture de crise de tout candidat récent — dot-com,
2008, COVID, 2022, tous disponibles grâce à l'historique NDX/MOVE
depuis 2002), mais coûts/SPA/DSR en échec (DSR=0,0293 à n_trials=362),
conforme à la conclusion déjà établie par l'investigation Piste A/C :
aucun candidat de ce backlog n'a jamais franchi le DSR.

**Généralisation testée et réfutée** : le #359 a testé le même
mécanisme sur le pétrole (OVX) — **FAIL NET 0/5**. Le lien "volatilité
implicite = jauge de stress transmissible aux actions" fonctionne pour
les obligations (canal taux/politique monétaire, universellement
transmis) mais pas pour le pétrole (chocs d'offre plus
idiosyncratiques, moins systématiquement liés au risque actions) —
conforme à la prédiction déclarée à l'avance au PREREG du #359. Une 3e
construction (change, `^EVZ`) a été envisagée puis déclinée pour
raison de qualité de données (~1,5 an de valeurs manquantes) — la
sous-famille est donc close à 2 constructions (1 PASS/2).

## 4. Bilan de la découverte "positionnement spéculatif CFTC"

**Première utilisation d'une nouvelle source de données ET d'un
nouveau mécanisme dans ce backlog** : jusqu'au #359, tous les signaux
reposaient sur le prix, le rendement ou la volatilité implicite d'un
actif. Le #360 a introduit le POSITIONNEMENT du marché à terme
(rapports CFTC "Commitment of Traders"), avec construction d'un ETL
dédié (téléchargement et vérification manuelle de 17 puis 41 fichiers
ZIP annuels CFTC, extraction, validation d'absence de doublons/trous).
Direction contrariante documentée à l'avance (net-long extrême =
trade "crowded" = défensif). Résultat sur les futures NASDAQ-100 :
**FAIL 2/5** (Russell 2000/DAX passent net, Composite/NDX échouent les
deux jambes — notable, NDX échoue malgré que la donnée porte
spécifiquement sur ses propres futures).

**2e construction, or (COMEX)** : même mécanisme, même direction
(aucun balayage d'interprétation), historique 40 ans (1986-2026).
**FAIL NET 0/5**, pire que le #360. Constat post-hoc honnête (n'a pas
affecté le verdict pré-enregistré) : le positionnement spéculatif net
sur l'or affiche une dérive structurelle marquée sur 40 ans (~0-1% en
moyenne quinquennale 1986-1996 contre ~27-40% en 2006-2026,
probablement liée à la croissance de la gestion systématique/CTA),
ancrant le seuil de tercile expanding trop bas pour le régime moderne.

**3e construction envisagée puis déclinée** : taux (T-Note 10 ans,
discontinué en 2022, remplacé par un contrat non comparable) et
pétrole (WTI, contrat standard également discontinué en 2022, son
successeur n'existant que depuis 2019) ont tous deux été vérifiés et
écartés pour raison de disponibilité/fraîcheur de données. **La
sous-famille "positionnement CFTC" est donc close à 2 constructions
(0 PASS/2)**, mais l'infrastructure ETL reste réutilisable pour
d'autres contrats (S&P 500 e-mini, etc.) si une hypothèse
matériellement nouvelle émerge.

## 5. État du terrain de recherche mono-signal après cette période

Sous-méthodes/familles désormais formellement closes dans ce
backlog : VIX-dérivés équité (0/4), inflation (2/4), crypto (1/2),
monétaire (0/3), marché du travail (0/4), valeur-refuge/risque global
(0/7), ratio de force relative (0/2... 1 PASS partiel selon
comptage), volatilité implicite inter-classes (1/2), positionnement
CFTC (0/2). **Le terrain de recherche mono-signal librement
disponible via les sources déjà exploitées (FRED, Yahoo Finance,
CFTC) apparaît désormais très largement épuisé** — chaque nouvelle
catégorie de mécanisme testée depuis la v12 (volatilité inter-classes,
positionnement) a produit exactement 1 PASS niveau 1 sur 2-4
constructions avant clôture, cohérent avec le taux de succès observé
sur l'ensemble du backlog.

## 6. Recommandation (mise à jour de la v12)

**La recommandation de fond reste inchangée depuis les v9-v12** : ne
pas forcer de recherche d'idées à chaque firing vide, accepter
honnêtement quand rien de nouveau n'est trouvé (pratique déjà
appliquée 2 fois cette période, cf. clôtures des #359/#361). **Les
deux voies productives restantes sont inchangées** : (1) une nouvelle
catégorie de données apportée par l'utilisateur (le terrain
gratuit/facilement accessible étant désormais très largement
cartographié), ou (2) un pivot explicite vers l'Étape D. **Les
meilleurs candidats de pivot Étape D sont désormais** : CPI (#338,
PASS NET 5/5, Règle 9 3/5), Bitcoin (#344, PASS NET 5/5, Règle 9 2/5),
et **MOVE (#357, PASS 4/5, Règle 9 2/5)** — ce dernier nouvellement
qualifié cette période, avec la meilleure couverture de scénarios de
crise (dot-com/2008/COVID/2022) de tout candidat Règle 9 du backlog,
un atout distinct des deux autres candidats (historiques plus courts).

Voir `NONML_STRATEGY_BACKLOG.md` entrées #356-#361 pour le détail
complet de chaque cycle.
