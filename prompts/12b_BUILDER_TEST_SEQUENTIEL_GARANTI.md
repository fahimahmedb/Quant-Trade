# Ordre 12b — 🟦 B2 (nouvelle session) : test séquentiel à garantie d'α pour les pistes forward

> À coller tel quel dans une NOUVELLE session Claude Code, à la racine du dépôt Quant.
> Tâche unique et bornée. Aucun autre travail.

```text
Tu es le Builder B2 de Quant. Avant d'écrire du code, tu dois COMPRENDRE le contexte ci-dessous.

## Contexte (à lire et à comprendre)
Quant est un système de recherche quantitative en papier/shadow. Aucun capital réel :
REAL_CAPITAL_AUTHORIZED = FALSE. Son objectif final est la croissance nette du capital
après frais réels.
QUESTION PRINCIPALE : « Cette stratégie peut-elle produire un gain net ENCAISSABLE, après
tous les frais, sur le capital réellement immobilisé, avec une exécution plausible ? »

Le rail rapide teste des stratégies sur des données forward jamais vues. Les stratégies
entrées en SHADOW_DIRECT sont jugées par un test séquentiel : on regarde les données à chaque
nouvel événement, et on s'arrête dès que la preuve est décisive. Le taux de faux passages de
la k-ième stratégie ouverte doit rester ≤ α_k = 0,05/(k·(k+1)) ; pour H-001, α = 0,025.

Le test actuel, event_sequential_test dans src/quant/learning/sequential.py, est un t-SPRT
« plug-in » : volatilité estimée au fil de l'eau, plancher déclaré, bornes de Wald approchées.
L'audit Astra du 2026-09-29, vérifié par Blue, établit que son α N'EST PAS GARANTI sous
dépendance (plusieurs matchs d'un même soir, d'une même ligue) ni sous queues épaisses. Un
faux FORWARD_PASS est l'erreur la plus coûteuse du projet : il enverrait une fausse piste
vers le capital.

Première utilisatrice : H-001. On calcule une CLV nette par match (prix de clôture de la
venue − prix d'entrée − frais, en points de probabilité), comprise dans [−1, 1]. L'effet H1
déclaré vaut 0,00475, avec σ déclarée ≈ 0,05 (H1/σ = 0,095 ; environ 806 matchs attendus
avec le t-SPRT si l'edge est réel).

Lis seulement :
- QUANT_NORTH_STAR.md, §1 ;
- CLAUDE.md, « Integrity invariants » ;
- le §4 de governance/TWO_SPEED_RESEARCH_PROPOSAL.md (SHADOW_DIRECT) ;
- src/quant/learning/sequential.py et tests/test_event_sequential.py ;
- research/fast_rail/h001/forward.py (la fonction evaluate, pour l'interface).
Base : git fetch origin claude/new-session-0ydmkg, puis une branche de travail tirée de
origin/claude/new-session-0ydmkg (celle que la session impose).

## Tâche
Ajouter à sequential.py, sans modifier les fonctions existantes :
anytime_valid_mean_test(values, lower, upper, alpha, beta, h1_mean, max_observations)
- Un e-processus « testing by betting » pour une moyenne bornée (Waudby-Smith et Ramdas,
  2023, « Estimating means of bounded random variables by betting »). Mise prévisible,
  par exemple aGRAPA ou une mise plug-in tronquée, choisie et justifiée par toi.
- ACCEPT_EDGE quand la richesse contre H0 (moyenne ≤ 0) atteint 1/α.
- REJECT_EDGE quand la richesse contre H0' (moyenne ≥ h1_mean) atteint 1/β.
- INCONCLUSIVE à max_observations.
- La garantie ne doit supposer ni l'indépendance, ni une variance connue : seulement des
  valeurs dans [lower, upper] et une espérance conditionnelle ≤ 0 sous H0. Écris cette
  hypothèse dans la docstring.
- Fonction pure : la même histoire donne toujours le même verdict (crash et replay sûrs).
- Tous les paramètres sont fixés dans le code AVANT les données. Aucun réglage sur le forward.

## Validation (obligatoire, simulations seedées, dans tests/)
1. Sous H0 : taux de faux ACCEPT ≤ α, sur au moins 20 000 chemins par scénario :
   - i.i.d. normal tronqué ;
   - queues épaisses (Student t3 tronqué) ;
   - pertes rares (beaucoup de petits gains, quelques grosses pertes) ;
   - chocs communs par soirée (5 à 10 matchs corrélés, ρ = 0,3) ;
   - dérive de volatilité.
   Fais la même mesure pour l'ancien t-SPRT et rapporte ses taux, sans le corriger.
2. Sous H1 (effet 0,00475, σ 0,05) : puissance et nombre médian de matchs jusqu'à la
   décision, comparés au t-SPRT.
3. INCONCLUSIVE à l'horizon ; replay identique ; valeur hors bornes → erreur.

## Interdits
Ne touche ni forward.py, ni une autre stratégie, ni le registre, ni la gouvernance. Aucun
capital, aucune clé. Aucun nouveau document : les résultats vont dans la docstring, les
tests et le message de commit.

## Livraison
Un commit, un push sur ta branche. Rapport en 6 lignes :
- SHA ;
- faux ACCEPT par scénario (nouveau test / ancien) ;
- puissance et matchs médians sous H1 ;
- mise retenue et pourquoi ;
- limite restante ;
- recommandation d'horizon pour H-001.
B branchera la fonction dans forward.py (ordre 12).
```
