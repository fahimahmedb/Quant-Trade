# Proposition : recherche à deux vitesses

Statut : **PROPOSÉE**. Le propriétaire doit l'accepter avant qu'elle prenne effet.
Elle ne modifie ni `QUANT_NORTH_STAR.md`, ni la frontière paper/shadow, ni aucun gel existant (Gate A V4, P0, première verticale).

## 1. Le problème

| Constat | Mesure |
|---|---|
| Rapport documentation / code sur Blue | environ 44 000 lignes de markdown pour 10 000 lignes dans `src/` |
| Documents de gouvernance et de handoff | 185 fichiers, dont plus de 60 créés le 2026-09-21 |
| Idées testées sur des données forward (jamais vues) | 0 |
| Première réponse économique de la voie Form 4 | environ 3,6 ans, estimation de la spec figée elle-même |
| Blocage actuel | un « Route-1 mutation pack » de la Gate B, sans lien avec l'économie |

Aujourd'hui, une seule procédure de très haute assurance, conçue pour le capital et l'hôte de production, s'applique aussi à la recherche papier. La recherche en hérite la lenteur sans en retirer de protection utile, puisque la recherche papier n'engage aucun capital.

## 2. La proposition : deux rails, une seule North Star

| | **Rail SÛR** (lent) | **Rail RAPIDE** (accéléré) |
|---|---|---|
| But | Qualifier ce qui peut un jour toucher du capital | Trouver vite des candidats d'edge et les soumettre à des données forward |
| Périmètre | P0 / Form 4, Gate B, hôte cible, première verticale, tout passage au capital réel | Recherche papier/shadow sur tout autre jeu de données ou marché |
| Autorité | Gouvernance Blue actuelle (inchangée) | Le builder décide seul, dans les invariants du §3 |
| Preuves | Sceaux, digests, revues Astra indépendantes | Tests, journal d'essais, red team par vague |
| Documentation | Inchangée, mais plafonnée (voir §5) | **Un seul** fichier d'état vivant, `FAST_RAIL_STATE.md`, et un registre JSONL |
| Capital | Seul rail pouvant un jour demander une autorisation | **Jamais.** Au mieux, le rail produit une *candidature* pour le rail sûr |
| Cadence | Par jalon | Par itération, de quelques heures à quelques jours |

Le rail rapide n'est pas « moins honnête » : il garde tous les invariants économiques qui coûtent peu. Il abandonne la cérémonie, c'est-à-dire les sceaux, la chaîne de réceptions et les revues de revues, parce qu'une erreur y coûte au pire une fausse piste sur un ledger papier.

## 3. Invariants non négociables sur les deux rails

1. **Une seule timeline causale** : aucune donnée future dans un signal. La recherche et le Desk utilisent le même chemin de code.
2. **Aucune donnée fabriquée** : provenance, horodatage d'observation et empreinte pour chaque jeu de données.
3. **Comptabilité des essais** : chaque expression testée est déclarée *avant* de toucher les données et comptée dans le budget de tests multiples du jeu de données (mécanisme `prior_trials` existant). Un essai non déclaré invalide le résultat.
4. **Coûts réalistes** : spread, frais, funding et roll imputés. Le verdict est établi net de coûts.
5. **Book idempotent et redémarrable** : aucune double écriture après un crash.
6. **Hold-out forward intouchable** : seules les données postérieures à `pristine_after` peuvent faire évoluer le cycle de vie d'une stratégie.
7. **Légalité** : la porte `desk/compliance.py` s'applique ; les pratiques interdites restent interdites.
8. **Aucun capital réel** sur le rail rapide, quel que soit le résultat.

## 4. L'échelle de preuve du rail rapide

