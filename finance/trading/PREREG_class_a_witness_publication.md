# Pré-enregistrement — **publier** les témoins de classe A

**Écrit et committé AVANT toute exécution et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #494.

## La décision, prise ici et pas après

Le #494 a établi que deux scripts — `net_pnl_correction_backtest` et
`sweep_pass_prose_fix_backtest` — sont **de classe A** : ils n'exécutent aucun
script tiers et n'écrivent que **leur propre rapport**. Leur témoin est dans le
code depuis les #487/#489 et **n'a jamais paru**.

Le #489 avait posé une règle : ne committer le rapport régénéré **que si son
diff se réduit au témoin**. Elle l'a fait renoncer, le diff étant dominé par la
dérive du dépôt. Le #494 a conclu que **le blocage est de méthode, pas
technique**, et a laissé l'arbitrage à ce cycle.

> **Décision : j'accepte un diff non borné au témoin — à une condition.**
>
> **Le diff complet de chaque rapport est publié dans le rapport de ce
> cycle**, et **chaque changement y est attribué** : au témoin, ou à la dérive
> du dépôt. Un rapport régénéré dont les chiffres bougent en silence serait
> pire que le témoin manquant ; publié ligne à ligne, il est traçable.

**Le refus reste possible et déclaré** : si un diff se révèle **impubliable en
entier** — plus de 200 lignes — le rapport correspondant **n'est pas committé**,
et le cycle le dit.

## Le protocole

Pour chacun des deux :

1. **restauration** de `results/` **avant** (base = état committé) ;
2. **deux exécutions** consécutives, empreintes SHA-256 comparées — contrôle
   d'idempotence au sens du #463 ;
3. **vérification** que la ligne de témoin est **présente** dans le rapport
   régénéré ;
4. **diff complet** committé-vs-régénéré, publié **en entier** dans le rapport
   de ce cycle ;
5. **attribution** de chaque ligne du diff : *témoin* ou *dérive*.

Budget **300 s** par exécution. **Aucun autre script n'est exécuté.**

## Critère de succès — chiffré, il porte sur le procédé

1. Les **2** exécutés **deux fois**, les **deux empreintes** publiées.
2. Le témoin **vérifié présent** dans chaque rapport régénéré.
3. Le **diff complet publié** pour chacun — ou le refus déclaré si > 200 lignes.
4. **Chaque ligne du diff attribuée** — témoin ou dérive.
5. **Aucun autre fichier** modifié, arbre vérifié à la fin.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **2** s'exécutent sans erreur **et sont idempotents**.
2. Le témoin **apparaît** dans les **2** rapports régénérés.
3. Le diff de **chacun** contient **plus** que le témoin — la dérive domine.

Si la prédiction 1 est réfutée — un des deux n'est pas idempotent — alors
**publier son rapport serait publier un texte instable**, et je devrai renoncer
pour celui-là **même si le témoin apparaît**.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script de classe C : la cascade reste interdite.
- Il ne **modifie** aucun code : les témoins sont déjà en place.
- Il n'**édite à la main** aucun rapport.
- Il ne **corrige** aucun chiffre qui aurait dérivé : il les publie.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si un rapport doit rester non publié.
2. Décision et seuil de 200 lignes **inchangés** après avoir vu les diffs.
3. **Chaque ligne du diff attribuée**, jamais résumée en « dérive diverse ».
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
