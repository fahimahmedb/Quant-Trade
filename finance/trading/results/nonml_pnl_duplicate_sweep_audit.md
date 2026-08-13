# Audit adversarial — balayage des doublons de P&L

Un balayage qui ne trouve presque rien peut vouloir dire deux choses opposées :
il n'y a presque rien à trouver, ou il ne sait pas chercher. Cet audit sépare
les deux — l'enjeu est de savoir si le résultat du balayage autorise à conclure
à une **absence** de doublons.

## 1. Contrôle positif — le balayage sait-il trouver ?

Une copie conforme d'un `.npz` existant est injectée dans une copie temporaire
du répertoire de résultats, sous un nom différent. Le balayage doit la signaler.

- doublon synthétique détecté : **OUI**

**CONFORME — le silence du balayage sur le reste est informatif.**

## 2. Contrôle négatif — le seuil est-il trop permissif ?

Une copie **bruitée** (bruit d'écart-type égal à celui de la série) est injectée.
Elle ne doit être signalée ni comme doublon exact ni comme quasi-doublon.

- série bruitée signalée à tort : **NON**

**CONFORME — le critère ne confond pas ressemblance et identité.**

## 3. Portée réelle — que voit le balayage ?

La « couverture 100 % » annoncée par le balayage porte sur les fichiers `.npz`
**qui existent**, pas sur les candidats du backlog. L'écart est ici.

- entrées numérotées du backlog : **404**
- fichiers `*_pnl.npz` disponibles : **165**
- proportion du backlog visible par le balayage : **41 %**

Un `.npz` n'est sauvegardé que par certains scripts, et souvent seulement en cas
de PASS. **Plus de la moitié du backlog est donc hors de portée de cette
méthode**, et son silence ne vaut que pour la partie qu'elle voit.

## 4. Angle mort démontré sur le doublon connu du #403

Contrôle décisif. Le #403 a établi que `sma200_leaders_overlay` et
`leaders_trend_union_overlay` sont la **même stratégie**, sur l'univers
d'origine comme sur l'univers point-in-time. Le balayage retrouve-t-il la paire
d'origine ?

- `nonml_sma200_leaders_overlay_pnl.npz` présent : **OUI**
- `nonml_leaders_trend_union_overlay_pnl.npz` présent : **NON**
- paire d'origine détectable par cette méthode : **NON**

**ANGLE MORT CONFIRMÉ.** Le seul doublon dont l'existence était établie
*avant* ce balayage est **invisible** pour lui, faute d'un `.npz` sauvegardé
par l'un des deux candidats. Le balayage n'a retrouvé que sa réplique sur
univers point-in-time, où les deux fichiers existent.

Conséquence directe sur la lecture du résultat : **le balayage ne permet pas
de conclure qu'il n'y a que deux groupes de doublons dans le backlog.** Il
permet seulement d'affirmer qu'il n'y en a que deux parmi les candidats ayant
sauvegardé un `.npz`. C'est une borne inférieure, pas un décompte.

## 5. Vérification par lecture des groupes signalés

Critère 2 du pré-enregistrement : chaque paire est confirmée ou rejetée **par
lecture**, pas sur la foi du chiffre.

### Groupe 1 — `etape_D_overlay_optimized` / `nonml_etape_d_garch_defensive_overlay`

Les deux fichiers ont été ajoutés par le **même commit** (`0516f8f`, cycle #118).
Lecture de l'entrée #118 du backlog : elle est explicitement qualifiée de
« **FAIT — découverte importante, pas un nouveau backtest** » — il s'agissait de
réparer des scripts Étape D cassés et de régénérer un résultat obsolète, pas
d'évaluer une stratégie neuve. Le second `.npz` est un **alias de nommage** vers
l'espace `nonml_`, pas un second essai.

**Doublon de fichier CONFIRMÉ, essai surnuméraire REJETÉ** : une seule stratégie,
un seul essai, déjà déclaré comme réutilisation à l'époque.

### Groupe 2 — `..._trend_union_overlay_pit_universe` / `..._sma200_leaders_overlay_pit_universe`

C'est la paire établie au #403, dont l'identité bit-à-bit avait déjà été prouvée
dans ce cycle-là. Les deux correspondent à **deux entrées distinctes du backlog**
(#401 et #403), chacune comptée comme un essai.

**Doublon CONFIRMÉ, 1 essai surnuméraire.**

### Décompte corrigé

Le balayage annonçait 2 entrées surnuméraires ; la lecture en rejette une.
**Correction retenue : 1 essai surnuméraire**, soit 372 → **371**.

Cette correction est **négligeable** devant l'angle mort du contrôle 4 : elle
porte sur la partie visible du backlog, qui en couvre moins de la moitié.

## Verdict de l'audit

**MÉTHODE VALIDE, PORTÉE INSUFFISANTE.** Le balayage détecte ce qu'il voit
(contrôles 1 et 2 conformes), mais ne voit qu'une fraction du backlog et
manque le seul doublon connu d'avance. Son résultat est une **borne
inférieure** : au moins un essai surnuméraire, probablement davantage.

Conclure de ce cycle qu'il n'y a « que » deux doublons serait une
surinterprétation. C'est écrit ici pour que le chiffre ne soit pas repris
plus tard comme un décompte complet.
