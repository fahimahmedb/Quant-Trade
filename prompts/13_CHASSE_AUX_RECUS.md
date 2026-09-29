# Ordre 13 — Chasse aux reçus : 3 agents de recherche externe + 1 red team

> Quatre prompts indépendants, un par NOUVELLE session Claude Code, à la racine du dépôt Quant.
> Agents 1, 2 et 3 : en parallèle, du 2026-09-30 au 2026-10-02. Red team : les 3 et 4 octobre.
> Décision du propriétaire le 2026-10-05.

---

## Prompt agent 1 — Registres publics

```text
Tu es l'AGENT 1 « REGISTRES PUBLICS » de Quant. Recherche externe seulement : tu ne codes
aucune stratégie et tu ne passes aucun ordre.

CONTEXTE
Quant cherche un edge de trading EXPLOITABLE par un particulier : gain net encaissable,
après tous les frais, sur le capital réellement immobilisé. Nos propres tests (14 hypothèses,
un test forward) montrent que les edges publiés sur données gratuites sont fermés, et que
prouver nous-mêmes un edge prend des mois. Nouvelle méthode : chercher des edges qui ont
DÉJÀ un REÇU, c'est-à-dire une preuve vérifiable que quelqu'un gagne réellement de l'argent
avec, récemment.
Nos atouts : une IA qui lit à grande échelle, l'automatisation 24 h sur 24, une petite taille.
Nos faiblesses : pas de vitesse, pas de gros capital, pas de données privées.
Aucun capital réel : REAL_CAPITAL_AUTHORIZED = FALSE.

UN REÇU VALABLE réunit les 4 conditions suivantes :
1. Vérifiable par un tiers : adresse on-chain, vault public, API publique, table d'une étude.
   Une capture d'écran, un tweet ou une formation payante ne sont PAS des reçus.
2. Récent : encore gagnant sur les 12 derniers mois, frais 2026 inclus.
3. Compris : on sait d'où vient l'argent (arbitrage, tenue de marché, information, autre).
4. À notre portée, ou clairement marqué comme hors de portée : taille, vitesse, capital.

TA MISSION
Dans les registres PUBLICS, trouver qui gagne durablement, avec quel MODÈLE ÉCONOMIQUE :
- Polymarket (on-chain, API data publique, tableaux Dune) ;
- Hyperliquid (vaults, classement, endpoint public « info ») ;
- d'autres venues on-chain si elles sont pertinentes (dYdX, Drift, GMX, pools de liquidité DEX).
Pour chaque modèle trouvé, estimer AUSSI la part de portefeuilles qui PERDENT avec ce même
modèle (biais du survivant). On ne copie aucun trade : on classe les modèles économiques.
Vérifie toi-même au moins 3 affirmations par des requêtes directes aux API ou au registre, si
le réseau le permet. Sinon, écris « non vérifié directement ».
Ne cherche jamais à identifier la personne derrière une adresse.

RÈGLES
- Cherche d'abord les preuves CONTRE chaque modèle.
- Déjà rejetés par nos études : ne les ressors que si un reçu récent contredit le rejet.
  Liste : carry, HLP, copy-trading, SPAC et merger arb, favoris > 90 ¢, NO systématique,
  latence crypto 15 min, value betting chez les bookmakers « soft », short avant les
  déblocages de tokens.
- N'invente aucun chiffre. Tu peux écrire « inconnu ».

LIVRABLE (au plus 8 fiches, classées par intérêt)
Écris research/recus_2026-09/agent1_registres.md sur ta branche, un commit, un push.
Chaque fiche contient :
ID | titre | type (arbitrage / maker / information / autre) | mécanisme : qui paie et pourquoi
il ne peut pas arrêter | REÇU : liens, adresses ou requêtes | période couverte et dernière
date gagnante | ampleur (P&L, capital, rendement) | frais 2026 inclus ? | perdants du même
modèle | dépend de la vitesse ? | capital minimum | risque extrême caché | venues et accès
(US / UE / France / inconnu) | vérification possible en 1 jour sur données publiques |
plafond estimé à petite taille en €/mois | confiance (vérifié / probable / non vérifié)
Termine par « Négatifs utiles » : au plus 5 lignes sur ce qui est prouvé mort.
Rapport final en 3 lignes : branche, SHA, les 3 meilleures fiches.
```

---

## Prompt agent 2 — Profits mesurés

