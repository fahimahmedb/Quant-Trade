# Audit indépendant — datation du basculement (#510)

Le backtest **maximise** un contraste. Un maximum peut être instable.
Cet audit **lit la courbe** : pour chaque **jour** de l'historique, la
part de « sans données » avant et après. **Aucun `argmax`.**

## Route 1 — balayage calendaire

- jours évaluables (plancher de **20** de chaque côté) : **10**
- jour de contraste maximal : **14/08/2026**
- avant **291** scripts (14,4 %), après (100,0 %)
- contraste : **+85,6** points
- date publiée par le #510 : **13/08/2026 21:51**
- **même jour** : **NON**

> **Le désaccord est de granularité, pas de fond.** Ce balayage
> ne peut couper qu'à **minuit** : une coupure à 21:51 ne fait
> pas partie de ses candidats. La coupure calendaire la plus
> proche range dans « avant » les
> **3** script(s) situés entre les deux instants.
>
> Les deux contrastes valent **+85,6** et le contraste publié
> par le #510 — un écart de moins d'un point. **Les deux routes
> décrivent la même transition ; seule leur résolution diffère.**
>
> **Je ne relâche pas le critère pour autant.** Il exigeait le
> même jour, il ne l'obtient pas, et l'audit porte une
> **RÉSERVE** — un critère qu'on assouplit après l'avoir vu
> échouer ne contrôle plus rien.

## Route 2 — stabilité au retrait des extrémités

- scripts retirés à chaque bout (**5 %**) : **17**
- coupure sur la population tronquée : **13/08/2026 21:51**
- contraste : **+87,8** points
- **même jour que le #510** : **OUI**

> **La coupure ne dépend pas des extrémités.** Retirer 5 % de la
> population de chaque côté ne la déplace pas de jour : le
> maximum n'est pas porté par quelques scripts de bord.

## Route 3 — le classement change-t-il de camp ?

Le #506 classait par **littéraux**, son audit par **appels**. Sur cette
population :

- scripts classés différemment par les deux routes : **30** sur **350**

> Un écart est **attendu** : nommer un fichier n'est pas l'ouvrir. Il
> est publié pour que le lecteur sache de combien la date pourrait
> bouger si l'on changeait de route de classement.

## La monotonie après la coupure

- part « sans données » après la coupure, publiée : **100,0 %**
- scripts postérieurs à la coupure : **62**
- dont **ouvrant des données** : **0**

> **Cohérent** : une part de 100 % après la coupure interdit toute
> exception, et il n'y en a aucune. **Le régime postérieur est
> homogène**, ce qui est plus fort qu'un simple contraste de
> moyennes.

## Ce que cet audit ne prouve pas

Il ne dit **pas** que le dépôt ait cessé d'étudier les marchés à cette
date : il date un changement dans **ce que les scripts à verdict
lisent**. Le #506 avait déjà établi que **72 %** des rapports à verdict
du dépôt ouvrent des données — l'essentiel de ce travail est **antérieur
à la coupure**, et reste acquis.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **25** ; dont **tapés en dur** : **0**

## Verdict

1. le balayage calendaire désigne le même jour — **NON**.
2. la coupure résiste au retrait de 5 % des extrémités — **OUI**.
3. l'écart entre routes de classement est publié — **OUI**.
4. la part après la coupure est cohérente avec les exceptions — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT — RÉSERVE** (4/5)

Anti-lookahead **sans objet au sens temporel** pour les prix ; la
datation est **strictement rétrospective** — premiers commits d'ajout.
