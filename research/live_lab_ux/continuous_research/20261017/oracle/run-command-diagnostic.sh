#!/bin/bash
# Run from Oracle Cloud Shell. Creates an OCI command record for a guest
# diagnostic, without modifying guest packages, storage, services, keys or IAM.
set -eu
qt_oci() { command oci --region eu-paris-1 --no-retry --connection-timeout 5 --read-timeout 10 "$@"; }
QT_INSTANCE='ocid1.instance.oc1.eu-paris-1.anrwiljrtoradqacmugziwzu3sls2orieua6i7vkjveiq7q5wsiypa3mejpa'
QT_COMPARTMENT=$(qt_oci compute instance get --instance-id "$QT_INSTANCE" --query 'data."compartment-id"' --raw-output)
QT_CONTENT='{"source":{"sourceType":"TEXT","text":"#!/bin/bash\nid\nuname -m\nfree -h\ndf -h /\nlsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS\nif sudo -n true 2>/dev/null; then echo SUDO=OK; else echo SUDO=NON; fi\nsystemctl list-units --type=service --state=running --no-pager --no-legend \"quant*\" 2>/dev/null || true"},"output":{"outputType":"TEXT"}}'
QT_COMMAND=$(qt_oci instance-agent command create --compartment-id "$QT_COMPARTMENT" --target "{\"instanceId\":\"$QT_INSTANCE\"}" --content "$QT_CONTENT" --timeout-in-seconds 45 --display-name 'Quant read-only diagnostic' --query data.id --raw-output)
printf 'Commande : %s\nAttente du resultat...\n' "$QT_COMMAND"
for QT_TRY in {1..30}; do
    QT_STATE=$(qt_oci instance-agent command-execution get --command-id "$QT_COMMAND" --instance-id "$QT_INSTANCE" --query 'data."lifecycle-state"' --raw-output 2>/dev/null || true)
    case "$QT_STATE" in SUCCEEDED|FAILED|TIMED_OUT|CANCELED) break ;; esac
    sleep 4
done
qt_oci instance-agent command-execution get --command-id "$QT_COMMAND" --instance-id "$QT_INSTANCE" --query 'data.{etat:"lifecycle-state",code:content."exit-code",sortie:content.text,message:content.message}' --output json
