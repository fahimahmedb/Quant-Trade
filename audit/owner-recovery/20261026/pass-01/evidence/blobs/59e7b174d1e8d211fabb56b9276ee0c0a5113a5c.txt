# Stratégie de co-gérance effective Claude–Codex — A2

Date : 2026-10-08. Statut : stratégie opérationnelle de co-gérance ; aucune décision d’Owner, activation, autorité économique ou de fusion n’est créée.

## 1. Principe

Claude et Codex sont co-gérants à parts égales. Aucun des deux n’est le chef permanent de l’autre. Une demande d’un agent est une proposition : l’autre peut l’accepter, la contester ou la remplacer par un contre-projet motivé.

L’équilibre ne se mesure ni au nombre de messages, ni aux tokens consommés, ni aux publications mécaniques. Il se mesure à l’origine des décisions substantielles, des contradictions utiles, des priorités et des actions effectivement prises.

Avant toute décision importante, chacun formule une proposition indépendante lorsque cela apporte une information nouvelle. Le désaccord est conservé comme mécanisme normal de réduction des angles morts ; il n’est ni effacé par le pilote, ni transformé en attente indéfinie.

Le pilotage alterne par lot borné. Le pilote ordonne le lot ; le contrôleur le contredit avant exécution. Le pilote ne peut ni étendre son mandat au lot suivant, ni remplacer unilatéralement l’ordre de travail choisi par l’autre agent.

Chaque agent peut inscrire et prendre directement une tâche utile dans la file, sans attendre une permission de l’autre, sous réserve des dépendances, de l’autorité applicable et de la contre-lecture prévue. La priorité va à la valeur économique nette paper/shadow et au pouvoir de falsification, non à l’activité documentaire.

`IDLE` reste légitime lorsqu’aucune tâche indépendante à valeur nette positive n’est due. Le watchdog peut réveiller un agent ou signaler une attente ; il ne choisit jamais les priorités et ne crée aucune tâche de remplissage.

## 2. Première décision autonome de Codex

Codex fixe son ordre de travail immédiat :

1. arbitrer le triage Astra Q17-A/C4, en contrôlant les classes de J-1 à J-9, la voie « fournir les preuves sans substitution » et la décision de ne pas modifier `build_result` sans défaut démontré ;
2. contre-lire Q15 puis Q22/C2 avant toute intervention d’Owner sur la VM, avec contrôle des commandes existantes, des blobs, des limites fail-closed et de la condition E §5(f) ;
3. terminer Q21/B1 en lecture seule, hors A2, puis proposer la prochaine expérience weather paper/shadow présentant la meilleure valeur d’information économique sans `t0`.

Claude peut contester cet ordre par une objection précise ou un contre-projet, mais ne peut pas le remplacer unilatéralement. Codex applique la même limite lorsque Claude pilote un lot.

## 3. Règle de fonctionnement symétrique

Pour chaque lot : proposition du pilote, contradiction du contrôleur, résolution écrite des objections, puis exécution. Tout changement de portée ou nouvelle donnée adverse rouvre le contrôle.

La publication, les SHA-256, l’inventaire Git et les statuts sont automatisés autant que possible. Ils ne donnent aucun avantage de gouvernance à l’agent qui les exécute.

Si un agent prend le lead à la place de l’autre, l’autre le signale en une ligne avec la référence et reprend une initiative substantielle. Aucun silence, oubli, accès d’interface plus direct ou rôle de publication ne vaut transfert d’autorité.

Les éléments réservés à Owner, l’indépendance d’Astra et les limites fail-closed restent inchangés. Cette stratégie organise le travail autonome autorisé ; elle n’étend aucune autorité.
