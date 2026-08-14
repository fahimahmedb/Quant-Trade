# Audit adversarial — vérification des chiffres du backlog (#461)

Recalcul par une **autre implémentation**, sans réutiliser une seule
fonction du backtest : un bug commun ne peut pas se cacher dans une
dépendance partagée.

## A. Recalcul indépendant du nombre de jetons

- annoncé par le rapport : **273**
- recalculé ici : **273**
- entrées introuvables : **0**

**CONCORDANT.**

## B. L'épinglage est-il le commit **introducteur** ?

Un épinglage qui viserait un commit postérieur laisserait la dérive du
dépôt rentrer par la fenêtre — c'est exactement le défaut des #445/#451.
Contrôle : l'entrée est présente au commit, **absente chez son parent**.

- conformes : **18/18**

**CONCORDANT.**

## C. Le rapport lit-il l'**histoire** ou le **disque** ?

Si les blobs épinglés étaient identiques au fichier courant, l'épinglage
serait **décoratif** et le rapport dériverait comme les inventaires que
les #436-#438 ont appris à repérer.

- blobs épinglés **différents** du fichier courant : **17**
- blobs épinglés identiques : **1**

**CONCORDANT** — l'épinglage mord réellement.

## D. Idempotence

Un rapport épinglé qui change d'une exécution à l'autre ne serait pas
épinglé. Le backtest est relancé et l'empreinte comparée.

- avant : `7be90fe842a42c02`
- après : `7be90fe842a42c02`

**CONCORDANT.**

## Ce que cet audit ne couvre pas

Il vérifie que le contrôle **fait ce qu'il dit**. Il ne peut pas rattraper
la limite de fond, déjà publiée dans le rapport : **un contrôle de recopie
ne voit pas un chiffre faux à l'identique dans le backlog et dans le
rapport.** Les quatre faux connus (#449, #451, #453, #457) sont de cette
nature — aucun audit de recopie ne les aurait trouvés.

## Verdict — **CONCORDANT** (4/4)

Aucun bug détecté par recalcul indépendant.