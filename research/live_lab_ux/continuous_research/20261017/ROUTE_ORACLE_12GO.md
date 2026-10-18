# Oracle Always Free → GPT-OSS → Research OS → Live Lab

État : chemin préparé le 17 octobre 2026 ; aucune instance Oracle inspectée, aucun modèle lancé, aucun coût engagé. L’Owner indique une instance créée, stockage gratuit maximal, téléphone uniquement et pas d’accès SSH utilisé.

Mise à jour du 18 octobre : l’Owner a interrogé OCI depuis le **Cloud Shell général**. A1.Flex, 2 OCPU, 12 Go, zéro GPU et plugin **Compute Instance Run Command RUNNING** sont confirmés par ses sorties. La clé de création du 20 septembre diffère de la clé console du 18 octobre. La livraison d’une commande à Ubuntu et l’accès sudo restent à établir. Le script `oracle/run-command-diagnostic.sh` soumet depuis Cloud Shell un diagnostic invité borné, affiche son identifiant puis suit son exécution. Il crée un enregistrement Run Command mais ne change ni packages, services, volumes, clés ou IAM. Un état RUNNING du plugin ne prouve pas à lui seul les permissions de livraison/exécution. Commande CLI vérifiée : `oci instance-agent command create --timeout-in-seconds`, corps source TEXT et cible `instanceId` ; suivi par `command-execution get --command-id --instance-id`. Le script ne recrée pas une commande si l’attente expire : conserver son identifiant et réinterroger l’exécution. Les 30 tentatives espacées de quatre secondes sont bornées ; le temps total dépend aussi des appels OCI.

ECONOMIC_PROGRESS : préparer une production de brouillons causaux qui ne consomme pas le quota Codex, avec admission distincte dans la recherche existante.
REMAINING_BLOCKER : accès à l’instance, configuration effective et faisabilité mémoire/débit inconnus.
EXIT_CONDITION : diagnostic réel, génération locale mesurée, puis intégration factuelle et essai de 24 heures réelles.

## 1. Chemin depuis le téléphone

1. Console Oracle → **Compute → Instances → instance**. Relever **Shape, OCPU, mémoire et image système**. L’allocation de stockage ne donne pas la quantité de RAM.
2. Pour une image compatible, vérifier **Oracle Cloud Agent → Compute Instance Run Command**. Le plugin doit être actif et les droits IAM applicables. Dans les ressources de l’instance : **Run command → Create command → Paste script → Output as text**. Cette voie exécute un diagnostic sans connexion SSH ni port entrant ouvert. La documentation actuelle ne liste pas Ubuntu parmi les images Run Command prises en charge : ne pas présumer sa disponibilité sur cette image.
3. Exécuter seulement le diagnostic `oracle/preflight.sh` de ce dossier ; il ne télécharge, n’installe ni ne modifie rien et n’affiche aucun secret. Le résultat vient de la VM uniquement s’il est exécuté dans cette VM, pas directement dans Cloud Shell.
4. Si Run Command est absent/non disponible, **Cloud Shell**, dans le navigateur Oracle, peut servir de terminal SSH vers l’instance avec sa clé existante. Une connexion console série est une autre voie, mais ne fournit pas automatiquement une session administrateur : l’OS peut demander un mot de passe configuré. Une clé perdue demande une récupération adaptée, sans recréer/supprimer l’instance par défaut.
5. L’installation persistante demande ensuite des droits administrateur dans l’OS. Run Command s’exécute normalement comme `ocarun`, pas comme root ; son bon fonctionnement ne prouve pas l’accès `sudo`. Aucun secret dans les scripts ou sorties Run Command. Provisionner ultérieurement les secrets par un canal dédié, par exemple OCI Vault avec une identité d’instance limitée.

**Cloud Shell sert à administrer. Le modèle et le contrôleur doivent tourner dans Compute, sous systemd.** Cloud Shell est interactif, avec des sessions limitées à 24 h et un délai d’inactivité de 60 minutes. Fermer Safari ne doit pas arrêter Compute.

## 2. Configuration à essayer sur 12 Go

Les métadonnées des fichiers ont été vérifiées, sans télécharger les poids :

| Candidat | Taille exacte | Observation |
| --- | ---: | --- |
| ggml-org, MXFP4 | 12 109 566 624 octets | Référence du moteur ; environ 11,28 Gio avant contexte et OS |
| Unsloth, Q3_K_S | 11 463 894 208 octets | Environ 10,68 Gio ; gain limité, qualité à vérifier |
| Unsloth, Q2_K | 11 468 317 888 octets | Pas plus petit que ce Q3 ; aucune promesse de « modèle 6 Go » |

Révisions et SHA-256 dans `oracle/model-candidates.json`. Ces noms de quantification ne garantissent ni un faible besoin total de RAM ni un débit.

