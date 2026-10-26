# Économie des essais — à coller dans 🟩 B après l'unification

```text
RÈGLES D'ÉCONOMIE DES ESSAIS (propriétaire, applicables dès maintenant, dans les invariants du §3)

Constat : sur les 6 REJECT, 4 sont de vrais échecs (le signal s'inverse ou se concentre hors échantillon) et 1 est dégénéré (H-003). Un seul (le fade des listings HL, SR 1,52, t 1,82) est un REJECT de puissance : la validation couvre 1 an, ce qui exige un SR ≥ 2,64 avec 6 essais. Le goulot est la PUISSANCE du test, plus que le nombre d'essais.

1. Calcul de puissance AVANT de déclarer. Chaque déclaration au registre ajoute :
   expected_sr (source : littérature ou mécanisme, citée), validation_years ou validation_events, et
   expected_t = expected_sr × √validation_years (ou effet/σ × √n_événements). Le seuil vaut required_t(prior_trials + grille).
   Si expected_t < required_t : NE PAS tester. Soit allonger les données (plus d'historique, plus de venues, plus d'événements), soit marquer UNDERPOWERED et passer à l'hypothèse suivante. Zéro essai consommé.

2. Grille minimale. Par défaut, UNE expression, avec ses paramètres fixés par la littérature ou le mécanisme avant les données. Au plus 3 expressions, et seulement avec une justification écrite. Une grille de 6 coûte +0,7 de t requis.

3. Validation consultée une seule fois. Le hold-out d'un jeu de données ne sert qu'une fois par hypothèse. Retester après une modification compte les essais déjà faits. Un jeu de données dont prior_trials ≥ 50 (HL vs dYdX : 50) est BRÛLÉ pour l'historique : seules les données forward ou un nouveau jeu de données sont admis.

4. Priorité aux hypothèses à forte puissance :
   - beaucoup d'événements indépendants par an, ou long historique (≥ 3 ans ramènent le SR requis de 2,64 à 1,52) ;
   - données fraîches (prior_trials = 0).
   Ordre recommandé :
   a) H-001, juste valeur Pinnacle contre sport Polymarket/Kalshi : des milliers d'événements, KPI CLV par pari ;
   b) Kalshi météo, avec juste valeur NWS et mesure des markouts (des centaines de milliers de trades) ;
   c) funding HL contre Binance/Bybit sur archives publiques 2020 → aujourd'hui (nouveau jeu de données, ≥ 4 ans) ;
   d) fin de mois des pensions (déjà filtré sur 119 mois : ne pas retester ; forward seulement).

5. Pas de doublon. Avant toute déclaration, grep du registre sur le mécanisme et le jeu de données. Un même mécanisme sur le même jeu de données garde le même id.

6. Chaque verdict note sa cause : SIGNAL (vrai échec), COÛTS, PUISSANCE (effet positif mais t insuffisant) ou CONCENTRATION. Les REJECT(PUISSANCE) vont dans une liste « à reprendre en forward seulement » dans FAST_RAIL_STATE.md, sans nouvel essai historique.
```

## Décision proposée au propriétaire (non encore en vigueur, relève de Blue)

Ajouter à l'échelle du §4 une voie **`SHADOW_DIRECT`** :
- pour une hypothèse à **1 expression**, aux paramètres fixés par la littérature avant les données, et **UNDERPOWERED** en historique ;
- la stratégie entre directement en shadow papier, sans passer par `CANDIDATE` ;
- elle n'est jugée que par le t-SPRT sur le forward pristine ;
- elle ne consomme aucun essai historique ;
- l'invariant 8 est inchangé : aucun capital, transfert au rail sûr seulement sur `FORWARD_PASS`.

Coût d'une erreur : un slot de shadow papier.
