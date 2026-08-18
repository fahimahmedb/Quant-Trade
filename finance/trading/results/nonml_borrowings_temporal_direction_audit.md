# Audit indépendant — direction temporelle des emprunts (#509)

Le backtest date par le **premier commit d'ajout**, à la seconde. Cet
audit compare les **jours calendaires** : un rang de jour est insensible
aux écarts de quelques minutes — **le point faible du #509**, dont
l'unique « antérieure » tient à moins d'une heure.

## La population, recoupée avec le #508

- classe **B** du #508 : **26**
- dont **circulaires** : **5**
- « B tiers » attendus : **21**
- « B tiers » annoncés par le #509 : **21**
- accord : **OUI**

## La partition

- postérieure **19** + antérieure **1** + indatable **1** = **21**
- effectif : **21** — partition : **OUI**

## Le test par jour calendaire

- « antérieures » publiées : **1**
- **survivant à un test par jour** (source d'un jour strictement
  antérieur) : **0**

> **Aucune antériorité ne survit.** Toutes tiennent à un écart
> intra-journalier, c'est-à-dire à l'**ordre d'écriture des fichiers**
> et non à l'ordre des travaux. Le #509 le disait ; cet audit le
> confirme par une route qui **ne peut pas** voir les minutes.
>
> **Le résidu de neuf cycles d'enquête est donc nul par deux voies
> indépendantes.**

## Ce que cet audit ne prouve pas

Une antériorité, même de plusieurs jours, **n'établit pas** qu'une
citation soit fausse : une grandeur peut légitimement apparaître dans
deux cycles. Cet audit **resserre** un soupçon, il n'en fonde aucun.

Et il partage avec le backtest la **règle contextuelle du #502** : si
« ≥ 2 mots-clés dans ±200 caractères » est un mauvais test de « même
sujet », les deux routes se trompent ensemble depuis le début.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **25** ; dont **tapés en dur** : **0**

## Verdict

1. la population égale celle du #508 moins ses circulaires — **OUI**.
2. les trois classes forment une partition — **OUI**.
3. le test par jour est appliqué aux **1** antérieures — **OUI**.
4. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (4/4)

Anti-lookahead **sans objet au sens temporel** pour les prix ; la
datation est **strictement rétrospective** — premiers commits d'ajout.
