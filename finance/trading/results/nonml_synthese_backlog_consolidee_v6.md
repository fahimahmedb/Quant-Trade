# Synthèse consolidée v6 — cycles #257 à #266 (10 cycles depuis la v5)

Complète (ne remplace pas) `..._v5.md` (couvrait #245-256). Pas de
nouveau calcul. Backlog au moment de la rédaction : **88 PASS niveau 1
sur 273 hypothèses testées, 0 PASS RENFORCÉ Règle 9 sans exception**.

## A. Clôture du balayage même barre élargi (#257)

Un grep générique (`weights_[a-z_]+\[t:end\] = w`, au lieu du grep
restreint des cycles #252-255) a révélé 29 scripts partageant le motif
de la fuite d'exécution « même barre », dont 3 derniers candidats PASS
jamais vérifiés (#35, #74, #83, tous des overlays SMA200 construits sur
le même mécanisme que #33). Les trois **survivent** au décalage causal
(marge réduite, comme #33) — le balayage même barre est désormais
**complet sur l'intégralité des 29 scripts identifiés**, aucun candidat
PASS non vérifié ne subsistait dans le backlog.

## B. Ouverture et fermeture complète de la catégorie volume (#258-263)

Après un constat d'exhaustion explicite (#257 : six catégories de
signaux déjà couvertes de façon dense), le volume — jamais extrait de
l'API Yahoo pourtant déjà utilisée — a été identifié comme la seule
catégorie de données réellement nouvelle disponible.

- **#258** (Lee & Swaminathan 2000, momentum+turnover double-tri) et
  **#261** (Amihud 2002, tilt illiquidité) : deux PASS nets, construits
  causal dès le départ, robustesse 5/5 plateau parfait chacun.
- **#259** et **#262** : batteries Règle 9 adaptées au format
  portefeuille (première fois pour des candidats stock-selection plutôt
  que des overlays mono-actif). Le #262 (Amihud) obtient **4/5 — le
  meilleur score de tout le backlog** (avec #209/#229), DSR=0,2731 alors
  le record authentique.
- **#263** : le guide de déploiement (figé depuis le #252) est mis à
  jour pour intégrer le #261 comme nouveau Candidat C.
- **Découverte incidente au passage (#259)** : les batteries historiques
  #161/#162 sur le #38 n'avaient jamais été recalculées depuis la
  correction du bug même barre — corrigé au #260 (effondrement 4/5→1/5
  et 3/5→0/5), clôturant la totalité des résidus du bug même barre dans
  ce backlog (backtests ET batteries).

## C. Balayage d'intégrité point-in-time des candidats volume (#264-266)

Le Candidat C (v2, #261) venait d'être ajouté au guide quand le **#264**
a révélé que #258 ET #261 basculent NETTEMENT en FAIL sous l'univers
point-in-time réel du NDX-100 (fetch dédié du volume pour 214 tickers
PIT, jamais fait) — un résultat **inverse** de celui du #38 (dont l'edge
avait survécu à la même correction au #163). Le guide de déploiement a
été corrigé LE JOUR MÊME (Candidat C v2 retiré).

Les cycles **#265** et **#266** ont isolé la cause : le momentum 12-1
(#73) et le momentum de constance (#82), testés SEULS sous PIT (jamais
fait jusqu'ici malgré leur usage comme briques de base de plusieurs
autres cycles), **survivent tous les deux** avec des marges nettes et
des plateaux de robustesse solides (4/5 et 5/5). Combiné à #4/#38 (déjà
connu, survit), **le trio complet des constructions de momentum "prix
pur" du backlog est désormais validé sous PIT**.

| Candidat | Construction | Verdict PIT |
|---|---|---|
| #4/#38 | 52w-high | **Survit** (#163) |
| #73 | 12-1 mois académique | **Survit** (#265) |
| #82 | Constance | **Survit** (#266) |
| #258 | Momentum + double-tri turnover | **FAIL** (#264) |
| #261 | Amihud illiquidité | **FAIL** (#264) |

## Ce que cette période apprend, au-delà de son score

1. **La survivorship bias de ce backlog affecte des MÉCANISMES
   spécifiques, pas les signaux stock-level en général.** Les trois
   signaux de momentum construits directement sur le PRIX survivent
   systématiquement à la correction de l'univers point-in-time ; les
   deux raffinements construits sur le VOLUME (turnover, illiquidité)
   n'y survivent pas, quel que soit leur score de robustesse ou de
   batterie Règle 9 sur l'univers biaisé (le #261 avait pourtant le
   meilleur score Règle 9 de tout le backlog avant sa correction).
   C'est une leçon plus fine que "corriger le survivant dégrade
   toujours l'edge" — ici la dégradation dépend du TYPE de signal, pas
   de sa force brute apparente.
2. **Une confirmation croisée par construction totalement indépendante
   reste le meilleur garde-fou contre un bug silencieux** : le #265 a
   confirmé son propre calcul en retrouvant EXACTEMENT le Sharpe de la
   jambe référence du #258 (+0,44), obtenu par un script n'ayant aucun
   code partagé au-delà de trois constantes.
3. **Un score Règle 9 élevé (4/5, DSR record) ne protège pas contre un
   biais de construction de l'univers** : le #261 avait le meilleur
   profil statistique jamais observé dans ce backlog pour un candidat
   stock-selection, et s'est pourtant effondré dès qu'un test plus
   rigoureux (mais orthogonal aux 5 contrôles de la Règle 9) a été
   appliqué — la Règle 9 et la correction PIT sont deux gardes-fous
   complémentaires, ni redondants ni substituables l'un à l'autre.
4. **Le cycle de correction le plus rapide de tout ce backlog** : le
   Candidat C (v2) a été ajouté au guide de déploiement (#263) et
   retiré (#264) en l'espace d'un seul cycle suivant — contraste avec
   les 4 jours entre le #163 (découverte de la composition PIT) et le
   #251/#252 (première formalisation puis correction du Candidat C
   original).

**Recommandation honnête, inchangée dans son fond depuis la v3/v4/v5** :
sans nouvelle catégorie de données ou de mécanisme, les cycles suivants
produiront probablement des variantes de plus en plus marginales des
mécanismes déjà exhaustivement testés, ou des corrections d'intégrité de
portée de plus en plus étroite (comme ce cycle l'illustre lui-même :
tester #33/#41/#48/#23 sous PIT, tous construits sur la même base #4
déjà validée sous PIT via #38, aurait une valeur informative marginale
décroissante). Le trio momentum validé sous PIT constitue, avec le
Candidat A (#149) et le Candidat B (#237/#238) du guide de déploiement,
la base la plus solide actuellement disponible dans ce backlog pour un
usage prudent.
