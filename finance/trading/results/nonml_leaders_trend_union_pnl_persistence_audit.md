# Audit — lever l'angle mort des balayages de doublons

## 1. Non-régression

- fichier de résultat identique après ré-exécution : **OUI**

**CONFORME — l ajout du savez n a rien perturbé.**

## 2. Test de la prédiction pré-enregistrée

Le pré-enregistrement annonçait, **avant l'ajout** : « le balayage doit détecter
la paire comme doublon exact, et le décompte corrigé passer de 1 à 2 ».

- paire détectée comme doublon exact : **OUI**
- groupes de doublons trouvés : **3**
- entrées surnuméraires brutes : **3**
- après rejet de l'alias de nommage Étape D (fait par lecture au #406) : **2**

**PRÉDICTION CONFIRMÉE.** Le décompte passe de 1 à 2, exactement comme
annoncé. Ce n'était pas une intuition : c'était la conséquence arithmétique
du #403, et elle se vérifie.

Le point n'est pas d'avoir eu raison — la prédiction était déductive, pas
risquée. Il est que **les deux balayages précédents avaient tort de conclure
à 1**, et le savaient : tous deux ont écrit que leur résultat était une borne
inférieure. Cette borne vient de monter d'un cran.

## 3. Identité vérifiée sans passer par le balayage

Contrôle direct, pour ne pas dépendre du seul outil dont on teste la portée.

- schéma reconnu : `panier` / `panier`
- longueurs : **1144** / **1144**
- P&L nets bit-à-bit identiques : **OUI**

**CONFORME — l identité établie au #403 se retrouve sur l univers d origine.**

## Ce qui reste hors de portée

- fichiers `*_pnl.npz` : **184**
- schémas non reconnus par le balayage : **0**

L'angle mort **spécifique** documenté aux #406 et #418 est levé. La limite
**générale** ne l'est pas : le balayage ne voit toujours que les candidats ayant
sauvegardé un `.npz`, soit moins de la moitié du backlog. Un doublon entre deux
candidats dépourvus de `.npz` resterait invisible, et rien ne dit qu'il n'y en a
pas.

## Verdict de l'audit

**CONFORME — les trois contrôles passent.**
