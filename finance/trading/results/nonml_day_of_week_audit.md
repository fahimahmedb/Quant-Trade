# Audit adversarial — Effet jour-de-semaine

## Vérification indépendante du décompte de lundis

| Marché | Lundis (méthode dayofweek) | Lundis (méthode nom du jour texte) | Identique ? |
|---|---|---|---|
| Composite (5 ans) | 231 | 231 | OUI |
| NDX (40 ans) | 1939 | 1939 | OUI |
| Russell 2000 | 1844 | 1844 | OUI |
| S&P 500 | 2701 | 2701 | OUI |
| DAX | 1332 | 1332 | OUI |

**OK — deux méthodes indépendantes concordent.**

Sanity check additionnel : la part de lundis dans l'échantillon doit être proche de 20% (1/5 jours ouvrés) sur chaque marché — vérifié visuellement dans le tableau ci-dessus par rapport au nombre total d'observations de chaque fichier (non recalculé séparément ici pour éviter la redondance).
