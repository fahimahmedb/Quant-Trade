# Quant — recherche continue : audit et options au 17 octobre 2026

Statut : **analyse sourcée + reproduction locale d’un blocage réel**. Aucun service H24 nouveau n’a été déployé. Aucun rappel, état scientifique ou paramètre de production n’a été modifié. Aucun achat/API facturée lancé. Le budget actif reste nul pour les nouvelles dépenses.

## 1. Le blocage concret trouvé

La branche active des cinq workflows est **`builder/research-os-autonomous-loop-20261015`**, observée à **`89ece99da11d04fe725161a6ccc66b80d6d91466`**. Elle est distincte de l’ancienne branche `research/edge-lab-continuous` et de la branche de reconstruction du Live Lab.

L’outil natif des automatisations confirme cinq workflows horaires activés, avec des heures de lancement récentes. Cela prouve des lancements observés, pas la réussite du travail. L’ancienne tâche « Discovery V4.2 » est désactivée. Le Site lui-même n’a aucune automatisation liée. [Relevé borné](ACTIVE_WORKFLOWS.json).

À l’instant de l’audit, la file contient **21 tâches : 20 COMPLETE, 0 READY, 1 CLAIMED**. La réservation restante est `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-002`, génération 1, propriétaire `fundamental_events_workflow`. Son bail a expiré le **16 octobre à 10:10:23 UTC**, sans completion persistée.

J’ai exécuté la fonction pure `derive_refill_task` du code exact de cette branche contre les fichiers exacts : elle renvoie **`NOOP_QUEUE_NOT_EMPTY`**. Le remplissage compte le statut CLAIMED sans résoudre ici l’expiration. Les prompts sélectionnent d’abord des tâches READY. Cette combinaison peut maintenir la file bloquée malgré des réveils réguliers. La règle de reprise existe dans le protocole, mais son application effective à cette réservation n’est pas démontrée. [Reproduction et horloges](CURRENT_OS_PROOF.json).

Autres limites explicites actuelles :

- Une lignée, cinq étapes maximum par réveil, puis arrêt. Un contrôleur peut garder ces unités bornées tout en déclenchant automatiquement la suivante.
- Le steward crée une seule tâche lorsque la file globale est vide, puis s’arrête ; le producteur attend son propre réveil.
- Quatre frontières, chacune limitée à douze émissions : au plafond, la politique impose une mise en veille jusqu’au rafraîchissement Owner. Une durée de vie infinie du serveur ne supprimerait pas ce plafond.
- Le périmètre actuel autorise la recherche documentaire et sa critique ; les expériences économiques et observations prospectives restent non autorisées. Les rendre continues ne les rend pas économiquement validées.
- Les événements du Research OS inspectés sont des fichiers JSON « native-shaped » sur GitHub. Aucun transport HTTP vers l’ingress du Site n’a été trouvé dans ce sous-arbre. Le démarrage inspecté n’indique pas de `ui_activity`. Le flux public du Site observé reste sur le dernier canary technique. Écrire un fichier d’événement ne prouve ni son acceptation par l’ingress ni son rendu.

Le diagnostic antérieur fondé uniquement sur le flux 3D était incomplet : des workflows existent et publient du travail sur une autre branche. Il faut résoudre **continuité, reprise des réservations et livraison native des événements** séparément.

## 2. Ce que H24 doit signifier

Le service reste disponible quand le navigateur et cette conversation sont fermés. Une étape terminée déclenche le travail admissible suivant. Une arrivée de données, un handoff ou une dépendance résolue réveille la file concernée. Un crash provoque une reprise à partir de preuves persistées, sans recommencer aveuglément une expérience.

`IDLE` est un état vivant et honnête lorsque rien d’utile n’est admissible. H24 ne garantit ni calcul IA permanent, ni découvertes rentables, ni absence de panne. Une couverture réellement continue se mesure sur une période réelle et inclut les attentes et incidents.

Un rappel ChatGPT horaire peut rester un recours. Il ne doit pas être l’horloge principale qui autorise chaque étape.

## 3. Les familles d’options examinées

Les sources primaires sont regroupées dans [SOURCES.json](SOURCES.json). « Faisable » signifie compatible avec le besoin architectural ; ce n’est pas une preuve de fonctionnement sur ce compte.

