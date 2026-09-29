# Prompt 9 — Blue : amendement SHADOW_DIRECT (échelle de preuve du rail rapide)

> À coller dans la session **🟪 BLUE gouvernance** (celle qui a adopté la proposition le 2026-09-25), ou dans toute autre session Claude Code de gouvernance.
> Une seule session courte, un seul commit, aucun nouveau document.

---

Tu es **Blue**, gouverneur de Quant. Ta tâche est unique et bornée : **statuer sur l'amendement `SHADOW_DIRECT`** de l'échelle de preuve du rail rapide et, s'il passe les vérifications, l'inscrire. La décision de principe vient du propriétaire ; ton rôle est de la vérifier et de l'écrire.

## Pourquoi cet amendement

Aujourd'hui, l'échelle (§4 de la proposition) exige de passer par `CANDIDATE`, c'est-à-dire une validation historique, avant `SHADOW`. Or plusieurs hypothèses sont **UNDERPOWERED en historique** : l'historique ne peut pas trancher, même si l'edge est réel. C'est le cas de H-008 (funding HL contre CEX), de H-009 (adjudications du Trésor, `expected_t` 0,99 < 1,96) et des pistes R2 à R4 de l'étude praticiens. Ces hypothèses ne peuvent donc jamais être observées, ou poussent le builder à brûler des essais sur des backtests sans puissance. Le forward pristine est le vrai juge, et il ne consomme aucun essai historique.

## Lire, et seulement ceci

1. `QUANT_NORTH_STAR.md` : §1, §7 et §10.
2. Depuis `origin/claude/new-session-kfwf1b` :
   - `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` (§9 Rail C) ;
   - `governance/TWO_SPEED_RESEARCH_PROPOSAL.md` (§3 et §4) ;
   - `governance/FAST_RAIL_BUILDER_PROMPT.md` (§4) ;
   - `prompts/5_ECONOMIE_DES_ESSAIS.md`.
3. Depuis `origin/claude/new-session-0ydmkg` :
   - `src/quant/learning/sequential.py` (le t-SPRT actuel) ;
   - les entrées H-008 et H-009 de `research/fast_rail/registry.jsonl`.

## Texte proposé

> **`SHADOW_DIRECT`** (amendement du <date>) : entrée en `SHADOW` sans passer par `CANDIDATE`, si toutes ces conditions sont réunies.
> 1. **Une seule expression.** Ses paramètres sont fixés par une source citée ou par le mécanisme, et écrits au registre avant toute donnée.
> 2. **Historique sans puissance.** Soit `expected_t` < `required_t` est documenté au registre, soit l'historique n'existe pas.
> 3. **Déclaration avant la première décision forward.** On y fixe :
>    - la statistique de test (P&L net, CLV, markouts…) ;
>    - l'effet H1, égal à l'effet de la source × 0,5 (même réduction que `SHRINKAGE`) ;
>    - l'horizon maximal.
>    `pristine_after` doit être postérieur ou égal à la date du commit de la règle.
> 4. **Multiplicité forward.** Le α du t-SPRT vaut 0,05 / M, où M est le nombre cumulé de stratégies entrées en `SHADOW_DIRECT` depuis l'amendement ; M n'est jamais décrémenté. Au plus 5 stratégies `SHADOW_DIRECT` peuvent être ouvertes en même temps.
> 5. **Statistique proxy.** Si la statistique de test n'est pas le P&L net (CLV, markouts), `FORWARD_PASS` exige en plus un P&L net papier positif sur la même période.
> 6. **Sortie.**
>    - Frontière de rejet du t-SPRT atteinte : `REJECT(FORWARD)`.
>    - Horizon atteint sans décision : `INCONCLUSIVE`.
>    - Jamais de relance sur le même forward avec d'autres paramètres.
> 7. **Coût.** 0 essai historique ; `MAX_DECLARED_TRIALS` n'est pas consommé.
> 8. **Capital : inchangé.** Aucune autorité de capital. Un `FORWARD_PASS` produit un dossier de transfert au rail sûr, et c'est le propriétaire qui décide.

Point technique connu, à vérifier : `alternative_sharpe(None)` renvoie le plancher 0,5. Or le t-SPRT actuel travaille sur des rendements quotidiens annualisés. Une statistique par événement (CLV ou markout par pari) demande donc un H1 déclaré et un test indexé par événement.

## Vérifier (oui ou non, avec une ligne de justification chacune)

1. L'amendement ne change ni la North Star, ni `REAL_CAPITAL_AUTHORIZED = FALSE`, ni les 10 invariants du §3, ni aucun artefact figé.
2. Il ne permet pas de choisir un paramètre en regardant le forward (invariant 6).
3. La multiplicité des tests forward est contrôlée : α / M cumulatif et plafond.
4. Une statistique proxy ne peut pas produire seule un `FORWARD_PASS`.
5. Il est implémentable avec le t-SPRT actuel. Sinon, décris l'écart en une ligne pour le builder, sans modifier le code.

## Décider

- **Si tout est oui**, ou si la seule correction nécessaire tient en une ligne (dans ce cas, fais-la) :
  - dans `governance/TWO_SPEED_RESEARCH_PROPOSAL.md` §4, ajoute la ligne `SHADOW_DIRECT` au tableau et place le texte ci-dessus sous le tableau ;
  - dans `governance/FAST_RAIL_BUILDER_PROMPT.md` et `prompts/2_BUILDER_RAIL_RAPIDE.md` §4, ajoute la même ligne, avec un renvoi au §4 de la proposition ;
  - dans `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` §9, ajoute une ligne : « Amendement SHADOW_DIRECT adopté le <date> (α forward = 0,05/M, 5 slots au plus) : voir §4 de la proposition. »
- **Sinon** : n'écris rien. Donne au propriétaire le point qui échoue et la correction nécessaire, en 5 lignes au plus.

## Git

- `git fetch origin claude/new-session-kfwf1b`, puis, sur ta branche (celle que la session impose) : `git merge --ff-only origin/claude/new-session-kfwf1b`. Si l'avance rapide est impossible : `git merge --no-edit origin/claude/new-session-kfwf1b`.
- Un seul commit, un push. Ne fusionne vers aucune autre branche et ne force-push rien.

## Rendu

Au plus 8 lignes : la décision, les 5 vérifications, le nom de ta branche et le SHA du commit.

---

# Ensuite : à coller dans 🟩 B, une fois connus la branche et le SHA de Blue

```text
Blue a adopté l'amendement SHADOW_DIRECT (branche <BRANCHE_BLUE>, commit <SHA>).
git fetch origin <BRANCHE_BLUE> && git merge --no-edit origin/<BRANCHE_BLUE>, puis vérifie que <SHA> est dans l'historique.
Applique le §4 amendé :
- Si Blue a signalé un écart sur le t-SPRT, implémente-le d'abord, avec son test.
- Pour chaque hypothèse UNDERPOWERED qui remplit les conditions (une expression, paramètres tirés d'une source, déclaration avant les données), déclare-la en SHADOW_DIRECT avec sa statistique de test, un effet H1 réduit de 50 %, un horizon maximal et α = 0,05/M.
- Au plus 5 stratégies SHADOW_DIRECT ouvertes en même temps.
```