| Niveau | Condition d'entrée | Qui décide | Coût d'une erreur |
|---|---|---|---|
| `IDEA` | Une ligne au registre : hypothèse, mécanisme économique, données, falsification prévue | Le builder | Nul |
| `EXPLORE` | Discovery sur l'historique, grille déclarée et comptée | Le builder | Un essai consommé |
| `CANDIDATE` | Validation hors échantillon : t de l'alpha net ≥ seuil corrigé du nombre d'essais, stabilité par sous-période, coûts inclus | Le builder, après la red team de la vague | Un slot de shadow |
| `SHADOW` | Tourne sur le ledger d'évaluation avec les données forward du relais (`sync-feeds`) | Automatique | Nul (papier) |
| `FORWARD_PASS` | Test séquentiel (t-SPRT) accepté sur des données forward *pristine*, avec au moins N événements indépendants (N déclaré à l'entrée en `SHADOW`) | Automatique, puis audit indépendant | — |
| **Transfert** | Dossier de candidature remis au rail sûr | **Le propriétaire** | — |

Le rail rapide s'arrête au transfert. Le rail sûr seul décide s'il y a lieu de qualifier davantage, puis de demander une autorisation de capital.

## 5. Plafonds anti-bureaucratie

- **Rail rapide** : aucun nouveau fichier de gouvernance. L'état tient dans `FAST_RAIL_STATE.md` (réécrit, jamais dupliqué), le registre `research/fast_rail/registry.jsonl` et les messages de commit.
- **Rail sûr** : un document par décision réelle. Candidat, puis final, remplace le candidat, qui part dans `archive/`. Les points de reprise de contexte sont réécrits en place, pas datés et empilés.
- Un document qui ne change ni le code, ni les données, ni une décision n'est pas un progrès et n'est pas créé.
- Le rangement (`archive/`) est rejoué à chaque clôture de jalon du rail sûr.

## 6. Mesures de progrès du rail rapide

| Métrique | Pourquoi |
|---|---|
| Hypothèses testées par semaine (discovery → verdict) | Vitesse de recherche |
| Stratégies en `SHADOW` et jours forward accumulés | Accumulation de preuve réelle |
| Taux de rejet et motif (signal, coûts, capacité, données) | Apprentissage |
| Délai attendu jusqu'au verdict par candidat (`expected_sessions_to_accept_if_true`) | Priorisation |
| P&L du ledger d'évaluation par manchon | Sanction économique |

## 7. Conditions d'arrêt du rail rapide

Le rail rapide itère jusqu'à l'une des conditions suivantes :

1. **Transfert** : un candidat atteint `FORWARD_PASS`. On s'arrête pour la décision du propriétaire.
2. **Budget** : le budget d'itérations ou d'essais déclaré au lancement est épuisé.
3. **Épuisement** : il ne reste dans le backlog aucune hypothèse testable avec les données accessibles, et chaque idée restante demande une ressource payante ou une clé.
4. **Violation d'intégrité** : un invariant du §3 est violé et n'est pas réparable dans l'itération.
5. **Frontière externe** : accès, paiement, action irréversible, contrainte juridique.
6. **Demande du propriétaire.**

Un échec de test, une hypothèse rejetée ou un agent en panne **ne sont pas** des conditions d'arrêt.

## 8. Rangement associé

Cette proposition s'accompagne d'un rangement du dépôt (voir `governance/CLEANUP_MANIFEST_PROPOSED.md`) :
- 89 documents remplacés ou clos sur 215 sont à déplacer dans `archive/` sous le même nom, et l'historique Git est conservé ;
- rien n'est supprimé ;
- les fichiers lus par le code, les tests ou la CI restent en place.

Le rangement n'est **pas exécuté** : il touche l'autorité du rail sûr et attend la validation du propriétaire.

## 9. Décision demandée au propriétaire

- [ ] Accepter les deux rails et les invariants du §3.
- [ ] Accepter l'échelle de preuve du §4, en particulier : le rail rapide ne touche jamais au capital.
- [ ] Fixer le budget de lancement du rail rapide, par exemple 10 itérations ou 200 essais déclarés.
- [ ] Valider le rangement (`governance/CLEANUP_MANIFEST_PROPOSED.md`) et fusionner le prompt du builder (`governance/FAST_RAIL_BUILDER_PROMPT.md`).
