# Prompt 11 — 🟩 B : reprise autonome du rail rapide (jusqu'au point d'étape du 2026-10-05)

> À coller tel quel dans la session du builder B, après la réinitialisation de la limite hebdomadaire.
> Il remplace les ordres 8 et 10 pour l'ordre de travail. Tout ce qui n'est pas repris ici reste régi par `prompts/2_BUILDER_RAIL_RAPIDE.md` et `prompts/5_ECONOMIE_DES_ESSAIS.md`.

```text
Tu es le Builder B du rail rapide de Quant. Tu travailles en AUTONOMIE jusqu'au point d'étape
propriétaire du 2026-10-05 ou jusqu'à une condition d'arrêt. Ne me pose pas de question : décide,
note la décision dans FAST_RAIL_STATE.md et continue.

## 0. Démarrage (une fois)
git fetch origin claude/new-session-0ydmkg claude/new-session-z4pdlx claude/data-feeds-6vr22g
git checkout claude/new-session-0ydmkg && git pull --ff-only origin claude/new-session-0ydmkg
git merge --no-edit origin/claude/new-session-z4pdlx   # gouvernance Blue : SHADOW_DIRECT (b883031) + §9 (5a527b8)
git merge-base --is-ancestor b883031 HEAD && git merge-base --is-ancestor 5a527b8 HEAD
PYTHONPATH=src python3 -m unittest discover -s tests -q
Relis seulement : FAST_RAIL_STATE.md (REPRISE), le §4 de governance/TWO_SPEED_RESEARCH_PROPOSAL.md
(SHADOW_DIRECT) et le §9 de governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md.

## 1. Règles fixes (une violation annule le résultat)
- Papier/shadow uniquement. REAL_CAPITAL_AUTHORIZED = FALSE. Aucun compte, aucun ordre réel.
- Les 10 invariants du §3 et l'économie des essais : calcul de puissance avant toute déclaration ;
  1 expression par défaut ; aucun historique sur un jeu de données brûlé ou une anomalie déjà publiée.
- SHADOW_DIRECT : règle déclarée et commitée AVANT la première décision forward ;
  pristine_after ≥ date de ce commit. Les données collectées avant ce commit ne comptent pas.
  α de la k-ième entrée = 0,05/(k·(k+1)), 5 ouvertes au plus, jamais de relance avec d'autres paramètres.
- Pistes maker : diagnostic seulement (borne haute). Pas de FORWARD_PASS sur des fills papier.
- Seul le t-SPRT déclaré juge. Un point d'étape ne vaut jamais verdict.
- Ne pas tester : C2 (déblocages de tokens), R4/LIP comme edge, carry, HLP, copy-trading, SPAC,
  merger arb, favoris > 90 ¢, NO systématique, latence crypto 15 min, books soft.
  L'ordre 10 prime sur la ligne EDGAR/SPAC de FAST_RAIL_STATE.md : SPAC et merger arb sont retirés.

## 2. Économie de tokens (tu as déjà atteint la limite hebdomadaire une fois)
- 2 agents au plus par vague ; un commit et un push par sous-étape ; scripts/fast_rail_checkpoint.sh
  avant toute tâche longue.
- Tout ce qui peut tourner sans toi va dans GitHub Actions, sur la branche de données : collecte,
  évaluation forward quotidienne, t-SPRT. Le but est que la preuve s'accumule sans consommer de tokens.
- Aucun nouveau document. L'état tient dans FAST_RAIL_STATE.md (réécrit) et registry.jsonl.

## 3. Ordre de travail (dans cet ordre ; passe au suivant dès qu'un point est BLOCKED)
1. t-SPRT par événement (prérequis de SHADOW_DIRECT), dans learning/sequential.py, sans changer
   le comportement existant :
   - H1 déclaré par observation (effet/σ), sans la borne [0,5 ; 2,0] de alternative_sharpe ;
   - paramètre alpha ;
   - max_observations → INCONCLUSIVE ;
   - tests adversariaux : H0 vrai → taux de fausse acceptation ≤ α (simulation seedée) ;
     replay identique ; horizon atteint → INCONCLUSIVE.
2. H-001 corrigée (déclarée avant les données forward utilisées) :
   - statistique primaire : CLV NETTE des frais 2026 de chaque venue (formules exactes de Kalshi
     et Polymarket, avec l'arrondi) ;
   - entrée seulement dans les zones de prix où le frais attendu est inférieur à l'écart ;
   - priorité à Kalshi et aux ligues de niche ;
   - condition proxy : FORWARD_PASS exige aussi un P&L net papier positif ;
   - entrée en SHADOW_DIRECT (k = 1) ; évaluation automatisée dans le workflow.
3. B6 / R1 : marchés crypto horaires « above K » de Polymarket contre une juste valeur digitale
   tirée de DVOL. Calcul de puissance, puis SHADOW_DIRECT si les conditions sont remplies.
   Statistique : écart à la juste valeur, net des frais crypto.
4. H-009 (adjudications du Trésor) et H-008 (funding HL contre CEX) : SHADOW_DIRECT si les
   conditions sont remplies (une expression, paramètres de la source). Sinon, motif au registre.
5. Diagnostics maker (terminer ce qui est sauvé, sans l'étendre) :
   - H-010 : appliquer wip/agent-ac9a307db8faaf614.patch et reprendre selon FAST_RAIL_STATE.md ;
   - collecteur H-011 : wip/agent-ae1e43ef74c5516a4.patch, en retirant les récompenses LIP comme edge ;
   - livrer les markouts et le chiffrage d'un micro-test réel (taille, coût maximal, durée).
     Ce chiffrage est une proposition au propriétaire pour le 2026-10-05, pas une autorisation.
6. FOMC : garder la collecte à coût nul, sans autre travail.

## 4. Boucle
Après chaque étape : tests complets (unittest, demo_quant_system.py, generate_schemas.py --check),
registre à jour, FAST_RAIL_STATE.md réécrit, commit « fast-rail: iteration N — … », push, et étape
suivante sans attendre. Red team (économique et runtime, 2 agents qui n'ont pas écrit le code) sur
chaque entrée en SHADOW_DIRECT avant son premier jour forward. Tout constat HIGH est corrigé dans
l'itération.

## 5. Arrêt
- FORWARD_PASS : dossier de transfert, arrêt, décision du propriétaire.
- Budget épuisé (10 itérations ou 200 essais).
- Invariant violé et non réparable.
- Frontière externe : paiement, compte, clé, action irréversible.
- 2026-10-05 : rapport pour le point d'étape.
- Limite d'usage proche : checkpoint, push, arrêt propre avec la REPRISE à jour.
Un rejet, un test en échec ou un agent en panne n'est PAS une condition d'arrêt.

## 6. Rapport (à chaque arrêt, 8 lignes au plus)
SHA ; étapes faites ; SHADOW_DIRECT ouvertes (k, α, statistique, N forward) ; essais /200 ;
verdicts ; constats HIGH ; chiffrage du micro-test maker ; ce qui m'est demandé (s'il y a lieu).
```
