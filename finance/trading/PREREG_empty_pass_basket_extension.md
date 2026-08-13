# Pré-enregistrement — étendre le critère d'inactivité aux schémas panier

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.
Cycle de **requalification documentaire** : aucun verdict recalculé, aucun
paramètre de stratégie touché.

## La lacune, chiffrée au #417

Le #417 a appliqué la règle « PASS obtenu par inactivité » à **158** candidats au
schéma `pos` / `r_asset` : 0 nouvelle requalification, le cas connu étant isolé.

Mais **15** `.npz` échappaient à la règle, **dont 8 portant un PASS** : leur jambe
de référence n'est pas Buy & Hold mais un **portefeuille**, et le critère
d'identité au P&L de l'indice ne s'y transpose pas. Le #417 déclarait cette
extension comme travail distinct. C'est ce cycle.

## Ce que le schéma panier permet — et ce qu'il ne permet pas

Le schéma « panier » stocke **les deux jambes** : `pnl_gross_ov` / `turn_ov` pour
le candidat, `pnl_gross_bh` / `turn_bh` pour sa référence. La comparaison
naturelle existe donc dans le fichier, sans hypothèse supplémentaire :

> P&L net candidat = `pnl_gross_ov − turn_ov × c`
> P&L net référence = `pnl_gross_bh − turn_bh × c`

Le schéma **« deux jambes »** (`pos`, `r_asset`, `r_alt`) est **exclu
explicitement** : sa référence n'est pas stockée, et définir ce que « ne rien
faire » y signifie demanderait une convention que j'inventerais pour l'occasion.
Le nombre de candidats ainsi écartés est publié plutôt que dissous dans un
total.

## Règle — reprise du #417, transposée sans être assouplie

> Un candidat au schéma panier est requalifié **« PASS NON INFORMATIF »** si, et
> seulement si :
> 1. son rapport porte un **PASS**, **et**
> 2. le P&L net de sa jambe candidate est **strictement identique** à celui de sa
>    jambe de référence sur toutes les séances **sauf la première**.

L'exclusion de la première séance reprend celle du #417 (convention de coût
d'entrée, défaut attrapé au #416). Elle est conservée par cohérence même si les
deux jambes d'un panier ont toutes deux un turnover initial — la retirer serait
un changement de règle au moment de l'appliquer à de nouvelles données.

Le critère reste l'**identité du P&L**, jamais un seuil d'activation : le #416 a
montré qu'un seuil bas confond porte neutralisée et porte rare.

## Prédiction — tranchée, et fondée sur les rapports déjà publiés

Contrairement aux cycles où je me suis abstenu, celui-ci autorise une attente
vérifiable : les rapports de ces candidats affichent des **rendements totaux
différents** entre les deux jambes (par exemple `winners_trend` : +179,0 % contre
+181,7 % ; `leaders_vol_targeting_20` : +252,3 % contre +557,8 %). Si les P&L
étaient identiques, ces écarts n'existeraient pas.

> **Attente : 0 requalification.**

Si un candidat était pourtant requalifié, cela signifierait qu'un rapport publié
affiche deux rendements différents pour deux séries identiques — une
contradiction interne, et le résultat principal du cycle.

## Critère de succès — chiffré

1. **100 %** des `.npz` au schéma panier examinés, ou listés comme inexploitables.
2. Chaque requalification éventuelle **confirmée par lecture** du script et du
   rapport.
3. Nombre de candidats écartés faute de schéma exploitable publié.

## Engagements

1. Résultat rapporté tel quel, y compris s'il confirme l'attente de 0 — auquel
   cas le cycle aura fermé la dernière dette actionnable sans rien trouver, ce
   qui est un résultat.
2. Aucun verdict PASS/FAIL modifié, seulement étiqueté.
3. Aucun rapport réécrit : l'avertissement serait **ajouté** en fin de fichier.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
