# Juillet — historique de surface en cours

Périmètre initial figé ; dates UTC de commit séparées des dates GitHub. Lecture de surface des intitulés, modifications de chemins et événements collectés. Les tests, métriques et déploiements déclarés ne sont pas requalifiés. Le devenir dans les lignées de septembre/octobre sera relié dans la suite chronologique.

## 13 juillet — démarrage NASDAQ, prédiction et overlay

09 commits accessibles. À 01:44, d49290b2a3 introduit les diagnostics A et volatilité C, leurs scripts, données NASDAQ et rapports ; 35cf6d626e ajoute gitignore et retire les bytecodes. À 14:43, eb588f5711 ajoute prediction.py et le runner B (triple-barrier, walk-forward, DSR). La PR #1 est ouverte à 14:44:36 : sa description rapporte l'absence de signal actif supérieur au Buy & Hold au seuil déclaré ; ce n'est pas une nouvelle validation économique de cet audit.

À 15:50, 777c7960c5 ajoute l'historique NASDAQ-100 et met à jour scripts/rapports. À 23:24, b2dcd5720c ajoute CLAUDE.md et quatre définitions d'agents. À 23:34, 6fff20de5d ajoute overlay.py, meta_labeling.py et leurs runners/synthèse. Les trois derniers commits 69007c88d5, 1e04a9dcde, 841b713bfa ajoutent les rapports D, C, B et meta-labeling. Publication de rapports et résultat scientifiquement vérifié restent distincts.

Réutilisation à examiner : loaders/diagnostics/volatilité/prédiction/overlay sont les sources historiques de départ ; ne pas reprendre leurs premiers états sans les corrections des jours suivants. Les définitions d'agents sont des instructions historiques.

## 14 juillet — composition, généralisation et premiers correctifs lookahead

11 commits accessibles. De 00:08 à 00:27 : a40cc098b6 ajoute l'optimisation overlay et variantes meta-labeling ; ffbf4880d1 décrit la tâche pipeline ; 5b91c0f51f introduit integrated_pipeline.py et runner ; af0e709f6b décrit les tâches ensemble/cross-market/rapport ; a8543f23e5 publie le rapport exécutif ; 912f6f11d9 ajoute les runners ensemble/cross-market et les fichiers Russell/S&P/DAX.

À 00:41, be13c3e72a publie backtest_indices.md avec un intitulé « généralisation ÉCHOUÉE ». À 00:44, 9683dca5ed publie RECAP_COMPLET.md. Ces déclarations précèdent les corrections de causalité : ne pas les agréger sans conserver cet ordre.

À 01:32, 58e5c21b21 introduit l'analyse PBO/CSCV et l'audit overlay. À 01:54, 4816b2dbbd ajoute tests/test_no_lookahead.py et un hook. À 02:14, 27d41c07fe modifie overlay.py, volatility.py et ces tests avec l'intitulé de corrections lookahead. La timeline PR #1 référence ces trois commits à 01:32:47, 01:54:35 et 02:14:50 ; ces heures GitHub ne remplacent pas les heures de commit.

Réutilisation : audit/contrôles de causalité et corrections sont à préserver avec leur portée. L'ajout d'un test n'est pas la preuve qu'il a été exécuté. Aucun backtest n'est rejoué ici.

## 15 juillet — embargo, sigma causal et verdict de simplification

04 commits accessibles : ee8a2fd136 à 07:08 annonce pré-enregistrement du couple cap=1.50/pctl=95 et embargo de 21 jours ; c709982f4c à 07:13 annonce sigma triple-barrier calculé en walk-forward ; 06915ec365 à 07:27 ajoute un test d'isolation avec l'intitulé indiquant que l'overlay détruit le signal LogitL2 ; 5932795643 à 07:29 consigne un verdict de simplification vers Buy & Hold. La PR #1 référence le dernier commit à 07:29:32.

Réutilisation : retenir la séquence de corrections et le verdict historique, pas seulement la synthèse optimiste antérieure. Les propriétés exactes du code et les nombres restent à approfondir uniquement si leur réutilisation l'exige.

## 20 juillet — robot paper annoncé

01 commit accessible : 97b961cece à 00:15 annonce un robot paper sans coût et un déploiement « complete ». Le titre ne prouve pas une installation externe ni une continuité de service. La destination actuelle de ces éléments sera examinée dans les jours suivants ; aucune activation n'est effectuée.

## 24 juillet — audit canonique et robustesse du socle A/C/D

10 commits accessibles, chaîne linéaire de 97b961cece à 0894777f8b. Le premier, 517ba73473, corrige selon son message la reproductibilité SPA, la cohérence walk-forward et l'alignement du proxy ; les résultats numériques annoncés restent des résultats rapportés, non rejoués ici. Au milieu du lot, 2334c675b8 ajoute un driver d'audit de robustesse avec grilles de perturbation, régimes, stress cross-window, stabilité des paramètres, ADF/autocorrélation, CSCV/PBO et courbure locale. Le lot ajoute ensuite les sorties de robustesse, dont cinq heatmaps, une stabilité de paramètres et un PBO annoncé à 0,109 sur 3 432 partitions. 0894777f8b clôt la journée par un statut « audit complete / deployment ready » : conserver cette déclaration comme état historique, pas comme garantie indépendante.