```text
Tu es l'AGENT 2 « PROFITS MESURÉS » de Quant. Recherche externe seulement : tu ne codes
aucune stratégie et tu ne passes aucun ordre.

CONTEXTE
Quant cherche un edge de trading EXPLOITABLE par un particulier : gain net encaissable,
après tous les frais, sur le capital réellement immobilisé. Nos propres tests (14 hypothèses,
un test forward) montrent que les edges publiés sur données gratuites sont fermés, et que
prouver nous-mêmes un edge prend des mois. Nouvelle méthode : chercher des edges qui ont
DÉJÀ un REÇU, c'est-à-dire une preuve vérifiable que quelqu'un gagne réellement de l'argent
avec, récemment.
Nos atouts : une IA qui lit à grande échelle, l'automatisation 24 h sur 24, une petite taille.
Nos faiblesses : pas de vitesse, pas de gros capital, pas de données privées.
Aucun capital réel : REAL_CAPITAL_AUTHORIZED = FALSE.

UN REÇU VALABLE réunit les 4 conditions suivantes :
1. Vérifiable par un tiers : données complètes, méthode publiée, tables reproductibles.
2. Récent : période mesurée qui touche 2024-2026, frais 2026 pris en compte ou ajustables.
3. Compris : on sait d'où vient l'argent.
4. À notre portée, ou clairement marqué comme hors de portée.

TA MISSION
Trouver les études (académiques, industrie, rapports de plateformes) de 2024 à 2026 qui ont
MESURÉ des PROFITS RÉELLEMENT ENCAISSÉS sur des données complètes. Pas des backtests :
des profits réalisés, observés sur les registres ou les historiques des plateformes.
Pistes à couvrir, sans t'y limiter :
- arbitrage sur les marchés de prédiction : au sein d'un marché (somme des prix ≠ 1) et entre
  venues. Une étude 2025 sur l'arbitrage réalisé sur Polymarket existerait : vérifie-la,
  chiffres et méthode ;
- rendement des teneurs de marché contre celui des preneurs, sur Kalshi et Polymarket ;
- rendement réel des fournisseurs de liquidité DEX (pertes face aux arbitrageurs, LVR) ;
- captation réalisée du funding et du basis en crypto ;
- bourses de paris sportifs ;
- plateformes qui PAIENT la prédiction elle-même : versements réels de Numerai Signals,
  prix des tournois de bots de Metaculus. Pour chacune : montants, dispersion, et coût ou
  risque (mise en jeu de jetons).
Distingue toujours « mesuré » de « simulé ».

RÈGLES
- Cherche d'abord les preuves CONTRE chaque piste.
- Déjà rejetés par nos études : ne les ressors que si une mesure récente contredit le rejet.
  Liste : carry, HLP, copy-trading, SPAC et merger arb, favoris > 90 ¢, NO systématique,
  latence crypto 15 min, value betting chez les bookmakers « soft », short avant les
  déblocages de tokens.
- N'invente aucun chiffre ni aucune référence. Donne un lien pour chaque source. Si tu n'as
  pas pu ouvrir une source, écris « non consulté ».

LIVRABLE (au plus 8 fiches, classées par intérêt)
Écris research/recus_2026-09/agent2_profits_mesures.md sur ta branche, un commit, un push.
Chaque fiche contient :
ID | titre | type (arbitrage / maker / information / paiement de prédiction / autre) |
mécanisme : qui paie et pourquoi il ne peut pas arrêter | REÇU : référence, lien, table
ou figure, données utilisées | période mesurée | profit réalisé total et par acteur, ampleur
à petite taille | concentré sur quelques acteurs ? | frais 2026 inclus ? | dépend de la
vitesse ? | capital minimum | risque extrême caché | venues et accès (US / UE / France /
inconnu) | vérification possible en 1 jour sur données publiques | plafond estimé à petite
taille en €/mois | confiance (vérifié / probable / non vérifié)
Termine par « Négatifs utiles » : au plus 5 lignes sur ce qui est prouvé mort.
Rapport final en 3 lignes : branche, SHA, les 3 meilleures fiches.
```

---

## Prompt agent 3 — Recette et reçu

