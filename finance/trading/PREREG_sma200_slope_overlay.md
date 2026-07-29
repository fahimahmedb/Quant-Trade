# Pré-enregistrement — Overlay levé filtre de PENTE de la SMA200

**Committé AVANT tout calcul.** Cycle #66 du backlog non-ML. Variante du
#29 (SMA200, filtre de NIVEAU : prix > SMA200) testant un filtre de
PENTE : la SMA200 elle-même est-elle croissante ? Motivé par
l'observation technique classique selon laquelle une moyenne mobile
longue s'aplatit ou s'infléchit AVANT que le prix ne passe dessous
(signal précurseur), ce qui pourrait permettre une sortie plus précoce
en début de retournement que le filtre de niveau seul.

## Hypothèse

Un filtre basé sur la PENTE de la SMA200 (SMA200 croissante sur les 20
derniers jours) pourrait couper l'exposition plus tôt qu'un filtre de
NIVEAU (prix > SMA200, #29) en début de marché baissier, car la moyenne
mobile s'infléchit généralement avant que le prix ne la traverse. Un
overlay qui reste investi 1,0x en permanence mais AMPLIFIE l'exposition
uniquement quand la SMA200 est en pente positive pourrait battre
Buy&Hold, avec potentiellement un meilleur profil MDD que le #29 (qui a
montré une coupe tardive pendant les krachs prolongés, 61,6% de jours
encore levés en drawdown ≥40% sur NDX selon son audit).

## Définition (fixée ici, avant tout résultat)

- SMA200 = moyenne mobile simple des 200 dernières clôtures (identique
  au #29).
- Pente positive au jour t = SMA200(t) > SMA200(t − `SLOPE_LAG=20`)
  (comparaison de la SMA200 à sa propre valeur 20 séances plus tôt,
  fenêtre de pente choisie par analogie directe avec les autres fenêtres
  "moyen terme" déjà utilisées dans ce backlog — vol-targeting #46/#47
  fenêtre 20j, SMA50 #60).
- Position = **1,0x** en permanence, **CAP = 2,0x** les jours où la
  SMA200 est en pente positive, **1,0x** sinon.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2,0x identique à tous les cycles précédents,
fenêtre SMA200 identique au #29, SLOPE_LAG=20j fixé a priori par
analogie avec les autres fenêtres 20j du backlog, aucune grille testée
avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_sma200_slope_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py sma200_slope_overlay`.
