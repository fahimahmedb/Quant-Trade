# Audit — sauvegarde du P&L des 10 PASS restés invérifiables

## 1. Non-régression — dix résultats publiés testés contre leur code

Chaque `results/nonml_<nom>_result.md` est comparé **octet à octet** avant et
après ré-exécution. Une différence signifierait que le résultat publié n'est plus
reproductible par son propre script.

- fichiers identiques : **10 / 10**
- fichiers différents : **0**
- comparaison impossible : **0**


**CONFORME — les dix résultats sont reproduits à l identique.**

Ce contrôle valait d'être fait pour lui-même : dix résultats publiés à des
dates diverses, dont certains avant les corrections des #375-#404, se
reproduisent exactement. L'ajout du `savez` n'a rien perturbé, et les
corrections intermédiaires avaient bien été rejouées.

## 2. Production effective des `.npz`

- `.npz` produits : **10 / 10**

| Candidat | Longueur | Séances à exposition > 1,0× |
|---|---|---|
| `dispersion_trend_vol_targeting_overlay` | 1385 | 22.38 % |
| `momentum_breadth_vol_targeting_overlay` | 1133 | 53.66 % |
| `momentum_dispersion_trend_and_overlay` | 1385 | 32.13 % |
| `multimarket_breadth_vol_targeting_overlay` | 1254 | 56.54 % |
| `net_breadth_vol_targeting_overlay` | 1385 | 44.40 % |
| `santa_vol_targeting_overlay` | 10252 | 1.70 % |
| `sma200_breadth_vol_targeting_overlay` | 1186 | 54.97 % |
| `sma200_momentum_breadth_and_overlay` | 1133 | 52.52 % |
| `weakness_breadth_vol_targeting_overlay` | 1385 | 0.00 % |
| `winners_trend_vol_targeting_overlay` | — | schéma panier |

## 3. Couverture du balayage du #415

| | Avant (#415) | Après (#416) |
|---|---|---|
| candidats mesurés | 33 | **42** |
| détectés non mesurés | 29 | **20** |
| dont portant un PASS | 10 | **0** |

Les **dix** PASS que le #415 laissait en suspens sont désormais mesurés. Les 20
candidats encore non mesurés portent tous un FAIL — leur activation n'est donc
pas une question ouverte de la même nature.

## 4. Porte neutralisée ou porte rare ? — discrimination par mesure

Le seuil d'activation de 2 %, repris du #410, est un **filtre**, pas un verdict :
il ne distingue pas une porte *neutralisée* par le plancher du vol-targeting
d'une porte *rare par construction*. La distinction se tranche par une mesure
directe — le P&L de l'overlay diffère-t-il de celui de Buy & Hold ?

### `santa_vol_targeting_overlay`

- séances à porte ouverte : **174 / 10252** (1.70 %)
- séances où le P&L diffère de Buy & Hold, hors coût d'entrée : **203**
- rendement total : overlay **+27985.2 %** contre Buy & Hold **+25465.6 %**

**Porte RARE, pas neutralisée.** L'overlay agit bien lorsqu'il s'ouvre :
les deux séries de P&L diffèrent, et l'écart de rendement est mesurable.
Ce candidat est donc **écarté** de la liste des « PASS vides » — sa rareté
est un choix de conception, pas une neutralisation.

### `weakness_breadth_vol_targeting_overlay`

- séances à porte ouverte : **0 / 1385** (0.00 %)
- séances où le P&L diffère de Buy & Hold, hors coût d'entrée : **0**
- rendement total : overlay **+132.5 %** contre Buy & Hold **+132.4 %**

**Porte NEUTRALISÉE.** Le P&L est strictement identique à celui de
Buy & Hold : l'overlay ne prend jamais de position effective. Le PASS ne
mesure que cette inactivité.

### Ce que ce contrôle corrige dans le critère du #415

Le #415 déclarait « PASS vide » tout candidat sous le seuil de 2 %. Appliqué
mécaniquement, ce critère aurait requalifié une stratégie calendaire dont la
fenêtre ne dure que quelques séances par an — alors qu'elle agit réellement
quand elle s'ouvre. **Le seuil sert à sélectionner les cas à examiner, pas à**
**les juger** ; c'est exactement pourquoi le pré-enregistrement du #415 imposait
une confirmation par lecture, et c'est ce qui a évité l'erreur ici.

## Verdict de l'audit

**CONFORME.**

Aucune requalification n'est appliquée : conformément aux pré-enregistrements
du #415 et du #416, c'est une opération distincte à déclarer.
