# Audit indépendant — #530, témoin (permutation + négatif/positif) de D528

Route distincte du backtest : dénombrement par grep externe, fenêtre structurelle (paragraphe) au lieu de la fenêtre fixe de 400 caractères, seed de permutation différente (530).

## Recompte externe de la population

- sections (`grep -c '^## Backlog #'`) : **350** (backtest : 350, accord : OUI)
- radicaux (`ls | wc -l`) : **1039** (backtest : 1039, accord : OUI)
- occurrences de marqueur, somme des `grep -o -F | wc -l` : **164** (backtest : 164, accord : OUI)

| Marqueur | grep -o -F \| wc -l |
|---|---|
| « rétracté » | 35 |
| « FAUSSE » | 3 |
| « n'est pas un défaut » | 1 |
| « contredit » | 22 |
| « réfuté » | 103 |

## Taux structurel (fenêtre = paragraphe) vs taux du backtest (fenêtre = 400 caractères)

- `A_struct` (fenêtre paragraphe) : **0.3598** (59/164)
- `A_nul_struct` (moyenne sur 20 tirages, seed=530) : **0.3951**
- **lift structurel = 0.91**

> Accord qualitatif avec le backtest (lift < 3, la proximité seule ne discrimine pas) : **OUI**. Les deux routes utilisent une définition de fenêtre différente (paragraphe vs 400 caractères) — un accord sur les **valeurs exactes** n'est **pas** attendu, seulement sur le **sens** du résultat.

## Vérification directe des deux témoins

- citation du témoin négatif 1 (« collision avec la phrase générique... ») trouvée dans le backlog par grep externe : **OUI**
- citation du témoin positif (« n'est pas un défaut », marqueur du #482) trouvée dans le backlog par grep externe : **OUI**

## Aucun script existant modifié par ce commit

- confirmé : **0** fichier de `scripts/` touché par ce commit en dehors des deux nouveaux scripts du #530.

**PASS** — la route indépendante confirme la population du backtest, confirme le **sens** du lift (< 3) sous une définition de fenêtre différente, et confirme les deux citations et l'absence de modification hors du commit du #530.
