# Pré-enregistrement — second balayage des doublons de P&L

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.
Cycle de **diagnostic** : aucune stratégie évaluée, aucun paramètre choisi.

## Pourquoi rejouer

Le **#406** avait balayé les paires de candidats à P&L identique et conclu à
**1 essai surnuméraire** — mais son audit avait établi que la méthode ne voyait
que **41 %** du backlog et manquait le seul doublon connu d'avance, faute de
`.npz` sauvegardé. Le résultat était une **borne inférieure**, pas un décompte,
et je l'avais écrit pour que le chiffre ne soit pas repris comme tel.

Depuis, **18 `.npz` supplémentaires** ont été produits (12 portages point-in-time
des #394-#414, 10 au #416, moins les recoupements) : le dépôt en compte
maintenant **183** contre 165 au #406. La question du #406 peut donc être reposée
sur une base plus large.

## Méthode — strictement celle du #406, sans un paramètre changé

Le script `nonml_pnl_duplicate_sweep_backtest.py` est **rejoué tel quel**.
Aucun seuil n'est retouché :

- **doublon exact** : `np.array_equal` sur le P&L net reconstruit, à longueur
  égale ;
- **quasi-doublon** : corrélation de Pearson **≥ 0,9999**.

Rejouer un balayage en ajustant son seuil parce qu'on connaît désormais les
données serait exactement le geste que le protocole interdit. Le seuil de 0,9999
reste donc celui fixé au #406, y compris s'il laisse passer des paires que je
sais proches.

## Mesures annoncées d'avance

Outre le décompte, trois quantités seront publiées **quel que soit leur
résultat** :

1. **Couverture** : nombre de `.npz` exploitables rapporté au nombre d'entrées du
   backlog, comparé au 41 % du #406.
2. **L'angle mort du #406 est-il levé ?** Le doublon `sma200_leaders_overlay` /
   `leaders_trend_union_overlay` sur univers **d'origine** était invisible faute
   d'un `.npz` pour le second. Ce fichier existe-t-il désormais ? Si non, l'angle
   mort persiste et le résultat reste une borne inférieure — à écrire tel quel.
3. **Les paires mesurées au #414** : `momentum_decile_spread` / `momentum_dispersion`
   (portes identiques à 93,3 %, corrélation 0,8679) et leurs versions
   point-in-time. Leur corrélation de **P&L** est publiée, **sans** que le seuil
   de doublon soit ajusté pour les inclure ou les exclure.

## Critère de succès — chiffré

1. **100 %** des `*_pnl.npz` traités ou explicitement listés comme schéma non
   reconnu.
2. Chaque paire signalée est **confirmée ou rejetée par lecture** des deux
   scripts — critère repris du #406, où il avait fait rejeter une paire sur deux.
3. Le décompte corrigé d'essais est publié, ainsi que l'écart avec celui du #406.

**Aucune correction du DSR n'est appliquée**, comme au #406 : c'est une seconde
opération, à déclarer.

## Prédiction — non tranchée

Aucune. Le #406 avait trouvé un seul essai surnuméraire sur une base de 165
fichiers ; je ne sais pas ce que 183 donneront.

## Engagements

1. Résultat rapporté **tel quel**, y compris s'il est identique à celui du #406 —
   auquel cas le cycle aura confirmé une stabilité, ce qui est un résultat.
2. Aucun seuil ajusté après lecture.
3. Si l'angle mort du #406 persiste, il est **redit explicitement** plutôt que
   laissé à la mémoire du lecteur.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
5. **Vérification de l'historique avant d'agir**, y compris pour cette tâche de
   maintenance (règle étendue au #417 après une tâche inscrite à tort).
