# Synthèse consolidée v14 — cycles #363-367 (backlog #363-368)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v13 (#362), qui clôturait l'arc
#356-361 (volatilité implicite inter-classes, positionnement CFTC).
L'arc #363-367 documenté ici (5 cycles) est marqué par la maturation
complète de la famille des portes combinées macro-externes — désormais
close après 2 extensions supplémentaires réussies — et l'exploration
d'une nouvelle source de données (FINRA) qui a immédiatement révélé
un bug de format corrigé avant tout calcul de signal.

## 2. Bilan chiffré des 5 cycles (#363-367)

| Cycle | Sujet | Résultat |
|---|---|---|
| #363 | Panel élargi à 5 signaux (+MOVE), vote ≥4/5 | **PASS NET 5/5** — meilleur profil MDD de la famille, robustesse 15/15 |
| #364 | Batterie Règle 9 sur le #363 | 3/5 — égale le record de la famille (#304), stabilité parfaite 4/4 |
| #365 | Panel élargi à 6 signaux (+CPI), vote ≥5/6 | **PASS NET 5/5** — robustesse 15/15, dernière extension (bornage déclaré à l'avance) |
| #366 | Batterie Règle 9 sur le #365 | 3/5 — égale le record, meilleure p-value SPA de la famille (0,4046) |
| #367 | Ratio de volume vendu à découvert QQQ (FINRA Reg SHO) | FAIL NET 0/5 — nouvelle source/mécanisme, bug de format corrigé avant calcul |

**+2 PASS niveau 1 sur la période** (#363, #365 — numérateur incrémenté
deux fois). **1 famille supplémentaire formellement fermée** : portes
combinées macro-externes, désormais close à 7 constructions (0
nouvelle extension sans motivation utilisateur explicite).

## 3. Bilan complet de la famille des portes combinées (désormais close)

**Chronologie complète** (7 constructions, toutes des extensions d'un
même panel de signaux de stress économiquement distincts) :

| Construction | Signaux | Logique | Niveau 1 | Règle 9 |
|---|---|---|---|---|
| #296 | 2 (carte+NFCI) | ET | PASS NET 5/5 | 2/5 (#297) |
| #298 | 2 (carte+NFCI) | OU | FAIL 3/5 | — |
| #301 | 3 (+BAA10Y) | majorité 2/3 | PASS NET 5/5 | 2/5 |
| #303 | 3 (+BAA10Y) | graduée | PASS 4/5 | 2/5 (#305) |
| #304 | 4 (+corr NDX-DAX) | majorité 3/4 | PASS NET 5/5 | **3/5** (#306) |
| #363 | 5 (+MOVE) | majorité 4/5 | PASS NET 5/5, MDD partout | **3/5** (#364) |
| #365 | 6 (+CPI) | majorité 5/6 | PASS NET 5/5 | **3/5** (#366) |

**Constat central** : le score Règle 9 **plafonne mécaniquement à
3/5 depuis la 4e construction**, quel que soit le nombre de signaux
ajoutés (4, 5 ou 6) ou la sophistication du vote. Chaque extension a
amélioré des dimensions QUALITATIVES du profil (stabilité temporelle
4/4 parfaite dès le #363, p-value SPA passant de 1,0000 systématique à
0,4046 au #365) sans jamais franchir le plafond formé par SPA et DSR
simultanément. **Explication structurelle déjà établie par
l'investigation Piste A/C** : le Sharpe brut de ces panels plafonne
autour de 0,4-0,7 quelle que soit la diversification, très loin des
~1,7-2,0 requis pour franchir le DSR à `n_trials≈370` — ajouter des
signaux corrélés au stress de marché AMÉLIORE la robustesse
qualitative (moins de false positives, moins de whipsaw) mais
n'AUGMENTE PAS fondamentalement l'edge brut au point de changer
l'ordre de grandeur du Sharpe. **La famille est donc désormais
formellement close** (engagement pris au PREREG du #365, confirmé
empiriquement par le #366) : toute 8e extension de signal nécessiterait
une motivation utilisateur explicite, la valeur marginale attendue
étant désormais quasi nulle sur le plan Règle 9/DSR.

## 4. Bilan de la découverte FINRA Reg SHO (#367)

**Nouvelle source ET nouveau mécanisme confirmés fonctionnels**
(volume quotidien de vente à découvert, flux transactionnel distinct
du positionnement CFTC hebdomadaire sur futures déjà clos 0/2), mais
**FAIL NET sur QQQ** — hypothèse a priori déclarée fragile (interprétation
économique non tranchée dans la littérature, risque de bruit de
market-making sur un ETF très liquide), confirmée empiriquement. **Un
bug réel a été trouvé et corrigé AVANT tout calcul de signal** : le
script de récupération de données parsait les volumes en entier, ce
qui rejetait silencieusement ~6 mois de données après un changement de
format FINRA (volumes fractionnaires depuis le 23/02/2026) — corrigé
en parsant en flottant, avec vérification exhaustive que les 78 jours
ouvrés manquants restants correspondent tous à des jours fériés
connus. **La source reste réutilisable** pour un futur test sur des
titres individuels moins liquides/plus arbitrés (l'hypothèse
économique du signal — proportion de vente à découvert dans le volume
quotidien comme proxy de désaccord informationnel — est documentée
dans la littérature de microstructure sur des actions, pas
spécifiquement des ETF indiciels), mais nécessiterait une nouvelle
motivation économique distincte pour éviter une simple répétition.

## 5. État global du backlog après 367 hypothèses testées

Sous-méthodes/familles désormais formellement closes : VIX-dérivés
équité (0/4), inflation (2/4), crypto (1/2), monétaire (0/3), marché
du travail (0/5), immobilier (0/2), valeur-refuge/risque global
(0/7), ratio de force relative (0/2), volatilité implicite
inter-classes (1/2), positionnement CFTC (0/2), **portes combinées
macro-externes (7 constructions, plafond Règle 9 3/5)**. Une nouvelle
source (FINRA Reg SHO) est confirmée fonctionnelle mais non encore
concluante (0/1). **Le terrain de recherche mono-signal ET
multi-signaux via les sources déjà exploitées (FRED, Yahoo Finance,
CFTC, FINRA) apparaît désormais exhaustivement cartographié.**

## 6. Recommandation (mise à jour de la v13)

**Inchangée sur le fond** : les deux voies productives restantes sont
(1) une nouvelle catégorie de données apportée par l'utilisateur, ou
(2) un pivot explicite vers l'Étape D. **Candidats de pivot classés
par robustesse Règle 9** : le **panel à 6 signaux (#365, PASS NET 5/5,
Règle 9 3/5, meilleur profil qualitatif combiné — stabilité parfaite
4/4, meilleure p-value SPA de tout le backlog)** est désormais le
candidat le plus solide sur le plan de la robustesse structurelle,
devant CPI seul (#338, Règle 9 3/5) et MOVE seul (#357, Règle 9 2/5,
meilleure couverture de scénarios de crise individuelle) et Bitcoin
(#344, Règle 9 2/5). **Aucun candidat ne franchira jamais le DSR à ce
niveau de n_trials** (conclusion définitive de la Piste A/C, reconfirmée
une 3e fois par cette famille) — le critère de sélection pour un
pivot Étape D devrait donc s'appuyer sur le score Règle 9 partiel et
le profil qualitatif (stabilité, coûts, crise), pas sur l'attente d'un
PASS RENFORCÉ qui n'arrivera pas dans ce cadre.

Voir `NONML_STRATEGY_BACKLOG.md` entrées #363-#367 pour le détail
complet de chaque cycle.
