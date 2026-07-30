# Pré-enregistrement — Synthèse consolidée du backlog non-ML (131 cycles)

**Committé AVANT rédaction.** Cycle #132 du backlog non-ML. Document
récapitulatif, PAS un nouveau backtest ni une nouvelle analyse
statistique — consolide des résultats DÉJÀ committés.

## Objet (fixé ici, avant rédaction)

Après 131 hypothèses testées (61 PASS niveau 1, 0 PASS RENFORCÉ Règle 9
complet sur 10 candidats évalués), le volume de résultats accumulés
justifie une synthèse unique et lisible pour l'utilisateur, plutôt que
de continuer à empiler des variantes sans vue d'ensemble. Ce document :

1. Récapitule les marchés, signaux et mécanismes testés.
2. Documente le plafond structurel identifié (n_trials élevé rend le
   DSR>0,95 quasi inatteignable pour une stratégie directionnelle
   quotidienne sur indice unique, cf. #116).
3. Liste les candidats les plus proches d'un PASS Règle 9 complet
   (#115/#121/#124/#131, tous à 3/5) et ce qui les sépare d'un PASS.
4. Formule une recommandation honnête sur la suite (continuer à
   itérer sur la même famille vs. changer d'approche).

## Méthode (fixée ici)

Lecture et compilation des fichiers `results/nonml_*.md` et du tableau
`NONML_STRATEGY_BACKLOG.md` déjà committés. AUCUN nouveau calcul,
aucune nouvelle donnée, aucun nouveau chiffre qui ne soit pas déjà
présent dans un fichier committé antérieurement. Les chiffres cités
sont ré-extraits tels quels, pas recalculés.

## Ce que ce document NE fait PAS

Ne change aucun verdict Règle 9 déjà rendu. N'introduit aucun nouveau
critère de succès. N'est pas un audit (rien à auditer — pas de calcul
nouveau à vérifier).

## Anti-cheat

Rédigé en un seul passage après ce pré-enregistrement, sans calcul
intermédiaire dont le résultat influencerait le contenu.