| Piste | Ce qu’elle apporte | Limite et adéquation à Quant |
|---|---|---|
| Machine existante toujours allumée + service supervisé | Processus Python/Node, Python scientifique, Codex CLI, reprise automatique | Meilleure première voie si aucun nouveau coût API n’est accepté. Dépend de l’alimentation, du réseau et des quotas d’abonnement. |
| Petit VPS/VM + même service | Exécution indépendante du téléphone et du chat | Recommandation simple pour un premier pilote autonome. Coût serveur, entretien, stockage et authentification à qualifier. |
| Conteneur/worker permanent managé | Cloud Run worker pool, Render Background Worker ou service équivalent | Vrai traitement de fond ; nécessite une offre qui maintient du calcul, pas simplement un endpoint HTTP. Facturation et volume persistant à vérifier. [S11, S19] |
| Site + Agents API OpenAI, sandbox géré + webhooks | Le Site peut lancer un agent distant et recevoir sa fin ; sessions durables, outils, code, compaction | Voie cloud pertinente et actuelle. Modèles/outils/sandboxes facturés ; accès API et reprise du contrôleur à prouver. Le Site ne porte pas lui-même le calcul scientifique. [S4–S6] |
| Site + Responses/background + outils applicatifs | Réponses asynchrones et orchestration sur événements | Plus de runtime/outils à construire que les agents gérés ; un appel background ne remplit pas automatiquement toute la campagne. [S25] |
| Cloudflare Workflows + Queue/DO + exécuteur | Coordination durable, attentes, retries, alarmes, livraison de messages | Bonne voie événementielle. CPU/étapes par instance limités ; rotation des instances nécessaire à terme. Les bindings ne sont pas actuellement configurés/exposés dans ce Site : ne pas assimiler Cloudflare générique à une capacité Sites déjà disponible. [S7–S9] |
| Cloudflare Containers/Sandboxes | Exécuteur Linux/Python associé au contrôle durable | Faisable avec compte, bindings, stockage et facturation adaptés ; nouvelle intégration à qualifier. [S10] |
| Temporal + workers | Historique durable, reprise, signaux, Continue-As-New | Très robuste pour une campagne longue ; Temporal n’héberge pas automatiquement les activités Python/Codex. Complexité supplémentaire pour une première seule machine. [S12] |
| Trigger.dev | Exécution managée, tâches enchaînées, attentes, retries | Bon compromis si un service tiers et ses coûts sont acceptés. Vérifier le mode de reprise réel et les limites de chaque tâche. [S13] |
| Inngest | Fonctions durables déclenchées par événements, étapes mémorisées | Bon contrôle événementiel ; l’hébergement de chaque fonction/exécuteur reste à définir. [S14] |
| AWS Step Functions/Azure Durable Functions + compute | Orchestration durable avec calcul externalisé | Alternatives valides, davantage de composants/configuration. Une Lambda standard seule reste bornée par invocation. [S20, S21] |
| n8n/Node-RED/Activepieces | Raccordement visuel d’événements et de services | Utile pour collecteurs/handoffs. Le moteur doit être hébergé ; n8n en queue requiert des workers et Redis. Ne crée ni budget IA ni méthode de recherche. [S15] |
| LangGraph/Agents SDK/CrewAI/autres frameworks | Organisation des étapes, mémoire/checkpoints selon framework | Une bibliothèque ne fournit pas une machine H24. Peut s’insérer dans les voies précédentes ; changer de framework ne résout pas seul le blocage observé. [S22] |
| ChatGPT/Codex tâches et automatisations | Exécution cloud à des horaires/événements pris en charge | Déjà en place pour cinq voies. Aucun contrôle exposé ici ne garantit un chaînage durable « terminé → prochain » avec reprise et disponibilité H24. Ne pas promettre qu’une cadence plus courte résout cela. [S16] |
| Workspace Agents déclenchés par API | Déclenchement possible d’agents publiés dans les workspaces éligibles | Piste native conditionnelle au compte, aux droits, jetons et quotas ; disponibilité non vérifiée ici. Pas le même mécanisme qu’une page Site appelant un MCP. [S24] |
| GitHub Actions en jobs chaînés/cron | Jobs reproductibles, artefacts et CI | Pas le premier choix pour un service continu : jobs GitHub-hosted bornés, cron pouvant être retardé ou perdu. Un runner auto-hébergé ramène à la question du serveur permanent. GitHub reste mémoire/audit, jamais bus live de substitution. [S17] |
| IA locale sur machine disponible | Exécution sans facture API distante, éventuellement sans quota fournisseur | Matériel/électricité, qualité et débit à mesurer. Intéressant pour tri/documentation/déterminisme ; pas d’équivalence scientifique garantie avec les modèles actuels. [S23] |
| Navigateur/iPhone, Service Worker, onglet ouvert | Calcul et interactions pendant la vie permise par le navigateur | Inadapté comme garant H24 : suspension/termination et compatibilité de fond. Le service doit continuer lorsque Safari est fermé. [S18] |
| `setInterval`, `waitUntil`, SSE ou WebSocket maintenu ouvert | Vie locale d’une requête/connexion et suivi visuel | Aucun n’est un ordonnanceur durable. `waitUntil` reste limité après réponse/déconnexion. Garder une connexion ouverte ne garantit pas une campagne autonome. [S7] |
| Hébergements gratuits, VM gratuite, crédits d’essai | Possibilité de pilote à coût limité | Capacité, sommeil, arrêt, expiration et récupération à vérifier offre par offre. Exemple documenté : Render Free s’endort après inactivité. Aucun « gratuit H24 garanti » déduit d’un free tier. [S19] |

