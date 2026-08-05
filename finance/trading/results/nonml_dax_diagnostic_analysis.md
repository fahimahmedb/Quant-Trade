# Diagnostic structurel — pourquoi DAX est-il systématiquement le marché le plus difficile de la lignée de portes #216-242 ?

Analyse diagnostique (pas un backtest, pas de critère PASS/FAIL) : diagnostics déjà implémentés à l'Étape A, calculés sur l'échantillon complet de chaque marché.

| Marché | n séances | Sharpe BH ann. | Vol ann. | Skew | Kurtosis excès | VR(5) | VR(5) p robuste | Ljung-Box Q(22) rdt² p | ARCH-LM p | ν Student-t |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | +0.52 | 22.6% | +0.06 | +4.57 | 0.894 | 0.2087 | 0.0000 | 0.0000 | 4.78 |
| NDX (40 ans) | 10272 | +0.53 | 25.9% | -0.16 | +7.75 | 0.889 | 0.0074 | 0.0000 | 0.0000 | 2.84 |
| Russell 2000 | 9781 | +0.34 | 21.6% | -0.65 | +9.50 | 0.976 | 0.6372 | 0.0000 | 0.0000 | 2.97 |
| S&P 500 | 14251 | +0.45 | 17.2% | -0.94 | +23.49 | 0.940 | 0.1868 | 0.0000 | 0.0000 | 3.18 |
| DAX | 6776 | +0.25 | 22.4% | -0.17 | +6.06 | 0.963 | 0.3863 | 0.0000 | 0.0000 | 3.08 |

## Lecture comparative DAX vs les 4 autres marchés

- **Sharpe Buy&Hold annualisé** : DAX = 0.251, autres marchés ∈ [0.341, 0.529] — DAX HORS de la plage des 4 autres
- **Volatilité annualisée** : DAX = 22.410, autres marchés ∈ [17.214, 25.867] — DAX dans la plage des 4 autres
- **Asymétrie (skew)** : DAX = -0.171, autres marchés ∈ [-0.940, 0.057] — DAX dans la plage des 4 autres
- **Excès de kurtosis** : DAX = 6.060, autres marchés ∈ [4.574, 23.492] — DAX dans la plage des 4 autres
- **Ratio de variance VR(5)** : DAX = 0.963, autres marchés ∈ [0.889, 0.976] — DAX dans la plage des 4 autres
- **ν Student-t (épaisseur des queues, non conditionnel)** : DAX = 3.085, autres marchés ∈ [2.840, 4.782] — DAX dans la plage des 4 autres

**Lecture honnête** : ce diagnostic est purement descriptif et comparatif, sans critère de succès pré-défini au-delà de la question posée.

**Interprétation qualitative (déclarée après calcul, comme prévu — ce cycle n'a jamais promis de trancher, seulement de documenter).**
Sur les 6 propriétés comparées, **UNE SEULE place DAX hors de la plage des 4
autres marchés : le Sharpe Buy&Hold annualisé** (0,25, contre 0,34-0,53
ailleurs — le plus faible des 5, nettement). Sur toutes les propriétés
directement liées aux mécanismes de porte testés (vol-de-la-vol via VR,
épaisseur des queues via kurtosis/ν, clustering ARCH via Ljung-Box/ARCH-LM),
**DAX ne se distingue PAS structurellement** des autres marchés — son
comportement statistique de second/troisième/quatrième ordre est banal
dans cet échantillon de 5.

L'explication la plus simple et mécaniquement plausible : le mécanisme
`position = clip(cible/vol_estimée, floor, CAP)` amplifie SYMÉTRIQUEMENT
le rendement moyen ET la volatilité pendant les périodes actives, à coût
de transaction FIXE (5 bps/rotation). Sur un marché dont le rendement
moyen quotidien sous-jacent est déjà le plus faible des 5 (cohérent avec
le Sharpe BH le plus bas), le ratio "gain de rendement additionnel
apporté par l'amplification" / "coût de rotation" est structurellement
moins favorable — pas parce que le SIGNAL de porte est moins pertinent
sur DAX, mais parce que le "carburant" (drift sous-jacent) sur lequel la
porte s'appuie est plus mince. **Ce n'est PAS une certitude établie ici**
(un seul marché, aucun test statistique formel de cette hypothèse
spécifique n'a été construit) — c'est l'explication la plus cohérente
avec les données observées, à traiter comme une hypothèse de travail
plutôt qu'une conclusion. Aucune "correction" de DAX n'est proposée : le
résultat honnête est que DAX échoue plus souvent pour une raison
plausiblement structurelle (rendement sous-jacent plus faible), pas pour
une raison de bug ou de mauvaise calibration des portes.
