# Audit adversarial — les cycles sans entrée de backlog (#477)

**Recalcul par une route différente** : découpage du backlog par
`split("\n## ")` au lieu du générateur du #464, recherche de mention
**ligne à ligne** au lieu du texte entier, présence des fichiers par
`os.scandir` au lieu de `Path.glob`.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| cycles complets re-dérivés | **13** | 13 | **concordant** |
| couverts autrement | **0** | 0 | **concordant** |
| non couverts | **13** | 13 | **concordant** |
| avec un `_result.md` | **9** | 9 | **concordant** |
| avec un `_audit.md` seul | **3** | 3 | **concordant** |

## Le contrôle qui compte : zéro couvert, est-ce crédible ?

Un `0 / 13` est un résultat extrême. **Un audit qui se contenterait de
le confirmer par la même logique ne prouverait rien.** Contrôle en sens
inverse : je prends des noms de rapports que le backlog **cite**
certainement, et je vérifie que ma recherche les trouve.

- rapports `_result.md` **trouvés** dans le backlog par la même
  recherche : **145**
  - `nonml_amihud_illiquidity_tilt_pit_universe_result.md`
  - `nonml_autocorrelation_regime_overlay_result.md`
  - `nonml_beta_dispersion_vol_targeting_overlay_result.md`
  - `nonml_breadth_confirmation_overlay_result.md`
  - `nonml_breadth_vol_targeting_overlay_result.md`

> **La recherche fonctionne.** Elle trouve **145** rapports
> cités ailleurs ; si elle n'en trouve **aucun** parmi les 13, c'est
> que ces 13 ne sont réellement cités nulle part. **Le `0` n'est pas
> un défaut de méthode.**

## Effets de bord du backtest

- écritures : **1** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire.**

L'ajout de l'entrée collective au backlog est fait **hors du script**,
à la main, et signalé dans le rapport — un script qui réécrit le backlog
serait exactement le genre d'effet de bord que ces cycles traquent.

## Verdict

**CONCORDANT** — **5/5** grandeurs se retrouvent par
une route indépendante.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date
> de son exécution (cycles #436-#438).