## 4. Ma recommandation pour ce projet

**Conserver le Site et le Research OS existants ; ajouter un contrôleur de campagne durable et un véritable exécuteur.** Le premier choix dépend du cadre financier :

1. **Abonnement actuel / pas d’API facturée :** machine de confiance existante ou petit serveur, service supervisé et Codex CLI/SDK. La CLI locale se déclare aujourd’hui connectée à ChatGPT ; c’est une évolution par rapport aux anciennes preuves d’authentification bloquée. Je n’ai pas encore exécuté un nouveau tour headless ni vérifié ses quotas. Le login courant n’est pas une identité transférable automatiquement vers une autre machine. L’automatisation par abonnement doit suivre les modes documentés ; le dépôt public ne doit pas recevoir les credentials. [S1–S3]
2. **API facturée acceptée :** Site + Agents API/sandbox géré + contrôleur durable à webhooks. Les nouvelles documentations officielles décrivent cette voie ; elle évite de maintenir soi-même tout le harness d’agent. Elle ne dispense pas du journal de campagne, des reprises et du contrôle des coûts. [S4–S6]
3. **Plusieurs exécuteurs / besoin de résilience plus élevé :** orchestration durable Temporal, Trigger.dev, Inngest ou Cloudflare, après une première tranche fonctionnelle mesurée. Ne pas migrer tout le système pour commencer.

Le coût complet comporte : hébergement + inférence + outils/recherche web + stockage/transferts + données éventuelles. L’abonnement peut éviter une facture API distincte, mais ses quotas peuvent interrompre le raisonnement. H24 du contrôleur et disponibilité continue de l’inférence sont deux engagements séparés. Sans machine disponible et sans coût supplémentaire, je ne peux garantir une nouvelle capacité de calcul permanente.

## 5. Déclenchements automatiques par le Site

Architecture proposée, pas encore installée :

```text
Site : démarrer / suspendre / reprendre une campagne
  → commande persistée et autorisée côté serveur
  → contrôleur durable : état, file, baux, reprise, budget
  → exécuteur de la voie admissible
  → résultat + artefacts + mémoire persistés
  → handoff / prochaine action admissible, déclenché immédiatement
  → événements réels authentifiés → ingress natif → D1 → SSE → reducer → labo
```

Le backend peut déclencher du travail automatiquement sur : fin d’étape, fin de validation, nouvelle donnée documentaire, échéance réelle, dépendance débloquée et incident récupéré. L’iPhone sert au contrôle et à l’observation ; sa fermeture ne doit changer aucun de ces mécanismes.

Le contrôleur doit conserver les rôles indépendants déjà définis. Un exécuteur ne peut pas s’auto-valider en changeant simplement son étiquette. La durée d’un tour reste bornée pour limiter contexte et erreurs ; sa fin donne la main au contrôleur, qui décide du suivant sans rappel humain.

