# Clarification Owner — flux d’idées continu

Objectif ajouté : production d’idées décorrélée de la vitesse de validation, backlog accepté, aucun réveil horaire comme déclencheur principal. Préserver les quotas Codex autant que possible. Proposition documentaire, non activée.

## Accès et modèles

Un modèle ne fournit pas un service de lancement permanent. Codex peut construire/lancer un programme qui appelle des modèles conversationnels ; ces appels utilisent l’accès et la facturation de leur fournisseur. Les mécanismes officiels de partage de l’abonnement ChatGPT examinés imputent les requêtes admissibles à l’allocation Work/Codex. Ils ne donnent pas un nouveau quota de chats classiques. L’API a une facturation séparée de l’abonnement.

Candidats à mesurer :

- **gpt-oss-20b local** pour l’idéation volumique : pas de tokens Codex ni de facture API à la requête, mais machine, mémoire, énergie, débit et qualité à qualifier. La possibilité documentée de tenir dans 16 Go avec quantification adaptée n’est pas une promesse de débit élevé, notamment avec plusieurs contextes.
- **GPT-5.6 Terra via API** pour une idéation conversationnelle plus simple à héberger ; coût API distinct. **GPT-5.6 Luna** peut être évalué pour classement/extraction/tri moins coûteux. Aucun de ces choix n’a encore été évalué sur les idées Quant.
- **Abonnement ChatGPT partagé** : possible pour certains accès documentés, mais ne satisfait pas à lui seul l’objectif d’épargner le quota agentique. Aucun accès officiel vérifié ici ne permet de lancer indéfiniment les chats classiques sous un quota séparé garanti.

## Flux proposé

Un ordonnanceur logiciel supervisé entretient plusieurs générateurs de familles distinctes. Chaque slot disponible prend immédiatement un nouveau mandat admissible ; la fin d’un appel remplit ce slot, sans délai artificiel horaire. Les conversations ont des contextes courts et une mémoire durable commune filtrée. Le nombre de slots est mesuré et borné par les ressources réelles.

`Générateurs → IdeaCards non validées → déduplication/Legacy → réserve priorisée → recherche documentaire → challenge indépendant → intégration`

Le résultat d’un générateur n’attend pas la validation du précédent. Chaque idée conserve mécanisme, payeur/contrainte, ancrage documentaire disponible, objection fatale, statut non validé et parent de mandat. Aucune source inventée. Le backlog peut croître, avec suivi des coûts et du nombre d’idées distinctes ; sa taille n’est pas un résultat scientifique. Ne pas retirer les contrôles d’indépendance ni transformer un brouillon en hypothèse gelée sans screening.

Les plafonds actuels de refill et le verrou global READY/CLAIMED doivent être révisés dans une politique de campagne concrète avant activation : garder les unités de travail bornées, autoriser la production indépendante, récupérer les baux expirés, et préserver tous les droits scientifiques applicables. Aucun changement de ces règles n’est exécuté dans cette note.

Codex reste le constructeur/mainteneur. Le contrôleur déterministe orchestre ; il n’a pas besoin d’appeler un grand modèle pour chaque dispatch. Les gestes du labo restent déclenchés par l’activité réelle de chaque producteur/exécuteur.

## Mesure avant engagement

Comparer les candidats sur idées causalement distinctes, taux de doublons/erreurs, qualité documentaire et coût par idée retenue. Mesurer débit, disponibilité et quota consommé. Aucun flux ne peut être garanti sans interruption face aux pannes, limites ou ressources épuisées.

Exemple budgétaire, non prévision : Terra est affiché à 2 USD/M tokens entrants et 12 USD/M sortants. Au débit moyen de 60 générations/h, avec 1 000 tokens entrants et 400 tokens sortants facturés chacune, cela représenterait environ **9,79 USD/jour par générateur**, hors recherche web, raisonnement supplémentaire, stockage, hébergement et remises/cache. La production continue n’est donc pas synonyme de coût négligeable. Aucun appel API facturé n’a été lancé.

Sources officielles vérifiées le 17 octobre 2026 :
- https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites
- https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://openai.com/index/introducing-gpt-oss/
