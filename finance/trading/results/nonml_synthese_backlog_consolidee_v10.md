# Synthèse consolidée v10 — cycles #320-341 (backlog #322-341)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v9 (#311), qui avait déjà conclu à une
saturation du backlog et recommandé de ne plus forcer de recherche
d'idées à chaque firing vide. L'arc #320-341 documenté ici est la
PREUVE la plus longue et la plus productive de ce backlog depuis cette
recommandation : 20 nouvelles lignes de backlog (#322-341), presque
entièrement consacrées à la famille macro-externe défensive (séries
FRED), avec deux méthodologies de recherche d'idées distinctes
(mono-signal classique, puis pivot vers la combinaison de signaux déjà
testés) et deux réouvertures de canal explicitement justifiées
(inflation, activité économique réelle). L'arc se termine par **5
firings consécutifs sans nouvelle idée trouvée**, malgré une recherche
systématique à chaque tentative — signal de saturation au moins aussi
fort que celui ayant motivé la v9, justifiant ce nouveau bilan avant
de statuer sur la suite.

## 2. Bilan chiffré des 20 cycles (#320-341)

| Sous-thème | Lignes backlog | Résultat |
|---|---|---|
| Mono-signal macro-externe (nouvelles catégories de données) | #322-333, #337, #341 (14 constructions) | 0 PASS niveau 1 net — toutes FAIL, seuil renforcé jamais atteint |
| Réouverture inflation (CPI/PPI, distincte du breakeven #200 déjà PASS) | #338-339 | **1 PASS net (CPI, #338, 5/5, le meilleur profil brut de toute la session)**, 1 FAIL (PPI, #339, 2/5) |
| Réouverture activité économique réelle (PIB réel, distinct des 4 proxys déjà FAIL) | #341 | 0 PASS — FAIL 1/5, n'a pas reproduit le succès de la réouverture inflation |
| Combinaison de 3 signaux macro (breakeven + CCSA + balance commerciale) | #334-336 | **1 PASS net (logique ET, #335, 4/5)**, 1 FAIL de justesse (majorité, #334, 3/5) |
| Batteries Règle 9 sur les 2 nouveaux PASS | #336, #340 | #335 (combo ET) → 2/5 ; #338 (CPI) → **3/5, égale le meilleur score Règle 9 de toute la famille macro-externe**, avec une couverture de crise complète inédite (4/4 fenêtres y compris dot-com) |
| Recherches d'idées infructueuses en fin d'arc | 5 firings consécutifs | Candidats envisagés et écartés après examen (FEDFUNDS, INDPRO, indice d'incertitude mondiale, gap overnight — catégorie déjà close) ; 1 candidat introuvable (TPUINDEX, 404) |

**+2 PASS niveau 1 nets enregistrés dans le tracker sur la période**
(95→97), portant le total à 345 hypothèses testées.

## 3. Enseignements transversaux de la période #320-341

**a. La recommandation de la v9 a été suivie avec nuance, pas
littéralement.** La v9 recommandait de ne pas forcer de recherche
d'idées à chaque firing vide. Dans les faits, cet arc a activement
cherché et testé 20 nouvelles constructions — mais chaque recherche
est restée bornée par une vérification de non-redondance systématique
(grep + fetch de test), et **à plusieurs reprises la recherche a
honnêtement conclu "rien trouvé" sans forcer d'idée marginale**
(notamment les 5 firings consécutifs qui clôturent cet arc). Le bilan
montre que cette application nuancée — chercher activement mais
refuser de forcer — a été nettement plus productive que l'abstention
totale : 2 PASS niveau 1 nets ont été trouvés APRÈS la déclaration de
saturation de la v9, ce qui aurait été manqué par une lecture littérale
de sa recommandation.

**b. Le motif "mesure officielle/source indépendante vs proxy" a
fonctionné de façon spectaculaire pour l'inflation, mais PAS pour
l'activité économique réelle.** La découverte que le CPI (inflation
RÉALISÉE, mesure BLS) n'avait jamais été testée malgré le breakeven
(inflation ANTICIPÉE, #200) déjà validé a directement produit le
meilleur résultat brut de toute la session (#338, PASS NET 5/5,
plateau de robustesse parfait 15/15). Le même raisonnement appliqué au
PIB réel (mesure officielle comprehensive vs les 4 proxys partiels
déjà FAIL du canal activité réelle) a semblé également prometteur au
PREREG — mais a produit un FAIL net (#341, 1/5), étendant ce canal à
0/5. **Enseignement honnête : cette heuristique de recherche n'est pas
généralisable automatiquement** — elle a fonctionné une fois sur deux
essais cette période, ce qui reste informatif (mieux que le taux de
succès général des idées mono-signal de cet arc, 1/16) mais ne
justifie pas de la traiter comme une règle fiable pour de futures
réouvertures de canal.

**c. Le pivot méthodologique vers la COMBINAISON a été le 2e axe
productif de la période**, après l'épuisement apparent du filon
mono-signal (déclaré au #331). Contrairement au sous-thread
combinaison original (#296-305, qui combinait NFCI/BAA10Y/défaut carte
de crédit), ce nouveau trio (breakeven inflation, demandes continues
de chômage, balance commerciale) a été choisi spécifiquement parce que
2 de ses 3 composantes présentaient un profil "Sharpe individuellement
fort mais rendement pénalisé par le bruit" — une heuristique de
sélection de signaux à combiner qui s'est révélée efficace : la
logique ET (la plus conservatrice, réduisant le taux d'activation à
6-11%) a transformé un FAIL de justesse (majorité, 3/5) en PASS net
(4/5). **Cette heuristique — repérer des signaux au profil
Sharpe-fort/rendement-faible et tester leur combinaison conservatrice
— constitue un candidat sérieux de méthode reproductible** pour de
futurs cycles, si de nouveaux signaux macro-externes présentant ce
profil venaient à être découverts.

**d. Cinq canaux/catégories sont désormais fermés à 0 PASS niveau 1
net**, tous confirmés ou étendus durant cette période : marché du
travail (0/5, ICSA/CCSA/PAYEMS/AWHMAN/JOLTS), activité économique
réelle (0/5, CFNAI/ICSA/UMCSENT/RSXFS/GDPC1), monétaire (0/2, M2
growth/M2V), matières premières (0/3, pétrole/cuivre/gaz naturel), et
désormais fiscal (0/1, déficit fédéral — un seul essai à ce stade, pas
encore formellement "clos" par plusieurs constructions). Seul le canal
inflation reste net positif (2 PASS sur 3 constructions : breakeven
#200, CPI #338 ; PPI #339 FAIL).

**e. Aucun bug de calcul significatif cette période** (contrairement à
la v9 qui en documentait deux) — plusieurs artefacts de tendance/
fenêtre courte ont été rencontrés et vérifiés explicitement par audit
dédié à chaque fois (taux de coupure élevé expliqué par ancrage sur un
pic historique ou tendance séculaire réelle : #326 PAYEMS post-COVID,
#329 balance commerciale, #331 TCU, #333 déficit fédéral, #328 taux
d'épargne/pic COVID) — tous confirmés comme des effets de données
réels, pas des bugs, avec une méthodologie de vérification de plus en
plus systématique (recherche de la transition de valeur réelle la plus
récente pour les tests de décalage causal, évitant le piège de
transition aveugle découvert au #320 lui-même en tout début d'arc).

## 4. Réponse à la question posée au PREREG : la saturation de la v9 est-elle confirmée ou infirmée ?

**Les deux, selon l'angle.** Infirmée dans l'absolu : 2 PASS niveau 1
nets ont été trouvés après la déclaration de saturation de la v9,
prouvant que le filon n'était pas complètement épuisé. Confirmée dans
sa substance : ces 2 PASS sont venus de deux sources bien identifiées
et désormais elles-mêmes épuisées — (1) une lacune de couverture
véritablement surprenante (CPI/PIB jamais testés malgré ~30
constructions macro-externes), maintenant comblée sur les candidats
évidents restants (CPI fait, PPI fait, PIB fait) ; (2) un pivot
méthodologique (combinaison) qui a produit exactement 1 PASS sur 1
trio testé et a été explicitement clos après ce succès pour éviter une
recherche combinatoire non bornée. **Les 5 firings consécutifs sans
idée en fin d'arc confirment qu'aucune des deux sources n'a plus de
potentiel immédiat identifiable.**

## 5. Recommandation (mise à jour de la v9)

**La recommandation de la v9 reste valide et est renforcée par cet
arc** : les deux seules voies productives restantes sont (1) une
nouvelle catégorie de données apportée par l'utilisateur, ou (2) un
pivot vers l'Étape D. **Mise à jour méthodologique pour tout futur
cycle de recherche mono-signal** : privilégier systématiquement la
question "cette série est-elle la mesure OFFICIELLE/SOURCE INDÉPENDANTE
d'un concept déjà testé uniquement via un PROXY ?" avant toute
recherche large — c'est la seule heuristique de cette période à avoir
produit un PASS net (CPI), même si elle n'est pas garantie (échec sur
le PIB). Le meilleur candidat de synthèse pour un pivot Étape D reste
le CPI (#338, PASS NET 5/5, plateau 15/15, meilleur score Règle 9 de
la famille macro-externe à 3/5 avec couverture de crise complète) —
un candidat sensiblement plus solide que le panel #304 identifié à la
v9, si un tel pivot est instruit.

Voir `NONML_STRATEGY_BACKLOG.md` entrées #322-#341 pour le détail
complet de chaque cycle.
