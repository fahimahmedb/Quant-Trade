# Pré-enregistrement — ajouter la colonne « Séances test. » aux 3 rapports non vérifiables

**Écrit et committé AVANT toute modification.** `n_trials = 1`.
Cycle d'**outillage documentaire**, sous le régime déclaratif du #429 : il
**modifie** des rapports publiés. Aucune stratégie évaluée, aucun verdict
recalculé, aucun paramètre de stratégie touché.

## La lacune, chiffrée au #427

Le contrôle de cohérence du #427 — le `.npz` doit reproduire un chiffre que le
rapport publiait déjà — a atteint **13 candidats sur 16**. Les **3** restants ne
publient **ni** nombre de séances **ni** taux d'activation :

`halloween_effect`, `intraday_range_regime_overlay`, `tom_overlay`

Leur `.npz` est produit et lisible, mais aucun chiffre déjà publié ne permet de
le confronter. J'avais écrit alors que « la lacune est dans le rapport d'origine,
et elle est notée plutôt que comblée par une valeur inventée ici ». Ce cycle la
comble — non par une valeur inventée, mais en **publiant une grandeur que le
script calcule déjà** et que cinq rapports frères affichent depuis toujours.

## La colonne, fixée avant tout calcul

Format **repris tel quel** de `golden_cross_overlay` et `sma50_trend_overlay`,
non redécidé :

- **en-tête** : `Séances test.`
- **position** : deuxième colonne, immédiatement après `Marché`
- **valeur** : `len(pnl_bh)` — la longueur de la **série évaluée**

Le choix de `len(pnl_bh)` plutôt que `len(bh_full)` n'est pas cosmétique.
`intraday_range_regime_overlay` évalue une fenêtre tronquée
(`pnl_bh = pnl_bh_full[idx]`) : c'est cette fenêtre-là que son `.npz` contient,
et c'est donc elle que la colonne doit annoncer. Publier `len(bh_full)` y
afficherait un nombre que rien ne vérifie. Pour les deux autres, les deux
expressions coïncident.

## Régime de modification — plus large que le #429, donc borné autrement

Le #429 remplaçait **une ligne**. Ici, ajouter une colonne réécrit **toutes les
lignes du tableau** : en-tête, séparateur, et une ligne par marché. Un contrôle
« N suppressions » ne dirait rien.

Le garde-fou devient **structurel** :

> Après avoir retiré la colonne ajoutée du tableau produit, le rapport doit être
> **identique octet à octet** à sa version d'avant.

Autrement dit : la seule différence admise est l'insertion d'une cellule par
ligne du tableau. Toute autre valeur qui bougerait — un Sharpe, un rendement, un
verdict, une ligne hors tableau — fait échouer le contrôle et devient le résultat
du cycle.

## Ce que le cycle doit produire — le vrai bénéfice

Le contrôle de cohérence du #427 doit passer de **13/16 à 16/16** : les 3 `.npz`
deviennent confrontables à un chiffre publié par leur propre script.

C'est la mesure qui compte. Ajouter une colonne sans que ce contrôle progresse
n'aurait aucun intérêt.

## Contrôles — fixés avant calcul

1. **Structurel** : colonne retirée ⇒ rapport identique octet à octet à l'avant,
   pour les **3**.
2. **Cohérence** : pour chacun des 3, la valeur de la colonne sur la ligne **NDX**
   doit égaler le nombre de séances du `.npz`. Écart toléré : **0**.
3. **Verdicts inchangés** : les 3 rapports portent un PASS avant ; ils doivent le
   porter après.
4. **Non-débordement** : aucun autre rapport du dépôt modifié.

## Critère de succès — chiffré

1. **3/3** rapports dotés de la colonne, ou l'échec publié avec sa raison.
2. **3/3** au contrôle structurel.
3. **3/3** au contrôle de cohérence, écart nul.
4. Contrôle du #427 recalculé et publié : attendu **16/16**.

## Prédiction — déductive

Ajouter une colonne construite à partir d'une variable déjà calculée ne touche
aucun calcul.

> **Attente : 3/3 structurel, 3/3 cohérence, contrôle du #427 porté à 16/16,
> verdicts inchangés.**

## Engagements

1. Résultat rapporté tel quel, y compris si le contrôle structurel échoue.
2. Le format de colonne n'est pas retouché après avoir vu le rendu.
3. Aucune ligne de calcul modifiée ; chaque script lu avant édition.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
