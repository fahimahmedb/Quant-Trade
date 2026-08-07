# Synthèse consolidée v12 — cycles #348-354 (backlog #352-358)

Synthèse pure — aucun nouveau calcul, relecture des résultats déjà
committés.

## 1. Contexte

Cette synthèse fait suite à la v11 (#347), qui clôturait un arc de 8
cycles caractérisé par la méthode "test-puis-bornage-explicite" (VIX-
dérivés, inflation, crypto, monétaire). L'arc #348-354 documenté ici
(7 cycles) est plus court mais méthodologiquement dense : il combine
(a) une réponse directe et explicite à une demande de l'utilisateur —
« recommençons depuis le début » sur la méthode DSR, ayant mené à
l'investigation complète de la Piste A/C de
`RECHERCHE_dsr_par_construction.md` — et (b) la découverte fortuite
d'une nouvelle source de données gratuite (Yahoo Finance), qui a
permis de tester enfin l'or (bloqué depuis le #134) et trois autres
candidats jusqu'ici inaccessibles.

## 2. Bilan chiffré des 7 cycles (#348-354)

| Cycle | Sujet | Résultat |
|---|---|---|
| #348 | Momentum de l'or (GLD, Yahoo Finance) | FAIL 3/5 — 2e meilleur score de la famille matières premières |
| #349 | Portefeuille L/S dollar-neutre composite (Piste A) | FAIL — Sharpe +0,45 positif net, t-stat 1,52 < 2 |
| #350 | Sleeve dollar-neutre redimensionné par sa vol (Piste C) | **PASS niveau 1** — Sharpe +0,61, t-stat +2,08 |
| #351 | Batterie Règle 9 sur le #350 | **1/5** — DSR=0,0406, très loin du seuil 0,95 |
| #352 | Momentum de l'ETF obligataire TLT | FAIL NET 0/5 — pire score que l'or, MDD dégradé (régime 2022) |
| #353 | Rotation sectorielle défensive (XLP/XLK) | FAIL 2/5 — meilleur profil MDD des candidats Yahoo Finance |
| #354 | Force relative EM/DM (EEM/SPY) | FAIL NET 0/5 |

**+1 PASS niveau 1 (critère propre, dollar-neutre) enregistré sur la
période** (#350 — non comptabilisé au numérateur principal du
backlog, catégoriellement distinct des PASS "bat Buy&Hold" habituels,
décision documentée et laissée à la clarification de l'utilisateur).
**2 sous-méthodes/familles supplémentaires fermées** : valeur-refuge/
matières premières étendue à 0 PASS sur 7 constructions (pétrole,
cuivre, gaz, or, obligataire — plus rotation sectorielle et EM/DM du
même esprit "risque global défensif") ; sous-méthode "ratio de force
relative entre deux actifs" bornée à 2 constructions (#353, #354).

## 3. Bilan complet de l'investigation Piste A/C (question centrale posée par l'utilisateur)

**Chaîne complète, cycle par cycle** :
1. **Constat de départ** : sur l'ensemble du backlog, AUCUN candidat
   n'avait jamais passé le contrôle DSR de la Règle 9 (confirmé par
   requête directe : 0 occurrence de "DSR OK" sur des dizaines de
   batteries exécutées).
2. **Diagnostic déjà écrit** (`RECHERCHE_dsr_par_construction.md`,
   commandé par l'utilisateur le 01/08/2026, relu au #349) : le
   problème n'est PAS le calibrage du DSR (vérifié empiriquement au
   #133 — réduire `n_trials` de 125 à 8 par regroupement en familles
   ne suffit toujours pas, DSR=0,51) mais l'AMPLEUR structurellement
   faible des stratégies de timing mono-actif (loi de Grinold :
   `IR≈IC×√ampleur`, ~12 paris indépendants/an pour un timing d'indice
   mensuel).
3. **Piste A testée** (#349) : portefeuille cross-sectionnel L/S
   dollar-neutre, composite de 4 signaux déjà validés (#4/#73/#82/#15),
   univers point-in-time réel (~100+ titres simultanés). Résultat :
   Sharpe +0,45 positif net et supérieur à la référence, MDD nettement
   amélioré (-28,2% vs -36,4%), mais **t-stat 1,52 < 2 requis** — FAIL
   de justesse. **2 bugs trouvés et corrigés avant tout commit**, dont
   un dans le script d'audit lui-même.
4. **Piste C testée** (#350) : le même sleeve redimensionné par sa
   propre volatilité (overlay #46 déjà validé, réutilisé à l'identique,
   zéro nouveau paramètre). Résultat : **PASS** — Sharpe +0,61, t-stat
   +2,08, confirmant empiriquement la littérature (Daniel & Moskowitz,
   Barroso & Santa-Clara).
5. **Batterie Règle 9 sur le #350** (#351) : **1/5**. Seule la crise
   passe (la meilleure marge de tout le backlog, MDD -4,5%/-8,4% vs
   référence -32,8%/-34,5%, cohérente avec la quasi-neutralité au
   marché). Coûts, stabilité, SPA et **DSR échouent** — DSR=0,0406,
   très loin du seuil 0,95 malgré un Sharpe supérieur à la quasi-
   totalité des candidats du backlog. **Vérification de régression
   exacte effectuée avant tout verdict** (le pipeline reconstruit
   reproduit exactement le #350 déjà committé).

**Réponse définitive** : même la construction la plus favorable
jamais testée dans ce backlog au regard de la théorie (ampleur,
neutralité au marché, sizing statistique validé par la littérature)
échoue le DSR par un ordre de grandeur considérable, pas de justesse.
**Le mur n'est donc PAS un artefact du calibrage du DSR — c'est un
fait structurel de ce programme de recherche** : à `n_trials≈360`, le
Sharpe requis (~1,7-2,0 selon `RECHERCHE_dsr_par_construction.md`)
dépasse largement tous les repères académiques standards (prime de
risque actions 0,4-0,5, facteurs Fama-French 0,3-0,5, CTA
systématiques 0,5-0,8) et n'est atteint historiquement que par des
fonds quantitatifs d'exception opérant à une fréquence et une
diversification sans rapport avec ce qui a été testé ici.

## 4. Bilan de la découverte Yahoo Finance

**Productive mais pas au sens d'un nouveau PASS** : 4 candidats testés
via cette nouvelle source (or, obligataire, rotation sectorielle,
EM/DM), tous FAIL au niveau 1. Cependant, la découverte a une valeur
méthodologique propre : elle a débloqué l'or (bloqué depuis le #134,
2 échecs FRED confirmés), a permis de tester pour la première fois
deux catégories entièrement nouvelles (obligataire réel via ETF,
rotation sectorielle/inter-marchés), et reste disponible pour de
futures recherches motivées par une hypothèse économique distincte
(au-delà des 2 sous-méthodes désormais bornées).

## 5. Réponse aux questions posées au PREREG

**Question 2 (bilan Piste A/C)** : voir §3 — réponse empirique
définitive et honnête, obtenue avec une rigueur méthodologique complète
(2 bugs corrigés en cours de route, vérification de régression avant
verdict, prédictions déclarées à l'avance à chaque étape et confirmées
ou infirmées honnêtement).

**Question 3 (bilan Yahoo Finance)** : source confirmée fonctionnelle
et réutilisable, 0/4 PASS niveau 1 sur les candidats testés via cette
source mais 2 catégories de signaux inédites explorées proprement.

## 6. Recommandation (mise à jour de la v11)

**La recommandation de fond des v9/v10/v11 reste valide et est
renforcée** : ne pas forcer de recherche d'idées à chaque firing vide.
**Mise à jour spécifique post-Piste A/C** : le sujet DSR est
considéré comme clos empiriquement pour ce backlog dans sa forme
actuelle (stratégies de timing/portefeuille scalaire), sauf nouvelle
instruction explicite de l'utilisateur pour tester la Piste B (paires
cointégrées) — dont la littérature annonce déjà un FAIL probable post-
2003 sur l'échantillon disponible (2015+), donc non prioritaire.
**Les deux voies productives restantes sont inchangées** : (1) une
nouvelle catégorie de données apportée par l'utilisateur, ou (2) un
pivot explicite vers l'Étape D — CPI (#338, PASS NET 5/5, Règle 9 3/5)
et Bitcoin (#344, PASS NET 5/5, Règle 9 2/5) restent les meilleurs
candidats identifiés, le sleeve dollar-neutre (#349/#350) étant
désormais explicitement écarté de cette liste après son échec
définitif à la Règle 9.

Voir `NONML_STRATEGY_BACKLOG.md` entrées #352-#358 pour le détail
complet de chaque cycle.
