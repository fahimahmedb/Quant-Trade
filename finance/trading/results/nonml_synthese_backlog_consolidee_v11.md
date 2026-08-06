# Synthèse consolidée v11 — cycles #340-347 (backlog #343-350)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v10 (#341), qui couvrait les cycles
#320-341 et recommandait, pour toute future recherche mono-signal, de
privilégier l'heuristique "mesure officielle/source indépendante vs
proxy déjà testé", tout en réitérant la recommandation de fond de la
v9 : ne plus forcer de recherche d'idées à chaque firing vide. L'arc
#340-347 documenté ici (8 cycles) introduit une méthode nouvelle,
distincte de l'heuristique officielle-vs-proxy : le
**"test-puis-bornage-explicite"**, appliquée systématiquement à
chaque candidat proche d'un canal déjà partiellement exploré.

## 2. Bilan chiffré des 8 cycles (#340-347)

| Cycle | Sujet | Résultat |
|---|---|---|
| #340 | Structure par terme du VIX (VXV-VIX) | FAIL 1/5 — étend la famille VIX-dérivés à 0/3 |
| #341 | Indice CBOE SKEW (risque de queue) | FAIL NET 0/5 — pire score de la famille, étend à 0/4 |
| — | **Famille VIX-dérivés formellement close** (après recherche de VVIX/VXDCLS explicitement déclinée) | **0 PASS / 4 constructions** |
| #342 | Règle de Sahm en temps réel | FAIL 1/5 — confirme la prédiction déclarée à l'avance, étend le canal travail à 6/6 |
| #343 | Anticipation d'inflation long terme (T5YIFR) | FAIL 2/5 — clôt le canal inflation à 4 constructions |
| — | **Canal inflation formellement clos** | **2 PASS / 4 constructions** (breakeven #200, CPI #338) |
| #344 | **Momentum du Bitcoin** | **PASS NET 5/5** — 1re classe d'actif crypto, MDD amélioré partout |
| #345 | Batterie Règle 9 sur le #344 | 2/5 — crise et stabilité OK (4/4 folds), coûts/SPA/DSR échouent |
| #346 | Momentum de l'Ethereum | FAIL 2/5 — clôt la classe d'actif crypto à 2 constructions |
| — | **Classe d'actif crypto formellement close** | **1 PASS / 2 constructions** |
| #347 | Bilan de la Réserve fédérale (WALCL) | FAIL NET 0/5 — clôt le canal monétaire à 3 constructions |
| — | **Canal monétaire formellement clos** | **0 PASS / 3 constructions** |

**+1 PASS niveau 1 net enregistré dans le tracker sur la période**
(97→98), portant le total à 353 hypothèses testées. **4 canaux/familles
formellement bornés et clos durant cet arc** (VIX-dérivés, inflation,
crypto, monétaire), chacun accompagné d'une déclaration explicite de
tension et d'un engagement de bornage pris AVANT calcul.

## 3. Enseignements transversaux de la période #340-347

**a. La méthode "test-puis-bornage-explicite" s'est révélée à la fois
productive et disciplinée.** Contrairement à une politique
d'évitement pur (ne jamais retester un candidat proche d'un canal déjà
exploré) ou à une politique de recherche libre (risque de snooping non
borné), cette méthode — déclarer la tension de redondance, poser une
prédiction explicite, puis s'engager à clore le canal après le
résultat quel qu'il soit — a permis de tester 6 candidats
supplémentaires (Sahm, T5YIFR, Bitcoin, Ethereum, WALCL, plus SKEW en
amont) tout en respectant `PROTOCOLE_ANTI_SNOOPING.md`. Elle a produit
1 PASS net (Bitcoin) sur 6 essais bornés (16,7%), un taux comparable
à celui de la recherche mono-signal générale de ce backlog sur la
session entière — **la méthode n'a pas gonflé artificiellement le taux
de succès, elle a simplement permis d'explorer plus de terrain de
façon disciplinée plutôt que par évitement excessif.**

