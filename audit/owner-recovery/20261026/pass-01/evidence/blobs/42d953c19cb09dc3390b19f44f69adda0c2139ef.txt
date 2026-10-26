# Commandes Owner — qualification factice L2-A

Préparées le 7 octobre 2026 ; **aucune de ces commandes n'a été exécutée sur la VM par Builder**. Le paquet contient onze fichiers de qualification et leur manifest d'épingles. Il ne contient ni harnais, ni root, ni contexte d'opération, ni manifest réel, ni fixture. Cette procédure ne lance pas le script d'opération A2.

Autorité : décision ratifiée `276fd995fe494e1734bba13827e6103864ce68da`, blob `d9809d0cca1faa51b713f02e453b7233c7a16811`, ratification consignée à `ccd4747e4bb9e2a4d93c552ba10e081f254af1e7`. Owner seul utilise son accès SSH et sudo existants, sous les conditions L2-A. Le commit final de cette remise est donné extérieurement au présent fichier pour éviter une référence auto-déterminée.

## 1. Sur le poste Owner : préparer les seuls fichiers nécessaires

Dans un checkout Git existant de Quant-Trade, remplacer les deux valeurs entre chevrons par le commit complet de la remise et l'alias SSH habituel. Aucune nouvelle infrastructure ou clé n'est créée.

```bash
set -euo pipefail
A2_COMMIT='<commit complet de la remise>'
A2_HOST='<alias SSH habituel de la VM>'
A2_BASE=research/weather_forward/v4/a2_operation
A2_PIN_BLOB=e718b284982a0f8c5c119be6a44cd1b803651f9b
git fetch origin "$A2_COMMIT"
git show "$A2_COMMIT:$A2_BASE/qualification/file_pins.tsv" > a2-qualification-pins.tsv
test "$(git hash-object --no-filters a2-qualification-pins.tsv)" = "$A2_PIN_BLOB"
mapfile -t A2_FILES < <(cut -f2 a2-qualification-pins.tsv)
test "${#A2_FILES[@]}" -eq 11
git archive --format=tar "$A2_COMMIT" \
  "$A2_BASE/qualification/file_pins.tsv" "${A2_FILES[@]}" > a2-qualification.tar
scp a2-qualification.tar "$A2_HOST:~/a2-qualification.tar"
```

Le checkout et l'archive partielle sont préparés hors unité contrainte. Aucun clone ou checkout complet n'est fait sur la VM. Le transport administratif n'est pas le réseau d'un processus de calcul/test/A2.

## 2. Dans le terminal Owner déjà connecté à la VM : réception et contrôles

Ce bloc reçoit le code et contrôle les blobs avant usage. Il ne crée pas le compte, ne monte pas le tmpfs et ne lance aucune sonde. Un répertoire déjà présent impose arrêt, sans effacement.

```bash
set -euo pipefail
A2_BASE=research/weather_forward/v4/a2_operation
A2_PIN_BLOB=e718b284982a0f8c5c119be6a44cd1b803651f9b
A2_STAGE="$PWD/a2-qualification-reception-20261007"
test ! -e "$A2_STAGE"
test ! -L "$A2_STAGE"
mkdir -m 0700 "$A2_STAGE"
tar -xOf a2-qualification.tar "$A2_BASE/qualification/file_pins.tsv" > "$A2_STAGE/file_pins.tsv"
test "$(git hash-object --no-filters "$A2_STAGE/file_pins.tsv")" = "$A2_PIN_BLOB"
mapfile -t A2_FILES < <(cut -f2 "$A2_STAGE/file_pins.tsv")
test "${#A2_FILES[@]}" -eq 11
tar -xf a2-qualification.tar -C "$A2_STAGE" --no-same-owner \
  "$A2_BASE/qualification/file_pins.tsv" "${A2_FILES[@]}"
while IFS=$'\t' read -r expected relative; do
  test -f "$A2_STAGE/$relative"
  test ! -L "$A2_STAGE/$relative"
  test "$(readlink -f "$A2_STAGE/$relative")" = "$A2_STAGE/$relative"
  test "$(git hash-object --no-filters "$A2_STAGE/$relative")" = "$expected"
done < "$A2_STAGE/file_pins.tsv"
sudo bash "$A2_STAGE/$A2_BASE/qualification/host_facts.sh"
```