Réutilisation : les correctifs de causalité/reproductibilité et les scripts d'audit sont plus importants que le label « final ». Le diff cumulé ajoute notamment AUDIT_CANONICAL_FRAMEWORK_FINAL.md, ROBUSTNESS_AUDIT_DETAILED.md, résultats A/C/D, scripts d'audit et robustesse. Aucune occurrence GitHub datée supplémentaire dans l'index de cette journée.

## 25 juillet — réorganisation puis invalidation d'une partie des résultats

14 commits accessibles, chaîne linéaire de 0894777f8b à 5dcf49c7cd. fdbd19342c réorganise le dépôt en finance/, divers/robot-politique/ et cours/, avec de nombreux renommages : cette migration de chemins est une information d'identité importante pour relier les fichiers historiques aux successeurs. Plus tard, f70ae6713d annonce deux bugs critiques corrigés, calc_mdd() et frac_diff(), et requalifie plusieurs signaux auparavant présentés comme robustes en artefacts de data-snooping ; son verdict déclaré remet Buy & Hold en tête après 50+ hypothèses. Le lot ajoute de nombreux scripts d'hypothèses et rapports d'audit/recherche. En fin de journée, 5dcf49c7cd valide O5 sur un marché indépendant mais le requalifie en overlay défensif : réduction du MDD, pas edge directionnel généralisable sur le Sharpe.

Réutilisation : ne jamais reprendre une synthèse du 24 juillet sans appliquer les corrections/requalifications du 25. Les mouvements de fichiers sont des continuités d'identité, pas de nouvelles capacités. Aucune occurrence GitHub datée supplémentaire dans l'index de cette journée.

## 26 juillet — nouvelle candidate, package paper puis boucle ML itérative

27 commits accessibles, chaîne linéaire de 5dcf49c7cd à 2b1f03b13f. Le premier commit de la journée, 55e0ce0686, annonce S5 (EMA 50>200) comme première candidate ayant passé une validation cross-market et prévoit explicitement une correction DSR multi-testing : le statut « VALIDATED » est donc historique et non une autorité finale. Le milieu du lot, ef3b60fe88, publie un package de déploiement paper et réaffirme une Phase D ; ce paquet est une construction, pas la preuve d'un service externe actif. La journée bascule ensuite vers un cadre anti-data-snooping, un rebuild strict de Phase B et une boucle d'itérations ML. Le dernier commit, 2b1f03b13f, supprime les résultats d'une première tentative d'Iteration 3 après 48/50 erreurs dues à un off-by-one et indique un retry après correction.

Le diff cumulé confirme l'ajout de TESTING_FRAMEWORK.md, AUDIT_CONCLUSION.md, anti_data_snooping_audit.py, phase_b_strict_rebuild.py, plusieurs runners ML, résultats de protocole et un package zip ; il supprime aussi de nombreux rapports/scripts de la phase précédente. La timeline de la PR #1 contient une occurrence GitHub datée le 26 à 00:05:56 référençant 90872c4b ; elle est distincte de l'heure de commit.

Réutilisation : la présence simultanée de « deployment ready », d'un nouveau protocole anti-snooping et d'une itération échouée montre que les labels de maturité ne doivent pas être utilisés comme autorité. Préserver les correctifs de protocole et les échecs observés.

## 27 juillet — exploration ML massive, protocole anti-snooping et alternatives au market timing

67 commits accessibles, chaîne linéaire de 2b1f03b13f à 8d5cd59278. Le début de journée nettoie les artefacts runtime et poursuit les itérations ; au milieu, f2af1dccc1 correspond déjà à l'Itération 15, avec de multiples familles de modèles. Le diff cumulé ajoute les scripts iter4 à iter27, un brute-force ML, notifications/daemon Telegram, une validation cross-market, un audit adversarial et surtout PROTOCOLE_ANTI_SNOOPING.md.

En fin de journée, la lecture change de niveau : 5a0b0b8dbd pré-enregistre D v2 sans levier, 1307611d50 rapporte le test final unique et un échec 0/3 marchés selon le critère complet ; le message interdit alors de retuner cette hypothèse sur les mêmes marchés. 8d5cd59278 explore ensuite deux familles alternatives : levier Kelly et diversification risk-parity multi-indices ; le message rapporte demi-Kelly favorable sur NDX, plein Kelly plus risqué en MDD et un gain de diversification actions-actions seulement marginal. Ces résultats restent des résultats rapportés, pas une validation économique actuelle.

La timeline de la PR #1 contient deux occurrences datées le 27 : référence à b640a9533f à 08:25:13 puis à 5a0b0b8dbd à 22:09:15. Elles expliquent les deux occurrences GitHub de l'index sans créer deux nouveaux travaux indépendants.

Réutilisation : conserver l'anti-snooping et les verdicts négatifs comme contraintes de continuité. Les nombreuses itérations sont des explorations historiques, pas 24 capacités autonomes à maintenir. Les utilitaires Telegram et dashboard devront être classés plus tard entre infrastructure réutilisable et surface abandonnée.

## Couverture de ce lot

143 commits sont désormais revus à la surface sur huit journées actives : 13, 14, 15, 20, 24, 25, 26 et 27 juillet. Les occurrences GitHub datées associées sont rattachées en conservant leur nature de référence/timeline. Les jours intermédiaires sans trace datée ne sont pas interprétés comme une absence certaine d'activité.

Prochaine journée active : **28 juillet 2026**. La lecture profonde des milliers de versions documentaires n'est pas requise pour clôturer cette méthode ; approfondir seulement les ambiguïtés qui changent la réutilisation, l'autorité ou la future convergence.
