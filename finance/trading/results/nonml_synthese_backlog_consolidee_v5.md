# Synthèse consolidée v5 — cycles #245 à #255 (11 cycles depuis la v4)

Complète (ne remplace pas) `..._v4.md` (couvrait #156-243). Pas de
nouveau calcul. Backlog au moment de la rédaction : **86 PASS niveau 1
sur 260 hypothèses testées, 0 PASS RENFORCÉ Règle 9 sans exception**.

## A. Clôture de la méga-famille vol-targeting (#247-250)

Quatre cycles de découverte consécutifs, **tous FAIL** : largeur de
bande de Bollinger (#247, redondante avec le dénominateur du mécanisme
#46 lui-même), ACF lag-1 (#248, dégradé par rapport au VR(5) déjà
testé malgré ρ=0,87 de corrélation), rebalancement hebdomadaire de la
porte Ljung-Box (#249, corrige les coûts mais dégrade stabilité et
crise — aucune amélioration nette), profondeur de drawdown relative
(#250, distincte du #38 par construction mais FAIL quand même). Après
ce bloc, la méga-famille #215-250 affiche un taux d'échec net sur ses 6
derniers cycles de découverte non-Règle-9 — confirme et aggrave le
constat de saturation déjà posé à la v4.

## B. Diagnostics informatifs (#245-246)

**#245** : DAX (le marché systématiquement le plus difficile de la
lignée #216-242) est statistiquement banal sur toutes les propriétés
liées aux mécanismes de porte (VR, kurtosis, ν, clustering ARCH) — seul
son Sharpe Buy&Hold le distingue (0,25, le plus faible des 5).
Hypothèse de travail : drift plus faible = ratio gain/coût moins
favorable à l'amplification. **#246** généralise partiellement cette
hypothèse à l'échelle de 16 cycles homogènes (ρ de Spearman = +0,700
entre Sharpe BH et taux de succès par marché) — NDX/DAX confirment les
deux extrêmes, mais Composite reste un contre-exemple net, probablement
confondu par son échantillon plus court.

## C. Guide de formalisation et sa correction (#251-252)

**#251** propose trois candidats pour un déploiement prudent : #149
(risk management), #237/#238 (meilleure significativité récente),
#38/#163 (meilleur Sharpe historique corrigé du biais du survivant, DSR
"record" 0,754). **Découverte majeure au #252** : ce DSR record n'avait
JAMAIS été recalculé avec la correction du bug d'exécution "même barre"
(#166/#167) — committé `c51ec31` avant le fix `bd5ef75`. Recalculé
correctement : **0/5 sur toute la ligne, DSR réel 0,011**. Le Candidat C
du #251 a été retiré et le guide corrigé le jour même. Un bug logiciel
distinct (texte narratif figé, `PIT_POSTAMBLE`) a été trouvé et corrigé
au passage — un script produisait un document interne contradictoire
lors de sa ré-exécution.

## D. Balayage d'intégrité complet du bug "même barre" (#252-255)

Extension systématique de la découverte du #252 à TOUS les scripts
stock-selection du backlog partageant le motif `weights[t:end] = w`
suivi de `pnl = weights[start:] * R[start:]` (le rendement du jour
`t`, déjà réalisé à la clôture, appliqué à une décision prise à cette
même clôture). L'audit original (#166/#167) n'avait couvert que #38 et
#14 ; cinq autres candidats n'avaient jamais été vérifiés.

| Candidat | Base | Overlay | Verdict causal | Marge résiduelle |
|---|---|---|---|---|
| #14 | Winners momentum court terme | — | **FAIL** (déjà su, #252) | Sharpe +1,85→-0,01 |
| #38 | Leaders 52w | 52w-high indice | **FAIL** (déjà su, #163 jamais recalculé, #252) | Sharpe +1,42→+0,47 (sous réf.) |
| #33 | Leaders 52w | SMA200 | PASS | Sharpe +1,08→+0,69 |
| #41 | Leaders 52w | union SMA200∪52w-high | PASS (= #33) | Sharpe +1,08→+0,69 |
| #48 | Leaders 52w | vol-targeting 20% | PASS | Sharpe +0,91→+0,74 |
| #11 | Leaders 52w | ToM | **FAIL** | Sharpe +0,95→+0,54 (sous réf.) |
| #23 | Leaders 52w | union ToM∪Halloween | PASS (marginal) | Sharpe +0,85→+0,60 |
| #53 | Low-Vol tilt | tendance+vol-targeting | **FAIL** | Sharpe +0,81→+0,44 (sous réf.) |

**Bilan : 4 FAIL (#14, #38, #11, #53) sur 8 candidats vérifiés, 4
survivent (#33, #41, #48, #23).** Aucun facteur simple ne prédit le
résultat individuel : ni la vitesse du signal (#11 et #23 partagent la
même architecture Leaders+calendrier et divergent), ni le type
d'overlay (#48 vol-targeting survit, #53 vol-targeting sur un autre
portefeuille échoue), ni le portefeuille de base (Leaders donne 3 FAIL
sur 6, Low-Vol donne 1 FAIL sur 1, Winners donne 1 FAIL sur 1). Chaque
candidat a dû être vérifié individuellement — **le balayage est
maintenant complet sur tous les scripts stock-selection identifiés**.

## Ce que cette période apprend, au-delà de son score

1. **Le "meilleur résultat du backlog" a changé au moins deux fois de
   nature sans jamais changer de valeur affichée**, jusqu'à ce que le
   #252 découvre l'artefact : le #38 est resté cité comme référence
   (DSR 0,754) pendant 4 jours de cycles (du #163 au #251 inclus) alors
   que le bug qui l'invalidait était déjà connu et corrigé ailleurs dans
   le même backlog depuis le #166. **Une correction de bug appliquée à
   un script ne se propage pas automatiquement aux résultats déjà
   committés par des scripts voisins qui partagent le même défaut** —
   c'est la leçon opérationnelle la plus importante de cette période,
   au-delà du contenu statistique.
2. **La méga-famille vol-targeting et le balayage d'intégrité
   stock-selection sont désormais TOUS LES DEUX épuisés** avec les
   données et outils actuellement dans le repo. Les deux axes productifs
   qui ont porté la majorité des cycles depuis la v3 (#165 pour le
   premier, #166 pour le second) ne produisent plus de découvertes
   fraîches.
3. **Le tableau des "meilleurs candidats"** (guide #251, corrigé au
   #252) reste, après ce cycle : **#149** (risk management, MDD -45
   points, SPA non significatif) et **#237/#238** (meilleure
   significativité récente, SPA p=0,0022, mais estimateur ν
   numériquement fragile). Aucun remplacement identifié pour la
   catégorie "meilleur Sharpe historique corrigé" retirée au #252.

**Recommandation honnête, inchangée dans son fond depuis la v3/v4** :
sans nouvelle catégorie de données ou de mécanisme, ou sans arbitrage
explicite de l'utilisateur entre formaliser l'existant et élargir le
périmètre, les cycles suivants produiront probablement soit des
corrections d'intégrité de portée de plus en plus étroite, soit des
variantes de plus en plus marginales des mécanismes déjà exhaustivement
testés.
