# Audit adversarial — Leaders 52-semaines + overlay accélération signal

## Test anti-lookahead (mutation du ratio moyen au rebalancement SUIVANT)

Décision au rebalancement 27 avant mutation du futur : normal
Décision au rebalancement 27 après mutation de avg_ratio[28] : normal
**OK — décision inchangée, aucune fuite (ne dépend que du passé/présent).**

Nombre de rebalancements testés : 55, régime accéléré détecté 28 fois.