Examiner le constat avec la déclaration Owner de l'hôte : Ubuntu, cgroup v2, Python ≥ 3.10, systemd et commandes déjà disponibles, sudo existant et absence de présence ou inconnue matérielle de données/credentials opérationnels exposés au traitement. Le constat n'ouvre pas leurs contenus et n'atteste pas une absence exhaustive. Il ne produit pas `CONTROL_VERIFIED`. Une installation, une mise à niveau, un utilisateur/chemin déjà présent ou une mutation non listée ne sont pas des réparations automatiques autorisées par ces commandes.

Environnement Builder constaté : Python 3.12.14, x86_64. La version et l'architecture VM sont encore **NON_OBSERVÉES** ; leur comparaison reste à consigner. Un écart n'est pas accepté implicitement.

## 3. Après satisfaction des conditions L2-A : compte, tmpfs et copie vérifiée

Utiliser le même terminal et les variables du bloc 2. Ce bloc crée uniquement les éléments explicitement permis par L2-A. Il ne lance pas les sondes.

```bash
sudo bash "$A2_STAGE/$A2_BASE/qualification/setup_host.sh"
sudo bash "$A2_STAGE/$A2_BASE/qualification/deploy_files.sh" "$A2_STAGE" "$A2_PIN_BLOB"
```

`setup_host.sh` refuse un compte, groupe ou chemin existant, y compris un lien symbolique. `deploy_files.sh` vérifie tout le paquet avant la première copie et refuse un `/opt/a2` non vide. Les onze fichiers et leur manifest sont détenus par root ; aucun fichier H n'est déployé. Aucun service permanent ni `/etc/fstab` n'est modifié. Le tmpfs de 1 MiB est perdu au redémarrage ; cette perte ne démontre pas une purge contrôlée.

## 4. Qualification factice seule

```bash
sudo bash /opt/a2/research/weather_forward/v4/a2_operation/qualification/run_qualification.sh \
  e718b284982a0f8c5c119be6a44cd1b803651f9b
```

Le superviseur administratif reste extérieur aux plafonds de l'unité. Chaque sonde est lancée une fois, avec le profil partagé, dont la variante réseau « PrivateNetwork seul » est explicitement distinguée. Les sondes n'importent pas H. Le réseau est essayé seulement après constat d'un namespace distinct et d'une interface loopback seule ; les cibles sont les plages documentaires, jamais une source opérationnelle.

Les sorties retenues ici sont **des observations factices L2-A**, pas des preuves d'opération A2. Le superviseur affiche le répertoire de transcripts. Il capture les propriétés et pics avant reset de l'unité. Le résumé retourne `0` uniquement si son critère composé est satisfait ; sinon `2`, avec `NOT_VERIFIED` ou `DETECTED_AFTER_BREACH` par limite. Une valeur numériquement au-dessus du plafond n'est pas arrondie en succès. Un arrêt par un autre contrôle ou une sonde non atteinte ne démontre pas la limite ciblée.

Le témoin positif et les lectures de pics sont nécessaires ; la simple présence des propriétés dans le profil ne suffit pas. Le test de lecture couvre exactement les répertoires énumérés dans les sondes, sans preuve d'isolation absolue des interfaces système. Les hooks de l'opération future ne sont pas qualifiés comme une isolation système par ce test.

Le script refuse un tmpfs non vide et conserve tout artefact inattendu. Il retire seulement les fichiers `qual-*.json` de la sonde qu'il vient de copier ; il ne purge pas un résultat d'opération retenu. Il n'y a ni retry automatique ni modification du profil pour transformer un échec en succès.

## 5. Retour documentaire

Conserver les transcripts de qualification et le constat local. Avant publication éventuelle des seuls éléments factices autorisés, retirer secrets, IP, nom d'hôte public et autres identifiants d'hôte. Ne pas publier de payload ou de preuve d'opération A2. Consigner les mutations réellement faites et les limites non démontrées, puis fournir ces références pour la suite L2-J/lot 3. Cette procédure ne produit aucune signature Astra, gel de configuration, autorité E, activation de root ou permission d'opération lot 4.
