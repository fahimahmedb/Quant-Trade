# Labo de recherche continu — branche indépendante

Construction autorisée par l'Owner le 10 octobre 2026 : « en full autonomie construit ce labo […] il faut pas que ça détruise notre N ». Base vérifiée : `09ba64b8bee1419076ec8a30f8d75a916932c2ba`. Le [rapport révisé](https://github.com/fahimahmedb/Quant-Trade/blob/fae3be50549d8b023c3e9a42eb14a51613bcb8c4/research/mission_audit_2026-10-10/REPORT.md) et ses sources restent conservés. Son ancien statut d'attente concernait la phase précédente ; cette nouvelle instruction autorise la construction.

[Voir le panneau et la prochaine décision](STATUS.md). [Pause/reprise persistante](https://github.com/fahimahmedb/Quant-Trade/edit/research/edge-lab-continuous/research/edge_lab/CONTROL.json) : mettre `paused` à `true` ou `false` puis enregistrer sur cette branche. Le contrôle est lu avant chaque travail. Désactiver « Poursuivre la recherche Quant » arrête aussi les réveils. Aucun autre scheduler de recherche n'est créé.

## Ce qui fonctionne et ce que cela apprend

| Recommandation | Raccord concret | Information attendue |
|---|---|---|
| Programme économique conditionnel | Questions ZF → EURUSD → HL ; sources/états et réveils précis, rejets conservés | Quel travail est accessible et peut changer une décision ? |
| Paquet de données complet | Droits/coût/horloge requis avant réservation ; accès manquant distinct d'un rejet | Lever un verrou réel, sans achats ou comptes automatiques |
| Contrat résultat/décision | Gel immuable, une réservation par protocole, voies/benchmarks/incertitude et apprentissage | Comprendre ce que le résultat permet de décider |
| Continuité minimale | État atomique + verrou, CAS GitHub, scheduler existant, vue générée, reprise/pause persistante | Ne pas reconstruire le contexte ou exécuter deux fois |
| Ressources/modèles | Métadonnées déterministes, contexte de la seule question ouverte, cache de preuves ; Claude sur question distincte | Une décision utile par dépense de contexte, sans audit en boucle |

La recherche autonome traite accès, sources primaires, contradictions et choix de test sur événements. Elle peut enregistrer de nouveaux mécanismes et exécuter un runner local qualifié, figé et réservé. Une absence de travail admissible produit IDLE/BLOCKED ; l'activité de l'IA n'est pas une preuve économique. Il n'y a actuellement aucun alpha établi.

Les protocoles historiques sont **référencés**, pas recopiés ou édités. F1 fermé, negative-risk KILL et B2/B4 rejetés ne peuvent repartir par renommage. EURUSD conserve ses 433 jours planifiés, trois expressions/six chemins, fenêtre et gel ; l'ancien harnais reste sur son SHA. Son admission exige capture complète aveugle, rapprochement des expositions/artefacts, réservation originale atomique et environnement qualifié. Une adaptation de lancement doit conserver ces gates : le générique refuse de fabriquer un substitut de ce protocole. ZF reste sans BBO/droits/prix exact ; HL sans hôte qualifié attesté. Ces dépendances ne sont pas résolues par le déploiement du labo.

## N et multiplicité

`N` observations et `M` essais sont deux comptes distincts. Le labo ne réduit pas les fenêtres, ne compte pas les instruments/routes corrélés comme autant de jours indépendants et ne modifie aucun seuil de Sharpe/t ou niveau alpha historique. 40 essais déclarés = 36 B2 + 4 B4 pour le même panel ; le registre incomplet et le M effectif restent UNKNOWN. Les 54 entrées FastRail ne deviennent pas un nombre d'essais indépendants. Les expositions publiques et privées inconnues de l'audit restent référencées.

Qualifier une source ou lire un protocole n'ajoute pas un backtest. Tout résultat public utilisé pour sélectionner est enregistré comme exposition/méthode avec période et limites. Une future confirmation historique est bloquée lorsque l'historique d'expositions du dataset est inconnu. Un nouveau fournisseur ne rend pas une période vierge. Exploration, validation, observation prospective et capital sont séparés ; aucun résultat n'est automatiquement rebaptisé alpha.

Les variantes/chemins effectivement prévus sont chargés conservativement avant la lecture. Leur dépendance reste explicite, sans inventer un M effectif moindre. Un look est unique par protocole, indépendamment du fingerprint/fournisseur. Un crash ou timeout reste consommé/UNKNOWN_OUTCOME, sans retry économique. L'exploration sur données déjà exposées conserve ses charges ; la collecte prospective ne permet pas des looks intermédiaires opportunistes.

`trial_charges` est un compte conservateur de chemins réservés, **pas** un M statistiquement indépendant : exprimer le nombre de mécanismes/variantes, leurs dépendances et la règle de sélection dans le protocole. Les scénarios de coûts joints, contrôles logiciels et sorties de diagnostic ne sont pas autant de tests indépendants imposant un Sharpe plus fort. Le labo ne calcule aucun seuil à partir de ce compteur ; les seuils legacy sont conservés. Une hausse légitime de multiplicité après davantage de sélections ne doit pas être effacée.

## Exécution et reprise

```sh
python scripts/edge_lab.py status
python scripts/edge_lab.py next
python scripts/edge_lab.py tick --actor manual
python scripts/edge_lab.py pause --reason 'Owner pause'
python scripts/edge_lab.py resume --reason 'Owner resume'
python scripts/edge_lab.py serve --port 8765
```

Le serveur local `http://127.0.0.1:8765` affiche l'état et sauvegarde pause/reprise locale. Pour piloter les prochaines sessions distantes, publier le contrôle sur GitHub ; le lien du panneau fonctionne sans service web hébergé. Aucun hébergement payant ni panneau public prétendument déployé.

Le worker économique générique suit `evidence → family → freeze → reserve → publication GitHub → execute → reçu → décision`. Les commandes prennent des packets JSON. Protocoles : mécanisme, qui paie, dataset canonique, fenêtre, expressions/chemins, unité indépendante, benchmark, coûts, horloge, droits primaires, décision par issue, politique de multiplicité et runner SHA256. Les packets d'outcomes requièrent un look déjà réservé. `execute` relit l'autorité distante et publie RUNNING contre le parent exact avant lancement ; le perdant d'une course n'exécute pas. Après lancement, il publie le reçu ; une course de publication conserve le reçu local et laisse la réservation distante consommée, à rapprocher sans replay.

Le code qualifié s'exécute sans shell ni secrets hérités, sous timeout. Le hash ne constitue pas un bac à sable contre du code malveillant : admission/revue du runner nécessaire. Aucun runner de trading/broker, capital ou API payante n'est installé. La pause empêche les nouveaux lancements ; un runner déjà lancé reste borné par son timeout. Les seuils économiques viennent du protocole, jamais d'un objectif arbitraire de Sharpe.

Les primitives `quant.state.write_json` et `ResearchTask` sont réutilisées. Le package historique autonomous_research importe son pipeline à l'import ; l'adaptateur charge uniquement son fichier runtime pour éviter de démarrer des dépendances non qualifiées. Aucun boot du `QuantSystem` ancien. Le journal critique est un état JSON atomique vérifié avec chaîne de hashes ; il ne répare pas silencieusement une ligne de ledger tronquée. Git conserve les versions. État/counters/preuves ne sont pas remis à zéro lors d'une reprise.

Avant une lecture/revue coûteuse, `claim-question IDENTITE --actor ACTEUR` prend la question. Publier ce claim avec CAS avant raisonnement : un second hôte ne répète pas la même revue. `decide` reçoit son `claim_id`. Une lease expirée conserve les sources/coûts et demande rapprochement, sans recommencer aveuglément.

## Scheduler, coûts et limites actuelles

Scheduler réutilisé : `6ac978ecda1081918fba4d76dee437f4`, « Poursuivre la recherche Quant ». Son ancien prompt FX est remplacé avant activation. À chaque réveil : lire contrôle/état distants, exécuter le petit tick de métadonnées, puis traiter seulement une question économique réellement nouvelle/admissible. Une question résolue revient uniquement sur nouveau fait. Les sources lues sont mises en cache dans STATE avec URL/version/passage/limite. Aucun quota d'essais, cible de rendement ou rythme imposé de backtests.

Le workflow de cette branche vérifie les garanties et fait un tick metadata sur modifications code/contrôle. Il n'a pas de cron : GitHub exécute les crons sur la branche par défaut. Les commits de heartbeat ne déclenchent pas une nouvelle boucle. Le workflow data-feeds/H001 existant conserve son périmètre ; ce labo ne relance ni collecte H001 ni évaluation concurrente. Cette exclusion ne certifie pas l'activité réelle d'un autre hôte.

Le polling de l'automatisation implique un réveil de modèle, même si le travail est mécanique. Le coût/modèle de ce réveil n'est pas sélectionnable ni mesuré ici ; ne pas annoncer « zéro tokens » ou un routage moins cher déjà installé. Les contexts se limitent au contrôle, résumé d'état et dossier pertinent. Le code ne lance aucune API LLM. Claude indisponible avant le 13 octobre selon l'Owner : rien n'est simulé ni bloqué pour l'attendre. Toute revue future reçoit une question distincte et conserve coût disponible, défaut vérifié et décision modifiée.

Budget Owner global : NON FOURNI. Achats autorisés : zéro. Les bornes 120 secondes/2 MiB de payload par opération sont techniques, modifiables, pas un budget inventé de recherche. CPU/durée instrumentés couvrent les opérations locales suivies et le runner, pas toute la machine/facture. Tokens, trafic réseau total, temps humain et coût des modèles sont NON MESURÉS. Un plafond tokens renseigné sans compteur provoque arrêt BUDGET_UNMEASURED ; les plafonds connus survivent aux reprises. Les données volumineuses/collectes requièrent une capacité et une enveloppe documentées avant admission.

Tests : `PYTHONPATH=src python -m unittest discover -s tests -p 'test_edge_lab*.py'`. Vérifications synthétiques de concurrence réelle Git/local, reprise, pause, budget, expositions inconnues, freezes et absence de double look. Ce sont des contrôles logiciels, aucun nouveau test économique. Aucun changement de défaut, fusion, suppression ou capital/live.

État vérifié le 10 octobre à 16:34 UTC : scheduler existant activé et prompt exact relu ; CI [38068124875](https://github.com/fahimahmedb/Quant-Trade/actions/runs/38068124875) réussie avec 30 tests, cycle et état publiés. Premier reçu du worker de recherche horaire non observé ; l'API de lancement immédiat renvoie HTTP 404 avant invocation. Activation du timer et liveness du worker restent des preuves différentes. Ce blocage/point de reprise est conservé dans CHECKPOINT/STATE ; aucun second scheduler n'est créé pour le masquer.
