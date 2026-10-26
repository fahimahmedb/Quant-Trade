# Critères fonctionnels — pas d'implémentation pendant cette analyse

Tous ces critères s'appliquent à une future cible composée explicitement qualifiée. Aucun n'est déclaré PASS par cette note. L'audit de l'ensemble du projet reste INCOMPLETE.

| ID | Critère observable | Réutilisation / limite |
|---|---|---|
| A01 | Un manifeste exact distingue contenu qualifié, contenu intégré et release opérationnelle. | Qualification de branche non transitive. Q ne passe pas tant que ses attaques obligatoires pertinentes restent inexpliquées. |
| A02 | Les contrôles d'indépendance sémantique, sujet/proposition, modèle et fenêtre de génération sont cohérents sur la cible. | Réutiliser C0/V2/H/V/Q selon équivalence, sans copie globale des anciennes implémentations. |
| A03 | Une observation primaire réelle nouvelle est capturée et qualifiée ; ses droits, clocks, version et incertitudes sont durables. | Réutiliser le plan données. Une date de capture n'est pas une PIT historique ni une preuve d'indépendance. |
| A04 | Root, seed, variante et exposition précèdent la sélection favorable ; les tentatives bloquées/rejetées sont conservées. | Réutiliser F et native V2 ; V3 compte ses propositions, pas tout l'historique. |
| A05 | Une proposition passe une admission V3 réelle ou est rejetée avec raisons ; les fixtures ne sont pas une production scientifique. | Un seul propriétaire de l'admission V3, sans Candidate upstream. |
| A06 | Une décision RI qualifiée, et non l'éligibilité seule, conduit au prochain propriétaire ou à un arrêt motivé. | Réutiliser RI/Discovery. Une action RI d'enquête n'est pas RUN_PRODUCER. |
| A07 | Toute disposition exigeant une suite référence un descendant durable, ou un blocage/parking avec précondition de réouverture. | Étendre le Control Plane/handoffs existants, sans second workflow engine ou ledger. |
| A08 | La création de descendant et sa publication se reprennent sans double tâche ni double essai après perte d'ACK/crash. | Réutiliser transactions, leases, reçus et outbox existants ; distinguer tentatives d'infrastructure et essais scientifiques. |
| A09 | Les tâches/capacités/stages sont compatibles et leur autorité explicite ; un veto demeure effectif. | Aucun simple changement de texte ne confère de droit. |
| A10 | Un témoin UST a une disposition actuelle explicite ; son historique et son conflit d'autorité restent traçables. | Ne pas fabriquer un ancien reçu, modifier le protocole exposé ou présumer son grant actif. |
| A11 | Un cas admissible atteint une expérience figée sous autorité et un résultat traité par l'évaluateur compétent. | PARK/BLOCK prouve le traitement d'un arrêt ; il ne remplace pas la preuve d'exécution de cette expérience. |
| A12 | Résultat nul/négatif/positif et portée de claim entrent dans Memory sans nouvelle indépendance fictive. | Maintenir séparées reproduction, OOS, prospective, économie, portefeuille et autorité live. |
| A13 | La génération s'arrête sur budget/backlog/doublons/source absente/capacité indépendante insuffisante, et zéro idée valide est accepté. | Réutiliser F ; les seuils/capacités déclarés exigent une validation opérationnelle. |
| A14 | Les métriques ont root/cohorte/variantes/coûts/délais et exposent les observations censurées ou inconnues. | Aucune optimisation sur le nombre de seeds ou le ratio naïf de PASS. |
| A15 | Les preuves et versions des prochaines passes sont publiées séparément avec manifeste et ZIP. | Ne jamais réécrire pass-01 ou l'archive initiale. |

Premier jalon de lignée : source → disposition explicite. Jalon distinct, plus fort : expérience réellement exécutée → évaluation → mémoire. Ni l'un ni l'autre ne prouve l'existence d'un edge durable.
