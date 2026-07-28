# Audit adversarial — Leaders 52-semaines + overlay union SMA200∪52w-high indice

Fraction SMA200 (signal A) : 75.4%
Fraction 52w-high (signal B) : 54.6%
Fraction union (A∪B) : 75.4%

Jours où B est actif MAIS PAS A : 0
**CONFIRMÉ — le signal 52w-high (B) est un SOUS-ENSEMBLE STRICT du signal SMA200 (A) sur cet historique : être à ≥95% du plus haut 252j implique quasi-systématiquement être au-dessus de la SMA200. L'union A∪B est donc mathématiquement IDENTIQUE à A seul.**

**Explication du résultat** : c'est pourquoi le résultat du backtest #41 (Sharpe +1,08, rendement +287,6%, MDD -27,6%) est chiffre pour chiffre IDENTIQUE au cycle #33 (Leaders + SMA200 seul) -- ce n'est ni une coïncidence ni un bug de copier-coller, mais une conséquence mathématique directe de la relation d'inclusion entre les deux signaux sur cette donnée. **L'union n'apporte donc rigoureusement AUCUNE valeur ajoutée par rapport au SMA200 seul dans cette combinaison** -- résultat honnête, différent de l'union calendaire du #21 (ToM∪Halloween) où les deux fenêtres NE se recouvrent PAS et où l'union apportait un vrai gain.
