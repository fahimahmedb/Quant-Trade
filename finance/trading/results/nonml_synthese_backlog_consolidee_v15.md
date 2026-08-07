# Synthèse consolidée v15 — cycles #369-370 (backlog #369-371)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v14 (#368), qui clôturait l'arc
#363-367 (maturation complète de la famille des portes combinées,
découverte FINRA Reg SHO). L'arc #369-370 documenté ici est court (2
cycles) mais clôt une question méthodologique importante ouverte
depuis plusieurs synthèses : la méga-famille "positionnement/flux des
participants de marché", explorée sur 3 sources indépendantes au fil
de plusieurs cycles récents, est désormais formellement bornée.

## 2. Bilan chiffré des 2 cycles (#369-370)

| Cycle | Sujet | Résultat |
|---|---|---|
| #369 | Pression de vente des initiés (SEC Form 4, AAPL/MSFT/NVDA) | FAIL NET 0/5 — 2 bugs réels corrigés avant tout calcul |
| #370 | Clôture formelle de la méga-famille "positionnement/flux" | 0 PASS sur 4 constructions (CFTC×2, FINRA×1, SEC×1) |

**0 PASS niveau 1 sur la période.** Le cycle #369 a nécessité un
travail d'ingénierie de données substantiel (1879 dépôts SEC
individuels récupérés et parsés) réparti sur 2 firings (recherche de
faisabilité puis construction complète), avec deux erreurs réelles
identifiées et corrigées avant tout calcul de signal — illustrant que
la discipline anti-snooping de ce backlog (PREREG avant calcul,
correction des bugs de données avant tout résultat) s'applique aussi
bien à un cycle "lourd" en ingénierie qu'à un simple fetch FRED.

## 3. Bilan complet et définitif de la méga-famille "positionnement/flux"

**Chronologie complète** (4 constructions, 3 sources indépendantes,
tous FAIL) :

| Cycle | Source | Actif | Mécanisme | Résultat |
|---|---|---|---|---|
| #360 | CFTC (futures) | NASDAQ-100 | positionnement spéculatif net, hebdomadaire | FAIL 2/5 |
| #361 | CFTC (futures) | Or (COMEX) | positionnement spéculatif net, hebdomadaire | FAIL NET 0/5 |
| #367 | FINRA (actions/ETF comptant) | QQQ | ratio de volume vendu à découvert, quotidien | FAIL NET 0/5 |
| #369 | SEC (transactions d'initiés) | AAPL/MSFT/NVDA | pression de vente nette, quotidien agrégé | FAIL NET 0/5 |

**Enseignement transversal** : contrairement aux signaux de PRIX/
RENDEMENT (momentum, spread de taux) et de VOLATILITÉ IMPLICITE
(options), qui ont produit plusieurs PASS niveau 1 dans ce backlog
(CPI, MOVE, Bitcoin, panels combinés), **aucune des 3 grandes
catégories de données de POSITIONNEMENT/FLUX librement disponibles
n'a produit de signal exploitable**, malgré des mécanismes
économiquement distincts (spéculation sur futures, vente à découvert
au comptant, transactions d'initiés) et chacun documenté
individuellement dans la littérature académique (Wang 2001-2003 pour
le COT ; Diether/Lee/Werner 2009 et Boehmer/Jones/Zhang 2008 pour le
volume court ; Seyhun 1986 et Lakonishok & Lee 2001 pour les initiés).
**Hypothèse structurelle plausible** (non testée formellement, offerte
à titre de lecture) : ces signaux de positionnement/flux sont conçus
et étudiés dans la littérature académique pour PRÉDIRE LE RENDEMENT
D'UN TITRE OU D'UN CONTRAT SPÉCIFIQUE (l'actif sur lequel porte la
position), pas nécessairement pour servir de JAUGE DE STRESS
SYSTÉMIQUE généralisable à 5 indices actions distincts — la
transposition "signal spécifique à un actif → jauge de risque de
marché large" (déjà appliquée avec succès pour des signaux de PRIX/
VOLATILITÉ comme MOVE) ne semble PAS se généraliser aussi bien pour
des signaux de POSITIONNEMENT.

## 4. État global du backlog après 372 hypothèses testées

**4 firings consécutifs sans nouvelle piste trouvée** avant ce cycle
de synthèse — recherche répétée ayant systématiquement confirmé que
les catégories envisagées (crédit à la consommation, WEI, NFIB, PMI
global, macro allemand/zone euro, sous-composante inflation, ventes de
logements) sont soit déjà closes formellement, soit indisponibles
gratuitement en historique long. **Ce constat, répété de manière
indépendante sur 4 cycles distincts avec des recherches non
identiques, constitue une preuve convergente robuste** (pas une
paresse méthodologique) que le terrain de recherche non-ML librement
disponible via les sources déjà exploitées (FRED, Yahoo Finance, CFTC,
FINRA, SEC EDGAR) est désormais exhaustivement cartographié pour ce
backlog.

## 5. Recommandation (mise à jour de la v14)

**Inchangée sur le fond, renforcée par la convergence de 4 recherches
indépendantes** : les deux voies productives restantes sont (1) une
nouvelle catégorie de données apportée par l'utilisateur, ou (2) un
pivot explicite vers l'Étape D. **Recommandation pratique pour la
boucle autonome** : continuer à vérifier le backlog à chaque firing
(au cas où une instruction utilisateur ou une nouvelle idée
apparaisse), mais **ne plus forcer de recherche exploratoire complète
à chaque cycle vide** — une vérification légère suffit, conformément à
la discipline déjà établie d'éviter les commits répétitifs sans valeur
ajoutée. Les meilleurs candidats de pivot Étape D restent inchangés :
panel à 6 signaux (#365, Règle 9 3/5, meilleur profil qualitatif),
CPI (#338, Règle 9 3/5), MOVE (#357, Règle 9 2/5, meilleure couverture
de crise individuelle) et Bitcoin (#344, Règle 9 2/5).

Voir `NONML_STRATEGY_BACKLOG.md` entrées #369-#370 pour le détail
complet de chaque cycle.