Chemin retenu pour le **pilote** : **llama.cpp CPU natif ARM64**, référence MXFP4 en premier, puis Q3_K_S si nécessaire. Le moteur documente GPT-OSS/MXFP4 sur CPU. Compiler et charger le modèle sur la VM réelle restent à faire. Ollama est une alternative valide ; le choix llama.cpp donne ici un contrôle explicite sur contexte, slots et mémoire.

- Un seul modèle chargé et **une génération à la fois** ; les familles de propositions alternent.
- Contexte initial 2 048 tokens, deux threads si deux OCPU, batch 128 / microbatch 64, raisonnement borné. Mesurer la place du prompt + raisonnement + réponse.
- Mapping mémoire du fichier, sans verrouillage de toute la RAM ; sous pression, le système peut relire le disque. Cela peut dégrader fortement le débit.
- Étudier 4–8 Gio de swap **sur le volume existant** seulement après lecture de l’espace libre ; pas de nouveau volume ni de redimensionnement facturable. Le swap ne transforme pas le disque en RAM rapide.
- Endpoint modèle **127.0.0.1:8080**, accessible au contrôleur local. Les échanges avec le site sont sortants en HTTPS ; pas de port LLM public à ouvrir.

Commande indicative après installation et vérification du fichier, non exécutée ici :

```sh
/opt/quant-ideation/llama.cpp/build/bin/llama-server \
  --model /var/lib/quant-ideation/models/gpt-oss-20b-MXFP4.gguf \
  --alias quant-ideation --host 127.0.0.1 --port 8080 \
  --n-gpu-layers 0 --ctx-size 2048 --parallel 1 --threads 2 \
  --batch-size 128 --ubatch-size 64 --reasoning-budget 128 --jinja
```

La révision du moteur vérifiée est `ea0c4c2c85fb183ec0fbd30a1af4e4275a18a064` ; les options ci-dessus existent dans sa documentation. Cette vérification n’est pas un test d’inférence. Mesurer ensuite temps de chargement, tokens/s, durée par proposition, RAM/swap, erreurs et proportion de réponses exploitables. Arrêter les répétitions en cas d’échec mémoire persistant plutôt que de boucler sur des crashs.

Oracle documente actuellement 2 OCPU / 12 Go pour Always Free et des reprises possibles d’instances inactives. Vérifier les droits réels du compte ; aucune disponibilité H24 garantie par ce document. La licence des poids est gratuite ; API externes, dépassements de quotas et ressources payantes restent des coûts distincts.

## 3. Répartition des composants

```text
VM Oracle Compute : llama.cpp + contrôleur supervisé
  → IdeaDrafts et outbox durables locaux
  → admission contrôlée dans le Research OS GitHub existant
  → événements authentifiés au serveur du Site
  → D1 → SSE → adaptateur → mapper → reducer → scène
```

| Objet | Autorité prévue |
| --- | --- |
| Brouillons non admis, état du pilote, outbox | SQLite local à Oracle, avec sauvegardes à définir dans le quota existant |
| ResearchTask, baux, hypothèses admises, preuves et décisions scientifiques | Branche Research OS actuelle, contrôle par SHA/CAS existant |
| Acceptation des événements et projection live | Serveur Site / D1 ; jamais les commits GitHub comme source live |
| Commandes Start/Pause/Resume du site | Futur journal authentifié et acquitté par le contrôleur |

SQLite ne devient pas une seconde queue scientifique. L’admission crée une tâche canonique seulement après screening/Legacy et attribution d’autorité. Un échec d’envoi au site ne doit pas supprimer une idée persistée. Les brouillons restent explicitement **NON VALIDÉS**, avec mécanisme, contrainte/payeur, objection, sources réellement fournies et origine du mandat. Pas de source récente inventée : les documents doivent être obtenus et datés par un connecteur séparé.

Le contrôleur reprend immédiatement un mandat après la fin d’une génération, tant que campagne, mémoire, disque et mandat le permettent. Les validations consomment indépendamment le backlog. Les contrôles de santé/retry peuvent utiliser des échéances ; ils ne créent jamais de travail fictif. Un seul processus d’inférence est servi sur 12 Go. Réutiliser le modèle pour plusieurs familles ne crée pas une validation indépendante de ses propres idées.

## 4. Raccordement concret vérifié dans le projet

Sources observées :

- Quant UX : `4a6e952debcc443d134be1b1c60eda46d2c09fbf`.
- Site local : `517f510c096e752643c64097b475048cfc0385c1` ; hébergement Cloudflare avec D1 `DB` et capacité MCP.
- Branche `builder/research-os-autonomous-loop-20261015` : `e980d201d3c84d16d7d91fde0d27a06c9a2c3121`, HEAD distant revérifié. Ne pas remplacer ce code par l’ancien Edge Lab.

Points existants dans le dépôt Site :

