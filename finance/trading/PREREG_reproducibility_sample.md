# Pré-enregistrement — reproductibilité des rapports publiés (échantillon tiré au sort)

**Écrit et committé AVANT toute mesure d'échantillon.** `n_trials = 1`.
Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché.

## L'angle que les inventaires précédents n'ont pas couvert

Le #431 a passé cinq contrôles de protocole ; le #433 a corrigé une conclusion
que j'avais tirée trop vite. La règle du #429 impose de **chercher avant de
conclure**, et le #433 y a ajouté : **ne pas s'arrêter à la première résolution
disponible**.

Une question n'a jamais été posée : **les rapports publiés se reproduisent-ils
encore à partir de leur propre code ?**

Les lots #416 → #427 ont vérifié l'identité octet à octet pour **44** rapports —
mais uniquement ceux dont le script venait d'être modifié. Le dépôt en compte
**288**. Les **244** autres n'ont jamais été ré-exécutés depuis leur publication,
alors que le code partagé (`data_loader.py`, `prediction.py`) a évolué entre-temps
et que les corrections #375-#404 ont touché des fonctions communes.

C'est une dette **réelle et jamais chiffrée**, distincte de tout ce qui précède.

## Périmètre — un échantillon, et pourquoi pas l'exhaustif

Ré-exécuter 288 scripts prendrait des heures et plusieurs cycles. Traiter « tout »
d'un coup reproduirait le geste des #392 et #404, dont le #423 a tiré la leçon.

> **Échantillon de 12 scripts**, tiré au sort parmi ceux qui possèdent un
> `results/nonml_<nom>_result.md`, avec la graine **20260813** fixée ici.

La graine est écrite **avant** le tirage : je ne pourrai pas retirer un
échantillon qui donnerait un résultat déplaisant. Chaque script reçoit un
**délai maximal de 300 s** ; au-delà, il est compté **« non concluant »**, ni
réussite ni échec.

## Régime — aucun rapport publié ne doit changer

Ré-exécuter un script **réécrit** son rapport. Ce cycle ne veut rien publier de
neuf : il veut **savoir**. Donc :

> Chaque rapport de l'échantillon est **sauvegardé avant**, comparé après, puis
> **restauré à l'identique**. À la fin du cycle, `git status` doit être vide de
> toute modification de `results/*_result.md`.

Si un rapport diverge, la divergence est **publiée et analysée**, mais **pas
committée** : corriger un résultat publié est une opération distincte, qui
mériterait son propre pré-enregistrement et son propre régime déclaré (#428,
#429, #430 ont chacun déclaré le leur).

## Reconnaissance déjà faite — et déclarée

Pour dimensionner le délai, j'ai chronométré **3** scripts avant d'écrire ces
lignes (`halloween_effect` 12,5 s, `turn_of_month` 9,0 s, `sma50_trend_overlay`
3,1 s). Ils se sont **reproduits à l'octet près**. Ces trois-là sont donc déjà
connus au moment où j'écris : ils **restent dans le tirage** — les exclure
biaiserait l'échantillon — mais je le signale pour que leur éventuelle présence
ne soit pas lue comme un tirage neutre.

## Contrôle secondaire — la règle « zéro ML », balayée pour la première fois

Mesuré avant d'écrire, et publié tel quel : sur tous les `scripts/nonml_*.py`,
**1 seul** fichier contient un motif ML (`sklearn`, `torch`, `RandomForest`…),
et c'est `nonml_anti_cheat_check.py` — le vérificateur lui-même, dont c'est le
motif de détection. **0 violation réelle.**

Ce contrôle est simple et son résultat est nul ; je le publie quand même, parce
qu'un contrôle qui ne trouve rien reste une vérification faite.

## Critère de succès — chiffré

1. **12** scripts tirés avec la graine annoncée, la liste publiée **avant** les
   résultats individuels.
2. Chacun classé : **identique**, **divergent** (avec le `diff`), ou **non
   concluant** (délai dépassé / erreur d'exécution, avec le message).
3. `git status` **vide** de toute modification de `results/*_result.md` en fin de
   cycle.
4. Le taux de reproductibilité publié tel quel, quel qu'il soit.

## Prédiction

**Aucune prédiction chiffrée.** Les 44 rapports vérifiés aux #416-#427 l'ont été
juste après modification de leur script — ils ne disent rien des 244 autres, dont
certains datent d'avant les corrections #375-#404. Prédire sans base m'a déjà
trompé deux fois (#407, #408).

La seule attente que je formule est **négative et faible** : si une divergence
apparaît, elle viendra plus probablement d'un rapport ancien que d'un rapport
récent. Je ne la compte pas comme une prédiction testable sur 12 tirages.

## Engagements

1. Résultat rapporté tel quel, y compris **12/12 identiques** — ce serait alors
   une absence de dette confirmée, et je l'écrirai sans la présenter comme un
   exploit.
2. Aucun script exclu du tirage après l'avoir vu.
3. Aucun rapport publié modifié ni committé par ce cycle.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
