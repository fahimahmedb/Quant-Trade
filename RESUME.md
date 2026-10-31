# Point de reprise courant — 31 octobre 2026

PAUSE DEMANDÉE PAR L'OWNER. Audit exhaustif non terminé. Lire [la mémoire de reprise](governance/forensic-20261031/RESUME.md), puis [le guide de revue](governance/forensic-20261031/REVIEW_THIS_WORK.md). Les compteurs et lectures courants sont dans le même dossier. Les archives distantes ont été restaurées et vérifiées. Ne pas repartir du checkpoint 001 ni des chemins de son ancien workspace.

## Ancien point de reprise — historique CP001

# Reprise de l’audit

Lire README.md et checkpoint.json. Ne pas fusionner cette branche d’audit. Aucun fichier opérant du projet n’y est installé. Les noms, SHA et niveaux de revue initiaux sont dans refs-initial.json/csv.

Dans le workspace conservé : lire checkpoints/session.json, checkpoints/inventory-counts.json, checkpoints/resume-delta-20261019T0957Z.json puis agents/*.md/json. Le miroir preservation.git et quant-trade-initial.bundle restent immuables; utiliser analysis.git pour de nouveaux objets. Ne pas exécuter scripts du projet, réinitialiser essais/fenêtres, ouvrir outcomes scellés ou prendre/relibérer un bail.

Si le workspace est absent : ce checkpoint ne contient pas les collectes GitHub brutes ni la sauvegarde Git. Les retrouver avant de prétendre reprendre sans perte. Refaire une collecte distante séparée, comparer SHA par référence au manifeste initial, conserver chaque delta, puis compléter les lectures manquantes. Les sources du dépôt (registres existants, protocoles, notes Git) restent autorités de leur objet; les tables d’audit sont des index de preuves.