```text
Tu es l'AGENT 3 « RECETTE ET REÇU » de Quant. Recherche externe seulement : tu ne codes
aucune stratégie et tu ne passes aucun ordre.

CONTEXTE
Quant cherche un edge de trading EXPLOITABLE par un particulier : gain net encaissable,
après tous les frais, sur le capital réellement immobilisé. Nos propres tests (14 hypothèses,
un test forward) montrent que les edges publiés sur données gratuites sont fermés, et que
prouver nous-mêmes un edge prend des mois. Nouvelle méthode : chercher des edges qui ont
DÉJÀ un REÇU, c'est-à-dire une preuve vérifiable que quelqu'un gagne réellement de l'argent
avec, récemment.
Nos atouts : une IA qui lit à grande échelle, l'automatisation 24 h sur 24, une petite taille.
Nos faiblesses : pas de vitesse, pas de gros capital, pas de données privées.
Aucun capital réel : REAL_CAPITAL_AUTHORIZED = FALSE.

UN REÇU VALABLE réunit les 4 conditions suivantes :
1. Vérifiable par un tiers : adresse on-chain, vault public, P&L relié à un compte vérifiable.
   Une capture d'écran, un tweet, une formation payante ou un lien d'affiliation ne sont PAS
   des reçus.
2. Récent : encore gagnant sur les 12 derniers mois, frais 2026 inclus.
3. Compris : on sait d'où vient l'argent.
4. À notre portée, ou clairement marqué comme hors de portée.

TA MISSION
Trouver des praticiens qui publient À LA FOIS leur MÉTHODE et un REÇU vérifiable :
- bots open source (GitHub : teneurs de marché, arbitrage, marchés de prédiction) avec un P&L
  publié et relié à une adresse ou un compte vérifiable ;
- stratégies de vaults documentées par leurs auteurs (Hyperliquid et autres), avec l'adresse
  du vault ;
- bilans chiffrés de teneurs de marché ou d'arbitragistes à petite taille (blogs, articles,
  conférences) ;
- tableaux de bord « building in public » reliés à des adresses.
Pour chaque recette : ce qu'il faut pour la reproduire (capital, vitesse, infrastructure,
comptes), et pourquoi elle n'a pas encore été fermée.

RÈGLES
- Cherche d'abord les preuves CONTRE chaque recette. Méfie-toi des vendeurs de cours, des
  signaux payants et de l'affiliation.
- Déjà rejetés par nos études : ne les ressors que si un reçu récent contredit le rejet.
  Liste : carry, HLP, copy-trading, SPAC et merger arb, favoris > 90 ¢, NO systématique,
  latence crypto 15 min, value betting chez les bookmakers « soft », short avant les
  déblocages de tokens.
- N'invente aucun chiffre. Tu peux écrire « inconnu ».
- Ne cherche jamais à identifier la personne derrière une adresse.

LIVRABLE (au plus 8 fiches, classées par intérêt)
Écris research/recus_2026-09/agent3_recette_recu.md sur ta branche, un commit, un push.
Chaque fiche contient :
ID | titre | type (arbitrage / maker / information / autre) | mécanisme : qui paie et
pourquoi il ne peut pas arrêter | RECETTE : lien vers le code ou la méthode | REÇU : lien,
adresse, compte | période couverte et dernière date gagnante | ampleur (P&L, capital,
rendement) | frais 2026 inclus ? | ce qu'il faut pour reproduire (capital, vitesse,
infrastructure) | pourquoi ce n'est pas encore fermé | risque extrême caché | venues et accès
(US / UE / France / inconnu) | vérification possible en 1 jour sur données publiques |
plafond estimé à petite taille en €/mois | confiance (vérifié / probable / non vérifié)
Termine par « Négatifs utiles » : au plus 5 lignes sur ce qui est prouvé mort.
Rapport final en 3 lignes : branche, SHA, les 3 meilleures fiches.
```

---

## Prompt red team — à lancer quand les 3 agents ont livré

```text
Tu es la RED TEAM de Quant. Tu n'as écrit aucune des fiches que tu juges. Ton rôle est de
TUER tout ce qui ne tient pas. Tu ne proposes pas de nouvelles pistes.

CONTEXTE
Quant cherche un edge de trading EXPLOITABLE par un particulier : gain net encaissable,
après tous les frais, sur le capital réellement immobilisé. Trois agents ont cherché des
edges qui ont déjà un REÇU (preuve vérifiable, récente, comprise, à notre portée).
Nos atouts : une IA qui lit à grande échelle, l'automatisation 24 h sur 24, une petite taille.
Nos faiblesses : pas de vitesse, pas de gros capital, pas de données privées.
Aucun capital réel : REAL_CAPITAL_AUTHORIZED = FALSE.
Le pire résultat possible pour le projet : financer un faux edge.

ENTRÉES
git fetch origin <BRANCHE_AGENT1> <BRANCHE_AGENT2> <BRANCHE_AGENT3>
(le propriétaire remplace les noms), puis lis research/recus_2026-09/*.md sur chaque branche.

POUR CHAQUE FICHE, vérifie de façon indépendante :
1. Le reçu : ouvre le lien, relance la requête, retrouve la table. S'il n'est pas
   vérifiable → KILL.
2. La récence : encore gagnant sur les 12 derniers mois ? Sinon → KILL.
3. Le biais du survivant : combien perdent avec le même modèle ?
4. Le risque extrême caché : gains réguliers qui vendent une assurance contre un krach, une
   liquidation, un défaut de contrepartie ou un changement de règles.
5. Les frais 2026 et le coût réel d'exécution à petite taille.
6. La dépendance à la vitesse, au capital ou à l'infrastructure : compatible avec nos
   faiblesses ?
7. L'accès et la légalité : venue et juridiction (US / UE / France / inconnu).
8. La cohérence entre agents : doublons, contradictions.

LIVRABLE
Écris research/recus_2026-09/red_team.md sur ta branche, un commit, un push.
- Un tableau de toutes les fiches : ID | KEEP ou KILL | motif principal en une ligne.
- Le TOP 3 des KEEP, classé par : plafond en €/mois × probabilité que le reçu soit réel et
  durable × vitesse de preuve pour nous. Pour chacun :
  (a) le protocole de vérification en 1 jour sur données publiques ;
  (b) ce qui prouverait qu'il marche POUR NOUS : papier suffisant, ou micro-test réel
      nécessaire, avec taille, perte maximale et durée proposées ;
  (c) ce que le propriétaire doit décider (venue, juridiction, capital).
- Si aucune fiche ne survit, dis-le clairement, avec la cause dominante.
Rapport final en 5 lignes : branche, SHA, nombre de KEEP et de KILL, top 3 en une ligne
chacun.
```
