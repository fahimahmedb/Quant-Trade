# Audit adversarial — Overlay levé post-drawdown extrême

## Test sur série synthétique (résultat attendu connu par construction)

Jours de levier attendus (choc initial jour 30, re-déclenché jusqu'au jour 49 tant que le max roulant contient le niveau pré-choc, dernière extension +20j) : [30, 31, 32]...[66, 67, 68]
Jours de levier observés : [30, 31, 32]...[66, 67, 68]
**OK — logique de détection/fenêtre conforme à la pré-registration (le re-déclenchement prolongé est un comportement PRÉVU du design, pas un bug).**

**Interprétation du FAIL du backtest principal** : sur les 5 marchés réels, lever l'exposition juste après un choc amplifie le risque de POURSUITE de la baisse (les chocs de marché ne sont pas suivis d'un rebond systématique à court terme — mécanisme similaire au reversal titre du cycle #5, également en échec net). Ce n'est pas un artefact de mesure : les MDD de l'overlay sont systématiquement pires que Buy&Hold sur les 5 marchés.