**b. Le Bitcoin (#344) est le PREMIER signal d'une classe d'actif
NON-macro-économique à réussir dans ce backlog.** Les 97 PASS niveau 1
précédents provenaient tous soit de signaux de marché actions
(momentum, volatilité, corrélation), soit de séries macro-économiques
publiées (FRED). Le Bitcoin, un actif spéculatif coté en continu, a
produit le 2e meilleur profil MDD de la session parmi les nouveaux
candidats (NDX -35,6%→-29,9%). **Enseignement transférable pour de
futures recherches** : les classes d'actifs négociées en continu
(matières premières exotiques, indices de sentiment dérivés d'actifs
cotés) méritent d'être considérées comme catégorie à part entière,
au même titre que les séries macro FRED — mais l'échec de sa
réplication immédiate sur l'Ethereum (#346, construction identique,
FAIL 2/5) démontre que **le succès du Bitcoin est probablement propre
à cet actif précis** (statut de "réserve de valeur" relative, plus
proche conceptuellement de l'or que des autres crypto-actifs plus
spéculatifs), pas à la classe d'actif crypto dans son ensemble — la
même leçon "construction identique ne garantit pas un résultat
identique" déjà observée 2 fois sur les paires PPI/breakeven et
T5YIFR/breakeven au sein du canal inflation.

**c. Quatre canaux supplémentaires portent désormais le score final
suivant** : VIX-dérivés (0/4 — niveau, VRP, structure par terme,
SKEW), inflation (2/4 — breakeven et CPI PASS, PPI et T5YIFR FAIL),
crypto (1/2 — Bitcoin PASS, Ethereum FAIL), monétaire (0/3 — M2
growth, M2V, WALCL). Combinés aux canaux déjà bornés lors des arcs
précédents (marché du travail 0/6, activité économique réelle 0/5,
matières premières 0/3, immobilier 0/2, corrélation cross-marché
1/3), **la quasi-totalité des catégories de signaux macro/marché
identifiables et librement disponibles a désormais fait l'objet d'au
moins une tentative bornée et documentée.**

**d. Aucun bug de calcul significatif cette période**, à l'exception
d'un artefact de bord `shift(1)` désormais routinier (#340, corrigé
dans le script d'audit avant tout commit, même classe que les bugs
déjà documentés aux #320/#321) — la méthodologie d'audit à 5 dates
consécutives, désormais appliquée systématiquement dès l'écriture
initiale de chaque script (et non plus découverte après un premier
échec), a évité toute récidive sur les cycles suivants (#341-347).

## 4. Réponse aux questions posées au PREREG

**Question 2 (méthode test-puis-bornage) : OUI, confirmée productive
et disciplinée.** Le taux de succès (1/6 candidats bornés) est
cohérent avec le reste du backlog, et chaque canal a été refermé
proprement avec une justification écrite avant résultat — aucun signe
de data-snooping non déclaré.

**Question 3 (enseignement du Bitcoin) : partiellement transférable.**
La leçon n'est PAS "tester systématiquement d'autres crypto-actifs"
(l'Ethereum a immédiatement échoué, et la classe est désormais
close) — c'est plutôt "les actifs négociés en continu hors du
périmètre macro-FRED classique constituent une catégorie de recherche
légitime, à explorer au cas par cas selon un narratif économique
propre à CHAQUE actif (pas par la classe d'actif dans son ensemble)".

## 5. Recommandation (mise à jour de la v10)

**La recommandation de fond des v9/v10 reste valide** : ne pas forcer
de recherche d'idées à chaque firing vide. **Mise à jour
méthodologique** : la méthode "test-puis-bornage-explicite" est
désormais un outil éprouvé et recommandé pour tout candidat futur
proche d'un canal partiellement exploré (par opposition à l'éviter
purement et simplement) — mais elle ne doit pas être confondue avec
une licence à tester systématiquement toute variante d'un canal déjà
PASS (elle a été appliquée ici précisément aux canaux encore ouverts
ou mixtes, pas pour ré-ouvrir des canaux déjà formellement clos comme
la corrélation cross-marché #196). **Avec 4 canaux supplémentaires
désormais bornés cette période** (VIX-dérivés, inflation, crypto,
monétaire), en plus de tous les canaux déjà clos aux synthèses
précédentes, **le terrain de recherche mono-signal apparaît désormais
proche de l'épuisement complet** pour les données librement
disponibles et économiquement motivées. Les deux voies productives
restantes sont, comme depuis la v9 : (1) une nouvelle catégorie de
données apportée par l'utilisateur, ou (2) un pivot explicite vers
l'Étape D — le CPI (#338, toujours PASS NET 5/5, Règle 9 3/5) reste le
meilleur candidat de pivot, désormais suivi de près par le Bitcoin
(#344, PASS NET 5/5, Règle 9 2/5, MDD amélioré sur les 5 marchés).

Voir `NONML_STRATEGY_BACKLOG.md` entrées #343-#350 pour le détail
complet de chaque cycle.
