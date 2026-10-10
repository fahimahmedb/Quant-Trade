# Checkpoint — construction autorisée

STATUS = BUILD_VERIFY_PUBLISH
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

- Accord Owner : construction autonome sur les recommandations, protection du N ; instruction actuelle remplace l'attente documentaire précédente.
- Branche indépendante `research/edge-lab-continuous`, base distante vérifiée `09ba64b8bee1419076ec8a30f8d75a916932c2ba`.
- Rapport révisé : `docs/owner-edge-audit-2026-10-10@fae3be50549d8b023c3e9a42eb14a51613bcb8c4`, trois fichiers documentaires conservés.
- Réutilise écritures atomiques quant.state et ResearchTask ; ne démarre pas l'ancien QuantSystem.
- Rejets/expositions/réservations conservés ; 40 B2+B4 sans double somme ; M effectif et historique privé UNKNOWN.
- Aucun nouveau look économique au bootstrap. Fenêtres/thresholds legacy inchangés, outcomes F1 A/B non ouverts.
- Programme : ZF qualification prioritaire ; EURUSD proxy conditionnel ; HL prospective si hôte réel qualifié.
- Mémoires/Book/data-feeds restent séparés ; H001 exclu du dispatcher pour éviter travail concurrent.
- Contrôle persistant : CONTROL.json ; source de vérité runtime : STATE.json ; panneau dérivé : STATUS.md.
- Scheduler unique prévu : réutiliser `6ac978ecda1081918fba4d76dee437f4` ; remplacer ancien prompt avant activation.
- Workflow limité à cette branche : tests + métadonnées sur push code/contrôle ; aucun cron branch-only trompeur.
- Tests locaux : 29 PASS, synthétiques uniquement, dont deux clones Git réels et deux processus de réservation.
- Coût : tokens/facture/polling/temps humain NON MESURÉS ; budget total Owner NON FOURNI ; aucun achat.
- Bornes techniques par job/payload : 120 s / 2 MiB ; aucune quota d'essais ou Sharpe cible.
- Pause/reprise/CAS/crash/budget/inconnus testés. Un résultat incertain reste consommé, sans relance économique.
- Prochaine action : vérifier/publier fichiers sur la branche, activer scheduler existant, vérifier état/outils/reçu.
- Condition d'arrêt : pause Owner, droit/ressource manquants, budget observé atteint, ambiguïté de réservation ou intégrité.
- À la reprise : lire ce checkpoint + CONTROL + résumé STATE ; rafraîchir seuls heads pertinents ; exécuter la prochaine question utile.
