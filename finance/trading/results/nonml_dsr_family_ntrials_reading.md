# Lecture DSR alternative — #131, n_trials par FAMILLE (cycle #133, INFORMATIF)

PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu — répond à la question ouverte du #116, méthode fixée dans le PREREG avant calcul.

Lignes classifiées : 131 (backlog #0 à #130, avant le candidat #131 lui-même).

## Répartition par famille

| Famille | Nombre de lignes |
|---|---|
| volatilite_autoreferentielle | 37 |
| momentum_tendance | 31 |
| calendaire_saisonnier | 20 |
| breadth_dispersion_titre | 20 |
| choc_microstructure | 7 |
| autre | 7 |
| macro_externe | 7 |
| evenementiel_fondamental | 2 |

**Nombre de familles distinctes peuplées : 8**

## DSR du #131 — officiel (n_trials=125, brut) vs alternative (n_trials=familles)

| Convention | n_trials | SR0 (journalier) | DSR |
|---|---|---|---|
| Officielle (Règle 9e, compte brut de lignes) | 125 | 0.0802 | 0.0003 |
| Alternative (nombre de familles distinctes) | 8 | 0.0449 | 0.5121 |

**La convention alternative NE fait PAS passer le DSR>0,95 (reste sous le seuil malgré la réduction de n_trials).**

**Ce résultat NE change PAS le verdict Règle 9 officiel du #131 (reste FAIL sous la convention n_trials=125, seule officiellement adoptée). Reste soumis à l'utilisateur : la partition en familles ci-dessus est UNE classification défendable parmi d'autres (cf. limite reconnue dans le PREREG), pas LA réponse définitive à la question ouverte du #116.**
