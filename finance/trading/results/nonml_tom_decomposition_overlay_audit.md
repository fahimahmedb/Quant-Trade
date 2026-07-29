# Audit adversarial — Décomposition du turn-of-month

## 1. Recalcul indépendant des deux masques (balayage séquentiel via datetime standard)

| Marché | Écart masque A (fin de mois) | Écart masque B (début de mois) |
|---|---|---|
| Composite (5 ans) | 0 | 0 |
| NDX (40 ans) | 0 | 0 |
| Russell 2000 | 0 | 0 |
| S&P 500 | 0 | 0 |
| DAX | 0 | 0 |

**OK — les deux masques sont confirmés par recalcul indépendant.**

## 2. Vérification : les deux masques sont-ils disjoints (pas de double comptage) ?

| Marché | Jours communs A∩B (doit être 0) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — les deux sous-fenêtres sont disjointes, cohérent avec la construction du #8 (union sans chevauchement).**

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Variante A stable | Variante B stable |
|---|---|---|
| Composite (5 ans) | OUI | OUI |
| NDX (40 ans) | OUI | OUI |
| Russell 2000 | OUI | OUI |
| S&P 500 | OUI | OUI |
| DAX | OUI | OUI |

**OK — comportement stable (le calendrier n'est pas une donnée de marché, aucune fuite possible par construction).**

**Lecture économique** : la décomposition confirme précisément l'hypothèse de la littérature du turn-of-month (Ariel 1987, Lakonishok & Smidt 1988) — l'edge est concentré dans les derniers jours du mois (Variante A, PASS 4/5), pas dans les premiers jours du mois suivant (Variante B, FAIL 3/5). Les deux sous-fenêtres sont vérifiées disjointes (aucun chevauchement), confirmant que le #8 (PASS 4/5) combine bien deux fenêtres distinctes dont une seule porte véritablement l'edge.
