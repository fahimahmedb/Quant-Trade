# Pré-enregistrement — Ajout de la Règle 10 à PROTOCOLE_ANTI_SNOOPING.md

**Committé AVANT rédaction.** Cycle #147 du backlog non-ML. Mise à jour
de documentation de protocole, PAS un nouveau backtest.

## Objet

Le #142 a montré que 86-89% du gain du #134 (meilleur candidat du
backlog) venait d'une correction implicite d'une hypothèse de backtest
irréaliste (0% de taux sans risque sur la fraction "hors-marché" d'un
mécanisme défensif). Le #146 a montré que cette correction NE sauve
PAS un signal structurellement mauvais, et ne s'applique de toute
façon PAS à la majorité des overlays du backlog (construits pour
rester ≥1,0x en permanence). Ces deux résultats, pris ensemble,
justifient une règle de bonne pratique PROSPECTIVE (éviter de refaire
cette découverte par accident dans un futur mécanisme défensif) plutôt
qu'une nouvelle campagne de correction rétroactive systématique
(#146 a montré que l'effet est spécifique au profil du #115, pas
généralisable).

## Contenu prévu de la Règle 10 (fixé ici, avant rédaction finale)

1. Tout NOUVEAU mécanisme qui réduit l'exposition sous 1,0x (donc
   détient implicitement une fraction du capital "hors-marché") doit
   être pré-enregistré avec une hypothèse EXPLICITE sur la
   rémunération de cette fraction — soit 0% (cash, hypothèse à
   justifier explicitement si retenue), soit un proxy de taux sans
   risque réaliste (ex. DGS3MO/DGS10, déjà disponibles dans
   `data/`), jamais une valeur implicite non déclarée.
2. Si un mécanisme défensif est rapporté avec l'hypothèse 0% et
   s'avère PASS ou proche du seuil Règle 9, la décomposition
   portage/effet-prix (méthode du #142) doit être appliquée avant de
   communiquer le résultat comme une découverte de diversification/
   couverture — pour éviter de confondre une correction de biais de
   backtest avec un edge authentique.
3. Cette règle ne s'applique PAS rétroactivement à tous les mécanismes
   déjà committés (cela nécessiterait de refaire ~144 cycles) — elle
   s'applique aux mécanismes FUTURS, et au #134/#137/#139 qui restent
   la référence documentée du phénomène.

## Ce que ce cycle NE fait PAS

Ne relance aucun test rétroactif sur les mécanismes déjà committés
(#146 a montré que l'effet n'est pas généralisable, une nouvelle
campagne systématique ne serait pas justifiée). Ne change aucun
verdict Règle 9 déjà rendu.

## Anti-cheat

Rédaction en un seul passage après ce pré-enregistrement.
