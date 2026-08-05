# Pré-enregistrement — Découverte incidente : le DSR record du #214 (dispersion) est caduc, mise à jour du guide (v3)

**Committé AVANT toute rédaction.** Cycle #273 du backlog non-ML. Pas un
nouveau backtest — découverte incidente en documentant le nouveau record
DSR du #272, et synthèse des résultats déjà committés.

## Découverte incidente

Le #214 (batterie Règle 9 sur le #78, dispersion cross-sectionnelle)
avait obtenu **DSR=0,1427**, resté le meilleur DSR de toute la lignée
vol-targeting jusqu'au #262 (Amihud illiquidité, DSR=0,2731, lui-même
invalidé au #264). Le #214 a été calculé sur la spécification
**originale** du #78 (univers = 99 membres NDX-100 **2026** appliqués
rétroactivement à 2021-2026) — jamais recalculé depuis que le #270 a
démontré que cette spécification bascule en FAIL sous l'univers
point-in-time réel (échantillon 2× plus long, composition réelle à
chaque date). **Exactement le même défaut de propagation** que celui
documenté pour #161/#162 (#259) et pour le DSR du #258 lui-même (#264) :
un DSR calculé sur un univers désormais démontré biaisé ne doit plus
être cité comme un résultat de référence, même s'il n'a jamais été
"corrigé" formellement par une nouvelle batterie (le #270, FAIL, n'a
logiquement jamais eu de batterie Règle 9 — inutile sur un FAIL).

**Conséquence** : en excluant les DSR caducs déjà identifiés (#161/#162
sur le #38 : 0,730/0,612 ; #258 : 0,4307 ; désormais #214 sur le #78 :
0,1427), le **nouveau record DSR authentique du backlog est 0,1341**
(#271/#272, breadth SMA200 sous univers point-in-time — un candidat qui,
lui, a RÉELLEMENT survécu à la correction du survivant avant d'être
soumis à la Règle 9, contrairement aux quatre candidats dont le DSR
s'est révélé caduc).

## Méthode

Lecture des résultats déjà committés (#270, #271, #272, #214), aucune
nouvelle donnée ni nouveau calcul. Mise à jour du guide
`results/nonml_meilleurs_candidats_guide_deploiement.md` (v3) : note sur
le DSR caduc du #214, mention du nouveau record authentique #271/#272
comme référence de comparaison (sans en faire un nouveau "Candidat" au
sens du guide — les leçons du Candidat C v1 et v2, tous deux retirés
après coup, incitent à la prudence : un score Règle 9 de 2/5 avec échec
sur les coûts et la stabilité temporelle n'est pas un profil à
recommander pour un déploiement, même avec le meilleur DSR authentique).

## Anti-cheat

Ce fichier committé avant toute rédaction. Sortie : mise à jour de
`results/nonml_meilleurs_candidats_guide_deploiement.md` et annotation
de l'entrée #214 dans le backlog. Pas de vérification anti-cheat
automatisée applicable (pas de nouveau backtest).
