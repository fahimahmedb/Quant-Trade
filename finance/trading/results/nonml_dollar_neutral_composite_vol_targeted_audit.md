# Audit — Sleeve dollar-neutre composite redimensionné par sa vol (Piste C)

## 1. Recalcul indépendant de la position vol-target (boucle pure, écart-type manuel)

- Écart max sur les 2907 séances : 1.22e-14
- **OK**

## 2. Vérification du décalage causal (séance 1475)
- Position officielle à t=1475 : 0.681638
- Position recalculée à partir de la fenêtre [t-20, t-1] uniquement : 0.681638
- **OK — la fenêtre de vol exclut bien le rendement du jour t**

## 3. Anti-lookahead (troncature à 1453 séances)
- Écart max position sur la zone valide, pleine série vs série tronquée : 0.00e+00
- **OK — aucune fuite**

## Verdict global : **CONFORME**
