#!/bin/bash
set -e

echo -n """omaha.aws.dwos.com (and updates.aws.dwos.com) should be served by:
    (A) The new cluster (commit to DW)
    (B) The historic cluster (rollback to DentalWingsCanda)

Please type your answer [Aa]|[Bb]: """

read answer

case "$answer" in
    a|A) script='dns_commit.json';;
    b|B) script='dns_rollback.json';;
    *) echo "CANCEL: Could not understand '$answer'";exit ;;
esac

aws route53 change-resource-record-sets --hosted-zone-id Z3DP0PXNLQLR6U --change-batch "file://./$script"

echo """
You can monitor the outcome with: aws route53 get-change --id '<change_id>'"""