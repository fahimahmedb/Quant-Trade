# Pré-enregistrement — requalification des PASS obtenus par inactivité

**Écrit et committé AVANT toute modification de rapport.** `n_trials = 1`.
Cycle de **requalification documentaire** : aucune stratégie n'est ré-évaluée,
aucun paramètre touché, aucun verdict recalculé.

## Ce qui est requalifié, et ce qui ne l'est pas

Le #416 a établi **par mesure** que `weakness_breadth_vol_targeting_overlay`
produit un P&L **strictement identique** à Buy & Hold : sa porte ne s'ouvre
jamais (0 séance sur 1385), l'overlay ne prend aucune position effective, et son
« PASS » ne mesure que cette inactivité.

**Le verdict PASS n'est pas annulé** : le critère pré-enregistré du cycle
d'origine était bien atteint, arithmétiquement. Ce qui est ajouté est une
**étiquette** disant ce que ce PASS mesure — exactement celle que porte déjà sa
version point-in-time depuis le #410.

Annuler un verdict rétroactivement serait réécrire l'histoire du backlog.
L'étiqueter dit la vérité sans l'effacer.

## Règle de requalification — fixée avant exécution

> Un candidat est requalifié **« PASS NON INFORMATIF »** si, et seulement si :
> 1. son rapport porte un **PASS**, **et**
> 2. son `.npz` permet de reconstruire le P&L de l'overlay, **et**
> 3. ce P&L est **strictement identique** à celui de Buy & Hold sur toutes les
>    séances **sauf la première** — exclue parce que les scripts du dépôt y
>    imputent un coût d'entrée à la seule jambe Buy & Hold, écart comptable et
>    non décision de stratégie (défaut attrapé au #416).

Le critère est l'**identité du P&L**, pas un seuil d'activation. Le #416 a montré
qu'un seuil d'activation basse ne distingue pas une porte neutralisée d'une porte
rare par construction : `santa_vol_targeting_overlay`, à 1,70 % d'activation, agit
réellement et n'est pas requalifiable.

## Portée — balayage systématique, pas le seul cas connu

La règle est appliquée à **tous** les `results/*_pnl.npz` du dépôt au schéma
`pos` / `r_asset`, et non au seul candidat identifié au #416. Restreindre le
balayage à ce que je sais déjà est précisément ce qui m'a fait manquer un foyer
au #390, un portage au #395 et un doublon au #406.

Le nombre de candidats examinés, requalifiés, et non examinables faute de `.npz`
est publié.

## Effet sur les rapports

Pour chaque candidat requalifié, le fichier `results/nonml_<nom>_result.md`
reçoit un bloc d'avertissement **ajouté en fin de fichier**, jamais une
réécriture du contenu existant. Le texte du rapport d'origine reste lisible tel
qu'il a été publié.

## Critère de succès — chiffré

1. **100 %** des `.npz` au schéma `pos` examinés, ou listés comme inexploitables.
2. Chaque requalification est **vérifiée par relecture** du rapport modifié.
3. Le décompte des PASS du backlog affecté par cette requalification est publié —
   y compris s'il vaut 1.

## Prédiction — non tranchée

Aucune. Le #416 a mesuré un cas ; je ne sais pas si le balayage systématique en
trouvera d'autres.

## Engagements

1. Aucun verdict PASS/FAIL n'est modifié, seulement étiqueté.
2. Aucun rapport existant n'est réécrit : l'avertissement est ajouté.
3. Résultat rapporté tel quel, y compris si le seul cas requalifié est celui déjà
   connu — auquel cas le balayage aura confirmé une absence, ce qui est un
   résultat.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