- `worker/platform-probe.mjs` : POST `/__platform_probe/session` et `/__platform_probe/event`, identité liée à une clé, génération, bail, séquence, déduplication. Les canaris ont un scope de preuve opérationnelle ; réutiliser leur protocole ne constitue pas une autorité de recherche.
- `worker/native-live.mjs` : GET `/api/work/snapshot`, GET `/api/work/events`. Projection native des événements acceptés, sans lecture GitHub.
- `worker/server.mjs` : routage existant, ancien observateur documentaire et MCP à préserver.
- Quant `adapters/platform-native.js`, `core/state-machine.js`, `ui/motion-authority.js` : mapper/reducer/autorité d’animation existants.

**Travail requis avant activation**, distinct d’une simple configuration d’URL :

1. Ajouter au serveur Site un principal dédié à Oracle et un ingress de production, en réutilisant le protocole natif sans usurper les identités des sondes. Les deux identités fixes et l’ancienne clé canari ne sont pas une inscription générique de workers.
2. Préserver le chemin D1/SSE et ses tests. Définir un label d’activité explicite pour l’idéation, par exemple `hypothesis-generation`, et son geste autorisé. Aujourd’hui le mapper n’invente aucun rôle et n’accepte que les activités connues : ne pas étiqueter une génération comme du codage ou une lecture documentaire fictive.
3. Le client Oracle sérialise les séquences d’événements et maintient les heartbeats pendant l’inférence. Le profil serveur actuel a un intervalle par défaut de 2 s et un bail de 6 s ; une boucle réseau dédiée et un profil cohérent sont nécessaires sur CPU lent. Heartbeat = présence uniquement.
4. Start après lancement réel de l’inférence, completion après écriture durable du résultat vérifiable. Le protocole actuel exige à completion un hash SHA-256 de sortie et un code de terminaison ; définir la preuve correspondante à un appel HTTP au modèle. En cas de crash/réseau, réconcilier l’action, le bail et la génération ; ne pas rejouer un ancien start pour simuler du travail.
5. Réconcilier le bail expiré `FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-002`, sans terminer ni supprimer silencieusement le travail. Revoir la politique de refill globale qui renvoie `NOOP_QUEUE_NOT_EMPTY`, et la limite de 12 émissions par frontier. Le backlog de brouillons peut se remplir séparément ; l’admission canonique doit respecter la politique révisée et les autres workers encore actifs.
6. Ajouter un vrai journal de commandes Owner au serveur : le `/owner-toggle` existant est une sonde, pas un contrôle effectif de cette campagne. Oracle peut relever les commandes par HTTPS sortant ; ce contrôle réseau n’impose aucun réveil horaire à la génération. Pause doit être acquittée et définir le sort de l’appel en cours.

Tout cela est **à implémenter et tester**, pas déjà raccordé. Le noyau Economic Look reste éteint en l’absence d’autorité native explicite. Capital réel et live trading restent interdits ; coûts d’inférence externes non engagés.

## 5. Chemins prévus dans la VM

- `/opt/quant-ideation/` : moteur et contrôleur versionnés.
- `/var/lib/quant-ideation/models/` : fichier modèle vérifié par SHA-256.
- `/var/lib/quant-ideation/ideas.sqlite3` : brouillons et outbox du producteur, sans duplicata des tâches canoniques.
- `/etc/quant-ideation/` : configuration ; secrets provisionnés séparément, absents de Git et de Run Command.
- `quant-ideation-model.service` et `quant-ideation-controller.service` : supervision systemd à créer après qualification.

## 6. Séquence d’acceptation

Diagnostic téléphone → accès administrateur qualifié → chargement du modèle et plusieurs idées réelles → boucle locale persistante → admission Research OS → événements natifs → commande Pause acquittée → capture live → pilote de 24 h réelles.

Vérifier arrêt du navigateur, redémarrage du processus/VM, panne réseau, récupération des baux, absence de doublons et marge disque. La qualité se mesure sur des mécanismes distincts et falsifiables, pas sur le seul nombre de cartes. Aucun essai H24 n’est déclaré réussi à l’avance.

## Sources vérifiées

- Oracle quotas : https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Oracle Run Command : https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/runningcommands.htm
- Oracle Cloud Agent : https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/manage-plugins.htm
- Oracle Cloud Shell : https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cloudshellintro.htm
- Oracle connexion Linux : https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/connect-to-linux-instance.htm
- Oracle console série : https://docs.oracle.com/en-us/iaas/Content/Compute/References/serialconsole.htm
- Moteur et CPU : https://github.com/ggml-org/llama.cpp/discussions/15095
- Options épinglées : https://github.com/ggml-org/llama.cpp/blob/ea0c4c2c85fb183ec0fbd30a1af4e4275a18a064/tools/server/README.md
- Métadonnées modèle : https://huggingface.co/api/models/ggml-org/gpt-oss-20b-GGUF?blobs=true
- Métadonnées quantifications : https://huggingface.co/api/models/unsloth/gpt-oss-20b-GGUF?blobs=true
