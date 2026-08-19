# Audit indépendant — #521, littéraux périmés du script du #485

Route distincte du backtest : import direct du module cible (pas
de regex sur texte source) pour recalculer `n_irrep`, `n_rep` et le
pourcentage depuis son dictionnaire `V` ; comparaison de `HEAD~1` à
`HEAD` via `git show` pour les seuils de prédiction figés.

## Recalcul depuis le module importé, vs publié dans le rapport

| Grandeur | Recalculée | Publiée | Accord |
|---|---|---|---|
| irréparables | 8 | 8 | **OUI** |
| réparables | 9 | 9 | **OUI** |
| % réparables (dette actionnable) | 52.9 % | 52,9 % | **OUI** |

## Les seuils de prédiction figés — inchangés par le commit de réparation

- seuils avant (`5915dbb~1`) : ['len(irrep) >= 5', 'len(rep) >= 8']
- seuils après (`5915dbb`) : ['len(irrep) >= 5', 'len(rep) >= 8']
- identiques : **OUI**

**PASS** — la route indépendante (import direct du module) reproduit les 3 grandeurs publiées, et les seuils de prédiction figés du #485 sont confirmés intacts par comparaison git directe.
