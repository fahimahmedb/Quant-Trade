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

## Couverture de ce lot

25 commits et les occurrences GitHub datées de ces quatre journées sont rattachés au registre traces.jsonl. Les jours intermédiaires sans trace datée ne sont pas interprétés comme une absence certaine d'activité. Prochaine journée active : 24 juillet ; ne pas sauter directement à septembre. Pas de revue profonde des 6 465 versions documentaires requise pour clôturer cette méthode de surface.
