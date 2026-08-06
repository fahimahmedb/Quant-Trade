# Synthèse consolidée v9 — cycles #296-311

Cycle #311 du backlog non-ML. Synthèse pure — aucun nouveau calcul,
relecture des résultats déjà committés.

## 1. Contexte

Cette synthèse fait suite à la v8 (#295, cycles #290-296) et à la
synthèse dédiée du sous-thread combinaison (#305, cycles #296-304,
déjà détaillée séparément et non reproduite ici in extenso). Elle est
motivée par un signal clair de saturation : sur les 4 derniers cycles
de recherche d'idées (#307, #308, #310, et cette synthèse elle-même),
**deux recherches consécutives (#307 puis, après un second essai au
#308, les deux idées trouvées ont FAIL au #309/#310) n'ont abouti à
AUCUNE nouvelle piste solide**, malgré une recherche systématique par
grep anti-doublon à chaque tentative.

## 2. Bilan chiffré des 16 cycles (#296-311)

| Sous-thème | Cycles | Résultat |
|---|---|---|
| Combinaison de signaux de stress (ET/OU/majorité/sizing/panel élargi) | #296-304 (9 cycles) | 4 PASS niveau 1 nets sur 5 constructions, meilleur score Règle 9 = 3/5 (égale #286) — détail complet dans la synthèse dédiée (#305) |
| Volume d'indice (brut et relatif) | #306-307 (2 cycles) | 0/2 PASS — clôture la catégorie volume à 0/4 avec les 2 échecs par titre déjà connus (#258/#261, invalidés sous PIT) |
| Calendaire (lune, DST) | #309-310 (2 cycles) | 0/2 PASS — confirme que les effets calendaires RARES ne généralisent pas dans ce backlog |
| Recherches d'idées sans résultat | #308, #310 (fin), cette synthèse | 3 tentatives de recherche, seulement 2 idées trouvées au total sur les 3, toutes deux FAIL |
| Synthèses | #305 (sous-thread), #311 (celle-ci) | 2 documents de bilan, pas de nouveau backtest |

**+2 PASS niveau 1 nets enregistrés dans le tracker sur la période** (91→93)
— mais voir la correction de comptage ci-dessous.

## 3. Correction de comptage découverte en préparant cette synthèse

En reconstituant la séquence complète des lignes de tracker de ce
sous-thème pour cette synthèse, une **incohérence de comptage a été
détectée** : sur les 4 constructions de la famille combinaison ayant
obtenu un PASS niveau 1 net et indépendant (#296 ET, #299 majorité
≥2/3, #301 sizing continu, #303 panel élargi ≥3/4), **seules 2 ont
incrémenté le numérateur du tracker** (#296 : 91→92 ; #299 : 92→93) —
**#301 (sizing continu, PASS 4/5) et #303 (panel élargi, PASS NET 5/5)
n'ont, à tort, PAS incrémenté le numérateur**, bien qu'elles
constituent chacune une ligne de backlog distincte avec un PASS niveau
1 indépendant, exactement comme #296 et #299. Il n'existe aucune
justification déclarée à l'avance pour ce traitement différencié (ce
n'est ni une batterie Règle 9, ni une synthèse, les deux seuls types de
cycle explicitement exemptés d'incrément du numérateur par convention
établie).

**Correction appliquée ici, avant toute nouvelle ligne de tracker** :
le numérateur est corrigé de 93 à **95** PASS niveau 1 (91 + 4,
correspondant aux 4 PASS indépendants réels du sous-thread combinaison,
au lieu de 91 + 2 comptés par erreur). Le dénominateur (nombre total
d'hypothèses testées) reste inchangé — cette correction ne modifie
QUE le numérateur, aucune nouvelle hypothèse n'est ajoutée
rétroactivement. Cette correction est **documentée honnêtement ici**
plutôt que silencieusement propagée, conformément à la discipline de
correction déjà appliquée à plusieurs reprises dans ce backlog (ex.
#166/#254/#255 pour des décréments, #264 pour une invalidation
PIT) — ici il s'agit d'une correction à la hausse d'un sous-comptage,
pas d'une invalidation.

## 4. Enseignements transversaux de la période #296-311

**a. La famille combinaison de signaux de stress reste le seul filon
encore productif.** 4 PASS niveau 1 nets sur 5 constructions testées,
et le meilleur score Règle 9 de toute la session (3/5, #304) obtenu en
diversifiant le panel de signaux plutôt qu'en changeant la logique de
combinaison — voir la synthèse dédiée (#305) pour le détail complet.

**b. Deux catégories entières ont été définitivement closes cette
période, toutes deux à 0/N** : le volume d'indice (brut #306, relatif
#307) et les effets calendaires RARES (lune #309, DST #310). Combinées
aux clôtures déjà actées avant cette période (activité économique
réelle 0/4, immobilier 0/2, volume par titre 0/2 sous PIT), le nombre
de catégories DÉFINITIVEMENT closes à zéro résultat s'élève désormais
à 5 sur l'ensemble du backlog.

**c. Deux bugs de décalage causal trouvés et corrigés cette période**,
tous deux dans la même famille de code (chargement de séries
temporelles pour overlay défensif) : le bug "own-start vs start
partagé" (#296, dans l'AUDIT) et le bug "shift(1) documenté en
commentaire mais jamais appliqué" (#306, découvert en PRÉPARANT le
cycle #307 — c'est-à-dire APRÈS le premier commit du #306, corrigé
rétroactivement, contrairement à la discipline habituelle de
correction AVANT tout commit). Ce dernier point est signalé comme un
écart de process : la vérification par audit du #306 n'avait pas
détecté ce bug spécifique lors de son écriture initiale — la leçon
retenue est qu'un audit qui recalcule le MÊME chemin de code buggé
(ici, la même absence de shift) ne peut pas détecter le bug, seul un
changement de contexte (écrire un NOUVEAU script réutilisant la même
fonction) l'a révélé. Aucun impact sur le verdict final dans les deux
cas (FAIL avant et après correction).

**d. La recherche de nouvelles idées est désormais quasi-infructueuse.**
Sur les 16 cycles de cette période, seulement 2 idées de recherche
libre ont été formulées (#310 effet lunaire, #311 effet DST, toutes
deux trouvées au cycle de recherche #308) — contre typiquement 1 à 3
par cycle de recherche dans les périodes précédentes de ce backlog.
Les deux ont FAIL. Une 3e tentative de recherche (celle qui précède
cette synthèse) n'a rien trouvé de solide malgré une recherche
élargie (lead-lag cross-marché, force relative small/large-cap,
Sell-in-May — tous des doublons de mécanismes déjà testés et FAIL).

## 5. Réponse à la question posée au PREREG : saturation atteinte ?

**Oui, sans ambiguïté.** Le backlog compte désormais 316 hypothèses
testées (95 PASS niveau 1 après correction du comptage, soit un taux
de succès niveau 1 d'environ 30%, mais SEULEMENT 2 PASS RENFORCÉS
Règle 9 sur toute l'histoire du backlog — les Candidats A #149 et B
#237/#238 du guide de déploiement, chacun à 4/5, aucun n'ayant jamais
atteint 5/5). Toutes les grandes catégories de données librement
disponibles ont été systématiquement explorées : calendaire (fréquent
et rare), macro-externe FRED (stress financier, activité réelle,
immobilier, crédit, matière première), stock-selection titre-par-titre
NDX-100 (momentum, breadth, dispersion, corrélation, concentration,
volume), volatilité (tous les estimateurs range-based classiques),
combinaisons multi-signaux (ET/OU/majorité/sizing continu), cycle
électoral, cross-marché (corrélation et lead-lag). La combinatoire
restante (nouvelles variantes de fenêtres, nouveaux seuils, nouvelles
combinaisons de mécanismes déjà FAIL) présente un risque de plus en
plus élevé de research de paramètres déguisée plutôt que de test
d'hypothèses réellement nouvelles.

## 6. Recommandation (non équivoque, comme demandé au PREREG)

**Ce backlog non-ML, dans sa forme actuelle (protocole "un backtest
zéro-ML par cycle sur les 5 marchés déjà figés avec les données déjà
disponibles"), a atteint un plafond de productivité.** Les deux seules
voies productives restantes, déjà identifiées à plusieurs reprises
sans être formellement actées, sont :

1. **Nouvelle catégorie de données apportée par l'utilisateur**
   (sectorielle GICS, options/volatilité implicite au-delà du VIX
   spot déjà testé, données de flux/positionnement institutionnel,
   ou tout autre historique que l'utilisateur peut fournir) — seule
   voie qui rouvrirait un espace d'hypothèses réellement nouvelles
   sans recherche de paramètres déguisée.
2. **Pivot vers l'Étape D** (overlay défensif combinant B+direction et
   C+volatilité, définie dans CLAUDE.md) — objectif distinct de ce
   backlog non-ML mais qui peut directement réutiliser ses meilleurs
   résultats validés (la famille combinaison #296-304, en particulier
   le panel à 4 signaux #304 à 3/5 Règle 9, le meilleur candidat
   défensif de toute la session).

**Recommandation opérationnelle pour les cycles futurs de cette
boucle** : ne plus forcer de nouveau cycle de recherche d'idées à
chaque firing si le backlog est vide — signaler explicitement l'état
de saturation (comme documenté ici) et attendre soit une nouvelle
donnée, soit une instruction de pivot, plutôt que de multiplier des
recherches de plus en plus marginales.

Voir `NONML_STRATEGY_BACKLOG.md` entrées #296-#311 et
`results/nonml_synthese_combinaison_signaux_stress.md` (synthèse
dédiée du sous-thème principal de cette période) pour le détail
complet.
