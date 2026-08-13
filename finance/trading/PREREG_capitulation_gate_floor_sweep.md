# Pré-enregistrement — balayage des portes de capitulation neutralisées par le plancher 1,0×

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.
Cycle de **diagnostic** : aucune stratégie n'est évaluée, aucun paramètre choisi.

## Pourquoi

Le #410 a établi une propriété **structurelle**, non un accident d'échantillon :
`weakness_breadth_vol_targeting_overlay` combine une porte qui s'ouvre en régime
de faiblesse avec un vol-targeting `clip(20 % / vol, 1,0, 2,0)`. Or la faiblesse
et la volatilité haute coïncident : sur les **13** séances où la porte s'ouvrait,
l'exposition demandée avant clip était déjà sous 1,0 dans les **13** cas
(médiane 0,521× contre 1,096× en général). Les deux briques s'annulent, et le
« PASS » n'était que l'inactivité de la stratégie.

Rien ne garantit que ce candidat soit le seul. La question posée ici : **combien
d'entrées du backlog ont cette structure, et combien de leurs PASS sont vides
pour la même raison ?**

L'enjeu est direct : un PASS obtenu par inactivité n'est pas un résultat faible,
c'est un non-résultat étiqueté comme succès.

## Méthode — deux volets, dont un à couverture limitée (annoncé d'avance)

### Volet A — détection statique, exhaustive

Balayage de **tous** les `scripts/nonml_*_backtest.py`, à la recherche du motif
structurel : un `clip(..., 1.0, CAP)` appliqué à une exposition de vol-targeting
(plancher à 1,0, donc incapable de descendre sous l'exposition neutre).

Détection par lecture du code (`tokenize` + expressions régulières sur les appels
`np.clip`), **pas** par convention de nommage — c'est un critère de nommage qui
m'a fait manquer un foyer au #390 et un portage au #395.

### Volet B — mesure empirique, couverture limitée

Pour les candidats disposant d'un `.npz` au schéma `pos` : mesure directe de la
fraction de séances où l'exposition finale dépasse 1,0×.

**La couverture de ce volet est limitée par ce qui a été sauvegardé** — le #406 a
mesuré que les `.npz` ne couvrent que 41 % du backlog. Les candidats détectés au
volet A mais dépourvus de `.npz` seront **comptés et listés comme non mesurés**,
jamais silencieusement omis. Ce chiffre est un résultat du cycle, pas une excuse.

## Critères — FIXÉS AVANT EXÉCUTION

- **Structure présente** : le script applique un `clip` d'exposition à plancher
  `1.0`.
- **Candidat structurellement inactif** : exposition finale > 1,0× sur **moins de
  2 %** des séances. Le seuil de 2 % est repris **tel quel** du #410, où il avait
  été fixé avant calcul ; le reprendre évite d'en choisir un nouveau en voyant
  les chiffres.
- **PASS vide** : candidat structurellement inactif **dont le fichier de résultat
  porte un PASS**.

## Critère de succès — chiffré

Ce cycle est un diagnostic ; son succès ne se mesure pas en Sharpe.

1. **Couverture du volet A** : 100 % des `nonml_*_backtest.py` examinés, ou
   listés comme illisibles.
2. **Chaque candidat déclaré « PASS vide » est confirmé par lecture** de son
   script et de son rapport — pas sur la seule foi du compteur.
3. Le nombre de candidats détectés mais **non mesurés** faute de `.npz` est
   publié.

**Aucune correction du backlog n'est appliquée dans ce cycle.** Requalifier des
PASS est une seconde opération, à déclarer séparément : le faire ici, après avoir
vu lesquels tombent, serait exactement ce que le protocole interdit.

## Prédiction — non tranchée

Aucune. Le seul cas connu (#410) a été trouvé en portant un candidat sur univers
point-in-time, pas en cherchant cette structure ; je n'ai aucune base pour
extrapoler un nombre.

## Engagements

1. Résultat rapporté **tel quel**, y compris si le balayage ne trouve que le cas
   déjà connu — auquel cas le cycle aura confirmé une absence, ce qui est un
   résultat.
2. Aucun seuil ajusté après lecture.
3. Les candidats signalés puis **écartés** après lecture sont listés avec leur
   raison, au même titre que les confirmés.
4. **Relecture intégrale des rapports produits avant commit** (engagement pris au
   #414 après quatre incidents de dérivation consécutifs).
