# QUANT-TRADE — REPRISE DE PROFONDEUR INTERNE, SANS RECOMMENCER

Dépôt : fahimahmedb/Quant-Trade
Branche : builder/research-os-aggressive-architecture-20261015
Dernière implémentation poussée : 83f39cd479f6106952af0febd156e9ee6f6c10dc
Dernier code entièrement qualifié avant cette étape : df6b77041a8513d568274dabfadb0438eccc1021
Checkpoint initial de profondeur : 6130d6c4f97f76346760a5309ecc1efd32119eb6 — historique, ne pas y revenir.

## Mandat actuel

Poursuis en pleine autonomie les lots autorisés de profondeur interne du Research
OS derrière les interfaces déjà figées. NO_NEW_TOP_LEVEL_ARCHITECTURE = TRUE.
La spine canonique et les six contrats communs restent stables. Ce chantier ne
réintroduit pas les anciens agents Blue/Astra. Validator et Red Team restent des
fonctions du système avec séparation producteur/validation et droits négatifs.

Lis le HEAD distant actuel et conserve tout commit plus récent. Vérifie que
83f39cd479f6106952af0febd156e9ee6f6c10dc est dans son ascendance ; des commits de
reçu/handoff peuvent le suivre. Ne fais aucun reset vers un ancien checkpoint.

Lis AGENTS.md et le North Star dans le cadre de ce mandat actuel, puis :

- research/research_os/architecture/WORK_CONTINUOUS_BUILD_WORKFLOW_20261015.md
- research/research_os/architecture/work_receipts/WORK_BUILD_STATE.json
- research/research_os/architecture/work_receipts/DEPTH_FUNDAMENTAL_DOSSIER_002_RECEIPT_20261015.json
- research/research_os/architecture/work_receipts/DEPTH_FUNDAMENTAL_DOSSIER_002_20261015.json
- research/research_os/architecture/WORK_BUILD_QUALIFICATION_20261015.md

## Dernière étape réellement exécutée

DEPTH-FUNDAMENTAL-DOSSIER-002 est implémenté et poussé, en attente de qualification
CI générale. Dans expansion/engine_dossiers_v1.py, documentary_dossier_detail()
reconstruit le candidat avec son vrai moteur et lie les sections Fundamental à
la capture Apple déjà admise : identité, cellules comptables, trésorerie,
unités/période/disponibilité et condition de falsification. build_engine_dossier()
conserve son interface existante avec détail documentaire optionnel.

Les champs non étayés restent UNKNOWN, les cellules partielles PARTIAL ; une
valorisation, un bilan, des révisions ou des catalyseurs ne passent pas grâce à
du texte rempli. Le dossier économique reste BLOCK. Les prémisses de rentabilité
comptable non positives sont signalées comme DISCONFIRMED. Le candidat reste
immuable. Les contre-exemples numériques des tests ne sont pas de vraies sources.

127 tests Research OS passent localement, dont 4 nouveaux tests de dossier.
Sept CI Research OS sur 83f39cd… sont SUCCESS. SEC P0 run 38803294634 était encore
IN_PROGRESS au handoff. Inspecte son état frais :
https://github.com/fahimahmedb/Quant-Trade/actions/runs/38803294634

Si ce gate est encore en cours, ne l'annule pas et ne recommence pas Fundamental :
laisse son statut IN_PROGRESS et avance le lot Event indépendant. Si le gate
échoue, traite uniquement le défaut démontré. S'il réussit, persiste la conclusion
et le SHA exact, puis marque le lot COMPLETE à son périmètre. N'attribue jamais
une ancienne CI à un nouveau commit de code ou de documentation.

Cette étape construit le dossier Fundamental ; son raccordement aux consommateurs
canoniques/Validator/Portfolio n'est PAS encore réalisé et appartient au lot
DEPTH-DOSSIER-CHALLENGE-PORTFOLIO-003. Les captures et les lots documentaires
précédents sont déjà prouvés : ne les refais pas.

## Suite de la roadmap

1. DEPTH-EVENT-DOSSIER-002 : étendre le même dossier existant à Event/Documents.
   Réutiliser sources/apple_dividend_announcements.json ; garder la comparaison
   annuelle Q2, les horloges de capture et les conditions de falsification.
   Ne pas transformer une différence documentaire en nouveauté, surprise de
   consensus, diffusion ou réaction de prix démontrée. Tester incohérences et
   prémisses manquantes sans muter CandidateHypothesis.
2. DEPTH-QUANT-FLOW-RULE-002 : approfondir une règle officielle opérante, l'acteur,
   le périmètre éligible et les exceptions. La FAQ SEC déjà capturée est une
   explication non contraignante, pas le texte de règle. Legacy avant downstream ;
   pas de famille close rouverte ni de quantité/flux forcé inventé.
3. DEPTH-DOSSIER-CHALLENGE-PORTFOLIO-003 : faire consommer les dossiers renforcés
   par les Validator/Red Team et Economic Identity/Portfolio existants. Exiger
   une provenance pour les prémisses, conserver UNKNOWN et les blocages réels.
4. DEPTH-QUALIFICATION-003 : prouver replay/recovery et CI sur le SHA exact de la
   nouvelle implémentation ; persister le reçu et les écarts restant ouverts.

## Mode d'exécution et frontières

Push GitHub à chaque étape bornée, avec reçu, vrais résultats, SHA et prochaine
action. N'attends pas une confirmation de routine pour continuer les tâches
autorisées. Réconcilie un HEAD déplacé sans force-push ni écrasement d'autrui.
Si git push n'a pas de credentials, réutilise le connecteur GitHub disponible.

La forme canonique est prouvée sur une tranche ; la profondeur interne reste
PARTIAL. La fin d'un lot n'est pas la fin de toute la mission. Poursuis les
travaux utiles de la roadmap jusqu'à leur acceptation ou un blocage réel.

ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

Pas de prix/payoffs/rendements acquis, tests économiques, observation prospective,
allocation, ordres, ressources payantes, merge/déploiement de production ou
modification des cinq automatisations. Ne touche pas aux chantiers Live Lab/UX.
Des tests d'ingénierie ne constituent pas une validation scientifique indépendante.

La matérialisation locale research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json
est volontairement non suivie : ne pas la committer. Si elle manque, réutilise la
matérialisation épinglée décrite dans la CI existante.
