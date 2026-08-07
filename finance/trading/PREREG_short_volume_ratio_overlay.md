# Pré-enregistrement — Ratio de volume vendu à découvert (FINRA Reg SHO, QQQ), overlay défensif

**Committé AVANT tout calcul.** Cycle #367 du backlog non-ML.

## 1. Contexte et hypothèse (nouvelle source de données ET nouveau mécanisme)

**Nouvelle source de données, jamais utilisée dans ce backlog** : les
fichiers quotidiens "Reg SHO" de la FINRA (Financial Industry
Regulatory Authority, régulateur des marchés US), publiés gratuitement
chaque jour de bourse depuis ~8 ans en rolling window
(`cdn.finra.org/equity/regsho/daily/CNMSshvol<YYYYMMDD>.txt`), donnant
pour CHAQUE titre coté le volume vendu à découvert (`ShortVolume`) et
le volume total échangé (`TotalVolume`) ce jour-là, consolidé sur
l'ensemble des plateformes de négociation qui déclarent à la FINRA.

**Mécanisme distinct du positionnement CFTC déjà testé et clos (0/2,
#360/#361)** : le CFTC mesure le positionnement AGRÉGÉ HEBDOMADAIRE
des spéculateurs sur des contrats à terme (marché dérivé, mise à jour
lente). La FINRA Reg SHO mesure le **VOLUME QUOTIDIEN de vente à
découvert sur le marché ACTIONS/ETF au comptant** — un flux
transactionnel à haute fréquence (quotidien), pas une position
agrégée. **Ratio de volume vendu à découvert** (`ShortVolume /
TotalVolume`) : mesure la PROPORTION de l'activité de négociation
quotidienne qui est initiée par des vendeurs à découvert — utilisé
dans la littérature de microstructure de marché comme proxy
d'incertitude/désaccord informationnel (Diether, Lee & Werner 2009 ;
Boehmer, Jones & Zhang 2008) : un ratio élevé peut signaler soit une
anticipation baissière accrue, soit une activité de couverture/
arbitrage accrue en période de stress — **même direction contrariante/
défensive que le COT** (ratio élevé = incertitude/stress accru =
défensif), déclarée à l'avance par cohérence avec le reste des
signaux de ce backlog, PAS parce que l'interprétation économique est
tranchée dans la littérature (elle ne l'est pas — signalé honnêtement
au §6).

**Actif sous-jacent testé** : `QQQ` (ETF répliquant le NASDAQ-100,
le plus liquide, disponible en continu sur la fenêtre FINRA) — proxy
direct pour le sentiment/l'incertitude sur l'indice NDX lui-même,
contrairement au COT qui portait sur les FUTURES NASDAQ-100 (produit
dérivé séparé de l'ETF au comptant).

## 2. Données

**Nouvelle donnée** : fichiers quotidiens FINRA Reg SHO, extraction de
la ligne `QQQ` de chaque fichier journalier. **Fenêtre disponible
vérifiée par sondage systématique AVANT ce PREREG** : rolling window
d'environ 8 ans, début exact vérifié à **01/08/2018** (fichiers avant
cette date renvoient HTTP 403, fichiers à partir de cette date
renvoient un contenu valide avec la ligne QQQ présente) — **fenêtre
mobile** : à chaque nouvelle exécution future de ce script, la borne
de début reculera mécaniquement d'autant de jours écoulés (conséquence
du rolling window FINRA, pas un choix arbitraire de ce cycle).

**Récupération** : ~2900 requêtes HTTP individuelles (une par jour
calendaire depuis 01/08/2018, weekends/jours fériés retournant
naturellement une erreur 403 filtrée), **lancée en tâche de fond AVANT
ce PREREG et toujours en cours au moment de ce commit** (vérification
de faisabilité déjà complète — fenêtre confirmée par sondage manuel
avant d'écrire ce PREREG — mais téléchargement exhaustif encore en
cours, opération réseau longue, aucun calcul de signal effectué à ce
stade). Fichier brut à committer séparément dès que la récupération
est terminée : `data/qqq_short_volume_daily.csv` (colonnes `date,
short_volume, total_volume`, aucun calcul de ratio/signal dedans) —
**aucun calcul de tercile/backtest ne sera lancé avant que ce fichier
soit complet et committé**, conformément à la Règle 1
(PROTOCOLE_ANTI_SNOOPING.md).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que tout signal macro-externe/positionnement appliqué
uniformément (jauge de stress/incertitude systémique dérivée de
l'ETF le plus liquide du NASDAQ-100), cohérent avec la pratique déjà
établie (ex. COT NASDAQ-100 #360 appliqué aux 5 marchés).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `ShortVolRatio(t) = ShortVolume(t) / TotalVolume(t)` sur QQQ.
- Alignement causal : FINRA publie le fichier "en date du" jour J le
  soir même/le lendemain matin (délai de traitement établi ~T+1,
  publication généralement disponible avant l'ouverture du jour
  suivant) — **décalage conservateur de 2 jours calendaires**
  (`PUBLICATION_LAG_DAYS=2`, marge de sécurité), puis alignement
  causal quotidien standard `ffill+shift(1)` (Règle 7).
- Seuil : **tercile EXPANDING** de `ShortVolRatio_lag(t)` sur le
  NIVEAU BRUT (construction réutilisée à l'identique du #357 MOVE/
  #291 NFCI/#360 COT, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `ShortVolRatio_lag(t)` est dans son tercile expanding le PLUS HAUT,
  `1,0x` sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS`
  réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un niveau brut, une direction déclarée à
l'avance par cohérence avec le reste du backlog, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**FAIL anticipé mais pas exclu** : (1) l'interprétation économique du
ratio de volume court n'est PAS tranchée dans la littérature
(signal informationnel vs bruit de couverture/arbitrage) — direction
choisie par cohérence avec le reste du backlog, pas par conviction
forte ; (2) le CFTC (mécanisme de positionnement proche en esprit) a
déjà FAIL net les deux fois testées (#360/#361) ; (3) historique
court (~8 ans, comparable à BDRY) limite la puissance statistique.
Résultat rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le ratio de volume court sur un ETF très liquide comme QQQ est
   largement dominé par l'arbitrage de création/rachat et le
   market-making (obligation réglementaire de coter des deux côtés),
   pas par des paris directionnels informés — signal potentiellement
   très bruité pour un ETF (contrairement à une action individuelle).
2. Fenêtre mobile de ~8 ans (2018+), historique le plus court de la
   famille des signaux macro-externes après Bitcoin/BDRY/COT.
3. Décalage de publication approximatif (2j, non documenté
   officiellement par la FINRA avec la même précision qu'un
   calendrier de publication BLS/Fed) — risque de imprecision non
   quantifiable exactement, traité de façon conservatrice.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un
   résultat.

## 8. Sortie

`data/qqq_short_volume_daily.csv` (donnée brute, committée avec ce
PREREG), `scripts/nonml_short_volume_ratio_overlay_backtest.py`,
`scripts/nonml_short_volume_ratio_overlay_audit.py`,
`results/nonml_short_volume_ratio_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
