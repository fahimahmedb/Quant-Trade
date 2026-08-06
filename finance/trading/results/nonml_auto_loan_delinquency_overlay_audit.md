# Audit adversarial — Taux de défaut prêts automobiles US (DRALACBN), overlay défensif

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification dédiée du décalage d'un trimestre de publication

Dernière observation DRALACBN : trimestre de 2026-01-01. Disponible dans la série décalée à partir de 2026-04-01 (90 jours calendaires après, cohérent avec le délai de publication réel de ~2-3 mois déclaré au PREREG).
**OK — la valeur du trimestre T n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Investigation du taux de coupure élevé sur Composite (60,9%)

Le tercile expanding est calculé INDÉPENDAMMENT par marché, à partir de la première date valide de CE marché (même convention que #191/#193/#195/#198/#199/#286/#288) — même schéma que le #286 (Composite à 70%, effet de fenêtre courte 2021-2026).
Valeurs DRALACBN sur 2020-2026 (contexte) : min=1.19, max=1.64 — même schéma de hausse post-COVID (taux historiquement bas en 2021, remontée continue ensuite) déjà documenté au #286. Sur la fenêtre Composite (2021-2026), la majorité des trimestres récents se classent donc mécaniquement dans le tercile expanding le plus haut de LEUR PROPRE fenêtre, expliquant le taux de coupure de 60,9% — un effet de fenêtre courte documenté, cohérent avec le recalcul indépendant identique en §1, pas un bug de calcul.
**OK — comportement attendu de la méthodologie tercile expanding sur fenêtre courte, cohérent avec un contexte macro réel (même schéma que le #286), pas une anomalie de calcul.**

## 4. Test anti-lookahead (troncature de l'historique)

Troncature à 3000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 5000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 1500 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