Données minimales : campagne et génération ; tâche/voie et bail ; tentative et statut ; empreinte d’entrée ; références d’artefacts ; réservation/mesure de ressources ; commandes ; événements et outbox de livraison. Un seul propriétaire d’écriture par transition, ou des transactions/CAS sur les objets existants. Ne pas créer un deuxième état canonique concurrent entre GitHub, SQLite et D1 : choisir l’autorité de chaque objet et un seul chemin de publication. GitHub conserve les preuves et contrats ; D1/SSE conserve le chemin live natif.

Les retries sont au moins une fois. Il faut des identifiants stables, réconciliation des effets et déduplication ; aucune promesse d’« exactement une fois » sur un appel modèle ou une expérience externe. Une activité économique dont l’effet est ambigu doit être suspendue/réconciliée, pas rejouée pour faire avancer la file.

## 6. Tranche concrète à exécuter avant toute promesse H24

**A. Réparer le blocage existant.** Relire la branche active fraîche ; inspecter la tâche expirée, ses événements/artefacts et l’état du run avant reprise. Le contrôleur classe un bail expiré en récupération, exclut toute reprise concurrente par génération/CAS, puis reprend la même lignée au dernier effet confirmé ou la marque explicitement bloquée. Ne pas supprimer la tâche ou la déclarer terminée sans résultat.

**B. Remplacer l’attente du rappel par la continuation.** Après completion ou handoff durable, réveiller immédiatement la voie suivante admissible. Après refill, réveiller le producteur dans un nouveau tour indépendant. Conserver les limites par tour ; retirer leur effet de fin de vie de campagne. Prévoir une surveillance indépendante pour les événements perdus et réservations orphelines.

**C. Fixer la politique de frontière.** Le plafond actuel de douze émissions est réel. Proposer une politique de campagne explicite, avec sélection autonome dans des mandats définis, budget, distinction causale/Legacy et critères d’arrêt utiles. Une frontière épuisée ne justifie pas de recycler des variantes. Aucun plafond ni droit scientifique n’est modifié par cet audit.

**D. Brancher l’exécuteur réellement.** Premier tour headless autorisé sur la machine cible, résultat documentaire utile, fin persistée, événement natif accepté et rendu. Vérifier l’accès aux outils de recherche : une CLI authentifiée ne garantit pas les mêmes outils qu’une tâche Work. Gérer quota, renouvellement d’authentification, timeout et perte réseau sans boucler à vide.

**E. Prouver la campagne pendant 24 heures réelles.** Démarrage unique, chat/Safari fermés, aucune relance manuelle. Contrôler :

- au moins une lignée documentaire réellement recherchée, gelée puis critiquée par une voie indépendante ; un rejet est un résultat valide ;
- handoff déclenchant la voie suivante sans attendre l’heure suivante ;
- reprise après arrêt du processus, perte réseau et redémarrage de l’hôte ;
- bail expiré récupéré sans blocage global ni réexécution d’effet déjà confirmé ;
- pause/reprise authentifiées depuis le Site ; aucune nouvelle admission après pause ;
- quotas et ressources mesurés ; `RESOURCE_WAIT`/`AUTH_REQUIRED` visibles si nécessaire ;
- événements réels visibles, déduplication, snapshots/reconnexions sans reprise d’animation passée ;
- chaque attente et chaque incident expliqués ; une impossibilité d’inférence ne doit pas être maquillée en activité de recherche.

Passer un test unitaire ou laisser un processus local survivre quelques minutes ne vaut pas réussite H24. L’environnement de cette conversation n’a pas été qualifié comme hébergement permanent.

## 7. Livrable et limites de cette investigation

Les documents publics prouvent les capacités annoncées des fournisseurs ; ils ne prouvent ni leur activation pour ce compte ni l’uptime de Quant. La reproduction locale prouve le refus du refill sur l’état observé. Les métadonnées d’automatisation prouvent des lancements récents ; elles ne permettent pas d’expliquer seules pourquoi le dernier worker n’a pas achevé sa tâche.

Les seuls changements ici sont les fichiers de cet audit, sur la branche du Live Lab. Les cinq rappels restent inchangés, le Research OS actif reste intact, le Site n’est pas republié et aucun service payant n’est créé. Le prochain livrable utile est la tranche A→D avec un vrai exécuteur, suivie de l’épreuve E, et non un nouvel aperçu 3D ou un autre rappel horaire.
