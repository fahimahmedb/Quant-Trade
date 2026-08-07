# Pré-enregistrement — Pression de vente des initiés (SEC Form 4, panier AAPL/MSFT/NVDA), overlay défensif

**Committé AVANT tout calcul.** Cycle #369 du backlog non-ML.

## 1. Contexte et hypothèse (nouvelle source de données ET nouvelle classe de participant)

**Nouvelle source de données, jamais utilisée dans ce backlog** : les
déclarations "Form 4" de la SEC (Securities and Exchange Commission),
que tout dirigeant/administrateur ("insider" au sens de la Section 16
du Securities Exchange Act) doit déposer pour chaque transaction sur
les titres de sa propre entreprise, disponibles gratuitement via
`data.sec.gov/submissions/CIK<n>.json` (index des dépôts) et
`sec.gov/Archives/edgar/data/<cik>/<accession>/<document>.xml`
(détail de chaque transaction).

**3e classe de participant de marché testée dans ce backlog**, après
le positionnement spéculatif CFTC sur futures (#360/#361, clos 0/2) et
le volume de vente à découvert FINRA (#367, FAIL) : ici, les
DIRIGEANTS/ADMINISTRATEURS eux-mêmes des entreprises, dont l'activité
d'achat/vente sur leur propre titre est documentée dans la littérature
financière comme signal informationnel (Seyhun 1986 ; Lakonishok & Lee
2001) — **direction contrariante/défensive déclarée à l'avance, par
cohérence avec CFTC/FINRA** : une pression de VENTE nette élevée de la
part des initiés est interprétée comme un signal pessimiste informé
(les initiés ont un avantage informationnel sur la valorisation future
de leur entreprise), donc défensive.

**Limite reconnue à l'avance — investigation de faisabilité menée aux
2 cycles précédents** : aucun fichier consolidé quotidien équivalent
CFTC/FINRA n'existe — chaque dépôt individuel a été récupéré et parsé
séparément (1879 dépôts au total sur les 3 entreprises). **Filtre
strict appliqué** : seuls les codes de transaction `P` (achat de
marché ouvert) et `S` (vente de marché ouvert) sont retenus — TOUS les
autres codes (`M` exercice de dérivé, `F` retenue fiscale, `A`
attribution/octroi, `G` don, etc., confirmés dominants dans un dépôt
réel inspecté au cycle précédent) sont explicitement EXCLUS car ce
sont des événements de rémunération programmée sans contenu
informationnel directionnel — filtre appliqué et vérifié avant tout
calcul de signal (voir §2).

## 2. Données

**Nouvelle donnée** : panier de 3 entreprises parmi les plus grandes
pondérations du NASDAQ-100 (Apple, Microsoft, Nvidia — choisies pour
réduire le risque idiosyncratique d'une seule entreprise, chacune
individuellement testée aurait un poids économique trop spécifique
pour une jauge "de marché"). **Fenêtre commune vérifiée avant ce
PREREG** : le nombre de dépôts Form 4 disponibles via l'API
`submissions` (sans pagination vers l'historique antérieur) couvre
587 dépôts AAPL (2015-06-01+), 726 dépôts MSFT (2020-05-04+), 566
dépôts NVDA (2020-06-12+) — **fenêtre commune bornée par la plus
tardive (NVDA, 12/06/2020), soit ~6 ans**, limite reconnue à l'avance
(plus courte que la plupart des candidats macro-externes mais
comparable au précédent Bitcoin ~11 ans/BDRY ~8 ans déjà acceptés).

**Récupération** : ~1879 dépôts individuels (587+726+566), chacun
parsé pour ses transactions `nonDerivativeTable` de code `P`/`S`
uniquement, montant = `shares × pricePerShare` (transactions sans prix
renseigné explicitement exclues, cas rare pour du marché ouvert).
**Lancée en tâche de fond AVANT ce PREREG et toujours en cours au
moment de ce commit** (vérification de faisabilité et du format déjà
complète — inspection d'un dépôt réel documentée au cycle précédent —
mais téléchargement/parsing exhaustif des ~1879 dépôts encore en
cours, opération réseau longue, aucun calcul de signal effectué à ce
stade). Fichier brut à committer séparément dès que la récupération
est terminée : `data/insider_form4_transactions.csv` (colonnes `date,
ticker, code, shares, price, value`, aucun calcul de ratio/signal
dedans) — **aucun calcul de tercile/backtest ne sera lancé avant que
ce fichier soit complet et committé**, conformément à la Règle 1
(PROTOCOLE_ANTI_SNOOPING.md).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que tout signal macro-externe/positionnement appliqué
uniformément comme jauge systémique dérivée d'un panier de titres
technologiques dominants.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Pour chaque jour de bourse, `NetSellValue(t) = Σ(valeur des ventes S)
  − Σ(valeur des achats P)` agrégé sur les 3 entreprises (en dollars).
- **Fenêtre glissante de 21 jours** (`ROLL_WINDOW=21`, réutilisé du
  `RET_WINDOW=21` déjà validé au #198 et suivants, Règle 7) : les
  dépôts Form 4 étant rares et discontinus jour par jour (la plupart
  des jours n'ont aucune transaction P/S), un NIVEAU BRUT quotidien
  serait dominé par des zéros — la fenêtre glissante lisse ce
  problème, même logique que les signaux macro peu fréquents déjà
  traités par agrégation/moyenne mobile dans ce backlog.
  `NetSellPressure(t) = somme glissante 21j de NetSellValue`.
- Alignement causal : dépôt Form 4 réglementairement requis sous 2
  jours ouvrés après la transaction, mais délai de dépôt effectif
  variable — **décalage conservateur de 3 jours calendaires**
  (`PUBLICATION_LAG_DAYS=3`), puis alignement causal quotidien
  standard `ffill+shift(1)` (Règle 7).
- Seuil : **tercile EXPANDING** de `NetSellPressure_lag(t)` sur le
  NIVEAU (construction réutilisée du #357/#360, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `NetSellPressure_lag(t)` est dans son tercile expanding le PLUS
  HAUT (pression de vente nette des initiés la plus forte), `1,0x`
  sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre glissante réutilisée à
l'identique, une direction déclarée à l'avance par cohérence avec le
reste du backlog, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**FAIL anticipé mais pas exclu** : (1) panier de seulement 3
entreprises — signal potentiellement dominé par des événements
idiosyncratiques propres à une seule entreprise malgré la
diversification partielle ; (2) fenêtre la plus courte de ce backlog
après Bitcoin (~6 ans) ; (3) le CFTC et le FINRA (mécanismes de
positionnement/flux proches en esprit) ont déjà FAIL net les trois
fois testées (#360/#361/#367) ; (4) même les initiés les mieux
informés ne vendent pas toujours pour des raisons liées à leur
opinion sur le titre (diversification personnelle, liquidité,
planification fiscale de fin d'année — bruit reconnu dans la
littérature académique elle-même). Résultat rapporté tel quel, sans
retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Panier de 3 entreprises seulement — risque idiosyncratique résiduel
   malgré la diversification partielle.
2. Fenêtre la plus courte de la famille de signaux "positionnement/
   flux" après Bitcoin.
3. Le signal agrège des TRANSACTIONS DE VENTE D'INITIÉS DE
   TECHNOLOGIE MEGA-CAP appliquées comme jauge de stress sur 5
   marchés incluant des petites capitalisations (Russell 2000) et un
   marché européen (DAX) — lien économique direct non garanti.
4. Décalage de publication approximatif (délai légal théorique de 2
   jours ouvrés, mais délai effectif réel non garanti identique).
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un
   résultat.

## 8. Sortie

`data/insider_form4_transactions.csv` (donnée brute, committée avec
ce PREREG), `scripts/nonml_insider_selling_pressure_overlay_backtest.py`,
`scripts/nonml_insider_selling_pressure_overlay_audit.py`,
`results/nonml_insider_selling_pressure_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
